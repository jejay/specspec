/* Run installed VS Code and Chromium UI checks in a disposable profile. */
const { spawn } = require('node:child_process');
const { existsSync, mkdtempSync, mkdirSync, rmSync, writeFileSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join, resolve } = require('node:path');
const { createServer } = require('node:net');
const { checkUI } = require('./ui.cjs');

async function run() {
  const root = resolve(__dirname, '../..');
  const executable = process.env.VSCODE_EXECUTABLE || (process.platform === 'win32' ? [
    join(process.env.LOCALAPPDATA || '', 'Programs/Microsoft VS Code/Code.exe'),
    join(process.env.ProgramFiles || '', 'Microsoft VS Code/Code.exe'),
  ] : process.platform === 'darwin' ? ['/Applications/Visual Studio Code.app/Contents/MacOS/Electron']
    : ['/usr/share/code/code', '/usr/lib/code/code']).find(existsSync);
  const python = process.env.SPECSPEC_PYTHON || join(root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
  if (!executable || !existsSync(executable)) throw new Error('Set VSCODE_EXECUTABLE to your installed VS Code executable.');
  if (!existsSync(python)) throw new Error('Create the development virtual environment or set SPECSPEC_PYTHON.');
  if (typeof WebSocket === 'undefined') throw new Error('The real UI test runner requires Node 22+ (native WebSocket).');

  const port = await new Promise((resolve, reject) => {
    const server = createServer(); server.on('error', reject);
    server.listen(0, '127.0.0.1', () => { const port = server.address().port; server.close(() => resolve(port)); });
  });
  const profile = mkdtempSync(join(tmpdir(), 'specspec-vscode-host-'));
  const extensions = join(profile, 'extensions'), uiResult = join(profile, 'ui-result.json');
  mkdirSync(extensions);
  const env = { ...process.env, SPECSPEC_PYTHON: python, SPECSPEC_TEST_PROJECT_ROOT: root, SPECSPEC_UI_RESULT: uiResult };
  delete env.ELECTRON_RUN_AS_NODE;
  const child = spawn(executable, [
    '--new-window', '--skip-welcome', '--skip-release-notes', '--disable-workspace-trust',
    `--user-data-dir=${join(profile, 'user-data')}`, `--extensions-dir=${extensions}`,
    `--extensionDevelopmentPath=${join(root, 'vscode')}`, `--extensionTestsPath=${join(__dirname, 'smoke.cjs')}`,
    `--remote-debugging-port=${port}`, '--remote-debugging-address=127.0.0.1',
    join(root, 'specspec-dev.code-workspace'),
  ], { cwd: root, env, stdio: ['ignore', 'pipe', 'pipe'] });
  let smokePassed = false, uiPassed = false, markerBuffer = '';
  child.stdout.on('data', chunk => {
    const text = chunk.toString(); process.stdout.write(text); markerBuffer = (markerBuffer + text).slice(-4096);
    if (markerBuffer.includes('SPECSPEC_REAL_HOST_SMOKE_OK')) smokePassed = true;
  });
  child.stderr.on('data', chunk => process.stderr.write(chunk));
  const ui = checkUI(port).then(() => {
    uiPassed = true; writeFileSync(uiResult, JSON.stringify({ ok: true }));
  }, error => {
    console.error('Real webview UI test failed:', error);
    writeFileSync(uiResult, JSON.stringify({ ok: false, error: error.message }));
  });
  const timer = setTimeout(() => { console.error('VS Code host smoke test timed out.'); child.kill(); }, 120_000);
  child.on('error', error => { console.error(error); process.exitCode = 1; });
  child.on('close', async code => {
    clearTimeout(timer); await ui;
    process.exitCode = code === 0 && smokePassed && uiPassed ? 0 : 1;
    if (!smokePassed) console.error('The host did not confirm a successful rendering/UI smoke test.');
    if (process.exitCode) { console.error(`Isolated diagnostic profile retained at ${profile}`); return; }
    try { rmSync(profile, { recursive: true, force: true, maxRetries: 20, retryDelay: 200 }); }
    catch (error) { console.warn(`Temporary VS Code profile retained at ${profile}: ${error.message}`); }
  });
}
run().catch(error => { console.error(error); process.exitCode = 1; });
