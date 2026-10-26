const { test } = require('node:test');
const assert = require('node:assert/strict');
const { mkdtempSync, mkdirSync, writeFileSync, rmSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join, dirname } = require('node:path');
const { codeCli } = require('../test-host/install.cjs');
function fixture(t) {
  const root = mkdtempSync(join(tmpdir(), 'specspec-code-layout-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  return root;
}
function cli(root, path) {
  const file = join(root, path, 'resources/app/out/cli.js');
  mkdirSync(dirname(file), { recursive: true }); writeFileSync(file, 'test CLI'); return file;
}
test('Code artifact installation supports direct and version-folder resources', t => {
  const root = fixture(t);
  const version = cli(root, 'abc123'); assert.equal(codeCli(join(root, 'Code.exe')), version);
  const direct = cli(root, ''); assert.equal(codeCli(join(root, 'Code.exe')), direct);
});
test('ambiguous side-by-side resources are not guessed', t => {
  const root = fixture(t); cli(root, 'abc123'); cli(root, 'def456');
  assert.throws(() => codeCli(join(root, 'Code.exe')), /Cannot identify one/);
});
