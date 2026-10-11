/* Presentation-only graph calculations. Python remains authoritative for validation. */
(function (root, factory) {
  const commonJS = typeof module === 'object' && module.exports;
  const api = factory(commonJS ? require('./vendor/graph-vendor.js') : root.SpecSpecVendor);
  if (commonJS) module.exports = api;
  else root.SpecSpecGraph = api;
})(globalThis, vendor => {
  'use strict';
  const CARD_WIDTH = 264, CARD_HEIGHT = 112, DETAIL_WIDTH = 860;
  const RANK_GAP = 140, NODE_GAP = 44;
  const edgeKey = edge => JSON.stringify(edge);
  const compare = (a, b) => a < b ? -1 : a > b ? 1 : 0;
  const TYPE_COLORS = { manifesto: '#d3d3d3', requirement: '#43b5b0', implementation: '#a786eb' };
  const DEPTH_COLORS = ['#6699ee', '#a786eb', '#43b5b0', '#dd9b48', '#dc7aab', '#84b466', '#7d9ed2'];

  function sameNode(left, right) {
    if ([left, right].some(node => !node || typeof node.body !== 'string'
      || !Array.isArray(node.parents) || !Array.isArray(node.sources)
      || node.sources.some(source => !source || typeof source.path !== 'string'))) return false;
    const sorted = value => Array.isArray(value) ? value.map(sorted)
      : value && typeof value === 'object' ? Object.fromEntries(Object.keys(value).sort().map(key => [key, sorted(value[key])])) : value;
    const contents = node => ({ id: node.id, type: node.type, retired: Boolean(node.retired),
      body: node.body?.replace(/\r\n/g, '\n'), parents: [...(node.parents || [])].sort(),
      sources: [...(node.sources || [])].sort((a, b) => compare(a.path, b.path) || compare(a.symbol || '', b.symbol || '')),
      extensions: node.extensions || {}, format_version: node.format_version });
    return JSON.stringify(sorted(contents(left))) === JSON.stringify(sorted(contents(right)));
  }

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
    const minDistances = new Map(), maxDistances = new Map();
    const roots = snapshot.nodes.filter(node => node.type === 'manifesto').map(node => node.id);
    const queue = [...roots];
    queue.forEach(id => minDistances.set(id, 0));
    for (let index = 0; index < queue.length; index++) {
      const id = queue[index];
      for (const child of children.get(id) || []) {
        if (!minDistances.has(child)) {
          minDistances.set(child, minDistances.get(id) + 1);
          queue.push(child);
        }
      }
    }
    // Full snapshot relationships, never a focus/placement forest or revision
    // union. Deduplicated indegrees keep this iterative even for very deep DAGs.
    const remaining = new Map(snapshot.nodes.map(node => [node.id, 0]));
    for (const list of children.values()) for (const child of list) remaining.set(child, remaining.get(child) + 1);
    const ready = [...remaining.keys()].filter(id => !remaining.get(id)), candidates = new Map();
    for (const id of roots) if (!remaining.get(id)) maxDistances.set(id, 0);
    for (let index = 0; index < ready.length; index++) {
      const id = ready[index];
      for (const child of children.get(id) || []) {
        if (maxDistances.has(id)) candidates.set(child, Math.max(candidates.get(child) ?? -1, maxDistances.get(id) + 1));
        remaining.set(child, remaining.get(child) - 1);
        if (!remaining.get(child)) {
          if (candidates.has(child)) maxDistances.set(child, candidates.get(child));
          ready.push(child);
        }
      }
    }
    // A cycle (and its blocked descendants) has no finite maximum; leave unknown.
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
    return { minDistances, maxDistances, children, descendantCount };
  }

  function color(mode, node, distance) {
    if (node.type === 'manifesto') return TYPE_COLORS.manifesto;
    if (mode === 'type') return TYPE_COLORS[node.type] || '#929baa';
    return Number.isInteger(distance) ? DEPTH_COLORS[distance % DEPTH_COLORS.length] : '#929baa';
  }

  function layoutBackbone(nodes, edges) {
    const parents = new Map([...nodes.keys()].map(id => [id, []]));
    const children = new Map([...nodes.keys()].map(id => [id, []]));
    for (const { edge: [a, b] } of edges) { parents.get(b).push(a); children.get(a).push(b); }
    const remaining = new Map([...parents].map(([id, list]) => [id, list.length]));
    const queue = [...nodes.keys()].filter(id => !remaining.get(id)).sort(compare), ranks = new Map();
    queue.forEach(id => ranks.set(id, 0));
    for (let index = 0; index < queue.length; index++) {
      const id = queue[index];
      for (const child of children.get(id)) {
        ranks.set(child, Math.max(ranks.get(child) || 0, ranks.get(id) + 1));
        remaining.set(child, remaining.get(child) - 1);
        if (!remaining.get(child)) queue.push(child);
      }
    }
    // Defensive cyclic data still goes through Dagre's display-only cycle breaker.
    if (queue.length !== nodes.size) return edges;
    const chosen = new Map([...parents].filter(([, list]) => list.length).map(([id, list]) =>
      [id, list.filter(parent => ranks.get(parent) === ranks.get(id) - 1).sort(compare)[0]]));
    // This is a placement forest only. ALL records remain rendered and canonical
    // parents never change. A deepest parent preserves each all-parent rank.
    return edges.filter(({ edge: [a, b] }) => chosen.get(b) === a);
  }

  // Only graph structure and intrinsic node sizes enter this function. No viewport.
  function layoutGraph(nodes, records, sizes = new Map(), primary = {}) {
    const engine = new vendor.dagre.graphlib.Graph({ multigraph: true });
    // Longest-path normally anchors at sinks. Reverse input + RL instead gives
    // earliest SOURCE ranks: rank(node) = 1 + max(rank(parent)). Visible flow is LR.
    engine.setGraph({ rankdir: 'RL', ranksep: RANK_GAP, nodesep: NODE_GAP, edgesep: 16,
      marginx: 80, marginy: 80, acyclicer: 'greedy', ranker: 'longest-path' });
    engine.setDefaultEdgeLabel(() => ({}));
    for (const id of [...nodes.keys()].sort(compare)) {
      const size = sizes.get(id);
      engine.setNode(id, { width: size?.width || CARD_WIDTH, height: size?.height || CARD_HEIGHT });
    }
    const primaryIds = primary.ids || new Set(nodes.keys());
    const primaryEdges = primary.edges || new Set(records.filter(item => item.kind !== 'removed').map(item => edgeKey(item.edge)));
    const edges = records.filter(({ edge: [a, b] }) => nodes.has(a) && nodes.has(b))
      .slice().sort((a, b) => compare(edgeKey(a.edge), edgeKey(b.edge)));
    // Old references into surviving nodes cannot shift live ranks. A compact
    // rank-preserving backbone also prevents shared sinks from stretching the
    // origin vertically; omitted placement edges are still routed below.
    const constraints = edges.filter(item => primaryEdges.has(edgeKey(item.edge)) || !primaryIds.has(item.edge[1]));
    for (const { edge: [a, b] } of layoutBackbone(nodes, constraints)) {
      engine.setEdge(b, a, { weight: 8 }, edgeKey([a, b]));
    }
    if (nodes.size) vendor.dagre.layout(engine);
    const positions = new Map(), guides = new Map();
    for (const id of engine.nodes()) {
      const box = engine.node(id);
      positions.set(id, { x: box.x - box.width / 2, y: box.y - box.height / 2, width: box.width, height: box.height });
    }
    for (const edge of engine.edges()) guides.set(edge.name, [...engine.edge(edge).points].reverse());
    return { positions, guides, width: engine.graph().width || 480, height: engine.graph().height || 320 };
  }

  const EDGE_LEAD = 64, MIN_STROKE_PIXELS = 1.6, MIN_ARROW_PIXELS = 6;

  function routeEdges(positions, records, guides = new Map()) {
    const edges = records.filter(({ edge: [a, b] }) => positions.has(a) && positions.has(b));
    const incoming = new Map(), outgoing = new Map(), boxes = [...positions.values()];
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
    // Include the full intrinsic height: header-only ports make an expanded form
    // impose huge artificial bends even when Dagre has aligned node centers.
    const port = (box, list, item) => box.y + 16 + Math.max(0, box.height - 32) * (list.indexOf(item) + 1) / (list.length + 1);
    const column = box => boxes.filter(other => Math.abs(other.x + other.width / 2 - box.x - box.width / 2) < 1);
    return edges.map((item, index) => {
      const [a, b] = item.edge, from = positions.get(a), to = positions.get(b);
      const start = { x: from.x + from.width + 3, y: port(from, outgoing.get(a), item) };
      const end = { x: to.x - 3, y: port(to, incoming.get(b), item) };
      // Smooth to this horizontal settling point, not into a tight bend beneath
      // the arrowhead. It covers even the largest head at the camera's 12% limit.
      const settle = { x: end.x - EDGE_LEAD, y: end.y };
      const guide = guides.get(edgeKey(item.edge)) || [];
      let points, curved;
      const launch = { x: start.x + 16, y: start.y };
      if (settle.x > launch.x) {
        // Keep reserved lanes flat across the full width of skipped columns.
        let corridor = guide.slice(1, -1).flatMap(point => {
          const band = boxes.filter(box => box.x < point.x && box.x + box.width > point.x);
          if (!band.length) return [];
          return [{ x: Math.min(...band.map(box => box.x)) - 18, y: point.y },
            { x: Math.max(...band.map(box => box.x + box.width)) + 18, y: point.y }];
        }).filter(point => point.x > launch.x && point.x < settle.x);
        if (!guide.length) {
          // Non-backbone/overlaid relations still cross every skipped column.
          // Choose the nearest clear row gap, with an outer lane as fallback;
          // unrelated dependency links must not stretch the placement forest.
          const crossed = boxes.filter(box => box.x > launch.x && box.x + box.width < settle.x);
          const bands = new Map(crossed.map(box => [box.x + box.width / 2, column(box)]));
          corridor = [...bands].sort(([a], [b]) => a - b).flatMap(([center, band]) => {
            const left = Math.min(...band.map(box => box.x)) - 18;
            const right = Math.max(...band.map(box => box.x + box.width)) + 18;
            if (left <= launch.x || right >= settle.x) return [];
            const desired = start.y + (end.y - start.y) * (center - launch.x) / (settle.x - launch.x);
            const ordered = band.slice().sort((a, b) => a.y - b.y);
            const candidates = [ordered[0].y - 24, Math.max(...ordered.map(box => box.y + box.height)) + 24];
            for (let i = 1; i < ordered.length; i++) {
              const low = ordered[i - 1].y + ordered[i - 1].height + 18, high = ordered[i].y - 18;
              if (low <= high) candidates.push(Math.max(low, Math.min(high, desired)));
            }
            const lane = candidates.sort((a, b) => Math.abs(a - desired) - Math.abs(b - desired) || a - b)[0];
            return [{ x: left, y: lane }, { x: right, y: lane }];
          });
        }
        points = [start, launch, ...corridor, settle]; curved = curve(points);
      } else {
        // Historical reverse links loop around the world, retaining direction.
        const lane = Math.min(...boxes.map(box => box.y)) - 40 - (index % 4) * 8;
        const departure = Math.max(...column(from).map(box => box.x + box.width)) + 64;
        const arrival = Math.min(...column(to).map(box => box.x)) - 96;
        points = [start, { x: departure, y: start.y }, { x: departure, y: lane },
          { x: arrival, y: lane }, { x: arrival, y: end.y }, { x: settle.x - 16, y: end.y }, settle];
        curved = reverseCurve(points);
      }
      return { ...item, start, end, points: [...points, end], curved, d: `${curved}L${end.x},${end.y}` };
    });
  }

  function edgeAppearance(route, scale = 1) {
    const k = Number.isFinite(scale) && scale > 0 ? scale : 1;
    const strokeWidth = Math.max(1.7, MIN_STROKE_PIXELS / k);
    const length = Math.max(10, MIN_ARROW_PIXELS / k), half = length * 0.4;
    const base = { x: route.end.x - length, y: route.end.y };
    // The line stops at the filled head's base, never poking through its tip.
    return { strokeWidth, base, length,
      dashScale: Math.max(1, 1 / k),
      d: `${route.curved}L${base.x},${base.y}`,
      head: `M${base.x},${base.y - half}L${route.end.x},${route.end.y}L${base.x},${base.y + half}Z` };
  }

  return { CARD_WIDTH, CARD_HEIGHT, DETAIL_WIDTH, RANK_GAP, NODE_GAP, TYPE_COLORS, DEPTH_COLORS,
    EDGE_LEAD, MIN_STROKE_PIXELS, MIN_ARROW_PIXELS,
    sameNode, displayGraph, focusIds, renderMatches, metrics, color, layoutBackbone, layoutGraph, routeEdges, edgeAppearance };
});
