/* Local desktop host. All canonical operations remain in the shared Python bridge. */
const { app, BrowserWindow, dialog, ipcMain, protocol, Menu } = require('electron');
const { join, resolve } = require('node:path');
const { readFileSync } = require('node:fs');
const { randomBytes } = require('node:crypto');
const { APP_URL, assetName, trustedSender, validMessage, webPreferences } = require('./security.cjs');
const { PresentationStore } = require('./store.cjs');
const { resolveExecutable } = require('./launch.cjs');
const { GraphSession, pollInterval } = require('./build/common/host/session.cjs');
const { ProjectReads } = require('./build/common/host/reads.cjs');
const { GraphWatcher } = require('./build/common/host/watch.cjs');
const { GitWatcher } = require('./build/common/host/git-watch.cjs');
const { AnnotationWatcher } = require('./build/common/host/annotations.cjs');
const { invoke } = require('./build/common/host/cli.cjs');
const { findProjectRoot } = require('./build/common/host/project.cjs');
const { graphHtml } = require('./build/common/view.cjs');
const { renderMatches, sameNode } = require('./build/media/graph-model.js');

protocol.registerSchemesAsPrivileged([{ scheme: 'specspec', privileges: { standard: true, secure: true, supportFetchAPI: false } }]);
const option = name => { const i = process.argv.indexOf(name); return i < 0 ? undefined : process.argv[i + 1]; };
if (option('--profile')) app.setPath('userData', resolve(option('--profile')));
let window, root, graph, reads, store, watcher, gitWatcher, annotationWatcher, generation = randomBytes(16).toString('hex');
let selection = Promise.resolve(); const prompts = new Map();
const launchDirectory = process.cwd();
const polling = pollInterval(Number(option('--poll-interval-ms') ?? process.env.SPECSPEC_POLL_INTERVAL_MS ?? 0));
const pythonSetting = option('--python') || process.env.SPECSPEC_PYTHON;
const python = pythonSetting ? resolveExecutable(pythonSetting, launchDirectory) : undefined;
const command = python || resolveExecutable(process.env.SPECSPEC_COMMAND || 'specspec', launchDirectory);
const prefix = python ? ['-m', 'specspec'] : JSON.parse(process.env.SPECSPEC_ARGS || '[]');
if (!Array.isArray(prefix) || prefix.some(v => typeof v !== 'string')) throw new Error('SPECSPEC_ARGS must be a JSON string array.');
function post(value) { if (window && !window.isDestroyed()) window.webContents.send('specspec:host', value); }
function error(error) { console.error(error); post({ type: 'error', message: error.message || String(error) }); }
function sender(event, payload) { return window && trustedSender(event, window.webContents) && payload?.generation === generation; }
function revisions(base, target) {
  return new Promise((resolve, reject) => {
    const id = randomBytes(16).toString('hex');
    const timer = setTimeout(() => { prompts.delete(id); post({ type: 'revision-dismiss' }); reject(new Error('Revision input timed out.')); }, 120_000);
    prompts.set(id, { resolve, timer }); post({ type: 'revision-prompt', id, base, target });
  });
}
function cancelPrompts() { for (const p of prompts.values()) { clearTimeout(p.timer); p.resolve(undefined); } prompts.clear(); }

async function loadProject(next) {
  cancelPrompts();
  if (graph) { await graph.run(async () => {}); graph.dispose(); }
  reads?.dispose(); watcher?.close(); gitWatcher?.close(); annotationWatcher?.close(); store.flush(); root = next; generation = randomBytes(16).toString('hex');
  if (root) {
    const scope = root;
    const cli = async (args, input) => {
      console.log(`CLI: ${command} ${[...prefix, ...args].join(' ')}`);
      const result = await invoke(command, prefix, scope, args, input);
      if (['add', 'update', 'delete'].includes(args[0])) projectReads.changed();
      return result;
    };
    const projectReads = new ProjectReads({ cli });
    reads = projectReads;
    graph = new GraphSession({
      authorized: () => root === scope && !window.isDestroyed(),
      cli, initialGraph: () => projectReads.initial(), readGraph: (base, target) => projectReads.readGraph(base, false, target),
      post, log: text => console.log(text), renderMatches, sameNode, revisions,
      confirm: async message => (await dialog.showMessageBox(window, { type: 'warning', message,
        buttons: ['Cancel', 'Confirm'], defaultId: 0, cancelId: 0, noLink: true })).response === 1,
    });
    const session = graph;
    session.configurePolling(polling);
    const changed = () => { projectReads.changed(); session.scheduleRefresh(); };
    watcher = new GraphWatcher(scope, changed, failure => session.warn(failure));
    gitWatcher = new GitWatcher(scope, changed, failure => session.warn(failure));
    annotationWatcher = new AnnotationWatcher(scope, () => session.scheduleAnnotationsRefresh(), failure => session.annotationWarning(failure));
    window.setTitle(`SpecSpec — ${root}`);
  } else { graph = undefined; window.setTitle('SpecSpec — Open a project'); }
  await window.loadURL(APP_URL);
  if (graph) await graph.open();
  else post({ type: 'error', message: 'Choose Open project to authorize a local graph. Python CLI installation is required.' });
  if (store.error) error(new Error(store.error));
}
async function chooseProject() {
  const result = await dialog.showOpenDialog(window, { title: 'Open a SpecSpec project', properties: ['openDirectory'] });
  if (result.canceled || !result.filePaths[0]) return;
  const next = await findProjectRoot(result.filePaths[0]);
  const answer = await dialog.showMessageBox(window, { type: 'question', message: 'Trust and open this local project?',
    detail: `${next}\n\nSpecSpec will execute the configured Python CLI and can edit this managed graph. Only open projects and CLI executables you trust.`,
    buttons: ['Cancel', 'Trust and Open'], defaultId: 0, cancelId: 0, noLink: true });
  if (answer.response === 1) await loadProject(next);
}
function selectProject() { selection = selection.then(chooseProject).catch(error); }

