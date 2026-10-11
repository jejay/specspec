/* No editor/Electron imports: every host uses the same graph operations. */
const { isDeepStrictEqual } = require('node:util');

function pollInterval(value) {
  if (!Number.isSafeInteger(value) || value < 0 || value > 2_147_483_647) throw new Error('Polling interval must be an integer from 0 to 2147483647 ms (0 disables polling).');
  return value;
}

class GraphSession {
  constructor(host) {
    this.host = host; this.base = 'HEAD'; this.queue = Promise.resolve();
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
    if (value.type === 'ready') { this.resolveReady(); return; }
    if (value.type === 'client-error' && typeof value.message === 'string') {
      this.renderError = new Error(`Graph renderer failed: ${value.message}`); this.log(this.renderError);
      this.listeners.forEach(f => f()); return;
    }
    if (value.type === 'rendered') {
      if (value.renderToken !== this.renderSequence) return;
      if (!this.renderState || !this.host.renderMatches(this.renderState, value)) {
        this.renderError = new Error(`Graph rendering is incomplete or inconsistent; expected ${this.expectedCount} known nodes in the overview or a complete selected neighborhood.`);
      } else this.lastRendered = value.renderToken;
      this.listeners.forEach(f => f()); return;
    }
    if (value.type === 'edit' && this.host.document) {
      this.nextDocumentEdit = value;
      if (!this.documentEdits) this.documentEdits = this.drainDocumentEdits().finally(() => { this.documentEdits = undefined; });
      return;
    }
    this.enqueue(() => this.handle(value));
  }
  async open() {
    try {
      await this.waitReady(); await this.run(() => this.refresh()); return this.snapshot;
    } catch (error) { await this.post({ type: 'error', message: error.message }); throw error; }
  }
  async waitReady() {
    let timer;
    try {
      await Promise.race([this.ready, new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error('Graph webview did not initialize. Restart the host and check the SpecSpec output log.')), this.host.timeout || 10_000);
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
      const timer = setTimeout(() => done(new Error('Graph data loaded but the webview did not render. See the SpecSpec output log or Developer Tools.')), this.host.timeout || 10_000);
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
    const applied = await this.host.document.edit(message);
    if (!applied) { await this.post({ type: 'cancelled' }); return; }
    const document = this.host.document.state();
    if (Number.isInteger(applied.version)) document.version = applied.version;
    await this.post({ type: 'document-status', document, editSequence: message.editSequence });
    this.scheduleRefresh();
  }
  async readGraph() {
    if (this.target) {
      const response = await this.cli(['diff', '--base', this.base, '--target', this.target, '--json']);
      return { diff: response.result, snapshot: response.result.target, diagnostics: response.diagnostics, note: '' };
    }
    if (this.host.readGraph) return this.host.readGraph(this.base);
    const response = await this.cli(['export', '--format', 'json']);
    let snapshot = response.result, diff, note = '', diagnostics = response.diagnostics;
    try {
      const comparison = await this.cli(['diff', '--base', this.base, '--json']);
      diff = comparison.result; snapshot = diff.target; diagnostics = comparison.diagnostics;
    } catch (error) { note = `Diff unavailable: ${error.message}`; }
    return { snapshot, diff, note, diagnostics };
  }
  warn(error) {
    this.log(error); this.warning = error.message;
    void this.post({ type: 'sync-warning', message: this.warning });
  }
  async invalid(error) {
    this.sourceInvalid = true;
    const policy = this.host.document ? 'The bound document remains editable for repair.' : 'Editing is disabled until the files are valid.';
    await this.post({ type: 'sync-error', message: `Files could not be loaded. The displayed graph is out of date. ${policy}\n${error.message}` });
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
    } catch (error) { await this.invalid(error); if (!automatic) throw error; this.log(error); return; }
    if (this.disposed) return;
    const document = this.host.document?.state();
    const payload = { ...loaded, ...(document ? { document } : {}), note: [this.warning, loaded.note].filter(Boolean).join('\n'), readonly: Boolean(this.target) };
    // Direct record comparison, not a saved or calculated graph digest.
    if (automatic && !this.sourceInvalid && isDeepStrictEqual(payload, this.lastPayload)) return;
    this.sourceInvalid = false; this.lastPayload = payload; this.snapshot = loaded.snapshot;
    this.renderError = undefined; this.renderState = loaded;
    this.expectedCount = new Set([...(loaded.diff?.base.nodes || []), ...loaded.snapshot.nodes].map(n => n.id)).size;
    const renderToken = ++this.renderSequence;
    const initialId = this.host.document && !this.hasOpened ? document.nodeId : undefined;
    this.hasOpened = true;
    await this.post({ type: 'snapshot', ...payload, force, selectedId: selectedId || initialId, renderToken });
    await this.waitRender(renderToken);
  }
  async chooseRevisions() {
    const result = await this.host.revisions(this.base, this.target || '');
    if (!result) return;
    const [base, target] = result;
    if (typeof base !== 'string' || !base || base.length > 1024 || typeof target !== 'string' || target.length > 1024) throw new Error('Invalid revision input.');
    this.base = base; this.target = target || undefined; await this.refresh();
  }
  configurePolling(interval = 0) {
    interval = pollInterval(interval); clearInterval(this.pollTimer); this.pollTimer = undefined;
    if (interval && !this.disposed) this.pollTimer = setInterval(() => this.requestRefresh(), interval);
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
    if (this.host.document && ['save', 'retire', 'restore'].includes(message.type)) {
      if (!this.host.authorized()) throw new Error('Workspace trust / project authorization is required to edit documents.');
      if (message.id !== this.host.document.state().nodeId) throw new Error('A node-file editor can only edit its bound node.');
      await this.flushDocument();
      let applied;
      if (message.type === 'save') {
        applied = await this.host.document.edit(message);
        if (!applied) { await this.post({ type: 'cancelled' }); return; }
        await this.host.document.save();
      } else {
        if (!await this.host.confirm(`${message.type === 'restore' ? 'Restore this withdrawn node? Restoration is not approval.' : 'Retire this node, retaining its history?'} Check its dependency impact.`)) { await this.post({ type: 'cancelled' }); return; }
        await this.host.document.withdrawal(message.type === 'retire');
      }
      const document = this.host.document.state();
      if (Number.isInteger(applied?.version)) document.version = applied.version;
      await this.post({ type: 'document-status', document, editSequence: message.editSequence });
      await this.refresh(); return;
    }
    switch (message.type) {
      case 'refresh': await this.refresh(); return;
      case 'compare': await this.chooseRevisions(); return;
      case 'workspace': this.base = 'HEAD'; this.target = undefined; await this.refresh(); return;
    }
    if (this.target) throw new Error('Historical comparisons are read-only.');
    if (!this.snapshot?.valid) throw new Error('Load a valid graph before editing.');
    // Always validate actual current files, including changes whose watcher event was missed.
    let current;
    try {
      current = (await this.cli(['export', '--format', 'json'])).result;
      if (!current?.valid) throw new Error('Invalid specification graph.');
    } catch (error) { await this.invalid(error); throw error; }
    this.snapshot = current;
    const common = ['--json'];
    if (message.type === 'migrate') {
      if (current.format_version === 3) throw new Error('This graph already uses the current schema.');
      if (!await this.host.confirm('Migrate the whole graph to the hash-free format? Obsolete hashes and approval metadata are removed; IDs, text, dependencies and withdrawal history are preserved. Review the resulting Git diff.')) { await this.post({ type: 'cancelled' }); return; }
      await this.cli(['migrate', ...common]); await this.refresh(); return;
    }
    if (current.format_version !== 3) throw new Error('Migrate this legacy graph before editing.');
    const nodes = new Map(current.nodes.map(n => [n.id, n])), id = message.id;
    if (message.type !== 'add' && (typeof id !== 'string' || !nodes.has(id))) throw new Error('The node no longer exists. Unsaved text has been retained.');
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
        args = ['update', id, ...parents, ...(parents.length ? [] : ['--clear-parents']), '--body', '-'];
      }
      if (typeof message.sources !== 'string' || Buffer.byteLength(message.sources, 'utf8') > 1024 * 1024) throw new Error('Invalid source references.');
      if ((message.type === 'add' ? message.nodeType : nodes.get(id).type) === 'implementation') args.push('--sources', message.sources);
      input = message.body;
    } else if (message.type === 'restore' || message.type === 'retire') {
      if (!await this.host.confirm(`${message.type === 'restore' ? 'Restore this withdrawn node? Restoration is not approval.' : 'Retire this node, retaining its history?'} Check its dependency impact.`)) { await this.post({ type: 'cancelled' }); return; }
      args = [message.type, id];
    } else throw new Error('Unknown graph action.');
    const response = await this.cli([...args, ...common], input);
    await this.refresh(true, response.result.changed_ids?.[0]);
  }
  dispose() {
    this.disposed = true; clearTimeout(this.refreshTimer); clearInterval(this.pollTimer); clearTimeout(this.retryTimer);
    this.retryResolve?.(); this.resolveReady(); this.listeners.forEach(f => f());
  }
}
module.exports = { GraphSession, pollInterval };
