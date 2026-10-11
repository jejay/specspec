/* Installed VS Code: native documents, not a mocked custom-editor provider. */
const assert = require('node:assert/strict');
const { readFileSync, writeFileSync, existsSync, mkdirSync } = require('node:fs');
const { join } = require('node:path');
const { CDP } = require('../../graph-ui-common/test-host/ui.cjs');
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

exports.documentChecks = async function documentChecks(port, project, paths) {
  const clients = new Map(); let sequence = 0;
  async function request(action = 'inspect', extra = {}) {
    const id = ++sequence; writeFileSync(paths.request, JSON.stringify({ id, action, ...extra }));
    for (let i = 0; i < 200; i++) {
      if (existsSync(paths.response)) {
        let response; try { response = JSON.parse(readFileSync(paths.response, 'utf8')); } catch {}
        if (response?.id === id) { assert.equal(response.error, undefined); return response; }
      }
      await delay(50);
    }
    throw new Error(`Extension-host document request timed out: ${action}`);
  }
  async function contexts(id) {
    let targets;
    try { targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); } catch { return []; }
    for (const target of targets) if (target.webSocketDebuggerUrl && !clients.has(target.id)) {
      const client = new CDP(target.webSocketDebuggerUrl); clients.set(target.id, client);
      await client.send('Runtime.enable'); await client.send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true }).catch(() => {});
    }
    const found = [], seen = new Set();
    for (const client of clients.values()) for (const context of client.contexts.values()) {
      try {
        const probe = await client.evaluate(context, `typeof document!=='undefined'&&!!window.SpecSpecHost&&({url:location.href,identity:document.getElementById('identity')?.textContent,save:document.getElementById('save')?.textContent,message:document.getElementById('message')?.textContent,state:window.SpecSpecHost.getState()})`, 500);
        if (probe && probe.save === 'Save file' && probe.identity?.includes(id)) {
          if (!seen.has(probe.url)) { found.push({ client, context }); seen.add(probe.url); }
        }

      } catch { /* Frames that have navigated or aren't the custom editor. */ }
    }
    return found;
  }
  async function waitFor(check, label) {
    const until = Date.now() + 45_000;
    while (Date.now() < until) { if (await check()) return; await delay(50); }
    throw new Error(`Native document check timed out: ${label}`);
  }
  async function screenshot(name) {
    const directory = process.env.SPECSPEC_SCREENSHOT_DIR;
    if (!directory) return;
    const client = clients.values().next().value;
    const image = await client.send('Page.captureScreenshot', { format: 'png' });
    mkdirSync(directory, { recursive: true }); writeFileSync(join(directory, `${name}.png`), Buffer.from(image.data, 'base64'));
  }
  try {
    let view;
    await waitFor(async () => { view = (await contexts(project.modified))[0]; return view; }, 'default file editor');
    try { await view.client.send('Page.bringToFront'); } catch {}
    const evaluate = code => view.client.evaluate(view.context, code);
    const node = project.cli(['show', project.modified, '--json']).node;
    const path = join(project.root, node.path), before = readFileSync(path, 'utf8');
    const draft = '# Native VS Code draft 🐕\n';
    await evaluate(`document.getElementById('body').value=${JSON.stringify(draft)};document.getElementById('body').dispatchEvent(new Event('input'));document.getElementById('body').focus();document.getElementById('body').setSelectionRange(2,8)`);
    await waitFor(async () => { const d = await request(); return d.dirty && d.text.endsWith(draft); }, 'native dirty buffer');
    assert.equal(readFileSync(path, 'utf8'), before, 'Typing must not write the file through the CLI.');
    await waitFor(() => evaluate(`!window.SpecSpecHost.getState().dirty`), 'form acknowledgement');
    assert.deepEqual(await evaluate(`[document.getElementById('body').selectionStart,document.getElementById('body').selectionEnd]`), [2,8]);
    let native = await request();
    assert.ok(native.tabs.some(t => t.type === 'specspec.graphEditor'));
    await request('undo');
    await waitFor(async () => (await request()).text === before, 'native undo');
    await request('redo');
    await waitFor(async () => (await request()).text.endsWith(draft), 'native redo');
    await waitFor(() => evaluate(`document.getElementById('body').value===${JSON.stringify(draft)}`), 'undo/redo view synchronization');
    await evaluate(`document.getElementById('save').click()`);
    await waitFor(async () => !(await request()).dirty && readFileSync(path, 'utf8').endsWith(draft), 'native save');
    await screenshot('vscode-native-node-editor');

    await request('split');
    await waitFor(async () => (await contexts(project.modified)).length >= 2, 'split custom editors');
    const splitViews = await contexts(project.modified);
    view = splitViews[0];
    const split = splitViews[1];
    const splitEvaluate = code => split.client.evaluate(split.context, code);
    await request('raw', { before: draft, after: '# Native raw edit\n' });
    await waitFor(() => evaluate(`document.getElementById('body').value==='# Native raw edit\\n'`), 'raw edit in first view');
    await waitFor(() => splitEvaluate(`document.getElementById('body').value==='# Native raw edit\\n'`), 'raw edit in split view');
    // Different cameras must not become one shared project presentation state.
    await evaluate(`document.getElementById('zoom-in').click()`); await delay(400);
    assert.notEqual(await evaluate(`document.getElementById('viewport').dataset.scale`), await splitEvaluate(`document.getElementById('viewport').dataset.scale`));

    await evaluate(`document.getElementById('body').value='';document.getElementById('body').dispatchEvent(new Event('input'))`);
    await waitFor(() => evaluate(`!document.getElementById('sync-notice').hidden`), 'invalid native buffer diagnostics');
    assert.equal(await evaluate(`document.getElementById('body').readOnly`), false);
    await evaluate(`document.getElementById('body').value='# Repaired native document\\n';document.getElementById('body').dispatchEvent(new Event('input'))`);
    await waitFor(() => evaluate(`document.getElementById('sync-notice').hidden&&!window.SpecSpecHost.getState().dirty`), 'native repair');
    await evaluate(`document.getElementById('save').click()`);
    await waitFor(async () => !(await request()).dirty && readFileSync(path, 'utf8').endsWith('# Repaired native document\n'), 'repaired file save');
    const other = await request('other');
    await waitFor(async () => (await contexts(other.otherId)).length > 0, 'different node tab');
    const otherView = (await contexts(other.otherId))[0];
    assert.notEqual(await otherView.client.evaluate(otherView.context, `document.getElementById('body').value`), '# Repaired native document\n');
    const otherEvaluate = code => otherView.client.evaluate(otherView.context, code);
    const otherBefore = (await request('inspect-other')).otherDocument;
    assert.ok(otherBefore.text.includes('\r\n'));
    await otherEvaluate(`document.getElementById('body').value='# CRLF typed 🐕\\n';document.getElementById('body').dispatchEvent(new Event('input'))`);
    await waitFor(async () => { const d = (await request('inspect-other')).otherDocument; return d.dirty && d.text.endsWith('# CRLF typed 🐕\r\n'); }, 'native CRLF buffer');
    assert.equal(readFileSync(otherBefore.path, 'utf8'), otherBefore.text);
    await otherEvaluate(`document.getElementById('save').click()`);
    await waitFor(async () => { const d = (await request('inspect-other')).otherDocument; return !d.dirty && readFileSync(d.path, 'utf8').endsWith('# CRLF typed 🐕\r\n'); }, 'native CRLF save');
    await waitFor(() => otherEvaluate(`document.getElementById('body').value==='# CRLF typed 🐕\\n'&&!/Refreshing/.test(document.getElementById('message').textContent)`), 'CRLF form agrees with native buffer');
    await screenshot('vscode-independent-node-tabs');
    console.log('VS Code: default custom editor, native dirty/save/undo/redo, split synchronization, independent cameras, raw edits, invalid-buffer repair, CRLF/Unicode saves and different node tabs passed.');
  } catch (error) {
    const client = clients.values().next().value;
    if (client) try {
      const image = await client.send('Page.captureScreenshot', { format: 'png' });
      writeFileSync(join(require('node:os').tmpdir(), 'specspec-native-debug.png'), Buffer.from(image.data, 'base64'));
    } catch {}
    throw error;
  } finally { clients.forEach(client => client.close()); }
};
