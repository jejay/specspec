const { test } = require('node:test');
const assert = require('node:assert/strict');
const { GraphSession, pollInterval } = require('../host/session.cjs');
const { renderMatches, sameNode } = require('../media/graph-model.js');
const node = { id: 'node', type: 'requirement', body: '# Original', parents: [], sources: [], extensions: {}, path: '_specspec/node.md' };
const snapshot = { valid: true, format_version: 6, nodes: [node], edges: [] };
const pause = ms => new Promise(r => setTimeout(r, ms));
async function waitFor(check) { for (let i = 0; i < 100; i++) { if (check()) return; await pause(5); } assert.ok(check()); }
const isComparison = c => c.args[0] === 'api' && JSON.parse(c.input).op === 'read' && Boolean(JSON.parse(c.input).base);
function fixture(t, options = {}) {
  let current = options.snapshot || snapshot, authorized = true, failure = false, remainingFailures = 0, shots = options.shots || [];
  let annotationFailure = false;
  const calls = [], messages = [], confirmations = [];
  const s = new GraphSession({
    timeout: 40, retryMs: 1, debounceMs: 5, authorized: () => authorized, renderMatches, sameNode,
    cli: async (args, input) => { calls.push({ args, input });
      const value = args[0] === 'api' ? JSON.parse(input) : undefined;
      if (value?.op === 'annotations') {
        if (annotationFailure) throw new Error('Malformed local shot');
        return { api_version: 6, ok: true, diagnostics: [], result: { shots } };
      }
      if (value?.op === 'annotation-create') {
        if (options.creationFailure) throw new Error('Highlighted version changed.');
        return { api_version: 6, ok: true, result: { shots: [] } };
      }
      if (value?.op === 'annotation-flush') { shots = []; return { api_version: 6, ok: true, result: { flushed: 1 } }; }
      if (failure || remainingFailures-- > 0) throw new Error('YAML: partial external save');
      if (options.slow) await pause(options.slow);
      if (args[0] === 'update') current = { ...current, nodes: current.nodes.map(n => n.id === args[1] ? { ...n, body: input } : n), changed_ids: [args[1]] };
      if (args[0] === 'delete') {
        if (args.includes('--dry-run')) return { api_version: 6, ok: true, diagnostics: options.deleteWarnings || [], result: options.deletePlan || { requested_ids: [args[1]], deleted_ids: [args[1]], nodes: [{ id: args[1], path: node.path }], uncommitted: [], git_available: true, git_note: '' } };
        if (options.deleteError) throw new Error(options.deleteError);
        const plan = JSON.parse(input);
        current = { ...current, nodes: current.nodes.filter(n => !plan.deleted_ids.includes(n.id)), changed_ids: plan.deleted_ids };
      }
      return { api_version: 6, ok: true, diagnostics: [], result: value ? { snapshot: current, changes: [], note: '', ...(value.base ? {diff: {
        base: current, target: current, changes: [], added_edges: [], removed_edges: [],
        base_ref: value.base, target_ref: value.target || 'workspace', source_changes: [], source_affected: [],
      }} : {}) } : current };
    },
    post: async value => { messages.push(value); if (value.type === 'snapshot' && !options.noRender) s.receive({ type: 'rendered',
      renderToken: value.renderToken, view: 'overview',
      visibleIds: options.wrongMembership ? [] : value.snapshot.nodes.map(n => n.id), nodeCount: value.snapshot.nodes.length }); },
    confirm: async text => { confirmations.push(text); return options.confirm !== false; },
    revisions: async () => options.revisions,
  });
  t.after(() => s.dispose()); s.receive({ type: 'ready' });
  return { s, calls, messages, confirmations, change: value => { current = value; }, fail: value => { failure = value; }, failNext: count => { remainingFailures = count; }, changeShots: value => { shots = value; }, failAnnotations: value => { annotationFailure = value; }, revoke: () => { authorized = false; } };
}
test('highlight creation uses the guarded local API with trusted overlays, not canonical mutations', async t => {
  const f = fixture(t); await f.s.open();
  let drained = false;
  f.s.documentEdits = Promise.resolve().then(() => { drained = true; });
  f.s.host.annotationDocuments = async () => { assert.ok(drained); return { '_specspec/node.md': 'Native dirty text' }; };
  const message = 'Please reconsider', nodes = ['Zm9vYmE='];
  const count = f.calls.length;
  await f.s.handle({ type: 'annotation-create', message, nodes, documents: { 'forged.md': 'ignored' }, target: 'forged' });
  const request = JSON.parse(f.calls.slice(count).find(c => JSON.parse(c.input).op === 'annotation-create').input);
  assert.deepEqual(request, { api_version: 6, op: 'annotation-create', message, nodes, documents: { '_specspec/node.md': 'Native dirty text' } });
  assert.equal(f.messages.at(-1).type, 'annotation-created');
  assert.ok(!f.calls.slice(count).some(c => ['add','update','delete'].includes(c.args[0])));
  f.revoke(); const before = f.calls.length;
  await f.s.handle({type:'annotation-create',message,nodes});
  assert.equal(f.calls.length,before); assert.equal(f.messages.at(-1).type,'annotation-create-error');
  assert.match(f.messages.at(-1).message,/authorization/);
});

