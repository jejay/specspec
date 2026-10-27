const { test } = require('node:test');
const assert = require('node:assert/strict');
const { CDP, foreground } = require('../test-host/ui.cjs');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { committedRootSibling } = require('../test-host/platform.cjs');

function connection() {
  let socket;
  class Socket extends EventTarget {
    constructor() { super(); socket = this; this.sent = []; }
    send(text) { this.sent.push(JSON.parse(text)); }
    respond(value) { this.dispatchEvent(new MessageEvent('message', { data: JSON.stringify(value) })); }
    close() { this.dispatchEvent(new Event('close')); }
  }
  const client = new CDP('ws://disposable.test', Socket);
  return { client, socket };
}
const tick = () => new Promise(resolve => setImmediate(resolve));

test('production managed calls and real-host fixture mutations use automatic stdin without body flags', () => {
  for (const path of ['../host/session.cjs', '../test-host/fixture.cjs', '../test-host/platform.cjs', '../../vscode/test-host/run.cjs'])
    assert.doesNotMatch(readFileSync(join(__dirname, path), 'utf8'), /--body/);
});

test('CDP correlates out-of-order replies and preserves the target session', async t => {
  const { client, socket } = connection(); t.after(() => client.close());
  socket.dispatchEvent(new Event('open'));
  const first = client.send('First', { a: 1 }, 'frame'), second = client.send('Second');
  await tick();
  assert.deepEqual(socket.sent[0], { id: 1, method: 'First', params: { a: 1 }, sessionId: 'frame' });
  socket.respond({ id: 2, result: { value: 'second' } });
  socket.respond({ id: 1, result: { value: 'first' } });
  assert.deepEqual(await Promise.all([first,second]), [{ value: 'first' }, { value: 'second' }]);
  assert.equal(client.pending.size, 0);
});

test('host exit promptly rejects every pending CDP operation instead of a later evaluation timeout', async () => {
  const { client, socket } = connection(); socket.dispatchEvent(new Event('open'));
  const a = client.send('Runtime.evaluate'), b = client.send('Page.captureScreenshot');
  const checks = [assert.rejects(a, /host or target exited/), assert.rejects(b, /host or target exited/)];
  await tick(); socket.close(); await Promise.all(checks);
  assert.equal(client.pending.size, 0);
  await assert.rejects(client.send('Runtime.evaluate'), /closed/);
});

test('a transport closed during startup rejects readiness too', async () => {
  const { client, socket } = connection();
  const checking = assert.rejects(client.send('Runtime.enable'), /closed/);
  socket.close(); await checking;
});

test('a send failure or transport error releases pending work without leaving timers', async () => {
  const { client, socket } = connection(); socket.dispatchEvent(new Event('open'));
  socket.send = () => { throw new Error('Socket send failed'); };
  await assert.rejects(client.send('Runtime.evaluate'), /Socket send failed/);
  assert.equal(client.pending.size, 0); client.close();
  const other = connection(); other.socket.dispatchEvent(new Event('open'));
  const checking = assert.rejects(other.client.send('Runtime.enable'), /transport failed/);
  await tick(); other.socket.dispatchEvent(new Event('error')); await checking;
  assert.equal(other.client.pending.size, 0); other.client.close();
});

test('protocol errors, JavaScript exceptions and individual request timeouts stay failures', async t => {
  const { client, socket } = connection(); t.after(() => client.close()); socket.dispatchEvent(new Event('open'));
  const protocol = assert.rejects(client.send('Bad'), /Unsupported command/);
  await tick(); socket.respond({ id: 1, error: { message: 'Unsupported command' } }); await protocol;
  const script = assert.rejects(client.evaluate({ id: 12, session: 'frame' }, 'throw new Error()'), /Literal failure/);
  await tick(); socket.respond({ id: 2, result: { exceptionDetails: { exception: { description: 'Literal failure' } } } }); await script;
  assert.deepEqual(socket.sent[1].params, { expression: 'throw new Error()', contextId: 12, returnByValue: true, awaitPromise: true });
  await assert.rejects(client.send('Runtime.evaluate', { expression: 'not answered' }, undefined, 1), /CDP timeout.*not answered/);
  assert.equal(client.pending.size, 0);
});

test('cascade fixture selects a committed outside parent even when an uncommitted root child sorts first', () => {
  const root = { id: 'root', type: 'manifesto', parents: [] };
  const modified = { id: 'modified', type: 'requirement', parents: ['root'] };
  const stable = { id: 'stable', type: 'requirement', parents: ['root'] };
  const added = { id: 'AAAAAAA=', type: 'requirement', parents: ['root'] };
  const nested = { id: 'nested', type: 'requirement', parents: ['modified'] };
  const base = { nodes: [root,modified,stable,nested] };
  const current = { nodes: [added,modified,nested,stable,root] };
  assert.equal(committedRootSibling(current,base,'root','modified'),stable);
  assert.equal(committedRootSibling({ nodes: [added,modified,root] },base,'root','modified'),undefined,'Neither an uncommitted addition nor a deleted parent can enter the next HEAD.');
});

test('foregrounding still runs when optional browser window commands are unavailable', async () => {
  const calls = [];
  await foreground({ send: async (method) => { calls.push(method); if (method.startsWith('Browser.')) throw new Error('Unsupported Browser domain'); } });
  assert.deepEqual(calls, ['Browser.getWindowForTarget','Page.bringToFront']);
});

test('supported window sizing and foregrounding are independent best-effort operations', async () => {
  const calls = [];
  await foreground({ send: async (method,params) => { calls.push([method,params]); return { windowId: 9 }; } });
  assert.deepEqual(calls, [['Browser.getWindowForTarget',undefined], ['Browser.setWindowBounds',{ windowId: 9, bounds: { windowState: 'maximized' } }], ['Page.bringToFront',undefined]]);
  await foreground({ send: async () => { throw new Error('Host exiting'); } });
});
