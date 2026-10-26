const { test } = require('node:test');
const assert = require('node:assert/strict');
const { mkdtempSync, mkdirSync, writeFileSync, rmSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join } = require('node:path');
const { dependencyNotices } = require('../scripts/build.cjs');

function fixture(t) {
  const root = mkdtempSync(join(tmpdir(), 'specspec-licenses-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  mkdirSync(join(root, 'graph-ui-common'));
  return root;
}
function dependency(root, folder, name, version, license = 'LICENSE') {
  const directory = join(root, folder); mkdirSync(directory, { recursive: true });
  writeFileSync(join(directory, 'package.json'), JSON.stringify({ name, version, license: 'MIT' }));
  if (license) writeFileSync(join(directory, license), `License for ${name} ${version}`);
}
test('bundled notices include hoisted, scoped, nested and duplicate-version dependencies once', t => {
  const root = fixture(t);
  dependency(root, 'node_modules/@scope/one', '@scope/one', '1.0.0');
  dependency(root, 'graph-ui-common/node_modules/two', 'two', '2.0.0', 'LICENSE.md');
  dependency(root, 'node_modules/outer/node_modules/two', 'two', '3.0.0', 'license.txt');
  const notices = dependencyNotices(['../node_modules/@scope/one/a.js', '../node_modules/@scope/one/b.js',
    'node_modules/two/src/a.js', '../node_modules/outer/node_modules/two/src/a.js', 'src/graph-vendor.js'], join(root, 'graph-ui-common'));
  assert.equal(notices.count, 3);
  for (const name of ['@scope/one 1.0.0', 'two 2.0.0', 'two 3.0.0']) assert.ok(notices.text.includes(name));
  assert.equal(notices.text.match(/License for @scope\/one/g).length, 1);
});
test('missing actual bundled licenses fail rather than silently omit a notice', t => {
  const root = fixture(t); dependency(root, 'node_modules/one', 'one', '1.0.0', null);
  assert.throws(() => dependencyNotices(['../node_modules/one/a.js'], join(root, 'graph-ui-common')), /Missing bundled dependency license/);
});
