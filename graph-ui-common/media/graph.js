/* Project content is data: use textContent/value, never project-supplied HTML. */
(() => {
  const host = window.SpecSpecHost, model = window.SpecSpecGraph;
  const $ = id => document.getElementById(id);
  const restored = host.getState() || {};
  let state, graph = { nodes: new Map(), edges: [] }, targetMetrics, baseMetrics;
  let selected = restored.selected, view = restored.view || (selected || restored.creating ? 'focus' : 'overview');
  let colorMode = model.COLOR_MODES.includes(restored.colorMode) ? restored.colorMode : 'distance';
  let dirty = false, pending = false, creating = false, originalNode, sourceInvalid = false, formParents = [];
  let editSequence = 0, documentVersion;
  let layoutFrame, layout, layoutKey, cameraScene, snapshotReceivedAt;
  let drawnEdges = [], hoveredNode, hoverPoint;
  // Visual experiment only: never put these labels in drafts, host state or messages.
  const previewLabels = new Map();
  const labelCycle = [undefined, ['red', '#e65e66'], ['blue', '#5c9eff'], ['green', '#58ba7a'],
    ['purple', '#aa79df'], ['turquoise', '#35bdbe'], ['yellow', '#dfc24d']];
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
  const send = message => host.postMessage(message);
  const setMessage = message => { $('message').textContent = message; };
  const currentNodeById = id => state?.snapshot.nodes.find(node => node.id === id);
  const currentNode = () => currentNodeById(selected);
  const editable = () => state?.snapshot.valid && (!sourceInvalid || Boolean(state.document)) && state.snapshot.format_version === 5 && !state.readonly &&
    (state.document ? selected === state.document.nodeId && Boolean(currentNode()) : creating || Boolean(currentNode()));
  const orphaned = () => !creating && dirty && !currentNode() && !state?.readonly;
  const draftCard = () => creating || orphaned();
  const description = node => `${node.type}${currentNodeById(node.id) ? '' : ' · deleted'}`;
  const formNodeType = () => creating ? $('node-type').value : originalNode?.type || graph.nodes.get(selected)?.type;
  const parentsEditable = () => editable() && !pending && formNodeType() !== 'manifesto';
  const contextFor = id => currentNodeById(id) ? targetMetrics : baseMetrics || targetMetrics;
  const snapshotName = id => currentNodeById(id) ? 'target' : 'base';
  const distanceFor = id => (colorMode === 'max-distance' ? contextFor(id)?.maxDistances : contextFor(id)?.minDistances)?.get(id);

  function saveDraft() {
    host.setState({ selected, view, colorMode, cameras: { ...cameras }, dirty, creating, originalNode, draft: dirty || creating ? {
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
    $('sync-notice').textContent = state?.document ? 'Displaying the last valid graph. Repair the bound document or other invalid Markdown; native Save can persist invalid text.'
      : 'Displayed graph is out of date. Fix the Markdown files and refresh; graph changes are disabled.';
    $('back').hidden = view !== 'focus';
    $('back').disabled = pending;
    $('frame-node').hidden = view !== 'focus';
    $('resume').hidden = view !== 'overview' || !(dirty || creating);
    $('resume').disabled = pending;
    $('new').disabled = !state?.snapshot.valid || sourceInvalid || state.snapshot.format_version !== 5 || state.readonly || state.provisional || pending || Boolean(state.document);
    $('save').textContent = state?.document ? 'Save file' : 'Save node';
    $('discard').hidden = Boolean(state?.document) && !state.document.recoveredForm;
    $('discard').textContent = state?.document ? 'Discard recovered form' : 'Discard form edits';
    $('delete').title = 'Deletes this node and every descendant, including shared children. Uncommitted nodes are warned about before deletion; HEAD ghosts remain D until committed.';
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
      button.addEventListener('click', () => { setMessage('Resolving source region…'); send({ type: 'source-view', id: selected, reference: JSON.stringify(reference) }); });
      item.append(button); $('source-links').append(item);
    }
  }
  $('sources').addEventListener('input', sourceLinks);
  $('capture-source').addEventListener('click', () => {
    try { if (!Array.isArray(JSON.parse($('sources').value))) throw new Error(); }
    catch { setMessage('Complete the source JSON before appending a captured reference.'); return; }
    send({ type: 'source-capture', id: selected, path: $('source-path').value, ranges: $('source-ranges').value.split(/[,\s]+/).filter(Boolean), mode: $('source-mode').value, staged: $('source-staged').checked });
  });
  $('close-source-preview').addEventListener('click', () => { if ($('source-preview').close) $('source-preview').close(); else $('source-preview').removeAttribute('open'); });

  function changes() {
    const kinds = new Map((state?.diff?.changes || []).map(change => [change.id, change.kind]));
    for (const id of state?.diff?.source_affected || []) if (!kinds.has(id)) kinds.set(id, 'source-changed');
    return kinds;
  }

  function cardIdAt(target) {
    const card = target?.closest?.('.card');
    return card?.parentElement === $('cards') ? card.dataset.nodeId : undefined;
  }

  const labelIdFor = card => card.dataset.nodeId === '__draft__' && orphaned() ? selected : card.dataset.nodeId;
  function applyPreviewLabel(card) {
    const label = labelCycle[previewLabels.get(labelIdFor(card)) || 0];
    if (label) {
      card.dataset.previewLabel = label[0];
      card.style.setProperty('--preview-label-ink', label[1]);
      card.setAttribute('aria-description', `${label[0]} label preview only; not saved. Right-click card to cycle.`);
    } else {
      delete card.dataset.previewLabel;
      card.style.removeProperty('--preview-label-ink');
      card.removeAttribute('aria-description');
    }
  }
  $('viewport').addEventListener('contextmenu', event => {
    // Keep native editing/copy/link/button menus; card chrome is the experiment.
    if (event.defaultPrevented || event.target.closest?.('input, textarea, select, a, [contenteditable]:not([contenteditable="false"]), button:not(.card)')) return;
    const id = cardIdAt(event.target);
    if (id === undefined) return;
    const card = event.target.closest('.card'), key = labelIdFor(card);
    event.preventDefault(); event.stopPropagation();
    const next = ((previewLabels.get(key) || 0) + 1) % labelCycle.length;
    if (next) previewLabels.set(key, next); else previewLabels.delete(key);
    applyPreviewLabel(card);
  });

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
    $('color-mode').value = colorMode;
    $('legend').replaceChildren();
    const entries = colorMode === 'git-revision'
      ? Object.entries(model.REVISION_COLORS).filter(([kind]) => state.diff ? kind !== 'uncompared' : ['uncompared', 'draft'].includes(kind))
        .map(([kind, color]) => [model.REVISION_LABELS[kind], color])
      : colorMode === 'type' ? Object.entries(model.TYPE_COLORS)
      : [['Manifesto · 0 hops', model.TYPE_COLORS.manifesto],
        ...[...new Set([...graph.nodes.values()].filter(node => node.type !== 'manifesto')
          .map(node => distanceFor(node.id)).filter(Number.isInteger))]
          .sort((a, b) => a - b).map(depth => [`${depth} hop${depth === 1 ? '' : 's'}`, model.color('distance', {}, depth)])];
    for (const [label, color] of entries) {
      const item = document.createElement('span'), swatch = document.createElement('i');
      swatch.style.backgroundColor = color; item.append(swatch, document.createTextNode(label));
      $('legend').append(item);
    }
    const explanation = document.createElement('span');
    explanation.className = 'legend-help';
    explanation.textContent = colorMode === 'git-revision'
      ? state.diff ? 'Relative to selected comparison · D means a deleted file; source impact is not M'
        : 'No revision comparison available · neutral fills'
      : colorMode === 'type' ? 'Existing node types · not review stages'
      : `${colorMode === 'max-distance' ? 'Longest' : 'Shortest'} directed path from manifesto · violet → red, repeats every ${model.RAINBOW_COLORS.length} hops · not a confidence score`;
    $('legend').append(explanation);
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
    card.style.setProperty('--node-accent', model.color(colorMode, node, distanceFor(id), revisionKind(kind)));
    card.title = `${id}\n${node.path}\n${snapshotName(id)} revision context`;
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
      badge(`${count} downstream`, 'downstream-badge', 'All reachable descendants at every depth, excluding this child. Shared nodes counted once per child; totals may overlap. Potential impact, not guaranteed invalidation.');
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
      card.style.setProperty('--node-accent', model.color(colorMode, node || { type: $('node-type').value }, distanceFor(selected), draftCard() ? 'draft' : revisionKind(kinds.get(selected))));
      card.append($('node-details')); if (!creating) gitCorner(card, kinds.get(selected)); $('cards').append(card);
    }
    for (const card of $('cards').children) applyPreviewLabel(card);
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
    updateEdgeAppearance(camera.value().k);
    // Redraw creates new cards/pairs even when hovered identity is unchanged.
    updateHoverAppearance();
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
    rememberCamera();
    creating = false; dirty = false; selected = id; originalNode = currentNodeById(id);
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
    colorMode = model.COLOR_MODES.includes($('color-mode').value) ? $('color-mode').value : 'distance'; draw(); saveDraft();
  });

  $('new').addEventListener('click', () => {
    if (!state || sourceInvalid || pending || state.readonly || state.snapshot.format_version !== 5) return;
    if (dirty && !confirm('Discard unsaved form changes?')) return;
    const parent = currentNode();
    rememberCamera(); delete cameras.draft; previewLabels.delete('__draft__');
    creating = true; dirty = false; selected = undefined; view = 'focus'; originalNode = undefined;
    $('editor').hidden = false; $('title').textContent = 'New node';
    $('identity').textContent = 'The CLI will generate its ID.'; $('focus-context').textContent = 'Unsaved new node';
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
    if (message.type === 'source-captured') {
      if (message.id !== selected || !editable()) return;
      try {
        const references = JSON.parse($('sources').value); if (!Array.isArray(references)) throw new Error();
        references.push(message.reference); $('sources').value = JSON.stringify(references, null, 2);
        sourceLinks(); formChanged(); setMessage('Reference appended to the form. Save/stage normally; source staging remains manual.');
      } catch { setMessage('Source JSON changed while capture was pending; complete it before capturing again.'); }
      return;
    }
    if (message.type === 'source-preview') {
      const r = message.resolution;
      $('source-preview-title').textContent = `${r.path} · ${r.target}`;
      $('source-preview-status').textContent = `${r.mode} · ${r.outcome} · ${r.ranges.map(p => p.join('–')).join(', ')}${message.original ? ' · Original anchored content (current mapping is not trustworthy)' : ''}${r.message ? ' · ' + r.message : ''}`;
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
    if (message.type === 'error') { pending = false; setMessage(sourceInvalid ? `Displayed graph is out of date; ${state?.document ? 'the bound document can be repaired' : 'editing is disabled'}.\n${message.message}` : message.message); updateButtons(); return; }
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
      const warning = orphaned() ? 'The edited node was deleted. Draft retained for copying or discarding; saving is disabled.'
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
  updateButtons(); send({ type: 'ready' });
})();
