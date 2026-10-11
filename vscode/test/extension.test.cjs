const { test } = require('node:test');
const assert = require('node:assert/strict');
const Module = require('node:module');
const { mkdtempSync, mkdirSync, rmSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join, resolve } = require('node:path');

const extensionPath = require.resolve('../out/extension.js');
const snapshot = { format_version: 3, nodes: [], edges: [], valid: true };
const noopDisposable = { dispose() {} };

function fixture(t, options = {}) {
  const root = mkdtempSync(join(tmpdir(), 'specspec-extension-'));
  mkdirSync(join(root, '_specspec'));
  mkdirSync(join(root, 'vscode'));
  const uri = path => ({ scheme: 'file', fsPath: resolve(path) });
  const calls = { commands: new Map(), errors: [], warnings: [], logs: [], cli: [], panels: [], dialogs: 0, picks: 0, watchers: [] };
  const context = { extensionUri: uri(join(root, 'vscode')), extensionMode: 2, subscriptions: [] };
  const output = { appendLine: line => calls.logs.push(line), show() {}, dispose() {} };
  let current = options.snapshot || snapshot;
  const vscode = {
    ExtensionMode: { Production: 1, Development: 2, Test: 3 },
    ViewColumn: { One: 1 },
    Uri: { file: uri, joinPath: (base, ...parts) => uri(join(base.fsPath, ...parts)) },
    RelativePattern: class { constructor(base, pattern) { this.base = base; this.pattern = pattern; } },
    workspace: {
      isTrusted: options.trusted !== false,
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
      executeCommand: async name => {
        assert.equal(name, 'specspec.graph.focus');
        if (!calls.panels.length) calls.provider.resolveWebviewView(vscode.window.createWebviewView());
      } },
    extensions: { getExtension: () => undefined },
    window: {
      createOutputChannel: () => output,
      showOpenDialog: async () => { calls.dialogs++; return options.cancel ? undefined : [uri(root)]; },
      showWorkspaceFolderPick: async () => { calls.picks++; return undefined; },
      showErrorMessage: async message => { calls.errors.push(message); },
      showInputBox: async () => options.revisions?.shift(),
      showWarningMessage: async message => { calls.warnings.push(message); return options.confirm ? 'Confirm' : undefined; },
      registerWebviewViewProvider: (id, provider, options) => {
        assert.equal(id, 'specspec.graph'); assert.equal(options.webviewOptions.retainContextWhenHidden, true);
        calls.provider = provider; return noopDisposable;
      },
      createWebviewView: () => {
        let listener;
        let dispose;
        const messages = [];
        const panel = {
          messages,
          send: value => listener(value),
          show() {},
          dispose: () => dispose?.(),
          onDidDispose: handler => { dispose = handler; return noopDisposable; },
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
              assert.match(value, /Loading specification graph/);
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
  const invoke = async (command, prefix, selectedRoot, args) => {
    calls.cli.push({ command, prefix, root: selectedRoot, args });
    if (options.cliError) throw new Error('Cannot run Python backend');
    if (args[0] === 'migrate') current = { ...current, format_version: 3 };
    return { api_version: 3, ok: true, diagnostics: [], result: args[0] === 'diff' ? {
      base: current, target: current, changes: [], added_edges: [], removed_edges: [],
      base_ref: 'HEAD', target_ref: 'workspace', source_changes: [], source_affected: [],
    } : current };
  };
  // Exercise the actual command and panel lifecycle without requiring Electron.
  const originalLoad = Module._load;
  delete require.cache[extensionPath];
  try {
    Module._load = function(request, parent, ...rest) {
      if (request === 'vscode') return vscode;
      if (request === './bridge' && parent?.filename === extensionPath) return { invoke };
      return originalLoad.call(this, request, parent, ...rest);
    };
    require(extensionPath).activate(context);
  } finally { Module._load = originalLoad; }
  t.after(() => {
    calls.panels.forEach(panel => panel.dispose());
    rmSync(root, { recursive: true, force: true });
    delete require.cache[extensionPath];
  });
  return { root, uri, calls, context, workspace: vscode.workspace, change: value => { current = value; } };
}

async function waitFor(check) {
  for (let attempt = 0; attempt < 100; attempt++) {
    if (check()) return;
    await new Promise(resolve => setTimeout(resolve, 10));
  }
  assert.ok(check(), 'The serialized graph action did not complete.');
}

test('legacy migration is explicitly confirmed without hash expectations', async t => {
  const { calls } = fixture(t, { snapshot: { ...snapshot, format_version: 1 }, confirm: true });
  await calls.commands.get('specspec.openGraph')();
  calls.panels[0].send({ type: 'migrate' });
  await waitFor(() => calls.panels[0].messages.at(-1).snapshot?.format_version === 3);
  const mutation = calls.cli.find(call => call.args[0] === 'migrate');
  assert.deepEqual(mutation.args, ['migrate', '--json']);
  assert.match(calls.warnings[0], /whole graph/);
  assert.equal(calls.panels[0].messages.at(-1).snapshot.format_version, 3);
  assert.equal(calls.panels[0].messages.at(-1).force, false);
});

test('cancelled migration cannot invoke a writer', async t => {
  const { calls } = fixture(t, { snapshot: { ...snapshot, format_version: 1 } });
  await calls.commands.get('specspec.openGraph')();
  calls.panels[0].send({ type: 'migrate' });
  await waitFor(() => calls.panels[0].messages.at(-1).type === 'cancelled');
  assert.ok(!calls.cli.some(call => call.args[0] === 'migrate'));
});

test('ordinary writes cannot silently migrate a legacy workspace', async t => {
  const { calls } = fixture(t, { snapshot: { ...snapshot, format_version: 1 }, confirm: true });
  await calls.commands.get('specspec.openGraph')();
  calls.panels[0].send({ type: 'add', body: '# New', parents: [], sources: '[]', nodeType: 'requirement', slug: 'new' });
  await waitFor(() => calls.panels[0].messages.at(-1).type === 'error');
  assert.match(calls.panels[0].messages.at(-1).message, /Migrate/);
  assert.ok(!calls.cli.some(call => ['add', 'migrate'].includes(call.args[0])));
});

test('withdrawal and restoration are guarded commands and acceptance messages are rejected', async t => {
  const node = { id: 'node', type: 'requirement', retired: true, parents: [], sources: [], body: '# Node', path: '_specspec/node.md' };
  const { calls } = fixture(t, { snapshot: { ...snapshot, nodes: [node] }, confirm: true });
  await calls.commands.get('specspec.openGraph')();
  for (const action of ['restore', 'retire']) {
    const count = calls.panels[0].messages.filter(message => message.type === 'snapshot').length;
    calls.panels[0].send({ type: action, id: 'node' });
    await waitFor(() => calls.panels[0].messages.filter(message => message.type === 'snapshot').length > count);
    assert.deepEqual(calls.cli.find(call => call.args[0] === action).args, [action, 'node', '--json']);
  }
  calls.panels[0].send({ type: 'accept', id: 'node' });
  await waitFor(() => calls.panels[0].messages.at(-1).type === 'error');
  assert.match(calls.panels[0].messages.at(-1).message, /Unknown graph action/);
  assert.ok(!calls.cli.some(call => call.args[0] === 'accept'));
});

test('historical legacy comparisons cannot invoke migration', async t => {
  const { calls } = fixture(t, { snapshot: { ...snapshot, format_version: 1 }, confirm: true, revisions: ['HEAD', 'HEAD'] });
  await calls.commands.get('specspec.compareRevisions')();
  await waitFor(() => calls.panels[0].messages.at(-1).readonly === true);
  calls.panels[0].send({ type: 'migrate' });
  await waitFor(() => calls.panels[0].messages.at(-1).type === 'error');
  assert.match(calls.panels[0].messages.at(-1).message, /read-only/);
  assert.ok(!calls.cli.some(call => call.args[0] === 'migrate'));
});

test('losing trust prevents a previously loaded migration from executing', async t => {
  const { calls, workspace } = fixture(t, { snapshot: { ...snapshot, format_version: 1 }, confirm: true });
  await calls.commands.get('specspec.openGraph')();
  workspace.isTrusted = false;
  calls.panels[0].send({ type: 'migrate' });
  await waitFor(() => calls.panels[0].messages.at(-1).type === 'error');
  assert.match(calls.panels[0].messages.at(-1).message, /trust/);
  assert.ok(!calls.cli.some(call => call.args[0] === 'migrate'));
});

test('empty development windows use a filesystem folder picker and load the graph', async t => {
  const { root, calls } = fixture(t, { empty: true });
  const result = await calls.commands.get('specspec.openGraph')();
  assert.equal(calls.dialogs, 1);
  assert.equal(calls.picks, 0);
  assert.equal(result.format_version, 3);
  assert.equal('fingerprint' in result, false);
  assert.equal(calls.cli[0].root, root);
  assert.equal(calls.panels[0].messages.at(-1).type, 'snapshot');
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
  assert.match(calls.errors[0], /requires a local project folder/);
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


test('Activity Bar activation auto-loads its graph without creating an editor tab', async t => {
  const {calls}=fixture(t);assert.equal(calls.panels.length,0);
  const view = { show(){}, onDidDispose(){return noopDisposable;}, webview:{options:{},cspSource:'local',asWebviewUri:v=>v.fsPath,
    onDidReceiveMessage(fn){this.listener=fn;return noopDisposable;},postMessage(value){calls.iconSnapshot=value;if(value.type==='snapshot')this.listener({type:'rendered',renderToken:value.renderToken,view:'overview',visibleIds:value.snapshot.nodes.map(n=>n.id),nodeCount:value.snapshot.nodes.length});return Promise.resolve(true);},
    set html(value){this.listener({type:'ready'});}}};
  calls.provider.resolveWebviewView(view);await waitFor(()=>calls.iconSnapshot?.type==='snapshot');
  assert.equal(calls.panels.length,0,'No createWebviewPanel/editor tab API is used.');
  calls.provider.dispose();
});

test('watchers include directory replacement, refresh external changes, and polling defaults off', async t => {
  const f = fixture(t); await f.calls.commands.get('specspec.openGraph')();
  assert.equal(f.calls.watchers[0].pattern.pattern, '_specspec{,/**}');
  const count = f.calls.cli.length; await new Promise(r => setTimeout(r, 30)); assert.equal(f.calls.cli.length, count);
  f.change({ ...snapshot, nodes: [{ id: 'manual', type: 'requirement', body: '# Manually edited', parents: [], sources: [] }] });
  f.calls.watchers[0].change(); f.calls.watchers[0].create(); f.calls.watchers[0].delete();
  await waitFor(() => f.calls.panels[0].messages.at(-1).snapshot?.nodes.length === 1);
  f.calls.panels[0].dispose(); assert.equal(f.calls.watchers[0].disposed, true);
});

test('polling setting changes take effect and disposal stops old-root timers', async t => {
  const settings = { pollIntervalMs: 0 }, f = fixture(t, { settings });
  await f.calls.commands.get('specspec.openGraph')(); const first = f.calls.cli.length;
  settings.pollIntervalMs = 10; f.calls.configure({ affectsConfiguration: () => true });
  await waitFor(() => f.calls.cli.length > first);
  settings.pollIntervalMs = 0; f.calls.configure({ affectsConfiguration: () => true });
  await new Promise(r => setTimeout(r, 260)); const off = f.calls.cli.length;
  await new Promise(r => setTimeout(r, 30)); assert.equal(f.calls.cli.length, off);
  settings.pollIntervalMs = 10; f.calls.configure({ affectsConfiguration: () => true }); f.calls.panels[0].dispose();
  await new Promise(r => setTimeout(r, 30)); assert.equal(f.calls.cli.length, off);
});

test('Select Project resolves a nested graph in the same Activity Bar view', async t => {
  const {root,uri,calls}=fixture(t);await calls.commands.get('specspec.openGraph')();
  const nested=join(root,'example/gantt');mkdirSync(join(nested,'_specspec'),{recursive:true});
  await calls.commands.get('specspec.openGraph')(uri(nested));
  assert.equal(calls.panels.length,1);assert.equal(calls.cli.at(-1).root,nested);
  await calls.commands.get('specspec.openGraph')();assert.equal(calls.cli.at(-1).root,nested);
});
