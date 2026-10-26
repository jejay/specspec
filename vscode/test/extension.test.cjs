const { test } = require('node:test');
const assert = require('node:assert/strict');
const Module = require('node:module');
const { mkdtempSync, mkdirSync, rmSync, writeFileSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join, resolve } = require('node:path');

const extensionPath = require.resolve('../out/extension.js');
const snapshot = { format_version: 7, nodes: [], edges: [], valid: true };
const noopDisposable = { dispose() {} };
const lastSnapshot = panel => panel.messages.filter(m => m.type === 'snapshot').at(-1);

function fixture(t, options = {}) {
  const root = mkdtempSync(join(tmpdir(), 'specspec-extension-'));
  mkdirSync(join(root, '.specspec'));
  mkdirSync(join(root, 'vscode'));
  const uri = path => ({ scheme: 'file', fsPath: resolve(path), toString() { return this.fsPath; } });
  const calls = { commands: new Map(), errors: [], warnings: [], logs: [], cli: [], panels: [], dialogs: 0, picks: 0, watchers: [], gitWatchers: [], sessions: [], gitLookups: [], textListeners: [], saveListeners: [], closeListeners: [], edits: [], executed: [] };
  const backups = new Map();
  const context = { extensionUri: uri(join(root, 'vscode')), extensionMode: 2, subscriptions: [],
    workspaceState: { get: key => backups.get(key), keys: () => [...backups.keys()], update: async (key, value) => { value === undefined ? backups.delete(key) : backups.set(key, value); } } };
  const output = { appendLine: line => calls.logs.push(line), show() {}, dispose() {} };
  let current = options.snapshot || snapshot;
  const vscode = {
    env: { remoteName: options.remoteName },
    ExtensionMode: { Production: 1, Development: 2, Test: 3 },
    EndOfLine: { LF: 1, CRLF: 2 },
    ViewColumn: { One: 1, Active: -1 },
    Range: class { constructor(start, end) { this.start = start; this.end = end; } },
    WorkspaceEdit: class { replace(uri, range, text) { this.change = { uri, range, text }; } },
    Uri: { file: uri, joinPath: (base, ...parts) => uri(join(base.fsPath, ...parts)) },
    RelativePattern: class { constructor(base, pattern) { this.base = base; this.pattern = pattern; } },
    workspace: {
      isTrusted: options.trusted !== false,
      textDocuments: [],
      onDidChangeTextDocument: fn => { calls.textListeners.push(fn); return noopDisposable; },
      onDidSaveTextDocument: fn => { calls.saveListeners.push(fn); return noopDisposable; },
      onDidCloseTextDocument: fn => { calls.closeListeners.push(fn); return noopDisposable; },
      onWillSaveTextDocument: fn => { calls.willSave = fn; return noopDisposable; },
      applyEdit: async edit => {
        calls.edits.push(edit.change);
        const doc = vscode.workspace.textDocuments.find(d => d.uri.fsPath === edit.change.uri.fsPath);
        doc.text = doc.text.slice(0, edit.change.range.start) + edit.change.text + doc.text.slice(edit.change.range.end);
        doc.version++; doc.isDirty = true;
        calls.textListeners.forEach(fn => fn({ document: doc })); return true;
      },
      workspaceFolders: options.empty ? [] : [{ uri: uri(join(root, options.subfolder ? 'vscode' : '')) }],
      createFileSystemWatcher: pattern => {
        const watcher = { pattern, dispose() { this.disposed = true; },
          onDidChange(fn) { this.change = fn; return noopDisposable; },
          onDidCreate(fn) { this.create = fn; return noopDisposable; },
          onDidDelete(fn) { this.delete = fn; return noopDisposable; } };
        calls.watchers.push(watcher); return watcher;
      },
      onDidChangeConfiguration: fn => { calls.configure = fn; return noopDisposable; },
      getConfiguration: () => ({
        get: (name, fallback) => options.settings?.[name] ?? fallback,
        inspect: name => options.settings?.[name] !== undefined ? { globalValue: options.settings[name] } : {},
      }),
    },
    commands: { registerCommand: (name, handler) => { calls.commands.set(name, handler); return noopDisposable; },
      executeCommand: async (name, ...args) => { calls.executed.push({ name, args }); } },
    extensions: { getExtension: id => { calls.gitLookups.push(id); return undefined; } },
    window: {
      createOutputChannel: () => output,
      showOpenDialog: async () => { calls.dialogs++; return options.cancel ? undefined : [uri(root)]; },
      showWorkspaceFolderPick: async () => { calls.picks++; return undefined; },
      showErrorMessage: async message => { calls.errors.push(message); if(options.holdError)return new Promise(()=>{}); },
      showInputBox: async () => options.revisions?.shift(),
      showWarningMessage: async message => { calls.warnings.push(message); return options.confirm ? 'Confirm' : undefined; },
      registerCustomEditorProvider: (id, provider, options) => {
        assert.equal(id, 'specspec.graphEditor'); assert.equal(options.webviewOptions.retainContextWhenHidden, true);
        calls.provider = provider; return noopDisposable;
      },
      createWebviewPanel: () => {
        let listener;
        let dispose;
        const messages = [];
        const panel = {
          messages,
          send: value => listener(value),
          reveal() {},
          dispose: () => { if (dispose) { const handler = dispose; dispose = undefined; handler(); } },
          onDidDispose: handler => { dispose = handler; return noopDisposable; },
          onDidChangeViewState: handler => { panel.activate = () => handler({ webviewPanel: { active: true } }); return noopDisposable; },
          webview: {
            cspSource: 'local',
            asWebviewUri: value => value.fsPath,
            onDidReceiveMessage: handler => { listener = handler; return noopDisposable; },
            postMessage: async value => {
              messages.push(value);
              if (value.type === 'snapshot') {
                if (options.renderError) listener({ type: 'client-error', message: 'Renderer crashed' });
                else listener({ type: 'rendered', renderToken: value.renderToken, view: 'overview',
                  visibleIds: value.snapshot.nodes.map(n => n.id), nodeCount: options.wrongCount ? 999 : value.snapshot.nodes.length });
              }
              return true;
            },
            set html(value) {
              if (value.includes('SpecSpec graph unavailable')) { calls.fallbackHtml = value; return; }
              assert.match(value, /Loading specification graph/);
              assert.doesNotMatch(value, /id="project"/, 'VS Code uses its existing Select Project command instead of header chrome.');
              assert.ok(listener, 'message listener must be registered before HTML');
              listener({ type: 'ready' });
            },
          },
        };
        calls.panels.push(panel);
        return panel;
      },
    },
  };
  const invoke = async (command, prefix, selectedRoot, args, input) => {
    calls.cli.push({ command, prefix, root: selectedRoot, args, input });
    if (options.cliError) throw new Error(options.cliErrorMessage || 'Cannot run Python backend');
    if (args[0] === 'delete' && args.includes('--dry-run')) return { api_version:7,ok:true,diagnostics:options.deleteWarnings || [],result:options.deletePlan || {requested_ids:[args[1]],deleted_ids:[args[1]],nodes:[{id:args[1],path:current.nodes.find(n=>n.id===args[1]).path}],uncommitted:[],git_available:true,git_note:''} };
    if (args[0] === 'api') {
      const request = JSON.parse(input);
      if (request.op === 'annotations') return { api_version: 7, ok: true, diagnostics: [], result: { shots: options.shots || [] } };
      if (request.op === 'annotation-create') return { api_version: 7, ok: true, diagnostics: [], result: { shots: [] } };
      if (options.editError && request.edit) throw new Error('Planner temporarily unavailable');
      let overlaid = { ...current, valid: !request.target && options.invalidOverlay ? false : current.valid, nodes: current.nodes.map(n => ({ ...n, body: request.documents?.[n.path]?.split('\n---\n')[1] ?? n.body })) };
      const changes = [];
      if (request.edit) {
        const n = overlaid.nodes.find(n => n.id === request.edit.id);
        const before = request.documents[n.path];
        const after = before.slice(0, before.indexOf('\n---\n') + 5) + request.edit.body;
        changes.push({ path: n.path, before, after });
        overlaid = { ...overlaid, nodes: overlaid.nodes.map(item => item.id === n.id ? { ...item, body: request.edit.body } : item) };
      }
      return { api_version: 7, ok: true, diagnostics: [], result: { snapshot: overlaid, changes, note: '', ...(request.base ? { diff: {base:overlaid,target:overlaid,changes:[],added_edges:[],removed_edges:[],base_ref:request.base,target_ref:request.target || 'workspace',source_changes:[],source_affected:[]} } : {}) } };
    }
    return { api_version: 7, ok: true, diagnostics: [], result: current };
  };
  // Exercise the actual command and panel lifecycle without requiring Electron.
  const originalLoad = Module._load;
  delete require.cache[extensionPath];
  try {
    Module._load = function(request, parent, ...rest) {
      if (request === 'vscode') return vscode;
      if (request === './bridge' && parent?.filename === extensionPath) return { createClient: () => ({ invoke, dispose() {} }) };
      if (request === './common/host/session.cjs' && parent?.filename === extensionPath) {
        const portable = originalLoad.call(this, request, parent, ...rest);
        return { ...portable, GraphSession: class extends portable.GraphSession {
          constructor(...args) { super(...args); calls.sessions.push(this); }
        } };
      }
      if (request === './common/host/git-watch.cjs' && parent?.filename === extensionPath) {
        const portable = originalLoad.call(this, request, parent, ...rest);
        return { ...portable, GitWatcher: class extends portable.GitWatcher {
          constructor(root, changed, failed) {
            super(root, changed, failed, undefined, options.gitExecute); calls.gitWatchers.push(this);
          }
        } };
      }
      return originalLoad.call(this, request, parent, ...rest);
    };
    require(extensionPath).activate(context);
  } finally { Module._load = originalLoad; }
  t.after(() => {
    calls.panels.forEach(panel => panel.dispose()); calls.provider.dispose();
    rmSync(root, { recursive: true, force: true, maxRetries: 30, retryDelay: 100 });
    delete require.cache[extensionPath];
  });
  const openDocument = async node => {
    const doc = { uri: uri(join(root, node.path)), text: `---\nid: ${node.id}\n---\n${node.body}`, version: 1, isDirty: false, isClosed: false,
      getText() { return this.text; }, positionAt(offset) { return offset; },
      async save() { const waits = []; calls.willSave({ document: this, waitUntil: value => waits.push(value) }); await Promise.all(waits);
        this.isDirty = false; calls.saveListeners.forEach(fn => fn(this)); return true; } };
    vscode.workspace.textDocuments.push(doc); writeFileSync(doc.uri.fsPath, doc.text);
    const panel = vscode.window.createWebviewPanel(); await calls.provider.resolveCustomTextEditor(doc, panel);
    if (!calls.fallbackHtml) await waitFor(() => panel.messages.some(m => m.type === 'snapshot'));
    return { doc, panel };
  };
  return { root, uri, calls, context, workspace: vscode.workspace, openDocument, change: value => { current = value; } };
}

