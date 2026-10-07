const assert = require('node:assert/strict');
function platformChecks(fixture, host) {
  const { added, modified, removed } = fixture;
  return {
    before: async ({ evaluate, screenshot, delay }) => {
      const check = () => evaluate(`(() => {
        const cases=${JSON.stringify([[added,'A'],[modified,'M'],[removed,'D']])};
        return cases.map(([id,letter])=>{const c=[...document.querySelectorAll('#cards .card')].find(c=>c.dataset.nodeId===id),mark=c?.querySelector('.git-corner'),head=c?.querySelector('strong,h2');
          return {letter:mark?.textContent,expected:letter,title:getComputedStyle(head).color,marker:getComputedStyle(mark).color,label:mark?.getAttribute('aria-label')};});
      })()`);
      for (const c of await check()) { assert.equal(c.letter,c.expected); assert.equal(c.title,c.marker); assert.match(c.label,/comparison base/); }
      const world = await evaluate(`document.getElementById('graph').style.transform`);
      // Simulate live theme customizations without writing real VS Code settings.
      await evaluate(`document.documentElement.style.setProperty('--vscode-gitDecoration-addedResourceForeground','#12aa66');document.documentElement.style.setProperty('--vscode-editorGutter-modifiedBackground','#32aaff');document.documentElement.style.setProperty('--vscode-gitDecoration-deletedResourceForeground','#fa5555')`);
      assert.deepEqual((await check()).map(c=>c.title),['rgb(18, 170, 102)','rgb(50, 170, 255)','rgb(250, 85, 85)']);
      assert.equal(await evaluate(`document.getElementById('graph').style.transform`),world);
      await evaluate(`for(const n of ['--vscode-gitDecoration-addedResourceForeground','--vscode-editorGutter-modifiedBackground','--vscode-gitDecoration-deletedResourceForeground'])document.documentElement.style.removeProperty(n)`);
      for (const [id,label] of [[added,'added'],[modified,'modified'],[removed,'deleted']]) {
        await evaluate(`document.querySelector('[data-node-id="${id}"]').click()`); await delay(80);
        assert.ok(await evaluate(`document.querySelector('.expanded .git-corner')!==null`));
        await evaluate(`document.getElementById('frame-node').click()`); await delay(300);
        await screenshot(`${host}-git-${label}`);
        await evaluate(`document.getElementById('back').click()`);
      }
      console.log(`${host}: real A/M/D title/corner paint and live theme tokens passed.`);
    },
    after: async ({ evaluate, screenshot, delay }) => {
      if (host !== 'electron') return;
      assert.deepEqual(await evaluate(`[typeof require,typeof process]`),['undefined','undefined']);
      assert.deepEqual(await evaluate(`Object.keys(window.SpecSpecNative).sort()`),['getState','onMessage','postMessage','revisionResult','setState']);
      assert.equal(await evaluate(`fetch('https://example.invalid/').then(()=>false,()=>true)`),true);
      assert.equal(await evaluate(`window.open('https://example.invalid/')`),null);
      await evaluate(`document.getElementById('back').click();document.querySelector('[data-node-id="${modified}"]').click();document.getElementById('body').value=${JSON.stringify('# Saved from real Electron UI\n\nLiteral <script>data</script>.')};document.getElementById('body').dispatchEvent(new Event('input'));document.getElementById('save').click()`);
      // Wait for the host's completed-render acknowledgement before reading the
      // canonical files: the CLI intentionally rejects reads during an active journal.
      for(let i=0;i<300;i++){if(await evaluate(`!document.getElementById('save').disabled&&!window.SpecSpecHost.getState().dirty`))break;await delay(100);}
      assert.ok(await evaluate(`!document.getElementById('save').disabled&&!window.SpecSpecHost.getState().dirty`));
      assert.ok(fixture.cli(['show',modified,'--json']).node.body.includes('Saved from real Electron UI'));
      await evaluate(`document.getElementById('body').value='# Retained stale desktop draft';document.getElementById('body').dispatchEvent(new Event('input'));document.getElementById('body').focus();document.getElementById('body').setSelectionRange(2,8)`);
      const old = await evaluate(`window.SpecSpecHost.getState().formFingerprint`);
      const s = fixture.cli(['list','--json']);
      fixture.cli(['update',modified,'--expect',s.fingerprint,'--body','-','--json'],'# External fixture update\n');
      await delay(1000);
      assert.equal(await evaluate(`document.getElementById('body').value`),'# Retained stale desktop draft');
      assert.equal(await evaluate(`window.SpecSpecHost.getState().formFingerprint`),old);
      for(let i=0;i<100;i++){if(await evaluate(`!document.getElementById('save').disabled`))break;await delay(80);}
      assert.ok(await evaluate(`!document.getElementById('save').disabled`));
      await evaluate(`window.__staleError='';window.SpecSpecHost.onMessage(m=>{if(m.type==='error')window.__staleError=m.message});document.getElementById('editor').requestSubmit(document.getElementById('save'))`);
      for(let i=0;i<100;i++){if(await evaluate(`/stale|changed/i.test(window.__staleError)`))break;await delay(80);}
      assert.match(await evaluate(`window.__staleError`),/stale|changed/i);
      assert.equal(fixture.cli(['show',modified,'--json']).node.body,'# External fixture update\n');
      await screenshot('electron-stale-draft');
      await evaluate(`location.reload()`);await delay(1200);
      // The harness context is refreshed on a reload only in a separate test phase.
      console.log('Electron real UI save and stale-fingerprint rejection passed; persisted state written for reload checks.');
    },
  };
}
module.exports = { platformChecks };
