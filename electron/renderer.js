/* Electron services only. The canvas itself is unchanged shared code. */
(() => {
  const native = window.specspecNative;
  window.specspecHost = Object.freeze({ getState: native.getState, setState: native.setState,
    postMessage: native.postMessage, onMessage: native.onMessage });
  const dialog = document.createElement('dialog'); dialog.setAttribute('aria-label', 'Compare revisions');
  const form = document.createElement('form'); form.method = 'dialog';
  form.addEventListener('submit', event => { event.preventDefault(); dialog.close('apply'); });
  const heading = document.createElement('h2'); heading.textContent = 'Compare revisions'; form.append(heading);
  const fields = ['Base commit/ref', 'Target commit/ref (empty = workspace)'].map(text => {
    const label = document.createElement('label'), input = document.createElement('input');
    label.textContent = text; input.maxLength = 1024; label.append(input); form.append(label); return input;
  });
  const actions = document.createElement('div'); actions.className = 'actions';
  for (const [value, text] of [['cancel', 'Cancel'], ['apply', 'Compare']]) {
    const button = document.createElement('button'); button.value = value; button.textContent = text;
    button.type = value === 'apply' ? 'submit' : 'button';
    if (value === 'cancel') button.addEventListener('click', () => dialog.close('cancel'));
    actions.append(button);
  }
  form.append(actions); dialog.append(form); document.body.append(dialog);
  let request;
  dialog.addEventListener('close', () => {
    if (request) native.revisionResult({ id: request, result: dialog.returnValue === 'apply' ? fields.map(f => f.value) : null });
    request = undefined;
  });
  native.onMessage(message => {
    if (message.type === 'revision-prompt') {
      if (dialog.open) dialog.close('cancel');
      request = message.id; fields[0].value = message.base; fields[1].value = message.target;
      dialog.returnValue = 'cancel'; dialog.showModal(); fields[0].focus();
    } else if (message.type === 'revision-dismiss' && dialog.open) dialog.close('cancel');
  });
})();
