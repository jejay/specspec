/* Portable project-level document coordination. No VS Code/Electron imports. */
const { isDeepStrictEqual } = require('node:util');
function minimalTextEdit(before, after) {
  let start = 0, end = before.length, nextEnd = after.length;
  while (start < end && start < nextEnd && before[start] === after[start]) start++;
  const split = (text, offset) => offset > 0 && offset < text.length &&
    ((text[offset - 1] === '\r' && text[offset] === '\n') ||
      (text.charCodeAt(offset - 1) >= 0xD800 && text.charCodeAt(offset - 1) <= 0xDBFF &&
        text.charCodeAt(offset) >= 0xDC00 && text.charCodeAt(offset) <= 0xDFFF));
  if (split(before, start) || split(after, start)) start--;
  while (end > start && nextEnd > start && before[end - 1] === after[nextEnd - 1]) { end--; nextEnd--; }
  if (split(before, end) || split(after, nextEnd)) { end++; nextEnd++; }
  return { start, end, text: after.slice(start, nextEnd) };
}
class ProjectDocuments {
  constructor(host) { this.host = host; this.queue = Promise.resolve(); this.listeners = new Set(); this.generation = 0; this.reads = new Map(); }
  run(operation) {
    const result = this.queue.then(operation); this.queue = result.catch(() => {}); return result;
  }
  idle() { return this.queue; }
  subscribe(listener) { this.listeners.add(listener); return { dispose: () => this.listeners.delete(listener) }; }
  changed() { this.generation++; this.listeners.forEach(listener => listener()); }
  documents() { return this.host.documents().filter(d => !d.closed); }
  stamp() { return this.documents().map(d => [d.path, d.text, d.version, d.dirty, d.eol]).sort(([a], [b]) => a.localeCompare(b)); }
  async request(edit, base) {
    if (this.disposed) throw new Error('Project documents are closed.');
    const documents = Object.fromEntries(this.documents().map(d => [d.path, d.text]));
    const result = await this.host.cli(['editor', ...(base ? ['--base', base] : []), '--json'], JSON.stringify({ documents, ...(edit ? { edit } : {}),
      ...(base ? { cache: true, ...(this.baseCache ? { base_cache: this.baseCache } : {}) } : {}) }));
    const { base_cache, ...loaded } = result.result;
    // The backend validates these immutable byte hints against freshly read Git metadata.
    if (!this.disposed && base_cache && Buffer.byteLength(JSON.stringify(base_cache)) <= 3 * 1024 * 1024) this.baseCache = base_cache;
    return loaded;
  }
  async readGraph(base, allowInvalid = false) {
    const before = this.stamp(), generation = this.generation;
    const key = JSON.stringify([base, generation, before]);
    let pending = this.reads.get(key);
    if (!pending) {
      pending = this.request(undefined, base);
      if (this.reads.size < 32) this.reads.set(key, pending);
      const clear = () => { if (this.reads.get(key) === pending) this.reads.delete(key); };
      pending.then(clear, clear);
    }
    const result = await pending;
    if (this.disposed || generation !== this.generation || !isDeepStrictEqual(before, this.stamp())) throw new Error('Documents changed during graph loading; retry with current text.');
    if (!allowInvalid && !result.snapshot.valid) throw new Error(result.diagnostics.map(d => `${d.code}: ${d.message}`).join('\n') || 'Invalid open specification documents.');
    return structuredClone(result);
  }
  async bootstrap() {
    const stamp = this.stamp(), generation = this.generation;
    return { result: await this.readGraph(undefined, true), stamp, generation };
  }
  async initial(lease) {
    if (lease && !this.disposed && lease.generation === this.generation && isDeepStrictEqual(lease.stamp, this.stamp()) && lease.result.snapshot.valid) return structuredClone(lease.result);
    return this.readGraph();
  }
  dispose() { this.disposed = true; this.generation++; this.reads.clear(); this.baseCache = undefined; this.listeners.clear(); }
  edit(adapter, message) {
    return this.run(async () => {
      const current = adapter.get();
      if (current.closed) throw new Error('The node document is closed. Unsaved form text is retained.');
      if (message.id !== adapter.id) throw new Error('A node-file editor can only edit its bound node.');
      if (typeof message.body !== 'string' || Buffer.byteLength(message.body, 'utf8') > 1024 * 1024 ||
        !Array.isArray(message.parents) || message.parents.some(id => typeof id !== 'string') ||
        typeof message.sources !== 'string' || Buffer.byteLength(message.sources, 'utf8') > 1024 * 1024) throw new Error('Invalid document edit.');
      const body = ['\n', '\r\n'].includes(current.eol) ? message.body.replace(/\r?\n/g, current.eol) : message.body;
      const result = await this.request({ path: current.path, id: adapter.id, body, parents: message.parents, sources: message.sources });
      const change = result.changes[0];
      if (change.after !== change.before && message.documentVersion !== current.version && adapter.lastAppliedVersion !== current.version &&
        !await this.host.confirm('This document changed outside this form. Apply the form over its current body, parents and sources? Cancel retains the form text.')) return false;
      // Versions and actual text, not fingerprints; no rebase over concurrent typing.
      const latest = adapter.get();
      if (latest.version !== current.version || latest.text !== change.before) throw new Error('Document changed while planning. Your form is retained; retry after reviewing current text.');
      if (change.after !== change.before) await adapter.apply(change.before, change.after, minimalTextEdit(change.before, change.after));
      const applied = adapter.get();
      if (applied.text !== change.after) throw new Error('Document changed while applying. Current text is retained; review the pending form before retrying.');
      adapter.lastAppliedVersion = applied.version;
      this.changed(); return { version: applied.version };
    });
  }
  mutate(args, input) {
    return this.run(async () => {
      if (this.documents().some(d => d.dirty)) throw new Error('Save or revert dirty SpecSpec documents before a project-wide CLI mutation.');
      const result = await this.host.cli(args, input); this.changed(); return result;
    });
  }
}
module.exports = { ProjectDocuments, minimalTextEdit };
