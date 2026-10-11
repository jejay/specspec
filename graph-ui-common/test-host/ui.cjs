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
      } else if (message.method === 'Runtime.executionContextDestroyed') {
        this.contexts.delete(`${message.sessionId || ''}:${message.params.executionContextId}`);
      } else if (message.method === 'Runtime.executionContextsCleared' || message.method === 'Target.detachedFromTarget') {
        const session = message.params?.sessionId || message.sessionId;
        for (const [key, context] of this.contexts) if (context.session === session) this.contexts.delete(key);
      } else if (message.method === 'Target.attachedToTarget') {
        void this.send('Runtime.enable', {}, message.params.sessionId).catch(() => {});
      }
    });
  }
  async send(method, params = {}, sessionId, timeoutMs = 10_000) {
    await this.ready;
    const id = ++this.next;
    const result = new Promise((resolve, reject) => {
      const timer = setTimeout(() => { this.pending.delete(id); reject(new Error(`CDP timeout: ${method}`)); }, timeoutMs);
      this.pending.set(id, { resolve, reject, timer });
    });
    this.socket.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }));
    return result;
  }
  async evaluate(context, expression, timeoutMs) {
    const response = await this.send('Runtime.evaluate', { expression, contextId: context.id, returnByValue: true, awaitPromise: true }, context.session, timeoutMs);
    if (response.exceptionDetails) throw new Error(response.exceptionDetails.exception?.description || response.exceptionDetails.text);
    return response.result.value;
  }
  close() { this.socket.close(); }
}