test('historical highlight creation pins selected commits and excludes live documents', async t => {
  const f=fixture(t,{revisions:['older','newer']}); await f.s.open(); await f.s.chooseRevisions();
  f.s.lastPayload.diff.base_commit='b'.repeat(40); f.s.lastPayload.diff.target_commit='c'.repeat(40);
  f.s.host.annotationDocuments=()=>{throw new Error('Historical capture must not read live documents.');};
  const message='Old intent', nodes=['Zm9vYmE='];
  await f.s.handle({type:'annotation-create',message,nodes});
  const call=f.calls.find(c=>c.args[0]==='api'&&JSON.parse(c.input).op==='annotation-create');
  assert.deepEqual(JSON.parse(call.input),{api_version:6,op:'annotation-create',message,nodes,base:'b'.repeat(40),target:'c'.repeat(40)});
  assert.equal(f.messages.at(-1).type,'annotation-created');
});

test('creation errors return a retryable compose response and never publish a false success', async t => {
  const f=fixture(t,{creationFailure:true}); await f.s.open();
  const message='Retry me', nodes=['Zm9vYmE='];
  await f.s.handle({type:'annotation-create',message,nodes});
  assert.equal(f.messages.at(-1).type,'annotation-create-error'); assert.match(f.messages.at(-1).message,/version changed/);
  assert.equal(f.messages.some(m=>m.type==='annotation-created'),false);
  const count=f.calls.length;
  for(const invalid of [[],null,[{id:'Zm9vYmE='}]]) await f.s.handle({type:'annotation-create',message,nodes:invalid});
  for(const invalid of ['', 'x'.repeat(501), null]) await f.s.handle({type:'annotation-create',message:invalid,nodes});
  assert.equal(f.calls.length,count); assert.equal(f.messages.at(-1).type,'annotation-create-error');
});

test('source capture invokes only a validated preview and never a writer or Git operation', async t => {
  const impl={...node,type:'implementation'};const f=fixture(t,{snapshot:{...snapshot,nodes:[impl]}});await f.s.open();
  await f.s.handle({type:'source-capture',id:'node',path:'code.js',ranges:['2:4','9:10'],mode:'strict',staged:true});
  const c=f.calls.at(-1);assert.deepEqual(c.args,['api']);assert.deepEqual(JSON.parse(c.input),{api_version:6,op:'source-capture',id:'node',path:'code.js',ranges:['2:4','9:10'],mode:'strict',staged:true});
  assert.equal(f.calls.some(c=>['update','add'].includes(c.args[0])),false);
  await assert.rejects(f.s.handle({type:'source-capture',id:'node',path:'code.js',ranges:['--bad'],mode:'strict'}),/Invalid/);
  f.revoke();await assert.rejects(f.s.handle({type:'source-view',id:'node',reference:'{}'}),/authorization/);
});

test('source previews in historical views use selected code revisions but never permit capture', async t => {
  const impl={...node,type:'implementation'};const f=fixture(t,{snapshot:{...snapshot,nodes:[impl]},revisions:['older','newer']});await f.s.open();await f.s.chooseRevisions();
  await f.s.handle({type:'source-view',id:'node',requestId:1,renderToken:f.s.renderSequence,reference:JSON.stringify({path:'code.js'})});
  assert.deepEqual(f.calls.at(-1).args,['api']);assert.deepEqual(JSON.parse(f.calls.at(-1).input),{api_version:6,op:'source-view',reference:{path:'code.js'},ref:'newer'});
  await assert.rejects(f.s.handle({type:'source-capture',id:'node',path:'code.js',ranges:['1:2'],mode:'strict'}),/editable/);
});

