const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { JSDOM } = require('jsdom');

function fixture(t) {
  const dom = new JSDOM('<div id="body"></div>', { runScripts: 'outside-only', pretendToBeVisual: true });
  dom.window.Range.prototype.getClientRects = () => [];
  dom.window.Range.prototype.getBoundingClientRect = () => ({ left: 0, right: 0, top: 0, bottom: 0 });
  dom.window.eval(readFileSync(join(__dirname, '../media/vendor/graph-vendor.js'), 'utf8'));
  const body = dom.window.document.getElementById('body');
  const editor = dom.window.SpecSpecVendor.createBindingEditor(body, 'local-nonce');
  let inputs = 0;
  body.addEventListener('input', () => inputs++);
  t.after(() => { editor.destroy(); dom.window.close(); });
  const key = value => editor.view.contentDOM.dispatchEvent(new dom.window.KeyboardEvent('keydown', { key: value, ctrlKey: true, bubbles: true, cancelable: true }));
  return { dom, body, editor, inputs: () => inputs, key };
}

test('one editable target contains literal, non-persisted red deletions and green additions', t => {
  const f = fixture(t), { body, editor } = f;
  body.value = '# Current\n\nNew literal <script>text</script>.\n';
  editor.configure({ key: 'node', original: '# Earlier\n\nOld literal <img src=x onerror=alert(1)>.\n' });
  assert.match(body.querySelector('.cm-deletedChunk').textContent, /Earlier/);
  assert.ok(body.querySelector('.cm-changedLine'));
  assert.ok(body.querySelector('.cm-changedText'));
  assert.ok(!body.querySelector('img,script'));
  assert.equal(editor.view.contentDOM.getAttribute('aria-label'), 'Binding Markdown');
  assert.equal(body.value, '# Current\n\nNew literal <script>text</script>.\n');
  assert.equal(f.inputs(), 0, 'Loading text and the comparison is not an edit.');
  editor.view.dispatch({ changes: { from: 2, to: 9, insert: 'Typed' } });
  assert.equal(f.inputs(), 1);
  assert.match(body.value, /Typed/);
  assert.doesNotMatch(body.value, /Earlier|Old literal/);
  assert.ok([...f.dom.window.document.querySelectorAll('style')].some(s => s.nonce === 'local-nonce'));
});

test('comparison refresh preserves target, selection, focus, local history and input count', t => {
  const f = fixture(t), { body, editor } = f;
  body.value = '# Same\n'; editor.configure({ key: 'node', original: body.value });
  assert.ok(!body.querySelector('.cm-deletedChunk,.cm-changedLine'));
  editor.view.dispatch({ changes: { from: body.value.length, insert: 'Draft' } });
  body.focus(); body.setSelectionRange(2, 4, 'backward');
  const content = editor.view.contentDOM;
  editor.configure({ key: 'node', original: '# Refreshed HEAD\n' });
  assert.equal(body.value, '# Same\nDraft');
  assert.deepEqual([body.selectionStart, body.selectionEnd, body.selectionDirection], [2, 4, 'backward']);
  assert.equal(editor.view.contentDOM, content);
  assert.ok(body.contains(f.dom.window.document.activeElement));
  assert.equal(f.inputs(), 1);
  f.key('z'); assert.equal(body.value, '# Same\n', 'Managed hosts keep editor undo.');
  f.key('y'); assert.equal(body.value, '# Same\nDraft');
});

test('added, deleted, provisional and new-node forms use the appropriate comparison', t => {
  const { body, editor } = fixture(t);
  body.value = '# Added\n'; editor.configure({ key: 'added', original: '' });
  assert.ok(body.querySelector('.cm-changedLine')); assert.ok(!body.querySelector('.cm-deletedLine'), 'Added nodes have no deleted text.');
  editor.configure({ key: 'ghost', original: undefined }); body.value = '# Removed node, copyable\n';
  body.readOnly = true;
  assert.equal(editor.view.state.readOnly, true);
  assert.ok(!body.querySelector('.cm-changedLine,.cm-deletedChunk'));
  body.focus(); body.setSelectionRange(0, 5); assert.equal(body.selectionEnd, 5);
  body.disabled = true; assert.equal(editor.view.contentDOM.getAttribute('contenteditable'), 'false');
  body.readOnly = false; body.disabled = false;
  assert.equal(editor.view.state.readOnly, false);
  for (const key of ['provisional', '__new__']) {
    editor.configure({ key, original: undefined });
    assert.ok(!body.querySelector('.cm-changedLine,.cm-deletedChunk'));
  }
});

test('native documents route undo to the host and changing nodes resets managed undo', t => {
  const f = fixture(t), { body, editor } = f;
  editor.configure({ key: 'native', original: '# Before', native: true });
  body.value = '# Target'; editor.view.dispatch({ changes: { from: 8, insert: '!' } });
  f.key('z'); assert.equal(body.value, '# Target!', 'No second editor undo stack for native documents.');
  editor.configure({ key: 'managed', native: false });
  body.value = '# Managed'; editor.view.dispatch({ changes: { from: 9, insert: '!' } });
  body.value = '# Other node'; editor.configure({ key: 'other' });
  f.key('z'); assert.equal(body.value, '# Other node');
});
