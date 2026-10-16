const assert = require('node:assert/strict');
const { readFileSync, writeFileSync, existsSync } = require('node:fs');
const { execFileSync } = require('node:child_process');
const { join } = require('node:path');
function committedRootSibling(current, base, manifestoId, excludedId) {
  const committed = new Set(base.nodes.map(n=>n.id));
  return current.nodes.find(n=>n.type==='requirement'&&n.id!==excludedId&&n.parents.includes(manifestoId)&&committed.has(n.id));
}
function platformChecks(fixture, host) {
  const { added, modified, removed } = fixture;
  return {
    readSpotlights: () => fixture.cli(['spotlight', 'show', '--json']).shots,
    submitSpotlights: id => ['red','blue','green','purple','turquoise','yellow'].map(color =>
      fixture.cli(['spotlight', 'add', color, id, `${color} answer for ${id}`, '--json']).shots[0]),
    before: async ({ evaluate, screenshot, delay }) => {
      // Working-first is intentionally a usable graph without Git classification.
      // Git-paint assertions need the completed comparison, not the first cards.
      const compared = () => evaluate(`${JSON.stringify([[added,'A'],[modified,'M'],[removed,'D']])}.every(([id,letter])=>document.querySelector('[data-node-id="'+id+'"] .git-corner')?.textContent===letter)`);
      for (let i=0;i<300 && !await compared();i++) await delay(100);
      assert.ok(await compared(), 'Completed HEAD comparison must supply all A/M/D markers.');
      const check = () => evaluate(`(() => {
        const cases=${JSON.stringify([[added,'A'],[modified,'M'],[removed,'D']])};
        return cases.map(([id,letter])=>{const c=[...document.querySelectorAll('#cards .card')].find(c=>c.dataset.nodeId===id),mark=c?.querySelector('.git-corner'),head=c?.querySelector('strong,h2');
          const s=getComputedStyle(mark),box=mark.getBoundingClientRect(),bounds=c.getBoundingClientRect();
          const overlaps=[head,c.querySelector('small'),...c.querySelectorAll('.badge')].filter(Boolean).some(e=>{const r=e.getBoundingClientRect();return r.left<box.right&&r.right>box.left&&r.top<box.bottom&&r.bottom>box.top;});
          return {letter:mark?.textContent,expected:letter,title:getComputedStyle(head).color,marker:s.color,label:mark?.getAttribute('aria-label'),
            size:s.fontSize,weight:s.fontWeight,width:c.offsetWidth,height:c.offsetHeight,
            fits:box.left>=bounds.left&&box.right<=bounds.right&&box.top>=bounds.top&&box.bottom<=bounds.bottom&&!overlaps};});
      })()`);
      for (const c of await check()) {
        assert.equal(c.letter,c.expected); assert.equal(c.title,c.marker); assert.match(c.label,/comparison base/);
        assert.equal(c.size,'20px'); assert.equal(c.weight,'800');
        assert.equal(c.width,264); assert.equal(c.height,112); assert.ok(c.fits,'Enlarged Git letters must fit without colliding or growing cards.');
      }
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
      // A real root change in the independent disposable clone exercises the new
      // revision-mode exception, not a synthetic renderer-only status injection.
      const root=fixture.cli(['show','--json']).nodes.find(n=>n.type==='manifesto');
      fixture.cli(['update',root.id,'--body','-','--json'],root.body+'\nRoot revision-color fixture.\n');
      for(let i=0;i<300;i++) {
        if(await evaluate(`document.querySelector('#cards .card.manifesto.changed')!==null`)) break;
        await delay(100);
      }
      assert.ok(await evaluate(`document.querySelector('#cards .card.manifesto.changed')!==null`));
      console.log(`${host}: real A/M/D title/corner paint, live theme tokens and modified manifesto fixture passed.`);
    },
    after: async ({ evaluate, screenshot, delay }) => {
      const waitFor = async expression => {
        for (let i = 0; i < 300; i++) { if (await evaluate(expression)) return; await delay(100); }
        assert.ok(await evaluate(expression), JSON.stringify(await evaluate(`({message:document.getElementById('message').textContent,body:document.getElementById('body').value})`)));
      };
      // Real HEAD deletion lifecycle in this disposable independent Git history.
      // Stage only the already deleted fixture file, not unrelated A/M drafts.
      await evaluate(`document.getElementById('back').click()`);
      assert.ok(await evaluate(`document.querySelector('[data-node-id="${removed}"].removed')!==null`));
      const base = fixture.cli(['diff','HEAD','--json']).base;
      const deletedPath = base.nodes.find(n=>n.id===removed).path;
      assert.equal(existsSync(join(fixture.root,deletedPath)),false);
      const git = (...args) => {
        if(args.includes('commit')) fixture.cli(['check','--staged','--warnings-as-errors','--json']);
        return execFileSync('git',['-C',fixture.root,...args],{stdio:'pipe'});
      };
      git('add','-u','--',deletedPath); await delay(500);
      assert.ok(await evaluate(`document.querySelector('[data-node-id="${removed}"].removed')!==null`),'Staging must not remove a HEAD ghost.');
      await evaluate(`document.querySelector('[data-node-id="${removed}"]').click()`);
      assert.ok(await evaluate(`document.getElementById('save').disabled&&document.getElementById('delete').disabled&&document.getElementById('body').readOnly&&!document.getElementById('body').disabled`),'Deleted details are copyable but never editable.');
      await screenshot(`${host}-deleted-head-ghost`);
      git('-c','user.name=SpecSpec host fixture','-c','user.email=fixture@specspec.invalid','commit','-m','Delete the disposable implementation because this test is checking HEAD-relative ghost lifetime');
      await waitFor(`document.querySelector('[data-node-id="${removed}"]')===null&&document.getElementById('revision').textContent.startsWith('HEAD → ')`);
      assert.equal(existsSync(join(fixture.root,deletedPath)),false);
      console.log(`${host}: physical deletion D survives staging and vanishes after commit through Git watching without Refresh/polling.`);
      // A whole descendant cascade with two levels shared with independent outside
      // parents, over maintained history (not an invented one-commit baseline).
      const current = fixture.cli(['show','--json']);
      const manifesto = current.nodes.find(n=>n.type==='manifesto');
      const outside = current.nodes.find(n=>n.id===fixture.modified);
      const outsideBytes = readFileSync(join(fixture.root,outside.path));
      const deeperOutside = committedRootSibling(current,base,manifesto.id,outside.id);
      assert.ok(deeperOutside,'The maintained HEAD needs a second committed manifesto-child requirement.');
      const deeperOutsideBytes = readFileSync(join(fixture.root,deeperOutside.path));
      const add = (parents,slug) => fixture.cli(['add',...parents.flatMap(p=>['--parent',p]),'--slug',slug,'--body','-','--json'],`# ${slug}\n\nDisposable cascade regression.\n`).changed_ids[0];
      const branch = add([manifesto.id],'cascade-root');
      const full = add([branch],'cascade-full-child');
      const partial = add([branch,outside.id],'cascade-partial-child');
      const deep = add([partial,deeperOutside.id],'cascade-deeper-partial-child');
      const committed = [branch,full,partial,deep];
      const files = fixture.cli(['show','--json']).nodes.filter(n=>committed.includes(n.id)).map(n=>n.path);
      git('add','--',...files);
      git('-c','user.name=SpecSpec host fixture','-c','user.email=fixture@specspec.invalid','commit','-m','Record a disposable full and shared descendant branch');
      const fresh = add([deep],'cascade-never-committed-child');
      const deepPath = fixture.cli(['show','--json']).nodes.find(n=>n.id===deep).path;
      fixture.cli(['update',deep,'--body','-','--json'],'# Staged but uncommitted descendant\n');
      git('add','--',deepPath);
      const plan = fixture.cli(['delete',branch,'--dry-run','--json']);
      assert.deepEqual(new Set(plan.deleted_ids),new Set([...committed,fresh]));
      assert.deepEqual(new Set(plan.uncommitted.map(n=>n.id)),new Set([deep,fresh]));
      assert.equal(plan.uncommitted.find(n=>n.id===deep).status,'M ');
      fixture.cli(['delete',branch,'--yes','--reviewed-plan','-','--json'],JSON.stringify(plan));
      const ghostCheck = committed.map(id=>`document.querySelector('[data-node-id="${id}"].removed')!==null`).join('&&');
      await waitFor(ghostCheck);
      assert.ok(await evaluate(`document.querySelector('[data-node-id="${fresh}"]')===null`),'Never-committed descendant has no fabricated HEAD ghost.');
      assert.deepEqual(readFileSync(join(fixture.root,outside.path)),outsideBytes,'Shared outside parent survives without reparenting/editing.');
      assert.deepEqual(readFileSync(join(fixture.root,deeperOutside.path)),deeperOutsideBytes,'Independent deeper outside parent also survives.');
      assert.ok(plan.nodes.every(n=>!existsSync(join(fixture.root,n.path))),'All full/partial descendant files are physically gone.');
      git('add','-u','--',...files);await delay(500);
      assert.ok(await evaluate(ghostCheck),'All committed cascade ghosts survive staging.');
      git('-c','user.name=SpecSpec host fixture','-c','user.email=fixture@specspec.invalid','commit','-m','Delete all full and shared descendants because the disposable regression branch is no longer needed');
      await waitFor(committed.map(id=>`document.querySelector('[data-node-id="${id}"]')===null`).join('&&'));
      assert.deepEqual(readFileSync(join(fixture.root,outside.path)),outsideBytes);
      assert.deepEqual(readFileSync(join(fixture.root,deeperOutside.path)),deeperOutsideBytes);
      console.log(`${host}: real full/partial descendant cascade, staged/new-child warnings, outside-parent preservation and all HEAD/stage/commit ghosts passed without Refresh/polling.`);
      // Real manual Markdown writes, with no Refresh click, CLI mutation or polling.
      await evaluate(`document.getElementById('discard').click();document.getElementById('back').click();document.querySelector('[data-node-id="${modified}"]').click()`);
      const node = fixture.cli(['show', modified, '--json']).node, path = join(fixture.root, node.path);
      const raw = readFileSync(path), prefix = raw.subarray(0, raw.length - Buffer.byteLength(node.body));
      const manual = Buffer.concat([prefix, Buffer.from('# Manual watcher-only update\n')]);
      writeFileSync(path, manual);
      await waitFor(`document.getElementById('body').value==='# Manual watcher-only update\\n'`);
      await evaluate(`document.getElementById('body').value='# Retained external draft';document.getElementById('body').dispatchEvent(new Event('input'));document.getElementById('body').focus();document.getElementById('body').setSelectionRange(2,8)`);
      const baseline = await evaluate(`window.SpecSpecHost.getState().originalNode`);
      const external = Buffer.concat([prefix, Buffer.from('# External watcher update\n')]);
      writeFileSync(path, external);
      await waitFor(`/changed outside/.test(document.getElementById('message').textContent)`);
      assert.equal(await evaluate(`document.getElementById('body').value`), '# Retained external draft');
      assert.deepEqual(await evaluate(`window.SpecSpecHost.getState().originalNode`), baseline);
      assert.deepEqual(await evaluate(`[document.getElementById('body').selectionStart,document.getElementById('body').selectionEnd]`), [2,8]);
      const invalid = Buffer.from(external.toString().replace('parents:', 'broken:'));
      writeFileSync(path, invalid);
      await waitFor(`/out of date/.test(document.getElementById('message').textContent)&&document.getElementById('save').disabled`);
      assert.deepEqual(readFileSync(path), invalid, 'Invalid external files must not be rewritten.');
      assert.equal(await evaluate(`document.getElementById('body').value`), '# Retained external draft');
      writeFileSync(path, external);
      await waitFor(`!document.getElementById('save').disabled`);
      await screenshot(`${host}-watcher-retained-draft`);
      await evaluate(`document.getElementById('discard').click()`);
      assert.equal(await evaluate(`document.getElementById('body').value`), '# External watcher update\n');
      console.log(`${host}: watcher-only manual/invalid-file sync, native draft/caret preservation and recovery passed.`);
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
      const old = await evaluate(`window.SpecSpecHost.getState().originalNode`);
      fixture.cli(['update',modified,'--body','-','--json'],'# External fixture update\n');
      await waitFor(`/changed outside/.test(document.getElementById('message').textContent)`);
      assert.equal(await evaluate(`document.getElementById('body').value`),'# Retained stale desktop draft');
      assert.deepEqual(await evaluate(`window.SpecSpecHost.getState().originalNode`),old);
      for(let i=0;i<100;i++){if(await evaluate(`!document.getElementById('save').disabled`))break;await delay(80);}
      assert.ok(await evaluate(`!document.getElementById('save').disabled`));
      // Actual overwrite dialogs are tested through the shared host session,
      // not auto-accepted by this native-window smoke harness.
      assert.equal(fixture.cli(['show',modified,'--json']).node.body,'# External fixture update\n');
      await screenshot('electron-stale-draft');
      await evaluate(`location.reload()`);await delay(1200);
      // The harness context is refreshed on a reload only in a separate test phase.
      console.log('Electron real UI save and retained external-change draft passed; persisted state written for reload checks.');
    },
  };
}
module.exports = { platformChecks, committedRootSibling };
