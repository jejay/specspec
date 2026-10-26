/* Opt-in extensionTestsPath module: runs inside the real remote workspace host.
 * Use a disposable external maintained-history clone. No services or credentials
 * are installed; client connection/authentication are owned by VS Code/the user.
 */
const vscode = require('vscode');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {execFileSync} = require('node:child_process');

exports.run = async () => {
  const root = vscode.workspace.workspaceFolders?.[0]?.uri;
  assert.ok(root && root.scheme === 'file', 'Remote workspace files must be local to the executing host');
  const config = JSON.parse(fs.readFileSync(path.join(root.fsPath, '.specspec-remote-smoke.json'), 'utf8'));
  const resultPath = path.join(root.fsPath, '.specspec-remote-result.json');
  const report = { remoteName: vscode.env.remoteName, uiKind: vscode.env.uiKind, platform: process.platform, phases: [] };
  try {
    assert.equal(vscode.env.remoteName, config.remoteName);
    const extension = vscode.extensions.getExtension('specspec-dev.specspec-vscode');
    assert.ok(extension, 'Install/develop SpecSpec in this remote host');
    await extension.activate();
    assert.equal(extension.extensionKind, vscode.ExtensionKind.Workspace);
    assert.equal(extension.extensionUri.scheme, 'file');
    const cli = args => JSON.parse(execFileSync(config.python, ['-m','specspec','--root',root.fsPath,...args], {encoding:'utf8',timeout:120000})).result;
    const saved = cli(['query','--json']).target;
    const started = Date.now();
    const graph = await vscode.commands.executeCommand('specspec.openGraph', root);
    assert.equal(graph.valid,true);assert.deepEqual(graph.nodes.map(n=>n.id),saved.nodes.map(n=>n.id));
    report.phases.push({phase:'real-project-render',durationMs:Date.now()-started,nodes:graph.nodes.length});
    const node = saved.nodes.find(n=>n.type==='requirement');assert.ok(node);
    const uri = vscode.Uri.joinPath(root,node.path);
    await vscode.commands.executeCommand('vscode.openWith',uri,'specspec.graphEditor');
    const document = await vscode.workspace.openTextDocument(uri), original = document.getText();
    const edit = new vscode.WorkspaceEdit();edit.insert(uri,document.positionAt(original.length),'\nRemote Unicode 🐕 smoke draft.\n');
    assert.equal(await vscode.workspace.applyEdit(edit),true);assert.equal(document.isDirty,true);
    assert.equal(await document.save(),true);assert.equal(document.isDirty,false);
    const edited = await vscode.commands.executeCommand('specspec.openGraph',root);
    assert.match(edited.nodes.find(n=>n.id===node.id).body,/Remote Unicode 🐕/);
    const restore = new vscode.WorkspaceEdit();restore.replace(uri,new vscode.Range(document.positionAt(0),document.positionAt(document.getText().length)),original);
    await vscode.workspace.applyEdit(restore);await document.save();
    report.phases.push({phase:'remote-native-document-and-overlay',ok:true});
    const impl = saved.nodes.find(n=>n.sources.some(s=>s.blob));
    if (impl) {
      const number = impl.sources.findIndex(s=>s.blob) + 1;
      const preview = cli(['sources','show',impl.id,'--source',String(number),'--json']);
      assert.ok(preview.chunks.length);report.phases.push({phase:'remote-source-object-preview',ok:true});
    }
    report.ok=true;
  } catch (error) { report.ok=false;report.error=error.stack||String(error);throw error; }
  finally { fs.writeFileSync(resultPath,JSON.stringify(report,null,2)); }
};