const sourceRequest = (f,requestId) => ({type:'source-view',id:'node',requestId,renderToken:f.s.renderSequence,reference:JSON.stringify({path:`code-${requestId}.js`})});
const implementation = {...node,type:'implementation'};
function gate(t) { let release; const waiting=new Promise(resolve=>{release=resolve;});t.after(()=>release());return {waiting,release}; }

test('interactive source reads complete while automatic graph synchronization is blocked', async t => {
  const f=fixture(t,{snapshot:{...snapshot,nodes:[implementation]}});await f.s.open();
  const blocked=gate(t);let entered=false;
  f.s.host.readGraph=async()=>{entered=true;await blocked.waiting;return {snapshot:f.s.snapshot};};
  f.s.requestRefresh();await waitFor(()=>entered);
  f.s.receive(sourceRequest(f,1));await waitFor(()=>f.messages.some(m=>m.type==='source-preview'));
  assert.equal(f.messages.find(m=>m.type==='source-preview').requestId,1);
  assert.equal(f.s.autoQueued,true,'Preview delivery does not wait for the blocked synchronization.');
  blocked.release();await f.s.queue;
});

test('source lane freezes displayed commit IDs and coalesces clicks to the latest pending preview', async t => {
  const f=fixture(t,{snapshot:{...snapshot,nodes:[implementation]}});await f.s.open();
  f.s.target='moving-tag';f.s.lastPayload.readonly=true;f.s.lastPayload.diff={target_commit:'a'.repeat(40),base:{nodes:[]}};
  const blocked=gate(t),requests=[],cli=f.s.host.cli;
  f.s.host.cli=async(args,input)=>{const v=JSON.parse(input);if(v.op==='source-view'){requests.push(v);if(requests.length===1)await blocked.waiting;}return cli(args,input);};
  const first=f.s.sourcePreview(sourceRequest(f,1));await waitFor(()=>requests.length===1);
  const middle=f.s.sourcePreview(sourceRequest(f,2)),last=f.s.sourcePreview(sourceRequest(f,3));
  assert.equal(requests.length,1);blocked.release();await Promise.all([first,middle,last]);
  assert.deepEqual(requests.map(r=>[r.reference.path,r.ref]),[['code-1.js','a'.repeat(40)],['code-3.js','a'.repeat(40)]]);
  assert.deepEqual(f.messages.filter(m=>m.type==='source-preview').map(m=>m.requestId),[3]);
});

test('deleted source previews use the displayed base commit and discard changed-context results',async t=>{
  const f=fixture(t,{snapshot:{...snapshot,nodes:[implementation]}});await f.s.open();
  f.s.snapshot={...snapshot,nodes:[]};f.s.lastPayload.snapshot=f.s.snapshot;f.s.lastPayload.diff={base:{nodes:[implementation]},base_commit:'b'.repeat(40)};
  const blocked=gate(t),cli=f.s.host.cli;let request;
  f.s.host.cli=async(args,input)=>{request=JSON.parse(input);await blocked.waiting;return cli(args,input);};
  const pending=f.s.sourcePreview(sourceRequest(f,1));await waitFor(()=>Boolean(request));
  assert.equal(request.ref,'b'.repeat(40));
  f.s.lastPayload.diff.base_commit='c'.repeat(40);blocked.release();await pending;
  assert.equal(f.messages.some(m=>m.type==='source-preview'),false);
});

test('source disposal drops active/pending delivery and current failures have correlated errors',async t=>{
  const f=fixture(t,{snapshot:{...snapshot,nodes:[implementation]}});await f.s.open();
  f.s.host.cli=async()=>{throw new Error('Source unavailable');};
  f.s.receive(sourceRequest(f,1));await waitFor(()=>f.messages.some(m=>m.type==='source-error'));
  assert.deepEqual(f.messages.at(-1),{type:'source-error',requestId:1,message:'Source unavailable'});
  for(const requestId of [0,-1,NaN,'1'])await assert.rejects(f.s.sourcePreview({...sourceRequest(f,1),requestId}),/Invalid/);
  const blocked=gate(t);let entered=0;
  f.s.host.cli=async()=>{entered++;await blocked.waiting;return {result:{}};};
  const a=f.s.sourcePreview(sourceRequest(f,2)),b=f.s.sourcePreview(sourceRequest(f,3));
  await waitFor(()=>entered===1);f.s.dispose();blocked.release();await Promise.all([a,b]);
  assert.equal(entered,1);assert.equal(f.messages.some(m=>m.type==='source-preview'),false);
});

