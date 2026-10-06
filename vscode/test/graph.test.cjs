const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { JSDOM } = require('jsdom');
const { graphHtml } = require('../out/view.js');
const model = require('../media/graph-model.js');

const root = { id: 'root', type: 'manifesto', retired: false, parents: [], body: '# Purpose\n', path: '_specspec/root.md', sources: [] };
const child = { id: 'child', type: 'requirement', retired: false, parents: ['root'], body: '# Child\n', path: '_specspec/child.md', sources: [] };

function fixture(t, options = {}) {
  const dom = new JSDOM(graphHtml(name => name, 'local', 'test'), { runScripts: 'outside-only', pretendToBeVisual: true });
  const messages = [];
  const viewport = dom.window.document.getElementById('viewport');
  let viewportWidth = options.width || 1000;
  Object.defineProperty(viewport, 'clientWidth', { get: () => viewportWidth });
  Object.defineProperty(viewport, 'clientHeight', { value: 650 });
  let saved = options.restored;
  dom.window.acquireVsCodeApi = () => ({ postMessage: message => messages.push(message), getState: () => saved, setState: value => { saved = value; } });
  dom.window.confirm = () => true;
  dom.window.structuredClone = structuredClone; // Browser API not supplied by jsdom.
  for (const name of ['vendor/graph-vendor.js', 'graph-model.js', 'graph-camera.js', 'graph.js']) {
    dom.window.eval(readFileSync(join(__dirname, '../media', name), 'utf8'));
  }
  t.after(() => {
    dom.window.close();
    assert.deepEqual(messages.filter(message => message.type === 'client-error'), [], 'Renderer errors must not be mistaken for successful DOM tests.');
  });
  const snapshot = { fingerprint: 'version-1', format_version: 2, valid: true, nodes: [root, child], edges: [['root', 'child']] };
  const send = message => dom.window.dispatchEvent(new dom.window.MessageEvent('message', { data: message }));
  const $ = id => dom.window.document.getElementById(id);
  send({ type: 'snapshot', snapshot, diagnostics: [], readonly: false });
  return { dom, messages, snapshot, send, $, saved: () => saved, resize: width => {
    viewportWidth = width; dom.window.dispatchEvent(new dom.window.Event('resize'));
  } };
}

function hoverFixture(t) {
  const f = fixture(t);
  const grand = { ...child, id: 'grand', parents: ['child'], body: '# Grand\n' };
  const sibling = { ...child, id: 'sibling', body: '# Sibling\n' };
  f.snapshot = { ...f.snapshot, nodes: [root, child, grand, sibling], edges: [['root', 'child'], ['child', 'grand'], ['root', 'sibling']] };
  f.send({ type: 'snapshot', snapshot: f.snapshot, diagnostics: [], readonly: false });
  f.card = id => f.dom.window.document.querySelector(`[data-node-id="${id}"]`);
  return f;
}

function hoverEvent(dom, target, type = 'pointerover', relatedTarget = null, pointerType = 'mouse') {
  const event = new dom.window.MouseEvent(type, { bubbles: true, cancelable: true, relatedTarget, clientX: 120, clientY: 180 });
  Object.defineProperty(event, 'pointerType', { value: pointerType });
  target.dispatchEvent(event);
  return event;
}

function highlightedEdges($) {
  return [...$('edges').querySelectorAll('.link.incident-highlight')].map(p => `${p.dataset.parent}>${p.dataset.child}`).sort();
}

function assertPairedHighlights($) {
  const paths = [...$('edges').querySelectorAll('.link')], heads = [...$('edges').querySelectorAll('.arrow-head')];
  for (const path of paths) {
    const head = heads.find(h => h.dataset.parent === path.dataset.parent && h.dataset.child === path.dataset.child);
    assert.equal(head.classList.contains('incident-highlight'), path.classList.contains('incident-highlight'));
  }
}

test('hover emphasizes only direct incoming/outgoing curves and heads without mutation or geometry changes', t => {
  const { dom, $, card, messages, saved } = hoverFixture(t);
  const original = [...$('edges').children], geometry = original.map(p => [p.getAttribute('d'), p.style.strokeWidth, p.style.strokeDasharray]);
  const positions = [...$('cards').children].map(c => [c.style.left, c.style.top]);
  const preferences = saved(), count = messages.length, transform = $('graph').style.transform;
  hoverEvent(dom, card('child').querySelector('strong'));
  assert.deepEqual(highlightedEdges($), ['child>grand', 'root>child']);
  assertPairedHighlights($);
  assert.ok([...$('edges').children].slice(-4).every(p => p.classList.contains('incident-highlight')), 'Both incident pairs are raised above other curves.');
  assert.ok(original.every(p => p.isConnected));
  assert.deepEqual(original.map(p => [p.getAttribute('d'), p.style.strokeWidth, p.style.strokeDasharray]), geometry);
  assert.deepEqual([...$('cards').children].map(c => [c.style.left, c.style.top]), positions);
  assert.equal($('graph').style.transform, transform);
  assert.equal(saved(), preferences);
  assert.equal(messages.length, count);
  hoverEvent(dom, card('child'), 'pointerout', $('viewport'));
  assert.deepEqual(highlightedEdges($), []);
  assert.deepEqual([...$('edges').children], original, 'Leaving restores original SVG ordering and identity.');
});

test('hovering inside an expanded form does not flicker or disturb native drafts and caret', t => {
  const { dom, $, card, saved, messages } = hoverFixture(t);
  card('child').click();
  const body = $('body'); body.value = '# Unsaved'; body.dispatchEvent(new dom.window.Event('input'));
  body.focus(); body.setSelectionRange(2, 5, 'backward');
  const draft = saved(), count = messages.length;
  hoverEvent(dom, card('child'));
  hoverEvent(dom, card('child'), 'pointerout', body);
  hoverEvent(dom, body);
  hoverEvent(dom, body, 'pointerout', $('save'));
  assert.deepEqual(highlightedEdges($), ['child>grand', 'root>child']);
  assertPairedHighlights($);
  assert.equal(saved(), draft);
  assert.equal(saved().formFingerprint, 'version-1');
  assert.equal(messages.length, count);
  assert.equal(dom.window.document.activeElement, body);
  assert.deepEqual([body.selectionStart, body.selectionEnd, body.selectionDirection], [2, 5, 'backward']);
  assert.equal(hoverEvent(dom, body, 'pointermove').defaultPrevented, false);
});

