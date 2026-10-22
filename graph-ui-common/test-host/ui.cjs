/* Real Chromium/webview interaction via a loopback-only disposable host. */
const assert = require('node:assert/strict');
const { mkdirSync, writeFileSync } = require('node:fs');
const { join } = require('node:path');
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

class CDP {
  constructor(url, Socket = WebSocket) {
    this.socket = new Socket(url); this.next = 0; this.pending = new Map(); this.contexts = new Map();
    this.ready = new Promise((resolve, reject) => {
      this.socket.addEventListener('open', resolve, { once: true });
      this.fail = error => {
        this.closed = true; reject(error);
        for (const callback of this.pending.values()) { clearTimeout(callback.timer); callback.reject(error); }
        this.pending.clear(); this.contexts.clear();
      };
      this.socket.addEventListener('error', () => this.fail(new Error('CDP transport failed.')), { once: true });
      this.socket.addEventListener('close', () => this.fail(new Error('CDP connection closed; the host or target exited.')), { once: true });
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
    if (this.closed) throw new Error('CDP connection is closed.');
    const id = ++this.next;
    const result = new Promise((resolve, reject) => {
      const timer = setTimeout(() => { this.pending.delete(id); reject(new Error(`CDP timeout: ${method} ${String(params.expression || '').slice(0, 400)}`)); }, timeoutMs);
      this.pending.set(id, { resolve, reject, timer });
    });
    try { this.socket.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) })); }
    catch (error) { this.fail(error); }
    return result;
  }
  async evaluate(context, expression, timeoutMs) {
    const response = await this.send('Runtime.evaluate', { expression, contextId: context.id, returnByValue: true, awaitPromise: true }, context.session, timeoutMs);
    if (response.exceptionDetails) throw new Error(response.exceptionDetails.exception?.description || response.exceptionDetails.text);
    return response.result.value;
  }
  close() { this.fail(new Error('CDP client closed.')); this.socket.close(); }
}

async function foreground(client) {
  try {
    const { windowId } = await client.send('Browser.getWindowForTarget');
    await client.send('Browser.setWindowBounds', { windowId, bounds: { windowState: 'maximized' } });
  } catch { /* Electron versions may not implement optional Browser window commands. */ }
  // Foregrounding must still run when window sizing is unsupported.
  await client.send('Page.bringToFront').catch(() => {});
}

