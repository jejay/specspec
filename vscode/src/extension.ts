import * as vscode from 'vscode';
import { randomBytes } from 'node:crypto';
import { Envelope, GraphDiff, Snapshot, invoke } from './bridge';
import { findProjectRoot, resolveInvocation } from './project';
import { graphHtml } from './view';

const { GraphSession } = require('./common/host/session.cjs');

const presentation: {
  renderMatches(state: { snapshot: Snapshot; diff?: GraphDiff }, message: Record<string, unknown>): boolean;
} = require('../media/graph-model.js');

interface GitRepository {
  rootUri: vscode.Uri;
  state: { onDidChange: vscode.Event<void> };
}
interface GitAPI {
  repositories: GitRepository[];
  onDidOpenRepository: vscode.Event<GitRepository>;
}

const panels = new Map<string, GraphPanel>();

export function activate(context: vscode.ExtensionContext): void {
  const output = vscode.window.createOutputChannel('SpecSpec');
  context.subscriptions.push(output);
  const open = async (compare: boolean, resource?: vscode.Uri): Promise<Snapshot | undefined> => {
    try {
      if (!vscode.workspace.isTrusted) {
        await vscode.window.showWarningMessage('Trust this workspace before executing the SpecSpec CLI.');
        return;
      }
      let selected = resource;
      if (!selected) {
        const folders = vscode.workspace.workspaceFolders ?? [];
        if (folders.length === 1) selected = folders[0].uri;
        else if (folders.length > 1) selected = (await vscode.window.showWorkspaceFolderPick({
          placeHolder: 'Select the SpecSpec project',
        }))?.uri;
        else selected = (await vscode.window.showOpenDialog({
          title: 'Select a SpecSpec project folder',
          openLabel: 'Open SpecSpec graph',
          canSelectFolders: true,
          canSelectFiles: false,
          canSelectMany: false,
          defaultUri: vscode.Uri.joinPath(context.extensionUri, '..'),
        }))?.[0];
      }
      if (!selected) { output.appendLine('Project selection cancelled.'); return; }
      if (selected.scheme !== 'file') throw new Error('The current CLI integration requires a local project folder.');
      const root = vscode.Uri.file(await findProjectRoot(selected.fsPath));
      output.appendLine(`Opening graph: ${root.fsPath}`);
      let panel = panels.get(root.fsPath);
      if (!panel) {
        panel = new GraphPanel(root, context, output);
        panels.set(root.fsPath, panel);
      }
      const snapshot = await panel.open();
      if (compare) await panel.chooseRevisions();
      return snapshot;
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      output.appendLine(error instanceof Error ? error.stack ?? message : message);
      void vscode.window.showErrorMessage(`SpecSpec: ${message}`, 'Show Log').then(action => {
        if (action === 'Show Log') output.show();
      });
      return;
    }
  };
  context.subscriptions.push(
    vscode.commands.registerCommand('specspec.openGraph', (resource?: vscode.Uri) => open(false, resource)),
    vscode.commands.registerCommand('specspec.compareRevisions', (resource?: vscode.Uri) => open(true, resource)),
  );
}

class GraphPanel {
  private readonly panel: vscode.WebviewPanel;
  private readonly disposables: vscode.Disposable[] = [];
  private readonly session: any;
  private disposed = false;

  constructor(private readonly root: vscode.Uri, private readonly context: vscode.ExtensionContext,
    private readonly output: vscode.OutputChannel) {
    this.panel = vscode.window.createWebviewPanel('specspec.graph', 'SpecSpec Graph', vscode.ViewColumn.One, {
      enableScripts: true, localResourceRoots: [vscode.Uri.joinPath(context.extensionUri, 'media')], retainContextWhenHidden: true,
    });
    context.subscriptions.push(this.panel);
    this.session = new GraphSession({
      cli: (args: string[], input?: string) => this.cli(args, input),
      authorized: () => vscode.workspace.isTrusted,
      post: (message: unknown) => this.panel.webview.postMessage(message),
      log: (message: string) => this.output.appendLine(message),
      renderMatches: presentation.renderMatches,
      confirm: async (message: string) => (await vscode.window.showWarningMessage(message, { modal: true }, 'Confirm')) === 'Confirm',
      revisions: async (base: string, target: string) => {
        const a = await vscode.window.showInputBox({ prompt: 'Base commit/ref', value: base });
        if (!a) return;
        const b = await vscode.window.showInputBox({ prompt: 'Target commit/ref (empty = workspace)', value: target });
        if (b !== undefined) return [a, b];
      },
    });
    this.disposables.push(this.panel.webview.onDidReceiveMessage(message => this.session.receive(message)));
    const watcher = vscode.workspace.createFileSystemWatcher(new vscode.RelativePattern(root, '_specspec/*'));
    this.disposables.push(watcher, watcher.onDidChange(() => this.session.scheduleRefresh()),
      watcher.onDidCreate(() => this.session.scheduleRefresh()), watcher.onDidDelete(() => this.session.scheduleRefresh()));
    this.disposables.push(vscode.workspace.onDidChangeConfiguration(event => {
      if (event.affectsConfiguration('specspec', root)) this.session.scheduleRefresh();
    }));
    this.panel.onDidDispose(() => {
      this.disposed = true; this.session.dispose(); this.disposables.forEach(d => d.dispose()); panels.delete(root.fsPath);
    });
    this.panel.webview.html = this.html(context);
    void this.connectGit();
  }
  async open(): Promise<Snapshot> { this.panel.reveal(); return this.session.open(); }
  async chooseRevisions(): Promise<void> { this.session.enqueue(() => this.session.chooseRevisions()); }
  private async cli<T>(args: string[], input?: string): Promise<Envelope<T>> {
    if (!vscode.workspace.isTrusted) throw new Error('Workspace trust is required to run SpecSpec.');
    const configuration = vscode.workspace.getConfiguration('specspec', this.root);
    const command = configuration.get<string>('command', 'specspec');
    const prefix = configuration.get<string[]>('args', []);
    if (!command || !Array.isArray(prefix) || prefix.some(arg => typeof arg !== 'string')) {
      throw new Error('Invalid SpecSpec executable configuration.');
    }
    const hasExplicitSetting = (key: string) => {
      const values = configuration.inspect(key);
      return values?.globalValue !== undefined || values?.workspaceValue !== undefined || values?.workspaceFolderValue !== undefined;
    };
    const invocation = resolveInvocation({ command, args: prefix },
      this.context.extensionMode !== vscode.ExtensionMode.Production ? process.env.SPECSPEC_PYTHON : undefined,
      hasExplicitSetting('command') || hasExplicitSetting('args'));
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
        // Git notifications may cover a parent repository; a cheap refresh is harmless.
        this.disposables.push(repository.state.onDidChange(() => this.session.scheduleRefresh()));
      };
      api.repositories.forEach(subscribe);
      this.disposables.push(api.onDidOpenRepository(subscribe));
    } catch { /* Git integration is optional; file watching still works. */ }
  }

  private html(context: vscode.ExtensionContext): string {
    const webview = this.panel.webview;
    const resource = (name: string) => webview.asWebviewUri(vscode.Uri.joinPath(context.extensionUri, 'media', name)).toString();
    return graphHtml(resource, webview.cspSource, randomBytes(16).toString('hex'), { scope: this.root.fsPath });
  }
}
