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
    const curveCollisions = () => evaluate(`(() => {
      const boxes=[...document.querySelectorAll('#cards .card')].map(c=>({id:c.dataset.nodeId,x:parseFloat(c.style.left),y:parseFloat(c.style.top),w:c.offsetWidth,h:c.offsetHeight}));
      const collisions=[];
      for(const path of document.querySelectorAll('#edges .link')) {
        const length=path.getTotalLength();
        for(let d=2;d<length;d+=8) {
          const p=path.getPointAtLength(d),box=boxes.find(b=>p.x>b.x+1&&p.x<b.x+b.w-1&&p.y>b.y+1&&p.y<b.y+b.h-1);
          if(box) {collisions.push({parent:path.dataset.parent,child:path.dataset.child,through:box.id});break;}
        }
      }
      return collisions;
    })()`);
    assert.deepEqual(await curveCollisions(), [], 'Curves must not cross node content.');
    await screenshot('canvas-initial');
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
    await delay(300); await screenshot('canvas-overview');
    const overviewCamera = await camera();
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
    await screenshot('canvas-focused');
    // Resize the real textarea; verify links move with intrinsic (unscaled) bounds.
    await evaluate(`document.getElementById('body').style.height = '540px'`);
    await delay(250);
    const geometry = await evaluate(`(() => {
      const boxes = [...document.querySelectorAll('#cards .card')].map(card => ({ id:card.dataset.nodeId, x:parseFloat(card.style.left), y:parseFloat(card.style.top), w:card.offsetWidth, h:card.offsetHeight }));
      return [...document.querySelectorAll('#edges .link')].map(path => { const p=path.getPointAtLength(0), q=path.getPointAtLength(path.getTotalLength()); return { start:{x:p.x,y:p.y}, end:{x:q.x,y:q.y}, from:boxes.find(b=>b.id===path.dataset.parent), to:boxes.find(b=>b.id===path.dataset.child) }; });
    })()`);
    assert.ok(geometry.length);
    for (const route of geometry) {
      assert.ok(Math.abs(route.start.x - route.from.x - route.from.w - 3) < 1);
      assert.ok(Math.abs(route.end.x - route.to.x + 9) < 1);
      assert.ok(route.start.y > route.from.y && route.start.y < route.from.y + route.from.h);
      assert.ok(route.end.y > route.to.y && route.end.y < route.to.y + route.to.h);
    }
    await evaluate(`document.getElementById('back').click()`);
    assert.equal(await evaluate(`document.querySelectorAll('#cards .card').length`), total);
    assert.deepEqual(await camera(), overviewCamera);
    await evaluate(`document.getElementById('color-mode').value='distance'; document.getElementById('color-mode').dispatchEvent(new Event('change'))`);
    assert.ok(await evaluate(`document.getElementById('legend').textContent.includes('Shortest path')`));
    await evaluate(`document.querySelector('#cards .card.manifesto').click()`);
    assert.equal(await evaluate(`document.querySelectorAll('#parent-links li').length`), 0);
    assert.equal(await evaluate(`document.getElementById('parent-add-controls').hidden`), true);
    await evaluate(`document.getElementById('frame-all').click()`);
    await delay(300); await screenshot('canvas-root-neighborhood');
    console.log(`SPECSPEC_REAL_UI_OK: ${total} nodes; LR layout, viewport invariance, pan/zoom anchoring, focus/back cameras, native form gestures, colors and resized curve endpoints.`);
  } catch (error) {
    try { await screenshot('canvas-failure'); } catch { /* Keep the original failure. */ }
    throw error;
  } finally { clients.forEach(client => client.close()); }
};
