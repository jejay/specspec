const { test } = require('node:test');
const assert = require('node:assert/strict');
const model = require('../media/graph-model.js');

function snapshot(edges, extra = []) {
  const ids = new Set(['root', ...edges.flat(), ...extra]);
  return { nodes: [...ids].map(id => ({ id, type: id === 'root' ? 'manifesto' : 'requirement',
    parents: edges.filter(([, child]) => child === id).map(([parent]) => parent), body: `# ${id}\n`, sources: [] })), edges };
}
const diamond = () => snapshot([['root','a'],['root','b'],['root','c'],['a','left'],['a','right'],
  ['left','shared'],['right','shared'],['b','shared'],['shared','tail']]);

test('absolute influence includes self and scales influence minus one to the highest non-manifesto value', () => {
  const graph = diamond();
  graph.nodes.find(n => n.id === 'tail').type = 'implementation';
  const before = JSON.stringify(graph), metrics = model.metrics(graph);
  assert.equal(metrics.influence('root'), 8);
  assert.equal(metrics.influence('a'), 5);
  assert.equal(metrics.influence('tail'), 1);
  assert.equal(metrics.influence('missing'), undefined);
  assert.equal(metrics.descendantCount('root'), 7);
  assert.equal(metrics.descendantCount('a'), 4, 'A shared node and its tail contribute once each.');
  assert.equal(metrics.influenceRatio('a'), 1);
  assert.equal(metrics.influenceRatio('b'), 0.5);
  assert.equal(metrics.influenceRatio('shared'), 0.25);
  for (const id of ['c','tail']) {
    assert.equal(metrics.influenceRatio(id), 0);
    assert.equal(model.color('absolute-influence',graph.nodes.find(n => n.id === id),0), '#4df884');
  }
  assert.equal(metrics.influenceRatio('root'), undefined);
  assert.equal(JSON.stringify(graph), before, 'Metrics do not add scores or relationships to records.');
});

test('relative influence groups by maximum path, not shortest path, and normalizes cohort minimum to maximum', () => {
  const graph = snapshot([['root','a'],['root','b'],['root','c'],['a','p'],['p','long'],['b','short'],
    ['long','mixed'],['short','mixed'],['c','p2'],['p2','p3'],['p3','peer'],
    ['mixed','one'],['mixed','two'],['mixed','three'],['peer','last']]);
  const metrics = model.metrics(graph);
  assert.equal(metrics.minDistances.get('mixed'), 3);
  assert.equal(metrics.maxDistances.get('mixed'), 4);
  assert.equal(metrics.minDistances.get('peer'), 4);
  assert.equal(metrics.maxDistances.get('peer'), 4);
  assert.equal(metrics.descendantCount('mixed'), 3);
  assert.equal(metrics.descendantCount('peer'), 1);
  assert.equal(metrics.influenceRatio('mixed','relative-influence'), 1);
  assert.equal(metrics.influenceRatio('peer','relative-influence'), 0, 'A positive count can be green when it is the cohort minimum.');
  const d = model.metrics(diamond());
  assert.equal(d.influenceRatio('a','relative-influence'), 1);
  assert.equal(d.influenceRatio('b','relative-influence'), 0.5);
  assert.equal(d.influenceRatio('c','relative-influence'), 0);
});

test('all-one absolute ranges, tied positive cohorts and singleton cohorts use green; the manifesto stays gray', () => {
  for (const graph of [snapshot([['root','a'],['root','b']]), snapshot([['root','a'],['a','leaf']]),
    snapshot([['root','a'],['root','b'],['a','left'],['b','right']])]) {
    const metrics = model.metrics(graph);
    for (const node of graph.nodes) for (const mode of model.INFLUENCE_MODES) {
      const ratio = metrics.influenceRatio(node.id,mode);
      if (node.type === 'manifesto') assert.equal(model.color(mode,node,ratio),'#d3d3d3');
      else if (mode.endsWith('relative-influence') || metrics.descendantCount(node.id) === 0) {
        assert.equal(ratio,0); assert.equal(model.color(mode,node,ratio),'#4df884');
      }
    }
  }
  assert.equal(model.metrics(snapshot([])).influenceRatio('root'),undefined);
  assert.equal(model.metrics({ nodes: [], edges: [] }).influenceRatio('missing'),undefined);
});

test('logarithmic influence transforms self-inclusive counts before absolute and cohort normalization', () => {
  const edges=[['root','a'],['root','b'],['root','c']];
  for (const [id,count] of [['a',9],['b',3],['c',1]]) for(let i=0;i<count;i++) edges.push([id,`${id}-${i}`]);
  const metrics=model.metrics(snapshot(edges));
  assert.ok(Math.abs(metrics.influenceRatio('b','log-absolute-influence')-Math.log(4)/Math.log(10))<1e-12);
  assert.ok(Math.abs(metrics.influenceRatio('b','log-relative-influence')-(Math.log(4)-Math.log(2))/(Math.log(10)-Math.log(2)))<1e-12);
  assert.equal(metrics.influenceRatio('b','absolute-influence'),1/3,'The linear comparison remains available and unchanged.');
  for (const mode of ['log-absolute-influence','log-relative-influence']) {
    assert.equal(metrics.influenceRatio('a',mode),1);
    assert.equal(metrics.influenceRatio('a-0',mode),0,'log(1) is finite and leaves stay green.');
    assert.equal(model.color(mode,{type:'manifesto'},metrics.influenceRatio('root',mode)),'#d3d3d3');
  }
  assert.equal(metrics.influenceRatio('c','log-relative-influence'),0,'The positive minimum still maps to green.');
});