test('moving between cards replaces emphasis and exit/blur/cancel/touch clear transient hover', t => {
  const { dom, $, card } = hoverFixture(t);
  hoverEvent(dom, card('child'));
  hoverEvent(dom, card('child'), 'pointerout', card('grand'));
  assert.deepEqual(highlightedEdges($), ['child>grand']);
  hoverEvent(dom, card('grand'));
  hoverEvent(dom, card('grand'), 'pointerout', null);
  assert.deepEqual(highlightedEdges($), []);
  for (const event of ['pointerleave', 'pointercancel']) {
    hoverEvent(dom, card('child'));
    $('viewport').dispatchEvent(new dom.window.Event(event));
    assert.deepEqual(highlightedEdges($), []);
  }
  hoverEvent(dom, card('child'));
  dom.window.dispatchEvent(new dom.window.Event('blur'));
  assert.deepEqual(highlightedEdges($), []);
  hoverEvent(dom, card('child'));
  hoverEvent(dom, card('child'), 'pointerover', null, 'touch');
  assert.deepEqual(highlightedEdges($), []);
});

test('read-only historical and added/removed links keep their Git classes/dashes while highlighted', t => {
  const { dom, $, card, snapshot, send, messages } = hoverFixture(t);
  const target = { ...snapshot, nodes: [root, { ...child, parents: ['root', 'sibling'] }, snapshot.nodes[3]], edges: [['root', 'child'], ['root', 'sibling'], ['sibling', 'child']] };
  send({ type: 'snapshot', snapshot: target, diagnostics: [], readonly: true, diff: {
    base: snapshot, target, changes: [{ id: 'grand', kind: 'removed' }], added_edges: [['sibling', 'child']], removed_edges: [['child', 'grand']], base_ref: 'old', target_ref: 'new',
  } });
  const count = messages.length, removed = $('edges').querySelector('.link.removed');
  const dash = removed.style.strokeDasharray, width = removed.style.strokeWidth;
  hoverEvent(dom, card('child'));
  assert.deepEqual(highlightedEdges($), ['child>grand', 'root>child', 'sibling>child']);
  assertPairedHighlights($);
  assert.ok($('edges').querySelector('.link.added.incident-highlight'));
  assert.ok($('edges').querySelector('.arrow-head.removed.incident-highlight'));
  assert.equal(removed.style.strokeDasharray, dash);
  assert.equal(removed.style.strokeWidth, width);
  assert.equal(messages.length, count);
  hoverEvent(dom, card('grand'));
  assert.deepEqual(highlightedEdges($), ['child>grand']);
});

test('unsaved draft cards highlight their draft links and an isolated draft highlights nothing', t => {
  const { dom, $, card, messages } = hoverFixture(t);
  $('new').click();
  assert.equal($('edges').children.length, 0);
  hoverEvent(dom, card('__draft__'));
  assert.deepEqual(highlightedEdges($), []);
  $('parent-candidate').value = 'root'; $('parent-candidate').dispatchEvent(new dom.window.Event('change')); $('add-parent').click();
  const paths = [...$('edges').children], count = messages.length;
  hoverEvent(dom, $('body'));
  assert.deepEqual(highlightedEdges($), ['root>__draft__']);
  assertPairedHighlights($);
  assert.ok(paths.every(p => p.classList.contains('draft')));
  hoverEvent(dom, card('root'));
  assert.ok(paths.every(p => p.isConnected));
  assert.equal(messages.length, count);
});

test('refresh reconciles hovered identity and camera movement rechecks the stationary pointer', t => {
  const { dom, $, card, snapshot, send } = hoverFixture(t);
  let hit = 'child';
  dom.window.document.elementFromPoint = (x, y) => { assert.deepEqual([x, y], [120, 180]); return hit ? card(hit) : $('viewport'); };
  hoverEvent(dom, card('child'));
  const target = { ...snapshot, fingerprint: 'new', nodes: snapshot.nodes.map(n => n.id === 'child' ? { ...n, parents: ['root', 'sibling'] } : n), edges: [...snapshot.edges, ['sibling', 'child']] };
  send({ type: 'snapshot', snapshot: target, diagnostics: [], readonly: false });
  assert.deepEqual(highlightedEdges($), ['child>grand', 'root>child', 'sibling>child']);
  hit = 'sibling';
  $('viewport').dispatchEvent(new dom.window.WheelEvent('wheel', { bubbles: true, cancelable: true, deltaY: -100, clientX: 300, clientY: 200 }));
  assert.deepEqual(highlightedEdges($), ['root>sibling', 'sibling>child']);
  hit = undefined;
  send({ type: 'snapshot', snapshot: target, diagnostics: [], readonly: false });
  assert.deepEqual(highlightedEdges($), []);
});

test('navigation and disappearing cards cannot retain a stale incident highlight', t => {
  const { dom, $, card, snapshot, send } = hoverFixture(t);
  hoverEvent(dom, card('sibling'));
  card('child').click();
  assert.deepEqual(highlightedEdges($), []);
  $('back').click();
  assert.deepEqual(highlightedEdges($), []);
  hoverEvent(dom, card('grand'));
  send({ type: 'snapshot', snapshot: { ...snapshot, nodes: [root, child], edges: [['root', 'child']] }, diagnostics: [], readonly: false });
  assert.deepEqual(highlightedEdges($), []);
});

test('nodes are editable without approval states or an acceptance action', t => {
  const { dom, $, saved } = fixture(t);
  assert.equal($('accept'), null);
  assert.equal($('save').textContent, 'Save node');
  assert.deepEqual([...$('color-mode').options].map(option => option.value), ['distance', 'max-distance', 'type']);
  assert.equal(saved().colorMode, 'distance');
  for (const card of $('cards').children) {
    assert.equal('status' in card.dataset, false);
    assert.doesNotMatch(card.textContent, /proposed|accepted/);
  }
  dom.window.document.querySelector('[data-node-id="child"]').click();
  assert.equal($('body').disabled, false);
  assert.equal($('save').disabled, false);
  assert.equal($('retire').disabled, false);
  assert.doesNotMatch($('identity').textContent, /proposed|accepted/);
});

