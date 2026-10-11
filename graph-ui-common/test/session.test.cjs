const { test } = require('node:test');
const assert = require('node:assert/strict');
const { GraphSession, pollInterval } = require('../host/session.cjs');
const { renderMatches, sameNode } = require('../media/graph-model.js');
const node = { id: 'node', type: 'requirement', retired: false, body: '# Original', parents: [], sources: [], extensions: {}, path: '_specspec/node.md' };
const snapshot = { valid: true, format_version: 3, nodes: [node], edges: [] };
const pause = ms => new Promise(r => setTimeout(r, ms));
async function waitFor(check) { for (let i = 0; i < 100; i++) { if (check()) return; await pause(5); } assert.ok(check()); }
function fixture(t, options = {}) {
  let current = options.snapshot || snapshot, authorized = true, failure = false, remainingFailures = 0;
  const calls = [], messages = [], confirmations = [];
  const s = new GraphSession({
    timeout: 40, retryMs: 1, debounceMs: 5, authorized: () => authorized, renderMatches, sameNode,
    cli: async (args, input) => { calls.push({ args, input });
      if (failure || remainingFailures-- > 0) throw new Error('YAML: partial external save');
      if (options.slow) await pause(options.slow);
      if (args[0] === 'migrate') current = { ...current, format_version: 3 };
      if (args[0] === 'update') current = { ...current, nodes: current.nodes.map(n => n.id === args[1] ? { ...n, body: input } : n), changed_ids: [args[1]] };
      return { api_version: 3, ok: true, diagnostics: [], result: args[0] === 'diff' ? {
        base: current, target: current, changes: [], added_edges: [], removed_edges: [],
        base_ref: 'HEAD', target_ref: 'workspace', source_changes: [], source_affected: [],
      } : current };
    },
    post: async value => { messages.push(value); if (value.type === 'snapshot' && !options.noRender) s.receive({ type: 'rendered',
      renderToken: value.renderToken, view: 'overview',
      visibleIds: options.wrongMembership ? [] : value.snapshot.nodes.map(n => n.id), nodeCount: value.snapshot.nodes.length }); },
    confirm: async text => { confirmations.push(text); return options.confirm !== false; },
    revisions: async () => options.revisions,
  });
  t.after(() => s.dispose()); s.receive({ type: 'ready' });
  return { s, calls, messages, confirmations, change: value => { current = value; }, fail: value => { failure = value; }, failNext: count => { remainingFailures = count; }, revoke: () => { authorized = false; } };
}
const save = originalNode => ({ type: 'save', id: 'node', originalNode, parents: [], sources: '[]', body: '# Draft' });