exports.CDP = CDP;
exports.foreground = foreground;
exports.checkUI = async function checkUI(port, options = {}) {
  const started = Date.now();
  const phase = name => console.log(`Host UI phase: ${name} (${Date.now() - started}ms elapsed)`);
  const clients = new Map(); let active, context;
  async function screenshot(name) {
    const directory = process.env.SPECSPEC_SCREENSHOT_DIR;
    if (!directory || !active || (process.env.SPECSPEC_SCREENSHOT_FILTER && !name.includes(process.env.SPECSPEC_SCREENSHOT_FILTER))) return;
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
    await foreground(active); await delay(400);
    // Geometry/gesture checks use a deterministic supported accessibility profile.
    // Normal-motion behavior remains covered by camera tests; do not rely on
    // background-host animation timing to reach a pose before sampling ink.
    await active.send('Emulation.setEmulatedMedia', {features:[{name:'prefers-reduced-motion',value:'reduce'}]}, context.session);
    phase('canvas');
    await require('./canvas.cjs').checkCanvas({ evaluate, screenshot,
      input: params => active.send('Input.dispatchMouseEvent', params, context.session) });
    phase('Git/theme setup');
    await options.before?.({ evaluate, screenshot, delay });
    phase('inline binding editor');
    await require('./inline.cjs').checkInline({ evaluate, screenshot, delay });
    const total = await evaluate(`document.querySelectorAll('#cards .card').length`);
    assert.ok(total > 0);
    assert.equal(await evaluate(`document.getElementById('accept')`), null);
    assert.ok(await evaluate(`!document.getElementById('slug')&&!document.getElementById('slug-label')`), 'Creation uses generated ID-only filenames with binding fields only.');
    assert.deepEqual(await evaluate(`[...document.getElementById('color-mode').options].map(o=>o.value)`), ['distance', 'max-distance', 'absolute-influence', 'relative-influence', 'log-absolute-influence', 'log-relative-influence', 'type', 'git-revision']);
    assert.deepEqual(await evaluate(`[...document.getElementById('color-mode').options].map(o=>o.textContent)`), ['Min. Distance to Manifesto', 'Max. Distance to Manifesto', 'Absolute influence', 'Relative influence', 'Log Absolute Influence', 'Log Relative Influence', 'Node type', 'Git/Revision Status']);
    assert.equal(await evaluate(`document.querySelector('.distance-badge')`), null);
    assert.ok(await evaluate(`[...document.querySelectorAll('#cards .card')].every(c=>c.offsetWidth===264&&c.offsetHeight===(c.classList.contains('manifesto')?264:112)&&c.scrollHeight<=c.clientHeight+1)`), 'Ordinary compact cards stay short; the manifesto is square and all content fits.');
    assert.equal(await evaluate(`getComputedStyle(document.getElementById('graph')).willChange`), 'auto');
    assert.ok(await evaluate(`[...document.querySelectorAll('#cards .card')].every(c=>!('status' in c.dataset))`));
    assert.ok(await evaluate(`!document.getElementById('migrate')`), 'Superseded schema conversion is not offered.');
    assert.ok(await evaluate(`document.querySelector('[data-retired],.retired-badge,#retire,#restore')===null`), 'No retirement workflow or persisted-state cues remain.');
    assert.ok(await evaluate(`document.getElementById('revision').textContent.startsWith('HEAD → ')`), 'Default workspace compares against HEAD.');
    const positions = () => evaluate(`JSON.stringify([...document.querySelectorAll('#cards .card')].map(c => [c.dataset.nodeId, c.style.left, c.style.top, c.style.width, c.offsetHeight]))`);
    const camera = () => evaluate(`(() => { const d=document.getElementById('viewport').dataset; return { x:Number(d.cameraX),y:Number(d.cameraY),k:Number(d.scale) }; })()`);
    const toOKLCH = `color => {
      const probe=document.createElement('span');probe.style.color='oklch(from '+color+' l c h)';document.body.append(probe);
      const result=getComputedStyle(probe).color;probe.remove();
      if(!result.startsWith('oklch(')) throw new Error('Relative OKLCH is unsupported: '+result);
      return result.match(/[\\d.e+-]+/g).slice(0,3).map(Number);
    }`;
    const sameColor = `(left,right) => {const c=document.createElement('canvas');c.width=c.height=1;const ctx=c.getContext('2d');
      const rgb=color=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=color;ctx.fillRect(0,0,1,1);return [...ctx.getImageData(0,0,1,1).data].join(',');};return rgb(left)===rgb(right);}`;
    const assertStrongerHue = (actual, base, message) => {
      assert.ok(actual[0]>base[0]+0.09, message+' must be brighter.');
      assert.ok(actual[1]>base[1]*1.29, message+' must have stronger chroma, not wash out.');
      const hue=Math.abs(actual[2]-base[2]);
      assert.ok(Math.min(hue,360-hue)<0.1, message+' must retain its hue.');
    };
    async function checkHover(id, selector, image) {
      // Keep the real pointer outside the graph while synthetic hover probes run;
      // closing a spotlight overlay must not re-hit-test an unrelated OS cursor.
      await active.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: 1, y: 1 }, context.session);
      const paint = () => evaluate(`(() => {
        const oklch=${toOKLCH};
        const paths=[...document.querySelectorAll('#edges .link')],heads=[...document.querySelectorAll('#edges .arrow-head')];
        return paths.map(p=>{const h=heads.find(h=>h.dataset.parent===p.dataset.parent&&h.dataset.child===p.dataset.child);
          return {parent:p.dataset.parent,child:p.dataset.child,key:JSON.stringify([p.dataset.parent,p.dataset.child]),
            stroke:getComputedStyle(p).stroke,fill:getComputedStyle(h).fill,width:getComputedStyle(p).strokeWidth,
            kind:['added','removed','draft'].find(kind=>p.classList.contains(kind))||'normal',
            oklch:oklch(getComputedStyle(p).stroke),opacity:getComputedStyle(p).opacity,
            dash:getComputedStyle(p).strokeDasharray,d:p.getAttribute('d'),head:h.getAttribute('d'),
            highlighted:p.classList.contains('incident-highlight'),headHighlighted:h.classList.contains('incident-highlight'),
            darkened:p.classList.contains('hover-darkened'),headDarkened:h.classList.contains('hover-darkened')};});
      })()`);
      await evaluate(`document.getElementById('viewport').dispatchEvent(new PointerEvent('pointerleave'))`);
      const cardPaint = () => evaluate(`(() => {const oklch=${toOKLCH};return [...document.querySelectorAll('#cards .card')].map(c=>({id:c.dataset.nodeId,
        darkened:c.classList.contains('hover-darkened'),filter:getComputedStyle(c).filter,
        background:getComputedStyle(c).backgroundColor,border:getComputedStyle(c).borderTopColor,
        borderOKLCH:oklch(getComputedStyle(c).borderTopColor),accentOKLCH:oklch(c.style.getPropertyValue('--node-accent')),
        manifesto:c.classList.contains('manifesto'),revisionColored:c.classList.contains('revision-colored'),hovered:c.classList.contains('node-hovered'),accent:c.style.getPropertyValue('--node-accent')}));})()`);
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
        if(related) {
          incident++;neighbors.add(p.parent);neighbors.add(p.child);
          assert.notEqual(p.stroke,old.stroke);assert.notEqual(p.fill,old.fill);assert.equal(p.stroke,p.fill);
          assert.equal(p.opacity,'1');
          if(p.kind!=='normal') assertStrongerHue(p.oklch,old.oklch,p.kind+' incident curve/head');
        }
        else {
          assert.notEqual(p.stroke,old.stroke);assert.notEqual(p.fill,old.fill);assert.equal(p.stroke,p.fill);
          assert.ok(channels(p.stroke).every((v,i)=>v<channels(old.stroke)[i]),'Non-incident ink must actually darken.');
        }
      }
      assert.ok(incident>0);
      for (const card of await cardPaint()) {
        const old=beforeCards.find(c=>c.id===card.id),darkened=!neighbors.has(card.id);
        assert.equal(card.darkened,darkened);assert.equal(card.filter,darkened?'brightness(0.45)':'none');
        assert.equal(card.hovered,card.id===id);
        if(card.id===id) {
          if(card.manifesto&&!card.revisionColored) assert.equal(card.border,'rgb(255, 255, 255)');
          else assertStrongerHue(card.borderOKLCH,card.accentOKLCH,'Non-manifesto border');
        }
        assert.equal(card.accent,old.accent);
        if(card.id!==id) assert.equal(card.background,old.background);
      }
      assert.ok(after.slice(-incident).every(p=>p.highlighted),'Incident SVG pairs must paint last.');
      assert.equal(await positions(),world);assert.deepEqual(await camera(),transform);
      assert.ok(await evaluate(`window.__hoverPaths.every(p=>p.isConnected)`));
      if(image) await screenshot(image);
      await evaluate(`document.getElementById('viewport').dispatchEvent(new PointerEvent('pointerleave'))`);
      assert.deepEqual(await paint(),before,'Exiting hover restores computed paint and SVG order.');
      assert.deepEqual(await cardPaint(),beforeCards,'Exiting hover restores all card paint, including semantic borders.');
      await evaluate(`delete window.__hoverPaths`);
    }
    async function checkSpotlight(id, selector, image) {
      const world=await positions(),pose=await camera();
      const editing=()=>evaluate(`JSON.stringify((({selected,view,colorMode,dirty,creating,originalNode,draft})=>({selected,view,colorMode,dirty,creating,originalNode,draft}))(window.SpecSpecHost.getState()))`);
      const saved=await editing();
      const geometry=()=>evaluate(`JSON.stringify([...document.querySelectorAll('#edges path')].map(p=>[p.dataset.parent,p.dataset.child,p.classList.contains('arrow-head'),p.getAttribute('d'),getComputedStyle(p).strokeWidth,getComputedStyle(p).strokeDasharray]).sort((a,b)=>JSON.stringify(a.slice(0,3)).localeCompare(JSON.stringify(b.slice(0,3)))))`);
      const paths=await geometry();
      const focus=await evaluate(`(() => {const e=document.activeElement;return {id:e.id,start:e.selectionStart,end:e.selectionEnd};})()`);
      const answers=await options.submitSpotlights(id);
      const section=`document.querySelector('[data-shot-id="${answers.at(-1).id}"]')`;
      for(let i=0;i<300&&!await evaluate(`!!${section}`);i++) await delay(100);
      assert.ok(await evaluate(`!!${section}`),'An external CLI shot must arrive through watching, without Refresh or polling.');
      assert.equal(await evaluate(`document.getElementById('annotations-panel').hidden`),true);
      assert.equal(await evaluate(`document.getElementById('annotation-arrival')`),null);
      assert.deepEqual(await evaluate(`(() => {const b=document.getElementById('spotlights-count'),s=getComputedStyle(b);return {hidden:b.hidden,text:b.textContent,background:s.backgroundColor,color:s.color,round:parseFloat(s.borderRadius)>parseFloat(s.height)/2};})()`),
        {hidden:false,text:'6',background:'rgb(198, 40, 40)',color:'rgb(255, 255, 255)',round:true});
      assert.equal(await evaluate(`document.getElementById('annotations-toggle').getAttribute('aria-label')`),'Spotlights, 6 new');
      assert.deepEqual(await evaluate(`(() => {const e=document.activeElement;return {id:e.id,start:e.selectionStart,end:e.selectionEnd};})()`),focus);
      assert.equal(await editing(),saved);assert.equal(await positions(),world);assert.deepEqual(await camera(),pose);assert.equal(await geometry(),paths);
      if(image) await screenshot(image+'-arrival-badge');
      await evaluate(`document.getElementById('annotations-toggle').click()`);
      assert.ok(await evaluate(`document.getElementById('spotlights-count').hidden`));
      assert.equal(await evaluate(`document.getElementById('annotations-heading').textContent`),'Spotlights');
      assert.equal(await evaluate(`document.querySelectorAll('#annotation-filter,.annotation-swatch,.annotation-members,#annotation-preview').length`),0);
      for(let index=0;index<answers.length;index++) {
        if(index) await evaluate(`document.getElementById('annotations-toggle').click()`);
        await evaluate(`document.querySelector('[data-shot-id="${answers[index].id}"]').click()`);
        for(let i=0;i<300&&!await evaluate(`window.SpecSpecHost.getState().annotationActive===${JSON.stringify(answers[index].id)}`);i++) await delay(100);
        assert.equal(await evaluate(`window.SpecSpecHost.getState().annotationActive`),answers[index].id,'Comparison loads before spotlight application.');
        const result=await evaluate(`(() => {
          const c=[...document.querySelectorAll('#cards .card')].find(c=>c.dataset.nodeId===${JSON.stringify(id)});
          const style=getComputedStyle(c),probe=document.createElement('span');
          const paint=getComputedStyle(document.getElementById('cards'));
          probe.style.outline=paint.getPropertyValue('--annotation-ring-width')+' solid white';probe.style.outlineOffset=paint.getPropertyValue('--annotation-ring-offset');document.body.append(probe);
          const expected=getComputedStyle(probe),expectedWidth=expected.outlineWidth,expectedOffset=expected.outlineOffset;probe.remove();
          return {label:c.dataset.annotationLabel,color:style.outlineColor,width:style.outlineWidth,offset:style.outlineOffset,expectedWidth,expectedOffset,description:c.getAttribute('aria-description')};
        })()`);
        assert.equal(result.label,'highlight');assert.equal(result.color,'rgb(255, 255, 255)');assert.equal(result.width,result.expectedWidth);assert.equal(result.offset,result.expectedOffset);assert.match(result.description,/Shift-click toggles/);
        await evaluate(`(() => {const c=[...document.querySelectorAll('#cards .card')].find(c=>c.dataset.nodeId===${JSON.stringify(id)});c.dispatchEvent(new PointerEvent('pointerover',{bubbles:true,pointerType:'mouse'}));})()`);
        assert.equal(await evaluate(`getComputedStyle([...document.querySelectorAll('#cards .card')].find(c=>c.dataset.nodeId===${JSON.stringify(id)})).outlineColor`),'rgb(255, 255, 255)');
        if(index===0&&image) await screenshot(image);
        await evaluate(`document.getElementById('viewport').dispatchEvent(new PointerEvent('pointerleave'))`);
        assert.ok(await evaluate(`document.getElementById('annotations-panel').hidden`));
        assert.equal(await evaluate(`window.SpecSpecHost.getState().view`),'overview');
        assert.ok(await evaluate(`(() => {const c=[...document.querySelectorAll('#cards .card')].find(c=>c.dataset.nodeId===${JSON.stringify(id)}),r=c.getBoundingClientRect(),v=document.getElementById('viewport').getBoundingClientRect();return Math.abs((r.left+r.right-v.left-v.right)/2)<1&&Math.abs((r.top+r.bottom-v.top-v.bottom)/2)<1;})()`),'Selection frames in the full canvas, without dropdown inset.');
      }
      const highlightPose=await camera(), highlightEditing=await editing();
      const clickHighlight=modifiers=>evaluate(`document.querySelector('[data-node-id="${id}"]').dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true,button:0,shiftKey:true,${modifiers}}))`);
      await clickHighlight('ctrlKey:true');
      assert.equal(await evaluate(`document.querySelector('[data-node-id="${id}"]').dataset.annotationLabel`),undefined);
      for(const on of [true,false,true,false,true]) {
        await clickHighlight('ctrlKey:false');
        assert.equal(await evaluate(`Boolean(document.querySelector('[data-node-id="${id}"]').dataset.annotationLabel)`),on);
      }
      const highlights=await evaluate(`window.SpecSpecHost.getState().annotationHighlights`);
      assert.deepEqual(highlights,[id]);
      const priorCount=await evaluate(`document.querySelectorAll('.annotation-label').length`);
      const ownerMessage=`Owner backchannel <img> ${id}`;
      await evaluate(`document.getElementById('annotations-toggle').click();document.getElementById('annotation-create').click()`);
      assert.ok(await evaluate(`document.getElementById('annotation-compose').open`));
      assert.ok(await evaluate(`document.getElementById('annotations-panel').hidden`));
      await evaluate(`document.getElementById('annotation-compose-cancel').click()`);
      assert.equal(await evaluate(`document.querySelectorAll('.annotation-label').length`),priorCount);
      await evaluate(`document.getElementById('annotations-toggle').click();document.getElementById('annotation-create').click();document.getElementById('annotation-message').value=${JSON.stringify(ownerMessage)}`);
      if(image) await screenshot(image+'-backchannel');
      await evaluate(`document.getElementById('annotation-compose-save').click()`);
      for(let i=0;i<300&&await evaluate(`document.getElementById('annotation-compose').open`);i++) await delay(100);
      assert.equal(await evaluate(`document.getElementById('annotation-compose').open`),false,await evaluate(`document.getElementById('annotation-compose-error').textContent`));
      assert.equal(await evaluate(`document.querySelectorAll('.annotation-label').length`),priorCount+1);
      assert.equal(await evaluate(`document.querySelector('#annotation-list img')`),null);
      const created=options.readSpotlights().find(s=>s.message===ownerMessage);
      assert.ok(created,'The external agent reads the UI-created message through spotlight show.');
      assert.deepEqual(created.comparison,{base:'HEAD',target:'workspace'});
      assert.deepEqual(created.nodes,highlights);
      assert.ok(created.workspace);assert.equal('groups' in created,false);
      assert.deepEqual(await evaluate(`window.SpecSpecHost.getState().annotationHighlights`),highlights);
      assert.deepEqual(await camera(),highlightPose); assert.equal(await editing(),highlightEditing);
      console.log(`Real spotlight backchannel passed for ${id}: Shift/Ctrl+Shift toggles, compose/cancel, metadata-only comparison persistence and agent CLI readback.`);
      await evaluate(`document.getElementById('annotations-toggle').click();document.getElementById('annotation-clear').click()`);
      const prior=JSON.parse(saved);
      if(prior.view==='focus') {
        await evaluate(`document.querySelector('[data-node-id="${prior.selected}"]').click()`);
      } else await evaluate(`document.getElementById('frame-all').click()`);
      if(selector) await evaluate(`document.querySelector(${JSON.stringify(selector)}).focus()`);
      await delay(250);
      assert.equal(await positions(),world);assert.equal(await editing(),saved);
      // Selection intentionally reframes. Its scale-dependent arrowheads/strokes
      // may change; restoring the prior view must preserve the form/world.
      assert.equal(await evaluate(`document.querySelector('[data-annotation-label]')`),null);
      assert.ok(await evaluate(`(() => {
        const viewport=document.getElementById('viewport'),targets=[viewport,...document.querySelectorAll('#cards .card,#cards textarea,#cards input,#cards select,#cards button:not(.card)')];
        const stop=event=>event.stopPropagation();viewport.addEventListener('contextmenu',stop);
        try {return targets.every(target=>{
          const event=new MouseEvent('contextmenu',{bubbles:true,cancelable:true,button:2});let preventedByRenderer=false;
          const prevent=event.preventDefault.bind(event);event.preventDefault=()=>{if(event.currentTarget===viewport)preventedByRenderer=true;prevent();};
          target.dispatchEvent(event);return !preventedByRenderer;
        });}finally{viewport.removeEventListener('contextmenu',stop);}
      })()`),'Renderer leaves native card/field/button/background context menus untouched.');
    }
    async function checkQuietArrows() {
      await active.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: 1, y: 1 }, context.session);
      await evaluate(`document.getElementById('viewport').dispatchEvent(new PointerEvent('pointerleave'))`);
      const pose=await camera(),world=await positions();
      assert.equal(pose.k,1,'Probe neutral ink from a settled actual-size camera.');
      await evaluate(`window.__quietPaths=[...document.querySelectorAll('#edges path')]`);
      const paint=()=>evaluate(`(() => {
        const oklch=${toOKLCH},svg=document.getElementById('edges'),values=[];
        const raw=document.createElement('span');raw.style.color='var(--edge-normal)';document.body.append(raw);
        const rawLightness=oklch(getComputedStyle(raw).color)[0];raw.remove();
        for(const kind of ['normal','normal incident-highlight','added','removed','draft']) {
          const p=document.createElementNS('http://www.w3.org/2000/svg','path'),h=p.cloneNode();
          p.setAttribute('class','link '+kind);h.setAttribute('class','arrow-head '+kind);svg.append(p,h);
          const a=getComputedStyle(p),b=getComputedStyle(h);
          values.push({kind,stroke:a.stroke,fill:b.fill,lightness:oklch(a.stroke)[0],opacity:a.opacity});p.remove();h.remove();
        }
        return {values,rawLightness,actual:getComputedStyle(svg.querySelector('.link.normal')).stroke};
      })()`);
      const samples=[];
      for(const stage of ['actual','intermediate','minimum']) {
        if(stage==='intermediate') await evaluate(`for(let i=0;i<3;i++)document.getElementById('zoom-out').click()`);
        if(stage==='minimum') await evaluate(`(() => {const v=document.getElementById('viewport'),r=v.getBoundingClientRect();v.dispatchEvent(new WheelEvent('wheel',{bubbles:true,cancelable:true,deltaY:6000,clientX:r.left+r.width/2,clientY:r.top+r.height/2}));})()`);
        await delay(100);const value=await paint();samples.push(value);
        for(const pair of value.values) {assert.equal(pair.stroke,pair.fill);assert.equal(pair.opacity,'1');}
        assert.equal(value.actual,value.values[0].stroke,'The actual ordinary curve uses the same paired neutral ink.');
        if(samples.length===1) assert.ok(value.values[0].lightness<value.rawLightness,'Resting ordinary ink is darker than the theme neutral.');
        else {
          assert.ok(value.values[0].lightness<samples.at(-2).values[0].lightness,'Zooming out darkens ordinary curves and heads further.');
          assert.deepEqual(value.values.slice(1),samples[0].values.slice(1),'Diff/draft and incident-hover inks stay independent of neutral zoom dimming.');
        }
        assert.ok(await arrowJoins());assert.equal(await positions(),world);
        assert.ok(await evaluate(`window.__quietPaths.every(p=>p.isConnected)`));
        await screenshot('spotlights-quiet-arrows-'+stage);
      }
      assert.equal((await camera()).k,0.12);
      await restoreActualSize(pose);await evaluate(`delete window.__quietPaths`);
    }
    async function checkHoverPalette() {
      // Real browser CSS probes cover every colored link kind (including draft),
      // yellow/type/distance borders, and each node Git state without graph mutation.
      const values=await evaluate(`(() => {
        const oklch=${toOKLCH},results=[];
        for(const kind of ['added','removed','draft']) {
          const p=document.createElementNS('http://www.w3.org/2000/svg','path'),h=p.cloneNode();
          p.setAttribute('class','link '+kind);h.setAttribute('class','arrow-head '+kind);
          document.getElementById('edges').append(p,h);
          const base=oklch(getComputedStyle(p).stroke);
          p.classList.add('incident-highlight');h.classList.add('incident-highlight');
          results.push({label:kind+' probe',base,actual:oklch(getComputedStyle(p).stroke),paired:getComputedStyle(p).stroke===getComputedStyle(h).fill});
          p.remove();h.remove();
        }
        for(const accent of ['#e5be32',...window.SpecSpecGraph.RAINBOW_COLORS,...Object.values(window.SpecSpecGraph.TYPE_COLORS).filter(c=>c!=='#d3d3d3')]) {
          for(const kind of ['normal','changed','removed','added','source-changed']) for(const expanded of [false,true]) for(const type of ['requirement','implementation','manifesto revision-colored']) {
            const c=document.createElement('div');c.className='card '+type+' '+kind+(expanded?' expanded':'');
            c.style.setProperty('--node-accent',accent);document.getElementById('cards').append(c);
            const resting=getComputedStyle(c).borderTopColor;c.classList.add('node-hovered');
            results.push({label:accent+' '+kind+(expanded?' expanded':''),base:oklch(accent),actual:oklch(getComputedStyle(c).borderTopColor),paired:true});
            c.classList.remove('node-hovered');if(getComputedStyle(c).borderTopColor!==resting) throw new Error('Border failed to restore');c.remove();
          }
        }
        return results;
      })()`);
      for(const value of values) {assert.ok(value.paired,'Curve/head ink must match');assertStrongerHue(value.actual,value.base,value.label);}
    }
    async function restoreActualSize(pose) {
      // Deterministic restoration uses the existing accessibility branch, not a
      // weakened pose assertion or production camera change. Other probes retain
      // normal motion; background Electron animation frames can be throttled.
      await active.send('Emulation.setEmulatedMedia', {features:[{name:'prefers-reduced-motion',value:'reduce'}]}, context.session);
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
    async function checkShapes() {
      const shapes=await evaluate(`(() => {
        const inside=(rect,circle,gap)=>{const cx=circle.left+circle.width/2,cy=circle.top+circle.height/2,r=circle.width/2;
          return [[rect.left,rect.top],[rect.right,rect.top],[rect.right,rect.bottom],[rect.left,rect.bottom]].every(([x,y])=>Math.hypot(x-cx,y-cy)<=r-gap);};
        return [...document.querySelectorAll('#cards .card')].map(c=>{
          const s=getComputedStyle(c),circle=c.classList.contains('manifesto'),expanded=c.classList.contains('expanded'),r=c.getBoundingClientRect(),scale=r.width/c.offsetWidth;
          const form=expanded&&circle?c.querySelector('.node-settings'):null,mark=c.querySelector('.git-corner');
          const content=[...c.children].filter(e=>e!==mark&&e.getClientRects().length);
          return {type:circle?'manifesto':c.classList.contains('implementation')?'implementation':'requirement',expanded,radius:s.borderRadius,w:c.offsetWidth,h:c.offsetHeight,
            square:Math.abs(r.width-r.height)<1,contentFits:!circle||content.every(e=>inside(e.getBoundingClientRect(),r,(form?12:4)*scale)),
            markerFits:!circle||!mark||inside(mark.getBoundingClientRect(),r,4*scale),
            formWidth:form?.offsetWidth,expected:form?window.SpecSpecGraph.manifestoDiameter(822,Math.max(form.offsetHeight,form.scrollHeight)):undefined};
        });
      })()`);
      for(const s of shapes) {
        assert.equal(s.radius,{manifesto:'50%',requirement:'24px',implementation:'0px'}[s.type],JSON.stringify(s));
        if(s.type==='manifesto') {
          assert.equal(s.w,s.h);assert.ok(s.square&&s.contentFits&&s.markerFits,JSON.stringify(s));
          if(s.expanded){assert.equal(s.formWidth,822);assert.ok(Math.abs(s.w-s.expected)<=1,JSON.stringify(s));}
          else assert.equal(s.w,264);
        } else {assert.equal(s.w,s.expanded?860:264);if(!s.expanded)assert.equal(s.h,112);}
      }
    }
    await checkShapes();await screenshot('node-shapes-compact');
    const implementation=await evaluate(`document.querySelector('#cards .card.implementation').dataset.nodeId`);
    await evaluate(`document.querySelector('[data-node-id="'+${JSON.stringify(implementation)}+'"]').click()`);await delay(100);
    await checkShapes();await evaluate(`document.getElementById('frame-node').click()`);await delay(300);
    await screenshot('node-shapes-expanded-implementation');
    assert.ok(await evaluate(`document.querySelector('#source-links button')`),'Implementation source hints are navigable.');
    phase('historical source preview');
    await evaluate(`document.querySelector('#source-links button').click()`);
    for(let i=0;i<100;i++){if(await evaluate(`document.getElementById('source-preview').open`))break;await delay(100);}
    assert.ok(await evaluate(`document.getElementById('source-preview').open&&document.getElementById('source-preview-code').textContent.length>0`),'Actual source blob/working region preview loads: '+JSON.stringify(await evaluate(`({message:document.getElementById('message').textContent,open:document.getElementById('source-preview').open,identity:document.getElementById('identity').textContent,source:document.getElementById('source-links').textContent})`)));
    assert.ok(await evaluate(`!document.getElementById('source-preview-code').querySelector('script,img,iframe')`),'Code preview stays literal.');
    await screenshot('source-region-preview');await evaluate(`document.getElementById('close-source-preview').click()`);
    await evaluate(`document.getElementById('back').click()`);await checkShapes();
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
      const boxes=[...document.querySelectorAll('#cards .card')].map(c=>({id:c.dataset.nodeId,x:parseFloat(c.style.left),y:parseFloat(c.style.top),w:c.offsetWidth,h:c.offsetHeight,circle:c.classList.contains('manifesto'),radius:parseFloat(getComputedStyle(c).borderTopLeftRadius)}));
      const inside=(b,q)=>{
        if(!(q.x>b.x+1&&q.x<b.x+b.w-1&&q.y>b.y+1&&q.y<b.y+b.h-1))return false;
        if(b.circle)return ((q.x-b.x-b.w/2)/(b.w/2-1))**2+((q.y-b.y-b.h/2)/(b.h/2-1))**2<1;
        const r=Math.min(b.radius,b.w/2,b.h/2);
        if(r===0)return true; // The preceding inset bounding check covers a square.
        const cx=Math.max(b.x+r,Math.min(b.x+b.w-r,q.x)),cy=Math.max(b.y+r,Math.min(b.y+b.h-r,q.y));
        return Math.hypot(q.x-cx,q.y-cy)<r-1;
      };
      const square={x:0,y:0,w:20,h:20,circle:false,radius:0};
      if(!inside(square,{x:10,y:10})||inside(square,{x:21,y:10}))throw new Error('Square collision mask must include its interior, not its exterior.');
      const collisions=[];
      for(const path of document.querySelectorAll('#edges .link')) {
        const length=path.getTotalLength();
        for(let d=2;d<length;d+=8) {
          const p=path.getPointAtLength(d),before=path.getPointAtLength(d-1),after=path.getPointAtLength(Math.min(length,d+1));
          const dx=after.x-before.x,dy=after.y-before.y,norm=Math.hypot(dx,dy)||1,half=parseFloat(getComputedStyle(path).strokeWidth)/2;
          const samples=[p,{x:p.x-dy/norm*half,y:p.y+dx/norm*half},{x:p.x+dy/norm*half,y:p.y-dx/norm*half}];
          const box=boxes.find(b=>samples.some(q=>inside(b,q)));
          if(box) {collisions.push({parent:path.dataset.parent,child:path.dataset.child,through:box.id});break;}
        }
      }
      return collisions;
    })()`);
    assert.deepEqual(await curveCollisions(), [], 'Curves must not cross node content.');
    await screenshot('origin-initial');
    await checkHeadlineRendering();
    await checkQuietArrows();
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
    phase('compact/manifesto Spotlights');
    await checkSpotlight(hoverNode,undefined,'spotlights-compact');
    const labelRoot=await evaluate(`document.querySelector('#cards .card.manifesto').dataset.nodeId`);
    await checkSpotlight(labelRoot,undefined,'spotlights-manifesto');
    await checkHover(hoverNode, undefined, 'hover-overview');
    for(const kind of ['added','changed','removed']) {
      const id=await evaluate(`document.querySelector('#cards .card.${kind}').dataset.nodeId`);
      await checkHover(id,undefined,'hover-'+kind);
    }
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
          await evaluate(`document.getElementById('zoom-reset').click();document.getElementById('color-mode').value=${JSON.stringify(mode)};document.getElementById('color-mode').dispatchEvent(new Event('change'))`);
          assert.ok(await evaluate(`(() => {const c=document.querySelector('.card.manifesto'),s=getComputedStyle(c);
            const swatch=[...document.getElementById('legend').children].find(c=>/manifesto/i.test(c.textContent)).querySelector('i');
            const probe=document.createElement('span');probe.style.background=${JSON.stringify(theme.includes('contrast')?'var(--vscode-editor-background)':'color-mix(in srgb, #d3d3d3 15%, var(--vscode-editor-background))')};probe.style.color='var(--vscode-foreground)';document.body.append(probe);
            const matches=(${sameColor})(s.backgroundColor,getComputedStyle(probe).backgroundColor)&&s.color===getComputedStyle(probe).color;probe.remove();
            return matches&&c.style.getPropertyValue('--node-accent')==='#d3d3d3'&&getComputedStyle(swatch).backgroundColor==='rgb(211, 211, 211)';})()`),`Actual-size manifesto paint matches its theme and legend in ${theme}/${mode}.`);
        }
        await evaluate(`document.getElementById('frame-all').click()`);
        await checkHover(hoverNode, undefined, theme==='vscode-light'?'hover-light-theme':undefined);
        await checkHoverPalette();
        const rootId=await evaluate(`document.querySelector('.card.manifesto').dataset.nodeId`);
        await checkHover(rootId, undefined, theme==='vscode-dark'?'hover-gray-manifesto':undefined);
        await evaluate(`document.getElementById('zoom-reset').click();document.getElementById('color-mode').value='git-revision';document.getElementById('color-mode').dispatchEvent(new Event('change'))`);
        assert.ok(await evaluate(`(() => {
          const model=window.SpecSpecGraph,root=document.querySelector('.card.manifesto');
          const legend=document.getElementById('legend').textContent;
          return root.style.getPropertyValue('--node-accent')===model.REVISION_COLORS.changed
            &&root.classList.contains('revision-colored')
            &&[...document.querySelectorAll('#cards .card')].every(c=>{
              const kind=['added','changed','removed','source-changed'].find(k=>c.classList.contains(k))||'unchanged';
              const accent=model.REVISION_COLORS[kind];
              const probe=document.createElement('span');probe.style.background=${JSON.stringify(theme.includes('contrast')?'var(--vscode-editor-background)':'color-mix(in srgb, var(--accent) 15%, var(--vscode-editor-background))')};
              probe.style.setProperty('--accent',accent);document.body.append(probe);
              const matches=c.style.getPropertyValue('--node-accent')===accent&&(${sameColor})(getComputedStyle(c).backgroundColor,getComputedStyle(probe).backgroundColor);probe.remove();return matches;
            })&&legend.includes('A · Added')&&legend.includes('M · Modified')&&legend.includes('D · Deleted')
            &&!legend.includes('R · Renamed')&&!legend.includes('Manifesto · 0 hops');
        })()`),'Revision fills/legend match comparison kinds, including the modified manifesto.');
        await evaluate(`document.getElementById('frame-all').click()`);
        await checkHover(rootId,undefined,theme==='vscode-dark'?'hover-revision-manifesto':undefined);
        await checkHover(hoverNode);
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
    await delay(100);await checkShapes();
    const textFit = await evaluate(`(() => {
      const body=document.getElementById('body'),content=body.querySelector('.cm-content'),gutter=body.querySelector('.cm-gutters');
      const original=body.style.fontSize,results=[];
      try {
        for(const size of [13,14,16]) {
          body.style.fontSize=size+'px';
          const span=document.createElement('span');span.style.cssText='position:absolute;white-space:pre;';span.style.font=getComputedStyle(content).font;span.textContent='M'.repeat(80);body.querySelector('.cm-scroller').append(span);
          const inkWidth=span.offsetWidth;span.remove();
          const available=body.clientWidth-gutter.offsetWidth-12;
          results.push({size,available,inkWidth,editorFits:inkWidth<=available});
        }
      } finally {body.style.fontSize=original;}
      return results;
    })()`);
    assert.ok(textFit.every(r=>r.editorFits),`80-column text must fit the inline editor: ${JSON.stringify(textFit)}`);
    await delay(100);await checkShapes();
    const circleWidth=await evaluate(`document.querySelector('.card.manifesto.expanded').offsetWidth`);
    await evaluate(`document.getElementById('body').style.height='540px'`);await delay(250);
    await checkShapes();
    assert.ok(await evaluate(`document.querySelector('.card.manifesto.expanded').offsetWidth`)>circleWidth,'Resizing the inline root editor grows its circle.');
    assert.ok(await arrowJoins());assert.deepEqual(await curveCollisions(),[]);
    await evaluate(`document.getElementById('body').style.height=''`);await delay(250);
    await checkShapes();assert.equal(await evaluate(`document.querySelector('.card.manifesto.expanded').offsetWidth`),circleWidth);
    await evaluate(`document.getElementById('frame-node').click()`);await delay(300);
    await screenshot('roomier-markdown-root');await screenshot('node-shapes-expanded-manifesto');
    assert.equal(await evaluate(`document.querySelectorAll('aside:not(#annotations-panel)').length`), 0);
    assert.ok(await evaluate(`document.getElementById('annotations-panel').hidden&&!document.getElementById('annotations-panel').contains(document.getElementById('editor'))`));
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
    // Resize the inline editor; verify links move with intrinsic (unscaled) bounds.
    await evaluate(`document.getElementById('body').style.height = '540px'`);
    await delay(250);
    const geometry = await evaluate(`(() => {
      const boxes = [...document.querySelectorAll('#cards .card')].map(card => ({ id:card.dataset.nodeId, x:parseFloat(card.style.left), y:parseFloat(card.style.top), w:card.offsetWidth, h:card.offsetHeight, circle:card.classList.contains('manifesto'), radius:parseFloat(getComputedStyle(card).borderTopLeftRadius) }));
      return [...document.querySelectorAll('#edges .link')].map(path => {
        const p=path.getPointAtLength(0),head=[...document.querySelectorAll('#edges .arrow-head')].find(h=>h.dataset.parent===path.dataset.parent&&h.dataset.child===path.dataset.child);
        const n=head.getAttribute('d').match(/-?\\d+(?:\\.\\d+)?/g).map(Number);
        return { start:{x:p.x,y:p.y}, end:{x:n[2],y:n[3]}, from:boxes.find(b=>b.id===path.dataset.parent), to:boxes.find(b=>b.id===path.dataset.child) };
      });
    })()`);
    assert.ok(geometry.length);
    const boundary=(b,y,right)=>{
      let inset;
      if(b.circle)inset=b.w/2*(1-Math.sqrt(1-((y-b.y-b.h/2)/(b.h/2))**2));
      else {const r=Math.min(b.radius,b.w/2,b.h/2),dy=Math.max(0,r-Math.min(y-b.y,b.y+b.h-y));inset=r-Math.sqrt(r*r-dy*dy);}
      return right?b.x+b.w-inset:b.x+inset;
    };
    for (const route of geometry) {
      assert.ok(Math.abs(route.start.x - boundary(route.from,route.start.y,true) - 3) < 1);
      assert.ok(Math.abs(route.end.x - boundary(route.to,route.end.y,false) + 3) < 1);
      assert.ok(route.start.y > route.from.y && route.start.y < route.from.y + route.from.h);
      assert.ok(route.end.y > route.to.y && route.end.y < route.to.y + route.to.h);
    }
    await checkShapes();
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
    assert.ok(await evaluate(`document.getElementById('legend').textContent==='manifestorequirementimplementation'`));
    const paletteWorld=await positions(),paletteCamera=await camera();
    const minimum=await evaluate(`(() => {document.getElementById('color-mode').value='distance';document.getElementById('color-mode').dispatchEvent(new Event('change'));return [...document.querySelectorAll('#cards .card')].map(c=>[c.dataset.nodeId,c.style.getPropertyValue('--node-accent')]);})()`);
    assert.ok(await evaluate(`document.querySelector('#legend .legend-help')===null&&document.getElementById('legend').textContent.includes('1 hop')`));
    await evaluate(`document.getElementById('color-mode').value='max-distance';document.getElementById('color-mode').dispatchEvent(new Event('change'))`);
    assert.ok(await evaluate(`document.querySelector('#legend .legend-help')===null&&document.getElementById('legend').textContent.includes(' hops')`));
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
    const influenceExpected=await evaluate(`(() => {
      const all=[...document.querySelectorAll('#cards .card')],model=window.SpecSpecGraph;
      function reference(base){
        const cards=all.filter(c=>!c.classList.contains(base?'added':'removed')),ids=new Set(cards.map(c=>c.dataset.nodeId));
        const links=[...document.querySelectorAll(base?'#edges .link:not(.added)':'#edges .link:not(.removed)')]
          .map(p=>[p.dataset.parent,p.dataset.child]).filter(([a,b])=>ids.has(a)&&ids.has(b));
        const counts=new Map(cards.map(c=>{const id=c.dataset.nodeId,seen=new Set([id]),stack=[id];
          while(stack.length){const current=stack.pop();for(const [a,b] of links)if(a===current&&!seen.has(b)){seen.add(b);stack.push(b);}}
          return [id,seen.size];}));
        const root=cards.find(c=>c.classList.contains('manifesto')).dataset.nodeId,depths=new Map([[root,0]]);
        for(let round=0;round<cards.length;round++)for(const id of ids){if(depths.has(id))continue;const parents=links.filter(([,b])=>b===id).map(([a])=>a);
          if(parents.length&&parents.every(p=>depths.has(p)))depths.set(id,1+Math.max(...parents.map(p=>depths.get(p))));}
        const maximum=Math.max(1,...[...ids].filter(id=>id!==root).map(id=>counts.get(id)));
        return new Map([...ids].map(id=>{const peers=[...ids].filter(p=>depths.get(p)===depths.get(id)).map(p=>counts.get(p));
          const lo=Math.min(...peers),hi=Math.max(...peers),logCount=Math.log(counts.get(id));
          const logMaximum=Math.log(maximum),logLo=Math.log(lo),logHi=Math.log(hi);
          return [id,{'absolute-influence':id===root?'#d3d3d3':model.influenceColor(maximum>1?(counts.get(id)-1)/(maximum-1):0),
            'relative-influence':id===root?'#d3d3d3':model.influenceColor(hi>lo?(counts.get(id)-lo)/(hi-lo):0),
            'log-absolute-influence':id===root?'#d3d3d3':model.influenceColor(logMaximum?logCount/logMaximum:0),
            'log-relative-influence':id===root?'#d3d3d3':model.influenceColor(logHi>logLo?(logCount-logLo)/(logHi-logLo):0)}];}));
      }
      const target=reference(false),base=reference(true);
      return Object.fromEntries(all.map(c=>[c.dataset.nodeId,(c.classList.contains('removed')?base:target).get(c.dataset.nodeId)]));
    })()`);
    for(const mode of ['absolute-influence','relative-influence','log-absolute-influence','log-relative-influence']) {
      await evaluate(`document.getElementById('color-mode').value=${JSON.stringify(mode)};document.getElementById('color-mode').dispatchEvent(new Event('change'))`);
      assert.ok(await evaluate(`(() => {const expected=${JSON.stringify(influenceExpected)},mode=${JSON.stringify(mode)};
        const gradient=document.querySelector('#legend .influence-gradient');
        return [...document.querySelectorAll('#cards .card')].every(c=>c.style.getPropertyValue('--node-accent')===expected[c.dataset.nodeId][mode])
          &&getComputedStyle(gradient).backgroundImage.includes('linear-gradient')&&gradient.offsetWidth>=100
          &&document.querySelector('#legend .legend-help')===null;})()`),'Influence colors use independent full-revision descendant/cohort calculations and a painted continuous legend.');
      assert.equal(await evaluate(`window.SpecSpecHost.getState().colorMode`),mode);
      assert.equal(await positions(),paletteWorld);assert.deepEqual(await camera(),paletteCamera);
      await screenshot(mode+'-colors');
      console.log(`${mode}: independent revision-local counts/scaling, continuous gradient, preference and unchanged world/camera passed.`);
    }
    const statusWorld=await positions(),statusCamera=await camera();
    await evaluate(`document.getElementById('color-mode').value='git-revision';document.getElementById('color-mode').dispatchEvent(new Event('change'))`);
    assert.equal(await positions(),statusWorld);assert.deepEqual(await camera(),statusCamera);
    assert.equal(await evaluate(`window.SpecSpecHost.getState().colorMode`),'git-revision');
    await screenshot('git-revision-colors');
    await evaluate(`document.querySelector('#cards .card.manifesto').click()`);
    assert.equal(await evaluate(`document.querySelector('.card.manifesto.expanded').style.getPropertyValue('--node-accent')`),await evaluate(`window.SpecSpecGraph.REVISION_COLORS.changed`));
    await evaluate(`document.getElementById('frame-node').click()`);await delay(300);
    const expandedRoot=await evaluate(`document.querySelector('.card.manifesto').dataset.nodeId`);
    phase('expanded Spotlight');
    await checkSpotlight(expandedRoot,'#title','spotlights-expanded');
    await checkHover(expandedRoot,'#body','hover-revision-expanded-root');
    await evaluate(`document.getElementById('color-mode').value='distance';document.getElementById('color-mode').dispatchEvent(new Event('change'))`);
    assert.equal(await evaluate(`document.querySelectorAll('#parent-links li').length`), 0);
    assert.equal(await evaluate(`document.getElementById('parent-add-controls').hidden`), true);
    assert.equal(await evaluate(`document.getElementById('delete').disabled`), true);
    assert.equal(await evaluate(`document.getElementById('save').textContent`), 'Save node');
    await evaluate(`document.getElementById('frame-all').click()`);
    await delay(300); await screenshot('origin-root-neighborhood');
    assert.ok(await arrowJoins());
    phase('Git lifecycle and watcher recovery');
    await options.after?.({ evaluate, screenshot, delay });
    console.log(`SPECSPEC_REAL_UI_OK: ${total} nodes; minimum/maximum revision-local distance, no hop badges, sharp implementation/rounder requirement cards and true compact/expanded manifesto circles with fitting native content and arc ports, shorter ordinary cards/wider gaps, unhinted 250% native headlines, shared gray manifesto tint/root-only white hover border, stronger semantic borders and hue-preserving brighter/chromatic Git/draft connections, 80-column expanded text and larger Git corners, one-hop hover darkening with unchanged geometry and dark/light/contrast CSS probes, approval/retirement-free controls, HEAD deletion ghosts, exact user-selected seven-color spectrum, immutable CLI-spotlight arrivals integrated into the retained list, session-only round red batch-count badges, white identity-based inset rings and zoom-dependent quiet neutral arrows with unchanged editing/geometry, and eight fill modes with linear/log absolute/cohort-relative influence probes and revision-colored manifesto, earliest manifesto ranks, minimum screen stroke/head strength, circle-free tangent joins, LR layout, viewport invariance, pan/zoom, draft cameras, native gestures and resized curves (${Date.now() - started}ms).`);
  } catch (error) {
    try { await screenshot('origin-failure'); } catch { /* Keep the original failure. */ }
    throw error;
  } finally { clients.forEach(client => client.close()); }
};
