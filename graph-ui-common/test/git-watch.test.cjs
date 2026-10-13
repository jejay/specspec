const { test } = require('node:test');
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const { mkdtempSync, rmSync, writeFileSync } = require('node:fs');
const { join } = require('node:path');
const { tmpdir } = require('node:os');
const { GitWatcher } = require('../host/git-watch.cjs');
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
async function observed(check) {
  for (let n = 0; n < 200; n++) { if (check()) return; await delay(10); }
  assert.ok(check(), 'Git ref notification must arrive without polling or Refresh');
}
function fixture(t, initialize = true) {
  const container = mkdtempSync(join(tmpdir(), 'specspec-git-watching-'));
  const git = (...args) => execFileSync('git', ['-C', container, ...args], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim();
  t.after(() => rmSync(container, { recursive: true, force: true, maxRetries: 30, retryDelay: 100 }));
  if (initialize) {
    git('init', '-b', 'main'); git('config', 'user.name', 'Test'); git('config', 'user.email', 't@x');
  }
  return { container, git };
}
test('unborn, staged deletion, commit and packed refs notify without writing or polling', async t => {
  const f = fixture(t); let count = 0; const failures = [];
  const watcher = new GitWatcher(f.container, () => count++, error => failures.push(error.message));
  t.after(() => watcher.close());
  writeFileSync(join(f.container, 'file.md'), 'Earlier\n'); f.git('add', '.');
  let before = count; f.git('commit', '-m', 'Initial reason'); await observed(() => count > before);
  before = count; f.git('rm', 'file.md'); await observed(() => count > before);
  before = count; f.git('commit', '-m', 'Delete because the idea was replaced'); await observed(() => count > before);
  before = count; f.git('pack-refs', '--all', '--prune'); await observed(() => count > before);
  assert.deepEqual(failures, []); assert.equal(watcher.pollTimer, undefined);
  watcher.close(); before = count; f.git('commit', '--allow-empty', '-m', 'After disposal'); await delay(50);
  assert.equal(count, before); assert.equal(watcher.watches.size, 0);
});
test('branch creation/switch and detached HEAD replace the watched current ref', async t => {
  const f = fixture(t); f.git('commit', '--allow-empty', '-m', 'Base'); let count = 0; const failures = [];
  const watcher = new GitWatcher(f.container, () => count++, error => failures.push(error.message));
  t.after(() => watcher.close());
  let before = count; f.git('switch', '-c', 'topic/deep/branch'); await observed(() => count > before);
  await delay(50); before = count; f.git('commit', '--allow-empty', '-m', 'Nested branch'); await observed(() => count > before);
  before = count; f.git('checkout', '--detach'); await observed(() => count > before);
  before = count; f.git('commit', '--allow-empty', '-m', 'Detached'); await observed(() => count > before);
  assert.deepEqual(failures, []);
});
test('linked worktrees observe private HEAD and shared current branch refs', async t => {
  const f = fixture(t); f.git('commit', '--allow-empty', '-m', 'Base');
  const linked = join(f.container, 'linked'); f.git('worktree', 'add', '-b', 'linked/topic', linked);
  let count = 0; const failures = [];
  const watcher = new GitWatcher(linked, () => count++, error => failures.push(error.message));
  t.after(() => watcher.close());
  assert.notEqual(watcher.directory, watcher.common);
  const before = count;
  execFileSync('git', ['-C', linked, 'commit', '--allow-empty', '-m', 'Linked change'], { stdio: 'pipe' });
  await observed(() => count > before); assert.deepEqual(failures, []);
});
test('non-Git project creation is supported and later git init is observed', async t => {
  const f = fixture(t, false); let count = 0; const failures = [];
  const watcher = new GitWatcher(f.container, () => count++, error => failures.push(error.message));
  t.after(() => watcher.close());
  assert.equal(watcher.directory, undefined); assert.deepEqual(failures, []);
  f.git('init', '-b', 'main'); await observed(() => Boolean(watcher.directory) && count > 0);
  assert.deepEqual(failures, []);
});