test('source previews bind the published render, not a pending comparison or mutation preflight',async t=>{
  const f=fixture(t,{snapshot:{...snapshot,nodes:[implementation]}});await f.s.open();
  await assert.rejects(f.s.sourcePreview({...sourceRequest(f,1),renderToken:0}),/view changed/);
  f.s.target='pending-comparison';await f.s.sourcePreview(sourceRequest(f,2));
  assert.equal(JSON.parse(f.calls.at(-1).input).ref,undefined,'Displayed working view stays working while a comparison loads.');
  f.s.lastPayload.readonly=true;f.s.lastPayload.diff={target_commit:'d'.repeat(40),base:{nodes:[]}};
  f.s.target=undefined;f.s.snapshot={...snapshot,nodes:[]};await f.s.sourcePreview(sourceRequest(f,3));
  assert.equal(JSON.parse(f.calls.at(-1).input).ref,'d'.repeat(40),'Historical display stays pinned during workspace/preflight changes.');
});

test('graph-only automatic refresh skips Spotlight IO while independent list arrivals bypass its queue',async t=>{
  const f=fixture(t);await f.s.open();
  const before=()=>f.calls.filter(c=>JSON.parse(c.input||'{}').op==='annotations').length;
  const initial=before();await f.s.refresh(false,undefined,true);assert.equal(before(),initial);
  await f.s.refresh();assert.equal(before(),initial+1,'Explicit Refresh keeps the missed-event fallback.');
  const blocked=gate(t);let entered=false;
  f.s.host.readGraph=async()=>{entered=true;await blocked.waiting;return {snapshot};};
  f.s.requestRefresh();await waitFor(()=>entered);f.s.requestAnnotationsRefresh();
  await waitFor(()=>before()===initial+2);assert.equal(f.s.autoQueued,true);
  blocked.release();await f.s.queue;
});

test('concurrent explicit/event Spotlight reads share one flight and one coalesced follow-up',async t=>{
  const f=fixture(t);await f.s.open();const blocked=gate(t),cli=f.s.host.cli;let entered=0;
  f.s.host.cli=async(args,input)=>{if(JSON.parse(input).op==='annotations'){entered++;if(entered===1)await blocked.waiting;}return cli(args,input);};
  const first=f.s.refreshAnnotations(),second=f.s.refreshAnnotations();f.s.requestAnnotationsRefresh();
  await waitFor(()=>entered===1);await pause(10);assert.equal(entered,1);
  blocked.release();await Promise.all([first,second]);await waitFor(()=>entered===2);await pause(20);assert.equal(entered,2);
});

const save = originalNode => ({ type: 'save', id: 'node', originalNode, parents: [], sources: '[]', body: '# Draft' });