app.whenReady().then(async () => {
  store = new PresentationStore(join(app.getPath('userData'), 'graph-presentation.json')); store.onError = message => error(new Error(message));
  protocol.handle('specspec', request => {
    const name = assetName(request.url);
    if (!name) return new Response('Not found', { status: 404 });
    if (name === 'index.html') {
      const html = graphHtml(name => `specspec://app/${name}`, 'specspec:', randomBytes(16).toString('hex'), { scope: root || '' });
      return new Response(html, { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
    }
    const mime = name.endsWith('.css') ? 'text/css' : name.endsWith('.svg') ? 'image/svg+xml' : 'text/javascript';
    return new Response(readFileSync(join(__dirname, 'build/media', name)), { headers: { 'Content-Type': `${mime}; charset=utf-8` } });
  });
  window = new BrowserWindow({ width: 1320, height: 920, minWidth: 660, minHeight: 500, title: 'SpecSpec',
    icon: join(__dirname, 'build/app-icon.png'), webPreferences: webPreferences(join(__dirname, 'preload.cjs')) });
  window.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  window.webContents.on('will-navigate', (event, url) => { if (url !== APP_URL) event.preventDefault(); });
  window.webContents.on('will-attach-webview', event => event.preventDefault());
  window.webContents.session.setPermissionRequestHandler((_contents, _permission, callback) => callback(false));
  window.webContents.session.setPermissionCheckHandler(() => false);
  window.webContents.session.webRequest.onBeforeRequest((details, callback) => callback({ cancel: !assetName(details.url) }));
  ipcMain.on('specspec:initial', event => {
    if (!trustedSender(event, window.webContents)) { event.returnValue = {}; return; }
    event.returnValue = { generation, state: root ? store.get(root) : undefined };
  });
  ipcMain.on('specspec:state', (event, payload) => {
    if (!sender(event, payload) || !root) return;
    try { store.set(root, payload.value); } catch (failure) { error(failure); }
  });
  ipcMain.on('specspec:message', (event, payload) => {
    if (!sender(event, payload) || !validMessage(payload.value)) return;
    if (payload.value.type === 'select-project') selectProject();
    else if (graph) {
      graph.receive(payload.value);
      // A normal renderer reload must receive a fresh snapshot, not wait forever.
      if (payload.value.type === 'ready' && graph.snapshot) graph.enqueue(() => graph.refresh());
    }
    else if (payload.value.type !== 'ready') error(new Error('Choose a local project first.'));
  });
  ipcMain.on('specspec:revision-result', (event, payload) => {
    if (!sender(event, payload)) return;
    const value = payload.value, p = prompts.get(value?.id);
    if (!p) return;
    const result = value.result;
    if (result !== null && (!Array.isArray(result) || result.length !== 2 || result.some(v => typeof v !== 'string' || v.length > 1024))) return;
    prompts.delete(value.id); clearTimeout(p.timer); p.resolve(result || undefined);
  });
  window.webContents.on('render-process-gone', (_event, details) => { cancelPrompts(); graph?.dispose(); console.error('Renderer exited:', details.reason); });
  window.on('closed', () => { cancelPrompts(); graph?.dispose(); reads?.dispose(); watcher?.close(); gitWatcher?.close(); annotationWatcher?.close(); try { store.flush(); } catch (failure) { console.error(failure); } });
  Menu.setApplicationMenu(Menu.buildFromTemplate([
    { label: 'Project', submenu: [{ label: 'Open project…', accelerator: 'CmdOrCtrl+O', click: selectProject },
      { label: 'Refresh graph', accelerator: 'CmdOrCtrl+R', click: () => graph?.enqueue(() => graph.refresh()) },
      { label: 'Compare revisions…', click: () => graph?.enqueue(() => graph.chooseRevisions()) }, { type: 'separator' }, { role: 'quit' }] },
    { role: 'editMenu' },
    { label: 'View', submenu: [{ role: 'togglefullscreen' }, { role: 'toggleDevTools' }] },
  ]));
  // An explicit launch path is authorization by the local launcher, not project data.
  const initial = option('--project');
  await loadProject(initial ? await findProjectRoot(resolve(initial)) : undefined);
}).catch(failure => { console.error(failure); if (window) error(failure); else app.quit(); });
app.on('window-all-closed', () => app.quit());
