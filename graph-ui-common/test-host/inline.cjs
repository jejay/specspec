/* Exercise the real shared contenteditable control in both installed hosts. */
const assert = require('node:assert/strict');

exports.checkInline = async ({ evaluate, screenshot, delay }) => {
  const original = await evaluate(`(() => {
    const card=document.querySelector('#cards .card.changed:not(.manifesto)');
    if(!card) throw new Error('Inline diff fixture needs a modified node.');
    card.click();
    const body=document.getElementById('body');body.focus();body.setSelectionRange(body.value.length,body.value.length);
    return {id:card.dataset.nodeId,value:body.value};
  })()`);
  assert.ok(await evaluate(`Boolean(!document.getElementById('before-section')&&document.querySelector('#body .cm-deletedLine')&&document.querySelector('#body .cm-changedLine'))`));
  assert.ok(await evaluate(`document.execCommand('insertText',false,'Inline typing <script>literal</script>.')`));
  await delay(150);
  assert.equal(await evaluate(`document.getElementById('body').value`), original.value + 'Inline typing <script>literal</script>.');
  assert.ok(await evaluate(`window.specspecHost.getState().dirty&&!document.querySelector('#body script')`));
  const painted = await evaluate(`(() => {
    const root=document.documentElement;root.style.setProperty('--vscode-diffEditor-insertedTextBackground','rgb(10, 70, 20)');root.style.setProperty('--vscode-diffEditor-removedTextBackground','rgb(80, 10, 20)');
    const result=[getComputedStyle(document.querySelector('#body .cm-changedText')).backgroundColor,getComputedStyle(document.querySelector('#body .cm-deletedText')).backgroundColor];
    root.style.removeProperty('--vscode-diffEditor-insertedTextBackground');root.style.removeProperty('--vscode-diffEditor-removedTextBackground');return result;
  })()`);
  assert.deepEqual(painted, ['rgb(10, 70, 20)', 'rgb(80, 10, 20)']);
  await evaluate(`document.getElementById('body').setSelectionRange(2,6,'backward');document.getElementById('refresh').click()`);
  await delay(500);
  assert.deepEqual(await evaluate(`[document.getElementById('body').selectionStart,document.getElementById('body').selectionEnd,document.getElementById('body').selectionDirection]`), [2, 6, 'backward']);
  assert.ok(await evaluate(`document.getElementById('body').contains(document.activeElement)`));
  await evaluate(`document.getElementById('frame-node').click()`);await delay(100);
  await screenshot('editable-inline-diff');
  await evaluate(`document.getElementById('discard').click();document.getElementById('back').click()`);
  assert.equal(await evaluate(`document.getElementById('body').value`), original.value);
  console.log('Inline diff: actual typing, literal target-only draft, themed character/line changes and refresh/caret preservation passed.');
};
