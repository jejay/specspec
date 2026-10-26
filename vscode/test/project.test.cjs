const { test } = require('node:test');
const assert = require('node:assert/strict');
const { mkdtempSync, mkdirSync, writeFileSync, rmSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join } = require('node:path');
const { findProjectRoot, resolveInvocation } = require('../out/project.js');

function fixture(t) {
  const root = mkdtempSync(join(tmpdir(), 'specspec-project-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  mkdirSync(join(root, '.specspec'));
  mkdirSync(join(root, 'vscode', 'src'), { recursive: true });
  return root;
}

test('project discovery handles root folders, subfolders and selected files', async t => {
  const root = fixture(t);
  assert.equal(await findProjectRoot(root), root);
  assert.equal(await findProjectRoot(join(root, 'vscode')), root);
  const file = join(root, 'vscode', 'src', 'example.ts');
  writeFileSync(file, 'example');
  assert.equal(await findProjectRoot(file), root);
});

test('an invalid nearer workspace is not silently skipped', async t => {
  const root = fixture(t);
  const nested = join(root, 'vscode');
  writeFileSync(join(nested, '.specspec'), 'not a directory');
  assert.equal(await findProjectRoot(nested), nested);
});

test('missing projects produce actionable errors', async t => {
  const root = mkdtempSync(join(tmpdir(), 'specspec-missing-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  await assert.rejects(findProjectRoot(root), /Select a SpecSpec project folder/);
});

test('lookalike and underscore directories are not canonical projects', async t => {
  const root = mkdtempSync(join(tmpdir(), 'specspec-lookalike-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  for (const name of ['xspecspec', '_specspec', 'specspec', '.specspec-local']) mkdirSync(join(root, name));
  await assert.rejects(findProjectRoot(root), /Select a SpecSpec project folder/);
});

test('development interpreter is explicit and configured invocations take precedence', () => {
  const configured = { command: 'specspec', args: [] };
  assert.deepEqual(resolveInvocation(configured, 'C:/repo/.venv/Scripts/python.exe'), {
    command: 'C:/repo/.venv/Scripts/python.exe', args: ['-m', 'specspec'],
  });
  const explicit = { command: 'uvx', args: ['--from', '.', 'specspec'] };
  assert.deepEqual(resolveInvocation(explicit, 'python', true), explicit);
  assert.deepEqual(resolveInvocation(configured), configured);
});