test('continuous warm interpolation has exact green/yellow/red anchors and linear sRGB intermediate colors', () => {
  assert.deepEqual(model.INFLUENCE_COLORS,['#4df884','#e8d62c','#ba2208']);
  for (const [value,hex] of [[0,'#4df884'],[0.25,'#9be758'],[0.5,'#e8d62c'],[0.75,'#d17c1a'],[1,'#ba2208']]) {
    assert.equal(model.influenceColor(value),hex);
    for (const mode of model.INFLUENCE_MODES) assert.equal(model.color(mode,{type:'requirement'},value),hex);
  }
  const samples = Array.from({length:101},(_,i)=>model.influenceColor(i/100));
  assert.equal(new Set(samples).size,101,'The ramp does not bucket counts into fixed discrete swatches.');
  for (const hex of samples) {
    const [r,g,b] = [1,3,5].map(start=>parseInt(hex.slice(start,start+2),16));
    assert.ok(b < Math.max(r,g),'Blue never dominates the warm spectrum.');
  }
  assert.equal(model.influenceColor(-1),'#4df884'); assert.equal(model.influenceColor(2),'#ba2208');
  for (const value of [undefined,null,NaN,Infinity,'0.5']) assert.equal(model.influenceColor(value),model.NEUTRAL_COLOR);
});

test('influence ranges are lazy and all influence modes reuse cached descendant counts', () => {
  const metrics = model.metrics(diamond()); let reads = 0;
  for (const list of metrics.children.values()) {
    const iterator = list[Symbol.iterator].bind(list);
    list[Symbol.iterator] = function* () { reads++; yield* iterator(); };
  }
  assert.equal(metrics.influenceRatio('root'),undefined);
  assert.equal(reads,0);
  metrics.influenceRatio('a');
  assert.ok(reads>0,'Normalization is first built when influence is requested, not during ordinary metric construction.');
  const once = reads;
  for (const mode of model.INFLUENCE_MODES) for (const id of metrics.children.keys()) metrics.influenceRatio(id,mode);
  assert.equal(reads,once,'Repeated renders and mode switches reuse the snapshot-local ranges/counts.');
});

test('unreachable and cycle-blocked influence stays neutral without contaminating valid cohorts', () => {
  const graph = snapshot([['root','safe'],['safe','leaf'],['root','a'],['a','b'],['b','a'],['b','blocked'],
    ['orphan','remote']]);
  graph.edges.push(['missing-parent','safe'],['leaf','missing-child']);
  const metrics = model.metrics(graph);
  for (const mode of model.INFLUENCE_MODES) {
    for (const id of ['a','b','blocked','orphan','remote','missing-parent','missing-child']) {
      assert.equal(metrics.influenceRatio(id,mode),undefined);
      assert.equal(model.color(mode,{type:'requirement'},metrics.influenceRatio(id,mode)),model.NEUTRAL_COLOR);
    }
  }
  assert.equal(metrics.influenceRatio('safe'),1); assert.equal(metrics.influenceRatio('leaf'),0);
  assert.equal(metrics.influenceRatio('safe','unsupported-mode'),undefined);
});

test('generated current-shaped DAGs agree with independent closure/cohort oracles under input reordering', () => {
  let seed = 82;
  const random = () => { seed = (Math.imul(seed,1664525)+1013904223)>>>0; return seed/2**32; };
  for (let sample=0;sample<12;sample++) {
    const edges=[],depths=new Map([['root',0]]); let previous=['root'];
    for (let depth=1;depth<=6;depth++) {
      const level=Array.from({length:6},(_,i)=>`n${depth}-${i}`);
      for (const id of level) {
        depths.set(id,depth);
        const parents=new Set([previous[Math.floor(random()*previous.length)],previous[Math.floor(random()*previous.length)]]);
        for (const parent of parents) edges.push([parent,id]);
      }
      previous=level;
    }
    const graph=snapshot(edges),before=JSON.stringify(graph),ids=graph.nodes.map(n=>n.id),index=new Map(ids.map((id,i)=>[id,i]));
    const reach=ids.map(()=>ids.map(()=>false));
    for (const [a,b] of edges) reach[index.get(a)][index.get(b)]=true;
    for (let k=0;k<ids.length;k++) for (let i=0;i<ids.length;i++) for (let j=0;j<ids.length;j++) reach[i][j] ||= reach[i][k]&&reach[k][j];
    const counts=new Map(ids.map((id,i)=>[id,1+reach[i].filter(Boolean).length]));
    const maximum=Math.max(...ids.filter(id=>id!=='root').map(id=>counts.get(id)));
    const metrics=model.metrics(graph),reversed=model.metrics({...graph,nodes:[...graph.nodes].reverse(),edges:[...edges].reverse()});
    for (const id of ids.filter(id=>id!=='root')) {
      const peers=ids.filter(peer=>depths.get(peer)===depths.get(id)).map(peer=>counts.get(peer));
      const low=Math.min(...peers),high=Math.max(...peers);
      assert.equal(metrics.influence(id),counts.get(id));
      assert.equal(metrics.descendantCount(id),counts.get(id)-1);
      for (const mode of model.INFLUENCE_MODES) {
        const scale=mode.startsWith('log-')?Math.log:value=>value-1;
        const lo=mode.endsWith('absolute-influence')?1:low,hi=mode.endsWith('absolute-influence')?maximum:high;
        const expected=hi>lo?(scale(counts.get(id))-scale(lo))/(scale(hi)-scale(lo)):0;
        assert.ok(Math.abs(metrics.influenceRatio(id,mode)-expected)<1e-12);
        assert.ok(Math.abs(reversed.influenceRatio(id,mode)-expected)<1e-12);
      }
    }
    assert.equal(JSON.stringify(graph),before);
  }
});
