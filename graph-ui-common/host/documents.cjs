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
  constructor(host) { this.host = host; this.queue = Promise.resolve(); this.listeners = new Set(); this.generation = 0; }
  run(operation) {
    const result = this.queue.then(operation); this.queue = result.catch(() => {}); return result;
  }
  idle() { return this.queue; }
  subscribe(listener) { this.listeners.add(listener); return { dispose: () => this.listeners.delete(listener) }; }
  changed() { this.generation++; this.listeners.forEach(listener => listener()); }
  documents() { return this.host.documents().filter(d => !d.closed); }
  async request(edit, base) {
    const documents = Object.fromEntries(this.documents().map(d => [d.path, d.text]));
    const result = await this.host.cli(['editor', ...(base ? ['--base', base] : []), '--json'], JSON.stringify({ documents, ...(edit ? { edit } : {}) }));
    return result.result;
  }
  async readGraph(base) {
    const stamp = () => this.documents().map(d => [d.path, d.text, d.version, d.dirty, d.eol]).sort(([a], [b]) => a.localeCompare(b));
    const before = stamp(), generation = this.generation;
    const result = await this.request(undefined, base);
    // Don't attach a new document version to graph data read from an older buffer.
    // GraphSession retries boundedly and keeps the last valid graph during typing.
    if (generation !== this.generation || !isDeepStrictEqual(before, stamp())) throw new Error('Documents changed during graph loading; retry with current text.');
    if (!result.snapshot.valid) throw new Error(result.diagnostics.map(d => `${d.code}: ${d.message}`).join('\n') || 'Invalid open specification documents.');
    return result;
  }
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
