const { test } = require('node:test');
const assert = require('node:assert/strict');
const { ignored } = require('../scripts/package.cjs');

test('portable application packaging selects only built runtime roots', () => {
  for (const path of ['', '/', '/package.json', '/main.cjs', '/preload.cjs', '/security.cjs', '/store.cjs', '/launch.cjs', '/build/media/graph.js', '/build/common/host/session.cjs']) assert.equal(ignored(path), false, path);
  for (const path of ['/node_modules/electron/index.js', '/src/code.js', '/test/private.cjs', '/test-host/run.cjs', '/scripts/build.cjs', '/.specspec/local/journal.json', '/.env', '/release/old.exe', '/README.md']) assert.equal(ignored(path), true, path);
});
