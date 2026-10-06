/* Real Chromium/webview interaction via a loopback-only disposable host. */
const assert = require('node:assert/strict');
const { mkdirSync, writeFileSync } = require('node:fs');
const { join } = require('node:path');
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

class CDP {
  constructor(url) {
    this.socket = new WebSocket(url); this.next = 0; this.pending = new Map(); this.contexts = new Map();
    this.ready = new Promise((resolve, reject) => {
      this.socket.addEventListener('open', resolve, { once: true });
      this.socket.addEventListener('error', reject, { once: true });
    });
    this.socket.addEventListener('message', event => {
      const message = JSON.parse(event.data);
      if (message.id) {
        const callback = this.pending.get(message.id);
        if (callback) { this.pending.delete(message.id); clearTimeout(callback.timer); message.error ? callback.reject(new Error(message.error.message)) : callback.resolve(message.result); }
      } else if (message.method === 'Runtime.executionContextCreated') {
        const context = message.params.context;
        this.contexts.set(`${message.sessionId || ''}:${context.id}`, { id: context.id, session: message.sessionId });
      } else if (message.method === 'Target.attachedToTarget') {
        void this.send('Runtime.enable', {}, message.params.sessionId).catch(() => {});
      }
    });
  }
  async send(method, params = {}, sessionId) {
    await this.ready;
    const id = ++this.next;
    const result = new Promise((resolve, reject) => {
      const timer = setTimeout(() => { this.pending.delete(id); reject(new Error(`CDP timeout: ${method}`)); }, 10_000);
      this.pending.set(id, { resolve, reject, timer });
    });
    this.socket.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }));
    return result;
  }
  async evaluate(context, expression) {
    const response = await this.send('Runtime.evaluate', { expression, contextId: context.id, returnByValue: true, awaitPromise: true }, context.session);
    if (response.exceptionDetails) throw new Error(response.exceptionDetails.text);
    return response.result.value;
  }
  close() { this.socket.close(); }
}

