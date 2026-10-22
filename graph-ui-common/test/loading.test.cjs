const {test}=require('node:test');
const assert=require('node:assert/strict');
const {ProjectDocuments}=require('../host/documents.cjs');
const {GraphSession}=require('../host/session.cjs');
const {SupersededReadError}=require('../host/reads.cjs');
const snapshot={valid:true,format_version:7,nodes:[],edges:[]};
const annotationCli=async()=>({result:{shots:[]}});
const lastSnapshot=messages=>messages.filter(m=>m.type==='snapshot').at(-1);
const deferred=()=>{let resolve;const promise=new Promise(r=>resolve=r);return {promise,resolve};};

test('identical concurrent project reads share work, not mutable view payloads; later reads stay fresh',async()=>{
 const gate=deferred(),calls=[];const doc={path:'_specspec/node.md',text:'A',version:1,dirty:false};
 const cache={commit:'a'.repeat(40),files:{}};
 const p=new ProjectDocuments({documents:()=>[doc],cli:async(args,input)=>{calls.push(JSON.parse(input));await gate.promise;return {result:{snapshot,diagnostics:[],base_cache:cache}};}});
 const a=p.readGraph('HEAD'),b=p.readGraph('HEAD');assert.equal(calls.length,1);gate.resolve();const [x,y]=await Promise.all([a,b]);
 x.snapshot.nodes.push({id:'view-only'});assert.equal(y.snapshot.nodes.length,0);assert.equal(x.base_cache,undefined);
 await p.readGraph('HEAD');assert.equal(calls.length,2);assert.deepEqual(calls[1].base_cache,cache);
 p.dispose();assert.equal(p.baseCache,undefined);await assert.rejects(p.readGraph('HEAD'),/closed/);
});

test('bootstrap is one-shot reusable context with actual stamp checks, not a permanent working cache',async()=>{
 let calls=0;const doc={path:'_specspec/node.md',text:'A',version:1};
 const p=new ProjectDocuments({documents:()=>[doc],cli:async()=>{calls++;return {result:{snapshot,diagnostics:[]}};}});
 const lease=await p.bootstrap();await p.initial(lease);assert.equal(calls,1);
 doc.text='B';await p.initial(lease);assert.equal(calls,2);
 p.changed();await p.initial(lease);assert.equal(calls,3);
});

test('native bootstrap retries document/generation races before attaching the custom editor',async()=>{
 const doc={path:'_specspec/node.md',text:'A',version:1};let calls=0;
 const p=new ProjectDocuments({documents:()=>[doc],cli:async()=>{
  if(++calls<3){doc.text+='x';doc.version++;p.changed();}
  return {result:{snapshot,diagnostics:[]}};
 }});
 const lease=await p.bootstrap();assert.equal(calls,3);assert.equal(lease.generation,p.generation);
 assert.equal(lease.stamp[0][1],'Axx');await p.initial(lease);assert.equal(calls,3);p.dispose();
});

test('native bootstrap preserves bounded supersession and disposal distinctions',async()=>{
 let calls=0;const p=new ProjectDocuments({documents:()=>[],cli:async()=>{calls++;p.changed();return {result:{snapshot}};}});
 await assert.rejects(p.bootstrap(),SupersededReadError);assert.equal(calls,3);p.dispose();
 const gate=deferred();let reads=0;const q=new ProjectDocuments({cli:async()=>{reads++;await gate.promise;return {result:{snapshot}};}});
 const boot=q.bootstrap();q.dispose();gate.resolve();await assert.rejects(boot,/closed/);assert.equal(reads,1);
});

test('changed document text without a notification rejects shared late results; disposal drops hints',async()=>{
 const gate=deferred();const doc={path:'_specspec/node.md',text:'A',version:1};
 const p=new ProjectDocuments({documents:()=>[doc],cli:async()=>{await gate.promise;return {result:{snapshot,base_cache:{commit:'a'.repeat(40),files:{}},diagnostics:[]}};}});
 const reading=p.readGraph('HEAD');doc.text='B';gate.resolve();await assert.rejects(reading,SupersededReadError);
 const q=new ProjectDocuments({documents:()=>[],cli:async()=>({result:{snapshot,base_cache:{commit:'a'.repeat(40),files:{}},diagnostics:[]}})});
 const pending=q.readGraph('HEAD');q.dispose();await assert.rejects(pending,/closed/);assert.equal(q.baseCache,undefined);
});

test('valid working context renders before a delayed comparison with explicit provisional meaning',async t=>{
 const gate=deferred(),messages=[],timings=[];let session;
 session=new GraphSession({authorized:()=>true,cli:annotationCli,initialGraph:async()=>({snapshot,diagnostics:[],note:''}),
 readGraph:async()=>{await gate.promise;return {snapshot,diagnostics:[],note:'Diff unavailable: deliberate test'};},
 trace:(...args)=>timings.push(args),renderMatches:()=>true,
 post:async value=>{messages.push(value);if(value.type==='snapshot')session.receive({type:'rendered',renderToken:value.renderToken});}});
 t.after(()=>session.dispose());session.receive({type:'ready'});const opening=session.open();
 for(let i=0;i<20&&!messages.some(m=>m.provisional);i++)await new Promise(r=>setTimeout(r,1));
 assert.equal(messages.find(m=>m.type==='snapshot').provisional,true);assert.match(messages.find(m=>m.provisional).note,/comparison loading/);
 gate.resolve();await opening;assert.equal(lastSnapshot(messages).provisional,undefined);assert.match(lastSnapshot(messages).note,/unavailable/);
 assert.ok(timings.some(([phase])=>phase==='first-working-render'));assert.ok(timings.some(([phase])=>phase==='complete-comparison-render'));
});

