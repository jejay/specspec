import * as vscode from 'vscode';
import { randomBytes } from 'node:crypto';
import { relative, sep } from 'node:path';
import { Envelope, Snapshot, SpecNode, createClient } from './bridge';
import { findProjectRoot, resolveInvocation } from './project';
import { graphHtml } from './view';
const { GraphSession } = require('./common/host/session.cjs');
const { ProjectDocuments } = require('./common/host/documents.cjs');
const { GitWatcher } = require('./common/host/git-watch.cjs');
const { AnnotationWatcher } = require('./common/host/annotations.cjs');
const { probeCli, inspectProject } = require('./common/host/startup.cjs');
const presentation = require('../media/graph-model.js');

const VIEW_TYPE = 'specspec.graphEditor';
interface DocumentState { path: string; text: string; version: number; dirty: boolean; closed: boolean; eol: string; }
interface FormEdit { id: string; body: string; parents: string[]; sources: string; editSequence: number; documentVersion?: number; }
interface FormRecovery { key: string; form: FormEdit; }

export function activate(context: vscode.ExtensionContext): void {
  const output = vscode.window.createOutputChannel('specspec');
  const editors = new GraphEditors(context, output);
  context.subscriptions.push(output, editors,
    vscode.window.registerCustomEditorProvider(VIEW_TYPE, editors, { webviewOptions: { retainContextWhenHidden: true } }),
    vscode.commands.registerCommand('specspec.openGraph', (resource?: vscode.Uri) => editors.open(resource)),
    vscode.commands.registerCommand('specspec.compareRevisions', (resource?: vscode.Uri) => editors.open(resource, true)),
    vscode.commands.registerCommand('specspec.selectProject', () => editors.open(undefined, false, true)));
}