test('migration uses no hashes or expectation options and cancellation preserves legacy files', async t => {
  const f = fixture(t, { snapshot: { ...snapshot, format_version: 2 }, confirm: false }); await f.s.open();
  await f.s.handle({ type: 'migrate' }); assert.equal(f.messages.at(-1).type, 'cancelled');
  assert.ok(!f.calls.some(c => c.args[0] === 'migrate'));
  const yes = fixture(t, { snapshot: { ...snapshot, format_version: 1 } }); await yes.s.open();
  await yes.s.handle({ type: 'migrate' });
  assert.deepEqual(yes.calls.find(c => c.args[0] === 'migrate').args, ['migrate', '--json']);
  assert.equal(yes.messages.at(-1).force, false);
});
test('authorization loss and historical selection block writes', async t => {
  const f = fixture(t); await f.s.open(); f.revoke();
  await assert.rejects(f.s.handle(save(node)), /authorization/);
  assert.ok(!f.calls.some(c => c.args[0] === 'update'));
  const history = fixture(t, { revisions: ['HEAD', 'HEAD'] }); await history.s.open(); await history.s.chooseRevisions();
  await assert.rejects(history.s.handle(save(node)), /read-only/);
});
test('full render membership and sequence tokens replace fingerprint acknowledgements', async t => {
  const wrong = fixture(t, { wrongMembership: true }); await assert.rejects(wrong.s.open(), /incomplete/);
  const absent = fixture(t, { noRender: true }); await assert.rejects(absent.s.open(), /did not render/);
  const ok = fixture(t); await ok.s.open();
  ok.s.receive({ type: 'rendered', renderToken: 0, view: 'overview', visibleIds: [], nodeCount: 0 });
  assert.equal(ok.s.renderError, undefined);
});
test('disposal releases an outstanding renderer wait', async t => {
  const { s, messages } = fixture(t, { noRender: true }); const opening = s.open();
  await waitFor(() => messages.some(m => m.type === 'snapshot'));
  s.dispose(); await assert.rejects(opening, /closed while rendering/);
});
test('serialized operations pass body as stdin, never renderer commands', async t => {
  const f = fixture(t); await f.s.open();
  await Promise.all([f.s.run(() => f.s.handle({ type: 'refresh' })), f.s.run(() => f.s.handle({ type: 'refresh' }))]);
  await f.s.handle({ type: 'add', nodeType: 'requirement', slug: 'literal', parents: [], body: '# Literal $(touch anything)', sources: '[]' });
  const write = f.calls.find(c => c.args[0] === 'add'); assert.equal(write.input, '# Literal $(touch anything)');
  assert.ok(!write.args.includes(write.input)); assert.ok(!write.args.includes('--expect'));
  await assert.rejects(f.s.handle({ type: 'exec', command: 'anything' }), /no longer exists|Unknown graph/);
});
test('unrelated changes do not block drafts; every save re-reads actual files', async t => {
  const f = fixture(t); await f.s.open(); f.change({ ...snapshot, nodes: [node, { ...node, id: 'another', body: '# External' }] });
  await f.s.handle(save(node));
  assert.equal(f.confirmations.length, 0);
  const write = f.calls.findIndex(c => c.args[0] === 'update');
  assert.equal(f.calls[write - 1].args[0], 'export');
  assert.ok(f.calls[write].args.every(a => a !== '--expect'));
});
test('same-node external changes ask before overwrite; cancellation retains current contents', async t => {
  const f = fixture(t, { confirm: false }); await f.s.open(); f.change({ ...snapshot, nodes: [{ ...node, body: '# External' }] });
  await f.s.handle(save(node)); assert.match(f.confirmations[0], /changed outside/);
  assert.equal(f.messages.at(-1).type, 'cancelled'); assert.ok(!f.calls.some(c => c.args[0] === 'update'));
  const yes = fixture(t); await yes.s.open(); yes.change({ ...snapshot, nodes: [{ ...node, body: '# External' }] });
  await yes.s.handle(save(node)); assert.ok(yes.calls.some(c => c.args[0] === 'update'));
});
test('missing original records ask confirmation and deleted edited nodes are never recreated', async t => {
  const f = fixture(t, { confirm: false }); await f.s.open(); await f.s.handle(save(undefined)); assert.equal(f.confirmations.length, 1);
  f.change({ ...snapshot, nodes: [] }); await assert.rejects(f.s.handle(save(node)), /no longer exists/);
  assert.ok(!f.calls.some(c => ['update', 'add'].includes(c.args[0])));
});
test('watcher bursts coalesce, identical data does not redraw, and changed contents do', async t => {
  const f = fixture(t); await f.s.open(); const first = f.messages.filter(m => m.type === 'snapshot').length;
  for (let i = 0; i < 50; i++) f.s.scheduleRefresh();
  await pause(25); await f.s.queue;
  assert.equal(f.calls.filter(c => c.args[0] === 'export').length, 2);
  assert.equal(f.messages.filter(m => m.type === 'snapshot').length, first);
  f.change({ ...snapshot, nodes: [{ ...node, body: '# Manual change' }] }); f.s.scheduleRefresh();
  await waitFor(() => f.messages.filter(m => m.type === 'snapshot').length === first + 1);
});
test('invalid reloads retain the last graph, disable editing, and later valid events restore it', async t => {
  const f = fixture(t); await f.s.open(); const original = f.s.snapshot; f.fail(true); f.s.scheduleRefresh();
  await waitFor(() => f.messages.at(-1).type === 'sync-error');
  assert.equal(f.s.snapshot, original); assert.equal(f.s.sourceInvalid, true);
  await assert.rejects(f.s.handle(save(node)), /YAML/); assert.ok(!f.calls.some(c => c.args[0] === 'update'));
  f.fail(false); f.s.scheduleRefresh(); await waitFor(() => f.messages.at(-1).type === 'snapshot');
  assert.equal(f.s.sourceInvalid, false);
});
test('partial writes retry a bounded number of times without a false invalid view', async t => {
  const f = fixture(t); await f.s.open(); f.failNext(2); f.s.scheduleRefresh();
  await waitFor(() => f.calls.filter(c => c.args[0] === 'export').length >= 4); await f.s.queue;
  assert.ok(!f.messages.some(m => m.type === 'sync-error'));
});
test('polling is off by default, configurable, coalesced, and cancelled on disposal', async t => {
  const f = fixture(t); await f.s.open(); assert.equal(f.s.pollTimer, undefined);
  const before = f.calls.length; await pause(25); assert.equal(f.calls.length, before);
  f.s.configurePolling(8); await waitFor(() => f.calls.length > before);
  f.s.configurePolling(0); await pause(20); await f.s.queue; const off = f.calls.length; await pause(25); assert.equal(f.calls.length, off);
  f.s.configurePolling(8); f.s.dispose(); await pause(25); assert.equal(f.calls.length, off);
  for (const value of [-1, 0.5, NaN, '10', 2_147_483_648]) assert.throws(() => pollInterval(value), /Polling interval/);
});
test('polls do not pile up behind slow reads or refresh immutable historical targets', async t => {
  const f = fixture(t, { slow: 15, revisions: ['HEAD', 'HEAD'] }); await f.s.open(); f.s.configurePolling(1);
  await pause(70); f.s.configurePolling(0); await pause(10); await f.s.queue;
  assert.ok(f.calls.filter(c => c.args[0] === 'export').length < 7);
  await f.s.chooseRevisions(); const count = f.calls.length; f.s.configurePolling(2); f.s.scheduleRefresh(); await pause(25);
  assert.equal(f.calls.length, count);
});
