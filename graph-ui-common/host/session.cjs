/* No editor/Electron imports: every host uses the same guarded graph operations. */
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
      if (!this.renderState || (value.view !== undefined && value.fingerprint !== this.renderState.snapshot.fingerprint)
        || !this.host.renderMatches(this.renderState, value)) {
        this.renderError = new Error(`Graph rendering is incomplete or inconsistent; expected ${this.expectedCount} known nodes in the overview or a complete selected neighborhood.`);
      } else this.lastRendered = value.renderToken;
      this.listeners.forEach(f => f()); return;
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
  async refresh(force = false, selectedId) {
    let diff, snapshot, diagnostics, note = '';
    if (this.target) {
      const response = await this.cli(['diff', '--base', this.base, '--target', this.target, '--json']);
      diff = response.result; snapshot = diff.target; diagnostics = response.diagnostics;
    } else {
      const response = await this.cli(['export', '--format', 'json']); snapshot = response.result; diagnostics = response.diagnostics;
      try { diff = (await this.cli(['diff', '--base', this.base, '--json'])).result; }
      catch (error) { note = `Diff unavailable: ${error.message}`; }
    }
    this.snapshot = snapshot; this.renderError = undefined; this.renderState = { snapshot, diff };
    this.expectedCount = new Set([...(diff?.base.nodes || []), ...snapshot.nodes].map(n => n.id)).size;
    const renderToken = ++this.renderSequence;
    await this.post({ type: 'snapshot', snapshot, diff, readonly: Boolean(this.target), force, selectedId, note, diagnostics, renderToken });
    await this.waitRender(renderToken);
  }
  async chooseRevisions() {
    const result = await this.host.revisions(this.base, this.target || '');
    if (!result) return;
    const [base, target] = result;
    if (typeof base !== 'string' || !base || base.length > 1024 || typeof target !== 'string' || target.length > 1024) throw new Error('Invalid revision input.');
    this.base = base; this.target = target || undefined; await this.refresh();
  }
  scheduleRefresh() {
    clearTimeout(this.refreshTimer);
    this.refreshTimer = setTimeout(() => this.enqueue(async () => { await this.waitReady(); await this.refresh(); }), 500);
  }
  async handle(message) {
    switch (message.type) {
      case 'refresh': await this.refresh(); return;
      case 'compare': await this.chooseRevisions(); return;
      case 'workspace': this.base = 'HEAD'; this.target = undefined; await this.refresh(); return;
    }
    if (this.target) throw new Error('Historical comparisons are read-only.');
    if (!this.snapshot?.valid || typeof message.expect !== 'string') throw new Error('Load a valid graph before editing.');
    if (message.expect !== this.snapshot.fingerprint) throw new Error('Displayed graph is stale; refresh before editing. Unsaved text has been retained.');
    const common = ['--expect', message.expect, '--json'];
    if (message.type === 'migrate') {
      if (this.snapshot.format_version !== 1) throw new Error('This graph already uses the current schema.');
      if (!await this.host.confirm('Migrate the whole graph to remove proposed/accepted metadata? IDs, text, dependencies and withdrawal history are preserved. Review the resulting Git diff.')) { await this.post({ type: 'cancelled' }); return; }
      await this.cli(['migrate', ...common]); await this.refresh(); return;
    }
    if (this.snapshot.format_version !== 2) throw new Error('Migrate this legacy graph before editing.');
    const nodes = new Map(this.snapshot.nodes.map(n => [n.id, n])), id = message.id;
    if (message.type !== 'add' && (typeof id !== 'string' || !nodes.has(id))) throw new Error('Unknown node ID.');
    let args, input;
    if (message.type === 'save' || message.type === 'add') {
      if (typeof message.body !== 'string' || Buffer.byteLength(message.body, 'utf8') > 1024 * 1024) throw new Error('Invalid or oversized body.');
      if (!Array.isArray(message.parents) || message.parents.some(p => typeof p !== 'string' || !nodes.has(p))) throw new Error('Invalid parent IDs.');
      const parents = message.parents.flatMap(p => ['--parent', p]);
      if (message.type === 'add') {
        if (!['requirement', 'implementation'].includes(message.nodeType) || typeof message.slug !== 'string') throw new Error('Invalid new-node form.');
        args = ['add', '--type', message.nodeType, '--slug', message.slug, ...parents, '--body', '-'];
      } else args = ['update', id, ...parents, ...(parents.length ? [] : ['--clear-parents']), '--body', '-'];
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
    this.disposed = true; clearTimeout(this.refreshTimer); this.resolveReady(); this.listeners.forEach(f => f());
  }
}
module.exports = { GraphSession };
