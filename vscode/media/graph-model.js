/* Presentation-only graph calculations. Python remains authoritative for validation. */
(function (root, factory) {
  const commonJS = typeof module === 'object' && module.exports;
  const api = factory(commonJS ? require('./vendor/graph-vendor.js') : root.SpecSpecVendor);
  if (commonJS) module.exports = api;
  else root.SpecSpecGraph = api;
})(globalThis, vendor => {
  'use strict';
  const CARD_WIDTH = 264, CARD_HEIGHT = 128, DETAIL_WIDTH = 620;
  const edgeKey = edge => JSON.stringify(edge);
  const compare = (a, b) => a < b ? -1 : a > b ? 1 : 0;
  const STATUS_COLORS = { accepted: '#37ad83', proposed: '#e8aa42', retired: '#929baa' };
  const DEPTH_COLORS = ['#6699ee', '#a786eb', '#43b5b0', '#dd9b48', '#dc7aab', '#84b466', '#7d9ed2'];

  function displayGraph(state) {
    const nodes = new Map([...(state.diff?.base.nodes || []), ...state.snapshot.nodes].map(node => [node.id, node]));
    const added = new Set((state.diff?.added_edges || []).map(edge => JSON.stringify(edge)));
    const edges = state.snapshot.edges.map(edge => ({ edge, kind: added.has(JSON.stringify(edge)) ? 'added' : '' }));
    const present = new Set(edges.map(item => JSON.stringify(item.edge)));
    for (const edge of state.diff?.removed_edges || []) {
      if (!present.has(JSON.stringify(edge))) edges.push({ edge, kind: 'removed' });
    }
    return { nodes, edges };
  }

  function focusIds(nodes, edges, id) {
    if (!nodes.has(id)) return [];
    const ids = new Set([id]);
    for (const { edge: [parent, child] } of edges) {
      if (parent === id && nodes.has(child)) ids.add(child);
      if (child === id && nodes.has(parent)) ids.add(parent);
    }
    return [...ids];
  }

  function renderMatches(state, message) {
    const { nodes, edges } = displayGraph(state);
    if (message.view === undefined) return message.nodeCount === nodes.size;
    if (!Array.isArray(message.visibleIds) || new Set(message.visibleIds).size !== message.visibleIds.length
      || message.visibleIds.some(id => !nodes.has(id))) return false;
    let expected;
    if (message.view === 'overview') expected = [...nodes.keys()];
    else if (message.view === 'focus' && !message.creating) expected = focusIds(nodes, edges, message.selectedId);
    else if (message.view === 'focus' && message.creating && Array.isArray(message.draftParents)) {
      expected = [...new Set(message.draftParents)];
      if (expected.some(id => !nodes.has(id))) return false;
    } else return false;
    return (message.creating || message.view === 'overview' || expected.length > 0)
      && expected.length === message.visibleIds.length
      && expected.every(id => message.visibleIds.includes(id))
      && message.nodeCount === expected.length + (message.creating ? 1 : 0);
  }

  function metrics(snapshot) {
    const nodes = new Map(snapshot.nodes.map(node => [node.id, node]));
    const children = new Map(snapshot.nodes.map(node => [node.id, new Set()]));
    for (const [parent, child] of snapshot.edges) {
      if (nodes.has(child)) children.get(parent)?.add(child);
    }
    const distances = new Map();
    const queue = snapshot.nodes.filter(node => node.type === 'manifesto').map(node => node.id);
    queue.forEach(id => distances.set(id, 0));
    for (let index = 0; index < queue.length; index++) {
      const id = queue[index];
      for (const child of children.get(id) || []) {
        if (!distances.has(child)) {
          distances.set(child, distances.get(id) + 1);
          queue.push(child);
        }
      }
    }
    const descendantCounts = new Map();
    function descendantCount(id) {
      if (!descendantCounts.has(id)) {
        const seen = new Set([id]), stack = [...(children.get(id) || [])];
        while (stack.length) {
          const current = stack.pop();
          if (seen.has(current)) continue;
          seen.add(current);
          for (const child of children.get(current) || []) stack.push(child);
        }
        descendantCounts.set(id, seen.size - 1);
      }
      return descendantCounts.get(id);
    }
    return { distances, children, descendantCount };
  }

  function color(mode, node, distance) {
    if (mode === 'status') return STATUS_COLORS[node.status] || '#929baa';
    return Number.isInteger(distance) ? DEPTH_COLORS[distance % DEPTH_COLORS.length] : '#929baa';
  }

  // Only graph structure and intrinsic node sizes enter this function. No viewport.
  function layoutGraph(nodes, records, sizes = new Map()) {
    const engine = new vendor.dagre.graphlib.Graph({ multigraph: true });
    engine.setGraph({ rankdir: 'LR', ranksep: 160, nodesep: 56, edgesep: 24,
      marginx: 80, marginy: 80, acyclicer: 'greedy', ranker: 'network-simplex' });
    engine.setDefaultEdgeLabel(() => ({}));
    for (const id of [...nodes.keys()].sort(compare)) {
      const size = sizes.get(id);
      engine.setNode(id, { width: size?.width || CARD_WIDTH, height: size?.height || CARD_HEIGHT });
    }
    const edges = records.filter(({ edge: [a, b] }) => nodes.has(a) && nodes.has(b))
      .slice().sort((a, b) => compare(edgeKey(a.edge), edgeKey(b.edge)));
    for (const { edge: [a, b], kind } of edges) {
      // Removed relations can make an overlay cyclic. This is display, not validation.
      engine.setEdge(a, b, { weight: kind === 'removed' ? 1 : 8 }, edgeKey([a, b]));
    }
    if (nodes.size) vendor.dagre.layout(engine);
    const positions = new Map(), guides = new Map();
    for (const id of engine.nodes()) {
      const box = engine.node(id);
      positions.set(id, { x: box.x - box.width / 2, y: box.y - box.height / 2, width: box.width, height: box.height });
    }
    for (const edge of engine.edges()) guides.set(edge.name, engine.edge(edge).points);
    return { positions, guides, width: engine.graph().width || 480, height: engine.graph().height || 320 };
  }

  function routeEdges(positions, records, guides = new Map()) {
    const edges = records.filter(({ edge: [a, b] }) => positions.has(a) && positions.has(b));
    const incoming = new Map(), outgoing = new Map();
    for (const item of edges) {
      const [a, b] = item.edge;
      if (!outgoing.has(a)) outgoing.set(a, []);
      if (!incoming.has(b)) incoming.set(b, []);
      outgoing.get(a).push(item); incoming.get(b).push(item);
    }
    outgoing.forEach(list => list.sort((a, b) => positions.get(a.edge[1]).y - positions.get(b.edge[1]).y || compare(a.edge[1], b.edge[1])));
    incoming.forEach(list => list.sort((a, b) => positions.get(a.edge[0]).y - positions.get(b.edge[0]).y || compare(a.edge[0], b.edge[0])));
    const curve = vendor.line().x(point => point.x).y(point => point.y).curve(vendor.curveBumpX);
    const reverseCurve = vendor.line().x(point => point.x).y(point => point.y).curve(vendor.curveBasis);
    const port = (box, list, item) => box.y + 32 + Math.min(64, box.height - 48) * (list.indexOf(item) + 1) / (list.length + 1);
    return edges.map((item, index) => {
      const [a, b] = item.edge, from = positions.get(a), to = positions.get(b);
      const start = { x: from.x + from.width + 3, y: port(from, outgoing.get(a), item) };
      const end = { x: to.x - 9, y: port(to, incoming.get(b), item) };
      const guide = guides.get(edgeKey(item.edge)) || [];
      let points;
      if (end.x > start.x) {
        // Dagre's dummy waypoints reserve a lane THROUGH each skipped rank. Keep
        // that lane flat across the full card-width band before smoothing the gaps.
        const corridor = guide.slice(1, -1).flatMap(point => {
          const column = [...positions.values()].filter(box => box.x < point.x && box.x + box.width > point.x);
          if (!column.length) return [];
          const left = Math.min(...column.map(box => box.x)) - 18;
          const right = Math.max(...column.map(box => box.x + box.width)) + 18;
          return [{ x: left, y: point.y }, { x: right, y: point.y }];
        }).filter(point => point.x > start.x && point.x < end.x);
        points = [start, ...corridor, end];
      } else {
        // Historical reverse links loop around the world, retaining their direction.
        const lane = Math.min(...[...positions.values()].map(box => box.y)) - 36 - (index % 4) * 8;
        const column = box => [...positions.values()].filter(other => Math.abs(other.x + other.width / 2 - box.x - box.width / 2) < 1);
        const departure = Math.max(...column(from).map(box => box.x + box.width)) + 48;
        const arrival = Math.min(...column(to).map(box => box.x)) - 48;
        points = [start, { x: departure, y: start.y }, { x: departure, y: lane },
          { x: arrival, y: lane }, { x: arrival, y: end.y }, end];
      }
      return { ...item, start, end, points, d: (end.x > start.x ? curve : reverseCurve)(points) };
    });
  }

  return { CARD_WIDTH, CARD_HEIGHT, DETAIL_WIDTH, STATUS_COLORS, DEPTH_COLORS,
    displayGraph, focusIds, renderMatches, metrics, color, layoutGraph, routeEdges };
});
