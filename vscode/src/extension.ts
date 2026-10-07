import * as vscode from 'vscode';
import { randomBytes } from 'node:crypto';
import { Envelope, Snapshot, invoke } from './bridge';
import { findProjectRoot, resolveInvocation } from './project';
import { graphHtml } from './view';
const { GraphSession } = require('./common/host/session.cjs');
const presentation = require('../media/graph-model.js');

interface GitRepository { state: { onDidChange: vscode.Event<void> }; }
interface GitAPI { repositories: GitRepository[]; onDidOpenRepository: vscode.Event<GitRepository>; }

export function activate(context: vscode.ExtensionContext): void {
  const output = vscode.window.createOutputChannel('SpecSpec');
  const provider = new GraphViewProvider(context, output);
  context.subscriptions.push(output, provider,
    vscode.window.registerWebviewViewProvider('specspec.graph', provider, { webviewOptions: { retainContextWhenHidden: true } }),
    vscode.commands.registerCommand('specspec.openGraph', (resource?: vscode.Uri) => provider.open(resource)),
    vscode.commands.registerCommand('specspec.compareRevisions', (resource?: vscode.Uri) => provider.open(resource, true)),
    vscode.commands.registerCommand('specspec.selectProject', () => provider.open(undefined, false, true)));
}

class GraphViewProvider implements vscode.WebviewViewProvider, vscode.Disposable {
  private view?: vscode.WebviewView;
  private graph?: GraphHost;
  private lastRoot?: vscode.Uri;
  private queue: Promise<unknown> = Promise.resolve();
  private pendingOpens = 0;
  private readonly waiters = new Set<() => void>();
  constructor(private context: vscode.ExtensionContext, private output: vscode.OutputChannel) {}

  resolveWebviewView(view: vscode.WebviewView): void {
    this.view = view;
    view.webview.options = { enableScripts: true, localResourceRoots: [vscode.Uri.joinPath(this.context.extensionUri, 'media')] };
    view.onDidDispose(() => { this.graph?.dispose(); this.graph = undefined; this.view = undefined; });
    this.waiters.forEach(f => f());
    // Direct icon activation opens the same path as the command. No parallel initial session.
    if (!this.pendingOpens) void this.open(this.lastRoot);
  }

  open(resource?: vscode.Uri, compare = false, selectFolder = false): Promise<Snapshot | undefined> {
    this.pendingOpens++;
    const result = this.queue.then(() => this.openImpl(resource, compare, selectFolder)).finally(() => { this.pendingOpens--; });
    this.queue = result.catch(() => {}); return result;
  }

  private async openImpl(resource?: vscode.Uri, compare = false, selectFolder = false): Promise<Snapshot | undefined> {
    try {
      if (!vscode.workspace.isTrusted) { await vscode.window.showWarningMessage('Trust this workspace before executing the SpecSpec CLI.'); return; }
      let selected = resource;
      if (!selected && !selectFolder && this.graph) selected = this.graph.root;
      if (!selected && !selectFolder) {
        const folders = vscode.workspace.workspaceFolders ?? [];
        if (folders.length === 1) selected = folders[0].uri;
        else if (folders.length > 1) selected = (await vscode.window.showWorkspaceFolderPick({ placeHolder: 'Select the SpecSpec project' }))?.uri;
      }
      if (!selected && (selectFolder || !(vscode.workspace.workspaceFolders?.length))) selected = (await vscode.window.showOpenDialog({
        title: 'Select a SpecSpec project folder', openLabel: 'Open SpecSpec graph', canSelectFolders: true,
        canSelectFiles: false, canSelectMany: false, defaultUri: this.lastRoot || vscode.Uri.joinPath(this.context.extensionUri, '..'),
      }))?.[0];
      if (!selected) { this.output.appendLine('Project selection cancelled.'); return; }
      if (selected.scheme !== 'file') throw new Error('The current CLI integration requires a local project folder.');
      const root = vscode.Uri.file(await findProjectRoot(selected.fsPath));
      this.output.appendLine(`Opening graph: ${root.fsPath}`);
      if (!this.view) { await vscode.commands.executeCommand('specspec.graph.focus'); await this.waitForView(); }
      if (!this.graph || this.graph.root.fsPath !== root.fsPath) {
        // Finish a pending authorized old-root operation before replacing the adapter.
        if (this.graph) { await this.graph.idle(); this.graph.dispose(); }
        this.lastRoot = root;
        this.graph = new GraphHost(root, this.view!, this.context, this.output, () => { void this.open(undefined, false, true); });
      }
      this.view!.description = root.fsPath; this.view!.show(false);
      const snapshot = await this.graph.open();
      if (compare) this.graph.chooseRevisions();
      return snapshot;
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      this.output.appendLine(error instanceof Error ? error.stack || message : message);
      await vscode.window.showErrorMessage(`SpecSpec: ${message}`, 'Show Log').then(action => { if (action === 'Show Log') this.output.show(); });
      return;
    }
  }
  private async waitForView(): Promise<void> {
    if (this.view) return;
    await new Promise<void>((resolve, reject) => {
      const check = () => { if (this.view) { clearTimeout(timer); this.waiters.delete(check); resolve(); } };
      const timer = setTimeout(() => { this.waiters.delete(check); reject(new Error('SpecSpec Activity Bar view did not open.')); }, 10_000);
      this.waiters.add(check); check();
    });
  }
  dispose(): void { this.graph?.dispose(); }
}