test('historical comparisons bypass provisional working data',async t=>{
 let initial=0,session;const messages=[];
 session=new GraphSession({authorized:()=>true,cli:annotationCli,initialGraph:async()=>{initial++;return {snapshot};},
 readGraph:async()=>({snapshot,diff:{base:snapshot,target:snapshot},diagnostics:[],note:''}),renderMatches:()=>true,
 post:async m=>{messages.push(m);if(m.type==='snapshot')session.receive({type:'rendered',renderToken:m.renderToken});}});
 t.after(()=>session.dispose());session.target='HEAD';session.receive({type:'ready'});await session.open();assert.equal(initial,0);assert.equal(lastSnapshot(messages).readonly,true);
});

function racingSession(t) {
 const doc={path:'_specspec/node.md',text:'A',version:1};
 const messages=[];let races=0,calls=0,session;
 const reads=new ProjectDocuments({documents:()=>[doc],cli:async()=>{
  calls++;
  if(races>0){races--;doc.text+='x';reads.changed();}
  return {result:{snapshot:{...snapshot,nodes:[],label:doc.text},diagnostics:[]}};
 }});
 session=new GraphSession({authorized:()=>true,cli:annotationCli,readGraph:()=>reads.readGraph('HEAD'),
 retryMs:1,debounceMs:2,renderMatches:()=>true,
 post:async m=>{messages.push(m);if(m.type==='snapshot')session.receive({type:'rendered',renderToken:m.renderToken});}});
 session.receive({type:'ready'});t.after(()=>{session.dispose();reads.dispose();});
 return {session,reads,messages,race:n=>{races=n;},calls:()=>calls};
}
async function settled(check) {
 for(let i=0;i<100;i++){if(check())return;await new Promise(r=>setTimeout(r,5));}
 assert.ok(check());
}

test('multiple exhausted superseded-read batches coalesce a fresh attempt without false invalid-file diagnostics',async t=>{
 const f=racingSession(t);await f.session.open();const original=f.session.snapshot;
 f.race(6);f.session.requestRefresh();
 await settled(()=>lastSnapshot(f.messages)?.snapshot.label==='Axxxxxx');await f.session.queue;
 assert.equal(f.calls(),8);assert.notEqual(f.session.snapshot,original);
 assert.equal(f.session.sourceInvalid,false);
 assert.ok(!f.messages.some(m=>['sync-error','error'].includes(m.type)));
 const count=f.calls();await new Promise(r=>setTimeout(r,20));assert.equal(f.calls(),count,'There is no recurring poll after convergence.');
});

test('an explicit superseded read reports retry while retaining its graph and scheduling a current follow-up',async t=>{
 const f=racingSession(t);await f.session.open();const original=f.session.snapshot;
 f.race(3);await assert.rejects(f.session.run(()=>f.session.refresh()),SupersededReadError);
 assert.equal(f.session.snapshot,original);assert.ok(!f.messages.some(m=>m.type==='sync-error'));
 await settled(()=>lastSnapshot(f.messages)?.snapshot.label==='Axxx');await f.session.queue;
 assert.equal(f.session.sourceInvalid,false);
});

test('disposal cancels coalesced supersession retries and actual invalid reads still enter the repair state',async t=>{
 const f=racingSession(t);await f.session.open();f.race(100);f.session.requestRefresh();await f.session.queue;
 f.session.dispose();const count=f.calls();await new Promise(r=>setTimeout(r,20));assert.equal(f.calls(),count);
 const g=racingSession(t);await g.session.open();const original=g.session.snapshot;
 g.session.host.readGraph=async()=>{throw new Error('SCHEMA: invalid actual Markdown');};
 g.session.requestRefresh();await g.session.queue;
 assert.equal(g.session.sourceInvalid,true);assert.equal(g.session.snapshot,original);
 assert.match(g.messages.find(m=>m.type==='sync-error').message,/invalid actual Markdown/);
});

test('late successful and failed reads after disposal do not diagnose or start another CLI operation',async t=>{
 for(const failed of [false,true]) {
  const f=racingSession(t);await f.session.open();const entered=deferred(),finish=deferred();let cliCalls=0;
  f.session.host.cli=async()=>{cliCalls++;return annotationCli();};
  f.session.host.readGraph=async()=>{entered.resolve();await finish.promise;if(failed)throw new Error('Project closed during read');return {snapshot,diagnostics:[]};};
  f.session.requestRefresh();await entered.promise;f.session.dispose();finish.resolve();await f.session.queue;
  assert.equal(cliCalls,0);assert.equal(f.session.sourceInvalid,false);
  assert.equal(f.messages.filter(m=>m.type==='snapshot').length,1);
 }
});
