const {test}=require('node:test');
const assert=require('node:assert/strict');
const {ProjectDocuments}=require('../host/documents.cjs');
const {GraphSession}=require('../host/session.cjs');
const snapshot={valid:true,format_version:5,nodes:[],edges:[]};
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

test('changed document text without a notification rejects shared late results; disposal drops hints',async()=>{
 const gate=deferred();const doc={path:'_specspec/node.md',text:'A',version:1};
 const p=new ProjectDocuments({documents:()=>[doc],cli:async()=>{await gate.promise;return {result:{snapshot,base_cache:{commit:'a'.repeat(40),files:{}},diagnostics:[]}};}});
 const reading=p.readGraph('HEAD');doc.text='B';gate.resolve();await assert.rejects(reading,/changed during/);
 const q=new ProjectDocuments({documents:()=>[],cli:async()=>({result:{snapshot,base_cache:{commit:'a'.repeat(40),files:{}},diagnostics:[]}})});
 const pending=q.readGraph('HEAD');q.dispose();await assert.rejects(pending,/changed during/);assert.equal(q.baseCache,undefined);
});

test('valid working context renders before a delayed comparison with explicit provisional meaning',async t=>{
 const gate=deferred(),messages=[],timings=[];let session;
 session=new GraphSession({authorized:()=>true,initialGraph:async()=>({snapshot,diagnostics:[],note:''}),
 readGraph:async()=>{await gate.promise;return {snapshot,diagnostics:[],note:'Diff unavailable: deliberate test'};},
 trace:(...args)=>timings.push(args),renderMatches:()=>true,
 post:async value=>{messages.push(value);if(value.type==='snapshot')session.receive({type:'rendered',renderToken:value.renderToken});}});
 t.after(()=>session.dispose());session.receive({type:'ready'});const opening=session.open();
 for(let i=0;i<20&&!messages.some(m=>m.provisional);i++)await new Promise(r=>setTimeout(r,1));
 assert.equal(messages.find(m=>m.type==='snapshot').provisional,true);assert.match(messages.find(m=>m.provisional).note,/comparison loading/);
 gate.resolve();await opening;assert.equal(messages.at(-1).provisional,undefined);assert.match(messages.at(-1).note,/unavailable/);
 assert.ok(timings.some(([phase])=>phase==='first-working-render'));assert.ok(timings.some(([phase])=>phase==='complete-comparison-render'));
});

test('historical comparisons bypass provisional working data',async t=>{
 let initial=0,session;const messages=[];
 session=new GraphSession({authorized:()=>true,initialGraph:async()=>{initial++;return {snapshot};},
 readGraph:async()=>({snapshot,diff:{base:snapshot,target:snapshot},diagnostics:[],note:''}),renderMatches:()=>true,
 post:async m=>{messages.push(m);if(m.type==='snapshot')session.receive({type:'rendered',renderToken:m.renderToken});}});
 t.after(()=>session.dispose());session.target='HEAD';session.receive({type:'ready'});await session.open();assert.equal(initial,0);assert.equal(messages.at(-1).readonly,true);
});
