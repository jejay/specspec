/* Disposable real CLI/Git fixture. Never writes the actual repository graph. */
const { execFileSync } = require('node:child_process');
const { mkdtempSync, mkdirSync, copyFileSync, readdirSync, rmSync } = require('node:fs');
const { join, resolve, dirname } = require('node:path');
const { tmpdir } = require('node:os');
function fixture(source, python) {
  const root = mkdtempSync(join(tmpdir(), 'specspec-ui-project-'));
  const cli = (args, input) => JSON.parse(execFileSync(python, ['-m', 'specspec', '--root', root, ...args], { input, encoding: 'utf8' })).result;
  const original = JSON.parse(execFileSync(python, ['-m', 'specspec', '--root', source, 'list', '--json'], { encoding: 'utf8' })).result;
  const paths = new Set(readdirSync(join(source, '_specspec')).map(n => '_specspec/' + n));
  for (const n of original.nodes) if (!n.retired) for (const s of n.sources) paths.add(s.path);
  for (const path of paths) { const to = join(root, path); mkdirSync(dirname(to), { recursive: true }); copyFileSync(join(source, path), to); }
  const git = (...args) => execFileSync('git', args, { cwd: root, encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] });
  git('init'); git('config', 'core.autocrlf', 'false'); git('config', 'user.name', 'Isolated UI fixture');
  git('config', 'user.email', 'ui-fixture@example.invalid'); git('add', '.'); git('commit', '-m', 'Disposable baseline');
  let s = cli(['list', '--json']);
  const manifesto = s.nodes.find(n => n.type === 'manifesto');
  const modified = s.nodes.find(n => n.type === 'requirement' && !n.retired && n.parents.includes(manifesto.id));
  if (!modified) throw new Error('The UI fixture needs a live manifesto-child requirement.');
  cli(['update', modified.id, '--body', '-', '--json'], '# Modified UI fixture intention\n\nDisposable test content, not the real project.\n');
  s = cli(['list', '--json']);
  const added = cli(['add', '--parent', s.nodes.find(n => n.type === 'manifesto').id, '--slug', 'added-ui-fixture', '--body', '-', '--json'], '# Added UI fixture intention\n\nDisposable test content.\n').changed_ids[0];
  s = cli(['list', '--json']);
  const removed = s.nodes.find(n => n.type === 'implementation' && !n.retired);
  // A literal deletion is required to exercise D; only this disposable terminal node.
  rmSync(join(root, removed.path));
  cli(['validate', '--warnings-as-errors', '--json']);
  return { root, added, modified: modified.id, removed: removed.id, cli, cleanup: () => rmSync(root, { recursive: true, force: true, maxRetries: 30, retryDelay: 200 }) };
}
module.exports = { fixture };
