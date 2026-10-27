const { test } = require('node:test');
const assert = require('node:assert/strict');
const { mkdtemp, mkdir, writeFile, symlink, rm } = require('node:fs/promises');
const { join } = require('node:path');
const { tmpdir } = require('node:os');
const { probeCli, inspectProject, CliUnavailableError } = require('../host/startup.cjs');
const { GraphSession } = require('../host/session.cjs');
const { renderMatches, sameNode, displayGraph } = require('../media/graph-model.js');

const fake = code => ['-e', code, '--'];
test('CLI availability executes the configured shell-free command without a project read', async () => {
  await probeCli(process.execPath, fake("if(process.argv.slice(-2).join(' ')!=='api --probe')process.exit(2);console.log(JSON.stringify({api_version:7,ok:true,diagnostics:[],result:{features:['stdin-body','project-init','nested-local-state']}}))"), process.cwd());
  await assert.rejects(probeCli('specspec-command-that-does-not-exist', [], process.cwd()), CliUnavailableError);
  await assert.rejects(probeCli(process.execPath, fake("console.error('No module named specspec');process.exit(1)"), process.cwd()), CliUnavailableError);
  await assert.rejects(probeCli(process.execPath, fake("console.log('unrelated program')"), process.cwd()), /not a compatible specspec CLI/);
  await assert.rejects(probeCli(process.execPath, fake("console.log(JSON.stringify({api_version:7,ok:true,diagnostics:[],result:{}}))"), process.cwd()), /incompatible/);
  for (const value of [null, [], { api_version: 7, ok: true, diagnostics: [], result: { features: 'stdin-body project-init nested-local-state' } }])
    await assert.rejects(probeCli(process.execPath, fake(`console.log(${JSON.stringify(JSON.stringify(value))})`), process.cwd()), /incompatible/);
  await assert.rejects(probeCli(process.execPath, fake("console.error('No such option --probe');process.exit(2)"), process.cwd()), /older than this UI/);
  await assert.rejects(probeCli(process.execPath, fake("console.error('Broken configuration');process.exit(2)"), process.cwd()), /Broken configuration/);
});
test('availability checks retain bounded output and deadlines', async () => {
  await assert.rejects(probeCli(process.execPath, fake("console.log('x'.repeat(70000))"), process.cwd()), /limit/);
  await assert.rejects(probeCli(process.execPath, fake("setTimeout(()=>{},60000)"), process.cwd(), 30), /did not respond/);
});

test('only absent or empty/local-only safe directories offer initialization', async t => {
  const root = await mkdtemp(join(tmpdir(), 'specspec-startup-'));
  t.after(() => rm(root, { recursive: true, force: true }));
  assert.deepEqual(await inspectProject(root), { kind: 'initialize', root });
  await mkdir(join(root, '.specspec'));
  assert.equal((await inspectProject(root)).kind, 'initialize');
  await mkdir(join(root, '.specspec/local'));
  await writeFile(join(root, '.specspec/local/diagnostics.txt'), 'Retained experiment');
  assert.equal((await inspectProject(root)).kind, 'initialize');
  await writeFile(join(root, '.specspec/local/journal.json'), '{}');
  await assert.rejects(inspectProject(root), /recover/);
  await rm(join(root, '.specspec/local/journal.json'));
  await writeFile(join(root, '.specspec/broken.md'), 'Not a parseable graph');
  assert.equal((await inspectProject(root)).kind, 'graph', 'Broken existing documents must not be treated as no graph.');
});
test('a file or symlink at the specification boundary is a repair case, not initialization', async t => {
  const root = await mkdtemp(join(tmpdir(), 'specspec-startup-path-'));
  t.after(() => rm(root, { recursive: true, force: true }));
  await writeFile(join(root, '.specspec'), 'Owner bytes');
  assert.equal((await inspectProject(root)).kind, 'graph');
  await rm(join(root, '.specspec'));
  await mkdir(join(root, 'outside'));
  await symlink(join(root, 'outside'), join(root, '.specspec'), process.platform === 'win32' ? 'junction' : 'dir');
  assert.equal((await inspectProject(root)).kind, 'graph');
});

