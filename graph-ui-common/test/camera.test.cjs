const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { JSDOM } = require('jsdom');
const api = require('../media/graph-camera.js');
const model = require('../media/graph-model.js');

function fixture(t, platform = 'Win32') {
  const dom = new JSDOM('<main id="viewport"><div id="graph"><button class="card" id="node">Node</button><article class="card expanded"><section id="node-details"><textarea id="body">Native draft</textarea><input><select><option>Choice</option></select><a href="#">Source</a><button>Save</button><div contenteditable="true">Editable</div></section></article></div></main><nav class="camera-controls"><button id="tool">Frame rectangle</button></nav>', { runScripts:'outside-only', pretendToBeVisual:true });
  const win=dom.window, doc=win.document, viewport=doc.getElementById('viewport'), world=doc.getElementById('graph');
  Object.defineProperty(win.navigator,'platform',{value:platform});
  win.matchMedia=()=>({matches:true});
  Object.defineProperty(viewport,'clientWidth',{value:1000});Object.defineProperty(viewport,'clientHeight',{value:650});
  viewport.getBoundingClientRect=()=>({left:80,top:120,right:1080,bottom:770,width:1000,height:650});
  const captures=[],released=[],active=[],errors=[];
  win.addEventListener('error',event=>errors.push(event.message));
  viewport.setPointerCapture=id=>captures.push(id);viewport.releasePointerCapture=id=>released.push(id);
  for(const name of ['vendor/graph-vendor.js','graph-camera.js']) win.eval(readFileSync(join(__dirname,'../media',name),'utf8'));
  const camera=win.SpecSpecCamera.createCamera(viewport,world,{onRectangleChange:value=>active.push(value)});
  camera.set({x:20,y:-10,k:0.5});
  t.after(()=>{camera.dispose();win.close();assert.deepEqual(errors,[]);});
  const pointer=(type,x=100,y=100,flags={},target=viewport)=>{
    const e=new win.MouseEvent(type,{bubbles:true,cancelable:true,view:win,button:0,clientX:x+80,clientY:y+120,...flags});
    Object.defineProperty(e,'pointerId',{value:flags.pointerId??1});Object.defineProperty(e,'pointerType',{value:flags.pointerType??'mouse'});
    target.dispatchEvent(e);return e;
  };
  const key=(type,key,flags={})=>win.dispatchEvent(new win.KeyboardEvent(type,{key,bubbles:true,cancelable:true,...flags}));
  const band=doc.getElementById('frame-selection');
  return {dom,win,doc,viewport,world,camera,captures,released,active,pointer,key,band};
}
const plain = value => JSON.parse(JSON.stringify(value));

test('node fill and arrow ink use separate zoom ranges with a shared 16% endpoint',()=>{
  const scales=[0.12,0.16,0.28,0.4,0.55,0.7,1,2.5];
  let previous=1;
  for(const scale of scales) {
    const q=model.nodeFillStrength(scale);
    assert.ok(q>=0&&q<=1);
    assert.ok(q<=previous,'Fill progress decreases monotonically as magnification increases.');
    previous=q;
  }
  assert.equal(model.nodeFillStrength(0.12),1);assert.equal(model.nodeFillStrength(0.16),1);
  assert.ok(Math.abs(model.nodeFillStrength(0.28)-0.5)<1e-12);
  assert.equal(model.nodeFillStrength(0.4),0);
  assert.equal(model.nodeFillStrength(0.7),0);
  for(const bad of [undefined,NaN,Infinity,-Infinity,-1,0,'0.12',null]) assert.equal(model.nodeFillStrength(bad),0);
  assert.equal(model.nodeFillStrength(1),0);assert.equal(model.nodeFillStrength(2.5),0);
  assert.equal(model.neutralEdgeStrength(0.7),0.7);
  assert.equal(model.neutralEdgeStrength(0.16),0.35);
  assert.equal(model.neutralEdgeStrength(0.12),0.35);
  assert.ok(Math.abs(model.neutralEdgeStrength(0.43)-0.525)<1e-12);
  assert.equal(model.neutralEdgeStrength(1),0.7);
});

