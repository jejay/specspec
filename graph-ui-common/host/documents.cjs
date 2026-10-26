/* Native document planning extends the same portable reads used by Electron. */
const { ProjectReads } = require('./reads.cjs');
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
class ProjectDocuments extends ProjectReads {
  edit(adapter, message) {
    return this.run(async () => {
      const current = adapter.get();
      if (current.closed) throw new Error('The node document is closed. Unsaved form text is retained.');
      if (message.id !== adapter.id) throw new Error('A node-file editor can only edit its bound node.');
      if (typeof message.body !== 'string' || Buffer.byteLength(message.body, 'utf8') > 1024 * 1024 ||
        !Array.isArray(message.parents) || message.parents.some(id => typeof id !== 'string') ||
        typeof message.sources !== 'string' || Buffer.byteLength(message.sources, 'utf8') > 1024 * 1024) throw new Error('Invalid document edit.');
      const body = ['\n', '\r\n'].includes(current.eol) ? message.body.replace(/\r\n?|\n/g, current.eol) : message.body;
      const result = await this.request({ path: current.path, id: adapter.id, body, parents: message.parents, sources: message.sources });
      const change = result.changes[0];
      if (change.after !== change.before && message.documentVersion !== current.version && adapter.lastAppliedVersion !== current.version &&
        !await this.host.confirm('This document changed outside this form. Apply the form over its current body, parents and sources? Cancel retains the form text.')) return false;
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
