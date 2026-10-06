const { test } = require('node:test');
const assert = require('node:assert/strict');
const Module = require('node:module');
const { mkdtempSync, mkdirSync, rmSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join, resolve } = require('node:path');

const extensionPath = require.resolve('../out/extension.js');
const snapshot = { fingerprint: 'current', nodes: [], edges: [], valid: true };
const noopDisposable = { dispose() {} };

function fixture(t, options = {}) {
  const root = mkdtempSync(join(tmpdir(), 'specspec-extension-'));
  mkdirSync(join(root, '_specspec'));
  mkdirSync(join(root, 'vscode'));
  const uri = path => ({ scheme: 'file', fsPath: resolve(path) });
  const calls = { commands: new Map(), errors: [], warnings: [], logs: [], cli: [], panels: [], dialogs: 0, picks: 0 };
  const context = { extensionUri: uri(join(root, 'vscode')), extensionMode: 2, subscriptions: [] };
  const output = { appendLine: line => calls.logs.push(line), show() {}, dispose() {} };
  const vscode = {
    ExtensionMode: { Production: 1, Development: 2, Test: 3 },
    ViewColumn: { One: 1 },
    Uri: { file: uri, joinPath: (base, ...parts) => uri(join(base.fsPath, ...parts)) },
    RelativePattern: class { constructor(base, pattern) { this.base = base; this.pattern = pattern; } },
    workspace: {
      isTrusted: options.trusted !== false,
      workspaceFolders: options.empty ? [] : [{ uri: uri(join(root, options.subfolder ? 'vscode' : '')) }],
      createFileSystemWatcher: () => ({ dispose() {}, onDidChange: () => noopDisposable, onDidCreate: () => noopDisposable, onDidDelete: () => noopDisposable }),
      onDidChangeConfiguration: () => noopDisposable,
      getConfiguration: () => ({
        get: (name, fallback) => options.settings?.[name] ?? fallback,
        inspect: name => options.settings?.[name] !== undefined ? { globalValue: options.settings[name] } : {},
      }),
    },
    commands: { registerCommand: (name, handler) => { calls.commands.set(name, handler); return noopDisposable; } },
    extensions: { getExtension: () => undefined },
    window: {
      createOutputChannel: () => output,
      showOpenDialog: async () => { calls.dialogs++; return options.cancel ? undefined : [uri(root)]; },
      showWorkspaceFolderPick: async () => { calls.picks++; return undefined; },
      showErrorMessage: async message => { calls.errors.push(message); },
      showWarningMessage: async message => { calls.warnings.push(message); },
      createWebviewPanel: () => {
        let listener;
        let dispose;
        const messages = [];
        const panel = {
          messages,
          reveal() {},
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
                else listener({ type: 'rendered', renderToken: value.renderToken,
                  nodeCount: options.wrongCount ? 999 : value.snapshot.nodes.length });
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
    return { api_version: 1, ok: true, diagnostics: [], result: args[0] === 'diff' ? {
      base: snapshot, target: snapshot, changes: [], added_edges: [], removed_edges: [],
      base_ref: 'HEAD', target_ref: 'workspace', source_changes: [], source_affected: [],
    } : snapshot };
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
  return { root, uri, calls, context };
}

test('empty development windows use a filesystem folder picker and load the graph', async t => {
  const { root, calls } = fixture(t, { empty: true });
  const result = await calls.commands.get('specspec.openGraph')();
  assert.equal(calls.dialogs, 1);
  assert.equal(calls.picks, 0);
  assert.equal(result.fingerprint, 'current');
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
