const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { UI_GUARD_MS, NATIVE_GUARD_MS, STARTUP_SHUTDOWN_MS, ELECTRON_RELOAD_MS, ELECTRON_HOST_GUARD_MS, VSCODE_HOST_GUARD_MS } = require('../../graph-ui-common/test-host/budgets.cjs');

test('installed-host guards cover every phase without changing individual operation deadlines', () => {
  assert.equal(UI_GUARD_MS, 300_000);
  assert.equal(NATIVE_GUARD_MS, 160_000);
  assert.equal(VSCODE_HOST_GUARD_MS, UI_GUARD_MS + NATIVE_GUARD_MS + STARTUP_SHUTDOWN_MS);
  assert.equal(ELECTRON_HOST_GUARD_MS, UI_GUARD_MS + ELECTRON_RELOAD_MS + STARTUP_SHUTDOWN_MS);
  assert.equal(VSCODE_HOST_GUARD_MS, 500_000);
  assert.equal(ELECTRON_HOST_GUARD_MS, 400_000);
  const runner = readFileSync(join(__dirname, '../test-host/run.cjs'), 'utf8');
  const desktop = readFileSync(join(__dirname, '../../electron/test-host/run.cjs'), 'utf8');
  const smoke = readFileSync(join(__dirname, '../test-host/smoke.cjs'), 'utf8');
  for (const text of [runner,desktop,smoke]) assert.match(text, /require\('\.\.\/\.\.\/graph-ui-common\/test-host\/budgets.cjs'\)/);
  assert.match(runner, /child.kill\(\); }, VSCODE_HOST_GUARD_MS/);
  assert.match(desktop, /child.kill\(\); }, ELECTRON_HOST_GUARD_MS/);
  assert.match(smoke, /Date.now\(\) \+ UI_GUARD_MS/);
  assert.match(smoke, /Date.now\(\) \+ NATIVE_GUARD_MS/);
  for (const flag of ['--disable-background-timer-throttling','--disable-renderer-backgrounding','--disable-backgrounding-occluded-windows']) {
    assert.ok(desktop.includes(`'${flag}'`));
    assert.ok(runner.includes(`'${flag}=true'`), 'Explicit values keep Code from consuming the following workspace path.');
  }
});
