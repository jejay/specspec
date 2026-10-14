const { test } = require('node:test');
const assert = require('node:assert/strict');
const { ProjectDocuments, minimalTextEdit } = require('../host/documents.cjs');

function fixture(options = {}) {
  const doc = { path: '_specspec/node.md', text: '# Original', version: 1, dirty: false };
  const calls = [], confirmations = [];
  const project = new ProjectDocuments({
    documents: () => [doc], confirm: async text => { confirmations.push(text); return options.confirm !== false; },
    cli: async (args, input) => {
      calls.push({ args, input });
      const request = JSON.parse(input || '{}');
      if (options.slow) await new Promise(resolve => setTimeout(resolve, 5));
      if (options.concurrent) { doc.version++; doc.text = '# External'; }
      const changes = request.edit ? [{ path: doc.path, before: request.documents[doc.path], after: request.edit.body ?? '# Unchanged' }] : [];
      return { diagnostics: options.invalid ? [{ code: 'SCHEMA', message: 'Invalid buffer' }] : [], result: { snapshot: { valid: !options.invalid, nodes: [] }, changes } };
    },
  });
  const adapter = { id: 'node', nodeType: 'requirement', get: () => ({ ...doc }),
    apply: async (before, after, edit) => { assert.equal(doc.text, before); assert.equal(before.slice(0, edit.start) + edit.text + before.slice(edit.end), after);
      doc.text = after; doc.version++; doc.dirty = true; } };
  return { doc, calls, project, adapter, confirmations };
}
const edit = body => ({ id: 'node', body, parents: [], sources: '[]', documentVersion: 1 });

test('document planning never invokes a writer and serializes rapid edits against current buffers', async () => {
  const f = fixture({ slow: true }); let notifications = 0; f.project.subscribe(() => notifications++);
  await Promise.all([f.project.edit(f.adapter, edit('# First')), f.project.edit(f.adapter, edit('# Second'))]);
  assert.equal(f.doc.text, '# Second'); assert.equal(f.doc.dirty, true);
  assert.equal(f.confirmations.length, 0); assert.equal(notifications, 2);
  assert.deepEqual(f.calls.map(c => c.args), [['api'], ['api']]);
  assert.equal(JSON.parse(f.calls[1].input).documents[f.doc.path], '# First');
});
test('native/other-view changes ask before overwriting; concurrent planning changes are refused', async () => {
  const f = fixture({ confirm: false }); f.doc.version = 2; f.doc.text = '# Native';
  assert.equal(await f.project.edit(f.adapter, edit('# Mine')), false);
  assert.equal(f.doc.text, '# Native'); assert.equal(f.calls.length, 1); assert.equal(f.calls[0].args[0], 'api');
  assert.match(f.confirmations[0], /outside this form/);
  const concurrent = fixture({ concurrent: true });
  await assert.rejects(concurrent.project.edit(concurrent.adapter, edit('# Mine')), /changed while planning/);
  assert.equal(concurrent.doc.text, '# External');
});
test('edits cannot claim ownership of a peer change that arrives during native apply', async () => {
  const f = fixture(), apply = f.adapter.apply;
  f.adapter.apply = async (...args) => { await apply(...args); f.doc.text = '# Peer'; f.doc.version++; };
  await assert.rejects(f.project.edit(f.adapter, edit('# Mine')), /changed while applying/);
  assert.equal(f.doc.text, '# Peer'); assert.equal(f.adapter.lastAppliedVersion, undefined);
});
test('invalid intermediate text stays in the native document but cannot masquerade as a valid graph', async () => {
  const f = fixture({ invalid: true });
  await f.project.edit(f.adapter, edit('')); assert.equal(f.doc.dirty, true);
  await assert.rejects(f.project.readGraph('HEAD'), /SCHEMA: Invalid buffer/);
  await assert.rejects(f.project.mutate(['delete', 'node', '--json']), /Save or revert/);
  assert.equal(f.project.withdrawal, undefined);
});
test('graph reads cannot label an old buffer snapshot with a newer native document version', async () => {
  const f = fixture({ concurrent: true });
  await assert.rejects(f.project.readGraph('HEAD'), /changed during graph loading/);
  assert.equal(f.doc.text, '# External'); assert.equal(f.doc.version, 2);
});
test('project-wide mutations refuse dirty open documents and unknown node editors', async () => {
  const f = fixture(); f.doc.dirty = true;
  await assert.rejects(f.project.mutate(['add', '--json']), /Save or revert/);
  assert.equal(f.calls.length, 0);
  await assert.rejects(f.project.edit(f.adapter, { ...edit('# Mine'), id: 'other' }), /bound node/);
  f.doc.closed = true; await assert.rejects(f.project.edit(f.adapter, edit('# Mine')), /closed/);
});
test('native document line endings are respected without an unnecessary overwrite after undo', async () => {
  const f = fixture(); f.doc.text = '# Same\r\n'; f.doc.eol = '\r\n'; f.doc.version = 4;
  f.adapter.lastAppliedVersion = 2;
  await f.project.edit(f.adapter, { ...edit('# Same\n'), documentVersion: 2 });
  assert.equal(f.doc.text, '# Same\r\n'); assert.equal(f.doc.dirty, false); assert.equal(f.confirmations.length, 0);
  assert.equal(JSON.parse(f.calls[0].input).edit.body, '# Same\r\n');
});
test('minimal edits preserve unchanged text and never split CRLF or surrogate pairs', () => {
  for (const [before, after] of [['same', 'same'], ['', 'new'], ['abc', ''], ['x\r\na', 'x\ra'], ['🐕 dog', '🐖 dog'], ['a🐕z', 'a🦊z'], ['---\r\n---\r\n# A', '---\r\n---\r\n# B']]) {
    const e = minimalTextEdit(before, after);
    assert.equal(before.slice(0, e.start) + e.text + before.slice(e.end), after);
    assert.ok(!(e.start && before[e.start - 1] === '\r' && before[e.start] === '\n'));
    assert.ok(!(e.end && before[e.end - 1] === '\r' && before[e.end] === '\n'));
  }
});
