const { test } = require('node:test');
const assert = require('node:assert/strict');
const { EventEmitter } = require('node:events');
const { mkdtempSync, mkdirSync, rmSync, writeFileSync, renameSync, unlinkSync } = require('node:fs');
const { join } = require('node:path');
const { tmpdir } = require('node:os');
const { GraphWatcher } = require('../host/watch.cjs');
const pause = ms => new Promise(r => setTimeout(r, ms));
async function waitFor(check) { for (let i = 0; i < 200; i++) { if (check()) return; await pause(10); } assert.ok(check(), 'Watcher did not notify in time.'); }

test('directory watches reattach on replacement and missing filenames without recursive watching', () => {
  let ino = 1, exists = true, changes = 0;
  const watches = [], errors = [];
  const fs = {
    watch(path, callback) { const watcher = new EventEmitter(); watcher.close = () => { watcher.closed = true; }; watcher.callback = callback; watcher.path = path; watches.push(watcher); return watcher; },
    lstatSync() { if (!exists) throw Object.assign(new Error('Gone'), { code: 'ENOENT' }); return { dev: 1, ino, isDirectory: () => true, isSymbolicLink: () => false }; },
  };
  const w = new GraphWatcher('/project', () => changes++, e => errors.push(e), fs);
  assert.equal(watches.length, 2); const first = watches[1];
  watches[0].callback('rename', 'unrelated'); assert.equal(changes, 0);
  ino = 2; watches[0].callback('rename', null);
  assert.equal(first.closed, true); assert.equal(watches.length, 3);
  exists = false; watches[0].callback('rename', Buffer.from('_specspec')); assert.equal(watches[2].closed, true);
  exists = true; ino = 3; watches[0].callback('rename', '_specspec'); assert.equal(watches.length, 4);
  watches[3].emit('error', new Error('Watch unavailable')); assert.equal(watches[3].closed, true); assert.match(errors[0].message, /optional polling/);
  watches[0].callback('rename', '_specspec'); assert.equal(watches.length, 5);
  w.close(); assert.ok(watches.every(watcher => watcher.closed));
});

test('real watcher-only saves, atomic replacements, deletion and directory recreation notify', async t => {
  const root = mkdtempSync(join(tmpdir(), 'specspec-watch-')), dir = join(root, '_specspec'); mkdirSync(dir);
  let changes = 0; const errors = [];
  const watcher = new GraphWatcher(root, () => changes++, error => errors.push(error));
  t.after(() => { watcher.close(); rmSync(root, { recursive: true, force: true }); });
  const file = join(dir, 'node.md');
  let before = changes; writeFileSync(file, '# Original'); await waitFor(() => changes > before);
  before = changes; writeFileSync(file, '# Manual'); await waitFor(() => changes > before);
  before = changes; writeFileSync(join(dir, 'temporary.md'), '# Atomic'); renameSync(join(dir, 'temporary.md'), file); await waitFor(() => changes > before);
  before = changes; unlinkSync(file); await waitFor(() => changes > before);
  before = changes; renameSync(dir, join(root, 'old-graph')); mkdirSync(dir); await waitFor(() => changes > before && watcher.nodes);
  await pause(30); before = changes; writeFileSync(file, '# Recreated'); await waitFor(() => changes > before);
  assert.deepEqual(errors, []);
  watcher.close(); before = changes; writeFileSync(file, '# Closed'); await pause(40); assert.equal(changes, before);
});
