import * as vscode from 'vscode';
import { randomBytes } from 'node:crypto';
import { Envelope, GraphDiff, Snapshot, invoke } from './bridge';
import { findProjectRoot, resolveInvocation } from './project';
import { graphHtml } from './view';

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
  private snapshot?: Snapshot;
  private base = 'HEAD';
  private target?: string;
  private queue: Promise<void> = Promise.resolve();
  private refreshTimer?: ReturnType<typeof setTimeout>;
  private disposed = false;
  private readonly ready: Promise<void>;
  private resolveReady!: () => void;
  private renderSequence = 0;
  private lastRendered = 0;
  private expectedRenderedCount = 0;
  private renderState?: { snapshot: Snapshot; diff?: GraphDiff };
  private renderError?: Error;
  private readonly renderListeners = new Set<() => void>();

  constructor(private readonly root: vscode.Uri, private readonly context: vscode.ExtensionContext,
    private readonly output: vscode.OutputChannel) {
    this.ready = new Promise(resolve => { this.resolveReady = resolve; });
    this.panel = vscode.window.createWebviewPanel('specspec.graph', 'SpecSpec Graph', vscode.ViewColumn.One, {
      enableScripts: true,
      localResourceRoots: [vscode.Uri.joinPath(context.extensionUri, 'media')],
      retainContextWhenHidden: true,
    });
    context.subscriptions.push(this.panel);
    // Register before assigning HTML: a cached webview can send ready immediately.
    this.disposables.push(this.panel.webview.onDidReceiveMessage((message: unknown) => {
      if (message && typeof message === 'object' && (message as Record<string, unknown>).type === 'ready') {
        this.resolveReady();
        return;
      }
      if (message && typeof message === 'object') {
        const data = message as Record<string, unknown>;
        if (data.type === 'client-error' && typeof data.message === 'string') {
          this.renderError = new Error(`Graph renderer failed: ${data.message}`);
          this.output.appendLine(this.renderError.message);
          this.renderListeners.forEach(listener => listener());
          return;
        }
        if (data.type === 'rendered' && data.renderToken === this.renderSequence) {
          if (!this.renderState || !presentation.renderMatches(this.renderState, data)) {
            this.renderError = new Error(`Graph rendering is incomplete or inconsistent; expected ${this.expectedRenderedCount} known nodes in the overview or a complete selected neighborhood.`);
          } else this.lastRendered = this.renderSequence;
          this.renderListeners.forEach(listener => listener());
          return;
        }
      }
      this.enqueue(() => this.handleMessage(message));
    }));
    const watcher = vscode.workspace.createFileSystemWatcher(new vscode.RelativePattern(root, '_specspec/*'));
    this.disposables.push(watcher, watcher.onDidChange(() => this.scheduleRefresh()),
      watcher.onDidCreate(() => this.scheduleRefresh()), watcher.onDidDelete(() => this.scheduleRefresh()));
    this.disposables.push(vscode.workspace.onDidChangeConfiguration(event => {
      if (event.affectsConfiguration('specspec', root)) this.scheduleRefresh();
    }));
    this.panel.onDidDispose(() => {
      this.disposed = true;
      this.resolveReady();
      this.renderListeners.forEach(listener => listener());
      if (this.refreshTimer) clearTimeout(this.refreshTimer);
      this.disposables.forEach(item => item.dispose());
      panels.delete(root.fsPath);
    });
    this.panel.webview.html = this.html(context);
    void this.connectGit();
  }

  async open(): Promise<Snapshot> {
    this.panel.reveal();
    try {
      await this.waitUntilReady();
      await this.runSerialized(() => this.refresh());
      return this.snapshot!;
    } catch (error) {
      if (!this.disposed) await this.post({ type: 'error', message: error instanceof Error ? error.message : String(error) });
      throw error;
    }
  }

  private async waitUntilReady(): Promise<void> {
    let timer: ReturnType<typeof setTimeout> | undefined;
    try {
      await Promise.race([
        this.ready,
        new Promise<void>((_resolve, reject) => {
          timer = setTimeout(() => reject(new Error('Graph webview did not initialize. Restart the development launch and check the SpecSpec output log.')), 10_000);
        }),
      ]);
      if (this.disposed) throw new Error('Graph panel was closed before loading.');
    } finally {
      if (timer) clearTimeout(timer);
    }
  }

  private async waitForRender(token: number): Promise<void> {
    if (this.renderError) throw this.renderError;
    if (this.lastRendered === token) return;
    await new Promise<void>((resolve, reject) => {
      const finished = (error?: Error) => {
        clearTimeout(timer);
        this.renderListeners.delete(check);
        if (error) reject(error); else resolve();
      };
      const check = () => {
        if (this.disposed) finished(new Error('Graph panel was closed while rendering.'));
        else if (this.renderError) finished(this.renderError);
        else if (this.lastRendered === token) finished();
      };
      const timer = setTimeout(() => finished(new Error('Graph data loaded but the webview did not render. See the SpecSpec output log or Developer Tools.')), 10_000);
      this.renderListeners.add(check);
      check();
    });
  }

  private runSerialized<T>(operation: () => Promise<T>): Promise<T> {
    const result = this.queue.then(async () => {
      if (this.disposed) throw new Error('Graph panel is closed.');
      return operation();
    });
    this.queue = result.then(() => undefined, () => undefined);
    return result;
  }

  private enqueue(operation: () => Promise<void>): void {
    void this.runSerialized(operation).catch(async error => {
      const message = error instanceof Error ? error.message : String(error);
      this.output.appendLine(error instanceof Error ? error.stack ?? message : message);
      if (!this.disposed) await this.post({ type: 'error', message });
    });
  }

  private post(message: unknown): Thenable<boolean> {
    return this.panel.webview.postMessage(message);
  }

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

  private scheduleRefresh(): void {
    if (this.refreshTimer) clearTimeout(this.refreshTimer);
    this.refreshTimer = setTimeout(() => this.enqueue(async () => {
      await this.waitUntilReady();
      await this.refresh();
    }), 500);
  }

  private async refresh(force = false, selectedId?: string): Promise<void> {
    let diff: GraphDiff | undefined;
    let note = '';
    let diagnostics: unknown[] = [];
    let snapshot: Snapshot;
    if (this.target) {
      const response = await this.cli<GraphDiff>(['diff', '--base', this.base, '--target', this.target, '--json']);
      diff = response.result;
      snapshot = diff.target;
      diagnostics = response.diagnostics;
    } else {
      const response = await this.cli<Snapshot>(['export', '--format', 'json']);
      snapshot = response.result;
      diagnostics = response.diagnostics;
      try {
        diff = (await this.cli<GraphDiff>(['diff', '--base', this.base, '--json'])).result;
      } catch (error) {
        note = `Diff unavailable: ${error instanceof Error ? error.message : String(error)}`;
      }
    }
    this.snapshot = snapshot;
    const renderToken = ++this.renderSequence;
    this.renderError = undefined;
    this.renderState = { snapshot, diff };
    this.expectedRenderedCount = new Set([
      ...(diff?.base.nodes ?? []), ...snapshot.nodes,
    ].map(node => node.id)).size;
    await this.post({ type: 'snapshot', snapshot, diff, readonly: Boolean(this.target),
      force, selectedId, note, diagnostics, renderToken });
    await this.waitForRender(renderToken);
  }

  async chooseRevisions(): Promise<void> {
    const base = await vscode.window.showInputBox({ prompt: 'Base commit/ref', value: this.base });
    if (!base) return;
    const target = await vscode.window.showInputBox({ prompt: 'Target commit/ref (empty = workspace)', value: this.target ?? '' });
    if (target === undefined) return;
    this.enqueue(async () => {
      this.base = base;
      this.target = target || undefined;
      await this.refresh();
    });
  }

  private async handleMessage(value: unknown): Promise<void> {
    if (!value || typeof value !== 'object') throw new Error('Invalid graph message.');
    const message = value as Record<string, unknown>;
    switch (message.type) {
      case 'refresh': await this.refresh(); return;
      case 'compare': await this.chooseRevisions(); return;
      case 'workspace': this.base = 'HEAD'; this.target = undefined; await this.refresh(); return;
    }
    if (this.target) throw new Error('Historical comparisons are read-only.');
    if (!this.snapshot?.valid || typeof message.expect !== 'string') throw new Error('Load a valid graph before editing.');
    if (message.expect !== this.snapshot.fingerprint) throw new Error('Displayed graph is stale; refresh before editing. Unsaved text has been retained.');
    const common = ['--expect', message.expect, '--json'];
    if (message.type === 'migrate') {
      if (this.snapshot.format_version !== 1) throw new Error('This graph already uses the current schema.');
      const answer = await vscode.window.showWarningMessage(
        'Migrate the whole graph to remove proposed/accepted metadata? IDs, text, dependencies and withdrawal history are preserved. Review the resulting Git diff.',
        { modal: true }, 'Confirm',
      );
      if (answer !== 'Confirm') { await this.post({ type: 'cancelled' }); return; }
      await this.cli<Snapshot>(['migrate', ...common]);
      // A restored draft keeps its old fingerprint; migration is never a rebase.
      await this.refresh();
      return;
    }
    if (this.snapshot.format_version !== 2) throw new Error('Migrate this legacy graph before editing.');
    const nodes = new Map(this.snapshot.nodes.map(node => [node.id, node]));
    const id = message.id;
    if (message.type !== 'add' && (typeof id !== 'string' || !nodes.has(id))) throw new Error('Unknown node ID.');
    let args: string[];
    let input: string | undefined;
    if (message.type === 'save' || message.type === 'add') {
      if (typeof message.body !== 'string' || Buffer.byteLength(message.body, 'utf8') > 1024 * 1024) throw new Error('Invalid or oversized body.');
      if (!Array.isArray(message.parents) || message.parents.some(parent => typeof parent !== 'string' || !nodes.has(parent))) throw new Error('Invalid parent IDs.');
      const parentArgs = message.parents.flatMap(parent => ['--parent', parent as string]);
      if (message.type === 'add') {
        if (!['requirement', 'implementation'].includes(String(message.nodeType)) || typeof message.slug !== 'string') throw new Error('Invalid new-node form.');
        args = ['add', '--type', String(message.nodeType), '--slug', message.slug, ...parentArgs, '--body', '-'];
      } else {
        args = ['update', id as string, ...parentArgs, ...(parentArgs.length ? [] : ['--clear-parents']), '--body', '-'];
      }
      if (typeof message.sources !== 'string' || Buffer.byteLength(message.sources, 'utf8') > 1024 * 1024) throw new Error('Invalid source references.');
      const nodeType = message.type === 'add' ? message.nodeType : nodes.get(id as string)?.type;
      if (nodeType === 'implementation') args.push('--sources', message.sources);
      input = message.body;
    } else if (message.type === 'restore' || message.type === 'retire') {
      const answer = await vscode.window.showWarningMessage(
        `${message.type === 'restore' ? 'Restore this withdrawn node? Restoration is not approval.' : 'Retire this node, retaining its history?'} Check its dependency impact.`,
        { modal: true }, 'Confirm',
      );
      if (answer !== 'Confirm') { await this.post({ type: 'cancelled' }); return; }
      args = [message.type, id as string];
    } else throw new Error('Unknown graph action.');
    const response = await this.cli<Snapshot>([...args, ...common], input);
    const selectedId = response.result.changed_ids?.[0];
    await this.refresh(true, selectedId);
  }

  private async connectGit(): Promise<void> {
    try {
      const extension = vscode.extensions.getExtension<{ getAPI(version: number): GitAPI }>('vscode.git');
      if (!extension) return;
      const api = (extension.isActive ? extension.exports : await extension.activate()).getAPI(1);
      if (this.disposed) return;
      const subscribe = (repository: GitRepository) => {
        // Git notifications may cover a parent repository; a cheap refresh is harmless.
        this.disposables.push(repository.state.onDidChange(() => this.scheduleRefresh()));
      };
      api.repositories.forEach(subscribe);
      this.disposables.push(api.onDidOpenRepository(subscribe));
    } catch { /* Git integration is optional; file watching still works. */ }
  }

  private html(context: vscode.ExtensionContext): string {
    const webview = this.panel.webview;
    const resource = (name: string) => webview.asWebviewUri(vscode.Uri.joinPath(context.extensionUri, 'media', name));
    const nonce = randomBytes(16).toString('hex');
    return graphHtml(name => resource(name).toString(), webview.cspSource, nonce);
  }
}
