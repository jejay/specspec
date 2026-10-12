const assert = require('node:assert/strict');
const { resolve } = require('node:path');
const { existsSync, readFileSync, writeFileSync } = require('node:fs');
const vscode = require('vscode');

exports.run = async function run() {
  const expected = resolve(process.env.SPECSPEC_TEST_PROJECT_ROOT);
  const actual = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
  assert.ok(actual, 'The development host must open a project, not an empty window.');
  const normalize = path => process.platform === 'win32' ? resolve(path).toLowerCase() : resolve(path);
  assert.equal(normalize(actual), normalize(expected));
  assert.ok(vscode.workspace.isTrusted, 'The isolated test workspace must be trusted.');

  // Only the disposable test profile: give the node editor a useful screenshot area.
  await vscode.commands.executeCommand('workbench.action.closeSidebar');
  await vscode.commands.executeCommand('workbench.action.closeAuxiliaryBar');
  const snapshot = await vscode.commands.executeCommand('specspec.openGraph');
  // The graph is now in the main editor, not an Activity Bar sidebar.
  assert.ok(snapshot?.valid, 'Open Graph must load and render a valid graph.');
  assert.ok(snapshot.nodes.length > 0);
  assert.ok(snapshot.nodes.some(node => node.type === 'manifesto'));
  // Wait for external Chromium checks before this test host exits.
  if (process.env.SPECSPEC_UI_RESULT) {
    // Aggregate guard covers the expanded source-preview/schema-4 fixture suite;
    // individual CDP, mapping and watcher deadlines/assertions remain unchanged.
    const until = Date.now() + 160_000;
    while (!existsSync(process.env.SPECSPEC_UI_RESULT) && Date.now() < until) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    assert.ok(existsSync(process.env.SPECSPEC_UI_RESULT), 'Real webview interaction checks timed out.');
    const result = JSON.parse(readFileSync(process.env.SPECSPEC_UI_RESULT, 'utf8'));
    assert.ok(result.ok, result.error);
  }
  if (process.env.SPECSPEC_NATIVE_RESULT) {
    const other = JSON.parse(process.env.SPECSPEC_NATIVE_OTHER);
    const uri = vscode.Uri.file(process.env.SPECSPEC_NATIVE_PATH);
    // Ordinary file opening must select the default custom editor.
    await vscode.commands.executeCommand('vscode.open', uri);
    const document = await vscode.workspace.openTextDocument(uri);
    console.log('SPECSPEC_NATIVE_OPEN:', JSON.stringify(vscode.window.tabGroups.all.flatMap(g => g.tabs).map(t => ({ label: t.label, type: t.input?.viewType }))));
    const requestPath = process.env.SPECSPEC_NATIVE_REQUEST, responsePath = process.env.SPECSPEC_NATIVE_RESPONSE;
    let last = 0;
    // Aggregate native lifecycle guard; each request still has its own deadline.
    const until = Date.now() + 160_000;
    while (!existsSync(process.env.SPECSPEC_NATIVE_RESULT) && Date.now() < until) {
      if (existsSync(requestPath)) {
        let request; try { request = JSON.parse(readFileSync(requestPath, 'utf8')); } catch {}
        if (request?.id > last) {
          last = request.id;
          try {
            if (['undo', 'redo'].includes(request.action)) await vscode.commands.executeCommand(request.action);
            if (request.action === 'split') await vscode.commands.executeCommand('workbench.action.splitEditorRight');
            if (request.action === 'raw') {
              const edit = new vscode.WorkspaceEdit();
              edit.replace(uri, new vscode.Range(document.positionAt(0), document.positionAt(document.getText().length)), document.getText().replace(request.before, request.after));
              await vscode.workspace.applyEdit(edit);
            }
            if (request.action === 'other') await vscode.commands.executeCommand('vscode.open', vscode.Uri.file(other.path));
            const otherDocument = request.action === 'inspect-other' ? await vscode.workspace.openTextDocument(vscode.Uri.file(other.path)) : undefined;
            writeFileSync(responsePath, JSON.stringify({ id: request.id, text: document.getText(), dirty: document.isDirty,
              ...(otherDocument ? { otherDocument: { text: otherDocument.getText(), dirty: otherDocument.isDirty, path: other.path } } : {}),
              version: document.version, otherId: other.id, tabs: vscode.window.tabGroups.all.flatMap(g => g.tabs).map(t => ({ label: t.label, type: t.input?.viewType })) }));
          } catch (error) { writeFileSync(responsePath, JSON.stringify({ id: request.id, error: error.message })); }
        }
      }
      await new Promise(resolve => setTimeout(resolve, 50));
    }
    assert.ok(existsSync(process.env.SPECSPEC_NATIVE_RESULT), 'Native document UI checks timed out.');
    const result = JSON.parse(readFileSync(process.env.SPECSPEC_NATIVE_RESULT, 'utf8'));
    assert.ok(result.ok, result.error);
  }
  console.log(`SPECSPEC_REAL_HOST_SMOKE_OK: ${snapshot.nodes.length} nodes rendered; project and native-document UI checks passed.`);
};