test('rectangle inversion normalizes all drag directions and rejects tiny or invalid extents',()=>{
  const pose={x:20,y:-10,k:0.5},expected={x:160,y:220,width:400,height:300};
  for(const [a,b] of [[{x:100,y:100},{x:300,y:250}],[{x:300,y:250},{x:100,y:100}],
    [{x:300,y:100},{x:100,y:250}],[{x:100,y:250},{x:300,y:100}]]) assert.deepEqual(api.rectangleBounds(a,b,pose),expected);
  for(const [a,b,p] of [[{x:1,y:1},{x:4,y:50},pose],[{x:1,y:1},{x:50,y:1},pose],
    [{x:0,y:0},{x:10,y:10},{...pose,k:0}],[{x:NaN,y:0},{x:10,y:10},pose],[null,null,null]]) assert.equal(api.rectangleBounds(a,b,p),undefined);
  const box={x:100,y:200,width:100,height:100};
  assert.equal(api.frameTransform(box,1000,650).k,1);
  assert.equal(api.frameTransform(box,1000,650,api.MAX_SCALE).k,2.5);
});

test('modifier hover arms the crosshair and release before pressing restores ordinary navigation',t=>{
  const f=fixture(t),before=f.camera.value();
  f.pointer('pointerover');f.key('keydown','Control',{ctrlKey:true});
  assert.ok(f.viewport.classList.contains('rectangle-ready'));assert.equal(f.active.at(-1),true);
  f.key('keyup','Control');assert.equal(f.viewport.classList.contains('rectangle-ready'),false);
  assert.equal(f.band.hidden,true);assert.deepEqual(f.camera.value(),before);assert.equal(f.active.at(-1),false);
  f.pointer('pointerover',100,100,{ctrlKey:true});f.pointer('pointerleave');
  assert.equal(f.viewport.classList.contains('rectangle-ready'),false);
});

test('drag stays latched after modifier release and frames on an outside release',t=>{
  const f=fixture(t),pose=plain(f.camera.value());
  assert.equal(f.pointer('pointerdown',300,250,{ctrlKey:true}).defaultPrevented,true);
  assert.equal(f.band.hidden,false);assert.deepEqual(f.captures,[1]);
  f.key('keyup','Control');f.pointer('pointermove',100,100,{},f.win);
  assert.ok(f.viewport.classList.contains('rectangle-dragging'));assert.ok(f.viewport.classList.contains('rectangle-ready'));
  assert.deepEqual([f.band.style.left,f.band.style.top,f.band.style.width,f.band.style.height],['100px','100px','200px','150px']);
  assert.deepEqual(plain(f.camera.value()),pose);
  f.pointer('pointerup',100,100,{},f.win);
  const bounds=api.rectangleBounds({x:300,y:250},{x:100,y:100},pose);
  assert.deepEqual(plain(f.camera.value()),api.frameTransform(bounds,1000,650,api.MAX_SCALE));
  assert.equal(f.band.hidden,true);assert.equal(f.viewport.classList.contains('rectangle-ready'),false);assert.deepEqual(f.released,[1]);
});

test('modifier-held completion is one-shot until release, and its click is consumed',t=>{
  const f=fixture(t);let clicks=0;const node=f.doc.getElementById('node');node.addEventListener('click',()=>clicks++);
  f.pointer('pointerdown',100,100,{ctrlKey:true},node);f.pointer('pointerup',300,250,{ctrlKey:true},node);
  f.pointer('click',300,250,{ctrlKey:true},node);assert.equal(clicks,0);
  f.pointer('pointermove',100,100,{ctrlKey:true});assert.equal(f.viewport.classList.contains('rectangle-ready'),false);
  f.pointer('pointerdown',100,100,{ctrlKey:true});assert.equal(f.band.hidden,true);
  f.key('keyup','Control');f.key('keydown','Control',{ctrlKey:true});assert.ok(f.viewport.classList.contains('rectangle-ready'));
});

test('the icon arms the same tool; tiny gestures and icon toggle retain the camera',t=>{
  const f=fixture(t),before=f.camera.value();
  f.camera.toggleRectangle();assert.equal(f.active.at(-1),true);
  f.pointer('pointerdown',100,100);f.pointer('pointerup',103,250);
  assert.deepEqual(f.camera.value(),before);assert.equal(f.active.at(-1),false);assert.equal(f.band.hidden,true);
  f.camera.toggleRectangle();f.camera.toggleRectangle();assert.equal(f.active.at(-1),false);
  f.camera.toggleRectangle();const tool=f.doc.getElementById('tool');tool.focus();
  const escape=new f.win.KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true});tool.dispatchEvent(escape);
  assert.equal(escape.defaultPrevented,true);assert.equal(f.active.at(-1),false);
});

