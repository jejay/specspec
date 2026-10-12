const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { JSDOM } = require('jsdom');
const palette = require('../../tools/rainbow-playground/palette.js');
const model = require('../media/graph-model.js');
const tool = join(__dirname, '../../tools/rainbow-playground');

function page(t) {
  const dom = new JSDOM(readFileSync(join(tool,'index.html'),'utf8'), { runScripts:'outside-only' });
  const errors=[];dom.window.addEventListener('error',e=>errors.push(e.message));
  for(const file of ['palette.js','app.js']) dom.window.eval(readFileSync(join(tool,file),'utf8'));
  t.after(()=>{dom.window.close();assert.deepEqual(errors,[]);});
  const $=id=>dom.window.document.getElementById(id);
  const input=(id,value)=>{$(id).value=value;$(id).dispatchEvent(new dom.window.Event('input',{bubbles:true}));};
  return {dom,$,input};
}

test('standalone generator defaults exactly match the production rainbow and mappings', () => {
  const result=palette.generate(palette.DEFAULTS);
  assert.deepEqual(result.colors,model.RAINBOW_COLORS);
  assert.deepEqual(result.parameters,{count:7,lightness:0.69,chroma:0.12,startHue:320,endHue:20});
  assert.deepEqual(result.colors,['#bc82c9','#7e97e6','#1facce','#37b390','#92a64b','#ca8d3e','#dc7b7c']);
  assert.deepEqual(result.mappings,{requirement:3,implementation:0,added:4,changed:1,removed:6,renamed:1,'source-changed':5});
  assert.deepEqual(result.gamutReducedIndices,[]);
  assert.equal(palette.css(result),`:root {
  --rainbow-1: #bc82c9;
  --rainbow-2: #7e97e6;
  --rainbow-3: #1facce;
  --rainbow-4: #37b390;
  --rainbow-5: #92a64b;
  --rainbow-6: #ca8d3e;
  --rainbow-7: #dc7b7c;
  --palette-requirement: var(--rainbow-4);
  --palette-implementation: var(--rainbow-1);
  --palette-added: var(--rainbow-5);
  --palette-changed: var(--rainbow-2);
  --palette-removed: var(--rainbow-7);
  --palette-renamed: var(--rainbow-2);
  --palette-source-changed: var(--rainbow-6);
}\n`);
  for(const [kind,index] of Object.entries(result.mappings)) {
    assert.equal(result.colors[index],kind in model.TYPE_COLORS ? model.TYPE_COLORS[kind] : model.REVISION_COLORS[kind]);
  }
});

test('count/hue endpoints interpolate linearly in either direction, with no implicit shortest sweep', () => {
  const result=palette.generate({...palette.DEFAULTS,count:3,startHue:30,endHue:300});
  assert.deepEqual(result.samples.map(s=>s.hue),[30,165,300]);
  assert.equal(palette.generate({...palette.DEFAULTS,count:32}).colors.length,32);
  assert.equal(palette.generate({...palette.DEFAULTS,chroma:0}).gamutReducedIndices.length,0);
});

test('out-of-gamut colors reduce chroma at fixed hue/lightness instead of silently clipping', () => {
  const result=palette.generate({...palette.DEFAULTS,chroma:0.4});
  assert.ok(result.gamutReducedIndices.length>0);
  for(const s of result.samples) {
    assert.equal(s.lightness,0.69);assert.equal(s.requestedChroma,0.4);
    assert.ok(palette.inGamut(palette.linearRGB(s.lightness,s.chroma,s.hue)));
    if(s.gamutReduced) assert.ok(s.chroma<0.4);
    assert.match(s.hex,/^#[0-9a-f]{6}$/);
  }
  for(const lightness of [0,1]) {
    const extreme=palette.generate({...palette.DEFAULTS,lightness,chroma:0.4});
    assert.ok(extreme.colors.every(c=>c===(lightness===0?'#000000':'#ffffff')));
  }
});

test('generator rejects missing, non-finite and out-of-range parameters', () => {
  for(const changes of [{count:1},{count:33},{count:2.5},{count:''},{lightness:-0.1},{lightness:1.1},
    {chroma:0.5},{chroma:-1},{startHue:-1},{endHue:361},{count:NaN},{chroma:undefined}]) {
    assert.throws(()=>palette.generate({...palette.DEFAULTS,...changes}));
  }
});

test('page updates slider/number inputs, previews and all export formats, with reset and theme switching', t => {
  const {dom,$,input}=page(t);
  assert.equal($('swatches').children.length,7);assert.equal($('nodes').children.length,8);
  input('count','6');assert.equal($('swatches').children.length,6);
  assert.equal(JSON.parse($('result').value).parameters.count,6);
  const slider=dom.window.document.querySelector('[data-for="chroma"]');slider.value='0.2';
  slider.dispatchEvent(new dom.window.Event('input',{bubbles:true}));assert.equal($('chroma').value,'0.2');
  $('format').value='palette';$('format').dispatchEvent(new dom.window.Event('change'));
  assert.equal(JSON.parse($('result').value).colors.length,6);
  $('format').value='css';$('format').dispatchEvent(new dom.window.Event('change'));
  assert.match($('result').value,/--rainbow-6: #[0-9a-f]{6}/);
  assert.match($('result').value,/--palette-added: var\(--rainbow-\d+\)/);
  $('theme').value='light';$('theme').dispatchEvent(new dom.window.Event('change'));assert.ok($('preview').classList.contains('light'));
  $('reset').click();assert.equal($('count').value,'7');assert.equal($('lightness').value,'0.69');assert.equal($('chroma').value,'0.12');
  assert.match($('result').value,/--rainbow-1: #bc82c9/);
});

test('invalid edits retain last valid output, disable copying, and recover with reset', t => {
  const {$,input}=page(t);const previous=$('result').value;
  input('count','1');assert.equal($('result').value,previous);assert.equal($('copy').disabled,true);
  assert.match($('message').textContent,/last valid result/);
  $('reset').click();assert.equal($('copy').disabled,false);
  input('chroma','0.4');assert.match($('message').textContent,/Chroma reduced/);
});

test('copy uses clipboard when available and selects output for manual copy on rejection', async t => {
  const {dom,$}=page(t);let text;
  Object.defineProperty(dom.window.navigator,'clipboard',{value:{writeText:async value=>{text=value;}},configurable:true});
  $('copy').click();await new Promise(resolve=>setImmediate(resolve));assert.equal(text,$('result').value);assert.match($('message').textContent,/Copied/);
  Object.defineProperty(dom.window.navigator,'clipboard',{value:{writeText:async()=>{throw new Error('Denied');}},configurable:true});
  $('copy').click();await new Promise(resolve=>setImmediate(resolve));
  assert.match($('message').textContent,/press Ctrl\+C/);assert.equal(dom.window.document.activeElement,$('result'));
  assert.equal($('result').selectionEnd,$('result').value.length);
});