async function waitFor(check) {
  for (let attempt = 0; attempt < 100; attempt++) {
    if (check()) return;
    await new Promise(resolve => setTimeout(resolve, 10));
  }
  assert.ok(check(), 'The serialized graph action did not complete.');
}

test('graph refresh watches real HEAD/refs without subscribing to Git-extension status churn',async t=>{
  const {calls}=fixture(t);await calls.commands.get('specspec.openGraph')();
  assert.deepEqual(calls.gitLookups,[]);
  const before=calls.cli.length;
  calls.watchers[0].change();await waitFor(()=>calls.cli.length>before);
  assert.deepEqual(calls.gitLookups,[],'Canonical notifications retain their independent fresh-read path.');
});

test('native fallback attachment completes while its error notification awaits owner action',async t=>{
  const {calls,openDocument}=fixture(t,{snapshot:{...snapshot,valid:false},holdError:true});
  let attached=false;const opening=openDocument({id:'node',path:'.specspec/node.md',body:'# Repair'}).then(()=>{attached=true;});
  await waitFor(()=>attached);await opening;assert.ok(calls.fallbackHtml);assert.equal(calls.errors.length,1);
});

test('unsupported schema snapshots cannot invoke ordinary writes', async t => {
  const { calls } = fixture(t, { snapshot: { ...snapshot, format_version: 999 }, confirm: true });
  await calls.commands.get('specspec.openGraph')();
  calls.panels[0].send({ type: 'add', body: '# New', parents: [], sources: '[]', nodeType: 'requirement', });
  await waitFor(() => calls.panels[0].messages.at(-1).type === 'error');
  assert.match(calls.panels[0].messages.at(-1).message, /Current-format graph unavailable/);
  assert.ok(!calls.cli.some(call => call.args[0] === 'add'));
});

