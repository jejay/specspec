/* Optional real-Chromium smoke test; Node 22+, no npm packages or personal profile. */
const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const http = require('node:http');
const os = require('node:os');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const ROOT = path.resolve(__dirname, '..');
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
async function wait(check, message) {
  const until = Date.now() + 15000;
  while (Date.now() < until) { const result = await check(); if (result) return result; await delay(80); }
  throw Error(message);
}
class CDP {
  constructor(url) {
    this.socket = new WebSocket(url); this.next = 0; this.pending = new Map(); this.events = () => {};
    this.ready = new Promise((resolve,reject) => { this.socket.addEventListener('open',resolve,{once:true});this.socket.addEventListener('error',reject,{once:true}); });
    this.socket.addEventListener('message', event => {
      const message=JSON.parse(event.data),callback=this.pending.get(message.id);
      if(callback){this.pending.delete(message.id);clearTimeout(callback.timer);message.error?callback.reject(Error(message.error.message)):callback.resolve(message.result);}
      else if(message.method)this.events(message);
    });
  }
  async send(method,params={}) {
    await this.ready;const id=++this.next;
    return new Promise((resolve,reject)=>{const timer=setTimeout(()=>{this.pending.delete(id);reject(Error(`CDP timeout: ${method}`));},10000);this.pending.set(id,{resolve,reject,timer});this.socket.send(JSON.stringify({id,method,params}));});
  }
  async evaluate(expression) {
    const r=await this.send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
    if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);
    return r.result.value;
  }
  close(){this.socket.close();}
}
(async()=>{
  if(typeof WebSocket==='undefined')throw Error('This test requires Node 22+.');
  const candidates=[process.env.GANTT_BROWSER,
    'C:/Program Files/Google/Chrome/Application/chrome.exe','C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    '/usr/bin/google-chrome','/usr/bin/chromium','/usr/bin/chromium-browser','/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'];
  const executable=candidates.find(p=>p&&fs.existsSync(p));
  if(!executable)throw Error('Set GANTT_BROWSER to an installed Chrome/Chromium/Edge executable. No browser is downloaded.');
  const allowed=new Map([['/','index.html'],['/model.js','model.js'],['/app.js','app.js'],['/styles.css','styles.css']]);
  const server=http.createServer((req,res)=>{
    const file=allowed.get(new URL(req.url,'http://localhost').pathname);
    if(!file){res.writeHead(404);res.end();return;}
    res.setHeader('Content-Type',file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':'text/html');
    res.setHeader('Cache-Control','no-store');res.end(fs.readFileSync(path.join(ROOT,file)));
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const origin=`http://127.0.0.1:${server.address().port}`,temp=fs.mkdtempSync(path.join(os.tmpdir(),'gantt-browser-'));
  const downloads=path.join(temp,'downloads');fs.mkdirSync(downloads);
  const browser=spawn(executable,['--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check','--remote-debugging-address=127.0.0.1','--remote-debugging-port=0',`--user-data-dir=${temp}`,'--window-size=1400,1100','about:blank'],{stdio:['ignore','ignore','pipe']});
  let stderr='',spawnError,client,dismissNext=false,closed=false;
  browser.stderr.on('data',chunk=>{stderr+=chunk;});browser.on('error',error=>{spawnError=error;});browser.on('exit',()=>{closed=true;});
  const exceptions=[],requests=[];
  async function screenshot(name){if(!process.env.GANTT_SCREENSHOT_DIR||!client)return;fs.mkdirSync(process.env.GANTT_SCREENSHOT_DIR,{recursive:true});const image=await client.send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(process.env.GANTT_SCREENSHOT_DIR,name+'.png'),Buffer.from(image.data,'base64'));}
  try{
    const active=path.join(temp,'DevToolsActivePort');
    await wait(()=>{if(spawnError)throw spawnError;if(closed)throw Error(stderr);return fs.existsSync(active);},'Browser did not expose the isolated loopback debugger.');
    const port=Number(fs.readFileSync(active,'utf8').trim().split(/\r?\n/)[0]);
    const target=await wait(async()=>{try{return (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find(t=>t.type==='page');}catch{return false;}},'No isolated browser page.');
    client=new CDP(target.webSocketDebuggerUrl);
    client.events=message=>{
      if(message.method==='Runtime.exceptionThrown')exceptions.push(message.params.exceptionDetails.text);
      if(message.method==='Network.requestWillBeSent')requests.push(message.params.request.url);
      if(message.method==='Page.javascriptDialogOpening'){const accept=!dismissNext;dismissNext=false;void client.send('Page.handleJavaScriptDialog',{accept}).catch(error=>exceptions.push(error.message));}
    };
    await client.send('Runtime.enable');await client.send('Page.enable');await client.send('Network.enable');
    await client.send('Page.setDownloadBehavior',{behavior:'allow',downloadPath:downloads});
    await client.send('Page.navigate',{url:origin+'/'});
    const evaluate=e=>client.evaluate(e),click=s=>evaluate(`document.querySelector(${JSON.stringify(s)}).click()`);
    const input=(id,value)=>evaluate(`(() => {const n=document.getElementById(${JSON.stringify(id)});n.value=${JSON.stringify(value)};n.dispatchEvent(new Event('input',{bubbles:true}));})()`);
    const saved=()=>evaluate(`localStorage.getItem('specspec-gantt-plan')`);
    const count=()=>evaluate(`document.querySelectorAll('#task-table tr').length`);
    const reload=async()=>{await client.send('Page.reload',{ignoreCache:true});await wait(async()=>await evaluate(`!!document.querySelector('#task-table tr')`),'App did not reload.');};
    await wait(async()=>await count()===6,'Initial workshop did not render six tasks.');
    assert.equal(await saved(),null,'Opening the demo must not write storage.');
    assert.equal(await evaluate(`document.querySelectorAll('.bar.current').length`),6);
    assert.equal(await evaluate(`document.querySelectorAll('.bar.baseline').length`),0);
    await click('#capture-baseline');const first=JSON.parse(await saved());assert.equal(first.baseline.tasks.length,6);
    await click('#task-table [data-id="materials"] .table-task');await input('task-duration','6');await click('#task-form button[type=submit]');
    let current=JSON.parse(await saved());assert.deepEqual(current.baseline,first.baseline);assert.equal(current.tasks.find(t=>t.id==='materials').duration,6);
    assert.ok(await evaluate(`document.querySelector('#task-table [data-id="workshop"]').textContent.includes('+1d')`));
    assert.ok(await evaluate(`document.querySelector('.bar.current[data-id="workshop"]').title.includes('2026-04-21')`));
    await screenshot('workshop-baseline');
    // Native caret/form identity survives responsive chart redraw.
    await evaluate(`window.__editor=document.getElementById('task-name');__editor.focus();__editor.setSelectionRange(2,6,'backward')`);
    await client.send('Emulation.setDeviceMetricsOverride',{width:480,height:900,deviceScaleFactor:1,mobile:false});await delay(100);
    assert.ok(await evaluate(`window.__editor===document.getElementById('task-name')&&document.activeElement===__editor&&__editor.selectionStart===2&&__editor.selectionEnd===6&&__editor.selectionDirection==='backward'`));
    assert.equal(await saved(),JSON.stringify(current));
    assert.ok(await evaluate(`document.documentElement.scrollWidth<=innerWidth`),'Narrow views scroll the timeline/table, not the whole page.');
    assert.ok(await evaluate(`document.getElementById('timeline-scroll').scrollWidth>document.getElementById('timeline-scroll').clientWidth`));
    await screenshot('workshop-narrow');
    await client.send('Emulation.clearDeviceMetricsOverride');await delay(100);
    // A failed cyclic draft remains editable; declining navigation preserves it.
    await click('#task-table [data-id="outline"] .table-task');
    await evaluate(`document.querySelector('#prerequisites input[value="dryrun"]').checked=true`);
    const validBefore=await saved();await click('#task-form button[type=submit]');
    assert.match(await evaluate(`document.getElementById('message').textContent`),/cycle/);assert.equal(await saved(),validBefore);
    dismissNext=true;await click('#task-table [data-id="materials"] .table-task');assert.equal(await evaluate(`document.getElementById('task-id').value`),'outline');
    assert.ok(await evaluate(`document.querySelector('#prerequisites input[value="dryrun"]').checked`));
    await click('#task-table [data-id="materials"] .table-task');await click('#task-table [data-id="outline"] .table-task');
    await click('#delete-task');assert.match(await evaluate(`document.getElementById('message').textContent`),/required by/);assert.equal(await saved(),validBefore);
    // Literal project content cannot create executable HTML.
    await click('#new-task');await input('task-name','<img src=x onerror="window.__unsafe=1">');await click('#task-form button[type=submit]');
    assert.equal(await evaluate(`document.querySelectorAll('#timeline img,#task-table img,#prerequisites img').length`),0);
    assert.equal(await evaluate(`typeof window.__unsafe`),'undefined');assert.equal(await count(),7);
    await click('#capture-baseline');await click('#delete-task');assert.equal(await count(),7,'Deleted task remains as baseline-only context.');
    assert.ok(await evaluate(`document.querySelector('#task-table [data-id="task-1"]').textContent.includes('Removed')`));
    await click('#export-plan');await wait(()=>fs.existsSync(path.join(downloads,'workshop-plan-v2.json')),'Export did not download.');
    assert.deepEqual(JSON.parse(fs.readFileSync(path.join(downloads,'workshop-plan-v2.json'),'utf8')),JSON.parse(await saved()));
    // Real file upload, preview/cancel/apply, and archived v1 compatibility.
    const beforeImport=await saved(),legacy=fs.readFileSync(path.join(ROOT,'history/personal-v1.json'),'utf8');
    const dom=await client.send('DOM.getDocument');const file=await client.send('DOM.querySelector',{nodeId:dom.root.nodeId,selector:'#import-file'});
    await client.send('DOM.setFileInputFiles',{nodeId:file.nodeId,files:[path.join(ROOT,'history/personal-v1.json')]});
    await wait(async()=>await evaluate(`!document.getElementById('import-preview').hidden`),'V1 file preview did not appear.');
    assert.equal(await saved(),beforeImport);assert.equal(await evaluate(`document.querySelectorAll('#import-warnings li').length`),3);
    await click('#cancel-import');assert.equal(await saved(),beforeImport);
    await input('import-json',legacy);await click('#import-form button[type=submit]');await click('#apply-import');
    current=JSON.parse(await saved());assert.equal(current.version,2);assert.equal(current.tasks.length,3);assert.ok(current.tasks.every(t=>!('priority' in t)));
    assert.ok(await evaluate(`document.querySelector('.bar.current[data-id="clear"]').title.includes('2026-04-06')`));
    const imported=await saved();await input('import-json','{"version":9}');await click('#import-form button[type=submit]');assert.equal(await saved(),imported);
    assert.ok(await evaluate(`document.getElementById('import-preview').hidden`));await reload();assert.equal(await count(),3);assert.equal(await saved(),imported);
    // Bad saved bytes are retained, even after otherwise valid edits.
    await evaluate(`localStorage.setItem('specspec-gantt-plan','{corrupt')`);await reload();assert.equal(await count(),6);
    assert.equal(await saved(),'{corrupt');assert.ok(await evaluate(`!document.getElementById('backup-saved').hidden`));
    await click('#task-table [data-id="materials"] .table-task');await input('task-duration','4');await click('#task-form button[type=submit]');assert.equal(await saved(),'{corrupt');
    await click('#backup-saved');await wait(()=>fs.existsSync(path.join(downloads,'protected-original-plan.json')),'Original-byte backup did not download.');
    assert.equal(fs.readFileSync(path.join(downloads,'protected-original-plan.json'),'utf8'),'{corrupt');
    // Stored v1 is never automatically migrated, and a declined Apply cannot write.
    await evaluate(`localStorage.setItem('specspec-gantt-plan',${JSON.stringify(legacy)})`);await reload();assert.equal(await count(),6);assert.equal(await saved(),legacy);
    await click('#preview-saved');assert.equal(await saved(),legacy);dismissNext=true;await click('#apply-import');assert.equal(await saved(),legacy);
    await click('#apply-import');assert.equal(JSON.parse(await saved()).version,2);assert.equal(await count(),3);
    // Storage denial is visible and does not prevent editing/exporting in memory.
    const denial=await client.send('Page.addScriptToEvaluateOnNewDocument',{source:`window.__originalGet=Storage.prototype.getItem;Storage.prototype.getItem=function(){throw new DOMException('denied','SecurityError')};Storage.prototype.setItem=function(){throw new DOMException('full','QuotaExceededError')}`});
    await reload();assert.equal(await count(),6);assert.match(await evaluate(`document.getElementById('storage-status').textContent`),/Session only/);
    await click('#task-table [data-id="materials"] .table-task');await input('task-duration','4');await click('#task-form button[type=submit]');
    assert.ok(await evaluate(`document.querySelector('.bar.current[data-id="materials"]').title.includes('4 workdays')`));
    assert.equal(JSON.parse(await evaluate(`window.__originalGet.call(localStorage,'specspec-gantt-plan')`)).tasks.length,3);
    // Classic scripts also work directly from disk: no running server/API needed.
    await client.send('Page.removeScriptToEvaluateOnNewDocument',{identifier:denial.identifier});
    await client.send('Page.navigate',{url:pathToFileURL(path.join(ROOT,'index.html')).href});
    await wait(async()=>await evaluate(`location.protocol==='file:'&&document.querySelectorAll('#task-table tr').length===6`),'Local-file app did not render.');
    assert.equal(await evaluate(`document.querySelectorAll('.bar.current').length`),6);
    assert.deepEqual(exceptions,[]);assert.deepEqual(requests.filter(url=>!url.startsWith(origin+'/')&&!url.startsWith('blob:')&&!url.startsWith('data:')&&!url.startsWith(pathToFileURL(ROOT+path.sep).href)),[],'App made an external request.');
    console.log('GANTT_REAL_BROWSER_OK: forecasts, immutable baseline, responsive native caret, cyclic drafts, deletion safety, literal text, file export/upload, import preview/cancel/conversion, reload, protected storage, session-only failures, and direct local-file launch.');
  }catch(error){await screenshot('workshop-failure').catch(()=>{});console.error('Browser diagnostics:',stderr.slice(-2000));throw error;}
  finally{
    if(client){await client.send('Browser.close').catch(()=>{});client.close();}
    if(!closed)browser.kill();await wait(()=>closed,'Browser did not close.').catch(()=>{});
    await new Promise(resolve=>server.close(resolve));
    if(closed){for(let attempt=0;attempt<10;attempt++){try{fs.rmSync(temp,{recursive:true,force:true});break;}catch{await delay(100);}}}
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
