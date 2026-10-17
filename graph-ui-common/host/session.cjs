/* No editor/Electron imports: every host uses the same graph operations. */
const { isDeepStrictEqual } = require('node:util');
const { ProjectReads, SupersededReadError } = require('./reads.cjs');

function pollInterval(value) {
  if (!Number.isSafeInteger(value) || value < 0 || value > 2_147_483_647) throw new Error('Polling interval must be an integer from 0 to 2147483647 ms (0 disables polling).');
  return value;
}

class GraphSession {
  constructor(host) {
    this.host = host; this.base = 'HEAD'; this.queue = Promise.resolve();
    this.reads = host.readGraph ? undefined : new ProjectReads({ cli: (args, input) => this.cli(args, input) });
    this.renderSequence = 0; this.lastRendered = 0; this.listeners = new Set();
    this.ready = new Promise(resolve => { this.resolveReady = resolve; });
  }
  log(error) { this.host.log?.(error instanceof Error ? error.stack || error.message : String(error)); }
  async post(value) { if (!this.disposed) await this.host.post(value); }
  run(operation) {
    const result = this.queue.then(() => { if (this.disposed) throw new Error('Graph panel is closed.'); return operation(); });
    this.queue = result.catch(() => {}); return result;
  }
  enqueue(operation) {
    void this.run(operation).catch(async error => { this.log(error); await this.post({ type: 'error', message: error.message }); });
  }
  receive(value) {
    if (!value || typeof value !== 'object' || Array.isArray(value)) return;
    if (value.type === 'ready') { this.annotationInitial = true; this.restoredSpotlight = typeof value.spotlight === 'string' ? value.spotlight : undefined; this.resolveReady(); return; }
    if (value.type === 'client-error' && typeof value.message === 'string') {
      this.renderError = new Error(`Graph renderer failed: ${value.message}`); this.log(this.renderError);
      this.listeners.forEach(f => f()); return;
    }
    if (value.type === 'rendered') {
      if (value.renderToken !== this.renderSequence) return;
      if (!this.renderState || !this.host.renderMatches(this.renderState, value)) {
        this.renderError = new Error(`Graph rendering is incomplete or inconsistent; expected ${this.expectedCount} known nodes in the overview or a complete selected neighborhood.`);
      } else {
        if (this.lastRendered !== value.renderToken && Number.isFinite(value.clientRenderMs) && value.clientRenderMs >= 0)
          this.host.trace?.('client-render', value.clientRenderMs, value.nodeCount);
        this.lastRendered = value.renderToken;
      }
      this.listeners.forEach(f => f()); return;
    }
    if (value.type === 'edit' && this.host.document) {
      this.nextDocumentEdit = value;
      if (!this.documentEdits) this.documentEdits = this.drainDocumentEdits().finally(() => { this.documentEdits = undefined; });
      return;
    }
    if (value.type === 'source-view') {
      void this.sourcePreview(value).catch(async error => {
        this.log(error); await this.post({ type: 'source-error', requestId: value.requestId, message: error.message });
      });
      return;
    }
    this.enqueue(() => this.handle(value));
  }
  async open() {
    try {
      const start = Date.now();
      await this.waitReady(); this.host.trace?.('ready', Date.now() - start);
      await this.run(async () => {
        if (this.restoredSpotlight) {
          await this.refreshAnnotations();
          const shot = this.annotationShots?.find(s => s.id === this.restoredSpotlight);
          if (shot) this.spotlightContext(shot);
          this.restoredSpotlight = undefined;
        }
        if (!this.hasOpened && !this.target && (this.host.initialGraph || this.reads)) {
          let initial;
          try { initial = await (this.host.initialGraph ? this.host.initialGraph() : this.reads.initial()); } catch (error) { this.log(error); }
          if (initial?.snapshot?.valid) {
            await this.display(initial, false, undefined, false, true);
            this.host.trace?.('first-working-render', Date.now() - start, initial.snapshot.nodes.length);
          }
        }
        const restoredShot = this.activeSpotlight;
        try { await this.refresh(); }
        catch (error) {
          if (!restoredShot) throw error;
          this.base = 'HEAD'; this.target = undefined; this.activeSpotlight = undefined;
          await this.refresh();
          await this.post({ type: 'annotation-applied', shot: restoredShot, warning: `Spotlight comparison unavailable; using workspace / HEAD. ${error.message}` });
        }
      });
      this.host.trace?.('complete-comparison-render', Date.now() - start, this.snapshot?.nodes.length);
      return this.snapshot;
    } catch (error) { await this.post({ type: 'error', message: error.message }); throw error; }
  }
  async waitReady() {
    let timer;
    try {
      await Promise.race([this.ready, new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error('Graph startup timed out. Restart the host; see SpecSpec output.')), this.host.timeout || 10_000);
      })]);
      if (this.disposed) throw new Error('Graph panel was closed before loading.');
    } finally { clearTimeout(timer); }
  }
  async waitRender(token) {
    if (this.renderError) throw this.renderError;
    if (this.lastRendered === token) return;
    await new Promise((resolve, reject) => {
      const done = error => { clearTimeout(timer); this.listeners.delete(check); error ? reject(error) : resolve(); };
      const check = () => {
        if (this.disposed) done(new Error('Graph panel was closed while rendering.'));
        else if (this.renderError) done(this.renderError);
        else if (this.lastRendered === token) done();
      };
      const timer = setTimeout(() => done(new Error('Graph rendering timed out. See SpecSpec output or Developer Tools.')), this.host.timeout || 10_000);
      this.listeners.add(check); check();
    });
  }
  async cli(args, input) {
    if (!this.host.authorized()) throw new Error('Workspace trust / project authorization is required to run SpecSpec.');
    return this.host.cli(args, input);
  }
  flushDocument() { return this.documentEdits || Promise.resolve(); }
  async drainDocumentEdits() {
    while (this.nextDocumentEdit) {
      const message = this.nextDocumentEdit; this.nextDocumentEdit = undefined;
      try { await this.editDocument(message); }
      catch (error) { this.log(error); await this.post({ type: 'error', message: error.message }); }
    }
  }
  async editDocument(message) {
    if (this.disposed || !this.host.authorized()) throw new Error('Workspace trust / project authorization is required to edit documents.');
    if (this.target) throw new Error('Historical comparisons are read-only.');
    const applied = await this.host.document.edit(message);
    if (!applied) { await this.post({ type: 'cancelled' }); return; }
    const document = this.host.document.state();
    if (Number.isInteger(applied.version)) document.version = applied.version;
    await this.post({ type: 'document-status', document, editSequence: message.editSequence });
    this.scheduleRefresh();
  }
  async readGraph() {
    return this.host.readGraph ? this.host.readGraph(this.base, this.target) : this.reads.readGraph(this.base, false, this.target);
  }
  warn(error) {
    this.log(error); this.warning = error.message;
    void this.post({ type: 'sync-warning', message: this.warning });
  }
  async invalid(error) {
    this.sourceInvalid = true;
    const policy = this.host.document ? 'The bound document remains editable for repair.' : 'Repair Markdown and refresh to resume graph actions.';
    await this.post({ type: 'sync-error', message: `Graph files need repair. Showing the last valid graph. ${policy}\n${error.message}` });
  }
  async refresh(force = false, selectedId, automatic = false) {
    if (!automatic) await this.post({ type: 'notice', message: this.target ? 'Loading revision comparison…' : 'Refreshing specification graph…' });
    let loaded;
    try {
      // Editors can truncate files or replace a whole directory while saving.
      for (let attempt = 0; ; attempt++) {
        try { loaded = await this.readGraph(); if (!loaded.snapshot?.valid) throw new Error('Invalid specification graph.'); break; }
        catch (error) {
          if (attempt >= 2 || this.disposed || !this.host.authorized()) throw error;
          await new Promise(resolve => { this.retryResolve = resolve; this.retryTimer = setTimeout(resolve, this.host.retryMs ?? (attempt + 1) * 200); });
          this.retryResolve = undefined;
          if (this.disposed) return;
        }
      }
    } catch (error) {
      if (this.disposed) return;
      if (error instanceof SupersededReadError) {
        // A notification raced the read, not proof of invalid Markdown. Keep the
        // existing view usable and let one coalesced follow-up catch up.
        if (automatic) this.autoAgain = true;
        else { this.scheduleRefresh(); throw error; }
        return;
      }
      await this.invalid(error);
      if (!automatic || this.annotationInitial || this.annotationError) await this.refreshAnnotations();
      if (!automatic) throw error; this.log(error); return;
    }
    if (this.disposed) return;
    await this.display(loaded, force, selectedId, automatic);
    if (!this.disposed && (!automatic || this.annotationInitial || this.annotationError)) await this.refreshAnnotations();
  }
  refreshAnnotations() {
    if (this.disposed) return Promise.resolve();
    if (this.annotationsWork) { this.annotationsAgain = true; return this.annotationsWork; }
    this.annotationsWork = this.readAnnotations().finally(() => {
      this.annotationsWork = undefined;
      if (this.annotationsAgain && !this.disposed) { this.annotationsAgain = false; this.scheduleAnnotationsRefresh(); }
    });
    return this.annotationsWork;
  }
  async readAnnotations() {
    try {
      const response = await this.cli(['api'], JSON.stringify({ api_version: 6, op: 'annotations' }));
      const shots = response.result?.shots;
      if (!Array.isArray(shots)) throw new Error('Spotlight response needs a valid list.');
      if (this.annotationInitial || !isDeepStrictEqual(shots, this.annotationShots) || this.annotationError) {
        this.annotationInitial = false;
        this.annotationShots = shots; this.annotationError = undefined;
        await this.post({ type: 'annotations', shots });
      }
    } catch (error) { this.annotationWarning(error); }
  }
  annotationWarning(error) {
    this.log(error); this.annotationError = error.message;
    void this.post({ type: 'annotations-error', message: error.message });
  }
  scheduleAnnotationsRefresh() {
    if (this.disposed) return;
    clearTimeout(this.annotationTimer);
    this.annotationTimer = setTimeout(() => this.requestAnnotationsRefresh(), this.host.debounceMs ?? 200);
  }
  requestAnnotationsRefresh() {
    if (this.disposed) return;
    void this.waitReady().then(() => this.refreshAnnotations()).catch(error => { if (!this.disposed) this.annotationWarning(error); });
  }
  sourceContext(id) {
    const displayed = this.lastPayload?.snapshot || this.snapshot, diff = this.lastPayload?.diff;
    const live = displayed?.nodes.find(n => n.id === id);
    const node = live || diff?.base.nodes.find(n => n.id === id);
    const ref = live ? (this.lastPayload?.readonly ? diff?.target_commit || diff?.target_ref : undefined)
      : diff?.base_commit || diff?.base_ref || this.base;
    return { node, ref };
  }
  async sourcePreview(message) {
    if (this.disposed || !this.host.authorized()) throw new Error('Project authorization is required to read sources.');
    if (message.renderToken !== this.renderSequence) throw new Error('Source view changed. Open the source again in the current graph.');
    const context = this.sourceContext(message.id);
    if (context.node?.type !== 'implementation') throw new Error('Select an implementation source.');
    if (!Number.isSafeInteger(message.requestId) || message.requestId < 1 || typeof message.reference !== 'string' ||
        Buffer.byteLength(message.reference, 'utf8') > 65536) throw new Error('Invalid source request.');
    const reference = JSON.parse(message.reference), sequence = this.sourceSequence = (this.sourceSequence || 0) + 1;
    this.sourcePending?.resolve();
    return new Promise((resolve, reject) => {
      this.sourcePending = { id: message.id, requestId: message.requestId, context: structuredClone(context), reference, sequence, resolve, reject };
      if (!this.sourceRunning) void this.drainSources();
    });
  }
  async drainSources() {
    this.sourceRunning = true;
    while (this.sourcePending && !this.disposed) {
      const request = this.sourcePending; this.sourcePending = undefined;
      const current = () => !this.disposed && request.sequence === this.sourceSequence &&
        isDeepStrictEqual(request.context, this.sourceContext(request.id));
      try {
        if (current()) {
          const response = await this.cli(['api'], JSON.stringify({ api_version: 6, op: 'source-view', reference: request.reference,
            ...(request.context.ref ? { ref: request.context.ref } : {}) }));
          if (current()) await this.post({ type: 'source-preview', requestId: request.requestId, ...response.result });
        }
        request.resolve();
      } catch (error) { if (current()) request.reject(error); else request.resolve(); }
    }
    this.sourceRunning = false;
  }
  async display(loaded, force, selectedId, automatic = false, provisional = false) {
    if (this.disposed) return;
    const document = this.host.document?.state();
    const payload = { ...loaded, ...(this.activeSpotlight ? { annotationShot: this.activeSpotlight } : {}), ...(document ? { document } : {}), ...(provisional ? { provisional: true } : {}), note: [this.warning, loaded.note, provisional ? 'Working graph — HEAD comparison loading…' : ''].filter(Boolean).join('\n'), readonly: Boolean(this.target) };
    // Direct record comparison, not a saved or calculated graph digest.
    if (automatic && !this.sourceInvalid && isDeepStrictEqual(payload, this.lastPayload)) return;
    this.sourceInvalid = false; this.lastPayload = payload; this.snapshot = loaded.snapshot;
    this.renderError = undefined; this.renderState = loaded;
    this.expectedCount = new Set([...(loaded.diff?.base.nodes || []), ...loaded.snapshot.nodes].map(n => n.id)).size;
    const renderToken = ++this.renderSequence;
    const initialId = this.host.document ? document.nodeId : undefined;
    this.hasOpened = true;
    await this.post({ type: 'snapshot', ...payload, force, selectedId: selectedId || initialId, renderToken });
    await this.waitRender(renderToken);
  }
  spotlightContext(shot) {
    this.activeSpotlight = shot;
    this.base = shot.comparison.base;
    this.target = shot.comparison.target === 'workspace' ? undefined : shot.comparison.target;
  }
  async selectSpotlight(id) {
    if (!this.host.authorized()) throw new Error('Project authorization is required for local spotlights.');
    await this.refreshAnnotations();
    const shot = this.annotationShots?.find(s => s.id === id);
    if (!shot) throw new Error('Select an existing spotlight; it may have been flushed.');
    const previous = { base: this.base, target: this.target, invalid: this.sourceInvalid };
    await this.flushDocument();
    this.spotlightContext(shot);
    try {
      await this.refresh();
      await this.post({ type: 'annotation-applied', shot });
    } catch (error) {
      this.base = previous.base; this.target = previous.target; this.activeSpotlight = undefined;
      // Keep the last usable view and still mark available IDs. Never silently
      // claim that a missing historical comparison was successfully loaded.
      this.sourceInvalid = Boolean(previous.invalid || shot.comparison.target === 'workspace');
      await this.post({ type: 'annotation-applied', shot, invalid: this.sourceInvalid, warning: `Spotlight comparison unavailable; using the displayed graph. ${error.message}` });
    }
  }
  async chooseRevisions() {
    const result = await this.host.revisions(this.base, this.target || '');
    if (!result) return;
    const [base, target] = result;
    if (typeof base !== 'string' || !base || base.length > 1024 || typeof target !== 'string' || target.length > 1024) throw new Error('Invalid revision input.');
    this.base = base; this.target = target || undefined; this.activeSpotlight = undefined;
    await this.post({ type: 'annotation-context' }); await this.refresh();
  }
  configurePolling(interval = 0) {
    interval = pollInterval(interval); clearInterval(this.pollTimer); this.pollTimer = undefined;
    if (interval && !this.disposed) this.pollTimer = setInterval(() => { this.requestRefresh(); this.requestAnnotationsRefresh(); }, interval);
  }
  scheduleRefresh() {
    if (this.disposed || this.target) return;
    clearTimeout(this.refreshTimer);
    this.refreshTimer = setTimeout(() => this.requestRefresh(), this.host.debounceMs ?? 200);
  }
  requestRefresh() {
    if (this.disposed || this.target) return;
    if (this.autoQueued) { this.autoAgain = true; return; }
    this.autoQueued = true;
    this.enqueue(async () => {
      try { await this.waitReady(); await this.refresh(false, undefined, true); }
      finally {
        this.autoQueued = false;
        if (this.autoAgain) { this.autoAgain = false; this.scheduleRefresh(); }
      }
    });
  }
  async handle(message) {
    if (message.type === 'annotation-select') return this.selectSpotlight(message.shot);
    if (message.type === 'annotation-create') {
      try {
        if (!this.host.authorized()) throw new Error('Project authorization is required for local spotlights.');
        if (!Array.isArray(message.nodes) || !message.nodes.length || message.nodes.length > 512 || message.nodes.some(id => typeof id !== 'string') || typeof message.message !== 'string' || !message.message.trim() || [...message.message].length > 500 || Buffer.byteLength(JSON.stringify(message.nodes), 'utf8') > 512 * 1024) throw new Error('Invalid or oversized highlight set/message.');
        await this.flushDocument();
        const documents = this.target ? {} : await this.host.annotationDocuments?.() || {};
        await this.cli(['api'], JSON.stringify({ api_version: 6, op: 'annotation-create', message: message.message, nodes: message.nodes,
          ...(this.base !== 'HEAD' || this.target ? { base: this.lastPayload?.diff?.base_commit || this.base } : {}),
          ...(this.target ? { target: this.lastPayload?.diff?.target_commit || this.target } : { documents }) }));
        await this.refreshAnnotations();
        await this.post({ type: 'annotation-created' });
      } catch (error) { this.log(error); await this.post({ type: 'annotation-create-error', message: error.message }); }
      return;
    }
    if (message.type === 'annotation-flush') {
      if (!this.host.authorized()) throw new Error('Project authorization is required for local spotlights.');
      const expected = (this.annotationShots || []).map(s => s.id);
      if (!expected.length) return;
      if (!await this.host.confirm(`Flush all ${expected.length} local spotlights? This affects both UIs for this checkout. Specification files, Git and recovery data are kept.`)) return;
      try {
        await this.cli(['api'], JSON.stringify({ api_version: 6, op: 'annotation-flush', expected }));
      } finally { await this.refreshAnnotations(); }
      return;
    }
    if (message.type === 'source-view') return this.sourcePreview(message);
    if (message.type === 'source-capture') {
      if (!this.host.authorized()) throw new Error('Project authorization is required to read sources.');
      const nodes = new Map([...(this.lastPayload?.diff?.base.nodes || []), ...(this.snapshot?.nodes || [])].map(n => [n.id, n]));
      const node = nodes.get(message.id);
      if (!node || node.type !== 'implementation') throw new Error('Select an implementation source.');
      if (this.target || !this.snapshot.nodes.some(n => n.id === message.id) || this.sourceInvalid) throw new Error('Capture requires a live editable implementation.');
      if (this.host.document && message.id !== this.host.document.state().nodeId) throw new Error('Capture belongs to the bound node.');
      if (typeof message.path !== 'string' || message.path.length > 4096 || !Array.isArray(message.ranges) || message.ranges.length > 64 || message.ranges.some(r => typeof r !== 'string' || !/^\d+:\d+$/.test(r)) || !['strict', 'expanding'].includes(message.mode)) throw new Error('Invalid source capture parameters.');
      const response = await this.cli(['api'], JSON.stringify({ api_version: 6, op: 'source-capture', id: message.id, path: message.path, ranges: message.ranges, mode: message.mode, staged: message.staged === true }));
      await this.post({ type: 'source-captured', id: message.id, reference: response.result.reference }); return;
    }
    if (this.host.document && message.type === 'delete') {
      if (message.id !== this.host.document.state().nodeId) throw new Error('A node-file editor can only delete its bound node.');
      await this.flushDocument();
    }
    if (this.host.document && message.type === 'save') {
      if (this.target) throw new Error('Historical comparisons are read-only.');
      if (!this.host.authorized()) throw new Error('Workspace trust / project authorization is required to edit documents.');
      if (message.id !== this.host.document.state().nodeId) throw new Error('A node-file editor can only edit its bound node.');
      await this.flushDocument();
      const applied = await this.host.document.edit(message);
      if (!applied) { await this.post({ type: 'cancelled' }); return; }
      await this.host.document.save();
      const document = this.host.document.state();
      if (Number.isInteger(applied?.version)) document.version = applied.version;
      await this.post({ type: 'document-status', document, editSequence: message.editSequence });
      await this.refresh(); return;
    }
    switch (message.type) {
      case 'refresh': await this.refresh(); return;
      case 'compare': await this.chooseRevisions(); return;
      case 'workspace': this.base = 'HEAD'; this.target = undefined; this.activeSpotlight = undefined; await this.post({ type: 'annotation-context' }); await this.refresh(); return;
    }
    if (this.target) throw new Error('Historical comparisons are read-only.');
    if (!this.snapshot?.valid) throw new Error('Load a valid graph before editing.');
    // Always validate actual current files, including changes whose watcher event was missed.
    let current;
    try {
      current = (await this.cli(['show', '--json'])).result;
      if (!current?.valid) throw new Error('Invalid specification graph.');
    } catch (error) { await this.invalid(error); throw error; }
    this.snapshot = current;
    const common = ['--json'];
    if (current.format_version !== 6) throw new Error('Unsupported specification format.');
    const nodes = new Map(current.nodes.map(n => [n.id, n])), id = message.id;
    if (message.type !== 'add' && (typeof id !== 'string' || !nodes.has(id))) throw new Error('Select a current node. Draft retained.');
    let args, input;
    if (message.type === 'save' || message.type === 'add') {
      if (typeof message.body !== 'string' || Buffer.byteLength(message.body, 'utf8') > 1024 * 1024) throw new Error('Invalid or oversized body.');
      if (!Array.isArray(message.parents) || message.parents.some(p => typeof p !== 'string' || !nodes.has(p))) throw new Error('Invalid parent IDs.');
      const parents = message.parents.flatMap(p => ['--parent', p]);
      if (message.type === 'add') {
        if (!['requirement', 'implementation'].includes(message.nodeType) || typeof message.slug !== 'string') throw new Error('Invalid new-node form.');
        args = ['add', '--type', message.nodeType, '--slug', message.slug, ...parents, '--body', '-'];
      } else {
        // No graph-wide stale gate: only overwriting this node needs user attention.
        if (!this.host.sameNode(message.originalNode, nodes.get(id)) && !await this.host.confirm('This node changed outside your draft (or its original contents are unavailable). Save your draft over its current text, parents and sources? Cancel keeps your unsaved text.')) { await this.post({ type: 'cancelled' }); return; }
        args = ['update', id, ...parents, '--body', '-'];
      }
      if (typeof message.sources !== 'string' || Buffer.byteLength(message.sources, 'utf8') > 1024 * 1024) throw new Error('Invalid source references.');
      if ((message.type === 'add' ? message.nodeType : nodes.get(id).type) === 'implementation') args.push('--sources', message.sources);
      input = message.body;
    } else if (message.type === 'delete') {
      if (nodes.get(id).type === 'manifesto') throw new Error('Keep the manifesto as the graph root.');
      const preview = await this.cli(['delete', id, '--dry-run', '--json']);
      const plan = preview.result;
      if (!Array.isArray(plan?.deleted_ids) || !plan.deleted_ids.includes(id)) throw new Error('Deletion plan needs a complete descendant list.');
      const warnings = (preview.diagnostics || []).filter(d => d.severity === 'warning').map(d => d.message);
      const text = `Delete this node and ALL its descendants (${plan.deleted_ids.length} Markdown files)? Children shared with surviving parents are also deleted. Outside parents/unrelated branches remain. The HEAD-relative workspace shows committed nodes as D until you commit; explain why in that commit.${warnings.length ? '\n\nWARNING — uncommitted nodes / unavailable Git assessment:\n' + warnings.join('\n') : ''}`;
      if (!await this.host.confirm(text)) { await this.post({ type: 'cancelled' }); return; }
      args = ['delete', id, '--yes', '--reviewed-plan', '-'];
      input = JSON.stringify(plan);
    } else throw new Error('Unknown graph action.');
    const response = await this.cli([...args, ...common], input);
    this.reads?.changed();
    await this.refresh(true, response.result.changed_ids?.[0]);
  }
  dispose() {
    this.disposed = true; clearTimeout(this.refreshTimer); clearTimeout(this.annotationTimer); clearInterval(this.pollTimer); clearTimeout(this.retryTimer);
    this.sourcePending?.resolve(); this.sourcePending = undefined;
    this.reads?.dispose(); this.retryResolve?.(); this.resolveReady(); this.listeners.forEach(f => f());
  }
}
module.exports = { GraphSession, pollInterval };