test('physical deletion is confirmed and retired/restore/accept messages are rejected', async t => {
  const node = { id: 'node', type: 'requirement', parents: [], sources: [], body: '# Node', path: '.specspec/node.md' };
  const { calls } = fixture(t, { snapshot: { ...snapshot, nodes: [node] }, confirm: true });
  await calls.commands.get('specspec.openGraph')();
  const count = calls.panels[0].messages.filter(message => message.type === 'snapshot').length;
  calls.panels[0].send({ type: 'delete', id: 'node' });
  await waitFor(() => calls.cli.some(call => call.args[0] === 'delete' && !call.args.includes('--dry-run')));
  await waitFor(() => calls.panels[0].messages.filter(message => message.type === 'snapshot').length > count);
  assert.deepEqual(calls.cli.filter(call => call.args[0] === 'delete').map(c=>c.args), [['delete','node','--dry-run','--json'],['delete','node','--yes','--reviewed-plan','-','--json']]);
  assert.match(calls.warnings.at(-1), /Delete only this node/);
  for (const action of ['retire', 'restore', 'accept']) {
    const errors = calls.panels[0].messages.filter(m => m.type === 'error').length;
    calls.panels[0].send({ type: action, id: 'node' });
    await waitFor(() => calls.panels[0].messages.filter(m => m.type === 'error').length > errors);
    assert.match(calls.panels[0].messages.at(-1).message, /Unknown graph action/);
    assert.ok(!calls.cli.some(call => call.args[0] === action));
  }
});

test('losing trust prevents a previously loaded graph from executing writes', async t => {
  const { calls, workspace } = fixture(t, { confirm: true });
  await calls.commands.get('specspec.openGraph')();
  workspace.isTrusted = false;
  calls.panels[0].send({ type: 'add', body: '# New', parents: [], sources: '[]', nodeType: 'requirement', });
  await waitFor(() => calls.panels[0].messages.at(-1).type === 'error');
  assert.match(calls.panels[0].messages.at(-1).message, /trust/);
  assert.ok(!calls.cli.some(call => call.args[0] === 'add'));
});