test('Escape, blur, pointer cancellation and lost capture cancel with clean cursors and camera',t=>{
  const f=fixture(t),before=f.camera.value(),node=f.doc.getElementById('node');let clicks=0;node.addEventListener('click',()=>clicks++);
  for(const cancel of [()=>f.key('keydown','Escape'),()=>f.win.dispatchEvent(new f.win.Event('blur')),
    ()=>f.pointer('pointercancel'),()=>f.pointer('lostpointercapture')]) {
    f.camera.toggleRectangle();f.pointer('pointerdown');f.pointer('pointermove',300,250);cancel();
    assert.equal(f.band.hidden,true);assert.equal(f.viewport.classList.contains('rectangle-ready'),false);
    assert.equal(f.viewport.classList.contains('rectangle-dragging'),false);assert.deepEqual(f.camera.value(),before);
    f.pointer('pointerup',300,250,{},node);f.pointer('click',300,250,{},node);assert.equal(clicks,0,'Cancelled drags consume their release click.');
  }
  f.pointer('pointerdown',100,100,{},node);f.pointer('pointerup',100,100,{},node);f.pointer('click',100,100,{},node);
  assert.equal(clicks,1,'Fresh ordinary input restores node selection.');
});

test('native controls, links, editing and modified highlight/context gestures retain their input',t=>{
  const f=fixture(t),before=f.camera.value();const body=f.doc.getElementById('body');body.focus();body.setSelectionRange(2,5);
  f.camera.toggleRectangle();
  for(const target of f.doc.querySelectorAll('#node-details, textarea,input,select,a,#node-details button,[contenteditable]')) {
    assert.equal(f.pointer('pointerdown',100,100,{ctrlKey:true},target).defaultPrevented,false);assert.equal(f.band.hidden,true);
  }
  const escape=new f.win.KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true});body.dispatchEvent(escape);
  assert.equal(escape.defaultPrevented,false);
  const node=f.doc.getElementById('node');
  for(const flags of [{ctrlKey:true,shiftKey:true},{shiftKey:true},{altKey:true},{button:2}]) {
    assert.equal(f.pointer('pointerdown',100,100,flags,node).defaultPrevented,false);assert.equal(f.band.hidden,true);
  }
  assert.equal(f.doc.activeElement,body);assert.deepEqual([body.selectionStart,body.selectionEnd],[2,5]);assert.deepEqual(f.camera.value(),before);
});

test('active drag freezes wheel and camera keys and ignores other pointer IDs',t=>{
  const f=fixture(t),before=f.camera.value();f.pointer('pointerdown',100,100,{ctrlKey:true});
  f.pointer('pointerup',300,250,{pointerId:2});assert.equal(f.band.hidden,false);
  f.viewport.dispatchEvent(new f.win.KeyboardEvent('keydown',{key:'+',bubbles:true,cancelable:true}));
  const wheel=new f.win.WheelEvent('wheel',{bubbles:true,cancelable:true,deltaY:-100,view:f.win});f.viewport.dispatchEvent(wheel);
  assert.equal(wheel.defaultPrevented,true);assert.deepEqual(f.camera.value(),before);
});

test('macOS uses Command and keeps Control-click and Command+Shift available',t=>{
  const f=fixture(t,'MacIntel');assert.equal(f.camera.rectangleModifier,'Command');
  assert.equal(f.pointer('pointerdown',100,100,{ctrlKey:true}).defaultPrevented,false);assert.equal(f.band.hidden,true);
  assert.equal(f.pointer('contextmenu',100,100,{ctrlKey:true,button:2}).defaultPrevented,false);
  assert.equal(f.pointer('pointerdown',100,100,{metaKey:true,shiftKey:true}).defaultPrevented,false);
  f.pointer('pointerdown',100,100,{metaKey:true});assert.equal(f.band.hidden,false);
  f.key('keyup','Meta');f.pointer('pointerup',300,250);assert.equal(f.band.hidden,true);assert.equal(f.active.at(-1),false);
});

test('disposing an active tool removes its overlay and input listeners',t=>{
  const f=fixture(t);f.pointer('pointerdown',100,100,{ctrlKey:true});f.camera.dispose();
  assert.equal(f.viewport.querySelector('#frame-selection'),null);assert.equal(f.viewport.classList.contains('rectangle-ready'),false);
  f.key('keydown','Control',{ctrlKey:true});f.pointer('pointerdown',100,100,{ctrlKey:true});
  assert.equal(f.viewport.classList.contains('rectangle-ready'),false);
});
