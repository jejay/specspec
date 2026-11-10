/* Take the README screenshots of both graph editors.

   node tools/readme_screenshots.cjs            # both
   node tools/readme_screenshots.cjs vscode     # docs/images/editor-vscode.png and -small.png
   node tools/readme_screenshots.cjs desktop    # docs/images/editor-desktop.png and -small.png

   Build the editors first (npm run build). Each host starts in an isolated, disposable
   profile and is captured through the DevTools protocol on the loopback interface.
   VS Code shows this repository's own graph; the desktop app shows an independent clone
   of the Gantt example while two of its stages are compared. SPECSPEC_PYTHON and
   VSCODE_EXECUTABLE override the development interpreter and the installed VS Code.

   VS Code also loads this file inside its extension host, where it only opens the graph
   and waits for the capture to finish. */
const { existsSync, mkdtempSync, mkdirSync, readdirSync, rmSync, writeFileSync } = require('node:fs');
const { join, relative, resolve } = require('node:path');

const ROOT = resolve(__dirname, '..');
const delay = ms => new Promise(done => setTimeout(done, ms));
const SCALE = 2; // twice the display resolution, for sharp images when opened full size
const SMALL = 0.5; // half of it, for the small versions under the README's introduction

if (require.main !== module) {
  exports.run = async function run() {
    const vscode = require('vscode');
    const root = process.env.SPECSPEC_SHOT_PROJECT;
    await vscode.commands.executeCommand('workbench.action.closeAuxiliaryBar');
    await vscode.commands.executeCommand('workbench.action.closePanel');
    await vscode.commands.executeCommand('specspec.openGraph', vscode.Uri.file(root));
    const first = readdirSync(join(root, '.specspec')).filter(name => name.endsWith('.md')).sort()[0];
    await vscode.commands.executeCommand('revealInExplorer', vscode.Uri.file(join(root, '.specspec', first)));
    await vscode.commands.executeCommand('workbench.action.focusActiveEditorGroup');
    const until = Date.now() + 240_000;
    while (!existsSync(process.env.SPECSPEC_SHOT_DONE) && Date.now() < until) {
      // Startup notifications would cover the canvas.
      await vscode.commands.executeCommand('notifications.clearAll');
      await delay(300);
    }
  };
} else {
  main().catch(error => { console.error(error); process.exitCode = 1; });
}