exports.CDP = CDP;
exports.checkUI = async function checkUI(port, options = {}) {
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
              if (await client.evaluate(candidate, `typeof document !== 'undefined' && !!window.SpecSpecHost && !!document.querySelector('#cards .card.manifesto')`)) {
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
      await active.send('Page.bringToFront');
      await delay(400);
    } catch { /* Some installed hosts do not expose window bounds. */ }
    await options.before?.({ evaluate, screenshot, delay });
    const total = await evaluate(`document.querySelectorAll('#cards .card').length`);
    assert.ok(total > 0);
    assert.equal(await evaluate(`document.getElementById('accept')`), null);
    assert.deepEqual(await evaluate(`[...document.getElementById('color-mode').options].map(o=>o.value)`), ['distance', 'max-distance', 'type']);
    assert.deepEqual(await evaluate(`[...document.getElementById('color-mode').options].map(o=>o.textContent)`), ['Min. Distance to Manifesto', 'Max. Distance to Manifesto', 'Node type']);
    assert.equal(await evaluate(`document.querySelector('.distance-badge')`), null);
    assert.ok(await evaluate(`[...document.querySelectorAll('#cards .card')].every(c=>c.offsetHeight===112&&c.scrollHeight<=c.clientHeight+1)`), 'Shorter compact cards must fit two-line headlines and remaining badges.');
    assert.equal(await evaluate(`getComputedStyle(document.getElementById('graph')).willChange`), 'auto');
    assert.ok(await evaluate(`[...document.querySelectorAll('#cards .card')].every(c=>!('status' in c.dataset))`));
    assert.ok(await evaluate(`!document.getElementById('migrate')`), 'Superseded schema conversion is not offered.');
    assert.ok(await evaluate(`document.querySelector('[data-retired="true"] .retired-badge') !== null`), 'Withdrawal is labeled independently of Git newness.');
    const positions = () => evaluate(`JSON.stringify([...document.querySelectorAll('#cards .card')].map(c => [c.dataset.nodeId, c.style.left, c.style.top, c.style.width, c.offsetHeight]))`);
    const camera = () => evaluate(`(() => { const d=document.getElementById('viewport').dataset; return { x:Number(d.cameraX),y:Number(d.cameraY),k:Number(d.scale) }; })()`);
    async function checkHover(id, selector, image) {
      const paint = () => evaluate(`(() => {
        const paths=[...document.querySelectorAll('#edges .link')],heads=[...document.querySelectorAll('#edges .arrow-head')];
        return paths.map(p=>{const h=heads.find(h=>h.dataset.parent===p.dataset.parent&&h.dataset.child===p.dataset.child);
          return {parent:p.dataset.parent,child:p.dataset.child,key:JSON.stringify([p.dataset.parent,p.dataset.child]),
            stroke:getComputedStyle(p).stroke,fill:getComputedStyle(h).fill,width:getComputedStyle(p).strokeWidth,
            dash:getComputedStyle(p).strokeDasharray,d:p.getAttribute('d'),head:h.getAttribute('d'),
            highlighted:p.classList.contains('incident-highlight'),headHighlighted:h.classList.contains('incident-highlight'),
            darkened:p.classList.contains('hover-darkened'),headDarkened:h.classList.contains('hover-darkened')};});
      })()`);
      await evaluate(`document.getElementById('viewport').dispatchEvent(new PointerEvent('pointerleave'))`);
      const cardPaint = () => evaluate(`([...document.querySelectorAll('#cards .card')].map(c=>({id:c.dataset.nodeId,
        darkened:c.classList.contains('hover-darkened'),filter:getComputedStyle(c).filter,
        background:getComputedStyle(c).backgroundColor,accent:c.style.getPropertyValue('--node-accent')})))`);
      const before=await paint(), beforeCards=await cardPaint(), world=await positions(), transform=await camera();
      await evaluate(`window.__hoverPaths=[...document.querySelectorAll('#edges path')]`);
      await evaluate(`(() => {
        const card=[...document.querySelectorAll('#cards .card')].find(c=>c.dataset.nodeId===${JSON.stringify(id)});
        const target=${JSON.stringify(selector)}?card.querySelector(${JSON.stringify(selector)}):card;
        const r=target.getBoundingClientRect(),v=document.getElementById('viewport').getBoundingClientRect();
        const x=(Math.max(r.left,v.left)+Math.min(r.right,v.right))/2,y=(Math.max(r.top,v.top)+Math.min(r.bottom,v.bottom))/2;
        if(!(x>v.left&&x<v.right&&y>v.top&&y<v.bottom)) throw new Error('Hover target is outside the clipped viewport.');
        target.dispatchEvent(new PointerEvent('pointerover',{bubbles:true,pointerType:'mouse',clientX:x,clientY:y}));
      })()`);
      const after=await paint(), byKey=new Map(after.map(p=>[p.key,p]));
      const neighbors=new Set([id]);
      const channels = color => color.startsWith('color(srgb')
        ? color.match(/[\d.]+/g).slice(0,3).map(Number)
        : color.match(/[\d.]+/g).slice(0,3).map(n=>Number(n)/255);
      let incident=0;
      for(const old of before) {
        const p=byKey.get(old.key),related=old.parent===id||old.child===id;
        assert.equal(p.highlighted,related);assert.equal(p.headHighlighted,related);
        assert.equal(p.darkened,!related);assert.equal(p.headDarkened,!related);
        for(const key of ['width','dash','d','head']) assert.equal(p[key],old[key]);
        if(related) {incident++;neighbors.add(p.parent);neighbors.add(p.child);assert.notEqual(p.stroke,old.stroke);assert.notEqual(p.fill,old.fill);assert.equal(p.stroke,p.fill);}
        else {
          assert.notEqual(p.stroke,old.stroke);assert.notEqual(p.fill,old.fill);assert.equal(p.stroke,p.fill);
          assert.ok(channels(p.stroke).every((v,i)=>v<channels(old.stroke)[i]),'Non-incident ink must actually darken.');
        }
      }
      assert.ok(incident>0);
      for (const card of await cardPaint()) {
        const old=beforeCards.find(c=>c.id===card.id),darkened=!neighbors.has(card.id);
        assert.equal(card.darkened,darkened);assert.equal(card.filter,darkened?'brightness(0.45)':'none');
        assert.equal(card.accent,old.accent);
        if(card.id!==id) assert.equal(card.background,old.background);
      }
      assert.ok(after.slice(-incident).every(p=>p.highlighted),'Incident SVG pairs must paint last.');
      assert.equal(await positions(),world);assert.deepEqual(await camera(),transform);
      assert.ok(await evaluate(`window.__hoverPaths.every(p=>p.isConnected)`));
      if(image) await screenshot(image);
      await evaluate(`document.getElementById('viewport').dispatchEvent(new PointerEvent('pointerleave'))`);
      assert.deepEqual(await paint(),before,'Exiting hover restores computed paint and SVG order.');
      assert.ok((await cardPaint()).every(c=>!c.darkened&&c.filter==='none'),'Exiting hover removes every card filter.');
      await evaluate(`delete window.__hoverPaths`);
    }
    async function restoreActualSize(pose) {
      await evaluate(`document.getElementById('zoom-reset').click()`);
      // Background hosts can throttle animation frames; wait for actual completion
      // before a synthetic drag interrupts the reset transition.
      for (let i = 0; i < 100; i++) { if (Math.abs((await camera()).k - 1) < 0.001) break; await delay(50); }
      const now=await camera(),dx=pose.x-now.x,dy=pose.y-now.y;
      await evaluate(`(() => { const v=document.getElementById('viewport'),r=v.getBoundingClientRect(),x=r.left+10,y=r.top+10;
        v.dispatchEvent(new MouseEvent('mousedown',{view:window,bubbles:true,cancelable:true,button:1,clientX:x,clientY:y}));
        window.dispatchEvent(new MouseEvent('mousemove',{view:window,bubbles:true,button:1,clientX:x+${dx},clientY:y+${dy}}));
        window.dispatchEvent(new MouseEvent('mouseup',{view:window,bubbles:true,button:1,clientX:x+${dx},clientY:y+${dy}}));
      })()`);
      const restored=await camera();
      // Synthetic MouseEvent client positions are integer-quantized in Chromium.
      for(const key of ['x','y','k']) assert.ok(Math.abs(restored[key]-pose[key])<(key==='k'?0.001:1),`Camera restoration ${key}: ${JSON.stringify({pose,now,restored,dx,dy})}`);
    }
    async function checkHeadlineRendering() {
      const pose=await camera(),world=await positions();
      await evaluate(`window.__testHeadline=document.querySelector('#cards .card.manifesto strong')`);
      const style=()=>evaluate(`(() => {const h=window.__testHeadline,r=h.getBoundingClientRect();return {text:h.textContent,width:h.offsetWidth,height:h.offsetHeight,font:getComputedStyle(h).fontSize,screenWidth:r.width,screenHeight:r.height,willChange:getComputedStyle(document.getElementById('graph')).willChange};})()`);
      const normal=await style();
      const zoom=()=>evaluate(`(() => {const h=window.__testHeadline,r=h.getBoundingClientRect(),v=document.getElementById('viewport');v.dispatchEvent(new WheelEvent('wheel',{bubbles:true,cancelable:true,deltaY:-6000,clientX:r.left+r.width/2,clientY:r.top+r.height/2}));})()`);
      // A/B probe of the old compositor hint at the same pose; only this test
      // temporarily restores it. Production has no forced raster promotion.
      await evaluate(`document.getElementById('graph').style.willChange='transform'`); await delay(100);
      await zoom();await delay(250);
      const hintedPose=await camera(); assert.equal(hintedPose.k,2.5);
      await screenshot('headline-before-250');
      // Removing the hint at this exact pose isolates raster behavior from any
      // camera/font/layout change (including subpixel mouse-coordinate rounding).
      await evaluate(`document.getElementById('graph').style.willChange=''`);await delay(300);
      const high=await style();
      await screenshot('headline-after-250');
      assert.equal(high.willChange,'auto');assert.equal(high.font,normal.font);
      assert.equal(high.width,normal.width);assert.equal(high.height,normal.height);assert.equal(high.text,normal.text);
      // getBoundingClientRect also includes any host/webview CSS zoom; compare
      // screen ratios rather than assuming it equals unscaled offset dimensions.
      assert.ok(Math.abs(high.screenWidth-normal.screenWidth*hintedPose.k/pose.k)<1,JSON.stringify({normal,high,pose,hintedPose}));
      assert.ok(Math.abs(high.screenHeight-normal.screenHeight*hintedPose.k/pose.k)<1,JSON.stringify({normal,high,pose,hintedPose}));
      assert.equal(await positions(),world);
      for(const key of ['x','y','k']) assert.ok(Math.abs((await camera())[key]-hintedPose[key])<0.01,'Before/after text must have the same camera pose.');
      assert.ok(await evaluate(`window.__testHeadline===document.querySelector('#cards .card.manifesto strong')&&!document.querySelector('#cards canvas,#cards img')`));
      await restoreActualSize(pose);await evaluate(`delete window.__testHeadline`);
    }
    const initialPositions = await positions();
    assert.ok(await evaluate(`(() => { const nodes=new Map([...document.querySelectorAll('#cards .card')].map(c=>[c.dataset.nodeId,c])); return [...document.querySelectorAll('#edges .link:not(.removed)')].every(p => parseFloat(nodes.get(p.dataset.parent).style.left)+nodes.get(p.dataset.parent).offsetWidth < parseFloat(nodes.get(p.dataset.child).style.left)); })()`), 'Target relationships progress LR; removed references are overlays and may share or reverse columns.');
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
    await checkHeadlineRendering();
    assert.equal(await positions(),initialPositions);
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
    let overviewCamera = await camera();
    const hoverNode = await evaluate(`(() => {
      const paths=[...document.querySelectorAll('#edges .link')];
      const v=document.getElementById('viewport').getBoundingClientRect();
      return [...document.querySelectorAll('#cards .card.requirement')].find(c=>{const r=c.getBoundingClientRect();return r.right>v.left&&r.left<v.right&&r.bottom>v.top&&r.top<v.bottom&&paths.some(p=>p.dataset.parent===c.dataset.nodeId)&&paths.some(p=>p.dataset.child===c.dataset.nodeId);})?.dataset.nodeId;
    })()`);
    assert.ok(hoverNode);
    await checkHover(hoverNode, undefined, 'hover-overview');
    // CSS theme probes in the real browser; restore the installed host's theme.
    const oldStyle = await evaluate(`document.documentElement.getAttribute('style')`);
    const oldClass = await evaluate(`document.body.className`);
    try {
      for (const theme of ['vscode-dark', 'vscode-light', 'vscode-high-contrast', 'vscode-high-contrast-light']) {
        const light=theme.endsWith('light');
        await evaluate(`document.body.className=${JSON.stringify(theme)};
          document.documentElement.style.setProperty('--vscode-editor-background',${JSON.stringify(light?'#ffffff':'#1f1f1f')});
          document.documentElement.style.setProperty('--vscode-editor-foreground',${JSON.stringify(light?'#202020':'#cccccc')});
          document.documentElement.style.setProperty('--vscode-foreground',${JSON.stringify(light?'#202020':'#cccccc')});`);
        for (const mode of ['distance', 'max-distance', 'type']) {
          await evaluate(`document.getElementById('color-mode').value=${JSON.stringify(mode)};document.getElementById('color-mode').dispatchEvent(new Event('change'))`);
          assert.ok(await evaluate(`(() => {const c=document.querySelector('.card.manifesto'),s=getComputedStyle(c);
            const swatch=[...document.getElementById('legend').children].find(c=>/manifesto/i.test(c.textContent)).querySelector('i');
            return c.style.getPropertyValue('--node-accent')==='#d3d3d3'&&s.backgroundColor==='rgb(211, 211, 211)'&&s.color==='rgb(32, 32, 32)'&&getComputedStyle(swatch).backgroundColor==='rgb(211, 211, 211)';})()`));
        }
        await checkHover(hoverNode, undefined, theme==='vscode-light'?'hover-light-theme':undefined);
      }
    } finally {
      await evaluate(`document.body.className=${JSON.stringify(oldClass)};
        ${oldStyle===null?"document.documentElement.removeAttribute('style')":`document.documentElement.setAttribute('style',${JSON.stringify(oldStyle)})`};
        document.getElementById('color-mode').value='distance';document.getElementById('color-mode').dispatchEvent(new Event('change'));`);
    }
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
    await checkHover(hoverNode, undefined, 'hover-minimum-zoom');
    await evaluate(`document.getElementById('frame-all').click()`);
    await delay(300);
    // Compare against the most recent explicit framing, not the older pose before
    // minimum-zoom/reframing (host progress chrome can change available height).
    overviewCamera = await camera();
    await evaluate(`document.querySelector('#cards .card.manifesto').click()`);
    assert.ok(await evaluate(`document.querySelector('#cards .expanded').contains(document.getElementById('editor'))`));
    assert.equal(await evaluate(`getComputedStyle(document.querySelector('.card.manifesto.expanded')).backgroundColor`), 'rgb(211, 211, 211)');
    assert.equal(await evaluate(`document.querySelectorAll('aside').length`), 0);
    const branch = await evaluate(`(() => { const cards = [...document.querySelectorAll('[data-relation="child"]')].sort((a,b) => Number(b.dataset.downstream)-Number(a.dataset.downstream)); return cards[0]?.dataset.nodeId; })()`);
    assert.ok(branch);
    await evaluate(`document.querySelector('[data-node-id="' + ${JSON.stringify(branch)} + '"]').click()`);
    assert.equal(await evaluate(`document.querySelector('.distance-badge')`), null);
    assert.ok(await evaluate(`!document.getElementById('focus-context').textContent.match(/distance|hops/i)`));
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
    await checkHover(branch, '#body', 'hover-focused');
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
        .filter(c=>c.parents.length>=2&&new Set(c.parents.map(p=>p.dataset.minDistance)).size>=2).sort((a,b)=>b.parents.length-a.parents.length)[0]?.id;
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
    for(const key of ['x','y','k']) assert.ok(Math.abs(restoredCamera[key]-overviewCamera[key])<0.01,JSON.stringify({key,restoredCamera,overviewCamera}));
    await evaluate(`document.getElementById('color-mode').value='type'; document.getElementById('color-mode').dispatchEvent(new Event('change'))`);
    assert.ok(await evaluate(`document.getElementById('legend').textContent.includes('Existing node types')`));
    const paletteWorld=await positions(),paletteCamera=await camera();
    const minimum=await evaluate(`(() => {document.getElementById('color-mode').value='distance';document.getElementById('color-mode').dispatchEvent(new Event('change'));return [...document.querySelectorAll('#cards .card')].map(c=>[c.dataset.nodeId,c.style.getPropertyValue('--node-accent')]);})()`);
    assert.ok(await evaluate(`document.getElementById('legend').textContent.includes('Shortest directed path')`));
    await evaluate(`document.getElementById('color-mode').value='max-distance';document.getElementById('color-mode').dispatchEvent(new Event('change'))`);
    assert.ok(await evaluate(`document.getElementById('legend').textContent.includes('Longest directed path')`));
    const maximum=await evaluate(`[...document.querySelectorAll('#cards .card')].map(c=>[c.dataset.nodeId,c.style.getPropertyValue('--node-accent')])`);
    assert.ok(maximum.some(([id,color])=>minimum.find(([key])=>key===id)[1]!==color),'Unequal root paths must produce different selected fills.');
    assert.equal(await positions(),paletteWorld);assert.deepEqual(await camera(),paletteCamera);
    assert.equal(await evaluate(`document.querySelector('.distance-badge')`),null);
    assert.ok(await evaluate(`(() => {
      const all=[...document.querySelectorAll('#cards .card')];
      function bounds(base){
        const cards=all.filter(c=>!c.classList.contains(base?'added':'removed')),links=[...document.querySelectorAll(base?'#edges .link:not(.added)':'#edges .link:not(.removed)')],root=cards.find(c=>c.classList.contains('manifesto')).dataset.nodeId;
        const min=new Map([[root,0]]),max=new Map([[root,0]]),queue=[root];
        for(let i=0;i<queue.length;i++)for(const p of links.filter(p=>p.dataset.parent===queue[i]))if(!min.has(p.dataset.child)){min.set(p.dataset.child,min.get(queue[i])+1);queue.push(p.dataset.child);}
        for(let round=0;round<cards.length;round++)for(const c of cards){if(max.has(c.dataset.nodeId))continue;const parents=links.filter(p=>p.dataset.child===c.dataset.nodeId).map(p=>p.dataset.parent);if(parents.length&&parents.every(id=>max.has(id)))max.set(c.dataset.nodeId,1+Math.max(...parents.map(id=>max.get(id))));}
        return {min,max};
      }
      const target=bounds(false),base=bounds(true);
      return all.every(c=>{const b=c.classList.contains('removed')?base:target;return Number(c.dataset.minDistance)===b.min.get(c.dataset.nodeId)&&Number(c.dataset.maxDistance)===b.max.get(c.dataset.nodeId);});
    })()`),'Both modes use all revision relationships, not the visible placement backbone.');
    await screenshot('distance-maximum');
    await evaluate(`document.getElementById('color-mode').value='distance';document.getElementById('color-mode').dispatchEvent(new Event('change'))`);
    await screenshot('distance-minimum');
    await evaluate(`document.querySelector('#cards .card.manifesto').click()`);
    assert.equal(await evaluate(`document.querySelectorAll('#parent-links li').length`), 0);
    assert.equal(await evaluate(`document.getElementById('parent-add-controls').hidden`), true);
    assert.equal(await evaluate(`document.getElementById('retire').disabled`), true);
    assert.equal(await evaluate(`document.getElementById('save').textContent`), 'Save node');
    await evaluate(`document.getElementById('frame-all').click()`);
    await delay(300); await screenshot('origin-root-neighborhood');
    assert.ok(await arrowJoins());
    await options.after?.({ evaluate, screenshot, delay });
    console.log(`SPECSPEC_REAL_UI_OK: ${total} nodes; minimum/maximum revision-local distance, no hop badges, shorter cards/wider gaps, unhinted 250% native headlines, light-gray manifesto and legends, one-hop hover darkening with unchanged geometry and dark/light/contrast CSS probes, approval-free controls, withdrawal labels, three fill modes, earliest manifesto ranks, minimum screen stroke/head strength, circle-free tangent joins, LR layout, viewport invariance, pan/zoom, draft cameras, native gestures and resized curves.`);
  } catch (error) {
    try { await screenshot('origin-failure'); } catch { /* Keep the original failure. */ }
    throw error;
  } finally { clients.forEach(client => client.close()); }
};