test('empty development windows use a filesystem folder picker and load the graph', async t => {
  const { root, calls } = fixture(t, { empty: true });
  const result = await calls.commands.get('specspec.openGraph')();
  assert.equal(calls.dialogs, 1);
  assert.equal(calls.picks, 0);
  assert.equal(result.format_version, 7);
  assert.equal('fingerprint' in result, false);
  assert.equal(calls.cli[0].root, root);
  assert.equal(lastSnapshot(calls.panels[0]).type, 'snapshot');
  assert.deepEqual(calls.panels[0].messages.find(m => m.type === 'annotations').shots, []);
  assert.deepEqual(calls.errors, []);
});

test('opening the extension subfolder resolves the containing project', async t => {
  const { root, calls } = fixture(t, { subfolder: true });
  await calls.commands.get('specspec.openGraph')();
  assert.equal(calls.cli[0].root, root);
  assert.equal(calls.dialogs, 0);
});

test('an explicit project URI works even without a workspace', async t => {
  const { root, uri, calls } = fixture(t, { empty: true });
  await calls.commands.get('specspec.openGraph')(uri(root));
  assert.equal(calls.dialogs, 0);
  assert.equal(calls.panels.length, 1);
});

test('cancelled project selection does not create panels or launch processes', async t => {
  const { calls } = fixture(t, { empty: true, cancel: true });
  assert.equal(await calls.commands.get('specspec.openGraph')(), undefined);
  assert.equal(calls.panels.length, 0);
  assert.equal(calls.cli.length, 0);
});

test('untrusted workspaces do not execute tools', async t => {
  const { calls } = fixture(t, { trusted: false });
  await calls.commands.get('specspec.openGraph')();
  assert.equal(calls.cli.length, 0);
  assert.equal(calls.warnings.length, 1);
});

test('startup failures are shown in a notification, the webview and output log', async t => {
  const { calls } = fixture(t, { cliError: true });
  await calls.commands.get('specspec.openGraph')();
  assert.match(calls.errors[0], /Cannot run Python backend/);
  assert.match(calls.panels[0].messages.at(-1).message, /Cannot run Python backend/);
  assert.ok(calls.logs.some(line => line.includes('Cannot run Python backend')));
});

test('renderer crashes and incomplete DOM rendering are surfaced instead of silently loading', async t => {
  const crashed = fixture(t, { renderError: true });
  assert.equal(await crashed.calls.commands.get('specspec.openGraph')(), undefined);
  assert.match(crashed.calls.errors[0], /Renderer crashed/);
  const incomplete = fixture(t, { wrongCount: true });
  assert.equal(await incomplete.calls.commands.get('specspec.openGraph')(), undefined);
  assert.match(incomplete.calls.errors[0], /expected 0/);
});

test('unsupported project URI schemes are explained instead of silently ignored', async t => {
  const { root, calls } = fixture(t);
  await calls.commands.get('specspec.openGraph')({ scheme: 'vscode-remote', fsPath: root });
  assert.match(calls.errors[0], /real filesystem on its workspace extension host/);
  assert.equal(calls.cli.length, 0);
});

test('development interpreter avoids PATH while explicit CLI settings override it', async t => {
  const old = process.env.SPECSPEC_PYTHON;
  process.env.SPECSPEC_PYTHON = 'C:/repo/.venv/Scripts/python.exe';
  t.after(() => { if (old === undefined) delete process.env.SPECSPEC_PYTHON; else process.env.SPECSPEC_PYTHON = old; });
  const automatic = fixture(t);
  await automatic.calls.commands.get('specspec.openGraph')();
  assert.equal(automatic.calls.cli[0].command, process.env.SPECSPEC_PYTHON);
  assert.deepEqual(automatic.calls.cli[0].prefix, ['-m', 'specspec']);
  const configured = fixture(t, { settings: { command: 'uvx', args: ['specspec'] } });
  await configured.calls.commands.get('specspec.openGraph')();
  assert.equal(configured.calls.cli[0].command, 'uvx');
  assert.deepEqual(configured.calls.cli[0].prefix, ['specspec']);
});


test('Open Graph creates independent main-editor panels and a shared project watcher', async t => {
  const { calls } = fixture(t);
  await calls.commands.get('specspec.openGraph')(); await calls.commands.get('specspec.openGraph')();
  assert.equal(calls.panels.length, 2); assert.equal(calls.watchers.length, 1);
  calls.panels[0].dispose(); assert.notEqual(calls.watchers[0].disposed, true);
  calls.panels[1].dispose(); await waitFor(() => calls.watchers[0].disposed);
});

