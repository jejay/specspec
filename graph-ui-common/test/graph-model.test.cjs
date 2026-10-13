const { test } = require('node:test');
const assert = require('node:assert/strict');
const model = require('../media/graph-model.js');

function snapshot(edges, extra = []) {
  const ids = new Set(['root', ...edges.flat(), ...extra]);
  return { valid: true, nodes: [...ids].map(id => ({
    id, type: id === 'root' ? 'manifesto' : 'requirement',
    parents: edges.filter(([, child]) => child === id).map(([parent]) => parent),
    body: `# ${id}\n`, sources: [],
  })), edges };
}

test('manifesto stays light gray in distance/type modes regardless of distance or revision state', () => {
  assert.equal(model.TYPE_COLORS.manifesto, '#d3d3d3');
  for (const mode of ['distance', 'max-distance', 'type']) {
    for (const distance of [undefined, 0, 1, 7, 30]) {
      assert.equal(model.color(mode, { type: 'manifesto' }, distance), '#d3d3d3');
    }
    assert.notEqual(model.color(mode, { type: 'requirement' }, 1), '#d3d3d3');
    assert.notEqual(model.color(mode, { type: 'implementation' }, 2), '#d3d3d3');
  }
});

test('minimum and maximum distance count shortest/longest directed root paths', () => {
  const graph = snapshot([['root', 'a'], ['a', 'b'], ['b', 'c'], ['root', 'c']]);
  const before = JSON.stringify(graph), metrics = model.metrics(graph);
  assert.equal(metrics.minDistances.get('root'), 0);
  assert.equal(metrics.maxDistances.get('root'), 0);
  assert.equal(metrics.minDistances.get('b'), 2);
  assert.equal(metrics.maxDistances.get('b'), 2);
  assert.equal(metrics.minDistances.get('c'), 1);
  assert.equal(metrics.maxDistances.get('c'), 3);
  assert.equal(JSON.stringify(graph), before, 'Derived distances do not alter canonical records.');
});

test('distance bounds handle repeated/shared paths, input order, missing edges and unreachable nodes', () => {
  const graph = snapshot([['root', 'a'], ['root', 'b'], ['a', 'shared'], ['b', 'shared'],
    ['shared', 'deep'], ['root', 'deep'], ['root', 'a'], ['orphan', 'remote']], ['isolated']);
  graph.edges.push(['missing-parent', 'a'], ['deep', 'missing-child']);
  const metrics = model.metrics(graph);
  assert.equal(metrics.minDistances.get('shared'), 2);
  assert.equal(metrics.maxDistances.get('shared'), 2);
  assert.equal(metrics.minDistances.get('deep'), 1);
  assert.equal(metrics.maxDistances.get('deep'), 3);
  for (const id of ['orphan', 'remote', 'isolated', 'missing-parent', 'missing-child']) {
    assert.equal(metrics.minDistances.has(id), false);
    assert.equal(metrics.maxDistances.has(id), false);
  }
  const reordered = model.metrics({ ...graph, nodes: [...graph.nodes].reverse(), edges: [...graph.edges].reverse() });
  for (const key of ['minDistances', 'maxDistances']) assert.deepEqual([...metrics[key]].sort(), [...reordered[key]].sort());
});

test('defensive cycles keep minimum paths but never invent finite maximums for blocked descendants', () => {
  const graph = snapshot([['root', 'a'], ['a', 'b'], ['b', 'a'], ['a', 'blocked'],
    ['root', 'blocked'], ['root', 'safe'], ['safe', 'leaf'], ['root', 'loop'], ['loop', 'loop']]);
  const metrics = model.metrics(graph);
  assert.equal(metrics.minDistances.get('a'), 1);
  assert.equal(metrics.minDistances.get('blocked'), 1);
  for (const id of ['a', 'b', 'blocked', 'loop']) assert.equal(metrics.maxDistances.has(id), false);
  assert.equal(metrics.maxDistances.get('leaf'), 2);
  assert.equal(model.color('max-distance', {}, metrics.maxDistances.get('a')), '#929baa');
});

