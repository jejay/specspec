/* Optional real file:// browser check. Node 22+ and the existing Electron dev install. */
const { join, resolve } = require('node:path');
if (process.versions.electron) {
  const { app, BrowserWindow } = require('electron');
  app.setPath('userData', process.env.SPECSPEC_PLAYGROUND_PROFILE);
  app.whenReady().then(() => {
    const window = new BrowserWindow({ width: 1150, height: 1000,
      webPreferences: { sandbox: true, contextIsolation: true, nodeIntegration: false } });
    window.loadFile(resolve(__dirname, '../../tools/rainbow-playground/index.html'));
  });
  app.on('window-all-closed', () => app.quit());
} else {
  const { spawn } = require('node:child_process');
  const { mkdtempSync, mkdirSync, writeFileSync, rmSync } = require('node:fs');
  const { tmpdir } = require('node:os');
  const { createServer } = require('node:net');
  const assert = require('node:assert/strict');
  const { CDP } = require('./ui.cjs');
  const delay = ms => new Promise(resolve => setTimeout(resolve,ms));
  async function run() {
    const profile=mkdtempSync(join(tmpdir(),'specspec-rainbow-browser-'));
    const port=await new Promise(resolve=>{const s=createServer();s.listen(0,'127.0.0.1',()=>{const p=s.address().port;s.close(()=>resolve(p));});});
    const env={...process.env,SPECSPEC_PLAYGROUND_PROFILE:profile};delete env.ELECTRON_RUN_AS_NODE;
    const child=spawn(require('../../electron/node_modules/electron'),[__filename,`--remote-debugging-port=${port}`,'--remote-debugging-address=127.0.0.1'],{env,stdio:['ignore','pipe','pipe']});
    child.stdout.on('data',d=>process.stdout.write(d));child.stderr.on('data',d=>process.stderr.write(d));
    const exit=new Promise((resolve,reject)=>{child.on('error',reject);child.on('close',resolve);});
    const timer=setTimeout(()=>child.kill(),60_000);let client,ok=false;
    try {
      for(let i=0;i<150;i++) {
        try {
          const targets=await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
          const target=targets.find(t=>t.type==='page'&&t.url.includes('/rainbow-playground/index.html'));
          if(target){client=new CDP(target.webSocketDebuggerUrl);break;}
        } catch { /* Browser starting. */ }
        await delay(100);
      }
      assert.ok(client,'Standalone file page must open');
      const evaluate=async expression=>{
        const r=await client.send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
        if(r.exceptionDetails)throw new Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);
        return r.result.value;
      };
      const screenshot=async name=>{if(process.env.SPECSPEC_SCREENSHOT_DIR){mkdirSync(process.env.SPECSPEC_SCREENSHOT_DIR,{recursive:true});const image=await client.send('Page.captureScreenshot',{format:'png'});writeFileSync(join(process.env.SPECSPEC_SCREENSHOT_DIR,name+'.png'),Buffer.from(image.data,'base64'));}};
      for(let i=0;i<100;i++){if(await evaluate(`document.getElementById('swatches')?.children.length===7`))break;await delay(50);}
      await screenshot('rainbow-playground-controls');
      assert.equal(await evaluate(`location.protocol`),'file:');
      assert.equal(await evaluate(`document.getElementById('swatches').children.length`),7);
      assert.ok(await evaluate(`document.getElementById('mappings').textContent.includes('Requirement · color 5 · #92a64b')&&document.getElementById('mappings').textContent.includes('A · Added · color 4 · #37b390')`));
      assert.ok(await evaluate(`document.getElementById('mapping-logic').textContent.includes('Requirement gets a leftover')`));
      assert.ok(await evaluate(`(() => {const c=document.querySelector('.node.manifesto'),r=c.getBoundingClientRect();return getComputedStyle(c).borderRadius==='50%'&&Math.abs(r.width-r.height)<1&&c.scrollHeight<=c.clientHeight;})()`));
      assert.ok(await evaluate(`getComputedStyle(document.querySelector('.node')).backgroundColor.startsWith('color(srgb')`),'Tint preview uses the real browser CSS');
      await evaluate(`document.getElementById('count').value='12';document.getElementById('count').dispatchEvent(new Event('input',{bubbles:true}))`);
      assert.equal(await evaluate(`document.getElementById('swatches').children.length`),12);
      await evaluate(`document.getElementById('chroma').value='0.4';document.getElementById('chroma').dispatchEvent(new Event('input',{bubbles:true}))`);
      assert.ok(await evaluate(`document.getElementById('message').textContent.includes('Chroma reduced')`));
      await evaluate(`document.getElementById('format').value='palette';document.getElementById('format').dispatchEvent(new Event('change'))`);
      assert.equal(await evaluate(`JSON.parse(document.getElementById('result').value).colors.length`),12);
      await evaluate(`document.getElementById('count').value='1';document.getElementById('count').dispatchEvent(new Event('input',{bubbles:true}))`);
      assert.ok(await evaluate(`document.getElementById('copy').disabled&&document.getElementById('swatches').children.length===12`));
      await evaluate(`document.getElementById('reset').click()`);
      assert.deepEqual(await evaluate(`JSON.parse(document.getElementById('result').value).colors`),require('../media/graph-model.js').RAINBOW_COLORS);
      assert.deepEqual(await evaluate(`JSON.parse(document.getElementById('result').value).mappings`),{requirement:4,implementation:0,added:3,changed:1,removed:6,'source-changed':5});
      await evaluate(`document.getElementById('format').value='css';document.getElementById('format').dispatchEvent(new Event('change'))`);
      assert.ok(await evaluate(`document.getElementById('result').value.includes('--rainbow-7: #dc7b7c')`));
      assert.ok(await evaluate(`document.getElementById('result').value.includes('--palette-requirement: var(--rainbow-5)')&&document.getElementById('result').value.includes('--palette-added: var(--rainbow-4)')`));
      await evaluate(`document.getElementById('theme').value='light';document.getElementById('theme').dispatchEvent(new Event('change'))`);
      assert.equal(await evaluate(`getComputedStyle(document.getElementById('preview')).backgroundColor`),'rgb(255, 255, 255)');
      // No automated writes to the user's clipboard: exercise the manual fallback.
      await evaluate(`Object.defineProperty(navigator,'clipboard',{value:undefined,configurable:true});document.getElementById('copy').click()`);
      assert.ok(await evaluate(`document.getElementById('message').textContent.includes('press Ctrl+C')&&document.getElementById('result').selectionEnd===document.getElementById('result').value.length`));
      await screenshot('rainbow-playground-result');
      console.log('SPECSPEC_RAINBOW_PLAYGROUND_OK: offline file startup, controls, gamut feedback, exports, reset, light preview and copy fallback.');ok=true;
    } finally {
      clearTimeout(timer);client?.close();child.kill();await exit;
      if(ok)rmSync(profile,{recursive:true,force:true,maxRetries:20,retryDelay:100});
      else console.error(`Playground diagnostic profile retained: ${profile}`);
    }
  }
  run().catch(error=>{console.error(error);process.exitCode=1;});
}
