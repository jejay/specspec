/* Qualify startup independently from the maintained existing-graph interaction suite. */
const { spawn, execFileSync } = require('node:child_process');
const { mkdtempSync, writeFileSync, rmSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join, relative } = require('node:path');
const { createServer } = require('node:net');
const { startupChecks } = require('../../graph-ui-common/test-host/startup.cjs');

async function startupHosts({ executable, launchDirectory, env, python }) {
  for (const missing of [true, false]) {
    const profile = mkdtempSync(join(tmpdir(), 'specspec-desktop-startup-profile-'));
    const root = mkdtempSync(join(tmpdir(), 'specspec-desktop-startup-project-'));
    writeFileSync(join(root, 'AGENTS.md'), '# Existing owner instructions\n');
    const port = await new Promise(resolve => { const server = createServer(); server.listen(0, '127.0.0.1', () => { const port = server.address().port; server.close(() => resolve(port)); }); });
    const args = [...(process.env.SPECSPEC_DESKTOP_EXECUTABLE ? [] : [launchDirectory]),
      ...(missing ? ['--python', join(profile, 'missing-python.exe')] : ['--project', root,
        ...(process.env.SPECSPEC_TEST_COMMAND ? [] : ['--python', relative(launchDirectory, python)])]),
      '--profile', profile, `--remote-debugging-port=${port}`, '--remote-debugging-address=127.0.0.1'];
    const child = spawn(executable, args, { cwd: launchDirectory, env, stdio: ['ignore', 'pipe', 'pipe'] });
    child.stdout.on('data', data => process.stdout.write(data)); child.stderr.on('data', data => process.stderr.write(data));
    const exit = new Promise((resolve, reject) => { child.on('error', reject); child.on('close', resolve); });
    const timer = setTimeout(() => child.kill(), 90000); let ok = false;
    try {
      const cli = args => JSON.parse(execFileSync(python, ['-m', 'specspec', '--root', root, ...args], { encoding: 'utf8' })).result;
      await startupChecks(port, { root: missing ? '' : root, missing, initialize: !missing, cli });
      console.log(missing ? 'SPECSPEC_DESKTOP_MISSING_CLI_OK: checked before project selection.' : 'SPECSPEC_DESKTOP_INITIALIZATION_OK'); ok = true;
    } finally {
      clearTimeout(timer); child.kill(); await exit;
      if (ok) for (const path of [profile, root]) rmSync(path, { recursive: true, force: true, maxRetries: 30, retryDelay: 100 });
      else console.error('Startup diagnostics retained:', profile, root);
    }
  }
}
module.exports = { startupHosts };
