const {test}=require('node:test');
const assert=require('node:assert/strict');
const {mkdtempSync,writeFileSync,rmSync}=require('node:fs');
const {tmpdir}=require('node:os');
const {join}=require('node:path');
const {CliClient}=require('../host/client.cjs');
function fixture(t){
  const root=mkdtempSync(join(tmpdir(),'specspec-channel-')),script=join(root,'worker.cjs'),client=new CliClient();
  writeFileSync(script,`const fs=require('node:fs'),rl=require('node:readline').createInterface({input:process.stdin});let count=0;
  const answer=v=>({api_version:6,ok:!v.fail,diagnostics:v.fail?[{code:'TEST',message:'Rejected'}]:[],result:{pid:process.pid,count:++count,value:v,args:process.argv.slice(2)}});
  if(!process.argv.includes('--stream')){let raw='';process.stdin.on('data',c=>raw+=c);process.stdin.on('end',()=>console.log(JSON.stringify(answer({raw}))));}
  else rl.on('line',async raw=>{const v=JSON.parse(raw);if(v.die)process.exit(7);if(v.gate)await new Promise(r=>{const timer=setInterval(()=>{if(fs.existsSync(v.gate)){clearInterval(timer);r();}},5);});
    if(v.bad){process.stdout.write(v.bad);return;}const data=Buffer.from(JSON.stringify(answer(v))+'\\n');
    if(v.split){for(const byte of data){process.stdout.write(Buffer.from([byte]));await new Promise(r=>setImmediate(r));}}
    else process.stdout.write(data);});`);
  t.after(async()=>{
    const children=[...client.channels.values()].map(c=>c.child);
    const exits=children.filter(c=>c.exitCode===null&&c.signalCode===null).map(c=>new Promise(resolve=>c.once('close',resolve)));
    client.dispose();await Promise.all(exits);rmSync(root,{recursive:true,force:true,maxRetries:30,retryDelay:100});
  });
  return {root,client,call:(value,timeout=5000,limit)=>client.invoke(process.execPath,[script],root,['api'],JSON.stringify({api_version:6,...value}),timeout,limit),script};
}
test('API channels reuse interpreter lifetime, preserve JSON bodies and warm an independent preview process',async t=>{
  const f=fixture(t),first=await f.call({op:'read',text:'Exact\nUTF-8 🦉'}),second=await f.call({op:'read'});
  assert.equal(first.result.pid,second.result.pid);assert.equal(second.result.count,2);assert.equal(first.result.value.text,'Exact\nUTF-8 🦉');
  const source=await f.call({op:'source-view'});assert.notEqual(source.result.pid,first.result.pid);assert.equal(f.client.channels.size,2);
  assert.deepEqual(source.result.args,['--root',f.root,'api','--stream']);
});
test('a held application read does not block the source channel; each channel preserves frame order',async t=>{
  const f=fixture(t),gate=join(f.root,'release'),blocked=f.call({op:'read',gate});
  const second=f.call({op:'read'}),source=await f.call({op:'source-view'});assert.equal(source.result.count,1);
  writeFileSync(gate,'go');const [a,b]=await Promise.all([blocked,second]);assert.equal(a.result.pid,b.result.pid);assert.equal(b.result.count,a.result.count+1);
});
test('split multibyte UTF-8 frames decode once and an API rejection retains the same process',async t=>{
  const f=fixture(t),a=await f.call({op:'read',split:true,text:'α 🐈\nLiteral <script>'});
  assert.equal(a.result.value.text,'α 🐈\nLiteral <script>');await assert.rejects(f.call({op:'read',fail:true}),/TEST: Rejected/);
  assert.equal((await f.call({op:'read'})).result.pid,a.result.pid);
});
test('active mutation transport loss reports uncertainty, queued mutations are unstarted, and only a later call restarts',async t=>{
  const f=fixture(t),a=f.call({op:'annotation-create',die:true}),b=f.call({op:'annotation-create'});
  const ca=assert.rejects(a,/result needs verification/),cb=assert.rejects(b,error=>!/verification/.test(error.message));await Promise.all([ca,cb]);
  const old=f.client.channels.get('main');assert.equal(old.closed,true);
  const next=await f.call({op:'read'});assert.notEqual(f.client.channels.get('main'),old);assert.equal(next.result.count,1);
});
test('malformed, incompatible and unsolicited frames fail the channel rather than shifting reply ownership',async t=>{
  const f=fixture(t);
  for(const bad of ['not json\n','{"api_version":5,"ok":true,"diagnostics":[]}\n',JSON.stringify({api_version:6,ok:true,diagnostics:[],result:{}})+'\n{}\n']){
    const p=f.call({op:'read',bad});
    if(bad.endsWith('{}\n')){await p;await new Promise(r=>setImmediate(r));assert.equal(f.client.channels.get('main').closed,true);}
    else await assert.rejects(p,/Invalid SpecSpec API response/);
    assert.equal((await f.call({op:'read'})).result.count,1);
  }
});
test('frame output, queued input and request deadlines remain bounded',async t=>{
  const f=fixture(t);
  await assert.rejects(f.call({op:'read',bad:'x'.repeat(512)},5000,64),/output limit/);
  await assert.rejects(f.call({op:'read',text:'x'.repeat(16*1024*1024)}),/input limit/);
  await assert.rejects(f.call({op:'annotation-flush',gate:join(f.root,'never')},200),/timed out.*verification/);
});
test('a queued timeout does not dispatch or replay that mutation',async t=>{
  const f=fixture(t),gate=join(f.root,'release'),first=f.call({op:'read',gate});
  await assert.rejects(f.call({op:'annotation-create'},50),error=>/before dispatch/.test(error.message)&&!/verification/.test(error.message));
  writeFileSync(gate,'go');await first;assert.equal((await f.call({op:'read'})).result.count,2);
});
test('queue limits, configuration changes and disposal reject pending work without replay',async t=>{
  const f=fixture(t),gate=join(f.root,'never'),jobs=Array.from({length:33},()=>f.call({op:'read',gate}));
  const checks=jobs.map(p=>assert.rejects(p,/disposed/));await assert.rejects(f.call({op:'read'}),/queue is full/);
  f.client.dispose();await Promise.all(checks);await assert.rejects(f.call({op:'read'}),/Project CLI is closed/);
});
test('ordinary argv/stdin commands retain the one-shot bridge and new configuration replaces channels',async t=>{
  const f=fixture(t);await f.call({op:'read'});const old=f.client.channels.get('main');
  const ordinary=await f.client.invoke(process.execPath,[f.script],f.root,['update','id','--json'],'# Exact\n');
  assert.equal(ordinary.result.value.raw,'# Exact\n');assert.deepEqual(ordinary.result.args,['--root',f.root,'update','id','--json']);
  const second=join(f.root,'second.cjs');writeFileSync(second,require('node:fs').readFileSync(f.script));
  await f.client.invoke(process.execPath,[second],f.root,['api'],JSON.stringify({op:'read'}));assert.equal(old.closed,true);
});