class GraphHost {
  private readonly disposables: vscode.Disposable[] = [];
  private readonly session: any;
  private disposed = false;
  constructor(readonly root: vscode.Uri, private panel: vscode.WebviewView,
    private context: vscode.ExtensionContext, private output: vscode.OutputChannel, selectProject: () => void) {
    this.session = new GraphSession({
      cli: (args: string[], input?: string) => this.cli(args, input), authorized: () => vscode.workspace.isTrusted,
      post: (message: unknown) => this.panel.webview.postMessage(message), log: (message: string) => this.output.appendLine(message),
      renderMatches: presentation.renderMatches,
      confirm: async (message: string) => (await vscode.window.showWarningMessage(message, { modal: true }, 'Confirm')) === 'Confirm',
      revisions: async (base: string, target: string) => {
        const a = await vscode.window.showInputBox({ prompt: 'Base commit/ref', value: base }); if (!a) return;
        const b = await vscode.window.showInputBox({ prompt: 'Target commit/ref (empty = workspace)', value: target });
        if (b !== undefined) return [a, b];
      },
    });
    this.disposables.push(panel.webview.onDidReceiveMessage(message => {
      if (message?.type === 'select-project') selectProject(); else this.session.receive(message);
    }));
    const watcher = vscode.workspace.createFileSystemWatcher(new vscode.RelativePattern(root, '_specspec/*'));
    this.disposables.push(watcher, watcher.onDidChange(() => this.session.scheduleRefresh()),
      watcher.onDidCreate(() => this.session.scheduleRefresh()), watcher.onDidDelete(() => this.session.scheduleRefresh()));
    this.disposables.push(vscode.workspace.onDidChangeConfiguration(event => {
      if (event.affectsConfiguration('specspec', root)) this.session.scheduleRefresh();
    }));
    const resource = (name: string) => panel.webview.asWebviewUri(vscode.Uri.joinPath(context.extensionUri, 'media', name)).toString();
    panel.webview.html = graphHtml(resource, panel.webview.cspSource, randomBytes(16).toString('hex'), { scope: root.fsPath });
    void this.connectGit();
  }
  open(): Promise<Snapshot> { return this.session.open(); }
  idle(): Promise<void> { return this.session.run(async () => {}); }
  chooseRevisions(): void { this.session.enqueue(() => this.session.chooseRevisions()); }
  dispose(): void { this.disposed = true; this.session.dispose(); this.disposables.forEach(d => d.dispose()); }

  private async cli<T>(args: string[], input?: string): Promise<Envelope<T>> {
    if (!vscode.workspace.isTrusted) throw new Error('Workspace trust is required to run SpecSpec.');
    const configuration = vscode.workspace.getConfiguration('specspec', this.root);
    const command = configuration.get<string>('command', 'specspec');
    const prefix = configuration.get<string[]>('args', []);
    if (!command || !Array.isArray(prefix) || prefix.some(arg => typeof arg !== 'string')) throw new Error('Invalid SpecSpec executable configuration.');
    const explicit = (key: string) => {
      const values = configuration.inspect(key);
      return values?.globalValue !== undefined || values?.workspaceValue !== undefined || values?.workspaceFolderValue !== undefined;
    };
    const invocation = resolveInvocation({ command, args: prefix },
      this.context.extensionMode !== vscode.ExtensionMode.Production ? process.env.SPECSPEC_PYTHON : undefined,
      explicit('command') || explicit('args'));
    this.output.appendLine(`CLI: ${invocation.command} ${[...invocation.args, ...args].join(' ')}`);
    return invoke<T>(invocation.command, invocation.args, this.root.fsPath, args, input);
  }

  private async connectGit(): Promise<void> {
    try {
      const extension = vscode.extensions.getExtension<{ getAPI(version: number): GitAPI }>('vscode.git');
      if (!extension) return;
      const api = (extension.isActive ? extension.exports : await extension.activate()).getAPI(1);
      if (this.disposed) return;
      const subscribe = (repository: GitRepository) => {
        this.disposables.push(repository.state.onDidChange(() => this.session.scheduleRefresh()));
      };
      api.repositories.forEach(subscribe);
      this.disposables.push(api.onDidOpenRepository(subscribe));
    } catch { /* Git notifications are optional; canonical-file watching still works. */ }
  }
}
