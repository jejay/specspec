/* Run installed VS Code and Chromium UI checks in a disposable profile. */
const { spawn, execFileSync } = require('node:child_process');
const { existsSync, mkdtempSync, mkdirSync, rmSync, readFileSync, writeFileSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join, resolve } = require('node:path');
const { createServer } = require('node:net');
const { checkUI } = require('./ui.cjs');
const { fixture } = require('../../graph-ui-common/test-host/fixture.cjs');
const { platformChecks } = require('../../graph-ui-common/test-host/platform.cjs');
const { documentChecks } = require('./documents.cjs');
const { codeCli } = require('./install.cjs');
const { VSCODE_HOST_GUARD_MS } = require('../../graph-ui-common/test-host/budgets.cjs');

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
  const project = fixture(join(root, 'example/gantt'), python);
  // Canvas/Git regressions use the maintained example graph, independent of
  // changes to the self-referencing design graph. Native lifecycle uses a compact graph.
  const nativeRoot = join(project.root, 'native-documents'); mkdirSync(nativeRoot);
  const nativeCli = (args, input) => JSON.parse(execFileSync(python, ['-m', 'specspec', '--root', nativeRoot, ...args], { input, encoding: 'utf8' })).result;
  const manifesto = nativeCli(['init', '--json'], '# Native document fixture\n').changed_ids[0];
  const nativeNode = nativeCli(['add', '--parent', manifesto, '--json'], '# Native node\n').changed_ids[0];
  const nativeOther = nativeCli(['add', '--parent', nativeNode, '--json'], '# Other node\n').changed_ids[0];
  const nativeSnapshot = nativeCli(['query', '--json']).target;
  const otherPath = join(nativeRoot, nativeSnapshot.nodes.find(n => n.id === nativeOther).path);
  writeFileSync(otherPath, readFileSync(otherPath, 'utf8').replace(/\n/g, '\r\n'));
  const nativeProject = { root: nativeRoot, modified: nativeNode, cli: nativeCli };
  const profile = mkdtempSync(join(tmpdir(), 'specspec-vscode-host-'));
  const extensions = join(profile, 'extensions'), uiResult = join(profile, 'ui-result.json');
  const startupRoot = mkdtempSync(join(tmpdir(), 'specspec-vscode-startup-project-'));
  writeFileSync(join(startupRoot, 'AGENTS.md'), '# Existing owner instructions\n');
  const startup = { request: join(profile, 'startup-request.json'), response: join(profile, 'startup-response.json') };
  mkdirSync(extensions);
  // Opt in only within this disposable profile; retain phase/CLI diagnostics on failure.
  const userData = join(profile, 'user-data');
  mkdirSync(join(userData, 'User'), { recursive: true });
  writeFileSync(join(userData, 'User', 'settings.json'), JSON.stringify({ 'specspec.traceLoading': true,
    ...(process.env.SPECSPEC_TEST_COMMAND ? { 'specspec.command': process.env.SPECSPEC_TEST_COMMAND, 'specspec.args': [] } : {}) }));
  let developmentPath = join(root, 'vscode');
  if (process.env.SPECSPEC_TEST_VSIX) {
    // The tested product is installed normally. Only this tiny controller is a
    // development extension, so --extensionTestsPath can run the existing harness.
    developmentPath = join(profile, 'test-controller'); mkdirSync(developmentPath);
    writeFileSync(join(developmentPath, 'package.json'), JSON.stringify({ name: 'specspec-artifact-controller', publisher: 'specspec-test', version: '0.0.0', engines: { vscode: '^1.90.0' }, main: './index.cjs' }));
    writeFileSync(join(developmentPath, 'index.cjs'), 'exports.activate = () => {};');
    const cli = codeCli(executable);
    const installed = execFileSync(executable, [cli, `--user-data-dir=${userData}`, `--extensions-dir=${extensions}`, '--install-extension', resolve(process.env.SPECSPEC_TEST_VSIX), '--force'],
      { env: { ...process.env, ELECTRON_RUN_AS_NODE: '1' }, encoding: 'utf8', timeout: 60_000 });
    console.log(installed);
  }
  const native = { request: join(profile, 'native-request.json'), response: join(profile, 'native-response.json'), result: join(profile, 'native-result.json') };
  const env = { ...process.env, SPECSPEC_PYTHON: python, SPECSPEC_TEST_PROJECT_ROOT: project.root, SPECSPEC_UI_RESULT: uiResult,
    SPECSPEC_STARTUP_ROOT: startupRoot, SPECSPEC_STARTUP_REQUEST: startup.request, SPECSPEC_STARTUP_RESPONSE: startup.response,
    SPECSPEC_STARTUP_MISSING: join(profile, 'missing-specspec.exe'),
    SPECSPEC_NATIVE_REQUEST: native.request, SPECSPEC_NATIVE_RESPONSE: native.response, SPECSPEC_NATIVE_RESULT: native.result, SPECSPEC_NATIVE_NODE: nativeNode,
    SPECSPEC_NATIVE_PATH: join(nativeRoot, nativeSnapshot.nodes.find(n => n.id === nativeNode).path),
    SPECSPEC_NATIVE_OTHER: JSON.stringify({ id: nativeOther, path: join(nativeRoot, nativeSnapshot.nodes.find(n => n.id === nativeOther).path) }),
    ...(process.env.SPECSPEC_TEST_VSIX ? { SPECSPEC_ARTIFACT_EXTENSIONS_DIR: extensions } : {}) };
  delete env.ELECTRON_RUN_AS_NODE;
  const child = spawn(executable, [
    '--new-window', '--skip-welcome', '--skip-release-notes', '--disable-workspace-trust',
    `--user-data-dir=${userData}`, `--extensions-dir=${extensions}`,
    `--extensionDevelopmentPath=${developmentPath}`, `--extensionTestsPath=${join(__dirname, 'smoke.cjs')}`,
    `--remote-debugging-port=${port}`, '--remote-debugging-address=127.0.0.1',
    // Unknown Code switches need explicit values; a bare final switch consumes
    // the following project path as its value and launches an empty window.
    '--disable-background-timer-throttling=true', '--disable-renderer-backgrounding=true', '--disable-backgrounding-occluded-windows=true',
    project.root,
  ], { cwd: root, env, stdio: ['ignore', 'pipe', 'pipe'] });
  let smokePassed = false, uiPassed = false, markerBuffer = '';
  child.stdout.on('data', chunk => {
    const text = chunk.toString(); process.stdout.write(text); markerBuffer = (markerBuffer + text).slice(-4096);
    if (markerBuffer.includes('SPECSPEC_REAL_HOST_SMOKE_OK')) smokePassed = true;
  });
  child.stderr.on('data', chunk => process.stderr.write(chunk));
  const ui = (async () => {
    const startupCli = args => JSON.parse(execFileSync(python, ['-m', 'specspec', '--root', startupRoot, ...args], { encoding: 'utf8' })).result;
    await require('../../graph-ui-common/test-host/startup.cjs').startupChecks(port, { root: startupRoot, cli: startupCli,
      restore: async () => {
        writeFileSync(startup.request, JSON.stringify({ action: 'restore' }));
        const until = Date.now() + 30000;
        while (Date.now() < until) {
          try { if (JSON.parse(readFileSync(startup.response, 'utf8')).stage === 'restored') return; } catch {}
          await new Promise(resolve => setTimeout(resolve, 50));
        }
        throw new Error('The disposable profile did not restore its CLI configuration.');
      } });
    writeFileSync(startup.request, JSON.stringify({ action: 'done' }));
    if (!process.env.SPECSPEC_NATIVE_ONLY) await checkUI(port, platformChecks(project, 'vscode'));
    writeFileSync(uiResult, JSON.stringify({ ok: true }));
    await documentChecks(port, nativeProject, native);
    uiPassed = true; writeFileSync(native.result, JSON.stringify({ ok: true }));
  })().catch(error => {
    console.error('Real webview UI test failed:', error);
    const result = JSON.stringify({ ok: false, error: error.message });
    writeFileSync(uiResult, result); writeFileSync(native.result, result);
    child.kill(); // A known failed phase terminates promptly; preserve the profile.
  });
  // Sum the shared/native phase allowances and startup/shutdown, while retaining
  // every individual assertion and operation deadline.
  const timer = setTimeout(() => { console.error(`VS Code host smoke exceeded its ${VSCODE_HOST_GUARD_MS}ms aggregate guard.`); child.kill(); }, VSCODE_HOST_GUARD_MS);
  child.on('error', error => { console.error(error); process.exitCode = 1; });
  child.on('close', async code => {
    clearTimeout(timer); await ui;
    process.exitCode = code === 0 && smokePassed && uiPassed ? 0 : 1;
    if (!smokePassed) console.error('The host did not confirm a successful rendering/UI smoke test.');
    if (process.exitCode) { console.error(`Isolated diagnostic profile retained at ${profile}; startup project ${startupRoot}`); return; }
    try { project.cleanup(); rmSync(startupRoot, { recursive: true, force: true, maxRetries: 20, retryDelay: 100 }); rmSync(profile, { recursive: true, force: true, maxRetries: 20, retryDelay: 200 }); }
    catch (error) { console.warn(`Temporary VS Code profile retained at ${profile}: ${error.message}`); }
  });
}
run().catch(error => { console.error(error); process.exitCode = 1; });