test('unsupported schema snapshots cannot invoke a writer', async t => {
  const f = fixture(t, { snapshot: { ...snapshot, format_version: 999 } }); await f.s.open();
  await assert.rejects(f.s.handle(save(node)), /Unsupported/);
  assert.ok(!f.calls.some(c => c.args[0] === 'update'));
});
test('authorization loss and historical selection block writes', async t => {
  const f = fixture(t); await f.s.open(); f.revoke();
  await assert.rejects(f.s.handle(save(node)), /authorization/);
  assert.ok(!f.calls.some(c => c.args[0] === 'update'));
  const history = fixture(t, { revisions: ['HEAD', 'HEAD'] }); await history.s.open(); await history.s.chooseRevisions();
  await assert.rejects(history.s.handle(save(node)), /read-only/);
});
test('full render membership and sequence tokens replace fingerprint acknowledgements', async t => {
  const wrong = fixture(t, { wrongMembership: true }); await assert.rejects(wrong.s.open(), /incomplete/);
  const absent = fixture(t, { noRender: true }); await assert.rejects(absent.s.open(), /rendering timed out/);
  const ok = fixture(t); await ok.s.open();
  ok.s.receive({ type: 'rendered', renderToken: 0, view: 'overview', visibleIds: [], nodeCount: 0 });
  assert.equal(ok.s.renderError, undefined);
});
test('disposal releases an outstanding renderer wait', async t => {
  const { s, messages } = fixture(t, { noRender: true }); const opening = s.open();
  await waitFor(() => messages.some(m => m.type === 'snapshot'));
  s.dispose(); await assert.rejects(opening, /closed while rendering/);
});
test('serialized operations pass body as stdin, never renderer commands', async t => {
  const f = fixture(t); await f.s.open();
  await Promise.all([f.s.run(() => f.s.handle({ type: 'refresh' })), f.s.run(() => f.s.handle({ type: 'refresh' }))]);
  await f.s.handle({ type: 'add', nodeType: 'requirement', slug: 'literal', parents: [], body: '# Literal $(touch anything)', sources: '[]' });
  const write = f.calls.find(c => c.args[0] === 'add'); assert.equal(write.input, '# Literal $(touch anything)');
  assert.ok(!write.args.includes(write.input)); assert.ok(!write.args.includes('--expect'));
  await assert.rejects(f.s.handle({ type: 'exec', command: 'anything' }), /Select a current node|Unknown graph/);
});
test('unrelated changes do not block drafts; every save re-reads actual files', async t => {
  const f = fixture(t); await f.s.open(); f.change({ ...snapshot, nodes: [node, { ...node, id: 'another', body: '# External' }] });
  await f.s.handle(save(node));
  assert.equal(f.confirmations.length, 0);
  const write = f.calls.findIndex(c => c.args[0] === 'update');
  assert.equal(f.calls[write - 1].args[0], 'show');
  assert.ok(f.calls[write].args.every(a => a !== '--expect'));
});
test('same-node external changes ask before overwrite; cancellation retains current contents', async t => {
  const f = fixture(t, { confirm: false }); await f.s.open(); f.change({ ...snapshot, nodes: [{ ...node, body: '# External' }] });
  await f.s.handle(save(node)); assert.match(f.confirmations[0], /changed outside/);
  assert.equal(f.messages.at(-1).type, 'cancelled'); assert.ok(!f.calls.some(c => c.args[0] === 'update'));
  const yes = fixture(t); await yes.s.open(); yes.change({ ...snapshot, nodes: [{ ...node, body: '# External' }] });
  await yes.s.handle(save(node)); assert.ok(yes.calls.some(c => c.args[0] === 'update'));
});
test('missing original records ask confirmation and deleted edited nodes are never recreated', async t => {
  const f = fixture(t, { confirm: false }); await f.s.open(); await f.s.handle(save(undefined)); assert.equal(f.confirmations.length, 1);
  f.change({ ...snapshot, nodes: [] }); await assert.rejects(f.s.handle(save(node)), /Select a current node/);
  assert.ok(!f.calls.some(c => ['update', 'add'].includes(c.args[0])));
});
test('watcher bursts coalesce, identical data does not redraw, and changed contents do', async t => {
  const f = fixture(t); await f.s.open(); const first = f.messages.filter(m => m.type === 'snapshot').length;
  for (let i = 0; i < 50; i++) f.s.scheduleRefresh();
  await pause(25); await f.s.queue;
  assert.equal(f.calls.filter(isComparison).length, 2);
  assert.equal(f.messages.filter(m => m.type === 'snapshot').length, first);
  f.change({ ...snapshot, nodes: [{ ...node, body: '# Manual change' }] }); f.s.scheduleRefresh();
  await waitFor(() => f.messages.filter(m => m.type === 'snapshot').length === first + 1);
});
test('invalid reloads retain the last graph, disable editing, and later valid events restore it', async t => {
  const f = fixture(t); await f.s.open(); const original = f.s.snapshot; f.fail(true); f.s.scheduleRefresh();
  await waitFor(() => f.messages.at(-1).type === 'sync-error');
  assert.equal(f.s.snapshot, original); assert.equal(f.s.sourceInvalid, true);
  await assert.rejects(f.s.handle(save(node)), /YAML/); assert.ok(!f.calls.some(c => c.args[0] === 'update'));
  f.fail(false); f.s.scheduleRefresh(); await waitFor(() => f.messages.at(-1).type === 'snapshot');
  assert.equal(f.s.sourceInvalid, false);
});
test('partial writes retry a bounded number of times without a false invalid view', async t => {
  const f = fixture(t); await f.s.open(); f.failNext(2); f.s.scheduleRefresh();
  await waitFor(() => f.calls.filter(isComparison).length >= 4); await f.s.queue;
  assert.ok(!f.messages.some(m => m.type === 'sync-error'));
});
test('polling is off by default, configurable, coalesced, and cancelled on disposal', async t => {
  const f = fixture(t); await f.s.open(); assert.equal(f.s.pollTimer, undefined);
  const before = f.calls.length; await pause(25); assert.equal(f.calls.length, before);
  f.s.configurePolling(8); await waitFor(() => f.calls.length > before);
  f.s.configurePolling(0); await pause(20); await f.s.queue; const off = f.calls.length; await pause(25); assert.equal(f.calls.length, off);
  f.s.configurePolling(8); f.s.dispose(); await pause(25); assert.equal(f.calls.length, off);
  for (const value of [-1, 0.5, NaN, '10', 2_147_483_648]) assert.throws(() => pollInterval(value), /Polling interval/);
});
test('polls do not pile up behind slow reads or refresh immutable historical targets', async t => {
  const f = fixture(t, { revisions: ['HEAD', 'HEAD'] }); await f.s.open();
  const cli = f.s.host.cli, before = f.calls.filter(isComparison).length;
  let release, entered = 0;
  const blocked = new Promise(resolve => { release = resolve; });
  f.s.host.cli = async (args, input) => {
    if (isComparison({ args, input })) { entered++; await blocked; }
    return cli(args, input);
  };
  f.s.configurePolling(1); await waitFor(() => entered === 1);
  for (let i = 0; i < 20; i++) f.s.requestRefresh();
  await pause(10); f.s.configurePolling(0);
  assert.equal(entered, 1, 'One comparison stays in flight while ticks and refresh hints coalesce.');
  f.s.host.cli = cli; release();
  await waitFor(() => f.calls.filter(isComparison).length >= before + 2); await f.s.queue;
  assert.equal(f.calls.filter(isComparison).length, before + 2, 'The blocked read gets exactly one coalesced follow-up.');
  await f.s.chooseRevisions(); const count = f.calls.filter(isComparison).length; f.s.configurePolling(2); f.s.scheduleRefresh(); await pause(25);
  assert.equal(f.calls.filter(isComparison).length, count);
  assert.ok(f.calls.some(c => c.args[0] === 'api' && JSON.parse(c.input).op === 'annotations'));
});
test('Delete previews a backend descendant plan and warns about partial uncommitted children before one confirmation', async t => {
  const plan = { requested_ids: ['node'], deleted_ids: ['child', 'node'], nodes: [{id:'child',path:'_specspec/child.md'},{id:'node',path:node.path}], uncommitted:[{id:'child',path:'_specspec/child.md',status:'A '}], git_available:true,git_note:'' };
  const warnings = [{ severity:'warning',node_id:'child',message:'Node child has uncommitted Git changes (A ); staging is not committing.' }];
  const f = fixture(t,{deletePlan:plan,deleteWarnings:warnings});await f.s.open();
  await f.s.handle({type:'delete',id:'node'});
  const calls=f.calls.filter(c=>c.args[0]==='delete');
  assert.deepEqual(calls.map(c=>c.args),[['delete','node','--dry-run','--json'],['delete','node','--yes','--reviewed-plan','-','--json']]);
  assert.deepEqual(JSON.parse(calls[1].input),plan);
  assert.equal(f.confirmations.length,1);assert.match(f.confirmations[0],/ALL.*descendants.*2 Markdown/);
  assert.match(f.confirmations[0],/shared with surviving parents/);assert.match(f.confirmations[0],/uncommitted.*child.*staging is not committing/s);
});
test('Delete cancellation and a changed plan retain input and never silently retry an enlarged cascade', async t => {
  const no=fixture(t,{confirm:false});await no.s.open();await no.s.handle({type:'delete',id:'node'});
  assert.equal(no.messages.at(-1).type,'cancelled');
  assert.ok(no.calls.filter(c=>c.args[0]==='delete').every(c=>c.args.includes('--dry-run')));
  const changed=fixture(t,{deleteError:'Deletion scope or uncommitted warnings changed; preview and confirm again.'});await changed.s.open();
  await assert.rejects(changed.s.handle({type:'delete',id:'node'}),/preview and confirm again/);
  assert.equal(changed.calls.filter(c=>c.args[0]==='delete'&&!c.args.includes('--dry-run')).length,1);
  assert.equal(changed.s.snapshot.nodes[0].body,node.body);
});
test('native document sessions coalesce rapid typing, flush received edits, and acknowledge per-view sequences', async t => {
  const f = fixture(t), edits = []; let version = 1;
  f.s.host.document = {
    state: () => ({ nodeId: 'node', version, dirty: true }),
    edit: async message => { edits.push(message.editSequence); await pause(10); version++; return true; },
    save: async () => {},
  };
  await f.s.open(); assert.equal(f.messages.filter(m => m.type === 'snapshot').at(-1).selectedId, 'node');
  for (let i = 1; i <= 20; i++) f.s.receive({ type: 'edit', id: 'node', editSequence: i });
  await f.s.flushDocument(); assert.deepEqual(edits, [1, 20]);
  assert.deepEqual(f.messages.filter(m => m.type === 'document-status').map(m => m.editSequence), [1, 20]);
  assert.ok(!f.calls.some(c => c.args[0] === 'update'));
});