test('watchers include directory replacement, refresh external changes, and polling defaults off', async t => {
  const f = fixture(t); await f.calls.commands.get('specspec.openGraph')();
  assert.equal(f.calls.watchers[0].pattern.pattern, '.specspec{,/**}');
  const count = f.calls.cli.length; await new Promise(r => setTimeout(r, 30)); assert.equal(f.calls.cli.length, count);
  f.change({ ...snapshot, nodes: [{ id: 'manual', type: 'requirement', body: '# Manually edited', parents: [], sources: [] }] });
  f.calls.watchers[0].change(); f.calls.watchers[0].create(); f.calls.watchers[0].delete();
  await waitFor(() => f.calls.panels[0].messages.at(-1).snapshot?.nodes.length === 1);
  f.calls.panels[0].dispose(); await waitFor(() => f.calls.watchers[0].disposed);
});

const nextTurn = () => new Promise(resolve => setImmediate(resolve));
const nonGit = () => Object.assign(new Error('Not a Git repository'), { code: 128 });
async function advanceClock(t, milliseconds, session) {
  t.mock.timers.tick(milliseconds); await nextTurn();
  await session.queue; await session.annotationsWork; await nextTurn();
}

test('polling setting changes take effect and disposal stops old-root timers', async t => {
  t.mock.timers.enable({ apis: ['setTimeout', 'setInterval'] });
  const settings = { pollIntervalMs: 0 }, f = fixture(t, { settings, gitExecute: async () => { throw nonGit(); } });
  await f.calls.commands.get('specspec.openGraph')();
  const session = f.calls.sessions[0];
  await f.calls.gitWatchers[0].discovery;
  const debounce = session.host.debounceMs ?? 200;
  await advanceClock(t, debounce, session); // Settle the independent startup watcher hint.
  const first = f.calls.cli.length;
  await advanceClock(t, 1000, session); assert.equal(f.calls.cli.length, first);
  settings.pollIntervalMs = 10; f.calls.configure({ affectsConfiguration: () => true });
  await advanceClock(t, 10, session); assert.ok(f.calls.cli.length > first);
  settings.pollIntervalMs = 0; f.calls.configure({ affectsConfiguration: () => true });
  await advanceClock(t, debounce, session); // Configuration itself legitimately refreshes.
  assert.equal(session.pollTimer, undefined);
  const off = f.calls.cli.length;
  await advanceClock(t, 10_000, session); assert.equal(f.calls.cli.length, off);
  settings.pollIntervalMs = 10; f.calls.configure({ affectsConfiguration: () => true }); f.calls.panels[0].dispose();
  await nextTurn(); assert.equal(session.disposed, true); // Disposal drains received native edits first.
  await advanceClock(t, 10_000, session); assert.equal(f.calls.cli.length, off);
});

test('polling off permits late initial Git discovery and subsequent file watcher refreshes', async t => {
  t.mock.timers.enable({ apis: ['setTimeout', 'setInterval'] });
  let rejectDiscovery;
  const settings = { pollIntervalMs: 0 }, f = fixture(t, { settings,
    gitExecute: () => new Promise((_, reject) => { rejectDiscovery = reject; }) });
  t.after(() => rejectDiscovery?.(nonGit()));
  await f.calls.commands.get('specspec.openGraph')();
  const session = f.calls.sessions[0], before = f.calls.cli.length;
  settings.pollIntervalMs = 10; f.calls.configure({ affectsConfiguration: () => true });
  await advanceClock(t, 10, session); assert.ok(f.calls.cli.length > before);
  settings.pollIntervalMs = 0; f.calls.configure({ affectsConfiguration: () => true });
  await advanceClock(t, 70, session);
  rejectDiscovery(nonGit()); await f.calls.gitWatchers[0].discovery; await nextTurn();
  await advanceClock(t, 190, session); const off = f.calls.cli.length;
  await advanceClock(t, 30, session);
  const late = f.calls.cli.slice(off);
  assert.equal(session.pollTimer, undefined);
  assert.deepEqual(late.map(c => JSON.parse(c.input).op), ['read'],
    'The old 260/30 ms quiet window sees a legitimate discovery refresh, not a poll.');
  const settled = f.calls.cli.length;
  await advanceClock(t, 1000, session); assert.equal(f.calls.cli.length, settled);
  f.calls.watchers[0].change();
  await advanceClock(t, session.host.debounceMs ?? 200, session);
  assert.equal(f.calls.cli.length, settled + 1, 'File watching stays active with polling disabled.');
});

test('closing a panel while initial Git discovery is pending ignores its late completion', async t => {
  t.mock.timers.enable({ apis: ['setTimeout', 'setInterval'] });
  let rejectDiscovery;
  const f = fixture(t, { gitExecute: () => new Promise((_, reject) => { rejectDiscovery = reject; }) });
  t.after(() => rejectDiscovery?.(nonGit()));
  await f.calls.commands.get('specspec.openGraph')();
  const session = f.calls.sessions[0], watcher = f.calls.gitWatchers[0], discovery = watcher.discovery;
  const before = f.calls.cli.length, messages = f.calls.panels[0].messages.length;
  f.calls.panels[0].dispose(); await nextTurn();
  assert.equal(session.disposed, true); assert.equal(watcher.closed, true);
  rejectDiscovery(nonGit()); await discovery;
  await advanceClock(t, 10_000, session);
  assert.equal(f.calls.cli.length, before); assert.equal(f.calls.panels[0].messages.length, messages);
});