class GraphEditors implements vscode.CustomTextEditorProvider, vscode.Disposable {
  private readonly projects = new Map<string, GraphProject>();
  private readonly views = new Set<GraphView>();
  private lastRoot?: vscode.Uri;
  private disposed = false;
  private readonly disposables: vscode.Disposable[];
  constructor(private context: vscode.ExtensionContext, private output: vscode.OutputChannel) {
    this.disposables = [vscode.workspace.onDidChangeTextDocument(event => this.documentChanged(event.document)),
      vscode.workspace.onDidSaveTextDocument(document => this.documentChanged(document)),
      vscode.workspace.onDidCloseTextDocument(document => this.documentChanged(document)),
      vscode.workspace.onWillSaveTextDocument(event => {
        // Drain form edits already received before a native save. This is not a
        // schema veto or a replacement for VS Code's persistence/backup model.
        const views = [...this.views].filter(view => view.document === event.document);
        if (views.length) event.waitUntil(Promise.all(views.map(view => view.flushDocument())).then(() => []));
      })];
  }
  private documentChanged(document: vscode.TextDocument): void {
    for (const project of this.projects.values()) if (project.documentPath(document)) project.documents.changed();
  }
  private async project(resource: vscode.Uri): Promise<GraphProject> {
    if (!vscode.workspace.isTrusted) throw new Error('Trust this workspace before executing the specspec CLI.');
    if (resource.scheme !== 'file') throw new Error('specspec requires a real filesystem on its workspace extension host. Install it in the connected remote window; virtual/client-local resources are unavailable here.');
    const started = Date.now();
    const root = vscode.Uri.file(await findProjectRoot(resource.fsPath));
    if (this.disposed) throw new Error('specspec editors are closed.');
    const key = process.platform === 'win32' ? root.fsPath.toLowerCase() : root.fsPath;
    let project = this.projects.get(key);
    if (!project) {
      project = new GraphProject(root, this.context, this.output); this.projects.set(key, project);
    }
    project.trace('discovery-and-watch-setup', Date.now() - started);
    this.lastRoot = root; return project;
  }
  private attach(project: GraphProject, panel: vscode.WebviewPanel, document?: vscode.TextDocument, node?: SpecNode, recovery?: FormRecovery, bootstrap?: any): GraphView {
    const view = new GraphView(project, panel, this.context, this.output, document, node, recovery, bootstrap,
      () => { void this.open(undefined, false, true); }, () => { void this.open(project.root, true); });
    this.views.add(view); project.references++;
    panel.onDidChangeViewState(event => { if (event.webviewPanel.active) this.lastRoot = project.root; });
    panel.onDidDispose(() => {
      this.views.delete(view); project.references--;
      // Already-received document edits finish before releasing their project.
      void view.flushDocument().finally(() => {
        view.dispose();
        if (!project.references) { project.dispose(); for (const [key, value] of this.projects) if (value === project) this.projects.delete(key); }
      });
    });
    return view;
  }
  async resolveCustomTextEditor(document: vscode.TextDocument, panel: vscode.WebviewPanel): Promise<void> {
    try {
      const project = await this.project(document.uri);
      const path = project.documentPath(document);
      if (!path) throw new Error('Only direct canonical .specspec node files can use the graph editor.');
      await project.probe();
      const bootstrap = await project.documents.bootstrap();
      const node: SpecNode | undefined = bootstrap.result.snapshot.nodes.find((item: SpecNode) => item.path === path);
      if (!node) throw new Error('Node Markdown needs repair. Reopen with Text Editor.');
      const prefix = `specspec.pendingForm:${document.uri.toString()}:`;
      const active = new Set([...this.views].map(view => view.recoveryKey));
      const key = this.context.workspaceState.keys().find(key => key.startsWith(prefix) && !active.has(key));
      const form = key ? this.context.workspaceState.get<FormEdit>(key) : undefined;
      const recovery = key && form && form.id === node.id && typeof form.body === 'string' && typeof form.sources === 'string'
        && Array.isArray(form.parents) && form.parents.every(p => typeof p === 'string') ? { key, form } : undefined;
      const view = this.attach(project, panel, document, node, recovery, bootstrap);
      // VS Code completes custom-editor wiring after resolve returns. Awaiting a
      // webview render acknowledgement here can deadlock that lifecycle.
      void view.open().catch(error => this.report(error, document.uri));
    } catch (error) {
      const text = (error instanceof Error ? error.message : String(error)).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' })[c]!);
      const missing = error instanceof Error && 'code' in error && error.code === 'CLI_UNAVAILABLE';
      panel.webview.html = `<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'"><style>body{font-family:system-ui;padding:10vh 8vw}h1{font-size:36px}pre{white-space:pre-wrap}</style></head><body><h1>${missing ? 'Install the specspec CLI' : 'specspec graph unavailable'}</h1>${missing ? '<p>Install specspec from PyPI with uv or pipx on this workspace host, then reopen the graph.</p><pre>uv tool install specspec</pre>' : ''}<pre>${text}</pre><p>Use Reopen Editor With → Text Editor to repair or copy the Markdown.</p></body></html>`;
      void this.report(error, document.uri).catch(failure => this.output.appendLine(String(failure)));
    }
  }
  async open(resource?: vscode.Uri, compare = false, selectFolder = false): Promise<Snapshot | undefined> {
    try {
      if (!vscode.workspace.isTrusted) { await vscode.window.showWarningMessage('Trust this workspace before executing the specspec CLI.'); return; }
      let selected = resource;
      if (!selected && !selectFolder) selected = this.lastRoot;
      if (!selected && !selectFolder) {
        const folders = vscode.workspace.workspaceFolders ?? [];
        if (folders.length === 1) selected = folders[0].uri;
        else if (folders.length > 1) selected = (await vscode.window.showWorkspaceFolderPick({ placeHolder: 'Select the specspec project' }))?.uri;
      }
      if (!selected && (selectFolder || !(vscode.workspace.workspaceFolders?.length))) selected = (await vscode.window.showOpenDialog({
        title: 'Select a specspec project folder', openLabel: 'Open specspec graph', canSelectFolders: true,
        canSelectFiles: false, canSelectMany: false, defaultUri: this.lastRoot || vscode.Uri.joinPath(this.context.extensionUri, '..'),
      }))?.[0];
      if (!selected) { this.output.appendLine('Project selection cancelled.'); return; }
      const project = await this.project(selected);
      const panel = vscode.window.createWebviewPanel('specspec.projectGraph', 'specspec Graph', vscode.ViewColumn.Active,
        { enableScripts: true, retainContextWhenHidden: true, localResourceRoots: [vscode.Uri.joinPath(this.context.extensionUri, 'media')] });
      const view = this.attach(project, panel);
      // A commit comparison must also open when dirty workspace buffers are invalid.
      if (compare) { await view.chooseRevisions(); if (view.snapshot) return view.snapshot; }
      return await view.open();
    } catch (error) { await this.report(error); return; }
  }
  private async report(error: unknown, resource?: vscode.Uri): Promise<void> {
    const message = error instanceof Error ? error.message : String(error);
    this.output.appendLine(error instanceof Error ? error.stack || message : message);
    const action = await vscode.window.showErrorMessage(`specspec: ${message}`, ...(resource ? ['Open Markdown'] : []), 'Show Log');
    if (action === 'Show Log') this.output.show();
    if (action === 'Open Markdown' && resource) await vscode.commands.executeCommand('vscode.openWith', resource, 'default');
  }
  dispose(): void {
    this.disposed = true; this.disposables.forEach(d => d.dispose());
    this.views.forEach(view => view.dispose()); this.projects.forEach(project => project.dispose());
  }
}

