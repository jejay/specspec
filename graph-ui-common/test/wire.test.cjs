const {test}=require('node:test');
const assert=require('node:assert/strict');
const {comparison,expandResult}=require('../host/wire.cjs');
const {ProjectReads}=require('../host/reads.cjs');
const root={id:'root',type:'manifesto',parents:[],body:'# Root',path:'_specspec/root.md'};
const old={id:'child',type:'requirement',parents:['root'],body:'# Earlier',sources:[],path:'_specspec/child.md'};
const current={format_version:7,valid:true,nodes:[root]};
const compact={base:{format_version:7,valid:true},before:[old],changes:[{id:'child',kind:'removed',fields:[]}],added_edges:[],removed_edges:[['root','child']],impact_complete:true};

test('compact ghost records reconstruct full revision-local membership and edges without mutating input',()=>{
 const input=structuredClone(compact),result=comparison(input,current);
 assert.deepEqual(result.base.nodes.map(n=>n.id),['child','root']);
 assert.deepEqual(result.base.edges,[['root','child']]);assert.deepEqual(result.target.edges,[]);
 assert.equal(result.base.nodes.find(n=>n.id==='child').body,'# Earlier');assert.deepEqual(input,compact);
 const loaded=expandResult({snapshot:current,diff:compact});assert.deepEqual(loaded.diff.target,loaded.snapshot);
 assert.equal(loaded.diff.base.nodes.length,2);
});

test('added and modified records restore original parents independently of the display union',()=>{
 const added={...old,id:'new',parents:['child'],body:'# Added'};
 const changed={...old,parents:['new'],body:'# Changed'};
 const result=comparison({...compact,changes:[{id:'new',kind:'added',fields:[]},{id:'child',kind:'changed',fields:['parents','body']}]},{...current,nodes:[root,added,changed]});
 assert.deepEqual(result.base.nodes.find(n=>n.id==='child'),old);
 assert.equal(result.base.nodes.some(n=>n.id==='new'),false);
 assert.deepEqual(result.target.nodes.find(n=>n.id==='child').parents,['new']);
 assert.throws(()=>comparison({...compact,before:[]},current),/Incomplete previous/);
});

test('saved-file Electron reads use the same optional-overlay coordinator, hints and current refresh path',async()=>{
 const calls=[],coordinator=new ProjectReads({cli:async(args,input)=>{
  const value=JSON.parse(input);calls.push({args,value});
  return {diagnostics:[],result:{snapshot:current,diff:compact,note:'',base_cache:{commit:'a'.repeat(40),files:{}}}};
 }});
 const first=await coordinator.readGraph('HEAD');
 assert.deepEqual(calls[0].args,['api']);assert.deepEqual(calls[0].value.documents,{});
 assert.equal(calls[0].value.api_version,7);assert.equal(calls[0].value.op,'read');
 assert.equal(first.base_cache,undefined);
 await coordinator.readGraph('HEAD');assert.equal(calls.length,2);assert.ok(calls[1].value.base_cache);
 coordinator.changed();await coordinator.readGraph('HEAD');assert.equal(calls.length,3);
 await coordinator.readGraph('HEAD',false,'older');assert.equal(calls[3].value.documents,undefined);assert.equal(calls[3].value.base_cache,undefined);
 coordinator.dispose();await assert.rejects(coordinator.readGraph('HEAD'),/closed/);
});