test('opening a nested project creates an independent graph tab', async t => {
  const {root,uri,calls}=fixture(t);await calls.commands.get('specspec.openGraph')();
  const nested=join(root,'example/gantt');mkdirSync(join(nested,'.specspec'),{recursive:true});
  await calls.commands.get('specspec.openGraph')(uri(nested));
  assert.equal(calls.panels.length,2);assert.equal(calls.cli.at(-1).root,nested);
  await calls.commands.get('specspec.openGraph')();assert.equal(calls.cli.at(-1).root,nested);
});

test('remote workspace placement uses host-file resources, remote executable settings and opt-in timings', async t => {
  const f = fixture(t, { remoteName: 'ssh-remote', settings: { command: '/remote/venv/bin/python', args: ['-m', 'specspec'], traceLoading: true } });
  await f.calls.commands.get('specspec.openGraph')();
  assert.ok(f.calls.cli.every(c => c.command === '/remote/venv/bin/python' && c.root === f.root));
  assert.match(f.calls.logs.find(s => s.startsWith('Execution:')), /workspace host.*ssh-remote/);
  assert.ok(f.calls.logs.some(s => s.includes('first-working-render')));
  assert.equal(f.calls.panels[0].messages.find(m => m.type === 'snapshot').provisional, true);
  assert.equal(lastSnapshot(f.calls.panels[0]).provisional, undefined);
  const manifest = require('../package.json');
  assert.deepEqual(manifest.extensionKind, ['workspace']);
  assert.equal(manifest.capabilities.virtualWorkspaces.supported, false);
  assert.equal(manifest.capabilities.untrustedWorkspaces.supported, false);
});

test('native spotlight creation includes actual dirty buffers without invoking Save or managed node writes', async t => {
  const node={id:'Zm9vYmE=',type:'requirement',parents:[],body:'# Original',sources:[],path:'.specspec/Zm9vYmE=.md'};
  const f=fixture(t,{snapshot:{...snapshot,nodes:[node]}}), {doc,panel}=await f.openDocument(node);
  doc.text=doc.text.replace('# Original','# Unsaved intent'); doc.version++; doc.isDirty=true;
  f.calls.textListeners.forEach(fn=>fn({document:doc}));
  const message='Please review',nodes=[node.id];
  await panel.send({type:'annotation-create',message,nodes,documents:{'../forged':'ignored'}});
  await waitFor(()=>panel.messages.some(m=>m.type==='annotation-created'));
  const call=f.calls.cli.find(c=>c.args[0]==='api'&&JSON.parse(c.input).op==='annotation-create');
  assert.deepEqual(JSON.parse(call.input).documents,{[node.path]:doc.text});
  assert.equal(doc.isDirty,true); assert.equal(f.calls.edits.length,0);
  assert.equal(f.calls.cli.some(c=>['add','update','delete'].includes(c.args[0])),false);
  f.workspace.isTrusted=false; const count=f.calls.cli.length;
  await panel.send({type:'annotation-create',message,nodes});
  await waitFor(()=>panel.messages.some(m=>m.type==='annotation-create-error'));
  assert.equal(f.calls.cli.length,count);
});

test('external annotation shots notify all project views without reloading their graphs', async t => {
  const options = { shots: [] }, f = fixture(t, options);
  await f.calls.commands.get('specspec.openGraph')(); await f.calls.commands.get('specspec.openGraph')();
  const reads = f.calls.cli.filter(c => c.args[0] === 'api' && JSON.parse(c.input).op === 'read').length;
  const path = join(f.root, '.specspec-local', 'annotations');
  mkdirSync(path, { recursive: true });
  options.shots = [{ id: '1'.repeat(32), message:'External answer',nodes:[],comparison:{base:'HEAD',target:'workspace'},workspace:{head:null,changes:{}} }];
  writeFileSync(join(path, '1'.repeat(32) + '.json'), '{}');
  await waitFor(() => f.calls.panels.every(panel => panel.messages.some(m => m.type === 'annotations' && m.shots.length === 1)));
  assert.equal(f.calls.cli.filter(c => c.args[0] === 'api' && JSON.parse(c.input).op === 'read').length, reads);
  assert.ok(f.calls.cli.filter(c => c.args[0] === 'api' && JSON.parse(c.input).op === 'annotations').every(c => c.root === f.root));
});

