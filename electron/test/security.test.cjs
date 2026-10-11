const { test } = require('node:test');
const assert = require('node:assert/strict');
const { mkdtempSync, readFileSync, writeFileSync, rmSync } = require('node:fs');
const { join } = require('node:path');
const { tmpdir } = require('node:os');
const { APP_URL, assetName, trustedSender, validMessage, webPreferences } = require('../security.cjs');
const { PresentationStore } = require('../store.cjs');

test('fixed protocol assets reject traversal, remote hosts and arbitrary project files', () => {
  assert.equal(assetName(APP_URL), 'index.html');
  assert.equal(assetName('specspec://app/vendor/graph-vendor.js'), 'vendor/graph-vendor.js');
  for (const value of ['https://app/graph.js', 'file:///secret', 'specspec://other/graph.js', 'specspec://app/../../secret',
    'specspec://app/%2e%2e%2fsecret', 'specspec://user@app/graph.js', 'specspec://app:42/graph.js', 'specspec://app/package.json']) assert.equal(assetName(value), undefined);
});
test('only the owning app main frame may use IPC', () => {
  const contents = { mainFrame: { url: APP_URL } };
  assert.ok(trustedSender({ sender: contents, senderFrame: contents.mainFrame }, contents));
  assert.ok(!trustedSender({ sender: {}, senderFrame: contents.mainFrame }, contents));
  assert.ok(!trustedSender({ sender: contents, senderFrame: { url: APP_URL } }, contents));
  contents.mainFrame.url = 'https://example.com';
  assert.ok(!trustedSender({ sender: contents, senderFrame: contents.mainFrame }, contents));
});
test('sandbox defaults and narrow bounded commands never expose arbitrary CLI/spawn', () => {
  assert.deepEqual(webPreferences('fixed'), { preload: 'fixed', contextIsolation: true, sandbox: true,
    nodeIntegration: false, webSecurity: true, allowRunningInsecureContent: false });
  assert.ok(validMessage({ type: 'save', body: '# Literal' }));
  for (const v of [null, [], 'save', { type: 'spawn' }, { type: 'accept' }, { type: 'save', body: 'a'.repeat(3 * 1024 * 1024) }]) assert.ok(!validMessage(v));
  const cycle = { type: 'save' }; cycle.self = cycle; assert.ok(!validMessage(cycle));
});
test('project-scoped persisted native drafts retain original contents independently', t => {
  const dir = mkdtempSync(join(tmpdir(), 'specspec-state-')); t.after(() => rmSync(dir, { recursive: true, force: true }));
  const path = join(dir, 'state.json'), store = new PresentationStore(path);
  store.set('/root/a', { dirty: true, originalNode: { body: '# Original A' }, draft: { body: '# A' } });
  store.set('/root/b', { dirty: true, originalNode: { body: '# Original B' }, draft: { body: '# B' } }); store.flush();
  const restored = new PresentationStore(path);
  assert.equal(restored.get('/root/a').originalNode.body, '# Original A'); assert.equal(restored.get('/root/b').draft.body, '# B');
  assert.equal(restored.get('/unknown'), undefined);
});
test('malformed presentation bytes remain protected rather than overwritten', t => {
  const dir = mkdtempSync(join(tmpdir(), 'specspec-state-')); t.after(() => rmSync(dir, { recursive: true, force: true }));
  const path = join(dir, 'state.json'); writeFileSync(path, '{bad original');
  const store = new PresentationStore(path); assert.match(store.error, /protected/);
  assert.throws(() => store.set('/root', { dirty: true }), /protected/); store.flush();
  assert.equal(readFileSync(path, 'utf8'), '{bad original');
});
test('oversized state is rejected without pruning a retained draft', t => {
  const dir = mkdtempSync(join(tmpdir(), 'specspec-state-')); t.after(() => rmSync(dir, { recursive: true, force: true }));
  const store = new PresentationStore(join(dir, 'state.json')); store.set('root', { draft: '# Keep' });
  assert.throws(() => store.set('other', { draft: 'a'.repeat(3 * 1024 * 1024) }), /exceeds/);
  assert.equal(store.get('root').draft, '# Keep'); store.flush();
});