test('potential impact counts the entire descendant DAG, including deep shared nodes once', () => {
  const graph = snapshot([['root', 'child'], ['child', 'a'], ['child', 'b'],
    ['a', 'shared'], ['b', 'shared'], ['shared', 'great'], ['great', 'deep'], ['root', 'other'], ['other', 'shared']]);
  const before = JSON.stringify(graph);
  const metrics = model.metrics(graph);
  assert.equal(metrics.descendantCount('child'), 5);
  assert.equal(metrics.descendantCount('other'), 3);
  assert.equal(metrics.descendantCount('deep'), 0);
  assert.equal(metrics.descendantCount('root'), 7);
  assert.equal(JSON.stringify(graph), before, 'Presentation must not store derived scores in nodes.');
});

test('descendant traversal is iterative and guards against repeated paths or cycles', () => {
  const chain = Array.from({ length: 6000 }, (_, i) => [i ? `n${i - 1}` : 'root', `n${i}`]);
  const deep = model.metrics(snapshot(chain));
  assert.equal(deep.descendantCount('root'), 6000);
  assert.equal(deep.minDistances.get('n5999'), 6000);
  assert.equal(deep.maxDistances.get('n5999'), 6000);
  const cyclic = snapshot([['root', 'a'], ['a', 'b'], ['b', 'a']]);
  assert.equal(model.metrics(cyclic).descendantCount('a'), 1);
});

test('focused visibility includes direct neighbors and removed relations, not the whole closure', () => {
  const base = snapshot([['root', 'a'], ['a', 'b'], ['b', 'c']]);
  const target = snapshot([['root', 'a'], ['root', 'b'], ['b', 'c']]);
  const state = { snapshot: target, diff: { base, added_edges: [['root', 'b']], removed_edges: [['a', 'b']] } };
  const graph = model.displayGraph(state);
  assert.deepEqual(model.focusIds(graph.nodes, graph.edges, 'a').sort(), ['a', 'b', 'root']);
  assert.equal(model.metrics(base).descendantCount('a'), 2);
  assert.equal(model.metrics(target).descendantCount('a'), 0);
});

test('render acknowledgements verify complete focused or total membership', () => {
  const state = { snapshot: snapshot([['root', 'a'], ['a', 'b'], ['b', 'c']]) };
  const report = { view: 'focus', selectedId: 'a', visibleIds: ['root', 'a', 'b'], nodeCount: 3 };
  assert.ok(model.renderMatches(state, report));
  assert.equal(model.renderMatches(state, { ...report, visibleIds: ['a'], nodeCount: 1 }), false);
  assert.equal(model.renderMatches(state, { ...report, view: 'overview' }), false);
  assert.ok(model.renderMatches(state, { view: 'overview', visibleIds: ['root', 'a', 'b', 'c'], nodeCount: 4 }));
  assert.equal(model.renderMatches(state, { nodeCount: 4 }), false, 'API 5 requires full membership, not legacy counts.');
  assert.ok(model.renderMatches(state, { view: 'focus', creating: true, draftParents: ['root'], visibleIds: ['root'], nodeCount: 2 }));
});

test('draft baseline comparison uses normalized contents, not paths or hashes', () => {
  const node = { id: 'a', type: 'requirement', body: '# Body\r\n', parents: ['b', 'c'],
    sources: [{ path: 'b.py', symbol: 'two' }, { path: 'a.py' }], extensions: { 'example:note': { b: 2, a: 1 } } };
  const reordered = { ...node, body: '# Body\n', path: 'renamed.md', parents: ['c', 'b'],
    sources: [...node.sources].reverse(), extensions: { 'example:note': { a: 1, b: 2 } } };
  assert.equal(model.sameNode(node, reordered), true);
  for (const changes of [{ body: '# Changed' }, { parents: ['b'] }, { extensions: {} }, { sources: [] }]) {
    assert.equal(model.sameNode(node, { ...reordered, ...changes }), false);
  }
  for (const bad of [undefined, {}, { ...node, parents: 5 }, { ...node, body: 5 }, { ...node, sources: ['not a source'] }]) {
    assert.equal(model.sameNode(bad, node), false);
  }
});

