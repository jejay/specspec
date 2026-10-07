const { test } = require('node:test');
const assert = require('node:assert/strict');
const { GraphSession } = require('../host/session.cjs');
const { renderMatches } = require('../media/graph-model.js');
const snapshot = { fingerprint: 'current', valid: true, format_version: 2, nodes: [], edges: [] };
function fixture(t, options = {}) {
  let current = options.snapshot || snapshot, authorized = true;
  const calls = [], messages = [];
  const s = new GraphSession({
    timeout: 30, authorized: () => authorized, renderMatches,
    cli: async (args, input) => { calls.push({ args, input });
      if (options.fail) throw new Error('Failed backend');
      if (args[0] === 'migrate') current = { ...current, format_version: 2, fingerprint: 'migrated' };
      return { api_version: 2, ok: true, diagnostics: [], result: args[0] === 'diff' ? {
        base: current, target: current, changes: [], added_edges: [], removed_edges: [],
        base_ref: 'HEAD', target_ref: 'workspace', source_changes: [], source_affected: [],
      } : current };
    },
    post: async value => { messages.push(value); if (value.type === 'snapshot' && !options.noRender) s.receive({ type: 'rendered',
      renderToken: value.renderToken, view: 'overview', fingerprint: options.wrongFingerprint ? 'wrong' : value.snapshot.fingerprint,
      visibleIds: value.snapshot.nodes.map(n => n.id), nodeCount: value.snapshot.nodes.length }); },
    confirm: async () => options.confirm !== false,
    revisions: async () => options.revisions,
  });
  t.after(() => s.dispose()); s.receive({ type: 'ready' });
  return { s, calls, messages, revoke: () => { authorized = false; } };
}

test('every host rejects stale writers before invoking the authoritative CLI', async t => {
  const { s, calls } = fixture(t); await s.open(); const reads = calls.length;
  await assert.rejects(s.handle({ type: 'migrate', expect: 'old' }), /stale/);
  assert.equal(calls.length, reads);
});
test('cancelled migration preserves legacy view and guarded migration keeps no force rebase', async t => {
  const f = fixture(t, { snapshot: { ...snapshot, format_version: 1 }, confirm: false }); await f.s.open();
  await f.s.handle({ type: 'migrate', expect: 'current' }); assert.equal(f.messages.at(-1).type, 'cancelled');
  assert.ok(!f.calls.some(c => c.args[0] === 'migrate'));
  const yes = fixture(t, { snapshot: { ...snapshot, format_version: 1 } }); await yes.s.open();
  await yes.s.handle({ type: 'migrate', expect: 'current' });
  assert.deepEqual(yes.calls.find(c => c.args[0] === 'migrate').args, ['migrate', '--expect', 'current', '--json']);
  assert.equal(yes.messages.at(-1).force, false);
});
test('authorization loss and historical selection block writes for every adapter', async t => {
  const f = fixture(t, { snapshot: { ...snapshot, format_version: 1 } }); await f.s.open(); f.revoke();
  await assert.rejects(f.s.handle({ type: 'migrate', expect: 'current' }), /authorization/);
  assert.ok(!f.calls.some(c => c.args[0] === 'migrate'));
  const history = fixture(t, { revisions: ['HEAD', 'HEAD'] }); await history.s.open(); await history.s.chooseRevisions();
  await assert.rejects(history.s.handle({ type: 'add', expect: 'current' }), /read-only/);
});
test('incomplete render fingerprints and missing acknowledgements are not successful opens', async t => {
  const wrong = fixture(t, { wrongFingerprint: true }); await assert.rejects(wrong.s.open(), /incomplete/);
  const absent = fixture(t, { noRender: true }); await assert.rejects(absent.s.open(), /did not render/);
});
test('disposal releases an outstanding renderer wait', async t => {
  const { s, messages } = fixture(t, { noRender: true }); const opening = s.open();
  while (!messages.some(m => m.type === 'snapshot')) await new Promise(r => setTimeout(r, 1));
  s.dispose(); await assert.rejects(opening, /closed while rendering/);
});
test('session serializes refreshes and passes body as stdin, never arbitrary renderer commands', async t => {
  const f = fixture(t); await f.s.open();
  await Promise.all([f.s.run(() => f.s.handle({ type: 'refresh' })), f.s.run(() => f.s.handle({ type: 'refresh' }))]);
  await f.s.handle({ type: 'add', expect: 'current', nodeType: 'requirement', slug: 'literal', parents: [], body: '# Literal $(touch anything)', sources: '[]' });
  const write = f.calls.find(c => c.args[0] === 'add'); assert.equal(write.input, '# Literal $(touch anything)');
  assert.ok(!write.args.includes(write.input));
  await assert.rejects(f.s.handle({ type: 'exec', expect: 'current', command: 'anything' }), /Unknown node|Unknown graph/);
});
