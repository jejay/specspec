const { test } = require('node:test');
const assert = require('node:assert/strict');
const { resolve, relative, join } = require('node:path');
const { mkdtempSync, writeFileSync, rmSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { resolveExecutable } = require('../launch.cjs');
const { invoke } = require('../../graph-ui-common/host/cli.cjs');

test('relative interpreter paths are anchored to launch, not either selected graph', () => {
  const launch = resolve(__dirname, '..');
  const configured = '../.venv/Scripts/python.exe';
  const executable = resolveExecutable(configured, launch);
  assert.equal(executable, resolve(launch, configured));
  for (const project of [resolve(launch, '..'), resolve(launch, '../example/gantt')]) {
    assert.notEqual(executable, resolve(project, configured));
  }
});

test('absolute executables and bare PATH commands keep their existing meaning', () => {
  const launch = resolve(__dirname, '..');
  assert.equal(resolveExecutable(process.execPath, launch), process.execPath);
  for (const command of ['python', 'specspec', 'uvx']) assert.equal(resolveExecutable(command, launch), command);
  const spaced = join(launch, 'interpreter folder', 'python.exe');
  assert.equal(resolveExecutable(relative(launch, spaced), launch), spaced);
});

test('launch-resolved executable actually runs with a different project cwd', async t => {
  const project = mkdtempSync(join(tmpdir(), 'specspec-relative-interpreter-'));
  t.after(() => rmSync(project, { recursive: true, force: true }));
  const script = join(project, 'cli.cjs');
  writeFileSync(script, 'process.stdout.write(JSON.stringify({api_version:4,ok:true,result:{cwd:process.cwd(),argv:process.argv.slice(2)},diagnostics:[]}));');
  const launch = resolve(__dirname, '..');
  const executable = resolveExecutable(relative(launch, process.execPath), launch);
  const result = await invoke(executable, [script], project, ['list', '--json']);
  assert.equal(result.result.cwd, project);
  assert.deepEqual(result.result.argv, ['--root', project, 'list', '--json']);
});