test('withdrawal and restoration send guarded actions, not acceptance', t => {
  const { dom, snapshot, send, messages, $ } = fixture(t);
  dom.window.document.querySelector('[data-node-id="child"]').click();
  $('retire').click();
  assert.equal(messages.at(-1).type, 'retire');
  assert.equal(messages.at(-1).expect, snapshot.fingerprint);
  assert.equal($('save').disabled, true);
  const target = { ...snapshot, nodes: [root, { ...child, retired: true }] };
  send({ type: 'snapshot', snapshot: target, diagnostics: [], readonly: false, force: true, selectedId: 'child' });
  assert.match($('identity').textContent, /retired/);
  assert.equal($('retire').hidden, true);
  assert.equal($('restore').hidden, false);
  $('restore').click();
  assert.equal(messages.at(-1).type, 'restore');
  assert.equal(messages.at(-1).expect, snapshot.fingerprint);
});

test('a legacy workspace is readable but only explicit migration can write', t => {
  const { dom, snapshot, send, messages, $ } = fixture(t);
  send({ type: 'snapshot', snapshot: { ...snapshot, format_version: 1 }, diagnostics: [], readonly: false });
  assert.equal($('new').disabled, true);
  assert.equal($('migrate').hidden, false);
  assert.match($('schema-notice').textContent, /Legacy v1/);
  dom.window.document.querySelector('[data-node-id="child"]').click();
  assert.equal($('body').value, child.body);
  assert.equal($('body').disabled, true);
  assert.equal($('save').disabled, true);
  assert.equal($('retire').disabled, true);
  $('migrate').click();
  assert.equal(messages.at(-1).type, 'migrate');
  assert.equal(messages.at(-1).expect, snapshot.fingerprint);
  send({ type: 'snapshot', snapshot: { ...snapshot, fingerprint: 'migrated' }, diagnostics: [], readonly: false });
  assert.equal($('migrate').hidden, true);
  assert.equal($('body').disabled, false);
  assert.equal($('body').value, child.body);
});

test('legacy histories cannot migrate and dirty drafts retain their original fingerprint', t => {
  const { dom, snapshot, send, $, saved } = fixture(t);
  dom.window.document.querySelector('[data-node-id="child"]').click();
  $('body').value = '# Still my draft\n'; $('body').dispatchEvent(new dom.window.Event('input'));
  send({ type: 'snapshot', snapshot: { ...snapshot, format_version: 1 }, diagnostics: [], readonly: false });
  assert.equal($('migrate').disabled, true);
  assert.equal($('body').value, '# Still my draft\n');
  assert.equal(saved().formFingerprint, 'version-1');
  send({ type: 'snapshot', snapshot: { ...snapshot, format_version: 1 }, diagnostics: [], readonly: true });
  assert.equal($('migrate').hidden, true);
  assert.equal($('save').disabled, true);
  send({ type: 'snapshot', snapshot: { ...snapshot, fingerprint: 'migrated' }, diagnostics: [], readonly: false });
  assert.equal($('body').value, '# Still my draft\n');
  assert.equal(saved().formFingerprint, 'version-1');
});

test('restored obsolete status colors fall back to distance without losing a draft or camera', t => {
  const { $, saved } = fixture(t, { restored: {
    colorMode: 'status', selected: 'child', view: 'focus', dirty: true,
    formFingerprint: 'original', creating: false,
    cameras: { 'focus:child': { x: 30, y: -50, k: 0.8 } },
    draft: { body: '# My draft\n', sources: '[]', slug: '', nodeType: 'requirement', parents: ['root'] },
  } });
  assert.equal(saved().colorMode, 'distance');
  assert.equal($('body').value, '# My draft\n');
  assert.equal(saved().formFingerprint, 'original');
  assert.deepEqual({ ...saved().cameras['focus:child'] }, { x: 30, y: -50, k: 0.8 });
});

test('graph renders and new-node creation goes through a typed message', t => {
  const { dom, messages, $ } = fixture(t);
  assert.equal(dom.window.document.querySelectorAll('.card').length, 2);
  assert.equal($('new').disabled, false);
  $('new').click();
  $('slug').value = 'new-conclusion'; $('body').value = '# New\n';
  $('parent-candidate').value = 'root';
  $('parent-candidate').dispatchEvent(new dom.window.Event('change'));
  $('add-parent').click();
  $('editor').dispatchEvent(new dom.window.Event('submit', { cancelable: true }));
  const message = messages.at(-1);
  assert.equal(message.type, 'add');
  assert.equal(message.expect, 'version-1');
  assert.equal(message.body, '# New\n');
  assert.deepEqual([...message.parents], ['root']);
  assert.equal($('save').disabled, true);
});

test('manifesto shows no parents or candidate choices while its body remains editable', t => {
  const { dom, messages, $ } = fixture(t);
  dom.window.document.querySelector('.card.manifesto').click();
  assert.equal($('parent-links').children.length, 0);
  assert.match($('parents-summary').textContent, /None.*manifesto is the root/);
  assert.equal($('parent-add-controls').hidden, true);
  assert.equal($('parent-candidate').options.length, 0);
  assert.equal($('parent-candidate').disabled, true);
  assert.equal($('add-parent').disabled, true);
  assert.equal($('body').disabled, false);
  $('editor').dispatchEvent(new dom.window.Event('submit', { cancelable: true }));
  assert.equal(messages.at(-1).id, 'root');
  assert.deepEqual([...messages.at(-1).parents], []);
});