exports.checkUI = async function checkUI(port) {
  const clients = new Map(); let active, context;
  async function screenshot(name) {
    const directory = process.env.SPECSPEC_SCREENSHOT_DIR;
    if (!directory || !active) return;
    const image = await active.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
    mkdirSync(directory, { recursive: true }); writeFileSync(join(directory, `${name}.png`), Buffer.from(image.data, 'base64'));
    console.log(`Screenshot: ${join(directory, `${name}.png`)}`);
  }
  try {
    const until = Date.now() + 60_000;
    while (!active && Date.now() < until) {
      try {
        const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
        for (const target of targets) {
          if (!target.webSocketDebuggerUrl || clients.has(target.id)) continue;
          const client = new CDP(target.webSocketDebuggerUrl); clients.set(target.id, client);
          await client.send('Runtime.enable');
          await client.send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true }).catch(() => {});
        }
        for (const client of clients.values()) {
          for (const candidate of client.contexts.values()) {
            try {
              if (await client.evaluate(candidate, `typeof document !== 'undefined' && !!document.querySelector('#cards .card.manifesto')`)) {
                active = client; context = candidate; break;
              }
            } catch { /* Other frames are not the graph. */ }
          }
          if (active) break;
        }
      } catch { /* Chromium is starting. */ }
      if (!active) await delay(150);
    }
    assert.ok(active, 'Could not find the real graph webview context.');
    const evaluate = expression => active.evaluate(context, expression);
    try {
      const { windowId } = await active.send('Browser.getWindowForTarget');
      await active.send('Browser.setWindowBounds', { windowId, bounds: { windowState: 'maximized' } });
      await delay(400);
    } catch { /* Some installed hosts do not expose window bounds. */ }
    const total = await evaluate(`document.querySelectorAll('#cards .card').length`);
    assert.ok(total > 0);
    const positions = () => evaluate(`JSON.stringify([...document.querySelectorAll('#cards .card')].map(c => [c.dataset.nodeId, c.style.left, c.style.top, c.style.width, c.offsetHeight]))`);
    const camera = () => evaluate(`(() => { const d=document.getElementById('viewport').dataset; return { x:Number(d.cameraX),y:Number(d.cameraY),k:Number(d.scale) }; })()`);
    const initialPositions = await positions();
    assert.ok(await evaluate(`(() => { const nodes=new Map([...document.querySelectorAll('#cards .card')].map(c=>[c.dataset.nodeId,c])); return [...document.querySelectorAll('#edges .link')].every(p => parseFloat(nodes.get(p.dataset.parent).style.left)+nodes.get(p.dataset.parent).offsetWidth < parseFloat(nodes.get(p.dataset.child).style.left)); })()`));
    assert.ok(await evaluate(`getComputedStyle(document.getElementById('viewport')).overflow === 'clip'`));
    assert.ok(await evaluate(`(() => {
      const cards=[...document.querySelectorAll('#cards .card:not(.removed)')],edges=[...document.querySelectorAll('#edges .link:not(.removed)')];
      const ranks=new Map(),columns=[...new Set(cards.map(c=>parseFloat(c.style.left)))].sort((a,b)=>a-b);
      for(let round=0;round<cards.length;round++) for(const c of cards) {
        if(ranks.has(c.dataset.nodeId)) continue;
        const parents=edges.filter(p=>p.dataset.child===c.dataset.nodeId).map(p=>p.dataset.parent);
        if(parents.every(id=>ranks.has(id))) ranks.set(c.dataset.nodeId,parents.length?1+Math.max(...parents.map(id=>ranks.get(id))):0);
      }
      return cards.every(c=>columns.indexOf(parseFloat(c.style.left))===ranks.get(c.dataset.nodeId));
    })()`), 'Each live node belongs in its earliest parent-permitted rank, not a shared-sink-biased column.');
    assert.ok(await evaluate(`(() => {
      const cards=[...document.querySelectorAll('#cards .card:not(.removed)')],root=cards.find(c=>c.classList.contains('manifesto'));
      const links=[...document.querySelectorAll('#edges .link:not(.removed)')];
      const children=cards.filter(c=>{const incoming=links.filter(p=>p.dataset.child===c.dataset.nodeId);return incoming.length===1&&incoming[0].dataset.parent===root.dataset.nodeId;});
      if(!children.length) return true;
      const low=Math.min(...children.map(c=>parseFloat(c.style.top))),high=Math.max(...children.map(c=>parseFloat(c.style.top)+c.offsetHeight));
      return high-low<=2*children.reduce((sum,c)=>sum+c.offsetHeight,0);
    })()`), 'Immediate origin branches must be compact vertically, not stretched to distant shared sinks.');
    const arrowJoins = () => evaluate(`(() => {
      if(document.querySelector('#edges circle, #edges marker')) return false;
      return [...document.querySelectorAll('#edges .link')].every(p=>{
        const head=[...document.querySelectorAll('#edges .arrow-head')].find(h=>h.dataset.parent===p.dataset.parent&&h.dataset.child===p.dataset.child);
        const n=head.getAttribute('d').match(/-?\\d+(?:\\.\\d+)?/g).map(Number),length=p.getTotalLength();
        const end=p.getPointAtLength(length),lead=p.getPointAtLength(length-1);
        const scale=Math.hypot(p.getScreenCTM().a,p.getScreenCTM().b);
        return Math.abs(end.x-n[0])<0.1 && Math.abs(end.y-n[3])<0.1 && Math.abs(lead.y-end.y)<0.1 && lead.x<end.x
          && parseFloat(getComputedStyle(p).strokeWidth)*scale>=1.59 && (n[2]-n[0])*scale>=5.99;
      });
    })()`);
    assert.ok(await arrowJoins(), 'Line ends must join the head base tangentially, with minimum screen strength.');
    const curveCollisions = () => evaluate(`(() => {
      const boxes=[...document.querySelectorAll('#cards .card')].map(c=>({id:c.dataset.nodeId,x:parseFloat(c.style.left),y:parseFloat(c.style.top),w:c.offsetWidth,h:c.offsetHeight}));
      const collisions=[];
      for(const path of document.querySelectorAll('#edges .link')) {
        const length=path.getTotalLength();
        for(let d=2;d<length;d+=8) {
          const p=path.getPointAtLength(d),before=path.getPointAtLength(d-1),after=path.getPointAtLength(Math.min(length,d+1));
          const dx=after.x-before.x,dy=after.y-before.y,norm=Math.hypot(dx,dy)||1,half=parseFloat(getComputedStyle(path).strokeWidth)/2;
          const samples=[p,{x:p.x-dy/norm*half,y:p.y+dx/norm*half},{x:p.x+dy/norm*half,y:p.y-dx/norm*half}];
          const box=boxes.find(b=>samples.some(q=>q.x>b.x+1&&q.x<b.x+b.w-1&&q.y>b.y+1&&q.y<b.y+b.h-1));
          if(box) {collisions.push({parent:path.dataset.parent,child:path.dataset.child,through:box.id});break;}
        }
      }
      return collisions;
    })()`);
    assert.deepEqual(await curveCollisions(), [], 'Curves must not cross node content.');
    await screenshot('origin-initial');
    // Actual browser event handling; no special production test commands.
    const beforeZoom = await camera();
    await evaluate(`(() => { const v=document.getElementById('viewport'),r=v.getBoundingClientRect(); v.dispatchEvent(new WheelEvent('wheel',{bubbles:true,cancelable:true,deltaY:-100,clientX:r.left+300,clientY:r.top+200})); })()`);
    await delay(200);
    const zoomed = await camera();
    assert.ok(zoomed.k > beforeZoom.k);
    assert.ok(Math.abs((300-beforeZoom.x)/beforeZoom.k - (300-zoomed.x)/zoomed.k) < 0.01);
    assert.equal(await positions(), initialPositions);
    await evaluate(`(() => { const v=document.getElementById('viewport'),r=v.getBoundingClientRect(); v.dispatchEvent(new MouseEvent('mousedown',{view:window,bubbles:true,cancelable:true,button:1,clientX:r.left+20,clientY:r.top+20})); window.dispatchEvent(new MouseEvent('mousemove',{view:window,bubbles:true,button:1,clientX:r.left+160,clientY:r.top+70})); window.dispatchEvent(new MouseEvent('mouseup',{view:window,bubbles:true,button:1,clientX:r.left+160,clientY:r.top+70})); })()`);
    const panned = await camera();
    assert.ok(Math.abs(panned.x - zoomed.x - 140) < 1);
    assert.ok(Math.abs(panned.y - zoomed.y - 50) < 1);
    assert.equal(await positions(), initialPositions);
    // Narrow the area itself; node positions must not wrap or change.
    await evaluate(`document.querySelector('.canvas-shell').style.width='520px'`);
    await delay(200);
    assert.equal(await positions(), initialPositions);
    assert.deepEqual(await camera(), panned);
    await evaluate(`document.querySelector('.canvas-shell').style.width=''`);
    await evaluate(`document.getElementById('frame-all').click()`);
    await delay(300); await screenshot('origin-overview');
    const overviewCamera = await camera();
    // Test the smallest camera scale, not just normal-sized nodes. Strokes and
    // arrow direction remain visible; the world and paths' DOM identities stay.
    const pathCount=await evaluate(`document.querySelectorAll('#edges .link').length`);
    await evaluate(`window.__testEdgeIdentity=[...document.querySelectorAll('#edges .link')]`);
    await evaluate(`(() => { const v=document.getElementById('viewport'),r=v.getBoundingClientRect(); v.dispatchEvent(new WheelEvent('wheel',{bubbles:true,cancelable:true,deltaY:6000,clientX:r.left+r.width/2,clientY:r.top+r.height/2})); })()`);
    await delay(350);
    assert.ok(Math.abs((await camera()).k-0.12)<0.0001);
    assert.ok(await arrowJoins(), 'Low-zoom arrows must still join correctly and keep their screen-pixel floor.');
    assert.equal(await evaluate(`document.querySelectorAll('#edges .link').length`),pathCount);
    assert.ok(await evaluate(`window.__testEdgeIdentity.every(p=>p.isConnected)`));
    await evaluate(`delete window.__testEdgeIdentity`);
    assert.equal(await positions(),initialPositions);
    assert.deepEqual(await curveCollisions(), [], 'Zoom compensation must not make strokes cut through node content.');
    await screenshot('origin-minimum-zoom');
    await evaluate(`document.getElementById('frame-all').click()`);
    await delay(300);
    await evaluate(`document.querySelector('#cards .card.manifesto').click()`);
    assert.ok(await evaluate(`document.querySelector('#cards .expanded').contains(document.getElementById('editor'))`));
    assert.equal(await evaluate(`document.querySelectorAll('aside').length`), 0);
    const branch = await evaluate(`(() => { const cards = [...document.querySelectorAll('[data-relation="child"]')].sort((a,b) => Number(b.dataset.downstream)-Number(a.dataset.downstream)); return cards[0]?.dataset.nodeId; })()`);
    assert.ok(branch);
    await evaluate(`document.querySelector('[data-node-id="' + ${JSON.stringify(branch)} + '"]').click()`);
    assert.ok(await evaluate(`document.querySelector('[data-relation="parent"] .distance-badge') !== null`));
    assert.ok(await evaluate(`document.querySelector('#cards .expanded').contains(document.getElementById('body'))`));
    assert.ok(await evaluate(`(() => { const focus=document.querySelector('.expanded'); return [...document.querySelectorAll('[data-relation="parent"]')].every(p=>parseFloat(p.style.left)+p.offsetWidth < parseFloat(focus.style.left)) && [...document.querySelectorAll('[data-relation="child"]')].every(c=>parseFloat(c.style.left)>parseFloat(focus.style.left)+focus.offsetWidth); })()`));
    const focusedPositions = await positions(), focusedCamera = await camera();
    await evaluate(`document.querySelector('.canvas-shell').style.width='600px'`);
    await delay(200);
    assert.equal(await positions(), focusedPositions);
    assert.deepEqual(await camera(), focusedCamera);
    await evaluate(`document.querySelector('.canvas-shell').style.width=''`);
    const beforeFormWheel = await camera();
    await evaluate(`document.getElementById('body').dispatchEvent(new WheelEvent('wheel',{bubbles:true,cancelable:true,deltaY:-120}))`);
    assert.deepEqual(await camera(), beforeFormWheel);
    assert.deepEqual(await curveCollisions(), [], 'Focused curves must not cross the form or neighbors.');
    assert.ok(await arrowJoins(), 'Focused connections must settle before the head.');
    await screenshot('origin-focused');
    // Resize the real textarea; verify links move with intrinsic (unscaled) bounds.
    await evaluate(`document.getElementById('body').style.height = '540px'`);
    await delay(250);
    const geometry = await evaluate(`(() => {
      const boxes = [...document.querySelectorAll('#cards .card')].map(card => ({ id:card.dataset.nodeId, x:parseFloat(card.style.left), y:parseFloat(card.style.top), w:card.offsetWidth, h:card.offsetHeight }));
      return [...document.querySelectorAll('#edges .link')].map(path => {
        const p=path.getPointAtLength(0),head=[...document.querySelectorAll('#edges .arrow-head')].find(h=>h.dataset.parent===path.dataset.parent&&h.dataset.child===path.dataset.child);
        const n=head.getAttribute('d').match(/-?\\d+(?:\\.\\d+)?/g).map(Number);
        return { start:{x:p.x,y:p.y}, end:{x:n[2],y:n[3]}, from:boxes.find(b=>b.id===path.dataset.parent), to:boxes.find(b=>b.id===path.dataset.child) };
      });
    })()`);
    assert.ok(geometry.length);
    for (const route of geometry) {
      assert.ok(Math.abs(route.start.x - route.from.x - route.from.w - 3) < 1);
      assert.ok(Math.abs(route.end.x - route.to.x + 3) < 1);
      assert.ok(route.start.y > route.from.y && route.start.y < route.from.y + route.from.h);
      assert.ok(route.end.y > route.to.y && route.end.y < route.to.y + route.to.h);
    }
    assert.ok(await arrowJoins(), 'Resized-form arrows must preserve tangent joins.');
    assert.deepEqual(await curveCollisions(), [], 'Resized-form routes must still avoid content.');
    await screenshot('origin-resized-form');
    // Also inspect a genuine multiple-parent/depth neighborhood; its skipped-rank
    // curves are a stronger fixture than the manifesto's mostly adjacent links.
    await evaluate(`document.getElementById('back').click()`);
    const multipleParent = await evaluate(`(() => {
      const cards=[...document.querySelectorAll('#cards .card')],links=[...document.querySelectorAll('#edges .link')];
      return cards.filter(c=>c.classList.contains('requirement')).map(c=>({id:c.dataset.nodeId,parents:links.filter(p=>p.dataset.child===c.dataset.nodeId).map(p=>cards.find(b=>b.dataset.nodeId===p.dataset.parent))}))
        .filter(c=>c.parents.length>=2&&new Set(c.parents.map(p=>p.dataset.distance)).size>=2).sort((a,b)=>b.parents.length-a.parents.length)[0]?.id;
    })()`);
    assert.ok(multipleParent,'Use an actual multiple-depth parent neighborhood.');
    await evaluate(`document.querySelector('[data-node-id="' + ${JSON.stringify(multipleParent)} + '"]').click()`);
    await evaluate(`document.getElementById('frame-all').click()`);
    await delay(300);
    assert.ok(await arrowJoins());
    assert.deepEqual(await curveCollisions(), [], 'Multiple-depth parent connections must clear intrinsic form/card bounds.');
    await screenshot('origin-multiple-parents');
    await evaluate(`document.getElementById('back').click()`);
    assert.equal(await evaluate(`document.querySelectorAll('#cards .card').length`), total);
    const restoredCamera = await camera();
    for(const key of ['x','y','k']) assert.ok(Math.abs(restoredCamera[key]-overviewCamera[key])<0.01);
    await evaluate(`document.getElementById('color-mode').value='distance'; document.getElementById('color-mode').dispatchEvent(new Event('change'))`);
    assert.ok(await evaluate(`document.getElementById('legend').textContent.includes('Shortest path')`));
    await evaluate(`document.querySelector('#cards .card.manifesto').click()`);
    assert.equal(await evaluate(`document.querySelectorAll('#parent-links li').length`), 0);
    assert.equal(await evaluate(`document.getElementById('parent-add-controls').hidden`), true);
    await evaluate(`document.getElementById('frame-all').click()`);
    await delay(300); await screenshot('origin-root-neighborhood');
    assert.ok(await arrowJoins());
    console.log(`SPECSPEC_REAL_UI_OK: ${total} nodes; earliest manifesto ranks, minimum screen stroke/head strength, circle-free tangent joins, LR layout, viewport invariance, pan/zoom, draft cameras, native gestures and resized curves.`);
  } catch (error) {
    try { await screenshot('origin-failure'); } catch { /* Keep the original failure. */ }
    throw error;
  } finally { clients.forEach(client => client.close()); }
};