async function main() {
  const { execFileSync, spawn } = require('node:child_process');
  const { tmpdir } = require('node:os');
  const { createServer } = require('node:net');
  const { CDP } = require('../graph-ui-common/test-host/ui.cjs');

  const which = process.argv[2] || 'all';
  if (!['all', 'vscode', 'desktop'].includes(which)) throw new Error('Usage: readme_screenshots.cjs [vscode|desktop]');
  const python = process.env.SPECSPEC_PYTHON
    || join(ROOT, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
  if (!existsSync(python)) throw new Error('Create the development virtual environment or set SPECSPEC_PYTHON.');
  const images = join(ROOT, 'docs', 'images');
  const freePort = () => new Promise(done => {
    const server = createServer();
    server.listen(0, '127.0.0.1', () => { const { port } = server.address(); server.close(() => done(port)); });
  });
  const targets = async port => (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const remove = path => { try { rmSync(path, { recursive: true, force: true, maxRetries: 30, retryDelay: 200 }); } catch { /* keep */ } };
  // Capture the posed page at full and at small scale; the layout stays the same.
  const save = async (client, name, width, height) => {
    for (const [scale, file] of [[SCALE, `${name}.png`], [SMALL, `${name}-small.png`]]) {
      await client.send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: scale, mobile: false });
      await delay(700);
      const image = await client.send('Page.captureScreenshot', { format: 'png' });
      writeFileSync(join(images, file), Buffer.from(image.data, 'base64'));
      console.log(`docs/images/${file}`);
    }
  };
  const pose = (evaluate, mode) => evaluate(
    `const s=document.getElementById('color-mode');s.value=${JSON.stringify(mode)};s.dispatchEvent(new Event('change'));`
    + `document.getElementById('frame-all').click()`);

  async function desktop() {
    const work = mkdtempSync(join(tmpdir(), 'specspec-shot-desktop-'));
    const project = join(work, 'gantt'), profile = join(work, 'profile');
    execFileSync(python, [join(ROOT, 'example/gantt/history/checkout.py'), project], { stdio: 'ignore' });
    const port = await freePort(), launch = join(ROOT, 'electron');
    const env = { ...process.env }; delete env.ELECTRON_RUN_AS_NODE;
    const child = spawn(require('electron'), [launch, '--project', project, '--python', relative(launch, python),
      '--profile', profile, `--remote-debugging-port=${port}`, '--remote-debugging-address=127.0.0.1',
      '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--disable-backgrounding-occluded-windows'],
    { cwd: launch, env, stdio: 'ignore' });
    const exit = new Promise(done => child.on('close', done));
    let client;
    try {
      let page;
      for (let i = 0; i < 400 && !page; i++) {
        try { page = (await targets(port)).find(target => target.url === 'specspec://app/index.html'); } catch { /* starting */ }
        if (!page) await delay(150);
      }
      if (!page) throw new Error('The desktop window did not appear. Run npm run build first.');
      client = new CDP(page.webSocketDebuggerUrl);
      const evaluate = async expression => {
        const reply = await client.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
        if (reply.exceptionDetails) throw new Error(reply.exceptionDetails.exception?.description || reply.exceptionDetails.text);
        return reply.result.value;
      };
      const waitFor = async (expression, what) => {
        for (let i = 0; i < 400; i++) { if (await evaluate(expression)) return; await delay(100); }
        throw new Error(`Timed out waiting for ${what}.`);
      };
      await waitFor(`document.querySelectorAll('#cards .card').length > 0`, 'the graph');
      await client.send('Emulation.setDeviceMetricsOverride', { width: 1240, height: 800, deviceScaleFactor: SCALE, mobile: false });
      await client.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] });
      await evaluate(`document.getElementById('compare').click()`);
      await waitFor(`Boolean(document.querySelector('dialog[aria-label="Compare revisions"]')?.open)`, 'the comparison dialog');
      await evaluate(`const inputs=document.querySelectorAll('dialog input');inputs[0].value='stage/02-code';inputs[1].value='stage/03-spec';`
        + `document.querySelector('dialog button[value="apply"]').click()`);
      await waitFor(`document.getElementById('revision').textContent.includes('stage/03-spec')`, 'the comparison');
      await pose(evaluate, 'git-revision');
      await delay(1000);
      // Frame the part of the graph where the redirect replaced whole branches.
      // The rectangle starts in the gap above a row, three rows over the deeper columns.
      const [left, top, right, bottom] = await evaluate(`(() => {
        const boxes=[...document.querySelectorAll('#cards .card')].map(card=>card.getBoundingClientRect());
        const columns=[...new Set(boxes.map(box=>Math.round(box.left)))].sort((a,b)=>a-b);
        const first=boxes.filter(box=>Math.round(box.left)===columns[1]).sort((a,b)=>a.top-b.top);
        const deep=boxes.filter(box=>Math.round(box.left)>=columns[2]);
        const gap=first[1].top-first[0].bottom, deepTop=Math.min(...deep.map(box=>box.top));
        const row=first[Math.max(0, first.filter(box=>box.top<deepTop).length-3)];
        return [columns[1]-14, row.top-gap/2, Math.max(...deep.map(box=>box.right))+14, Math.max(...boxes.map(box=>box.bottom))+gap/2+26];
      })()`);
      await evaluate(`document.getElementById('frame-area').click()`);
      await delay(200);
      const mouse = (type, x, y, buttons) => client.send('Input.dispatchMouseEvent', { type, x, y, button: 'left', buttons, clickCount: 1 });
      await mouse('mouseMoved', left, top, 0); await mouse('mousePressed', left, top, 1);
      for (let i = 1; i <= 8; i++) await mouse('mouseMoved', left + (right - left) * i / 8, top + (bottom - top) * i / 8, 1);
      await mouse('mouseReleased', right, bottom, 0);
      await delay(1200);
      // Framing leaves a margin that cuts the row above; slide the graph up until the edge falls in a gap.
      const [edge, cut, spot] = await evaluate(`(() => {
        const edge=document.getElementById('legend').getBoundingClientRect().bottom;
        const boxes=[...document.querySelectorAll('#cards .card:not(.manifesto)')].map(card=>card.getBoundingClientRect());
        const cut=boxes.filter(box=>box.top<edge&&box.bottom>edge).map(box=>box.bottom);
        return [edge, cut.length?Math.max(...cut):0, Math.max(...boxes.map(box=>box.right))+60];
      })()`);
      if (cut) {
        const from = edge + 240, to = from - (cut - edge + 8);
        await mouse('mouseMoved', spot, from, 0); await mouse('mousePressed', spot, from, 1);
        for (let i = 1; i <= 6; i++) await mouse('mouseMoved', spot, from + (to - from) * i / 6, 1);
        await mouse('mouseReleased', spot, to, 0);
        await delay(600);
      }
      await save(client, 'editor-desktop', 1240, 800);
    } finally {
      client?.close(); child.kill(); await exit; remove(work);
    }
  }

  async function vscode() {
    const executable = process.env.VSCODE_EXECUTABLE || (process.platform === 'win32' ? [
      join(process.env.LOCALAPPDATA || '', 'Programs/Microsoft VS Code/Code.exe'),
      join(process.env.ProgramFiles || '', 'Microsoft VS Code/Code.exe'),
    ] : process.platform === 'darwin' ? ['/Applications/Visual Studio Code.app/Contents/MacOS/Electron']
      : ['/usr/share/code/code', '/usr/lib/code/code']).find(existsSync);
    if (!executable || !existsSync(executable)) throw new Error('Set VSCODE_EXECUTABLE to your installed VS Code executable.');
    const profile = mkdtempSync(join(tmpdir(), 'specspec-shot-vscode-'));
    const userData = join(profile, 'user-data'), extensions = join(profile, 'extensions'), done = join(profile, 'done');
    mkdirSync(join(userData, 'User'), { recursive: true }); mkdirSync(extensions);
    writeFileSync(join(userData, 'User', 'settings.json'), JSON.stringify({
      'workbench.colorTheme': 'Default Dark Modern', 'workbench.startupEditor': 'none', 'window.zoomLevel': 0,
      // The native title bar stays outside the captured page, with the development-host title.
      'window.titleBarStyle': 'native', 'window.commandCenter': false, 'workbench.layoutControl.enabled': false,
      'telemetry.telemetryLevel': 'off', 'update.mode': 'none', 'extensions.autoUpdate': false,
      'extensions.ignoreRecommendations': true, 'workbench.tips.enabled': false, 'chat.disableAIFeatures': true,
      // Keep the picture independent of the checkout's uncommitted state.
      'git.enabled': false,
      'files.exclude': { '**/.git': true, '**/.venv': true, '**/node_modules': true, '**/dist': true, '**/.pytest_cache': true, '**/.ruff_cache': true },
    }));
    const port = await freePort();
    const env = { ...process.env, SPECSPEC_PYTHON: python, SPECSPEC_SHOT_PROJECT: ROOT, SPECSPEC_SHOT_DONE: done };
    delete env.ELECTRON_RUN_AS_NODE;
    const child = spawn(executable, [
      '--new-window', '--skip-welcome', '--skip-release-notes', '--disable-workspace-trust',
      `--user-data-dir=${userData}`, `--extensions-dir=${extensions}`,
      `--extensionDevelopmentPath=${join(ROOT, 'vscode')}`, `--extensionTestsPath=${__filename}`,
      `--remote-debugging-port=${port}`, '--remote-debugging-address=127.0.0.1',
      '--disable-background-timer-throttling=true', '--disable-renderer-backgrounding=true', '--disable-backgrounding-occluded-windows=true',
      ROOT,
    ], { cwd: ROOT, env, stdio: 'ignore' });
    const exit = new Promise(done => child.on('close', done));
    const clients = new Map();
    try {
      // The graph lives in a webview frame; the capture is of the whole workbench page.
      let graph, context, workbench;
      const until = Date.now() + 120_000;
      while ((!graph || !workbench) && Date.now() < until) {
        try {
          for (const target of await targets(port)) {
            if (!target.webSocketDebuggerUrl || clients.has(target.id)) continue;
            const client = new CDP(target.webSocketDebuggerUrl); client.target = target; clients.set(target.id, client);
            await client.send('Runtime.enable');
            await client.send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true }).catch(() => {});
          }
          for (const client of clients.values()) {
            if (client.target.type === 'page' && /workbench/.test(client.target.url)) workbench = client;
            for (const candidate of client.contexts.values()) {
              try {
                if (await client.evaluate(candidate, `typeof document !== 'undefined' && !!window.specspecHost && !!document.querySelector('#cards .card.manifesto')`)) { graph = client; context = candidate; }
              } catch { /* another frame */ }
            }
          }
        } catch { /* starting */ }
        if (!graph || !workbench) await delay(200);
      }
      if (!graph || !workbench) throw new Error('VS Code did not show the graph. Run npm run build first.');
      const evaluate = expression => graph.evaluate(context, expression);
      await workbench.send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 800, deviceScaleFactor: SCALE, mobile: false });
      await graph.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] }, context.session).catch(() => {});
      await delay(1500);
      await pose(evaluate, 'distance');
      await delay(1500);
      await save(workbench, 'editor-vscode', 1280, 800);
    } finally {
      writeFileSync(done, 'done');
      const timer = setTimeout(() => child.kill(), 15_000);
      await exit; clearTimeout(timer);
      for (const client of clients.values()) { try { client.close(); } catch { /* closed */ } }
      remove(profile);
    }
  }

  if (which !== 'vscode') await desktop();
  if (which !== 'desktop') await vscode();
}