const annotationShot = { id: '1'.repeat(32), message: 'Answer', comparison: {base:'HEAD',target:'workspace'}, nodes:['node'], workspace:{head:null,changes:{}} };
test('spotlight selection loads its pinned comparison before applying and preserves workspace access', async t => {
  const shot = {...annotationShot, comparison:{base:'b'.repeat(40),target:'c'.repeat(40)}};
  const f=fixture(t,{shots:[shot]}); await f.s.open();
  await f.s.handle({type:'annotation-select',shot:shot.id,base:'forged',target:'forged'});
  assert.equal(f.s.base,shot.comparison.base);assert.equal(f.s.target,shot.comparison.target);
  const applied=f.messages.findLastIndex(m=>m.type==='annotation-applied');
  const rendered=f.messages.findLastIndex(m=>m.type==='snapshot');
  assert.ok(applied>rendered);assert.equal(f.messages[rendered].readonly,true);
  assert.deepEqual(f.messages[rendered].annotationShot,shot);
  await f.s.handle({type:'workspace'});assert.equal(f.s.target,undefined);assert.equal(f.s.base,'HEAD');
  assert.equal(f.s.activeSpotlight,undefined);
  assert.ok(f.messages.some(m=>m.type==='annotation-context'));
  f.revoke();await assert.rejects(f.s.handle({type:'annotation-select',shot:shot.id}),/authorization/);
});