const fileNode = { id: 'node', type: 'requirement', parents: [], sources: [], body: '# Original', path: '.specspec/node.md' };
test('native bootstrap supplies the first working render with one no-baseline read', async t => {
  const f = fixture(t, { snapshot: { ...snapshot, nodes: [fileNode] } });
  const { panel } = await f.openDocument(fileNode);
  await waitFor(() => panel.messages.some(m => m.type === 'snapshot' && !m.provisional));
  assert.equal(f.calls.cli.filter(c => c.args[0] === 'api' && JSON.parse(c.input).op === 'read' && !JSON.parse(c.input).base).length, 1);
  assert.equal(f.calls.cli.filter(c => c.args[0] === 'api' && JSON.parse(c.input).base).length, 1);
});
test('custom text editor binds a real document, marks edits dirty, and saves without CLI update', async t => {
  const f = fixture(t, { snapshot: { ...snapshot, nodes: [fileNode] } });
  const { doc, panel } = await f.openDocument(fileNode);
  assert.equal(lastSnapshot(panel).document.nodeId, 'node');
  assert.equal(lastSnapshot(panel).selectedId, 'node');
  panel.send({ type: 'edit', id: 'node', body: '# Native draft', parents: [], sources: '[]', documentVersion: 1, editSequence: 1 });
  await waitFor(() => doc.isDirty);
  assert.match(doc.text, /# Native draft$/); assert.equal(doc.version, 2);
  await waitFor(() => panel.messages.some(m => m.type === 'document-status'));
  panel.send({ type: 'save', id: 'node', body: '# Native draft', parents: [], sources: '[]', documentVersion: 2, editSequence: 1 });
  await waitFor(() => !doc.isDirty);
  assert.ok(!f.calls.cli.some(c => c.args[0] === 'update'));
});
test('native Delete is bound, confirmed and managed, never a retired buffer edit; dirty documents block it', async t => {
  const f = fixture(t, { snapshot: { ...snapshot, nodes: [fileNode] }, confirm: true });
  const { doc, panel } = await f.openDocument(fileNode);
  panel.send({ type: 'delete', id: 'other' });
  await waitFor(() => panel.messages.at(-1).type === 'error');
  assert.match(panel.messages.at(-1).message, /bound node/);
  doc.isDirty = true;
  const errors = panel.messages.filter(m => m.type === 'error').length;
  panel.send({ type: 'delete', id: 'node' });
  await waitFor(() => panel.messages.filter(m => m.type === 'error').length > errors);
  assert.match(panel.messages.at(-1).message, /dirty SpecSpec/);
  assert.ok(!f.calls.cli.some(c => c.args[0] === 'delete'));
  doc.isDirty = false;
  panel.send({ type: 'delete', id: 'node' });
  await waitFor(() => f.calls.cli.some(c => c.args[0] === 'delete' && !c.args.includes('--dry-run')));
  assert.deepEqual(f.calls.cli.find(c => c.args[0] === 'delete' && !c.args.includes('--dry-run')).args, ['delete', 'node', '--yes', '--reviewed-plan', '-', '--json']);
  assert.ok(!f.calls.cli.some(c => c.args[0] === 'api' && JSON.parse(c.input).edit?.retired !== undefined));
  assert.equal(doc.isDirty, false);
});
test('native exact deletion warns about the selected file and dirty descendant tabs remain protected', async t => {
  const child={...fileNode,id:'child',parents:['node'],path:'.specspec/child.md'};
  const plan={requested_ids:['node'],deleted_ids:['node'],nodes:[{id:'node',path:fileNode.path}],uncommitted:[{id:'node',path:fileNode.path,status:'M '}],git_available:true,git_note:'',broken_references:[{parent:'node',child:'child'}],potentially_affected:['child'],graph_valid:false};
  const f=fixture(t,{snapshot:{...snapshot,nodes:[fileNode,child]},deletePlan:plan,deleteWarnings:[{severity:'warning',message:'Node node has uncommitted staged changes; staging is not committing.'}]});
  const root=await f.openDocument(fileNode),leaf=await f.openDocument(child);
  root.panel.send({type:'delete',id:'node'});
  await waitFor(()=>root.panel.messages.at(-1).type==='cancelled');
  assert.match(f.calls.warnings.at(-1),/only this node.*1 Markdown/);
  assert.match(f.calls.warnings.at(-1),/Descendants and their parent declarations remain/);
  assert.match(f.calls.warnings.at(-1),/uncommitted staged.*staging is not committing/);
  assert.ok(f.calls.cli.filter(c=>c.args[0]==='delete').every(c=>c.args.includes('--dry-run')));
  const count=f.calls.cli.filter(c=>c.args[0]==='delete').length;
  leaf.doc.isDirty=true;root.panel.send({type:'delete',id:'node'});
  await waitFor(()=>root.panel.messages.at(-1).type==='error');
  assert.match(root.panel.messages.at(-1).message,/dirty SpecSpec/);
  assert.equal(f.calls.cli.filter(c=>c.args[0]==='delete').length,count);
  assert.equal(root.doc.isDirty,false);assert.equal(leaf.doc.isDirty,true);
});
test('split node views share native contents but preserve independent panels and open other node files', async t => {
  const other = { ...fileNode, id: 'other', path: '.specspec/other.md', body: '# Other' };
  const f = fixture(t, { snapshot: { ...snapshot, nodes: [fileNode, other] } });
  const { doc, panel } = await f.openDocument(fileNode);
  const split = await f.openDocument(other);
  panel.send({ type: 'edit', id: 'node', body: '# Shared', parents: [], sources: '[]', documentVersion: 1, editSequence: 1 });
  await waitFor(() => split.panel.messages.some(m => m.snapshot?.nodes.some(n => n.body === '# Shared')));
  assert.equal(split.doc.isDirty, false); assert.equal(doc.isDirty, true);
  panel.send({ type: 'open-node', id: 'other' });
  await waitFor(() => f.calls.executed.some(c => c.name === 'vscode.openWith'));
  assert.equal(f.calls.executed.at(-1).args[0].fsPath, split.doc.uri.fsPath);
  assert.equal(f.calls.executed.at(-1).args[1], 'specspec.graphEditor');
});
test('native undo/raw edits update graph views and project commands protect dirty documents', async t => {
  const f = fixture(t, { snapshot: { ...snapshot, nodes: [fileNode] } });
  const { doc, panel } = await f.openDocument(fileNode);
  doc.text = doc.text.replace('# Original', '# Raw edit'); doc.version++; doc.isDirty = true;
  f.calls.textListeners.forEach(fn => fn({ document: doc }));
  await waitFor(() => panel.messages.some(m => m.snapshot?.nodes[0]?.body === '# Raw edit'));
  await f.calls.commands.get('specspec.openGraph')();
  const projectPanel = f.calls.panels.at(-1);
  projectPanel.send({ type: 'add', nodeType: 'requirement', body: '# New', parents: [], sources: '[]' });
  await waitFor(() => projectPanel.messages.at(-1).type === 'error');
  assert.match(projectPanel.messages.at(-1).message, /dirty SpecSpec/);
  assert.ok(!f.calls.cli.some(c => c.args[0] === 'add'));
  panel.send({ type: 'undo' }); await waitFor(() => f.calls.executed.some(c => c.name === 'undo'));
});
test('node-file comparisons open an independent panel instead of rebinding the working document', async t => {
  const f = fixture(t, { snapshot: { ...snapshot, nodes: [fileNode] }, revisions: ['HEAD', 'HEAD'] });
  const { doc, panel } = await f.openDocument(fileNode);
  panel.send({ type: 'compare' });
  await waitFor(() => f.calls.panels.length === 2 && lastSnapshot(f.calls.panels[1])?.readonly);
  assert.equal(lastSnapshot(panel).readonly, false); assert.equal(doc.isDirty, false);
});
test('the manifest selects only canonical node patterns and has no Activity Bar container', () => {
  const manifest = require('../package.json');
  assert.deepEqual(manifest.contributes.customEditors[0].selector, [{ filenamePattern: '**/.specspec/???????=.md' }]);
  assert.equal(manifest.contributes.customEditors[0].priority, 'default');
  assert.equal(manifest.contributes.viewsContainers, undefined);
});
test('unapplied form input survives a closed tab/backend failure without claiming the native file is dirty', async t => {
  const f = fixture(t, { snapshot: { ...snapshot, nodes: [fileNode] }, editError: true });
  const { doc, panel } = await f.openDocument(fileNode);
  panel.send({ type: 'edit', id: 'node', body: '# Recover me', parents: [], sources: '[]', documentVersion: 1, editSequence: 1 });
  await waitFor(() => panel.messages.at(-1).type === 'error');
  assert.equal(doc.isDirty, false); assert.equal(f.context.workspaceState.keys().length, 1);
  panel.dispose(); doc.isClosed = true; await waitFor(() => f.calls.watchers[0].disposed);
  const reopened = await f.openDocument(fileNode);
  assert.equal(lastSnapshot(reopened.panel).document.recoveredForm.body, '# Recover me');
  assert.equal(reopened.doc.isDirty, false);
  reopened.panel.send({ type: 'discard-form' });
  await waitFor(() => f.context.workspaceState.keys().length === 0);
});
test('unparseable files have an escaped actionable fallback instead of a blank custom editor', async t => {
  const f = fixture(t, { cliError: true, cliErrorMessage: 'Bad <script>project text</script>' });
  const { doc } = await f.openDocument(fileNode);
  assert.match(f.calls.fallbackHtml, /Reopen Editor With/);
  assert.match(f.calls.fallbackHtml, /&lt;script&gt;project text&lt;\/script&gt;/);
  assert.ok(!f.calls.fallbackHtml.includes('<script>'));
  assert.equal(doc.isDirty, false);
});
test('commit comparisons load independently even when open-document overlays are invalid', async t => {
  const f = fixture(t, { invalidOverlay: true, revisions: ['HEAD', 'HEAD'] });
  const result = await f.calls.commands.get('specspec.compareRevisions')();
  assert.equal(result.valid, true); assert.equal(lastSnapshot(f.calls.panels[0]).readonly, true);
  assert.ok(!f.calls.cli.some(c => c.args[0] === 'api' && JSON.parse(c.input).edit));
});