test('parent list displays actual links; adding and removing are explicit draft changes', t => {
  const { dom, messages, snapshot, send, $, saved } = fixture(t);
  const branch = { ...child, id: 'branch', body: '# Branch\n' };
  send({ type: 'snapshot', snapshot: { ...snapshot, nodes: [...snapshot.nodes, branch] }, diagnostics: [], readonly: false });
  dom.window.document.querySelector('.card.requirement').click();
  assert.equal($('parent-links').children.length, 1);
  assert.equal($('parent-links').firstElementChild.dataset.parentId, 'root');
  assert.ok(![...$('parent-candidate').options].some(option => ['root', 'child'].includes(option.value)));
  $('parent-candidate').value = 'branch';
  $('parent-candidate').dispatchEvent(new dom.window.Event('change'));
  assert.equal($('parent-links').children.length, 1, 'Choosing a candidate is not adding a link.');
  $('add-parent').click();
  assert.equal($('parent-links').children.length, 2);
  assert.deepEqual([...saved().draft.parents], ['root', 'branch']);
  assert.equal($('retire').disabled, true);
  assert.ok(![...$('parent-candidate').options].some(option => option.value === 'branch'));
  $('parent-links').querySelector('button').click();
  assert.equal($('parent-links').firstElementChild.dataset.parentId, 'branch');
  $('editor').dispatchEvent(new dom.window.Event('submit', { cancelable: true }));
  assert.deepEqual([...messages.at(-1).parents], ['branch']);
  assert.equal(messages.at(-1).expect, 'version-1');
});

test('switching a new node to implementation removes its manifesto parent from the draft', t => {
  const { dom, messages, $ } = fixture(t);
  dom.window.document.querySelector('.card.manifesto').click();
  $('new').click();
  assert.equal($('parent-links').firstElementChild.dataset.parentId, 'root');
  $('node-type').value = 'implementation';
  $('node-type').dispatchEvent(new dom.window.Event('change'));
  assert.equal($('parent-links').children.length, 0);
  assert.ok(![...$('parent-candidate').options].some(option => option.value === 'root'));
  $('parent-candidate').value = 'child';
  $('parent-candidate').dispatchEvent(new dom.window.Event('change'));
  $('add-parent').click();
  $('editor').dispatchEvent(new dom.window.Event('submit', { cancelable: true }));
  assert.equal(messages.at(-1).nodeType, 'implementation');
  assert.deepEqual([...messages.at(-1).parents], ['child']);
});

test('parent drafts survive refresh and can be discarded without adopting a newer fingerprint', t => {
  const { dom, messages, snapshot, send, $ } = fixture(t);
  dom.window.document.querySelector('.card.requirement').click();
  $('parent-links').querySelector('button').click();
  send({ type: 'snapshot', snapshot: { ...snapshot, fingerprint: 'version-2' }, diagnostics: [], readonly: false });
  assert.equal($('parent-links').children.length, 0);
  $('editor').dispatchEvent(new dom.window.Event('submit', { cancelable: true }));
  assert.deepEqual([...messages.at(-1).parents], []);
  assert.equal(messages.at(-1).expect, 'version-1');
  send({ type: 'error', message: 'Graph is stale' });
  $('discard').click();
  assert.equal($('parent-links').firstElementChild.dataset.parentId, 'root');
});

test('restored parent drafts use their original fingerprint and do not turn candidates into links', t => {
  const { dom, messages, $ } = fixture(t, { restored: {
    selected: 'child', dirty: true, creating: false, formFingerprint: 'old-version',
    draft: { body: '# Unsaved\n', sources: '[]', slug: '', nodeType: 'requirement', parents: [] },
  } });
  assert.equal($('parent-links').children.length, 0);
  assert.ok([...$('parent-candidate').options].some(option => option.value === 'root'));
  $('editor').dispatchEvent(new dom.window.Event('submit', { cancelable: true }));
  assert.equal(messages.at(-1).expect, 'old-version');
  assert.deepEqual([...messages.at(-1).parents], []);
});

test('old invalid manifesto parent drafts cannot restore editable root links', t => {
  const { dom, messages, $ } = fixture(t, { restored: {
    selected: 'root', dirty: true, creating: false, formFingerprint: 'old-version',
    draft: { body: '# Unsaved purpose\n', sources: '[]', slug: '', nodeType: 'requirement', parents: ['child'] },
  } });
  assert.equal($('body').value, '# Unsaved purpose\n');
  assert.equal($('parent-links').children.length, 0);
  assert.equal($('parent-add-controls').hidden, true);
  $('editor').dispatchEvent(new dom.window.Event('submit', { cancelable: true }));
  assert.deepEqual([...messages.at(-1).parents], []);
});

test('external refresh preserves unsaved text and its original fingerprint', t => {
  const { dom, messages, snapshot, send, $ } = fixture(t);
  dom.window.document.querySelector('.card.requirement').click();
  $('body').value = '# Unsaved\n';
  $('body').dispatchEvent(new dom.window.Event('input'));
  assert.equal($('retire').disabled, true);
  send({ type: 'snapshot', snapshot: { ...snapshot, fingerprint: 'version-2' }, diagnostics: [], readonly: false });
  assert.equal($('body').value, '# Unsaved\n');
  $('editor').dispatchEvent(new dom.window.Event('submit', { cancelable: true }));
  assert.equal(messages.at(-1).expect, 'version-1');
  send({ type: 'error', message: 'Graph is stale' });
  assert.equal($('body').value, '# Unsaved\n');
  $('discard').click();
  assert.equal($('body').value, '# Child\n');
});

test('historical and removed nodes are read-only, with old text visible', t => {
  const { dom, snapshot, send, $ } = fixture(t);
  const target = { ...snapshot, nodes: [root], edges: [] };
  send({ type: 'snapshot', snapshot: target, diagnostics: [], readonly: true, diff: {
    base: snapshot, target, changes: [{ id: 'child', kind: 'removed', fields: [] }],
    added_edges: [], removed_edges: [['root', 'child']], base_ref: 'older', target_ref: 'newer',
  } });
  dom.window.document.querySelector('.card.removed').click();
  assert.equal($('body').disabled, true);
  assert.equal($('new').disabled, true);
  assert.equal($('before').textContent, '# Child\n');
  assert.equal($('parent-links').firstElementChild.dataset.parentId, 'root');
  assert.equal($('parent-links').querySelectorAll('button').length, 0);
  assert.equal($('parent-add-controls').hidden, true);
  assert.equal($('add-parent').disabled, true);
  assert.equal(dom.window.document.querySelectorAll('svg .link.removed').length, 1);
});