test('unavailable comparison keeps the usable graph and applies IDs with an explicit fallback warning', async t => {
  const shot={...annotationShot,comparison:{base:'older',target:'missing'}};
  const f=fixture(t,{shots:[shot]});await f.s.open();const before=f.s.snapshot;
  const cli=f.s.host.cli;f.s.host.cli=async(args,input)=>{if(JSON.parse(input).target==='missing')throw new Error('Commit unavailable');return cli(args,input);};
  await f.s.handle({type:'annotation-select',shot:shot.id});
  assert.equal(f.s.snapshot,before);assert.equal(f.s.sourceInvalid,false);assert.equal(f.s.base,'HEAD');assert.equal(f.s.target,undefined);
  assert.equal(f.messages.at(-1).type,'annotation-applied');assert.match(f.messages.at(-1).warning,/using the displayed graph.*Commit unavailable/);
});

test('workspace spotlight fallback keeps actual invalid-file restrictions while applying available IDs', async t => {
  const f=fixture(t,{shots:[annotationShot]});await f.s.open();f.fail(true);
  await f.s.handle({type:'annotation-select',shot:annotationShot.id});
  assert.equal(f.s.sourceInvalid,true);assert.equal(f.messages.at(-1).type,'annotation-applied');
  assert.equal(f.messages.at(-1).invalid,true);
});

test('native document saves and edits remain guarded after a spotlight switches to historical comparison', async t => {
  const f=fixture(t);await f.s.open();let writes=0;
  f.s.host.document={state:()=>({nodeId:'node'}),edit:()=>{writes++;},save:()=>{writes++;}};
  f.s.target='older';
  await assert.rejects(f.s.handle({type:'save',id:'node'}),/read-only/);
  await assert.rejects(f.s.editDocument({type:'edit',id:'node'}),/read-only/);
  assert.equal(writes,0);
});

test('unavailable restored comparisons fall back to workspace with a visible advisory', async t => {
  const shot={...annotationShot,comparison:{base:'older',target:'missing'}};
  const f=fixture(t,{shots:[shot]}),cli=f.s.host.cli;
  f.s.host.cli=async(args,input)=>{if(JSON.parse(input).target==='missing')throw new Error('Missing commit');return cli(args,input);};
  f.s.receive({type:'ready',spotlight:shot.id});await f.s.open();
  assert.equal(f.s.target,undefined);assert.equal(f.s.base,'HEAD');assert.equal(f.s.sourceInvalid,false);
  assert.equal(f.messages.at(-1).type,'annotation-applied');assert.match(f.messages.at(-1).warning,/workspace \/ HEAD/);
});

