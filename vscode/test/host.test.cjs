const { test } = require('node:test');
const assert = require('node:assert/strict');
const { JSDOM } = require('jsdom');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const script = readFileSync(join(__dirname, '../src/host.js'), 'utf8');
function open(t, scope, get, set) {
  const dom = new JSDOM('<meta name="specspec-project">', { runScripts: 'outside-only' });
  dom.window.document.querySelector('meta').content = scope;
  dom.window.acquireVsCodeApi = () => ({ getState: get, setState: set, postMessage() {} });
  dom.window.eval(script); t.after(() => dom.window.close()); return dom.window.specspecHost;
}
test('the VS Code port preserves dirty drafts across project switches without sharing them', t => {
  let saved;
  const a = open(t, '/a', () => saved, value => { saved = value; });
  a.setState({ dirty: true, originalNode: { id: 'a', body: '# Original A' }, draft: { body: '# A' } });
  const b = open(t, '/b', () => saved, value => { saved = value; }); assert.equal(b.getState(), undefined);
  b.setState({ dirty: true, originalNode: { id: 'b', body: '# Original B' }, draft: { body: '# B' } });
  const again = open(t, '/a', () => saved, value => { saved = value; });
  assert.equal(again.getState().originalNode.body, '# Original A'); assert.equal(again.getState().draft.body, '# A');
  assert.equal(saved.projects['/b'].originalNode.body, '# Original B');
});
test('current project-scoped drafts restore their full node record', t => {
  let saved = { projects: { '/a': { dirty: true, originalNode: { id: 'Zm9vYmE=', body: '# Original' }, draft: { body: '# Unfinished' } } } };
  const a = open(t, '/a', () => saved, value => { saved = value; });
  assert.equal(a.getState().originalNode.id, 'Zm9vYmE=');
  a.setState(a.getState()); assert.equal(saved.projects['/a'].draft.body, '# Unfinished');
});
