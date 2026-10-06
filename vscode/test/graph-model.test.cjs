const { test } = require('node:test');
const assert = require('node:assert/strict');
const model = require('../media/graph-model.js');

function snapshot(edges, extra = []) {
  const ids = new Set(['root', ...edges.flat(), ...extra]);
  return { valid: true, nodes: [...ids].map(id => ({
    id, type: id === 'root' ? 'manifesto' : 'requirement', retired: false,
    parents: edges.filter(([, child]) => child === id).map(([parent]) => parent),
    body: `# ${id}\n`, sources: [],
  })), edges };
}

test('distance is shortest root hop count, not longest layout rank', () => {
  const graph = snapshot([['root', 'a'], ['a', 'b'], ['b', 'c'], ['root', 'c']]);
  const metrics = model.metrics(graph);
  assert.equal(metrics.distances.get('root'), 0);
  assert.equal(metrics.distances.get('b'), 2);
  assert.equal(metrics.distances.get('c'), 1);
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
  assert.equal(model.metrics(snapshot(chain)).descendantCount('root'), 6000);
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
  assert.ok(model.renderMatches(state, { view: 'focus', creating: true, draftParents: ['root'], visibleIds: ['root'], nodeCount: 2 }));
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
  assert.equal(model.metrics(data).distances.get('c'), 1, 'Visual rank is not the color/badge distance.');
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