test('click opens only the neighborhood and places the editor inside the expanded node', t => {
  const { dom, snapshot, send, $, messages } = fixture(t);
  const node = (id, parent) => ({ ...child, id, parents: [parent], body: `# ${id}\n` });
  const nodes = [root, child, node('grand', 'child'), node('great', 'grand'), node('deep', 'great'), node('unrelated', 'root')];
  const target = { ...snapshot, nodes, edges: [['root', 'child'], ['child', 'grand'], ['grand', 'great'], ['great', 'deep'], ['root', 'unrelated']] };
  send({ type: 'snapshot', snapshot: target, diagnostics: [], readonly: false });
  dom.window.document.querySelector('[data-node-id="child"]').click();
  assert.equal($('cards').children.length, 3);
  assert.equal(dom.window.document.querySelector('aside'), null);
  const expanded = dom.window.document.querySelector('.expanded[data-node-id="child"]');
  assert.ok(expanded.contains($('editor')));
  const parent = dom.window.document.querySelector('[data-node-id="root"]');
  assert.equal(parent.querySelector('.distance-badge'), null);
  assert.equal(parent.dataset.minDistance, '0');
  assert.doesNotMatch($('focus-context').textContent, /distance|hops/i);
  const childCard = dom.window.document.querySelector('[data-node-id="grand"]');
  assert.equal(childCard.dataset.downstream, '2');
  assert.match(childCard.textContent, /2 downstream/);
  assert.match(childCard.querySelector('.downstream-badge').title, /every depth/);
  assert.ok(model.renderMatches({ snapshot: target }, messages.at(-1)));
  childCard.click();
  assert.equal(dom.window.document.querySelector('.expanded').dataset.nodeId, 'grand');
  $('back').click();
  assert.equal($('cards').children.length, 6);
  assert.equal($('detail-parking').contains($('editor')), true);
});

test('downstream badge deduplicates shared nodes across all deeper generations', t => {
  const { dom, snapshot, send } = fixture(t);
  const edges = [['root', 'child'], ['child', 'a'], ['child', 'b'], ['a', 'shared'], ['b', 'shared'], ['shared', 'deep']];
  const nodes = [root, ...['child', 'a', 'b', 'shared', 'deep'].map(id => ({ ...child, id, body: `# ${id}\n`, parents: edges.filter(([, target]) => target === id).map(([source]) => source) }))];
  send({ type: 'snapshot', snapshot: { ...snapshot, nodes, edges }, diagnostics: [], readonly: false });
  dom.window.document.querySelector('[data-node-id="root"]').click();
  const card = dom.window.document.querySelector('[data-node-id="child"]');
  assert.equal(card.dataset.downstream, '4');
  assert.ok(!card.textContent.includes('2 downstream'));
});

test('back and resume preserve the same dirty form and switching nodes requires confirmation', t => {
  const { dom, messages, $, saved } = fixture(t);
  dom.window.document.querySelector('[data-node-id="child"]').click();
  const body = $('body'); body.value = '# Draft\n'; body.dispatchEvent(new dom.window.Event('input'));
  $('back').click();
  assert.equal(saved().view, 'overview');
  assert.equal($('resume').hidden, false);
  dom.window.confirm = () => false;
  dom.window.document.querySelector('[data-node-id="root"]').click();
  assert.equal(saved().selected, 'child');
  $('resume').click();
  assert.equal($('body'), body);
  assert.equal($('body').value, '# Draft\n');
  $('editor').dispatchEvent(new dom.window.Event('submit', { cancelable: true }));
  assert.equal(messages.at(-1).expect, 'version-1');
  assert.equal(messages.at(-1).body, '# Draft\n');
});

test('new-node drafts survive the total-graph view and produce valid render reports', t => {
  const { dom, snapshot, $, messages, saved } = fixture(t);
  $('new').click();
  $('body').value = '# Candidate\n'; $('body').dispatchEvent(new dom.window.Event('input'));
  assert.ok(model.renderMatches({ snapshot }, messages.at(-1)));
  $('back').click();
  assert.ok(model.renderMatches({ snapshot }, messages.at(-1)));
  assert.equal(saved().creating, true);
  $('resume').click();
  assert.equal($('body').value, '# Candidate\n');
  assert.ok(model.renderMatches({ snapshot }, messages.at(-1)));
});

test('color modes have legends, persist without canonical changes and do not erase Git badges', t => {
  const { dom, snapshot, send, $, saved } = fixture(t);
  const target = { ...snapshot, nodes: [root, { ...child, retired: true }] };
  send({ type: 'snapshot', snapshot: target, diagnostics: [], readonly: false, diff: {
    base: snapshot, target, changes: [{ id: 'child', kind: 'changed' }], added_edges: [], removed_edges: [], base_ref: 'HEAD', target_ref: 'workspace',
  } });
  const oldColor = dom.window.document.querySelector('[data-node-id="child"]').style.getPropertyValue('--node-accent');
  $('color-mode').value = 'type'; $('color-mode').dispatchEvent(new dom.window.Event('change'));
  const card = dom.window.document.querySelector('[data-node-id="child"]');
  assert.notEqual(card.style.getPropertyValue('--node-accent'), oldColor);
  assert.equal(card.dataset.minDistance, '1');
  assert.equal(card.dataset.maxDistance, '1');
  assert.match(card.querySelector('.git-badge').textContent, /changed/);
  assert.match($('legend').textContent, /Existing node types/);
  assert.equal(saved().colorMode, 'type');
  assert.equal(target.nodes[1].retired, true);
  assert.equal(card.dataset.retired, 'true');
  assert.match(card.querySelector('.retired-badge').textContent, /retired/);
  assert.equal('status' in target.nodes[1], false);
  assert.equal('distance' in target.nodes[1], false);
});

function distanceFixture(t) {
  const f = fixture(t), nodes = [root, child, { ...child, id: 'a' }, { ...child, id: 'b', parents: ['a'] }];
  nodes[1] = { ...child, parents: ['root', 'b'] };
  f.snapshot = { ...f.snapshot, nodes, edges: [['root', 'a'], ['a', 'b'], ['b', 'child'], ['root', 'child']] };
  f.send({ type: 'snapshot', snapshot: f.snapshot, diagnostics: [], readonly: false });
  f.card = id => f.dom.window.document.querySelector(`[data-node-id="${id}"]`);
  return f;
}