test('expanded circle diameter contains the unchanged editor rectangle with breathing room', () => {
  assert.equal(model.DETAIL_CONTENT_WIDTH,822);
  for(const height of [250,720,900,1450,4000]) {
    const diameter=model.manifestoDiameter(822,height);
    assert.ok(Number.isInteger(diameter));
    assert.ok(diameter/2-Math.hypot(822/2,height/2)>=24);
    assert.ok(diameter/2-Math.hypot(822/2,height/2)<24.5);
  }
});

test('circle and rounded-corner ports attach at the actual outline, retaining clear horizontal leads', () => {
  const circle={x:80,y:100,width:264,height:264,shape:'circle'};
  const boxes=new Map([['root',circle],...Array.from({length:8},(_,i)=>['child'+i,{x:600,y:i*170,width:264,height:112,radius:24}])]);
  const records=Array.from({length:8},(_,i)=>({edge:['root','child'+i],kind:''}));
  const routes=model.routeEdges(boxes,records);
  assert.notEqual(routes[0].start.x,circle.x+circle.width+3);
  for(const route of routes) {
    assert.ok(Math.abs(Math.hypot(route.start.x-3-(circle.x+132),route.start.y-(circle.y+132))-132)<1e-8);
    assert.ok(route.points[1].x>circle.x+circle.width);
    assert.equal(route.points[1].y,route.start.y);
    assert.ok(route.points.at(-2).x<boxes.get(route.edge[1]).x);
    for(const scale of [1,0.12]) assert.ok(!model.edgeAppearance(route,scale).d.includes('NaN'));
    // Thick minimum-zoom ink must clear even the inward edge of the departure.
    for(const dy of [-model.MIN_STROKE_PIXELS/0.12/2,model.MIN_STROKE_PIXELS/0.12/2]) {
      assert.ok(Math.hypot(route.start.x-(circle.x+132),route.start.y+dy-(circle.y+132))>132);
    }
  }
  const reverse=model.routeEdges(boxes,[{edge:['child0','root'],kind:'removed'},{edge:['child7','root'],kind:'removed'}]);
  for(const route of reverse) {
    assert.ok(Math.abs(Math.hypot(route.end.x+3-(circle.x+132),route.end.y-(circle.y+132))-132)<1e-8);
    assert.ok(route.points.at(-2).x<circle.x);
    assert.ok(!route.d.includes('NaN'));
  }
  const rounded={x:0,y:0,width:264,height:112,radius:24};
  const inset=24-Math.sqrt(24**2-8**2);
  assert.equal(model.sideBoundary(rounded,16,false),inset);
  assert.equal(model.sideBoundary(rounded,16,true),264-inset);
  assert.equal(model.sideBoundary(rounded,56,false),0);
  assert.equal(model.sideBoundary({...rounded,radius:7},16,true),264);
  for(const y of [0,4,16,56,108,112]) {
    assert.equal(model.sideBoundary({...rounded,radius:0},y,false),0);
    assert.equal(model.sideBoundary({...rounded,radius:0},y,true),264);
  }
  const nodes=new Map([['root',{type:'manifesto'}],['child0',{type:'requirement'}]]);
  const layout=model.layoutGraph(nodes,[records[0]],new Map([['root',{width:264,height:264,shape:'circle'}],['child0',{width:264,height:112,radius:24}]]));
  assert.equal(layout.positions.get('root').shape,'circle');assert.equal(layout.positions.get('child0').radius,24);
});