test('restored spotlight identity selects its stored comparison before startup rendering', async t => {
  const shot={...annotationShot,comparison:{base:'b'.repeat(40),target:'c'.repeat(40)}};
  const f=fixture(t,{shots:[shot]});f.s.receive({type:'ready',spotlight:shot.id});await f.s.open();
  assert.equal(f.s.target,shot.comparison.target);assert.equal(f.messages.find(m=>m.type==='snapshot').readonly,true);
});

test('a reloaded renderer receives the unchanged retained spotlight list as its new baseline', async t => {
  const f = fixture(t, { shots: [annotationShot] }); await f.s.open();
  const reads = f.calls.filter(isComparison).length;
  const before = f.messages.filter(m => m.type === 'annotations').length;
  f.s.receive({ type: 'ready' }); await f.s.refreshAnnotations();
  assert.equal(f.messages.filter(m => m.type === 'annotations').length, before + 1);
  assert.deepEqual(f.messages.at(-1), { type: 'annotations', shots: [annotationShot] });
  assert.equal(f.calls.filter(isComparison).length, reads);
});

test('annotation arrivals coalesce independently, including historical views, with no graph read or render', async t => {
  const f = fixture(t, { revisions: ['HEAD', 'HEAD'] }); await f.s.open(); await f.s.chooseRevisions();
  const reads = f.calls.filter(isComparison).length, renders = f.messages.filter(m => m.type === 'snapshot').length;
  f.changeShots([annotationShot]); for (let i = 0; i < 40; i++) f.s.scheduleAnnotationsRefresh();
  await waitFor(() => f.messages.some(m => m.type === 'annotations' && m.shots.length));
  assert.equal(f.calls.filter(isComparison).length, reads); assert.equal(f.messages.filter(m => m.type === 'snapshot').length, renders);
  const arrivals = f.messages.filter(m => m.type === 'annotations').length;
  f.s.scheduleAnnotationsRefresh(); await pause(25); await f.s.queue;
  assert.equal(f.messages.filter(m => m.type === 'annotations').length, arrivals);
  f.failAnnotations(true); f.s.scheduleAnnotationsRefresh(); await waitFor(() => f.messages.at(-1).type === 'annotations-error');
  assert.equal(f.s.sourceInvalid, false); assert.deepEqual(f.s.annotationShots, [annotationShot]);
  f.failAnnotations(false); f.s.scheduleAnnotationsRefresh(); await waitFor(() => f.messages.at(-1).type === 'annotations');
  f.s.dispose(); const calls = f.calls.length; f.s.scheduleAnnotationsRefresh(); await pause(20); assert.equal(f.calls.length, calls);
});
test('spotlight selection validates known identity and flush confirms a reviewed list even in read-only views', async t => {
  const f = fixture(t, { shots: [annotationShot], revisions: ['HEAD', 'HEAD'] }); await f.s.open(); await f.s.chooseRevisions();
  await f.s.handle({ type: 'annotation-select', shot: annotationShot.id, base:'forged',target:'forged' });
  assert.equal(f.messages.at(-1).type, 'annotation-applied');
  assert.equal(f.s.base,'HEAD'); assert.equal(f.s.target,undefined);
  await assert.rejects(f.s.handle({ type: 'annotation-select', shot: '../owner' }), /existing/);
  await f.s.handle({ type: 'annotation-flush' });
  assert.match(f.confirmations[0], /both UIs.*Specification files, Git and recovery/s);
  const flush = f.calls.find(c => c.args[0] === 'api' && JSON.parse(c.input).op === 'annotation-flush');
  assert.deepEqual(JSON.parse(flush.input), { api_version: 6, op: 'annotation-flush', expected: [annotationShot.id] });
  assert.deepEqual(f.messages.at(-1), { type: 'annotations', shots: [] });
  assert.ok(!f.calls.some(c => ['update','delete','add'].includes(c.args[0])));
  const no = fixture(t, { shots: [annotationShot], confirm: false }); await no.s.open(); await no.s.handle({ type: 'annotation-flush' });
  assert.ok(!no.calls.some(c => c.args[0] === 'api' && JSON.parse(c.input).op === 'annotation-flush'));
  no.revoke(); await assert.rejects(no.s.handle({ type: 'annotation-flush' }), /authorization/);
});