test('minimum/maximum distance modes have exact labels, different fills/legends, and no on-node hop text', t => {
  const { dom, $, card, snapshot, messages, saved } = distanceFixture(t);
  assert.deepEqual([...$('color-mode').options].map(o => o.textContent), ['Min. Distance to Manifesto', 'Max. Distance to Manifesto', 'Node type']);
  const world = [...$('cards').children].map(c => [c.dataset.nodeId, c.style.left, c.style.top, c.style.height]);
  const camera = $('graph').style.transform, before = JSON.stringify(snapshot);
  assert.equal(card('child').style.getPropertyValue('--node-accent'), model.color('distance', child, 1));
  assert.match($('legend').textContent, /Shortest directed path/);
  $('color-mode').value = 'max-distance'; $('color-mode').dispatchEvent(new dom.window.Event('change'));
  assert.equal(card('child').style.getPropertyValue('--node-accent'), model.color('max-distance', child, 3));
  assert.equal(card('child').dataset.minDistance, '1');
  assert.equal(card('child').dataset.maxDistance, '3');
  assert.match($('legend').textContent, /3 hops.*Longest directed path/);
  assert.equal(saved().colorMode, 'max-distance');
  assert.deepEqual([...$('cards').children].map(c => [c.dataset.nodeId, c.style.left, c.style.top, c.style.height]), world);
  assert.equal($('graph').style.transform, camera);
  card('child').click();
  for (const mode of ['type', 'distance', 'max-distance']) {
    $('color-mode').value = mode; $('color-mode').dispatchEvent(new dom.window.Event('change'));
    assert.equal(dom.window.document.querySelector('.distance-badge'), null);
    assert.doesNotMatch($('cards').textContent, /Manifesto:|\b\d+ hops?\b/);
    assert.doesNotMatch($('focus-context').textContent, /distance|hops/i);
  }
  assert.equal(JSON.stringify(snapshot), before);
  assert.ok(messages.every(m => ['ready', 'rendered'].includes(m.type)));
});

test('distance switches and refreshed path bounds retain the same dirty form, caret, fingerprint and camera', t => {
  const { dom, $, card, snapshot, send, saved } = distanceFixture(t);
  card('child').click();
  const body = $('body'); body.value = '# Draft'; body.dispatchEvent(new dom.window.Event('input'));
  body.focus(); body.setSelectionRange(2, 5, 'backward');
  const camera = $('graph').style.transform;
  $('color-mode').value = 'max-distance'; $('color-mode').dispatchEvent(new dom.window.Event('change'));
  assert.equal($('body'), body);
  assert.equal(dom.window.document.activeElement, body);
  assert.deepEqual([body.selectionStart, body.selectionEnd, body.selectionDirection], [2, 5, 'backward']);
  assert.equal(saved().formFingerprint, 'version-1');
  assert.equal($('graph').style.transform, camera);
  // Bounds come from the whole snapshot: b remains at distance two in this focus.
  assert.equal(card('b').dataset.maxDistance, '2');
  send({ type: 'snapshot', snapshot: { ...snapshot, fingerprint: 'new' }, diagnostics: [], readonly: false });
  assert.equal(saved().colorMode, 'max-distance');
  assert.equal(saved().formFingerprint, 'version-1');
  assert.equal($('body').value, '# Draft');
  assert.deepEqual([body.selectionStart, body.selectionEnd], [2, 5]);
});

test('maximum-distance preference restores without rebasing a draft or camera', t => {
  const { $, saved } = fixture(t, { restored: {
    colorMode: 'max-distance', selected: 'child', view: 'focus', dirty: true,
    formFingerprint: 'old', cameras: { 'focus:child': { x: 40, y: -70, k: 1.6 } },
    draft: { body: '# Restored', sources: '[]', slug: '', nodeType: 'requirement', parents: ['root'] },
  } });
  assert.equal($('color-mode').value, 'max-distance');
  assert.equal(saved().colorMode, 'max-distance');
  assert.equal(saved().formFingerprint, 'old');
  assert.equal($('body').value, '# Restored');
  assert.deepEqual({ ...saved().cameras['focus:child'] }, { x: 40, y: -70, k: 1.6 });
});

test('min/max revision metrics stay separate even when historical overlays create a display cycle', t => {
  const { dom, $, card, snapshot, send } = distanceFixture(t);
  const old = { ...child, id: 'old', parents: ['child'] };
  const base = { ...snapshot, nodes: [...snapshot.nodes, old], edges: [...snapshot.edges, ['child', 'old']] };
  const target = { ...snapshot, nodes: [root, { ...child, parents: ['root'] }, { ...child, id: 'a', parents: ['child'] }, { ...child, id: 'b', parents: ['a'] }],
    edges: [['root', 'child'], ['child', 'a'], ['a', 'b']] };
  send({ type: 'snapshot', snapshot: target, diagnostics: [], readonly: true, diff: {
    base, target, changes: [{ id: 'old', kind: 'removed' }], added_edges: [['child', 'a']], removed_edges: [['root', 'a'], ['b', 'child'], ['child', 'old']], base_ref: 'base', target_ref: 'target',
  } });
  $('color-mode').value = 'max-distance'; $('color-mode').dispatchEvent(new dom.window.Event('change'));
  assert.equal(card('child').dataset.maxDistance, '1', 'A surviving node uses target paths, not base or union.');
  assert.equal(card('old').dataset.minDistance, '2');
  assert.equal(card('old').dataset.maxDistance, '4', 'A removed node uses the complete base paths.');
  assert.equal(card('old').style.getPropertyValue('--node-accent'), model.color('max-distance', old, 4));
  card('old').click();
  assert.equal($('save').disabled, true);
  assert.doesNotMatch($('focus-context').textContent, /hops|distance/i);
});

