/* Project content is data: use textContent/value, never project-supplied HTML. */
(() => {
  const vscode = acquireVsCodeApi(), model = window.SpecSpecGraph;
  const $ = id => document.getElementById(id);
  const restored = vscode.getState() || {};
  let state, graph = { nodes: new Map(), edges: [] }, targetMetrics, baseMetrics;
  let selected = restored.selected, view = restored.view || (selected || restored.creating ? 'focus' : 'overview');
  let colorMode = restored.colorMode === 'type' ? 'type' : 'distance';
  let dirty = false, pending = false, creating = false, formFingerprint, formParents = [];
  let layoutFrame, layout, layoutKey, cameraScene;
  let drawnEdges = [], hoveredNode, hoverPoint;
  const cameraAPI = window.SpecSpecCamera;
  const cameras = Object.fromEntries(Object.entries(restored.cameras || {})
    .map(([key, value]) => [key, cameraAPI.validTransform(value)]).filter(([, value]) => value));
  const sceneKey = () => view === 'overview' ? 'overview' : creating ? 'draft' : `focus:${selected}`;
  const camera = cameraAPI.createCamera($('viewport'), $('graph'), {
    onChange: (value, finished) => {
      if (cameraScene) cameras[cameraScene] = value;
      $('zoom-level').textContent = `${Math.round(value.k * 100)}%`;
      updateEdgeAppearance(value.k);
      syncHover();
      if (finished && state) saveDraft();
    }, onFrame: () => frameAll(),
  });
  const elements = ['body', 'sources', 'slug', 'node-type'];
  const title = node => node.body.split(/\r?\n/).find(line => line.startsWith('#'))?.replace(/^#+\s*/, '') || node.body.split(/\r?\n/).find(line => line.trim()) || node.type;
  const send = message => vscode.postMessage(message);
  const setMessage = message => { $('message').textContent = message; };
  const currentNodeById = id => state?.snapshot.nodes.find(node => node.id === id);
  const currentNode = () => currentNodeById(selected);
  const legacyWorkspace = () => state?.snapshot.valid && !state.readonly && state.snapshot.format_version === 1;
  const editable = () => state?.snapshot.valid && state.snapshot.format_version === 2 && !state.readonly && (creating || Boolean(currentNode()));
  const description = node => `${node.type}${node.retired ? ' · retired' : ''}`;
  const formNodeType = () => creating ? $('node-type').value : graph.nodes.get(selected)?.type;
  const parentsEditable = () => editable() && !pending && formNodeType() !== 'manifesto';
  const contextFor = id => currentNodeById(id) ? targetMetrics : baseMetrics || targetMetrics;
  const snapshotName = id => currentNodeById(id) ? 'target' : 'base';

  function saveDraft() {
    vscode.setState({ selected, view, colorMode, cameras: { ...cameras }, dirty, creating, formFingerprint, draft: dirty || creating ? {
      body: $('body').value, sources: $('sources').value, slug: $('slug').value,
      nodeType: $('node-type').value, parents: [...formParents],
    } : undefined });
  }

  function updateButtons() {
    $('back').hidden = view !== 'focus';
    $('back').disabled = pending;
    $('frame-node').hidden = view !== 'focus';
    $('resume').hidden = view !== 'overview' || !(dirty || creating);
    $('resume').disabled = pending;
    $('new').disabled = !state?.snapshot.valid || state.snapshot.format_version !== 2 || state.readonly || pending;
    $('migrate').hidden = !legacyWorkspace();
    $('migrate').disabled = !legacyWorkspace() || pending || dirty || creating;
    $('save').disabled = !editable() || pending;
    const withdrawn = Boolean(graph.nodes.get(selected)?.retired);
    $('retire').hidden = withdrawn;
    $('restore').hidden = !withdrawn || creating;
    $('retire').disabled = !editable() || creating || dirty || pending || currentNode()?.type === 'manifesto' || withdrawn;
    $('restore').disabled = !editable() || creating || dirty || pending || !withdrawn;
    for (const id of elements) $(id).disabled = !editable() || pending;
    $('parent-candidate').disabled = !parentsEditable();
    $('add-parent').disabled = !parentsEditable() || !$('parent-candidate').value;
    for (const button of $('parent-links').querySelectorAll('button')) button.disabled = !parentsEditable();
  }

  function changes() {
    const kinds = new Map((state?.diff?.changes || []).map(change => [change.id, change.kind]));
    for (const id of state?.diff?.source_affected || []) if (!kinds.has(id)) kinds.set(id, 'source-changed');
    return kinds;
  }

  function cardIdAt(target) {
    const card = target?.closest?.('.card');
    return card?.parentElement === $('cards') ? card.dataset.nodeId : undefined;
  }

  function updateEdgeHighlights() {
    const plain = [], highlighted = [];
    for (const pair of drawnEdges) {
      const incident = hoveredNode !== undefined && pair.route.edge.includes(hoveredNode);
      pair.path.classList.toggle('incident-highlight', incident);
      pair.head.classList.toggle('incident-highlight', incident);
      (incident ? highlighted : plain).push(pair);
    }
    // Existing pairs only: highlight crossings without touching geometry/forms.
    const fragment = document.createDocumentFragment();
    for (const { path, head } of [...plain, ...highlighted]) fragment.append(path, head);
    $('edges').append(fragment);
  }

  function setHoveredNode(id) {
    if (id === hoveredNode) return;
    hoveredNode = id; updateEdgeHighlights();
  }

  function clearHover() { hoverPoint = undefined; setHoveredNode(undefined); }

  function syncHover() {
    if (hoverPoint && typeof document.elementFromPoint === 'function') {
      setHoveredNode(cardIdAt(document.elementFromPoint(hoverPoint.x, hoverPoint.y)));
    } else if (hoveredNode !== undefined && ![...$('cards').children].some(card => card.dataset.nodeId === hoveredNode)) {
      setHoveredNode(undefined);
    }
  }

  function trackHover(event) {
    if (event.pointerType === 'touch') { clearHover(); return; }
    hoverPoint = { x: event.clientX, y: event.clientY };
    setHoveredNode(cardIdAt(event.target));
  }
  for (const event of ['pointerover', 'pointermove']) $('viewport').addEventListener(event, trackHover);
  $('viewport').addEventListener('pointerout', event => {
    if (event.pointerType === 'touch' || !(event.relatedTarget instanceof Element) || !$('viewport').contains(event.relatedTarget)) {
      clearHover(); return;
    }
    hoverPoint = { x: event.clientX, y: event.clientY };
    setHoveredNode(cardIdAt(event.relatedTarget));
  });
  for (const event of ['pointerleave', 'pointercancel']) $('viewport').addEventListener(event, clearHover);
  window.addEventListener('blur', clearHover);

  function neighbors() {
    if (creating) return { parents: formParents.filter(id => graph.nodes.has(id)), children: [] };
    const parents = new Set(), children = new Set();
    for (const { edge: [a, b] } of graph.edges) {
      if (b === selected && graph.nodes.has(a)) parents.add(a);
      if (a === selected && graph.nodes.has(b)) children.add(b);
    }
    const sorted = ids => [...ids].sort((a, b) => title(graph.nodes.get(a)).localeCompare(title(graph.nodes.get(b))) || a.localeCompare(b));
    return { parents: sorted(parents), children: sorted(children) };
  }

  function drawLegend() {
    $('color-mode').value = colorMode;
    $('legend').replaceChildren();
    const entries = colorMode === 'type' ? Object.entries(model.TYPE_COLORS)
      : [...new Set([...graph.nodes.keys()].map(id => contextFor(id)?.distances.get(id)).filter(Number.isInteger))]
        .sort((a, b) => a - b).map(depth => [`${depth} hop${depth === 1 ? '' : 's'}`, model.color('distance', {}, depth)]);
    for (const [label, color] of entries) {
      const item = document.createElement('span'), swatch = document.createElement('i');
      swatch.style.backgroundColor = color; item.append(swatch, document.createTextNode(label));
      $('legend').append(item);
    }
    const explanation = document.createElement('span');
    explanation.className = 'legend-help';
    explanation.textContent = colorMode === 'distance' ? 'Shortest path from manifesto · not a confidence score' : 'Existing node types · not review stages';
    $('legend').append(explanation);
  }

  function compactCard(id, kind, related) {
    const node = graph.nodes.get(id), context = contextFor(id), distance = context?.distances.get(id);
    const card = document.createElement('button');
    card.type = 'button'; card.className = `card ${node.type} ${kind || ''}`;
    card.dataset.nodeId = id; card.dataset.retired = String(Boolean(node.retired));
    card.dataset.relation = related || ''; card.dataset.distance = distance ?? 'unknown';
    card.style.setProperty('--node-accent', model.color(colorMode, node, distance));
    card.title = `${id}\n${node.path}\n${snapshotName(id)} revision context`;
    const heading = document.createElement('strong'); heading.textContent = title(node);
    const metadata = document.createElement('small'); metadata.textContent = `${description(node)} · ${id.slice(0, 8)}`;
    const badges = document.createElement('span'); badges.className = 'badges';
    function badge(text, className, tooltip) {
      const item = document.createElement('span'); item.className = `badge ${className}`; item.textContent = text;
      if (tooltip) item.title = tooltip;
      badges.append(item);
    }
    if (related === 'parent' || related === 'both' || colorMode === 'distance') {
      badge(`Manifesto: ${distance ?? '?'} hop${distance === 1 ? '' : 's'}`, 'distance-badge', 'Shortest directed path in this node’s revision.');
    }
    if (related === 'child' || related === 'both') {
      const count = context?.descendantCount(id) ?? 0;
      card.dataset.downstream = count;
      badge(`${count} downstream`, 'downstream-badge', 'All reachable descendants at every depth, excluding this child. Shared nodes counted once per child; totals may overlap. Potential impact, not guaranteed invalidation.');
    }
    if (node.retired) badge('retired', 'retired-badge', 'Withdrawn, retained as history. Not an approval level.');
    if (kind) badge(kind.replace(/-/g, ' '), `git-badge ${kind}`);
    card.append(heading, metadata, badges);
    card.addEventListener('click', () => select(id));
    return card;
  }

  function draw() {
    if (!state) return;
    if (!creating && !graph.nodes.has(selected)) view = 'overview';
    // Move the SAME form DOM, preserving values, handlers and draft fingerprint.
    const activeInput = document.activeElement;
    const caret = activeInput?.tagName === 'TEXTAREA' ? [activeInput.selectionStart, activeInput.selectionEnd, activeInput.selectionDirection] : undefined;
    $('detail-parking').append($('node-details'));
    $('cards').replaceChildren();
    const kinds = changes(), related = neighbors();
    const ids = view === 'overview' ? [...graph.nodes.keys()] : creating
      ? related.parents : model.focusIds(graph.nodes, graph.edges, selected);
    const focalId = creating ? '__draft__' : selected;
    for (const id of ids) {
      if (view === 'focus' && id === selected) continue;
      const role = view === 'focus' ? related.parents.includes(id)
        ? related.children.includes(id) ? 'both' : 'parent' : 'child' : '';
      $('cards').append(compactCard(id, kinds.get(id), role));
    }
    if (view === 'focus') {
      const card = document.createElement('article'), node = graph.nodes.get(selected);
      card.className = `card expanded ${creating ? $('node-type').value : node.type} ${kinds.get(selected) || ''}`;
      card.dataset.nodeId = focalId; card.dataset.retired = String(Boolean(!creating && node?.retired));
      card.style.setProperty('--node-accent', model.color(colorMode, node || { type: $('node-type').value }, contextFor(selected)?.distances.get(selected)));
      card.append($('node-details')); $('cards').append(card);
    }
    drawLegend(); updateButtons(); applyLayout();
    if ($('cards').contains(activeInput) && !activeInput.disabled) {
      activeInput.focus({ preventScroll: true });
      if (caret) activeInput.setSelectionRange(...caret);
    }
    send({ type: 'rendered', renderToken: state.renderToken, view, selectedId: selected, creating: creating && view === 'focus',
      visibleIds: ids, draftParents: creating && view === 'focus' ? [...related.parents] : undefined,
      nodeCount: $('cards').children.length, fingerprint: state.snapshot.fingerprint });
  }

  function applyLayout() {
    if (!state || !$('cards').children.length) return;
    const focalId = creating ? '__draft__' : selected;
    const sizes = new Map(), visible = new Map();
    for (const card of $('cards').children) {
      const expanded = card.classList.contains('expanded');
      card.style.width = `${expanded ? model.DETAIL_WIDTH : model.CARD_WIDTH}px`;
      if (!expanded) card.style.height = `${model.CARD_HEIGHT}px`;
      // Intrinsic dimensions, not zoomed screen rectangles. No viewport input.
      sizes.set(card.dataset.nodeId, { width: card.offsetWidth || (expanded ? model.DETAIL_WIDTH : model.CARD_WIDTH),
        height: card.offsetHeight || card.scrollHeight || (expanded ? 720 : model.CARD_HEIGHT) });
      visible.set(card.dataset.nodeId, graph.nodes.get(card.dataset.nodeId) || { id: focalId });
    }
    const edges = (creating && view === 'focus' ? neighbors().parents.map(id => ({ edge: [id, focalId], kind: 'draft' })) : graph.edges)
      .filter(({ edge: [a, b] }) => visible.has(a) && visible.has(b));
    // Overview/current focus ranks follow the target; a removed selected node
    // follows its base context. Extra revision links remain visible but don't
    // push surviving ranks toward a sink or make the ranking graph cyclic.
    const revision = view === 'focus' && !creating && !currentNode() && state.diff ? state.diff.base : state.snapshot;
    const primary = { ids: new Set(revision.nodes.map(node => node.id)), edges: new Set(revision.edges.map(edge => JSON.stringify(edge))) };
    if (creating && view === 'focus') {
      primary.ids.add(focalId); edges.forEach(item => primary.edges.add(JSON.stringify(item.edge)));
    }
    const key = JSON.stringify([[...sizes].sort(([a], [b]) => a.localeCompare(b)), edges,
      [...primary.ids].sort(), [...primary.edges].sort()]);
    const oldFocus = cameraScene === sceneKey() ? layout?.positions.get(focalId) : undefined;
    if (key !== layoutKey) { layout = model.layoutGraph(visible, edges, sizes, primary); layoutKey = key; }
    $('graph').style.width = `${layout.width}px`; $('graph').style.height = `${layout.height}px`;
    for (const card of $('cards').children) {
      const box = layout.positions.get(card.dataset.nodeId);
      card.style.left = `${box.x}px`; card.style.top = `${box.y}px`;
    }
    drawEdges(model.routeEdges(layout.positions, edges, layout.guides), layout.width, layout.height);
    if (cameraScene !== sceneKey()) {
      cameraScene = sceneKey();
      const { width, height } = camera.dimensions();
      const box = view === 'focus' ? layout.positions.get(focalId)
        : [...visible.values()].find(node => node.type === 'manifesto') && layout.positions.get([...visible.values()].find(node => node.type === 'manifesto').id);
      const initial = box ? view === 'focus'
        ? { x: width / 2 - (box.x + box.width / 2) * 0.9, y: 36 - box.y * 0.9, k: 0.9 }
        : { x: 56 - box.x, y: height / 2 - box.y - box.height / 2, k: 1 } : { x: 24, y: 24, k: 1 };
      camera.set(cameras[cameraScene] || initial);
    } else if (oldFocus && view === 'focus') {
      const box = layout.positions.get(focalId), current = camera.value();
      if (box.x !== oldFocus.x || box.y !== oldFocus.y) camera.set({ ...current,
        x: current.x + (oldFocus.x - box.x) * current.k, y: current.y + (oldFocus.y - box.y) * current.k });
    }
    syncHover();
  }

  function drawEdges(routes, width, height) {
    const svg = $('edges'), ns = 'http://www.w3.org/2000/svg';
    svg.replaceChildren(); svg.setAttribute('width', width); svg.setAttribute('height', height);
    drawnEdges = routes.map(route => {
      const path = document.createElementNS(ns, 'path'), head = document.createElementNS(ns, 'path');
      path.setAttribute('class', `link ${route.kind || 'normal'}`);
      head.setAttribute('class', `arrow-head ${route.kind || 'normal'}`);
      for (const element of [path, head]) {
        element.dataset.parent = route.edge[0]; element.dataset.child = route.edge[1];
      }
      svg.append(path, head);
      return { route, path, head };
    });
    updateEdgeAppearance(camera.value().k);
    updateEdgeHighlights();
  }

  function updateEdgeAppearance(scale) {
    for (const { route, path, head } of drawnEdges) {
      const appearance = model.edgeAppearance(route, scale);
      path.setAttribute('d', appearance.d); head.setAttribute('d', appearance.head);
      path.style.strokeWidth = appearance.strokeWidth;
      const dash = route.kind === 'removed' ? [6, 5] : route.kind === 'draft' ? [3, 4] : undefined;
      if (dash) path.style.strokeDasharray = dash.map(value => value * appearance.dashScale).join(' ');
    }
  }

  function requestLayout() {
    if (layoutFrame) return;
    layoutFrame = requestAnimationFrame(() => { layoutFrame = undefined; applyLayout(); });
  }
  if (typeof ResizeObserver !== 'undefined') {
    const observer = new ResizeObserver(requestLayout);
    observer.observe($('node-details'));
  }
  // A viewport resize changes the camera's available area, never the world layout.

  function populateParents(ids, nodeType) {
    const isRoot = nodeType === 'manifesto';
    formParents = isRoot ? [] : [...ids];
    const canEdit = editable() && !isRoot;
    $('parents-summary').textContent = isRoot ? 'None — the manifesto is the root and cannot have parents.'
      : formParents.length ? `${formParents.length} linked parent${formParents.length === 1 ? '' : 's'}` : 'No parents linked.';
    $('parent-links').replaceChildren();
    for (const id of formParents) {
      const node = graph.nodes.get(id), text = node ? `${title(node)} · ${description(node)} · ${id.slice(0, 8)}` : id;
      const item = document.createElement('li'); item.dataset.parentId = id;
      const label = document.createElement('span'); label.textContent = text; item.append(label);
      if (canEdit) {
        const remove = document.createElement('button'); remove.type = 'button'; remove.textContent = 'Remove';
        remove.setAttribute('aria-label', `Remove parent: ${text}`);
        remove.addEventListener('click', () => {
          if (!parentsEditable()) return;
          populateParents(formParents.filter(parent => parent !== id), formNodeType());
          dirty = true; updateButtons(); saveDraft();
          if (creating) draw(); else requestLayout();
        });
        item.append(remove);
      }
      $('parent-links').append(item);
    }
    $('parent-add-controls').hidden = !canEdit; $('parent-candidate').replaceChildren();
    if (canEdit) {
      const placeholder = document.createElement('option'); placeholder.value = ''; placeholder.textContent = 'Choose a parent to add…';
      $('parent-candidate').append(placeholder);
      for (const node of [...state.snapshot.nodes].sort((a, b) => title(a).localeCompare(title(b)))) {
        if (node.id === selected || formParents.includes(node.id) || node.type === 'implementation'
          || (nodeType === 'implementation' && node.type !== 'requirement')) continue;
        const option = document.createElement('option'); option.value = node.id;
        option.textContent = `${title(node)} · ${description(node)} · ${node.id.slice(0, 8)}`; $('parent-candidate').append(option);
      }
    }
  }

  function loadForm() {
    const node = graph.nodes.get(selected);
    if (!node) { $('editor').hidden = true; $('before-section').hidden = true; return; }
    $('editor').hidden = false; $('title').textContent = title(node);
    $('identity').textContent = `${node.id}\n${description(node)}\n${node.path}`;
    const context = contextFor(node.id);
    $('focus-context').textContent = `Manifesto distance: ${context.distances.get(node.id) ?? '?'} hops · ${context.descendantCount(node.id)} downstream nodes (all depths) · ${snapshotName(node.id)} revision`;
    $('type-label').hidden = true; $('slug-label').hidden = true;
    $('body').value = node.body; $('sources').value = JSON.stringify(node.sources, null, 2);
    $('sources-label').hidden = node.type !== 'implementation'; populateParents(node.parents, node.type);
    const old = state.diff?.base.nodes.find(item => item.id === selected);
    $('before-section').hidden = !old; $('before').textContent = old?.body || '';
  }

  function select(id, force = false) {
    if (!force && pending) return;
    if (!force && id === selected && !creating) {
      if (view === 'overview') { rememberCamera(); view = 'focus'; draw(); saveDraft(); }
      return;
    }
    if (dirty && !force && !confirm('Discard unsaved form changes before opening another node?')) return;
    rememberCamera();
    creating = false; dirty = false; selected = id; formFingerprint = state.snapshot.fingerprint;
    view = graph.nodes.has(id) ? 'focus' : 'overview'; loadForm(); draw(); saveDraft();
  }

  function rememberCamera() {
    camera.stop();
    if (cameraScene) cameras[cameraScene] = camera.value();
  }
  function frameAll() { if (layout) camera.frame({ x: 0, y: 0, width: layout.width, height: layout.height }); }
  $('zoom-out').addEventListener('click', () => camera.scaleBy(0.8));
  $('zoom-in').addEventListener('click', () => camera.scaleBy(1.25));
  $('zoom-reset').addEventListener('click', () => camera.scaleTo(1));
  $('frame-all').addEventListener('click', frameAll);
  $('frame-node').addEventListener('click', () => {
    const box = layout?.positions.get(creating ? '__draft__' : selected);
    if (box) camera.frame(box);
  });
  $('back').addEventListener('click', () => {
    if (pending) return;
    rememberCamera(); view = 'overview'; draw();
    if (dirty || creating) setMessage('Draft retained. Use Resume draft to continue editing.');
    saveDraft();
  });
  $('resume').addEventListener('click', () => {
    rememberCamera(); view = 'focus'; draw(); saveDraft();
  });
  $('color-mode').addEventListener('change', () => {
    colorMode = $('color-mode').value === 'type' ? 'type' : 'distance'; draw(); saveDraft();
  });

  $('new').addEventListener('click', () => {
    if (!state || pending || state.readonly || state.snapshot.format_version !== 2) return;
    if (dirty && !confirm('Discard unsaved form changes?')) return;
    const parent = currentNode();
    rememberCamera(); delete cameras.draft;
    creating = true; dirty = false; selected = undefined; view = 'focus'; formFingerprint = state.snapshot.fingerprint;
    $('editor').hidden = false; $('title').textContent = 'New node';
    $('identity').textContent = 'The CLI will generate its ID and integrity marker.'; $('focus-context').textContent = 'Unsaved new node';
    $('type-label').hidden = false; $('slug-label').hidden = false;
    $('node-type').value = 'requirement'; $('slug').value = ''; $('body').value = ''; $('sources').value = '[]';
    $('sources-label').hidden = true; $('before-section').hidden = true;
    populateParents(parent && parent.type !== 'implementation' ? [parent.id] : [], 'requirement');
    draw(); saveDraft();
  });

  for (const id of elements) $(id).addEventListener('input', () => { dirty = true; updateButtons(); saveDraft(); });
  $('parent-candidate').addEventListener('change', updateButtons);
  $('add-parent').addEventListener('click', () => {
    const id = $('parent-candidate').value;
    if (!parentsEditable() || !id || formParents.includes(id)) return;
    populateParents([...formParents, id], formNodeType()); dirty = true; updateButtons(); saveDraft();
    if (creating) draw(); else requestLayout();
  });
  $('node-type').addEventListener('change', () => {
    const nodeType = $('node-type').value;
    populateParents(formParents.filter(id => nodeType !== 'implementation' || currentNodeById(id)?.type === 'requirement'), nodeType);
    $('sources-label').hidden = nodeType !== 'implementation'; dirty = true; updateButtons(); saveDraft(); draw();
  });
  $('editor').addEventListener('submit', event => {
    event.preventDefault(); if (!editable() || pending) return;
    pending = true; updateButtons();
    send({ type: creating ? 'add' : 'save', id: selected, expect: formFingerprint,
      body: $('body').value, parents: [...formParents], sources: $('sources').value, slug: $('slug').value, nodeType: $('node-type').value });
  });
  for (const action of ['restore', 'retire']) $(action).addEventListener('click', () => {
    if (!editable() || creating || dirty || pending) return;
    pending = true; updateButtons(); send({ type: action, id: selected, expect: formFingerprint });
  });
  $('migrate').addEventListener('click', () => {
    if (!legacyWorkspace() || dirty || creating || pending) return;
    pending = true; updateButtons(); send({ type: 'migrate', expect: state.snapshot.fingerprint });
  });
  $('discard').addEventListener('click', () => {
    dirty = false;
    if (creating) { rememberCamera(); creating = false; selected = undefined; view = 'overview'; draw(); saveDraft(); }
    else { formFingerprint = state.snapshot.fingerprint; loadForm(); draw(); saveDraft(); }
  });
  for (const action of ['refresh', 'compare', 'workspace']) $(action).addEventListener('click', () => send({ type: action }));

  function showSnapshotNotes() {
    setMessage([state.note, ...state.diagnostics.map(d => `${d.code}: ${d.message}`)].filter(Boolean).join('\n'));
    $('schema-notice').hidden = !legacyWorkspace();
    $('schema-notice').textContent = legacyWorkspace() ? 'Legacy v1 graph: migrate to remove approval metadata before editing. Discard any dirty draft first; migration preserves node text and withdrawal history.' : '';
    const sources = state.diff?.source_changes || [];
    $('linked-sources').hidden = !sources.length;
    $('source-summary').textContent = `${sources.length} changed linked source file${sources.length === 1 ? '' : 's'} — potential review context`;
    $('source-files').replaceChildren();
    for (const source of sources) { const item = document.createElement('li'); item.textContent = source.path; $('source-files').append(item); }
  }

  window.addEventListener('message', event => {
    const message = event.data;
    if (message.type === 'error') { pending = false; setMessage(message.message); updateButtons(); return; }
    if (message.type === 'cancelled') { pending = false; updateButtons(); return; }
    if (message.type !== 'snapshot') return;
    state = message; pending = false; graph = model.displayGraph(state);
    targetMetrics = model.metrics(state.snapshot); baseMetrics = state.diff ? model.metrics(state.diff.base) : undefined;
    $('revision').textContent = state.diff ? `${state.diff.base_ref} → ${state.diff.target_ref}${state.readonly ? ' (read-only)' : ''}` : 'Workspace';
    showSnapshotNotes();
    if (message.force) { select(message.selectedId || selected, true); return; }
    if (!restored.used && restored.draft && (restored.dirty || restored.creating)) {
      restored.used = true; dirty = Boolean(restored.dirty); creating = Boolean(restored.creating); formFingerprint = restored.formFingerprint;
      if (!creating) loadForm();
      $('editor').hidden = false; $('body').value = restored.draft.body; $('sources').value = restored.draft.sources;
      $('slug').value = restored.draft.slug; $('node-type').value = restored.draft.nodeType;
      $('type-label').hidden = !creating; $('slug-label').hidden = !creating;
      if (creating) { $('title').textContent = 'New node'; $('identity').textContent = 'Restored unsaved draft'; }
      populateParents(restored.draft.parents, formNodeType());
      $('sources-label').hidden = formNodeType() !== 'implementation';
    } else if (dirty || creating) {
      setMessage('Graph refreshed. Draft retained with its original fingerprint; discard it to load the latest node before saving.');
    } else {
      formFingerprint = state.snapshot.fingerprint; loadForm();
    }
    draw(); saveDraft();
  });
  window.addEventListener('error', event => send({ type: 'client-error', message: event.message }));
  updateButtons(); send({ type: 'ready' });
})();
