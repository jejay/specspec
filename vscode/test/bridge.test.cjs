const { test } = require('node:test');
const assert = require('node:assert/strict');
const { mkdtempSync, writeFileSync, rmSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join } = require('node:path');
const { invoke } = require('../out/bridge.js');

function fixture(t, source) {
  const directory = mkdtempSync(join(tmpdir(), 'specspec-bridge-'));
  const file = join(directory, 'fake-cli.cjs');
  writeFileSync(file, source);
  t.after(() => rmSync(directory, { recursive: true, force: true }));
  return { directory, file };
}

test('CLI bridge preserves argv and sends bodies through stdin', async t => {
  const { directory, file } = fixture(t, `
    let input = ''; process.stdin.on('data', chunk => input += chunk);
    process.stdin.on('end', () => console.log(JSON.stringify({
      api_version: 7, ok: true, result: { args: process.argv.slice(2), input }, diagnostics: []
    })));
  `);
  const result = await invoke(process.execPath, [file], directory, ['update', 'id', '--json'], '# Body\n');
  assert.deepEqual(result.result.args, ['--root', directory, 'update', 'id', '--json']);
  assert.equal(result.result.input, '# Body\n');
});

test('validation diagnostics become actionable errors', async t => {
  const { directory, file } = fixture(t, `
    console.log(JSON.stringify({ api_version: 7, ok: false, result: null,
      diagnostics: [{ code: 'SCHEMA', message: 'Invalid parent IDs', severity: 'error' }] }));
    process.exitCode = 1;
  `);
  await assert.rejects(invoke(process.execPath, [file], directory, []), /SCHEMA: Invalid parent IDs/);
});

test('unknown APIs and non-JSON output are rejected', async t => {
  const { directory, file } = fixture(t, `console.log(JSON.stringify({ api_version: 99, ok: true, diagnostics: [] }));`);
  await assert.rejects(invoke(process.execPath, [file], directory, []), /Unsupported/);
  writeFileSync(file, `console.log(JSON.stringify({ api_version: 1, ok: true, diagnostics: [] }));`);
  await assert.rejects(invoke(process.execPath, [file], directory, []), /requires API 7/);
  writeFileSync(file, `console.log('not json');`);
  await assert.rejects(invoke(process.execPath, [file], directory, []), /not json/);
});

test('lost mutation replies expose an unknown outcome and are never automatically retried', async t => {
  const { directory, file } = fixture(t, `console.log('lost response');`);
  await assert.rejects(invoke(process.execPath, [file], directory, ['delete', 'node']), /result needs verification.*inspect project/);
  writeFileSync(file, `setInterval(() => {}, 1000);`);
  await assert.rejects(invoke(process.execPath, [file], directory, ['update', 'node'], undefined, 100), /result needs verification/);
});

test('timeout and output budgets bound subprocesses', async t => {
  const { directory, file } = fixture(t, `setInterval(() => {}, 1000);`);
  await assert.rejects(invoke(process.execPath, [file], directory, [], undefined, 50), /timed out/);
  writeFileSync(file, `process.stdout.write('x'.repeat(4096));`);
  await assert.rejects(invoke(process.execPath, [file], directory, [], undefined, 5000, 64), /output limit/);
});