test('high zoom keeps native headline/form identity, intrinsic size, caret and unhinted text styles', t => {
  const { dom, $, messages, saved } = fixture(t);
  const style = dom.window.document.createElement('style');
  style.textContent = readFileSync(join(__dirname, '../media/graph.css'), 'utf8'); dom.window.document.head.append(style);
  assert.doesNotMatch(style.textContent, /will-change\s*:\s*transform/);
  assert.equal(dom.window.getComputedStyle(dom.window.document.querySelector('.card')).height, '112px');
  dom.window.document.querySelector('[data-node-id="child"]').click();
  const headline = $('title'), body = $('body'), card = headline.closest('.card'), width = card.style.width;
  body.value = '# Native draft'; body.dispatchEvent(new dom.window.Event('input')); body.focus(); body.setSelectionRange(2, 7);
  $('viewport').dispatchEvent(new dom.window.WheelEvent('wheel', { bubbles: true, cancelable: true, deltaY: -6000, clientX: 400, clientY: 250 }));
  assert.equal(Number($('viewport').dataset.scale), 2.5);
  assert.equal($('title'), headline); assert.equal($('body'), body);
  assert.equal(card.style.width, width);
  assert.equal(dom.window.getComputedStyle(headline).fontSize, '18px');
  assert.deepEqual([body.selectionStart, body.selectionEnd], [2, 7]);
  assert.equal(saved().formFingerprint, 'version-1');
  assert.equal(dom.window.document.querySelector('#cards canvas, #cards img'), null);
  assert.ok(messages.every(m => ['ready', 'rendered'].includes(m.type)));
});

test('removed-node metrics come from the base snapshot rather than a revision union', t => {
  const { dom, snapshot, send, $ } = fixture(t);
  const base = { ...snapshot, nodes: [...snapshot.nodes, { ...child, id: 'grand', parents: ['child'] }], edges: [...snapshot.edges, ['child', 'grand']] };
  const target = { ...snapshot, nodes: [root], edges: [] };
  send({ type: 'snapshot', snapshot: target, diagnostics: [], readonly: true, diff: {
    base, target, changes: [{ id: 'child', kind: 'removed' }, { id: 'grand', kind: 'removed' }], added_edges: [], removed_edges: base.edges, base_ref: 'old', target_ref: 'new',
  } });
  dom.window.document.querySelector('[data-node-id="root"]').click();
  const removed = dom.window.document.querySelector('[data-node-id="child"]');
  assert.equal(removed.dataset.downstream, '1');
  removed.click();
  assert.match($('focus-context').textContent, /1 downstream nodes.*base revision/);
  assert.equal($('save').disabled, true);
});

test('viewport resize changes neither world positions nor camera, including the expanded form', t => {
  const { dom, snapshot, send, $, resize } = fixture(t);
  const positions = () => [...$('cards').children].map(card => [card.dataset.nodeId, card.style.left, card.style.top, card.style.width]);
  const before = positions(), transform = $('graph').style.transform;
  resize(360);
  send({ type: 'snapshot', snapshot, diagnostics: [], readonly: false });
  assert.deepEqual(positions(), before);
  assert.equal($('graph').style.transform, transform);
  dom.window.document.querySelector('[data-node-id="child"]').click();
  const focused = positions(), focusedTransform = $('graph').style.transform;
  resize(1900);
  send({ type: 'snapshot', snapshot, diagnostics: [], readonly: false });
  assert.deepEqual(positions(), focused);
  assert.equal($('graph').style.transform, focusedTransform);
  assert.equal(dom.window.document.querySelector('.expanded').style.width, `${model.DETAIL_WIDTH}px`);
});

test('wheel zoom is pointer-anchored, keeps layout unchanged and does not send mutations', t => {
  const { dom, messages, $ } = fixture(t);
  const current = () => ({ x: Number($('viewport').dataset.cameraX), y: Number($('viewport').dataset.cameraY), k: Number($('viewport').dataset.scale) });
  const before = current(), points = [...$('cards').children].map(card => [card.style.left, card.style.top]);
  const event = new dom.window.WheelEvent('wheel', { bubbles: true, cancelable: true, deltaY: -120, clientX: 410, clientY: 230 });
  $('viewport').dispatchEvent(event);
  const after = current();
  assert.ok(after.k > before.k);
  assert.ok(Math.abs((410 - before.x) / before.k - (410 - after.x) / after.k) < 1e-9);
  assert.ok(Math.abs((230 - before.y) / before.k - (230 - after.y) / after.k) < 1e-9);
  assert.deepEqual([...$('cards').children].map(card => [card.style.left, card.style.top]), points);
  assert.equal(event.defaultPrevented, true);
  assert.ok(messages.every(message => ['ready', 'rendered'].includes(message.type)));
});

test('middle-button and background drag pan without selecting nodes or clamping at graph bounds', t => {
  const { dom, $, saved } = fixture(t);
  const before = Number($('viewport').dataset.cameraX);
  const card = dom.window.document.querySelector('.card.manifesto');
  const mouse = (target, type, x, y, button) => target.dispatchEvent(new dom.window.MouseEvent(type, {
    bubbles: true, cancelable: true, view: dom.window, clientX: x, clientY: y, button,
  }));
  mouse(card, 'mousedown', 50, 100, 1);
  mouse(dom.window, 'mousemove', -4000, 170, 1);
  mouse(dom.window, 'mouseup', -4000, 170, 1);
  assert.equal(Number($('viewport').dataset.cameraX), before - 4050);
  assert.equal(saved().view, 'overview');
  assert.equal(saved().selected, undefined);
  const moved = Number($('viewport').dataset.cameraX);
  mouse($('viewport'), 'mousedown', 100, 100, 0);
  mouse(dom.window, 'mousemove', 220, 120, 0);
  mouse(dom.window, 'mouseup', 220, 120, 0);
  assert.equal(Number($('viewport').dataset.cameraX), moved + 120);
});

test('refresh retains native textarea focus, selection and the original draft fingerprint', t => {
  const { dom, snapshot, send, $, saved } = fixture(t);
  dom.window.document.querySelector('[data-node-id="child"]').click();
  $('body').value = '# Draft in progress'; $('body').dispatchEvent(new dom.window.Event('input'));
  $('body').focus(); $('body').setSelectionRange(3, 8, 'backward');
  send({ type: 'snapshot', snapshot: { ...snapshot, fingerprint: 'version-2' }, diagnostics: [], readonly: false });
  assert.equal(dom.window.document.activeElement, $('body'));
  assert.equal($('body').selectionStart, 3);
  assert.equal($('body').selectionEnd, 8);
  assert.equal($('body').selectionDirection, 'backward');
  assert.equal(saved().formFingerprint, 'version-1');
});

