const { test } = require('node:test');
const assert = require('node:assert/strict');
const Module = require('node:module');
const { mkdtempSync, rmSync, writeFileSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join, resolve } = require('node:path');

const mainPath = require.resolve('../main.cjs');
const common = resolve(__dirname, '../../graph-ui-common');

// The real main process against a fake Electron: no build, display or installed CLI needed.
function launch(t, args) {
  const profile = mkdtempSync(join(tmpdir(), 'specspec-desktop-main-'));
  const probe = join(profile, 'probe.cjs');
  writeFileSync(probe, "console.log(JSON.stringify({api_version:7,ok:true,diagnostics:[],result:{features:['stdin-body','project-init','nested-local-state']}}))");
  const names = ['SPECSPEC_PYTHON', 'SPECSPEC_POLL_INTERVAL_MS', 'SPECSPEC_COMMAND', 'SPECSPEC_ARGS'];
  const posts = [], handlers = new Map(), saved = { argv: process.argv, env: names.map(name => [name, process.env[name]]) };
  const mainFrame = { url: 'specspec://app/index.html' };
  const webContents = { mainFrame, send: (_channel, value) => posts.push(value), on() {}, setWindowOpenHandler() {},
    session: { setPermissionRequestHandler() {}, setPermissionCheckHandler() {}, webRequest: { onBeforeRequest() {} } } };
  const electron = {
    app: { setName() {}, setPath() {}, getPath: () => profile, whenReady: () => Promise.resolve(), on() {}, quit() {} },
    BrowserWindow: class { constructor() { this.webContents = webContents; } async loadURL() {} setTitle() {} setMenu() {} on() {} isDestroyed() { return false; } },
    dialog: {}, ipcMain: { on: (channel, handler) => handlers.set(channel, handler) },
    protocol: { registerSchemesAsPrivileged() {}, handle() {} }, Menu: { setApplicationMenu() {} },
  };
  process.argv = [...process.argv.slice(0, 2), ...args];
  for (const name of names) delete process.env[name];
  Object.assign(process.env, { SPECSPEC_COMMAND: process.execPath, SPECSPEC_ARGS: JSON.stringify([probe]) });
  const load = Module._load;
  Module._load = function (request, parent, ...rest) {
    if (parent?.filename === mainPath) {
      if (request === 'electron') return electron;
      if (request === './build/media/graph-model.js') return { renderMatches: () => true, sameNode: () => false };
      if (request.startsWith('./build/common/')) return load.call(this, join(common, request.slice('./build/common/'.length)), parent, ...rest);
    }
    return load.call(this, request, parent, ...rest);
  };
  delete require.cache[mainPath];
  try { require(mainPath); } finally { Module._load = load; }
  t.after(() => {
    process.argv = saved.argv; delete require.cache[mainPath];
    for (const [name, value] of saved.env) { if (value === undefined) delete process.env[name]; else process.env[name] = value; }
    rmSync(profile, { recursive: true, force: true, maxRetries: 30, retryDelay: 100 });
  });
  const event = { sender: webContents, senderFrame: mainFrame };
  const until = async check => { for (let i = 0; i < 400 && !check(); i++) await new Promise(r => setTimeout(r, 10)); assert.ok(check()); };
  const send = value => {
    const initial = { ...event }; handlers.get('specspec:initial')(initial);
    handlers.get('specspec:message')(event, { generation: initial.returnValue.generation, value });
  };
  return { posts, send, until, profile };
}

test('an unavailable --project opens the normal startup error state, and Retry continues to project selection', async t => {
  const f = launch(t, ['--project', join(tmpdir(), 'specspec-missing-project-' + process.pid, 'nested')]);
  await f.until(() => f.posts.some(p => p.type === 'startup' && p.stage === 'error'));
  const failure = f.posts.find(p => p.stage === 'error');
  assert.match(failure.message, /--project path .*specspec-missing-project-.* is unavailable/);
  assert.deepEqual(f.posts.map(p => p.stage), ['checking', 'error'], 'The renderer shows Retry instead of a blank window.');
  f.send({ type: 'retry-startup' });
  await f.until(() => f.posts.at(-1).stage === 'select');
  assert.deepEqual(f.posts.slice(2).map(p => p.stage), ['checking', 'select']);
});

test('a form request the desktop host rejects still settles with its requestId', async t => {
  const f = launch(t, []);
  await f.until(() => f.posts.some(p => p.stage === 'select'));
  const count = f.posts.length;
  f.send({ type: 'add', requestId: 9, body: 'x'.repeat(3 * 1024 * 1024) });
  assert.deepEqual(f.posts.slice(count).map(p => [p.type, p.requestId]), [['error', 9]]);
  assert.match(f.posts.at(-1).message, /3 MiB/);
  f.send({ type: 'spawn', requestId: 'forged' }); f.send({ type: 'spawn' });
  assert.equal(f.posts.length, count + 1, 'Invalid messages without a numeric requestId stay unanswered.');
});