test('side ports use measured card borders and splines retain horizontal endpoint tangents', () => {
  const boxes = new Map([['parent', { x: 80, y: 30, width: 310, height: 154 }],
    ['child', { x: 800, y: 400, width: 620, height: 850 }]]);
  const [route] = model.routeEdges(boxes, [{ edge: ['parent', 'child'], kind: '' }]);
  assert.equal(route.start.x, 393);
  assert.equal(route.start.y, 107);
  assert.equal(route.end.x, 797);
  assert.equal(route.end.y, 825);
  assert.match(route.d, /C/);
  const curves = route.curved.match(/C([^CLM]+)/g).map(segment => segment.slice(1).split(',').map(Number));
  assert.equal(curves[0][1], route.start.y);
  assert.equal(curves.at(-1)[3], route.end.y);
  assert.ok(route.points.every(point => Number.isFinite(point.x) && Number.isFinite(point.y)));
});

test('layered layout progresses left-to-right with engine waypoints for skipped levels', () => {
  const data = snapshot([['root', 'a'], ['a', 'b'], ['root', 'b']]);
  const nodes = new Map(data.nodes.map(node => [node.id, node])), edges = data.edges.map(edge => ({ edge, kind: '' }));
  const layout = model.layoutGraph(nodes, edges);
  for (const { edge: [a, b] } of edges) {
    assert.ok(layout.positions.get(a).x + model.CARD_WIDTH < layout.positions.get(b).x);
  }
  const routes = model.routeEdges(layout.positions, edges, layout.guides);
  assert.ok(routes.find(route => route.edge[0] === 'root' && route.edge[1] === 'b').points.length > 4);
  assert.ok(routes.every(route => route.d.includes('C')));
});

test('shorter label-free cards modestly widen rank/sibling gaps without a larger vertical pitch', () => {
  const data = snapshot([['root', 'a'], ['root', 'b']]);
  const layout = model.layoutGraph(new Map(data.nodes.map(n => [n.id, n])), data.edges.map(edge => ({ edge, kind: '' })));
  const root = layout.positions.get('root'), a = layout.positions.get('a'), b = layout.positions.get('b');
  assert.equal(model.CARD_HEIGHT, 112);
  assert.equal(a.x - root.x - root.width, model.RANK_GAP);
  assert.equal(Math.abs(a.y - b.y) - a.height, model.NODE_GAP);
  assert.ok(model.RANK_GAP > 128 && model.RANK_GAP <= 144);
  assert.ok(model.NODE_GAP > 36 && model.NODE_GAP <= 48);
  assert.ok(model.CARD_HEIGHT + model.NODE_GAP < 128 + 36, 'Less card content still improves net vertical density.');
});

test('layout is deterministic across input order and independent of display dimensions', () => {
  const data = snapshot([['root', 'a'], ['root', 'b'], ['a', 'c'], ['b', 'c']]);
  const edges = data.edges.map(edge => ({ edge, kind: '' }));
  const first = model.layoutGraph(new Map(data.nodes.map(node => [node.id, node])), edges);
  const second = model.layoutGraph(new Map([...data.nodes].reverse().map(node => [node.id, node])), [...edges].reverse());
  assert.deepEqual(first, second);
  assert.equal(model.layoutGraph.length, 2, 'There is no viewport dimension argument.');
});

test('focused expanded cards place upstream left, downstream right, and separate output sockets', () => {
  const data = snapshot([['root', 'focus'], ['focus', 'c1'], ['focus', 'c2']]);
  const edges = data.edges.map(edge => ({ edge, kind: '' }));
  const layout = model.layoutGraph(new Map(data.nodes.map(node => [node.id, node])), edges,
    new Map([['focus', { width: model.DETAIL_WIDTH, height: 1100 }]]));
  const box = layout.positions.get('focus');
  assert.equal(box.height, 1100);
  assert.ok(layout.positions.get('root').x + model.CARD_WIDTH < box.x);
  assert.ok(layout.positions.get('c1').x > box.x + box.width);
  const routes = model.routeEdges(layout.positions, edges, layout.guides).filter(route => route.edge[0] === 'focus');
  assert.notEqual(routes[0].start.y, routes[1].start.y);
  assert.ok(Math.abs(routes[0].start.y - routes[1].start.y) > 300, 'Expanded-card attachments must not bunch in a 64px header band.');
  assert.equal(routes[0].start.x, box.x + box.width + 3);
});