test('form scrolling, text selection and keyboard editing never initiate camera gestures', t => {
  const { dom, $ } = fixture(t);
  dom.window.document.querySelector('[data-node-id="child"]').click();
  const transform = $('graph').style.transform;
  const wheel = new dom.window.WheelEvent('wheel', { bubbles: true, cancelable: true, deltaY: -120 });
  $('body').dispatchEvent(wheel);
  $('body').dispatchEvent(new dom.window.KeyboardEvent('keydown', { bubbles: true, cancelable: true, key: '+' }));
  $('body').dispatchEvent(new dom.window.MouseEvent('mousedown', { bubbles: true, view: dom.window, button: 0 }));
  assert.equal(wheel.defaultPrevented, false);
  assert.equal($('graph').style.transform, transform);
  assert.equal($('body').disabled, false);
});

test('overview and focused cameras survive back, resume and refresh with the draft fingerprint', t => {
  const { dom, snapshot, send, $, saved } = fixture(t, { restored: {
    view: 'overview', cameras: { overview: { x: -275, y: 45, k: 0.75 } },
  } });
  const cameraValue = () => JSON.parse(JSON.stringify(saved().cameras));
  const overview = cameraValue().overview;
  dom.window.document.querySelector('[data-node-id="child"]').click();
  $('body').value = '# Draft'; $('body').dispatchEvent(new dom.window.Event('input'));
  $('viewport').dispatchEvent(new dom.window.KeyboardEvent('keydown', { bubbles: true, key: 'ArrowLeft' }));
  const focused = cameraValue()['focus:child'];
  $('back').click();
  assert.deepEqual(cameraValue().overview, overview);
  $('resume').click();
  assert.deepEqual(cameraValue()['focus:child'], focused);
  send({ type: 'snapshot', snapshot: { ...snapshot, fingerprint: 'version-2' }, diagnostics: [], readonly: false });
  assert.deepEqual(cameraValue()['focus:child'], focused);
  assert.equal(saved().formFingerprint, 'version-1');
  assert.equal($('body').value, '# Draft');
});

test('camera recovery controls have keyboard equivalents and clamp zoom limits', t => {
  const { dom, $ } = fixture(t);
  $('viewport').dispatchEvent(new dom.window.KeyboardEvent('keydown', { bubbles: true, key: '+' }));
  assert.equal(Number($('viewport').dataset.scale), 1.25);
  $('zoom-reset').click();
  assert.equal(Number($('viewport').dataset.scale), 1);
  for (let n = 0; n < 30; n++) $('zoom-in').click();
  assert.equal(Number($('viewport').dataset.scale), 2.5);
  for (let n = 0; n < 60; n++) $('zoom-out').click();
  assert.equal(Number($('viewport').dataset.scale), 0.12);
  $('viewport').dispatchEvent(new dom.window.KeyboardEvent('keydown', { bubbles: true, key: 'Home' }));
  assert.ok(Number($('viewport').dataset.scale) > 0.12);
});

test('connections retain screen strength and arrow joins at minimum zoom without endpoint circles', t => {
  const { dom, $, messages } = fixture(t);
  const world = [...$('cards').children].map(card => [card.style.left, card.style.top]);
  const paths = [...$('edges').querySelectorAll('.link')];
  for (let n = 0; n < 60; n++) $('zoom-out').click();
  const k = Number($('viewport').dataset.scale);
  assert.equal(k, 0.12);
  assert.equal($('edges').querySelectorAll('circle, marker').length, 0);
  assert.deepEqual([...$('edges').querySelectorAll('.link')], paths, 'Zoom must not recreate the connections.');
  for (const path of paths) {
    assert.ok(parseFloat(path.style.strokeWidth) * k >= model.MIN_STROKE_PIXELS - 1e-9);
    const head = $('edges').querySelector(`.arrow-head[data-child="${path.dataset.child}"]`);
    assert.ok(head);
    const coordinates = head.getAttribute('d').match(/-?\d+(?:\.\d+)?/g).map(Number);
    assert.ok((coordinates[2] - coordinates[0]) * k >= model.MIN_ARROW_PIXELS - 1e-9);
    assert.ok(path.getAttribute('d').endsWith(`L${coordinates[0]},${coordinates[3]}`));
  }
  assert.deepEqual([...$('cards').children].map(card => [card.style.left, card.style.top]), world);
  assert.ok(messages.every(message => ['ready', 'rendered'].includes(message.type)));
  dom.window.document.querySelector('.card.requirement').click();
  assert.equal($('edges').querySelectorAll('circle').length, 0);
});

test('historical dash patterns remain visible when zoomed out', t => {
  const { dom, snapshot, send, $ } = fixture(t);
  send({ type: 'snapshot', snapshot: { ...snapshot, nodes: [root], edges: [] }, diagnostics: [], readonly: true, diff: {
    base: snapshot, removed_edges: snapshot.edges, added_edges: [], changes: [{ id: 'child', kind: 'removed' }], base_ref: 'old', target_ref: 'new',
  } });
  for (let n = 0; n < 60; n++) $('zoom-out').click();
  const k = Number($('viewport').dataset.scale), removed = $('edges').querySelector('.link.removed');
  const dash = removed.style.strokeDasharray.split(' ').map(Number);
  assert.deepEqual(dash.map(length => length * k), [6, 5]);
  assert.ok($('edges').querySelector('.arrow-head.removed'));
});

test('project text cannot inject markup or scripts into node cards', t => {
  const { dom, snapshot, send } = fixture(t);
  const attack = '<img src=x onerror="globalThis.injected=true">';
  send({ type: 'snapshot', snapshot: { ...snapshot, nodes: [{ ...root, body: `# ${attack}\n` }] }, diagnostics: [], readonly: false });
  assert.equal(dom.window.document.querySelector('img'), null);
  assert.equal(dom.window.injected, undefined);
  assert.equal(dom.window.document.querySelector('.card strong').textContent, attack);
});
