/* Project content is data: use textContent/value, never project-supplied HTML. */
(() => {
  const host = window.SpecSpecHost, model = window.SpecSpecGraph;
  const $ = id => document.getElementById(id);
  const restored = host.getState() || {};
  let state, graph = { nodes: new Map(), edges: [] }, targetMetrics, baseMetrics;
  let selected = restored.selected, view = restored.view || (selected || restored.creating ? 'focus' : 'overview');
  let colorMode = model.COLOR_MODES.includes(restored.colorMode) ? restored.colorMode : 'distance';
  let dirty = false, pending = false, creating = false, originalNode, sourceInvalid = false, formParents = [];
  let editSequence = 0, documentVersion, sourceSequence = 0, sourceRequest;
  let layoutFrame, layout, layoutKey, cameraScene, snapshotReceivedAt;
  let drawnEdges = [], hoveredNode, hoverPoint;
  const cameraAPI = window.SpecSpecCamera;
  const cameras = Object.fromEntries(Object.entries(restored.cameras || {})
    .map(([key, value]) => [key, cameraAPI.validTransform(value)]).filter(([, value]) => value));
  const sceneKey = () => view === 'overview' ? 'overview' : creating ? 'draft' : `focus:${selected}`;
  const camera = cameraAPI.createCamera($('viewport'), $('graph'), {
    onChange: (value, finished) => {
      if (cameraScene) cameras[cameraScene] = value;
      $('zoom-level').textContent = `${Math.round(value.k * 100)}%`;
      updateCameraAppearance(value.k);
      syncHover();
      if (finished && state) saveDraft();
    }, onFrame: () => frameAll(),
    onRectangleChange: active => { $('frame-area').setAttribute('aria-pressed', String(active)); if (active) clearHover(); },
  });
  $('frame-area').title = `Frame rectangle (${camera.rectangleModifier}-drag)`;
  const elements = ['body', 'sources', 'slug', 'node-type'];
  const title = node => node.body.split(/\r?\n/).find(line => line.startsWith('#'))?.replace(/^#+\s*/, '') || node.body.split(/\r?\n/).find(line => line.trim()) || node.type;
  const send = message => host.postMessage(message);
  const setMessage = message => { $('message').textContent = message; };
  const currentNodeById = id => state?.snapshot.nodes.find(node => node.id === id);
  const currentNode = () => currentNodeById(selected);
  const editable = () => state?.snapshot.valid && (!sourceInvalid || Boolean(state.document)) && state.snapshot.format_version === 6 && !state.readonly &&
    (state.document ? selected === state.document.nodeId && Boolean(currentNode()) : creating || Boolean(currentNode()));
  const orphaned = () => !creating && dirty && !currentNode() && !state?.readonly;
  const draftCard = () => creating || orphaned();
  const description = node => `${node.type}${currentNodeById(node.id) ? '' : ' · deleted'}`;
  const formNodeType = () => creating ? $('node-type').value : originalNode?.type || graph.nodes.get(selected)?.type;
  const parentsEditable = () => editable() && !pending && formNodeType() !== 'manifesto';
  const contextFor = id => currentNodeById(id) ? targetMetrics : baseMetrics || targetMetrics;
  const snapshotName = id => currentNodeById(id) ? 'target' : 'base';
  const colorValueFor = id => model.INFLUENCE_MODES.includes(colorMode)
    ? contextFor(id)?.influenceRatio(id, colorMode)
    : (colorMode === 'max-distance' ? contextFor(id)?.maxDistances : contextFor(id)?.minDistances)?.get(id);

  function saveDraft() {
    host.setState({ selected, view, colorMode, cameras: { ...cameras }, ...annotations.presentation(), dirty, creating, originalNode, draft: dirty || creating ? {
      body: $('body').value, sources: $('sources').value, slug: $('slug').value,
      nodeType: $('node-type').value, parents: [...formParents],
    } : undefined });
  }

  function documentEdit() {
    if (!state?.document || creating || !editable()) return;
    send({ type: 'edit', id: selected, body: $('body').value, parents: [...formParents], sources: $('sources').value,
      documentVersion, editSequence: ++editSequence });
  }
  function formChanged() { dirty = true; updateButtons(); saveDraft(); documentEdit(); }

  function updateButtons() {
    $('sync-notice').hidden = !sourceInvalid;
    $('sync-notice').textContent = state?.document ? 'Last valid graph · Repair Markdown; native Save retains document text.'
      : 'Last valid graph · Repair Markdown and refresh to resume editing.';
    $('back').hidden = view !== 'focus';
    $('back').disabled = pending;
    $('frame-node').hidden = view !== 'focus';
    $('resume').hidden = view !== 'overview' || !(dirty || creating);
    $('resume').disabled = pending;
    $('new').disabled = !state?.snapshot.valid || sourceInvalid || state.snapshot.format_version !== 6 || state.readonly || state.provisional || pending || Boolean(state.document);
    $('save').textContent = state?.document ? 'Save file' : 'Save node';
    $('discard').hidden = Boolean(state?.document) && !state.document.recoveredForm;
    $('discard').textContent = state?.document ? 'Discard recovered form' : 'Discard form edits';
    $('delete').title = 'Delete this node and all descendants';
    $('save').disabled = !editable() || pending || Boolean(state?.provisional && !state.document);
    $('delete').disabled = !editable() || state?.provisional || creating || dirty || Boolean(state?.document?.dirty) || pending || currentNode()?.type === 'manifesto';
    for (const id of elements) $(id).disabled = !editable() || pending;
    for (const id of ['body', 'sources']) {
      // Keep retained text selectable/copyable when files are invalid or deleted.
      $(id).readOnly = !editable() || orphaned();
      $(id).disabled = pending;
    }
    $('parent-candidate').disabled = !parentsEditable();
    $('add-parent').disabled = !parentsEditable() || !$('parent-candidate').value;
    for (const button of $('parent-links').querySelectorAll('button')) button.disabled = !parentsEditable();
    $('source-tools').hidden = formNodeType() !== 'implementation';
    $('capture-source').disabled = !editable() || state?.provisional || pending || creating || !currentNode();
    for (const id of ['source-path', 'source-ranges', 'source-mode', 'source-staged']) $(id).disabled = $('capture-source').disabled;
  }

  const sourceContext = () => JSON.stringify([selected, view, state?.readonly,
    state?.diff?.base_commit, state?.diff?.target_commit, graph.nodes.get(selected), $('sources').value]);
  function cancelSourcePreview() {
    sourceRequest = undefined;
    if ($('source-preview').close) $('source-preview').close(); else $('source-preview').removeAttribute('open');
  }
  function sourceLinks() {
    $('source-links').replaceChildren();
    let references;
    try { references = JSON.parse($('sources').value); } catch { return; }
    if (!Array.isArray(references)) return;
    for (const reference of references) {
      if (!reference || typeof reference.path !== 'string') continue;
      const item = document.createElement('li'), button = document.createElement('button'); button.type = 'button';
      button.textContent = reference.blob ? `${reference.path} · anchor ${reference.ranges?.map(r => r.join('–')).join(', ')} · ${reference.mode}` : `${reference.path} · whole file`;
      button.title = 'Resolve in the selected revision or working files and open literal source preview';
      button.addEventListener('click', () => {
        sourceRequest = { id: ++sourceSequence, context: sourceContext() };
        setMessage('Resolving source region…');
        send({ type: 'source-view', requestId: sourceRequest.id, renderToken: state.renderToken, id: selected, reference: JSON.stringify(reference) });
      });
      item.append(button); $('source-links').append(item);
    }
  }
  $('sources').addEventListener('input', sourceLinks);
  $('capture-source').addEventListener('click', () => {
    try { if (!Array.isArray(JSON.parse($('sources').value))) throw new Error(); }
    catch { setMessage('Complete the source JSON before appending a captured reference.'); return; }
    send({ type: 'source-capture', id: selected, path: $('source-path').value, ranges: $('source-ranges').value.split(/[,\s]+/).filter(Boolean), mode: $('source-mode').value, staged: $('source-staged').checked });
  });
  $('close-source-preview').addEventListener('click', cancelSourcePreview);

  function changes() {
    const kinds = new Map((state?.diff?.changes || []).map(change => [change.id, change.kind]));
    for (const id of state?.diff?.source_affected || []) if (!kinds.has(id)) kinds.set(id, 'source-changed');
    return kinds;
  }

  function cardIdAt(target) {
    const card = target?.closest?.('.card');
    return card?.parentElement === $('cards') ? card.dataset.nodeId : undefined;
  }

  const annotations = window.SpecSpecAnnotations.create({ restored, snapshot: () => state, cards: () => $('cards'),
    save: saveDraft, send, frame: frameAnnotations });

  function updateHoverAppearance() {
    const plain = [], highlighted = [], neighbors = new Set([hoveredNode]);
    const hovering = hoveredNode !== undefined;
    for (const pair of drawnEdges) {
      const incident = hovering && pair.route.edge.includes(hoveredNode);
      if (incident) pair.route.edge.forEach(id => neighbors.add(id));
      for (const element of [pair.path, pair.head]) {
        element.classList.toggle('incident-highlight', incident);
        element.classList.toggle('hover-darkened', hovering && !incident);
      }
      (incident ? highlighted : plain).push(pair);
    }
    for (const card of $('cards').children) {
      card.classList.toggle('node-hovered', card.dataset.nodeId === hoveredNode);
      card.classList.toggle('hover-darkened', hovering && !neighbors.has(card.dataset.nodeId));
    }
    // Existing pairs only: highlight crossings without touching geometry/forms.
    const fragment = document.createDocumentFragment();
    for (const { path, head } of [...plain, ...highlighted]) fragment.append(path, head);
    $('edges').append(fragment);
  }

  function setHoveredNode(id) {
    if (id === hoveredNode) return;
    hoveredNode = id; updateHoverAppearance();
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
    if (event.pointerType === 'touch' || $('viewport').classList.contains('rectangle-ready')) { clearHover(); return; }
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
    if (draftCard()) return { parents: formParents.filter(id => graph.nodes.has(id)), children: [] };
    const parents = new Set(), children = new Set();
    for (const { edge: [a, b] } of graph.edges) {
      if (b === selected && graph.nodes.has(a)) parents.add(a);
      if (a === selected && graph.nodes.has(b)) children.add(b);
    }
    const sorted = ids => [...ids].sort((a, b) => title(graph.nodes.get(a)).localeCompare(title(graph.nodes.get(b))) || a.localeCompare(b));
    return { parents: sorted(parents), children: sorted(children) };
  }

  const revisionKind = kind => kind || (state?.diff ? 'unchanged' : 'uncompared');

  function drawLegend() {
    const absoluteInfluence = colorMode.endsWith('absolute-influence');
    $('color-mode').value = colorMode;
    $('legend').replaceChildren();
    const entries = colorMode === 'git-revision'
      ? Object.entries(model.REVISION_COLORS).filter(([kind]) => state.diff ? kind !== 'uncompared' : ['uncompared', 'draft'].includes(kind))
        .map(([kind, color]) => [model.REVISION_LABELS[kind], color])
      : colorMode === 'type' ? Object.entries(model.TYPE_COLORS)
      : model.INFLUENCE_MODES.includes(colorMode) ? [['Manifesto', model.TYPE_COLORS.manifesto]]
      : [['Manifesto · 0 hops', model.TYPE_COLORS.manifesto],
        ...[...new Set([...graph.nodes.values()].filter(node => node.type !== 'manifesto')
          .map(node => colorValueFor(node.id)).filter(Number.isInteger))]
          .sort((a, b) => a - b).map(depth => [`${depth} hop${depth === 1 ? '' : 's'}`, model.color('distance', {}, depth)])];
    for (const [label, color] of entries) {
      const item = document.createElement('span'), swatch = document.createElement('i');
      swatch.style.backgroundColor = color; item.append(swatch, document.createTextNode(label));
      $('legend').append(item);
    }
    if (model.INFLUENCE_MODES.includes(colorMode)) {
      const scale = document.createElement('span'), gradient = document.createElement('i');
      gradient.className = 'influence-gradient';
      gradient.style.backgroundImage = `linear-gradient(to right in srgb, ${[...model.INFLUENCE_COLORS].reverse().join(', ')})`;
      gradient.setAttribute('role', 'img');
      gradient.setAttribute('aria-label', 'Continuous influence: red highest, yellow intermediate, green lowest');
      scale.append(document.createTextNode(absoluteInfluence ? 'Maximum' : 'Group maximum'),
        gradient, document.createTextNode(absoluteInfluence ? '0 descendants' : 'Group minimum'));
      $('legend').append(scale);
    }
  }

  function gitCorner(card, kind) {
    const entry = { added: ['A', 'Added'], changed: ['M', 'Modified'], removed: ['D', 'Deleted'], renamed: ['R', 'Renamed'] }[kind];
    if (!entry) return; // Linked-source impact is not a node modification.
    const marker = document.createElement('span'); marker.className = `git-corner ${kind}`;
    marker.textContent = entry[0]; marker.title = `${entry[1]} relative to the comparison base`;
    marker.setAttribute('aria-label', marker.title); card.append(marker);
  }

  function compactCard(id, kind, related) {
    const node = graph.nodes.get(id), context = contextFor(id);
    const card = document.createElement('button');
    card.type = 'button'; card.className = `card ${node.type} ${kind || ''}`;
    card.dataset.nodeId = id;
    card.dataset.relation = related || '';
    card.dataset.minDistance = context?.minDistances.get(id) ?? 'unknown';
    card.dataset.maxDistance = context?.maxDistances.get(id) ?? 'unknown';
    card.classList.toggle('revision-colored', colorMode === 'git-revision');
    card.style.setProperty('--node-accent', model.color(colorMode, node, colorValueFor(id), revisionKind(kind)));
    card.title = `${id}\n${node.path}\n${snapshotName(id)} revision context`;
    if (model.INFLUENCE_MODES.includes(colorMode)) card.title += `\nInfluence: ${context?.descendantCount(id) ?? 'unknown'} unique descendants`;
    const heading = document.createElement('strong'); heading.textContent = title(node);
    const metadata = document.createElement('small'); metadata.textContent = `${description(node)} · ${id}`;
    const badges = document.createElement('span'); badges.className = 'badges';
    function badge(text, className, tooltip) {
      const item = document.createElement('span'); item.className = `badge ${className}`; item.textContent = text;
      if (tooltip) item.title = tooltip;
      badges.append(item);
    }
    if (related === 'child' || related === 'both') {
      const count = context?.descendantCount(id) ?? 0;
      card.dataset.downstream = count;
      badge(`${count} downstream`, 'downstream-badge', 'Unique descendants at all depths · Potential impact');
    }
    if (kind) badge(kind.replace(/-/g, ' '), `git-badge ${kind}`);
    card.append(heading, metadata, badges); gitCorner(card, kind);
    card.addEventListener('click', () => select(id));
    return card;
  }

  function draw() {
    if (!state) return;
    if (!draftCard() && !graph.nodes.has(selected)) view = 'overview';
    // Move the SAME form DOM, preserving values, handlers and draft baseline.
    const activeInput = document.activeElement;
    const caret = activeInput?.tagName === 'TEXTAREA' ? [activeInput.selectionStart, activeInput.selectionEnd, activeInput.selectionDirection] : undefined;
    $('detail-parking').append($('node-details'));
    $('cards').replaceChildren();
    const kinds = changes(), related = neighbors();
    const ids = view === 'overview' ? [...graph.nodes.keys()] : draftCard()
      ? related.parents : model.focusIds(graph.nodes, graph.edges, selected);
    const focalId = draftCard() ? '__draft__' : selected;
    for (const id of ids) {
      if (view === 'focus' && id === selected) continue;
      const role = view === 'focus' ? related.parents.includes(id)
        ? related.children.includes(id) ? 'both' : 'parent' : 'child' : '';
      $('cards').append(compactCard(id, kinds.get(id), role));
    }
    if (view === 'focus') {
      const card = document.createElement('article'), node = originalNode && orphaned() ? originalNode : graph.nodes.get(selected);
      card.className = `card expanded ${creating ? $('node-type').value : node?.type || 'requirement'} ${kinds.get(selected) || ''}`;
      card.dataset.nodeId = focalId;
      card.classList.toggle('revision-colored', colorMode === 'git-revision');
      card.style.setProperty('--node-accent', model.color(colorMode, node || { type: $('node-type').value },
        draftCard() && model.INFLUENCE_MODES.includes(colorMode) ? undefined : colorValueFor(selected), draftCard() ? 'draft' : revisionKind(kinds.get(selected))));
      card.append($('node-details')); if (!creating) gitCorner(card, kinds.get(selected)); $('cards').append(card);
    }
    annotations.changed();
    drawLegend(); updateButtons(); applyLayout();
    if ($('cards').contains(activeInput) && !activeInput.disabled) {
      activeInput.focus({ preventScroll: true });
      if (caret) activeInput.setSelectionRange(...caret);
    }
    send({ type: 'rendered', renderToken: state.renderToken, view, selectedId: selected, creating: draftCard() && view === 'focus',
      visibleIds: ids, draftParents: draftCard() && view === 'focus' ? [...related.parents] : undefined,
      nodeCount: $('cards').children.length, clientRenderMs: snapshotReceivedAt === undefined ? undefined : performance.now() - snapshotReceivedAt });
  }

  function applyLayout() {
    if (!state || !$('cards').children.length) return;
    const focalId = draftCard() ? '__draft__' : selected;
    const sizes = new Map(), visible = new Map();
    for (const card of $('cards').children) {
      const expanded = card.classList.contains('expanded');
      const circle = card.classList.contains('manifesto');
      let width = expanded ? model.DETAIL_WIDTH : model.CARD_WIDTH;
      let height = circle ? model.CARD_WIDTH : model.CARD_HEIGHT;
      if (circle && expanded) {
        card.style.setProperty('--detail-content-width', `${model.DETAIL_CONTENT_WIDTH}px`);
        const settings = card.querySelector('.node-settings');
        // Fixed native content width, measured intrinsic height; never viewport/zoom.
        // The fallback is for non-layout DOM test environments only.
        width = height = model.manifestoDiameter(model.DETAIL_CONTENT_WIDTH, Math.max(settings.offsetHeight, settings.scrollHeight) || 720);
      }
      card.style.width = `${width}px`;
      card.style.height = !expanded || circle ? `${height}px` : '';
      // Intrinsic dimensions, not zoomed screen rectangles. No viewport input.
      sizes.set(card.dataset.nodeId, { width: card.offsetWidth || width,
        height: card.offsetHeight || card.scrollHeight || (expanded ? (circle ? height : 720) : height),
        shape: circle ? 'circle' : undefined, radius: circle ? undefined : parseFloat(getComputedStyle(card).borderTopLeftRadius) || 0 });
      visible.set(card.dataset.nodeId, graph.nodes.get(card.dataset.nodeId) || { id: focalId });
    }
    const edges = (draftCard() && view === 'focus' ? neighbors().parents.map(id => ({ edge: [id, focalId], kind: 'draft' })) : graph.edges)
      .filter(({ edge: [a, b] }) => visible.has(a) && visible.has(b));
    // Overview/current focus ranks follow the target; a removed selected node
    // follows its base context. Extra revision links remain visible but don't
    // push surviving ranks toward a sink or make the ranking graph cyclic.
    const revision = view === 'focus' && !creating && !currentNode() && state.diff ? state.diff.base : state.snapshot;
    const primary = { ids: new Set(revision.nodes.map(node => node.id)), edges: new Set(revision.edges.map(edge => JSON.stringify(edge))) };
    if (draftCard() && view === 'focus') {
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
    updateCameraAppearance(camera.value().k);
    // Redraw creates new cards/pairs even when hovered identity is unchanged.
    updateHoverAppearance();
  }

  function updateCameraAppearance(scale) {
    const cards = $('cards'), ringWidth = model.annotationRingWidth(scale);
    cards.style.setProperty('--node-fill-strength', `${model.nodeFillStrength(scale) * 100}%`);
    cards.style.setProperty('--annotation-ring-width', `${ringWidth}px`);
    cards.style.setProperty('--annotation-ring-offset', `${-ringWidth}px`);
    $('edges').style.setProperty('--normal-edge-strength', `${model.neutralEdgeStrength(scale) * 100}%`);
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
    $('parents-summary').textContent = isRoot ? 'Manifesto root'
      : formParents.length ? `${formParents.length} linked parent${formParents.length === 1 ? '' : 's'}` : 'Choose a parent';
    $('parent-links').replaceChildren();
    for (const id of formParents) {
      const node = graph.nodes.get(id), text = node ? `${title(node)} · ${description(node)} · ${id}` : id;
      const item = document.createElement('li'); item.dataset.parentId = id;
      const label = document.createElement('span'); label.textContent = text; item.append(label);
      if (canEdit) {
        const remove = document.createElement('button'); remove.type = 'button'; remove.textContent = 'Remove';
        remove.setAttribute('aria-label', `Remove parent: ${text}`);
        remove.addEventListener('click', () => {
          if (!parentsEditable()) return;
          populateParents(formParents.filter(parent => parent !== id), formNodeType());
          formChanged();
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
        option.textContent = `${title(node)} · ${description(node)} · ${node.id}`; $('parent-candidate').append(option);
      }
    }
  }

  function loadForm() {
    const node = graph.nodes.get(selected);
    if (!node) { $('editor').hidden = true; $('before-section').hidden = true; return; }
    $('editor').hidden = false; $('title').textContent = title(node);
    $('identity').textContent = `${node.id}\n${description(node)}\n${node.path}`;
    const context = contextFor(node.id);
    $('focus-context').textContent = `${context.descendantCount(node.id)} downstream nodes (all depths) · ${snapshotName(node.id)} revision`;
    $('type-label').hidden = true; $('slug-label').hidden = true;
    if ($('body').value !== node.body) $('body').value = node.body;
    let sameSources = false;
    try { sameSources = JSON.stringify(JSON.parse($('sources').value)) === JSON.stringify(node.sources); } catch { /* Intermediate JSON typing. */ }
    if (!sameSources) $('sources').value = JSON.stringify(node.sources, null, 2);
    $('sources-label').hidden = node.type !== 'implementation'; sourceLinks(); populateParents(node.parents, node.type);
    const old = state.diff?.base.nodes.find(item => item.id === selected);
    $('before-section').hidden = !old; $('before').textContent = old?.body || '';
  }

  function select(id, force = false) {
    if (!force && state?.document && id !== state.document.nodeId && currentNodeById(id) && !state.readonly) {
      send({ type: 'open-node', id }); return;
    }
    if (!force && pending) return;
    if (!force && id === selected && !creating) {
      if (view === 'overview') { rememberCamera(); view = 'focus'; draw(); saveDraft(); }
      return;
    }
    if (dirty && !force && !confirm('Discard unsaved form changes before opening another node?')) return;
    cancelSourcePreview(); rememberCamera();
    creating = false; dirty = false; selected = id; originalNode = currentNodeById(id);
    view = graph.nodes.has(id) ? 'focus' : 'overview'; loadForm(); draw(); saveDraft();
  }

  function rememberCamera() {
    camera.stop();
    if (cameraScene) cameras[cameraScene] = camera.value();
  }
  function frameAll() { if (layout) camera.frame({ x: 0, y: 0, width: layout.width, height: layout.height }); }
  function frameAnnotations(ids) {
    if (!state || pending || !ids.length) return;
    cancelSourcePreview(); rememberCamera(); view = 'overview'; draw();
    const boxes = ids.map(id => layout?.positions.get(id)).filter(Boolean);
    if (boxes.length) {
      const x = Math.min(...boxes.map(box => box.x)), y = Math.min(...boxes.map(box => box.y));
      const bounds = { x, y, width: Math.max(...boxes.map(box => box.x + box.width)) - x,
        height: Math.max(...boxes.map(box => box.y + box.height)) - y };
      camera.frame(bounds);
    }
    saveDraft();
  }
  $('zoom-out').addEventListener('click', () => camera.scaleBy(0.8));
  $('zoom-in').addEventListener('click', () => camera.scaleBy(1.25));
  $('zoom-reset').addEventListener('click', () => camera.scaleTo(1));
  $('frame-all').addEventListener('click', frameAll);
  $('frame-area').addEventListener('click', () => camera.toggleRectangle());
  $('frame-node').addEventListener('click', () => {
    const box = layout?.positions.get(draftCard() ? '__draft__' : selected);
    if (box) camera.frame(box);
  });
  $('back').addEventListener('click', () => {
    if (pending) return;
    cancelSourcePreview(); rememberCamera(); view = 'overview'; draw();
    if (dirty || creating) setMessage('Draft retained. Use Resume draft to continue editing.');
    saveDraft();
  });
  $('resume').addEventListener('click', () => {
    rememberCamera(); view = 'focus'; draw(); saveDraft();
  });
  $('color-mode').addEventListener('change', () => {
    colorMode = model.COLOR_MODES.includes($('color-mode').value) ? $('color-mode').value : 'distance'; draw(); saveDraft();
  });

  $('new').addEventListener('click', () => {
    if (!state || sourceInvalid || pending || state.readonly || state.snapshot.format_version !== 6) return;
    if (dirty && !confirm('Discard unsaved form changes?')) return;
    const parent = currentNode();
    cancelSourcePreview(); rememberCamera(); delete cameras.draft;
    creating = true; dirty = false; selected = undefined; view = 'focus'; originalNode = undefined;
    $('editor').hidden = false; $('title').textContent = 'New node';
    $('identity').textContent = 'The CLI will generate its ID.'; $('focus-context').textContent = 'New node draft';
    $('type-label').hidden = false; $('slug-label').hidden = false;
    $('node-type').value = 'requirement'; $('slug').value = ''; $('body').value = ''; $('sources').value = '[]';
    $('sources-label').hidden = true; $('before-section').hidden = true;
    populateParents(parent && parent.type !== 'implementation' ? [parent.id] : [], 'requirement');
    draw(); saveDraft();
  });

  for (const id of elements) $(id).addEventListener('input', formChanged);
  $('parent-candidate').addEventListener('change', updateButtons);
  $('add-parent').addEventListener('click', () => {
    const id = $('parent-candidate').value;
    if (!parentsEditable() || !id || formParents.includes(id)) return;
    populateParents([...formParents, id], formNodeType()); formChanged();
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
    send({ type: creating ? 'add' : 'save', id: selected, originalNode,
      body: $('body').value, parents: [...formParents], sources: $('sources').value, slug: $('slug').value, nodeType: $('node-type').value,
      ...(state.document ? { documentVersion, editSequence } : {}) });
  });
  $('delete').addEventListener('click', () => {
    if ($('delete').disabled) return;
    pending = true; updateButtons(); send({ type: 'delete', id: selected });
  });
  $('discard').addEventListener('click', () => {
    if (state?.document) send({ type: 'discard-form' });
    dirty = false;
    if (creating) { rememberCamera(); creating = false; selected = undefined; view = 'overview'; draw(); saveDraft(); }
    else { originalNode = currentNode(); loadForm(); draw(); saveDraft(); }
  });
  for (const action of ['refresh', 'compare', 'workspace']) $(action).addEventListener('click', () => send({ type: action }));
  $('project').addEventListener('click', () => send({ type: 'select-project' }));

  function showSnapshotNotes() {
    setMessage([state.note, ...state.diagnostics.map(d => `${d.code}: ${d.message}`)].filter(Boolean).join('\n'));
    const sources = state.diff?.source_changes || [];
    $('linked-sources').hidden = !sources.length;
    $('source-summary').textContent = `${sources.length} changed linked source file${sources.length === 1 ? '' : 's'} — potential review context`;
    $('source-files').replaceChildren();
    for (const source of sources) { const item = document.createElement('li'); item.textContent = source.path; $('source-files').append(item); }
  }

  host.onMessage(message => {
    if (message.type === 'annotations') { annotations.receive(message.shots); return; }
    if (message.type === 'annotations-error') { annotations.error(message.message); return; }
    if (message.type === 'annotation-applied') { sourceInvalid = Boolean(message.invalid); updateButtons(); annotations.applied(message.shot, message.warning); return; }
    if (message.type === 'annotation-context') { annotations.context(); return; }
    if (message.type === 'annotation-created') { annotations.created(); return; }
    if (message.type === 'annotation-create-error') { annotations.created(message.message); return; }
    if (message.type === 'source-captured') {
      if (message.id !== selected || !editable()) return;
      try {
        const references = JSON.parse($('sources').value); if (!Array.isArray(references)) throw new Error();
        references.push(message.reference); $('sources').value = JSON.stringify(references, null, 2);
        sourceLinks(); formChanged(); setMessage('Source reference added · Save the form to keep it.');
      } catch { setMessage('Source JSON changed while capture was pending; complete it before capturing again.'); }
      return;
    }
    if (message.type === 'source-error' || message.type === 'source-preview') {
      if (!sourceRequest || message.requestId !== sourceRequest.id || sourceRequest.context !== sourceContext()) return;
      sourceRequest = undefined;
      if (message.type === 'source-error') { setMessage(message.message); return; }
      setMessage('');
      const r = message.resolution;
      $('source-preview-title').textContent = `${r.path} · ${r.target}`;
      $('source-preview-status').textContent = `${r.mode} · ${r.outcome} · ${r.ranges.map(p => p.join('–')).join(', ')}${message.original ? ' · Original anchored content · Mapping needs review' : ''}${r.message ? ' · ' + r.message : ''}`;
      $('source-preview-code').textContent = message.chunks.map(c => c.lines.map((line, i) => `${i + c.start >= c.selected[0] && i + c.start <= c.selected[1] ? '>' : ' '} ${i + c.start}: ${line}`).join('\n')).join('\n\n…\n\n');
      if ($('source-preview').showModal) $('source-preview').showModal(); else $('source-preview').setAttribute('open', '');
      return;
    }
    if (message.type === 'document-status') {
      const newerSnapshot = state?.document && state.document.version > message.document.version;
      if (!newerSnapshot) { documentVersion = message.document.version; if (state) state.document = message.document; }
      if (message.editSequence === editSequence) {
        dirty = false;
        if (state?.document) delete state.document.recoveredForm;
        if (newerSnapshot) { originalNode = currentNode(); loadForm(); draw(); }
        saveDraft();
      }
      updateButtons(); return;
    }
    if (message.type === 'notice' || message.type === 'sync-warning') { setMessage(message.message); return; }
    if (message.type === 'sync-error') { sourceInvalid = true; pending = false; setMessage(message.message); updateButtons(); return; }
    if (message.type === 'error') { pending = false; setMessage(sourceInvalid ? `Last valid graph · Repair ${state?.document ? 'the bound document' : 'Markdown and refresh'}.\n${message.message}` : message.message); updateButtons(); return; }
    if (message.type === 'cancelled') { pending = false; updateButtons(); return; }
    if (message.type !== 'snapshot') return;
    snapshotReceivedAt = performance.now();
    state = message; sourceInvalid = false; pending = false; graph = model.displayGraph(state);
    if (state.document) documentVersion = state.document.version;
    if (!restored.used && state.document?.recoveredForm && !restored.draft) {
      const form = state.document.recoveredForm;
      restored.draft = { body: form.body, parents: form.parents, sources: form.sources, slug: '', nodeType: graph.nodes.get(state.document.nodeId)?.type };
      restored.dirty = true; selected = state.document.nodeId; view = 'focus';
    }
    if (!restored.used && message.selectedId && !restored.draft) { selected = message.selectedId; view = 'focus'; }
    targetMetrics = model.metrics(state.snapshot); baseMetrics = state.diff ? model.metrics(state.diff.base) : undefined;
    $('revision').textContent = state.diff ? `${state.diff.base_ref} → ${state.diff.target_ref}${state.readonly ? ' (read-only)' : ''}` : state.provisional ? 'HEAD → workspace (comparison loading)' : 'Workspace';
    showSnapshotNotes();
    if (message.force) { select(message.selectedId || selected, true); return; }
    if (!restored.used && restored.draft && (restored.dirty || restored.creating)) {
      restored.used = true; dirty = Boolean(restored.dirty); creating = Boolean(restored.creating); originalNode = restored.originalNode;
      if (state.document) documentVersion = undefined; // Restored out-of-band drafts need conflict confirmation.
      if (!creating) loadForm();
      $('editor').hidden = false; $('body').value = restored.draft.body; $('sources').value = restored.draft.sources;
      $('slug').value = restored.draft.slug; $('node-type').value = restored.draft.nodeType;
      $('type-label').hidden = !creating; $('slug-label').hidden = !creating;
      if (creating) { $('title').textContent = 'New node'; $('identity').textContent = 'Restored unsaved draft'; }
      populateParents(restored.draft.parents, formNodeType());
      $('sources-label').hidden = formNodeType() !== 'implementation';
    } else if (!dirty && !creating) {
      if (selected && !graph.nodes.has(selected)) { rememberCamera(); selected = undefined; view = 'overview'; }
      originalNode = currentNode(); loadForm();
    }
    if (dirty || creating) {
      const warning = orphaned() ? 'Deleted node draft · Available for copying or discard.'
        : !creating && !model.sameNode(originalNode, currentNode()) ? 'This node changed outside your draft. Draft retained; saving will ask before overwriting current contents.'
          : 'Graph refreshed. Unsaved draft retained.';
      setMessage([state.note, ...state.diagnostics.map(d => `${d.code}: ${d.message}`), warning].filter(Boolean).join('\n'));
      if (orphaned()) { $('editor').hidden = false; $('title').textContent = 'Deleted node draft'; $('identity').textContent = selected || ''; }
    }
    draw(); saveDraft();
  });
  window.addEventListener('keydown', event => {
    if (state?.document && (event.ctrlKey || event.metaKey) && ['z', 'y'].includes(event.key.toLowerCase())) {
      event.preventDefault(); send({ type: event.key.toLowerCase() === 'y' || event.shiftKey ? 'redo' : 'undo' });
    }
  });
  window.addEventListener('error', event => send({ type: 'client-error', message: event.message }));
  updateButtons(); send({ type: 'ready', ...(typeof restored.annotationActive === 'string' ? { spotlight: restored.annotationActive } : {}) });
})();
