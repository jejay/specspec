/* Real Electron, isolated profile + disposable CLI/Git graph + loopback CDP only. */
const { spawn } = require('node:child_process');
const { mkdtempSync, existsSync, rmSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join, resolve, relative } = require('node:path');
const { createServer } = require('node:net');
const { checkUI, CDP } = require('../../graph-ui-common/test-host/ui.cjs');
const { fixture } = require('../../graph-ui-common/test-host/fixture.cjs');
const { platformChecks } = require('../../graph-ui-common/test-host/platform.cjs');
const assert = require('node:assert/strict');
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
async function run() {
  const source = resolve(__dirname, '../..');
  const python = process.env.SPECSPEC_PYTHON || join(source, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
  if (!existsSync(python)) throw new Error('Set SPECSPEC_PYTHON to an installed CLI interpreter.');
  const project = fixture(join(source, 'example/gantt'), python), profile = mkdtempSync(join(tmpdir(), 'specspec-electron-host-'));
  const port = await new Promise(resolve => { const server = createServer(); server.listen(0, '127.0.0.1', () => { const p = server.address().port; server.close(() => resolve(p)); }); });
  const env = { ...process.env }; delete env.ELECTRON_RUN_AS_NODE;
  const executable = process.env.SPECSPEC_DESKTOP_EXECUTABLE || require('electron');
  const launchDirectory = resolve(__dirname, '..');
  const child = spawn(executable, [...(process.env.SPECSPEC_DESKTOP_EXECUTABLE ? [] : [launchDirectory]), '--project', project.root, '--python', relative(launchDirectory, python), '--profile', profile,
    `--remote-debugging-port=${port}`, '--remote-debugging-address=127.0.0.1'], { cwd: launchDirectory, env, stdio: ['ignore', 'pipe', 'pipe'] });
  child.stdout.on('data', d => process.stdout.write(d)); child.stderr.on('data', d => process.stderr.write(d));
  const exit = new Promise((resolve, reject) => { child.on('error', reject); child.on('close', resolve); });
  const timer = setTimeout(() => child.kill(), 180_000);
  let ok = false;
  try {
    await checkUI(port, platformChecks(project, 'electron'));
    const target = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find(t => t.url === 'specspec://app/index.html');
    assert.ok(target); const client = new CDP(target.webSocketDebuggerUrl);
    try {
      const evaluate = async expression => {
        const r = await client.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
        if (r.exceptionDetails) throw new Error(r.exceptionDetails.text); return r.result.value;
      };
      for(let i=0;i<300;i++){if(await evaluate(`document.getElementById('body')?.value==='# Retained stale desktop draft'`))break;await delay(100);}
      assert.equal(await evaluate(`document.getElementById('body').value`),'# Retained stale desktop draft');
      assert.ok(await evaluate(`window.SpecSpecHost.getState().dirty`));
      await evaluate(`document.getElementById('discard').click();document.getElementById('compare').click()`);await delay(200);
      assert.ok(await evaluate(`document.querySelector('dialog').open`));
      await evaluate(`const inputs=document.querySelectorAll('dialog input');inputs[0].value='HEAD';inputs[1].value='HEAD';document.querySelector('dialog button[value="apply"]').click()`);
      for(let i=0;i<500;i++){if(await evaluate(`document.getElementById('revision').textContent.includes('read-only')`))break;await delay(100);}
      assert.ok(await evaluate(`document.getElementById('revision').textContent.includes('read-only')`), JSON.stringify(await evaluate(`({revision:document.getElementById('revision').textContent,message:document.getElementById('message').textContent,dialog:document.querySelector('dialog').open,returnValue:document.querySelector('dialog').returnValue})`)));
      assert.ok(await evaluate(`document.getElementById('save').disabled`));
      await evaluate(`document.getElementById('workspace').click()`);
      for(let i=0;i<500;i++){if(await evaluate(`!document.getElementById('revision').textContent.includes('read-only')`))break;await delay(100);}
      assert.ok(!await evaluate(`document.getElementById('revision').textContent.includes('read-only')`));
    } finally { client.close(); }
    project.cli(['validate','--warnings-as-errors','--json']);
    console.log('SPECSPEC_ELECTRON_HOST_OK: real canvas, themed A/M/D, sandbox/blocked network, actual save, watcher-only manual/invalid-file sync, persisted draft reload and historical/workspace switching.'); ok = true;
  } finally {
    clearTimeout(timer); child.kill(); await exit;
    if (ok) { project.cleanup(); rmSync(profile, { recursive: true, force: true, maxRetries: 30, retryDelay: 200 }); }
    else console.error(`Diagnostics retained: ${profile}; graph ${project.root}`);
  }
}
run().catch(error => { console.error(error); process.exitCode = 1; });
