const { test } = require('node:test');
const assert = require('node:assert/strict');
const { EventEmitter } = require('node:events');
const { mkdtempSync, mkdirSync, renameSync, writeFileSync, rmSync } = require('node:fs');
const { join } = require('node:path');
const { tmpdir } = require('node:os');
const { AnnotationWatcher } = require('../host/annotations.cjs');
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
async function waitFor(check) { for (let i = 0; i < 100; i++) { if (check()) return; await pause(10); } assert.ok(check()); }

test('real annotation watches attach after late directory creation, atomic shots and replacement, and close', async t => {
  const root = mkdtempSync(join(tmpdir(), 'specspec-annotations-watch-'));
  let changes = 0; const errors = [];
  const watcher = new AnnotationWatcher(root, () => changes++, error => errors.push(error));
  t.after(() => { watcher.close(); rmSync(root, { recursive: true, force: true }); });
  const path = join(root, '.specspec-local', 'annotations');
  mkdirSync(path, { recursive: true }); await waitFor(() => watcher.watches.size === 3);
  const before = changes; writeFileSync(join(path, '.shot-one.tmp'), '{}');
  renameSync(join(path, '.shot-one.tmp'), join(path, 'one.json'));
  await waitFor(() => changes > before);
  const published = changes; await pause(30);
  writeFileSync(join(path, '.shot-two.tmp'), '{}'); await pause(30);
  assert.equal(changes, published, 'Unpublished payloads do not trigger arrivals.');
  renameSync(path, path + '-old'); mkdirSync(path); await waitFor(() => watcher.watches.size === 3 && changes > published);
  const replaced = changes; writeFileSync(join(path, 'two.json'), '{}'); await waitFor(() => changes > replaced);
  watcher.close(); const closed = changes; writeFileSync(join(path, 'three.json'), '{}'); await pause(30);
  assert.equal(changes, closed); assert.equal(watcher.watches.size, 0); assert.deepEqual(errors, []);
});

test('annotation watching refuses symlink directories and exposes actionable failures', () => {
  const created = [], errors = [];
  const fs = {
    lstatSync: path => ({ dev: 1, ino: path, isDirectory: () => true, isSymbolicLink: () => path.endsWith('annotations') }),
    watch: path => { const watcher = new EventEmitter(); watcher.path = path; watcher.close = () => { watcher.closed = true; }; created.push(watcher); return watcher; },
  };
  const watcher = new AnnotationWatcher('root', () => {}, error => errors.push(error), fs);
  assert.equal(created.length, 2);
  created[0].emit('error', new Error('Watch limit'));
  assert.match(errors[0].message, /Spotlight watching failed.*Refresh.*polling/);
  assert.equal(created[0].closed, true); watcher.close(); assert.ok(created.every(w => w.closed));
});
