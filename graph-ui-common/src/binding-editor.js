// Shared editable inline diff. The control keeps the form's small textarea-like
// value/selection contract; persistence and native-document undo stay in the host.
import { Annotation, Compartment, EditorState, Transaction } from '@codemirror/state';
import { EditorView, keymap, lineNumbers } from '@codemirror/view';
import { defaultKeymap, history, historyKeymap } from '@codemirror/commands';
import { unifiedMergeView } from '@codemirror/merge';

const external = Annotation.define();

export function createBindingEditor(element, nonce) {
  const comparison = new Compartment(), permissions = new Compartment(), undo = new Compartment();
  let baseline, readOnly = false, disabled = false, nativeUndo = false, resource;
  const permissionExtensions = () => [EditorState.readOnly.of(readOnly || disabled), EditorView.editable.of(!disabled)];
  const undoExtensions = () => nativeUndo ? [] : [history(), keymap.of(historyKeymap)];
  const extensions = () => [
    EditorView.cspNonce.of(nonce), EditorView.lineWrapping, lineNumbers(),
    EditorView.contentAttributes.of({ 'aria-label': 'Binding Markdown', 'aria-multiline': 'true', spellcheck: 'false' }),
    permissions.of(permissionExtensions()), undo.of(undoExtensions()), comparison.of(mergeExtensions()),
    keymap.of(defaultKeymap),
    EditorView.updateListener.of(update => {
      if (update.docChanged && !update.transactions.every(tr => tr.annotation(external))) {
        element.dispatchEvent(new Event('input', { bubbles: true }));
      }
    }),
  ];
  function mergeExtensions() {
    return baseline === undefined ? [] : unifiedMergeView({ original: baseline, mergeControls: false,
      highlightChanges: true, gutter: true, syntaxHighlightDeletions: false });
  }
  const view = new EditorView({ parent: element, state: EditorState.create({ extensions: extensions() }) });
  function setValue(text) {
    text = String(text).replace(/\r\n?/g, '\n');
    const current = view.state.doc.toString();
    if (text === current) return;
    let from = 0, to = current.length, end = text.length;
    while (from < to && from < end && current[from] === text[from]) from++;
    // Keep surrogate pairs intact.
    if (from && /[\uD800-\uDBFF]/.test(current[from - 1])) from--;
    while (to > from && end > from && current[to - 1] === text[end - 1]) { to--; end--; }
    if (to < current.length && /[\uDC00-\uDFFF]/.test(current[to])) { to++; end++; }
    view.dispatch({ changes: { from, to, insert: text.slice(from, end) },
      annotations: [external.of(true), Transaction.addToHistory.of(false)] });
  }
  // These properties represent the editable target only, never deletion widgets.
  Object.defineProperties(element, {
    value: { get: () => view.state.doc.toString(), set: setValue },
    readOnly: { get: () => readOnly, set: value => {
      if (readOnly === Boolean(value)) return;
      readOnly = Boolean(value); view.dispatch({ effects: permissions.reconfigure(permissionExtensions()) });
    } },
    disabled: { get: () => disabled, set: value => {
      if (disabled === Boolean(value)) return;
      disabled = Boolean(value); view.dispatch({ effects: permissions.reconfigure(permissionExtensions()) });
    } },
    selectionStart: { get: () => view.state.selection.main.from },
    selectionEnd: { get: () => view.state.selection.main.to },
    selectionDirection: { get: () => view.state.selection.main.anchor > view.state.selection.main.head ? 'backward' : 'forward' },
  });
  element.focus = () => view.focus();
  element.setSelectionRange = (from, to, direction) => view.dispatch({ selection: direction === 'backward'
    ? { anchor: to, head: from } : { anchor: from, head: to } });
  return {
    view,
    configure({ key, original, native }) {
      if (nativeUndo !== Boolean(native)) {
        nativeUndo = Boolean(native); view.dispatch({ effects: undo.reconfigure(undoExtensions()) });
      }
      if (resource !== key) {
        resource = key; baseline = original;
        view.setState(EditorState.create({ doc: element.value, extensions: extensions() }));
      } else if (baseline !== original) {
        baseline = original; view.dispatch({ effects: comparison.reconfigure(mergeExtensions()) });
      }
    },
    destroy: () => view.destroy(),
  };
}