class GraphProject implements vscode.Disposable {
  readonly documents: any;
  references = 0;
  private readonly annotationListeners = new Set<(error?: Error) => void>();
  private readonly disposables: vscode.Disposable[] = [];
  private readonly cliClient = createClient();
  private verifiedInvocation?: string;
  constructor(readonly root: vscode.Uri, private context: vscode.ExtensionContext, private output: vscode.OutputChannel) {
    this.documents = new ProjectDocuments({
      documents: () => vscode.workspace.textDocuments.filter(d => this.documentPath(d)).map(d => this.documentState(d)),
      cli: (args: string[], input?: string) => this.cli(args, input),
      confirm: async (message: string) => (await vscode.window.showWarningMessage(message, { modal: true }, 'Confirm')) === 'Confirm',
    });
    const watcher = vscode.workspace.createFileSystemWatcher(new vscode.RelativePattern(root, '.specspec{,/**}'));
    const canonicalChanged = (resource?: vscode.Uri) => {
      const path = resource ? relative(root.fsPath, resource.fsPath).split(sep).join('/') : '';
      if (path !== '.specspec/local' && !path.startsWith('.specspec/local/')) this.documents.changed();
    };
    this.disposables.push(watcher, watcher.onDidChange(canonicalChanged),
      watcher.onDidCreate(canonicalChanged), watcher.onDidDelete(canonicalChanged));
    this.disposables.push(vscode.workspace.onDidChangeConfiguration(event => {
      if (event.affectsConfiguration('specspec', root)) this.documents.changed();
    }));
    const gitWatcher = new GitWatcher(root.fsPath, () => this.documents.changed(), (error: Error) => this.output.appendLine(error.message));
    this.disposables.push({ dispose: () => gitWatcher.close() });
    const annotationWatcher = new AnnotationWatcher(root.fsPath,
      () => this.annotationListeners.forEach(listener => listener()),
      (error: Error) => { this.output.appendLine(error.message); this.annotationListeners.forEach(listener => listener(error)); });
    this.disposables.push({ dispose: () => annotationWatcher.close() });
    this.output.appendLine(`Execution: workspace host (${vscode.env?.remoteName || 'local'}); install Python/Git and configure specspec on this host.`);
  }
  subscribeAnnotations(listener: (error?: Error) => void): vscode.Disposable {
    this.annotationListeners.add(listener);
    return { dispose: () => { this.annotationListeners.delete(listener); } };
  }
  trace(phase: string, durationMs: number, nodes?: number): void {
    if (vscode.workspace.getConfiguration('specspec', this.root).get<boolean>('traceLoading', false))
      this.output.appendLine(`Loading ${JSON.stringify({ phase, durationMs, ...(nodes === undefined ? {} : { nodes }) })}`);
  }
  documentPath(document: vscode.TextDocument): string | undefined {
    if (document.uri.scheme !== 'file') return;
    const path = relative(this.root.fsPath, document.uri.fsPath).split(sep).join('/');
    if (/^\.specspec\/[^/]+\.md$/.test(path)) return path;
  }
  documentState(document: vscode.TextDocument): DocumentState {
    return { path: this.documentPath(document)!, text: document.getText(), version: document.version, dirty: document.isDirty,
      closed: document.isClosed, eol: document.eol === vscode.EndOfLine.CRLF ? '\r\n' : '\n' };
  }
  private invocation() {
    if (!vscode.workspace.isTrusted) throw new Error('Workspace trust is required to run specspec.');
    const configuration = vscode.workspace.getConfiguration('specspec', this.root);
    const command = configuration.get<string>('command', 'specspec');
    const prefix = configuration.get<string[]>('args', []);
    if (!command || !Array.isArray(prefix) || prefix.some(arg => typeof arg !== 'string')) throw new Error('Invalid specspec executable configuration.');
    const explicit = (key: string) => {
      const values = configuration.inspect(key);
      return values?.globalValue !== undefined || values?.workspaceValue !== undefined || values?.workspaceFolderValue !== undefined;
    };
    return resolveInvocation({ command, args: prefix },
      this.context.extensionMode !== vscode.ExtensionMode.Production ? process.env.SPECSPEC_PYTHON : undefined,
      explicit('command') || explicit('args'));
  }
  async probe(): Promise<void> {
    const invocation = this.invocation();
    await probeCli(invocation.command, invocation.args, this.root.fsPath);
    this.verifiedInvocation = JSON.stringify(invocation);
  }
  async startup() { await this.probe(); return inspectProject(this.root.fsPath); }
  async cli<T>(args: string[], input?: string): Promise<Envelope<T>> {
    const invocation = this.invocation();
    const signature = JSON.stringify(invocation);
    if (signature !== this.verifiedInvocation) {
      await probeCli(invocation.command, invocation.args, this.root.fsPath);
      this.verifiedInvocation = signature;
    }
    if (!vscode.workspace.isTrusted) throw new Error('Workspace trust is required to run specspec.');
    this.output.appendLine(`CLI: ${invocation.command} ${[...invocation.args, ...args].join(' ')}`);
    const start = Date.now();
    try { return await this.cliClient.invoke<T>(invocation.command, invocation.args, this.root.fsPath, args, input); }
    finally { this.trace(`cli-${args[0]}`, Date.now() - start); }
  }
  dispose(): void { this.documents.dispose(); this.cliClient.dispose(); this.disposables.forEach(d => d.dispose()); }
}

