/* Real installed-host startup, before any existing-graph canvas assertions. */
const assert = require('node:assert/strict');
const { existsSync, readFileSync } = require('node:fs');
const { join } = require('node:path');
const { CDP } = require('./ui.cjs');
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

async function startupChecks(port, { root = '', missing = true, restore, initialize = true, cli }) {
  const clients = new Map(); let active, context;
  try {
    const until = Date.now() + 60000;
    while (!active && Date.now() < until) {
      try {
        for (const target of await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()) {
          if (!target.webSocketDebuggerUrl || clients.has(target.id)) continue;
          const client = new CDP(target.webSocketDebuggerUrl); clients.set(target.id, client);
          await client.send('Runtime.enable');
          await client.send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true }).catch(() => {});
        }
        for (const client of clients.values()) {
          for (const candidate of client.contexts.values()) {
            try {
              if (await client.evaluate(candidate, `typeof document !== 'undefined' && !!window.specspecHost && !!document.getElementById('startup') && String(document.querySelector('meta[name="specspec-project"]')?.content || '')${process.platform === 'win32' ? '.toLowerCase()' : ''} === ${JSON.stringify(process.platform === 'win32' ? root.toLowerCase() : root)}`)) {
                active = client; context = candidate; break;
              }
            } catch { /* Other host frames are not the selected project. */ }
          }
          if (active) break;
        }
      } catch { /* The host is still starting. */ }
      if (!active) await delay(100);
    }
    assert.ok(active, 'The installed host must show its startup surface.');
    const evaluate = expression => active.evaluate(context, expression);
    const wait = async (expression, message) => {
      const until = Date.now() + 30000;
      while (Date.now() < until) { if (await evaluate(expression)) return; await delay(100); }
      assert.fail(`${message}: ${JSON.stringify(await evaluate(`({title:document.getElementById('startup-title').textContent,detail:document.getElementById('startup-detail').textContent,message:document.getElementById('message').textContent})`))}`);
    };
    if (missing) {
      await wait(`document.getElementById('startup-title').textContent === 'Install the specspec CLI'`, 'Missing CLI must have a prominent blocking message');
      assert.ok(await evaluate(`!document.getElementById('startup').hidden && document.getElementById('new').disabled && document.getElementById('compare').disabled`));
      assert.equal(await evaluate(`document.querySelectorAll('#cards .card').length`), 0);
      assert.match(await evaluate(`document.getElementById('startup-command').textContent`), /uv tool install/);
      if (!initialize) return;
      await restore();
      await evaluate(`document.getElementById('startup-retry').click()`);
    }
    await wait(`!document.getElementById('initialize-form').hidden`, 'An uninitialized directory must offer initialization');
    assert.ok(!existsSync(join(root, '.specspec')), 'Opening a directory must not create its graph.');
    assert.equal(await evaluate(`document.getElementById('initialize').textContent`), 'Initialize specspec');
    const geometry = await evaluate(`(() => {const r=document.getElementById('initialize').getBoundingClientRect();return {center:r.left+r.width/2,viewport:innerWidth/2};})()`);
    assert.ok(Math.abs(geometry.center - geometry.viewport) < 10, 'The initialization action must be centered.');
    await evaluate(`document.getElementById('initialize-body').value='Test';document.getElementById('initialize-body').dispatchEvent(new Event('input',{bubbles:true}));document.getElementById('initialize').click()`);
    await wait(`document.getElementById('startup').hidden && document.querySelectorAll('#cards .card.manifesto').length === 1`, 'Explicit initialization must adopt the new graph');
    const snapshot = cli(['query', '--json']).target;
    assert.equal(snapshot.nodes.length, 1); assert.equal(snapshot.nodes[0].body, 'Test\n');
    assert.ok(existsSync(join(root, '.git'))); assert.ok(existsSync(join(root, '.specspec/local')));
    const guide = readFileSync(join(root, 'AGENTS.md'), 'utf8');
    assert.ok(guide.startsWith('# Existing owner instructions\n')); assert.ok(guide.includes('## Working phases'));
    assert.equal(await evaluate(`document.getElementById('new').disabled`), false);
    console.log('SPECSPEC_STARTUP_HOST_OK: blocking CLI guidance, explicit init, Git, appended guide, centered button and current graph.');
  } finally { for (const client of clients.values()) client.close(); }
}
module.exports = { startupChecks };
