const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { PHASE_GUARD_MS, HOST_GUARD_MS } = require('../test-host/budgets.cjs');

test('outer installed-host guard covers both unchanged shared/native guards and shutdown', () => {
  assert.equal(PHASE_GUARD_MS, 160_000);
  assert.equal(HOST_GUARD_MS, 360_000);
  assert.equal(HOST_GUARD_MS, 2 * PHASE_GUARD_MS + 40_000);
  const runner = readFileSync(join(__dirname, '../test-host/run.cjs'), 'utf8');
  const smoke = readFileSync(join(__dirname, '../test-host/smoke.cjs'), 'utf8');
  assert.match(runner, /require\('\.\/budgets.cjs'\)/);
  assert.match(runner, /child.kill\(\); }, HOST_GUARD_MS/);
  assert.equal((smoke.match(/Date.now\(\) \+ PHASE_GUARD_MS/g) || []).length, 2);
});