test('smoothing preserves the full-width obstacle corridor reserved at a skipped rank', () => {
  const boxes = new Map([['a', { x: 0, y: 0, width: 264, height: 128 }],
    ['obstacle', { x: 450, y: 100, width: 264, height: 128 }],
    ['b', { x: 900, y: 0, width: 264, height: 128 }]]);
  const guide = new Map([[JSON.stringify(['a', 'b']), [{ x: 264, y: 64 }, { x: 350, y: 20 },
    { x: 582, y: 20 }, { x: 800, y: 20 }, { x: 900, y: 64 }]]]);
  const [route] = model.routeEdges(boxes, [{ edge: ['a', 'b'], kind: '' }], guide);
  assert.deepEqual(route.points.slice(2, -2), [{ x: 432, y: 20 }, { x: 732, y: 20 }]);
  assert.match(route.d, /C/);
});

test('earliest root ranks keep shallow intentions near the manifesto despite a shared deep sink', () => {
  const data = snapshot([['root', 'shallow'], ['root', 'a'], ['a', 'b'], ['b', 'c'], ['c', 'sink'], ['shallow', 'sink']]);
  const edges = data.edges.map(edge => ({ edge, kind: '' }));
  const layout = model.layoutGraph(new Map(data.nodes.map(node => [node.id, node])), edges);
  assert.equal(layout.positions.get('shallow').x, layout.positions.get('a').x);
  assert.ok(layout.positions.get('shallow').x < layout.positions.get('b').x);
  const extended = snapshot([...data.edges, ['sink', 'later'], ['shallow', 'later']]);
  const expanded = model.layoutGraph(new Map(extended.nodes.map(node => [node.id, node])), extended.edges.map(edge => ({ edge, kind: '' })));
  assert.equal(expanded.positions.get('shallow').x, layout.positions.get('shallow').x, 'A new common sink cannot pull early intentions rightward.');
});

test('placement backbone compacts root neighbors vertically while rendering every dependency', () => {
  const children = ['a', 'b', 'c', 'd', 'e', 'f'];
  const edges = children.map(id => ['root', id]);
  for (let i = 0; i < 9; i++) edges.push(['b', `g${i}`], [`g${i}`, 'sink']);
  edges.push(...children.filter(id => id !== 'b').map(id => [id, 'sink']), ['sink', 'tail']);
  const data = snapshot(edges), nodes = new Map(data.nodes.map(node => [node.id, node]));
  const records = edges.map(edge => ({ edge, kind: '' })), before = JSON.stringify(data);
  const backbone = model.layoutBackbone(nodes, records);
  assert.equal(backbone.length, nodes.size - 1);
  assert.ok(backbone.some(item => item.edge[1] === 'sink' && item.edge[0].startsWith('g')), 'The deepest parent preserves full-parent rank.');
  const layout = model.layoutGraph(nodes, records), ys = children.map(id => layout.positions.get(id).y);
  assert.ok(Math.max(...ys) - Math.min(...ys) + model.CARD_HEIGHT <= children.length * (model.CARD_HEIGHT + 56));
  assert.equal(model.routeEdges(layout.positions, records, layout.guides).length, records.length, 'Omitted placement references are still drawn.');
  assert.equal(JSON.stringify(data), before, 'A presentation backbone cannot rewrite canonical parent metadata.');
});

test('earliest ranks respect every parent while context distance remains shortest hops', () => {
  const data = snapshot([['root', 'a'], ['a', 'b'], ['b', 'c'], ['root', 'c']]);
  const edges = data.edges.map(edge => ({ edge, kind: '' }));
  const layout = model.layoutGraph(new Map(data.nodes.map(node => [node.id, node])), edges);
  assert.ok(layout.positions.get('c').x > layout.positions.get('b').x + model.CARD_WIDTH);
  assert.equal(model.metrics(data).minDistances.get('c'), 1, 'Minimum path is not longest-path placement rank.');
  assert.equal(model.metrics(data).maxDistances.get('c'), 3);
});

