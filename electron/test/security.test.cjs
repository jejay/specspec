const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { mkdtempSync, readFileSync, writeFileSync, rmSync } = fs;
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
  assert.ok(validMessage({ type: 'annotation-create', message:'Owner intent', nodes:['Zm9vYmE='] }));
  assert.ok(validMessage({ type: 'annotation-select', shot:'1'.repeat(32) }));
  assert.equal(validMessage({ type: 'annotation-view', shot:'1'.repeat(32) }), false);
  for (const v of [null, [], 'save', { type: 'spawn' }, { type: 'accept' }, { type: 'save', body: 'a'.repeat(3 * 1024 * 1024) }]) assert.ok(!validMessage(v));
  const cycle = { type: 'save' }; cycle.self = cycle; assert.ok(!validMessage(cycle));
});
test('desktop removes application/window menus and retains an explicit project shortcut', () => {
  const main = readFileSync(join(__dirname, '../main.cjs'), 'utf8');
  assert.match(main, /Menu\.setApplicationMenu\(null\)/); assert.match(main, /window\.setMenu\(null\)/);
  assert.doesNotMatch(main, /buildFromTemplate|toggleDevTools|editMenu/);
  assert.match(main, /before-input-event/); assert.match(main, /input\.key\.toLowerCase\(\) === 'o'/);
  assert.ok(validMessage({ type: 'initialize', body: 'Test' })); assert.ok(validMessage({ type: 'retry-startup' }));
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
test('each window merges only its own projects, so another window keeps its saved drafts', t => {
  const dir = mkdtempSync(join(tmpdir(), 'specspec-state-')); t.after(() => rmSync(dir, { recursive: true, force: true }));
  const path = join(dir, 'state.json'), first = new PresentationStore(path), second = new PresentationStore(path);
  first.set('/root/a', { dirty: true, draft: { body: '# A' } }); first.flush();
  second.set('/root/b', { dirty: true, draft: { body: '# B' } }); second.flush();
  const restored = new PresentationStore(path);
  assert.equal(restored.get('/root/a').draft.body, '# A'); assert.equal(restored.get('/root/b').draft.body, '# B');
  assert.equal(second.get('/root/a').draft.body, '# A', 'Opening a project reads drafts another window saved.');
  first.set('/root/a', { dirty: false }); first.flush();
  assert.equal(new PresentationStore(path).get('/root/b').draft.body, '# B'); assert.equal(new PresentationStore(path).get('/root/a').dirty, false);
});
test('a failed presentation write is reported, keeps its changes and retries with the next update', t => {
  const dir = mkdtempSync(join(tmpdir(), 'specspec-state-')); t.after(() => rmSync(dir, { recursive: true, force: true }));
  const path = join(dir, 'state.json'), reports = []; let failures = 1;
  const filesystem = { ...fs, renameSync: (from, to) => {
    if (failures-- > 0) throw Object.assign(new Error('EPERM: operation not permitted, rename'), { code: 'EPERM' });
    return fs.renameSync(from, to);
  } };
  const store = new PresentationStore(path, filesystem); store.onError = message => reports.push(message);
  store.set('/root/a', { draft: '# A' }); store.save();
  assert.equal(reports.length, 1); assert.match(reports[0], /Presentation save failed: EPERM.*retry/);
  assert.deepEqual(fs.readdirSync(dir), [], 'The temporary file is removed; nothing partial remains.');
  assert.equal(store.error, undefined); assert.doesNotThrow(() => store.set('/root/b', { draft: '# B' }));
  store.flush(); assert.equal(reports.length, 1);
  const restored = new PresentationStore(path);
  assert.equal(restored.get('/root/a').draft, '# A'); assert.equal(restored.get('/root/b').draft, '# B');
});
test('oversized state is rejected without pruning a retained draft', t => {
  const dir = mkdtempSync(join(tmpdir(), 'specspec-state-')); t.after(() => rmSync(dir, { recursive: true, force: true }));
  const store = new PresentationStore(join(dir, 'state.json')); store.set('root', { draft: '# Keep' });
  assert.throws(() => store.set('other', { draft: 'a'.repeat(3 * 1024 * 1024) }), /exceeds/);
  assert.equal(store.get('root').draft, '# Keep'); store.flush();
});
