/* Disposable clone of the maintained Git history. Never writes the development graph. */
const { execFileSync } = require('node:child_process');
const { mkdtempSync, rmSync } = require('node:fs');
const { join } = require('node:path');
const { tmpdir } = require('node:os');
const { expandResult } = require('../host/wire.cjs');
function fixture(source, python) {
  const container = mkdtempSync(join(tmpdir(), 'specspec-ui-project-'));
  const root = join(container, 'gantt');
  const cleanup = () => rmSync(container, { recursive: true, force: true, maxRetries: 30, retryDelay: 200 });
  try {
    // The same safe checkout helper serves manual workspaces, Python tests and both hosts.
    // Keep all real stage tags/ancestry; do not copy a graph and invent a one-commit history.
    execFileSync(python, [join(source, 'history/checkout.py'), root], { encoding: 'utf8' });
    const cli = (args, input) => expandResult(JSON.parse(execFileSync(python, ['-m', 'specspec', '--root', root, ...args], { input, encoding: 'utf8' })).result);
    const saved = () => cli(['api'], JSON.stringify({ api_version: 7, op: 'read' })).snapshot;
    const node = id => saved().nodes.find(n => n.id === id);
    let s = saved();
    const manifesto = s.nodes.find(n => n.type === 'manifesto');
    const modified = s.nodes.find(n => n.type === 'requirement' && n.parents.includes(manifesto.id));
    if (!modified) throw new Error('The UI fixture needs a current manifesto-child requirement.');
    cli(['update', modified.id, '--body', '-', '--json'], '# Modified UI fixture intention\n\nDisposable test content, not the real project.\n');
    const added = cli(['add', '--parent', manifesto.id, '--body', '-', '--json'], '# Added UI fixture intention\n\nDisposable test content.\n').changed_ids[0];
    s = saved();
    const removed = s.nodes.find(n => n.type === 'implementation');
    // A managed physical deletion exercises D; this disposable terminal node only.
    cli(['delete', removed.id, '--json']);
    cli(['check', '--warnings-as-errors', '--json']);
    return { root, added, modified: modified.id, removed: removed.id, cli, saved, node, cleanup };
  } catch (error) { cleanup(); throw error; }
}
module.exports = { fixture };