test('old relations cannot pull live ranks away from the origin; base-only branches remain visible', () => {
  const data = snapshot([['root', 'a'], ['a', 'b'], ['b', 'c'], ['root', 'shallow']], ['old']);
  const edges = [...data.edges.map(edge => ({ edge, kind: '' })),
    { edge: ['c', 'shallow'], kind: 'removed' }, { edge: ['a', 'old'], kind: 'removed' }, { edge: ['old', 'shallow'], kind: 'removed' }];
  const layout = model.layoutGraph(new Map(data.nodes.map(node => [node.id, node])), edges, new Map(), { ids: new Set(['root', 'a', 'b', 'c', 'shallow']) });
  assert.equal(layout.positions.get('shallow').x, layout.positions.get('a').x);
  assert.equal(layout.positions.get('old').x, layout.positions.get('b').x);
  assert.equal(model.routeEdges(layout.positions, edges, layout.guides).length, edges.length);
  assert.ok(!layout.guides.has(JSON.stringify(['c', 'shallow'])));
});

test('strong bends settle tangentially before scale-stable heads, with no stroke through the tip', () => {
  const { MIN_SCALE, MAX_SCALE } = require('../media/graph-camera.js');
  const boxes = new Map([['a', { x: 0, y: 0, width: 264, height: 128 }],
    ['b', { x: 392, y: 5000, width: 264, height: 128 }]]);
  const [route] = model.routeEdges(boxes, [{ edge: ['a', 'b'], kind: '' }]);
  const settle = route.points.at(-2), last = route.curved.match(/C([^CLM]+)/g).at(-1).slice(1).split(',').map(Number);
  assert.equal(settle.x, route.end.x - model.EDGE_LEAD);
  assert.equal(settle.y, route.end.y);
  assert.equal(last[3], settle.y, 'Final control tangent aligns with the horizontal head approach.');
  for (const k of [MIN_SCALE, 0.25, 0.5, 1, MAX_SCALE]) {
    const appearance = model.edgeAppearance(route, k);
    assert.ok(appearance.strokeWidth * k >= model.MIN_STROKE_PIXELS - 1e-9);
    assert.ok(appearance.length * k >= model.MIN_ARROW_PIXELS - 1e-9);
    assert.ok(appearance.base.x > settle.x + 8, 'Reserve room for even the largest low-zoom head.');
    assert.ok(appearance.base.x < route.end.x);
    assert.equal(appearance.base.y, route.end.y);
    assert.ok(appearance.d.endsWith(`L${appearance.base.x},${appearance.base.y}`));
    assert.ok(appearance.head.includes(`L${route.end.x},${route.end.y}`));
  }
});

test('historical reverse connections also finish on a horizontal arrow approach', () => {
  const boxes = new Map([['a', { x: 80, y: 500, width: 264, height: 128 }],
    ['b', { x: 472, y: 0, width: 264, height: 128 }]]);
  const [route] = model.routeEdges(boxes, [{ edge: ['b', 'a'], kind: 'removed' }]);
  assert.equal(route.points.at(-2).x, route.end.x - model.EDGE_LEAD);
  assert.equal(route.points.at(-3).y, route.end.y);
  assert.equal(model.edgeAppearance(route, 0.12).base.y, route.end.y);
  assert.ok(!route.d.includes('NaN'));
});

test('cyclic historical overlays remain displayable with reversed removed links visible', () => {
  const data = snapshot([['root', 'a'], ['a', 'b']]);
  const edges = [...data.edges.map(edge => ({ edge, kind: '' })), { edge: ['b', 'a'], kind: 'removed' }];
  const layout = model.layoutGraph(new Map(data.nodes.map(node => [node.id, node])), edges);
  assert.ok(layout.positions.get('a').x < layout.positions.get('b').x);
  const routes = model.routeEdges(layout.positions, edges, layout.guides);
  assert.equal(routes.length, 3);
  assert.ok(routes.find(route => route.kind === 'removed').start.x > routes.find(route => route.kind === 'removed').end.x);
  assert.ok(routes.every(route => !route.d.includes('NaN')));
});
