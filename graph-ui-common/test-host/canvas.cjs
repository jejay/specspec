/* Focused installed-host checks, shared verbatim by Electron and VS Code. */
const assert = require('node:assert/strict');

exports.checkCanvas = async function checkCanvas({ evaluate, input, screenshot }) {
  const chrome=await evaluate(`(() => {
    const v=document.getElementById('viewport').getBoundingClientRect(),shell=document.querySelector('.canvas-shell').getBoundingClientRect(),nav=document.querySelector('.camera-controls').getBoundingClientRect();
    return {clutter:!!document.querySelector('footer,#canvas-help,.legend-help'),full:Math.abs(v.height-shell.height)<1,
      floating:nav.left>v.left&&nav.right<v.right&&nav.bottom<v.bottom&&nav.width<v.width,
      round:parseFloat(getComputedStyle(document.querySelector('.camera-controls')).borderRadius)>0,
      buttons:[...document.querySelectorAll('.framing-controls button')].filter(b=>!b.hidden).map(b=>b.getAttribute('aria-label'))};})()`);
  assert.deepEqual(chrome,{clutter:false,full:true,floating:true,round:true,buttons:['Frame graph','Frame rectangle']});
  await input({type:'mouseMoved',x:1,y:1});
  await evaluate(`window.__canvasPaint={style:document.documentElement.getAttribute('style'),bodyStyle:document.body.getAttribute('style'),classes:document.body.className,mode:document.getElementById('color-mode').value};document.getElementById('color-mode').value='type';document.getElementById('color-mode').dispatchEvent(new Event('change'));`);
  for(const theme of ['dark','light','contrast','contrast-light','contrast-fallback','contrast-light-fallback']) {
    await evaluate(`(() => {document.body.className=${JSON.stringify('vscode-'+(theme.includes('contrast')?(theme.includes('light')?'high-contrast-light':'high-contrast'):theme))};
      document.documentElement.style.setProperty('--vscode-editor-background',${JSON.stringify(theme.includes('light')?'#ffffff':'#111111')});
      document.documentElement.style.setProperty('--vscode-contrastBorder',${JSON.stringify(theme.includes('fallback')?'initial':'#ffff00')});
      document.body.style.setProperty('--vscode-contrastBorder',${JSON.stringify(theme.includes('fallback')?'initial':'#ffff00')});document.getElementById('zoom-reset').click();})()`);
    for(const zoom of ['actual','intermediate','minimum']) {
      await evaluate(`(() => {${zoom==='actual'?'':`for(let i=0;i<${zoom==='intermediate'?5:30};i++)document.getElementById('zoom-out').click();`}})()`);
      const results=await evaluate(`(() => {
        const canvas=document.createElement('canvas');canvas.width=canvas.height=1;const ctx=canvas.getContext('2d');
        const rgb=color=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=color;ctx.fillRect(0,0,1,1);return [...ctx.getImageData(0,0,1,1).data];};
        const v=document.getElementById('viewport'),q=1-Math.max(0,Math.min(1,(Number(v.dataset.scale)-0.16)/(0.40-0.16)));
        const probe=document.createElement('span');document.body.append(probe);
        const records=[...document.querySelectorAll('#cards .card')].map(c=>{
          const style=getComputedStyle(c),border=style.borderTopColor,base=${JSON.stringify(theme.includes('contrast'))}?'var(--vscode-editor-background)':'color-mix(in srgb, '+c.style.getPropertyValue('--node-accent')+' 15%, var(--vscode-editor-background))';
          probe.style.background='color-mix(in srgb, '+border+' '+(q*100)+'%, '+base+')';
          return {actual:rgb(style.backgroundColor),expected:rgb(getComputedStyle(probe).backgroundColor),border:rgb(border)};});
        probe.remove();return {q,records};})()`);
      for(const row of results.records) {
        assert.deepEqual(row.actual,row.expected,`${theme}/${zoom}: interpolated fill`);
        if(zoom==='minimum') assert.deepEqual(row.actual,row.border,`${theme}: solid overview shape`);
      }
      if(zoom==='minimum') {
        assert.ok(await evaluate(`(() => {const root=document.querySelector('.card.manifesto');root.dispatchEvent(new PointerEvent('pointerover',{bubbles:true,pointerType:'mouse'}));
          const s=getComputedStyle(root),canvas=document.createElement('canvas'),ctx=canvas.getContext('2d'),rgb=color=>{ctx.fillStyle=color;ctx.fillRect(0,0,1,1);return [...ctx.getImageData(0,0,1,1).data].join(',');};
          const equal=rgb(s.backgroundColor)===rgb(s.borderTopColor);document.getElementById('viewport').dispatchEvent(new PointerEvent('pointerleave'));return equal;})()`),'Hovered neutral manifesto fill matches its white border.');
      }
    }
  }
  await screenshot('canvas-polish-solid-overview');
  await evaluate(`(() => {const p=window.__canvasPaint;document.body.className=p.classes;if(p.bodyStyle===null)document.body.removeAttribute('style');else document.body.setAttribute('style',p.bodyStyle);if(p.style===null)document.documentElement.removeAttribute('style');else document.documentElement.setAttribute('style',p.style);document.getElementById('zoom-reset').click();})()`);
  console.log('Canvas paint: actual/intermediate/minimum fills, solid borders and hovered manifesto passed in dark/light/contrast themes.');

  const gesture=await evaluate(`(() => {
    const v=document.getElementById('viewport'),area=v.getBoundingClientRect(),pose=()=>({x:Number(v.dataset.cameraX),y:Number(v.dataset.cameraY),k:Number(v.dataset.scale)});
    const world=()=>JSON.stringify([...document.querySelectorAll('#cards .card')].map(c=>[c.dataset.nodeId,c.style.left,c.style.top,c.style.width,c.style.height]));
    const before=pose(),geometry=world(),p=(type,x,y,ctrl,target=v)=>target.dispatchEvent(new PointerEvent(type,{bubbles:true,cancelable:true,pointerId:7,pointerType:'mouse',button:0,clientX:area.left+x,clientY:area.top+y,ctrlKey:ctrl}));
    p('pointerover',100,100,true);const hover=getComputedStyle(v).cursor==='crosshair';
    window.dispatchEvent(new KeyboardEvent('keyup',{key:'Control'}));const released=getComputedStyle(v).cursor==='grab';
    p('pointerdown',100,100,true);p('pointermove',300,260,true,window);window.dispatchEvent(new KeyboardEvent('keyup',{key:'Control'}));
    const latched=getComputedStyle(v).cursor==='crosshair'&&!document.getElementById('frame-selection').hidden;
    p('pointerup',300,260,false,window);
    const bounds=window.specspecCamera.rectangleBounds({x:100,y:100},{x:300,y:260},before),expected=window.specspecCamera.frameTransform(bounds,v.clientWidth,v.clientHeight,2.5);
    return {hover,released,latched,finished:document.getElementById('frame-selection').hidden&&document.getElementById('frame-area').getAttribute('aria-pressed')==='false',actual:pose(),expected,world:world()===geometry};})()`);
  assert.ok(gesture.hover&&gesture.released&&gesture.latched&&gesture.finished&&gesture.world);
  for(const k of ['x','y','k']) assert.ok(Math.abs(gesture.actual[k]-gesture.expected[k])<0.001);

  // A real CDP mouse sequence exercises Chromium's pointer capture and outside release.
  const v=await evaluate(`(() => {const r=document.getElementById('viewport').getBoundingClientRect();return {x:r.left+120,y:r.top+120};})()`);
  await evaluate(`document.getElementById('frame-area').click()`);
  await input({type:'mouseMoved',x:v.x,y:v.y});await input({type:'mousePressed',button:'left',buttons:1,clickCount:1,x:v.x,y:v.y});
  assert.ok(await evaluate(`document.getElementById('viewport').hasPointerCapture(1)`),'Chromium captures the rectangle pointer.');
  await input({type:'mouseMoved',button:'left',buttons:1,x:v.x+220,y:v.y-132});
  await screenshot('canvas-polish-rectangle');
  await input({type:'mouseReleased',button:'left',buttons:0,clickCount:1,x:v.x+220,y:v.y-132});
  assert.ok(await evaluate(`document.getElementById('frame-selection').hidden&&document.getElementById('frame-area').getAttribute('aria-pressed')==='false'`));
  await input({type:'mouseMoved',x:1,y:1});

  const native=await evaluate(`(() => {
    document.querySelector('.card.manifesto').click();const body=document.getElementById('body');body.focus();body.setSelectionRange(2,6);
    const before=JSON.stringify(window.specspecHost.getState().cameras),value=body.value;
    body.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,button:0,pointerId:7,pointerType:'mouse',ctrlKey:true,clientX:100,clientY:100}));
    const result={buttons:[...document.querySelectorAll('.framing-controls button')].filter(b=>!b.hidden).map(b=>b.getAttribute('aria-label')),
      retained:body===document.getElementById('body')&&value===body.value&&body.selectionStart===2&&body.selectionEnd===6&&before===JSON.stringify(window.specspecHost.getState().cameras)&&document.getElementById('frame-selection').hidden};
    window.dispatchEvent(new KeyboardEvent('keyup',{key:'Control'}));document.getElementById('back').click();document.getElementById('color-mode').value=window.__canvasPaint.mode;document.getElementById('color-mode').dispatchEvent(new Event('change'));document.getElementById('zoom-reset').click();delete window.__canvasPaint;return result;})()`);
  assert.deepEqual(native,{buttons:['Frame graph','Frame node','Frame rectangle'],retained:true});
  console.log('Canvas framing: floating/contextual icons, Ctrl latch/release, one-shot completion, real pointer capture and native editing passed.');
};
