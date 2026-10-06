const assert = require('node:assert/strict');
const { resolve } = require('node:path');
const { existsSync, readFileSync } = require('node:fs');
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
  assert.ok(snapshot?.valid, 'Open Graph must load and render a valid graph.');
  assert.ok(snapshot.nodes.length > 0);
  assert.ok(snapshot.nodes.some(node => node.type === 'manifesto'));
  // Wait for external Chromium checks before this test host exits.
  if (process.env.SPECSPEC_UI_RESULT) {
    const until = Date.now() + 80_000;
    while (!existsSync(process.env.SPECSPEC_UI_RESULT) && Date.now() < until) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    assert.ok(existsSync(process.env.SPECSPEC_UI_RESULT), 'Real webview interaction checks timed out.');
    const result = JSON.parse(readFileSync(process.env.SPECSPEC_UI_RESULT, 'utf8'));
    assert.ok(result.ok, result.error);
  }
  console.log(`SPECSPEC_REAL_HOST_SMOKE_OK: ${snapshot.nodes.length} nodes rendered; UI checks passed.`);
};