class GraphView implements vscode.Disposable {
  private readonly disposables: vscode.Disposable[] = [];
  private readonly session: any;
  readonly recoveryKey: string;
  constructor(private project: GraphProject, panel: vscode.WebviewPanel, context: vscode.ExtensionContext,
    output: vscode.OutputChannel, readonly document: vscode.TextDocument | undefined, node: SpecNode | undefined, recovery: FormRecovery | undefined, bootstrap: any,
    selectProject: () => void, compare: () => void) {
    this.recoveryKey = `specspec.pendingForm:${document?.uri.toString()}:${randomBytes(16).toString('hex')}`;
    let latestEditSequence: number | undefined;
    const clearRecovery = async () => {
      await context.workspaceState.update(this.recoveryKey, undefined);
      if (recovery) { await context.workspaceState.update(recovery.key, undefined); recovery = undefined; }
    };
    panel.webview.options = { enableScripts: true, localResourceRoots: [vscode.Uri.joinPath(context.extensionUri, 'media')] };
    const adapter = document ? {
      id: node!.id,
      get: () => project.documentState(document),
      apply: async (before: string, _after: string, edit: { start: number; end: number; text: string }) => {
        if (!vscode.workspace.isTrusted) throw new Error('Workspace trust is required to edit specspec documents.');
        if (document.isClosed || document.getText() !== before) throw new Error('Document changed or closed; the form is retained.');
        const workspaceEdit = new vscode.WorkspaceEdit();
        workspaceEdit.replace(document.uri, new vscode.Range(document.positionAt(edit.start), document.positionAt(edit.end)), edit.text);
        if (!await vscode.workspace.applyEdit(workspaceEdit)) throw new Error('Document edit failed. See specspec output.');
      },
    } : undefined;
    this.session = new GraphSession({
      startup: () => project.startup(),
      cli: (args: string[], input?: string) => ['init', 'add', 'update', 'delete'].includes(args[0])
        ? project.documents.mutate(args, input) : project.cli(args, input),
      initialGraph: () => project.documents.initial(bootstrap),
      readGraph: (base: string, target?: string) => project.documents.readGraph(base, false, target),
      annotationDocuments: async () => {
        await project.documents.idle();
        return Object.fromEntries(project.documents.documents().map((d: any) => [d.path, d.text]));
      },
      trace: (phase: string, duration: number, nodes?: number) => project.trace(phase, duration, nodes),
      authorized: () => vscode.workspace.isTrusted,
      post: async (message: any) => {
        if (document && message.type === 'document-status' && message.editSequence === latestEditSequence) {
          await clearRecovery(); delete message.document.recoveredForm;
        }
        return panel.webview.postMessage(message);
      }, log: (message: string) => output.appendLine(message),
      renderMatches: presentation.renderMatches, sameNode: presentation.sameNode,
      confirm: async (message: string) => (await vscode.window.showWarningMessage(message, { modal: true }, 'Confirm')) === 'Confirm',
      revisions: async (base: string, target: string) => {
        const a = await vscode.window.showInputBox({ prompt: 'Base commit/ref', value: base }); if (!a) return;
        const b = await vscode.window.showInputBox({ prompt: 'Target commit/ref (empty = workspace)', value: target });
        if (b !== undefined) { panel.title = `specspec: ${a} → ${b || 'workspace'}`; return [a, b]; }
      },
      ...(adapter && document ? { document: {
        state: () => ({ nodeId: adapter.id, path: adapter.get().path, version: document.version, dirty: document.isDirty,
          ...(recovery ? { recoveredForm: recovery.form } : {}) }),
        edit: (message: unknown) => project.documents.edit(adapter, message),
        save: async () => { await project.documents.idle(); if (!await document.save()) throw new Error('Node file save needs attention. See specspec output.'); },
      } } : {}),
    });
    this.disposables.push(panel.webview.onDidReceiveMessage(message => {
      if (document && message?.type === 'edit' && message.id === adapter?.id && Buffer.byteLength(JSON.stringify(message), 'utf8') <= 3 * 1024 * 1024) {
        latestEditSequence = message.editSequence;
        // Native recovery covers applied document edits; this small separate
        // backup protects form input still waiting on (or rejected by) Python.
        void Promise.resolve(context.workspaceState.update(this.recoveryKey, message)).catch(error => this.session.warn(error));
      }
      if (document && message?.type === 'discard-form') {
        void clearRecovery().then(() => panel.webview.postMessage({ type: 'document-status', document: this.session.host.document.state() })).catch(error => this.session.warn(error));
      }
      else if (message?.type === 'select-project') selectProject();
      else if (document && message?.type === 'compare') compare();
      else if (document && message?.type === 'open-node') void this.openNode(message.id).catch(error => this.session.warn(error));
      else if (document && ['undo', 'redo'].includes(message?.type)) void this.session.flushDocument().then(() => vscode.commands.executeCommand(message.type));
      else this.session.receive(message);
    }));
    const configure = () => {
      try { this.session.configurePolling(vscode.workspace.getConfiguration('specspec', project.root).get<number>('pollIntervalMs', 0)); }
      catch (error) { this.session.warn(error); }
    };
    configure(); this.disposables.push(project.documents.subscribe(() => { configure(); this.session.scheduleRefresh(); }),
      project.subscribeAnnotations(error => error ? this.session.annotationWarning(error) : this.session.scheduleAnnotationsRefresh()));
    const resource = (name: string) => panel.webview.asWebviewUri(vscode.Uri.joinPath(context.extensionUri, 'media', name)).toString();
    panel.webview.html = graphHtml(resource, panel.webview.cspSource, randomBytes(16).toString('hex'), { scope: project.root.fsPath, showProject: false });
  }
  private async openNode(id: unknown): Promise<void> {
    if (typeof id !== 'string') throw new Error('Invalid node identity.');
    const graph = await this.project.documents.readGraph();
    const node: SpecNode | undefined = graph.snapshot.nodes.find((n: SpecNode) => n.id === id);
    if (!node) throw new Error('Select a current node.');
    await this.flushDocument();
    await vscode.commands.executeCommand('vscode.openWith', vscode.Uri.joinPath(this.project.root, node.path), VIEW_TYPE);
  }
  open(): Promise<Snapshot> { return this.session.open(); }
  get snapshot(): Snapshot | undefined { return this.session.snapshot; }
  async chooseRevisions(): Promise<void> { await this.session.waitReady(); await this.session.run(async () => { if (await this.session.checkStartup()) await this.session.chooseRevisions(); }); }
  flushDocument(): Promise<void> { return this.session.flushDocument(); }
  dispose(): void { this.session.dispose(); this.disposables.forEach(d => d.dispose()); }
}
