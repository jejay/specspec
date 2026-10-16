const { test } = require('node:test');
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const { mkdtempSync, rmSync, writeFileSync, mkdirSync } = require('node:fs');
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
test('unborn, deletion commits and packed refs notify without writing or polling', async t => {
  const f = fixture(t); let count = 0; const failures = [];
  const watcher = new GitWatcher(f.container, () => count++, error => failures.push(error.message));
  t.after(() => watcher.close()); await watcher.discovery;
  writeFileSync(join(f.container, 'file.md'), 'Earlier\n'); f.git('add', '.');
  let before = count; f.git('commit', '-m', 'Initial reason'); await observed(() => count > before);
  f.git('rm', 'file.md'); // Staging retains HEAD; canonical-file watching owns worktree edits.
  before = count; f.git('commit', '-m', 'Delete because the idea was replaced'); await observed(() => count > before);
  before = count; f.git('pack-refs', '--all', '--prune'); await observed(() => count > before);
  assert.deepEqual(failures, []); assert.equal(watcher.pollTimer, undefined);
  watcher.close(); before = count; f.git('commit', '--allow-empty', '-m', 'After disposal'); await delay(50);
  assert.equal(count, before); assert.equal(watcher.watches.size, 0);
});
test('index-only stat-cache writes leave HEAD-to-worktree watchers idle',async t=>{
  const f=fixture(t);f.git('commit','--allow-empty','-m','Base');let count=0;const failures=[];
  const watcher=new GitWatcher(f.container,()=>count++,e=>failures.push(e.message));t.after(()=>watcher.close());
  await watcher.discovery;await delay(50);const before=count;
  writeFileSync(join(f.container,'.git/index'),'Disposable stat-cache-only event');await delay(100);
  assert.equal(count,before);assert.deepEqual(failures,[]);
});

test('branch creation/switch and detached HEAD replace the watched current ref', async t => {
  const f = fixture(t); f.git('commit', '--allow-empty', '-m', 'Base'); let count = 0; const failures = [];
  const watcher = new GitWatcher(f.container, () => count++, error => failures.push(error.message));
  t.after(() => watcher.close()); await watcher.discovery;
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
  t.after(() => watcher.close()); await watcher.discovery;
  assert.notEqual(watcher.directory, watcher.common);
  const before = count;
  execFileSync('git', ['-C', linked, 'commit', '--allow-empty', '-m', 'Linked change'], { stdio: 'pipe' });
  await observed(() => count > before); assert.deepEqual(failures, []);
});
test('Git discovery stays asynchronous, coalesces a burst and adopts only the latest result', async t => {
  const f=fixture(t,false),directory=join(f.container,'.git');mkdirSync(directory);
  const replies=[],failures=[];let changed=0;
  const execute=()=>new Promise(resolve=>replies.push(resolve));
  const watcher=new GitWatcher(f.container,()=>changed++,e=>failures.push(e.message),undefined,execute);
  t.after(()=>watcher.close());
  for(let i=0;i<20;i++)void watcher.discover();
  await new Promise(resolve=>setImmediate(resolve));assert.equal(replies.length,1);assert.equal(watcher.watches.size,0);
  replies[0]({stdout:'/obsolete/git\n/obsolete/common\n'});await observed(()=>replies.length===2);
  assert.equal(watcher.directory,undefined);assert.equal(changed,0);
  replies[1]({stdout:`${directory}\n${directory}\n`});await watcher.discovery;
  assert.equal(watcher.directory,directory);assert.equal(replies.length,2);assert.equal(changed,1);assert.deepEqual(failures,[]);
});

test('closing a pending Git discovery prevents late watches and notifications',async t=>{
  const f=fixture(t,false),directory=join(f.container,'.git');mkdirSync(directory);let release,changed=0;
  const watcher=new GitWatcher(f.container,()=>changed++,()=>assert.fail('No late error'),undefined,
    ()=>new Promise(resolve=>{release=resolve;}));
  watcher.close();release({stdout:`${directory}\n${directory}\n`});await watcher.discovery;
  assert.equal(changed,0);assert.equal(watcher.watches.size,0);assert.equal(watcher.directory,undefined);
});

test('Git discovery distinguishes a non-Git folder from real execution failures',async t=>{
  const f=fixture(t,false),failures=[];
  for(const code of [128,'ENOENT','ETIMEDOUT']){
    const watcher=new GitWatcher(f.container,()=>{},e=>failures.push(e.message),undefined,async()=>{throw Object.assign(new Error(String(code)),{code});});
    await watcher.discovery;if(code!==128)await observed(()=>failures.length===(code==='ENOENT'?1:2));watcher.close();
  }
  assert.equal(failures.length,2);assert.match(failures[0],/ENOENT/);assert.match(failures[1],/ETIMEDOUT/);
});

test('bounded asynchronous Git discovery retries recover without blocking or installing polling',async t=>{
  const f=fixture(t,false),directory=join(f.container,'.git');mkdirSync(directory);let calls=0,changes=0;const failures=[];
  const watcher=new GitWatcher(f.container,()=>changes++,e=>failures.push(e.message),undefined,async(_cmd,_args,options)=>{
    assert.equal(options.timeout,3000);if(++calls===1)throw Object.assign(new Error('Slow launch'),{code:'ETIMEDOUT'});
    return {stdout:`${directory}\n${directory}\n`};
  });
  t.after(()=>watcher.close());await observed(()=>Boolean(watcher.directory));
  assert.equal(calls,2);assert.equal(changes,1);assert.deepEqual(failures,[]);assert.equal(watcher.pollTimer,undefined);
});

test('non-Git project creation is supported and later git init is observed', async t => {
  const f = fixture(t, false); let count = 0; const failures = [];
  const watcher = new GitWatcher(f.container, () => count++, error => failures.push(error.message));
  t.after(() => watcher.close()); await watcher.discovery;
  assert.equal(watcher.directory, undefined); assert.deepEqual(failures, []);
  f.git('init', '-b', 'main'); await observed(() => Boolean(watcher.directory) && count > 0);
  assert.deepEqual(failures, []);
});
