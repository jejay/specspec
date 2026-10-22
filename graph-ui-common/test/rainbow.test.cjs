const { test } = require('node:test');
const assert = require('node:assert/strict');
const model = require('../media/graph-model.js');

// Independent sRGB -> OKLCH check of the rounded, in-gamut table.
function oklch(hex) {
  const [r,g,b] = hex.slice(1).match(/../g).map(n => parseInt(n,16)/255)
    .map(v => v<=0.04045 ? v/12.92 : ((v+0.055)/1.055)**2.4);
  const l=Math.cbrt(0.4122214708*r+0.5363325363*g+0.0514459929*b);
  const m=Math.cbrt(0.2119034982*r+0.6806995451*g+0.1073969566*b);
  const s=Math.cbrt(0.0883024619*r+0.2817188376*g+0.6299787005*b);
  const L=0.2104542553*l+0.793617785*m-0.0040720468*s;
  const a=1.9779984951*l-2.428592205*m+0.4505937099*s;
  const bLab=0.0259040371*l+0.7827717662*m-0.808675766*s;
  return [L,Math.hypot(a,bLab),(Math.atan2(bLab,a)*180/Math.PI+360)%360];
}

test('seven swatches match the user selection exactly, with its requested lightness/chroma/hue sweep', () => {
  assert.deepEqual(model.RAINBOW_COLORS,['#bc82c9','#7e97e6','#1facce','#37b390','#92a64b','#ca8d3e','#dc7b7c']);
  assert.equal(new Set(model.RAINBOW_COLORS).size,7);
  for(const [i,color] of model.RAINBOW_COLORS.entries()) {
    assert.match(color,/^#[0-9a-f]{6}$/);
    const [l,c,h]=oklch(color);
    assert.ok(Math.abs(l-0.69)<0.003,`Lightness ${color}: ${l}`);
    assert.ok(Math.abs(c-0.12)<0.003,`Chroma ${color}: ${c}`);
    assert.ok(Math.abs(h-(320-50*i))<1,`Hue ${color}: ${h}`);
  }
});

test('distance starts at the first selected swatch for one hop and repeats the seven-entry table', () => {
  for(const mode of ['distance','max-distance']) {
    for(let distance=1;distance<=40;distance++) {
      assert.equal(model.color(mode,{type:'requirement'},distance),model.RAINBOW_COLORS[(distance-1)%7]);
      assert.equal(model.color(mode,{type:'manifesto'},distance),'#d3d3d3');
    }
    for(const distance of [undefined,NaN,Infinity,-1,0,1.5]) {
      assert.equal(model.color(mode,{type:'requirement'},distance),model.NEUTRAL_COLOR);
    }
  }
});

test('node-type and colored revision swatches come from the same rainbow table', () => {
  for(const type of ['requirement','implementation']) {
    assert.ok(model.RAINBOW_COLORS.includes(model.color('type',{type})));
  }
  assert.equal(model.TYPE_COLORS.requirement,model.RAINBOW_COLORS[4]);
  assert.equal(model.TYPE_COLORS.implementation,model.RAINBOW_COLORS[0]);
  for(const kind of ['added','changed','removed','source-changed']) {
    assert.ok(model.RAINBOW_COLORS.includes(model.REVISION_COLORS[kind]));
  }
  assert.equal(model.REVISION_COLORS.added,model.RAINBOW_COLORS[3]);
  assert.equal(model.REVISION_COLORS.changed,model.RAINBOW_COLORS[1]);
  assert.equal(model.REVISION_COLORS.removed,model.RAINBOW_COLORS[6]);
  assert.equal(model.REVISION_COLORS['source-changed'],model.RAINBOW_COLORS[5]);
  assert.deepEqual(model.TYPE_COLORS,{manifesto:'#d3d3d3',requirement:'#92a64b',implementation:'#bc82c9'});
  for(const [kind,hex] of Object.entries({added:'#37b390',changed:'#7e97e6',removed:'#dc7b7c','source-changed':'#ca8d3e'})) {
    assert.equal(model.color('git-revision',{type:'manifesto'},0,kind),hex);
    assert.equal(model.color('git-revision',{type:'requirement'},10,kind),hex);
  }
});

test('revision mode includes manifesto changes, but other modes keep it gray', () => {
  for(const kind of Object.keys(model.REVISION_COLORS)) {
    const node={type:'manifesto'};
    assert.equal(model.color('git-revision',node,0,kind),model.REVISION_COLORS[kind]);
    for(const mode of ['distance','max-distance','type']) {
      assert.equal(model.color(mode,node,0,kind),'#d3d3d3');
    }
  }
  for(const kind of ['unchanged','uncompared','draft','unknown',undefined]) {
    assert.equal(model.color('git-revision',{type:'requirement'},1,kind),model.NEUTRAL_COLOR);
  }
});