function fixture(t, options = {}) {
  const calls = [], messages = [];
  const n = { id: 'AAAAAAA=', type: 'manifesto', parents: [], sources: [], path: '.specspec/AAAAAAA=.md', body: 'Test\n' };
  const snapshot = { format_version: 7, valid: true, nodes: [n], edges: [] };
  let missing = options.missing, initialized = options.initialized, authorized = true, failure = options.failure;
  const session = new GraphSession({
    timeout: 100, authorized: () => authorized, renderMatches, sameNode,
    startup: async () => {
      if (missing) throw new CliUnavailableError('No executable');
      if (failure) throw new Error(failure);
      return { root: 'selected-project', kind: initialized ? 'graph' : 'initialize' };
    },
    cli: async (args, input) => {
      calls.push({ args, input });
      if (args[0] === 'init') {
        if (options.initFailure) throw new Error(options.initFailure);
        initialized = true;
        return { result: { changed_ids: [n.id] } };
      }
      const value = JSON.parse(input);
      if (value.op === 'annotations') return { result: { shots: [] } };
      return { result: { snapshot, ...(value.base ? { diff: { base: snapshot, target: snapshot, changes: [], added_edges: [], removed_edges: [], base_ref: 'HEAD', target_ref: 'workspace', source_changes: [], source_affected: [] } } : {}) } };
    },
    post: async value => {
      messages.push(value);
      if (value.type === 'snapshot') session.receive({ type: 'rendered', renderToken: value.renderToken, view: 'overview', visibleIds: [...displayGraph(value).nodes.keys()], nodeCount: displayGraph(value).nodes.size });
    },
  });
  t.after(() => session.dispose()); session.receive({ type: 'ready' });
  return { session, calls, messages, install: () => { missing = false; }, repair: () => { failure = undefined; }, revoke: () => { authorized = false; } };
}
test('missing CLI blocks reads/writes and retry can advance to the initialization screen', async t => {
  const f = fixture(t, { missing: true });
  assert.equal(await f.session.open(), undefined);
  assert.equal(f.messages.at(-1).stage, 'install'); assert.equal(f.calls.length, 0);
  await assert.rejects(f.session.handle({ type: 'add', body: 'Forged write' }), /startup check/);
  assert.equal(f.calls.length, 0);
  f.install(); await f.session.handle({ type: 'retry-startup' });
  assert.equal(f.messages.at(-1).stage, 'initialize'); assert.equal(f.calls.length, 0);
});
test('explicit initialization sends one stdin body with no body flag, then loads current context', async t => {
  const f = fixture(t); await f.session.open();
  assert.equal(f.messages.at(-1).stage, 'initialize');
  await f.session.handle({ type: 'initialize', body: 'Test', root: 'forged', command: 'forged' });
  assert.deepEqual(f.calls[0], { args: ['init', '--json'], input: 'Test' });
  assert.equal(f.calls.filter(c => c.args[0] === 'init').length, 1);
  assert.equal(f.session.snapshot.nodes[0].body, 'Test\n');
  await assert.rejects(f.session.handle({ type: 'initialize', body: 'Again' }), /uninitialized project/);
});
test('trust, input, native ownership and arbitrary startup failures cannot initialize', async t => {
  const f = fixture(t); await f.session.open();
  await assert.rejects(f.session.handle({ type: 'initialize', body: '' }), /nonempty/);
  f.session.host.document = {}; await assert.rejects(f.session.handle({ type: 'initialize', body: 'Test' }), /uninitialized/);
  delete f.session.host.document; f.revoke();
  await f.session.handle({ type: 'initialize', body: 'Test' });
  assert.equal(f.calls.length, 0); assert.equal(f.messages.at(-1).stage, 'error');
  const failed = fixture(t, { failure: 'Permission denied' }); await failed.session.open();
  assert.equal(failed.messages.at(-1).stage, 'error');
  assert.equal(failed.messages.some(m => m.stage === 'initialize'), false);
  assert.equal(failed.calls.length, 0);
});
test('unknown initialization outcomes require review/retry rather than automatic replay', async t => {
  const f = fixture(t, { initFailure: 'Action result needs verification; recover before retrying.' });
  await f.session.open(); await f.session.handle({ type: 'initialize', body: 'Test' });
  assert.equal(f.calls.length, 1); assert.equal(f.messages.at(-1).stage, 'error');
  assert.match(f.messages.at(-1).message, /verification/);
});
