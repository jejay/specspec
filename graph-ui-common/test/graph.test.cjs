const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { JSDOM } = require('jsdom');
const { graphHtml } = require('../view.cjs');
const model = require('../media/graph-model.js');

const root = { id: 'root', type: 'manifesto', parents: [], body: '# Purpose\n', path: '_specspec/root.md', sources: [] };
const child = { id: 'child', type: 'requirement', parents: ['root'], body: '# Child\n', path: '_specspec/child.md', sources: [] };

function fixture(t, options = {}) {
  const dom = new JSDOM(graphHtml(name => name, 'local', 'test', options.html), { runScripts: 'outside-only', pretendToBeVisual: true });
  const messages = [];
  const viewport = dom.window.document.getElementById('viewport');
  let viewportWidth = options.width || 1000;
  Object.defineProperty(viewport, 'clientWidth', { get: () => viewportWidth });
  Object.defineProperty(viewport, 'clientHeight', { value: 650 });
  let saved = options.restored;
  dom.window.SpecSpecHost = { postMessage: message => messages.push(message), getState: () => saved, setState: value => { saved = value; },
    onMessage: listener => dom.window.addEventListener('message', event => listener(event.data)) };
  dom.window.confirm = () => true;
  dom.window.structuredClone = structuredClone; // Browser APIs not supplied by jsdom.
  dom.window.Range.prototype.getClientRects = () => [];
  dom.window.Range.prototype.getBoundingClientRect = () => ({ left: 0, right: 0, top: 0, bottom: 0 });
  for (const name of ['vendor/graph-vendor.js', 'graph-model.js', 'graph-camera.js', 'graph-annotations.js', 'graph.js']) {
    dom.window.eval(readFileSync(join(__dirname, '../media', name), 'utf8'));
  }
  t.after(() => {
    dom.window.close();
    assert.deepEqual(messages.filter(message => message.type === 'client-error'), [], 'Renderer errors must not be mistaken for successful DOM tests.');
  });
  const snapshot = { format_version: 7, valid: true, nodes: [root, child], edges: [['root', 'child']] };
  const send = message => dom.window.dispatchEvent(new dom.window.MessageEvent('message', { data: message }));
  const $ = id => dom.window.document.getElementById(id);
  send({ type: 'snapshot', snapshot, diagnostics: [], readonly: false });
  return { dom, messages, snapshot, send, $, saved: () => saved, resize: width => {
    viewportWidth = width; dom.window.dispatchEvent(new dom.window.Event('resize'));
  } };
}

test('header uses only the optical brand symbol, adjacent revision and accessible refresh icon', t => {
  const { dom, $, send, snapshot, messages } = fixture(t, { html: { showProject: false } });
  const brand = dom.window.document.querySelector('.brand-icon');
  assert.equal(brand.getAttribute('aria-label'), 'SpecSpec');
  assert.equal(brand.getAttribute('role'), 'img');
  assert.equal(brand.nextElementSibling, $('revision'));
  assert.equal(dom.window.document.querySelector('.toolbar strong'), null);
  assert.equal($('project'), null);
  assert.equal($('refresh').textContent, '');
  assert.equal($('refresh').getAttribute('aria-label'), 'Refresh graph');
  assert.equal($('refresh').title, 'Refresh graph');
  assert.ok($('refresh').querySelector('svg[aria-hidden="true"]'));
  send({ type: 'snapshot', snapshot, diagnostics: [], readonly: false,
    diff: { base: snapshot, base_ref: 'HEAD', target_ref: 'workspace', nodes: [], edges: [] } });
  assert.equal($('revision').textContent, 'HEAD → workspace');
  $('refresh').click(); assert.equal(messages.at(-1).type, 'refresh');
  dom.window.document.querySelector('[data-node-id="child"]').click();
  assert.equal($('editor').hidden, false, 'Omitting project chrome must not interrupt renderer setup.');
  const desktop = fixture(t);
  desktop.$('project').click(); assert.equal(desktop.messages.at(-1).type, 'select-project');
});

test('source-file changes leave the header area quiet while retaining diagnostics and node source cues', t => {
  for (const showProject of [false, true]) {
    const { dom, $, send, snapshot } = fixture(t, { html: { showProject } });
    for (const count of [0, 1, 19, 100]) {
      const sourceChanges = Array.from({ length: count }, (_, i) => ({ path: `src/changed-${i}.js` }));
      send({ type: 'snapshot', snapshot, note: 'Comparison ready', diagnostics: [{ code: 'INFO', message: 'Literal diagnostic' }], readonly: false,
        diff: { base: snapshot, base_ref: 'HEAD', target_ref: 'workspace', nodes: [], edges: [], source_changes: sourceChanges,
          source_affected: count ? ['child'] : [] } });
      assert.equal($('linked-sources'), null); assert.equal($('source-summary'), null); assert.equal($('source-files'), null);
      assert.doesNotMatch(dom.window.document.body.textContent, /changed linked source file|potential review context|src\/changed-/i);
      assert.equal($('revision').textContent, 'HEAD → workspace');
      assert.equal($('message').textContent, 'Comparison ready\nINFO: Literal diagnostic');
      const card = dom.window.document.querySelector('[data-node-id="child"]');
      assert.equal(card.classList.contains('source-changed'), count > 0);
      if (count) assert.match(card.querySelector('.git-badge').textContent, /source changed/);
    }
    dom.window.document.querySelector('[data-node-id="child"]').click();
    assert.equal($('editor').hidden, false);
  }
});

test('fresh graph-invalid snapshots show missing endpoint stubs and keep current forms editable', t => {
  const f=fixture(t); f.dom.window.document.querySelector('[data-node-id="child"]').click();
  const broken={...f.snapshot,valid:false,nodes:[root,{...child,parents:['gone','root']}],edges:[['root','child'],['gone','child']]};
  f.send({type:'snapshot',snapshot:broken,diagnostics:[{code:'REFERENCE',message:'Missing parent gone'}],readonly:false});
  assert.match(f.$('message').textContent,/Graph INVALID/);
  assert.equal(f.$('save').disabled,false);assert.equal(f.$('body').readOnly,false);
  assert.equal(f.$('new').disabled,false);assert.equal(f.$('sync-notice').hidden,true);
  assert.ok(f.dom.window.document.querySelector('[data-node-id="gone"].missing'));
  assert.match(f.$('parent-links').textContent,/gone/);
  f.$('body').value='# Deliberate repair';f.$('body').dispatchEvent(new f.dom.window.Event('input'));
  f.$('save').click();assert.equal(f.messages.at(-1).type,'save');assert.deepEqual([...f.messages.at(-1).parents],['gone','root']);
  f.send({type:'cancelled'});f.$('discard').click();f.$('back').click();
  f.dom.window.document.querySelector('[data-node-id="gone"]').click();
  assert.equal(f.$('save').disabled,true);assert.equal(f.$('delete').disabled,true);assert.equal(f.$('body').readOnly,true);
  assert.equal(f.dom.window.document.querySelector('.git-corner'),null,'A missing never-committed identity is not a fabricated D.');
  assert.match(f.$('focus-context').textContent,/Unknown/);
  f.send({type:'snapshot',snapshot:{...broken,inventory:[root.path,child.path,'_specspec/gone.md'],unreadable_paths:['_specspec/gone.md']},diagnostics:[{code:'SCHEMA',message:'Unreadable current parent'}],readonly:false});
  assert.equal(f.$('title').textContent,'Unreadable parent');
  assert.match(f.$('identity').textContent,/unreadable document/);assert.doesNotMatch(f.$('identity').textContent,/deleted|earlier context/);
  assert.equal(f.$('save').disabled,true);
});

test('dirty unreadable targets retain the invalid banner, honest identity and copyable unsavable text', t => {
  const f=fixture(t);f.dom.window.document.querySelector('[data-node-id="child"]').click();
  f.$('body').value='# Retained local draft';f.$('body').dispatchEvent(new f.dom.window.Event('input'));
  f.send({type:'snapshot',snapshot:{...f.snapshot,valid:false,complete:false,nodes:[root],edges:[],inventory:[root.path,child.path],unreadable_paths:[child.path]},diff:{base:f.snapshot,base_ref:'HEAD',target_ref:'workspace',changes:[{id:'child',kind:'unavailable'}],added_edges:[],removed_edges:[]},diagnostics:[{code:'SCHEMA',message:'Unreadable current document'}],readonly:false});
  assert.match(f.$('message').textContent,/Graph INVALID/);assert.match(f.$('message').textContent,/Unreadable node draft/);
  assert.equal(f.$('title').textContent,'Unreadable node draft');assert.equal(f.$('body').value,'# Retained local draft');
  assert.equal(f.$('save').disabled,true);assert.equal(f.$('body').readOnly,true);assert.equal(f.$('body').disabled,false);
});

test('cyclic and disconnected current records render completely without a last-valid substitution', t => {
  const f=fixture(t), left={...child,id:'left',parents:['right']},right={...child,id:'right',parents:['left']};
  f.send({type:'snapshot',snapshot:{...f.snapshot,valid:false,nodes:[root,left,right],edges:[['left','right'],['right','left']]},diagnostics:[{code:'CYCLE',message:'left/right'}],readonly:false});
  assert.equal(f.dom.window.document.querySelectorAll('#cards .card').length,3);
  f.dom.window.document.querySelector('[data-node-id="left"]').click();assert.equal(f.$('save').disabled,false);
  assert.match(f.$('message').textContent,/CYCLE/);
});

function saveKey(f, target, flags = {}) {
  const event = new f.dom.window.KeyboardEvent('keydown', { key: 's', ctrlKey: true, bubbles: true, cancelable: true, ...flags });
  target.dispatchEvent(event); return event;
}

test('Ctrl/Command+S submits the focused managed form, preserves draft/caret and suppresses pending/repeat saves', t => {
  const f = fixture(t), { dom, $, messages, send } = f;
  assert.equal(saveKey(f, $('viewport')).defaultPrevented, false);
  dom.window.document.querySelector('[data-node-id="child"]').click();
  $('body').value = '# Keyboard draft'; $('body').dispatchEvent(new dom.window.Event('input'));
  $('body').focus(); $('body').setSelectionRange(2, 8);
  assert.equal(saveKey(f, dom.window.document.activeElement).defaultPrevented, true);
  assert.equal(messages.at(-1).type, 'save'); assert.equal(messages.at(-1).body, '# Keyboard draft');
  const count = messages.filter(m => m.type === 'save').length;
  saveKey(f, $('sources')); assert.equal(messages.filter(m => m.type === 'save').length, count);
  send({ type: 'error', message: 'Save failed' });
  assert.equal($('body').value, '# Keyboard draft'); assert.equal(f.saved().dirty, true);
  assert.deepEqual([$('body').selectionStart, $('body').selectionEnd], [2, 8]);
  saveKey(f, $('sources'), { repeat: true });
  assert.equal(messages.filter(m => m.type === 'save').length, count);
  assert.equal(saveKey(f, $('sources'), { altKey: true }).defaultPrevented, false);
  assert.equal(saveKey(f, $('sources'), { shiftKey: true }).defaultPrevented, false);
  $('source-preview').setAttribute('open', '');
  assert.equal(saveKey(f, $('source-preview-code')).defaultPrevented, false);
  $('source-preview').removeAttribute('open');
  saveKey(f, $('sources'), { ctrlKey: false, metaKey: true, key: 'S' });
  assert.equal(messages.filter(m => m.type === 'save').length, count + 1);
  send({ type: 'cancelled' }); $('back').click();
  assert.equal(saveKey(f, $('viewport')).defaultPrevented, false);
});

test('save shortcut reuses native document version/sequence and creates new nodes through the managed add path', t => {
  const f = fixture(t), { dom, $, snapshot, send, messages } = f;
  send({ type: 'snapshot', snapshot, diagnostics: [], readonly: false, selectedId: 'child',
    document: { nodeId: 'child', version: 4, dirty: false } });
  $('body').value = '# Native keyboard edit'; $('body').dispatchEvent(new dom.window.Event('input'));
  const edit = messages.at(-1); assert.equal(edit.type, 'edit');
  saveKey(f, dom.window.document.querySelector('.cm-content'));
  const save = messages.at(-1); assert.equal(save.type, 'save');
  assert.equal(save.documentVersion, 4); assert.equal(save.editSequence, edit.editSequence);
  assert.equal(save.body, edit.body); assert.equal(save.id, 'child');
  const n = fixture(t); n.$('new').click(); n.$('body').value = '# New keyboard node';
  saveKey(n, n.$('node-type'));
  assert.equal(n.messages.at(-1).type, 'add'); assert.equal(n.messages.at(-1).body, '# New keyboard node');
});

test('save shortcut and direct submits honor provisional, historical, invalid and deleted-node restrictions', t => {
  for (const kind of ['provisional', 'readonly', 'invalid', 'deleted']) {
    const f = fixture(t), { dom, $, snapshot, send, messages } = f;
    dom.window.document.querySelector('[data-node-id="child"]').click();
    $('body').value = '# Retained'; $('body').dispatchEvent(new dom.window.Event('input'));
    if (kind === 'invalid') send({ type: 'sync-error', message: 'Invalid graph' });
    else send({ type: 'snapshot', snapshot: kind === 'deleted' ? { ...snapshot, nodes: [root], edges: [] } : snapshot,
      diagnostics: [], readonly: kind === 'readonly', provisional: kind === 'provisional' });
    assert.equal($('save').disabled, true, kind);
    const before = messages.length;
    saveKey(f, $('sources'));
    $('editor').dispatchEvent(new dom.window.Event('submit', { cancelable: true }));
    assert.equal(messages.length, before, kind); assert.equal($('body').value, '# Retained');
  }
});

test('canvas chrome floats with contextual framing icons and color-only legends', t => {
  const {dom,$}=fixture(t);
  assert.equal(dom.window.document.querySelector('footer,#canvas-help,.legend-help'),null);
  assert.equal($('viewport').hasAttribute('aria-describedby'),false);
  const visible=()=>[...dom.window.document.querySelectorAll('.framing-controls button')].filter(b=>!b.hidden).map(b=>b.getAttribute('aria-label'));
  assert.deepEqual(visible(),['Frame graph','Frame rectangle']);
  for(const button of dom.window.document.querySelectorAll('.framing-controls button')) {
    assert.ok(button.querySelector('svg[aria-hidden="true"]'));assert.ok(button.title);assert.equal(button.textContent,'');
  }
  $('frame-area').click();assert.equal($('frame-area').getAttribute('aria-pressed'),'true');
  dom.window.dispatchEvent(new dom.window.KeyboardEvent('keydown',{key:'Escape'}));assert.equal($('frame-area').getAttribute('aria-pressed'),'false');
  dom.window.document.querySelector('[data-node-id="child"]').click();assert.deepEqual(visible(),['Frame graph','Frame node','Frame rectangle']);
  $('new').click();assert.deepEqual(visible(),['Frame graph','Frame node','Frame rectangle']);
  for(const mode of model.COLOR_MODES) {
    $('color-mode').value=mode;$('color-mode').dispatchEvent(new dom.window.Event('change'));
    assert.ok($('legend').querySelector('i'));assert.equal($('legend').querySelector('.legend-help'),null);
    assert.doesNotMatch($('legend').textContent,/\b(?:not|never|no)\b/i);
  }
  const css=readFileSync(join(__dirname,'../media/graph.css'),'utf8');
  assert.match(css,/#viewport \{ position: absolute; inset: 0;/);
  assert.match(css,/\.camera-controls \{[^}]*bottom: 14px;[^}]*border-radius: 12px/);
});

test('camera paint and rectangle framing preserve native editing, highlights and intrinsic world geometry',async t=>{
  const {dom,$,saved,messages,snapshot,send}=fixture(t);dom.window.document.querySelector('[data-node-id="child"]').click();
  const body=$('body');body.value='# Keep the draft';body.dispatchEvent(new dom.window.Event('input'));body.focus();body.setSelectionRange(2,7);
  const world=()=>JSON.stringify([...$('cards').children].map(c=>[c.dataset.nodeId,c.style.left,c.style.top,c.style.width,c.style.height]));
  const initial=world(),original=saved().originalNode;
  const pointer=(type,x,y,flags={},target=$('viewport'))=>{
    const e=new dom.window.MouseEvent(type,{bubbles:true,cancelable:true,view:dom.window,clientX:x,clientY:y,button:0,...flags});
    Object.defineProperty(e,'pointerId',{value:1});target.dispatchEvent(e);return e;
  };
  $('frame-area').click();pointer('pointerdown',150,160);pointer('pointermove',450,360,{},dom.window);
  assert.equal($('frame-selection').hidden,false);pointer('pointerup',450,360,{},dom.window);
  assert.equal($('frame-selection').hidden,true);assert.equal($('frame-area').getAttribute('aria-pressed'),'false');
  assert.equal(world(),initial);assert.equal($('body'),body);assert.equal(body.value,'# Keep the draft');
  assert.deepEqual([body.selectionStart,body.selectionEnd],[2,7]);assert.ok(body.contains(dom.window.document.activeElement));
  assert.equal(saved().originalNode,original);assert.equal(saved().selected,'child');assert.equal(saved().dirty,true);
  assert.ok(messages.every(m=>['ready','rendered'].includes(m.type)));
  await new Promise(resolve=>dom.window.setTimeout(resolve,1));
  $('zoom-reset').click();
  $('zoom-out').click();
  assert.equal($('viewport').dataset.scale,'0.8');
  assert.equal($('cards').style.getPropertyValue('--node-fill-strength'),'0%');
  assert.equal(parseFloat($('edges').style.getPropertyValue('--normal-edge-strength')),70);
  $('zoom-out').click();
  assert.ok(Math.abs(Number($('viewport').dataset.scale)-0.64)<1e-12);
  assert.equal($('cards').style.getPropertyValue('--node-fill-strength'),'0%');
  assert.ok(parseFloat($('edges').style.getPropertyValue('--normal-edge-strength'))<70);
  $('zoom-out').click();
  assert.equal($('cards').style.getPropertyValue('--node-fill-strength'),'0%');
  $('zoom-out').click();
  assert.equal($('cards').style.getPropertyValue('--node-fill-strength'),'0%');
  $('zoom-out').click();
  assert.ok(parseFloat($('cards').style.getPropertyValue('--node-fill-strength'))>0);
  for(let i=0;i<30;i++) $('zoom-out').click();
  assert.equal($('viewport').dataset.scale,'0.12');assert.equal($('cards').style.getPropertyValue('--node-fill-strength'),'100%');
  assert.equal($('edges').style.getPropertyValue('--normal-edge-strength'),'35%');assert.equal(world(),initial);
  $('zoom-reset').click();assert.equal($('cards').style.getPropertyValue('--node-fill-strength'),'0%');
  send({type:'snapshot',snapshot:{...snapshot,nodes:[root],edges:[]},diagnostics:[],readonly:false});
  assert.equal($('frame-node').hidden,false);assert.equal(dom.window.document.querySelector('.expanded').dataset.nodeId,'__draft__');
  const before=$('graph').style.transform;$('frame-node').click();assert.notEqual($('graph').style.transform,before);
  assert.equal(body.value,'# Keep the draft');assert.equal(body.readOnly,true);
});

test('tool copy stays concise and positive while project text and validation evidence remain literal',t=>{
  const {dom,$,snapshot,send}=fixture(t);
  const doc=new JSDOM(graphHtml(name=>name,'local','test')).window.document;
  const own=[doc.body.textContent,...[...doc.querySelectorAll('[title],[aria-label]')].map(e=>(e.title||'')+' '+(e.getAttribute('aria-label')||''))].join(' ');
  assert.doesNotMatch(own,/\b(?:not|never|cannot)\b/i);assert.equal(doc.querySelector('footer'),null);doc.defaultView.close();
  const literal='# This is not a tool label';
  send({type:'snapshot',snapshot:{...snapshot,nodes:[root,{...child,body:literal}]},diagnostics:[{code:'EXAMPLE',message:'Parent is not present.'}],readonly:false});
  dom.window.document.querySelector('[data-node-id="child"]').click();
  assert.equal($('body').value,literal);assert.match($('message').textContent,/Parent is not present/);
});

test('canonical compact IDs retain equals signs in cards, parent pickers and save messages', t => {
  const { dom, snapshot, send, $, messages } = fixture(t);
  const shortRoot = { ...root, id: '-_____8=', path: '_specspec/-_____8=.md' };
  const shortChild = { ...child, id: 'Zm9vYmE=', parents: [shortRoot.id], path: '_specspec/Zm9vYmE=.md' };
  const candidate = { ...child, id: 'ZnJlc2g=', parents: [shortRoot.id], path: '_specspec/ZnJlc2g=.md' };
  send({ type: 'snapshot', snapshot: { ...snapshot, nodes: [shortRoot, shortChild, candidate], edges: [[shortRoot.id, shortChild.id], [shortRoot.id, candidate.id]] }, diagnostics: [], readonly: false });
  assert.ok(dom.window.document.querySelector('[data-node-id="-_____8="] small').textContent.endsWith(shortRoot.id));
  dom.window.document.querySelector('[data-node-id="Zm9vYmE="]').click();
  assert.ok($('identity').textContent.includes(shortChild.id));
  assert.ok($('identity').textContent.includes(shortChild.path));
  assert.ok([...$('parent-candidate').options].some(o => o.textContent.endsWith(candidate.id)));
  $('body').value = '# Full identity'; $('body').dispatchEvent(new dom.window.Event('input'));
  $('editor').dispatchEvent(new dom.window.Event('submit', { cancelable: true }));
  const save = messages.at(-1);
  assert.equal(save.type, 'save'); assert.equal(save.id, shortChild.id);
  assert.deepEqual(Array.from(save.parents), [shortRoot.id]);
});

test('blob source links capture into the native form and preview literal resolved ranges without writes', t => {
  const {dom,$,messages,snapshot,send}=fixture(t);
  const reference={path:'code.js',blob:'a'.repeat(40),mode:'strict',ranges:[[2,4],[9,10]]};
  const impl={...child,id:'impl',type:'implementation',sources:[reference]};
  send({type:'snapshot',snapshot:{...snapshot,nodes:[root,impl],edges:[['root','impl']]},diagnostics:[],readonly:false});
  dom.window.document.querySelector('[data-node-id="impl"]').click();
  assert.equal($('source-tools').hidden,false);assert.match($('source-links').textContent,/anchor 2–4, 9–10.*strict/);
  $('source-links').querySelector('button').click();
  assert.equal(messages.at(-1).type,'source-view');assert.deepEqual(JSON.parse(messages.at(-1).reference),reference);
  $('source-path').value='code.js';$('source-ranges').value='2:4, 9:10';$('source-mode').value='expanding';$('source-staged').checked=true;$('capture-source').click();
  const capture=messages.at(-1);assert.equal(capture.type,'source-capture');assert.deepEqual(Array.from(capture.ranges),['2:4','9:10']);assert.equal(capture.staged,true);
  const body=$('body');body.focus();body.setSelectionRange(1,3);const value=body.value;
  send({type:'source-captured',id:'impl',reference:{...reference,mode:'expanding'}});
  assert.equal(JSON.parse($('sources').value).length,2);assert.equal(body.value,value);assert.equal($('body'),body);
  assert.equal(messages.some(m=>m.type==='save'||m.type==='add'),false);
  $('source-links').querySelector('button').click();
  send({type:'source-preview',requestId:messages.at(-1).requestId,resolution:{path:'moved.js',target:'HEAD',mode:'strict',outcome:'conflict',ranges:[[20,21]]},original:true,chunks:[{start:2,selected:[2,3],lines:['<img onerror="bad()">','literal']} ]});
  assert.match($('source-preview-title').textContent,/moved.js.*HEAD/);assert.match($('source-preview-status').textContent,/Original anchored/);
  assert.match($('source-preview-code').textContent,/> 2: <img/);assert.equal($('source-preview-code').querySelector('img'),null);
  $('close-source-preview').click();assert.equal($('source-preview').hasAttribute('open'),false);
});

test('historical source hints remain navigable while capture is disabled', t => {
  const {dom,$,snapshot,send}=fixture(t);const impl={...child,type:'implementation',sources:[{path:'code.js'}]};
  send({type:'snapshot',snapshot:{...snapshot,nodes:[root,impl]},diagnostics:[],readonly:true});
  dom.window.document.querySelector('[data-node-id="child"]').click();assert.equal($('capture-source').disabled,true);
  assert.equal($('source-links').querySelector('button').disabled,false);
});

test('source preview replies/errors follow the newest click and ignore navigation, edited refs and revision adoption', t => {
  const {dom,$,messages,snapshot,send}=fixture(t);
  const impl={...child,type:'implementation',sources:[{path:'a.js'},{path:'b.js'}]};
  const next={type:'snapshot',snapshot:{...snapshot,nodes:[root,impl]},diagnostics:[],readonly:false};
  send(next);dom.window.document.querySelector('[data-node-id="child"]').click();
  const click=index=>{$('source-links').children[index].querySelector('button').click();return messages.at(-1).requestId;};
  const result=requestId=>({type:'source-preview',requestId,resolution:{path:'a.js',target:'workspace',mode:'whole',outcome:'resolved',ranges:[]},chunks:[],original:false});
  const a=click(0),b=click(1);send(result(a));assert.equal($('source-preview').open,false);
  send({type:'source-error',requestId:a,message:'Obsolete failure'});assert.equal($('message').textContent,'Resolving source region…');
  send(result(b));assert.equal($('source-preview').open,true);$('close-source-preview').click();
  const c=click(0);$('back').click();send(result(c));assert.equal($('source-preview').open,false);
  dom.window.document.querySelector('[data-node-id="child"]').click();const d=click(0);
  $('sources').value='[{"path":"edited.js"}]';$('sources').dispatchEvent(new dom.window.Event('input'));send(result(d));assert.equal($('source-preview').open,false);
  const e=click(0);send({...next,readonly:true});send(result(e));assert.equal($('source-preview').open,false);
  const current=click(0);send({type:'source-error',requestId:current,message:'Current failure'});assert.equal($('message').textContent,'Current failure');
  assert.equal(messages.some(m=>m.type==='save'||m.type==='add'),false);
});

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

function rightClick(dom, target) {
  const event = new dom.window.MouseEvent('contextmenu', { bubbles: true, cancelable: true, button: 2 });
  target.dispatchEvent(event); return event;
}

const workspaceState = { head: 'e'.repeat(40), changes: {} };
function shot(id = '1', nodes = ['root', 'child'], text = 'Which nodes express this idea?') {
  return { id: id.repeat(32), spotlight_version: 2, created_at: `2026-01-0${id}T12:00:00+00:00`,
    message: text, nodes, comparison: { base: 'HEAD', target: 'workspace' }, workspace: workspaceState };
}
function annotationsFixture(t, baseline = [], autoApply = true) {
  const f = hoverFixture(t), originalSend = f.send;
  let shots = baseline;
  f.send = message => { if (message.type === 'annotations') shots = message.shots; return originalSend(message); };
  const originalPost = f.dom.window.SpecSpecHost.postMessage;
  f.dom.window.SpecSpecHost.postMessage = message => {
    originalPost(message);
    if (autoApply && message.type === 'annotation-select') f.send({ type: 'annotation-applied', shot: shots.find(s => s.id === message.shot) });
  };
  f.send({ type: 'snapshot', snapshot: f.snapshot, workspace_state: workspaceState, diagnostics: [], readonly: false });
  f.send({ type: 'annotations', shots: baseline });
  f.labels = () => [...f.$('annotation-list').querySelectorAll('.annotation-label')];
  return f;
}

test('a new shot catches attention without focus/caret/camera/form, graph or geometry changes', t => {
  const { dom, $, card, snapshot, saved, messages, send } = annotationsFixture(t);
  card('child').click(); const body = $('body'); body.value = '# A managed draft'; body.dispatchEvent(new dom.window.Event('input'));
  body.focus(); body.setSelectionRange(2, 6, 'backward');
  const before = JSON.stringify(snapshot), count = messages.length, camera = $('graph').style.transform;
  const world = [...$('cards').children].map(c => [c.style.left,c.style.top,c.style.width,c.style.height]);
  const paths = [...$('edges').children].map(p => p.getAttribute('d'));
  send({ type: 'annotations', shots: [shot('1', ['child'], '<img onerror="bad()">')] });
  assert.equal($('spotlights-count').textContent, '1'); assert.equal($('spotlights-count').hidden, false);
  assert.equal($('annotations-toggle').getAttribute('aria-label'), 'Spotlights, 1 new');
  assert.equal($('annotations-panel').hidden, true); assert.equal($('annotation-arrival'), null);
  assert.equal($('annotation-read'), null); assert.equal($('annotation-show'), null);
  assert.match($('annotation-live').textContent, /new spotlight/); assert.equal($('annotation-list').querySelector('img'), null);
  assert.ok(body.contains(dom.window.document.activeElement)); assert.deepEqual([body.selectionStart,body.selectionEnd,body.selectionDirection], [2,6,'backward']);
  assert.equal(body.value, '# A managed draft'); assert.equal(saved().dirty, true); assert.equal(saved().selected, 'child');
  assert.equal(messages.length, count); assert.equal(JSON.stringify(snapshot), before); assert.equal($('graph').style.transform, camera);
  assert.deepEqual([...$('cards').children].map(c => [c.style.left,c.style.top,c.style.width,c.style.height]), world);
  assert.deepEqual([...$('edges').children].map(p => p.getAttribute('d')), paths);
  for (const target of [body, $('title'), $('save'), card('root'), $('viewport')]) assert.equal(rightClick(dom, target).defaultPrevented, false);
});

test('the dropdown selects whole one-ink spotlights, closes, and retains older arrivals', t => {
  const { $, send, labels, card, saved } = annotationsFixture(t);
  const older = shot('1', ['root','child']), newer = shot('2', ['child'], 'Another answer');
  send({ type: 'annotations', shots: [older] }); $('annotations-toggle').click();
  assert.equal($('annotations-panel').getAttribute('role'), 'menu'); assert.equal($('spotlights-count').hidden, true);
  assert.equal(labels().length, 1); labels()[0].click(); const active = JSON.stringify(saved().annotationHighlights);
  assert.equal(saved().annotationHighlights.length, 2); assert.equal(card('root').dataset.annotationLabel, 'highlight');
  assert.equal(card('root').style.getPropertyValue('--annotation-ink'), '');
  assert.match(card('child').getAttribute('aria-description'), /Shift-click toggles/);
  assert.equal($('annotations-panel').hidden, true);
  send({ type: 'annotations', shots: [newer, older] });
  assert.equal($('annotations-panel').hidden, true); assert.equal($('spotlights-count').textContent, '1');
  assert.deepEqual([...$('annotation-list').children].map(n => n.dataset.shotId), [newer.id, older.id]);
  assert.deepEqual(labels().map(b => b.querySelector('.annotation-label-text').firstChild.textContent), ['Another answer', 'Which nodes express this idea?']);
  assert.equal(JSON.stringify(saved().annotationHighlights), active); assert.equal(labels()[1].getAttribute('role'), 'menuitem');
  $('annotations-toggle').click(); labels()[0].click();
  assert.equal(card('root').dataset.annotationLabel, undefined); assert.equal(card('child').dataset.annotationLabel, 'highlight');
  $('annotations-toggle').click(); labels()[0].click(); assert.ok(card('child').dataset.annotationLabel, 'Selecting again keeps the spotlight on.');
  $('annotations-toggle').click(); $('annotation-clear').click(); assert.equal($('cards').querySelector('[data-annotation-label]'), null);
  assert.equal($('annotations-panel').hidden, true); assert.equal('annotationSeen' in saved(), false); assert.equal('shots' in saved(), false);
  for (const id of ['annotation-filter', 'annotation-frame', 'annotation-preview']) assert.equal($(id), null);
  assert.equal($('annotation-list').querySelector('.annotation-swatch,.annotation-members'), null);
});

test('the session badge counts arriving spotlight batches since opening, not existing labels or repeated reads', t => {
  const existing = shot();
  const { $, send, labels } = annotationsFixture(t, [existing]);
  assert.equal($('spotlights-count').hidden, true); assert.equal($('annotations-toggle').textContent, 'Spotlights');
  const second = shot('2'), third = shot('3');
  send({ type: 'annotations', shots: [third, second, existing] });
  assert.equal($('spotlights-count').textContent, '2');
  send({ type: 'annotations', shots: [third, second, existing] });
  assert.equal($('spotlights-count').textContent, '2');
  $('annotations-toggle').click(); assert.equal($('spotlights-count').hidden, true);
  const fourth = shot('4'); send({ type: 'annotations', shots: [fourth, third, second, existing] });
  assert.equal($('spotlights-count').textContent, '1');
  labels()[0].click(); assert.equal($('spotlights-count').textContent, '1');
  assert.equal($('annotations-panel').hidden, true); assert.equal($('spotlights-count').hidden, false);
  $('annotations-toggle').click(); assert.equal($('spotlights-count').hidden, true);
  send({ type: 'annotations', shots: [] }); assert.equal($('spotlights-count').hidden, true);
});

test('identity rings include changed versions and deleted base ghosts, retaining absent IDs', t => {
  const { $, send, snapshot, card, labels, saved } = annotationsFixture(t);
  const target = { ...snapshot, nodes: snapshot.nodes.filter(n => n.id !== 'grand'), edges: snapshot.edges.filter(e => !e.includes('grand')) };
  send({ type: 'snapshot', snapshot: target, diagnostics: [], readonly: true,
    diff: { base: snapshot, changes: [{ id:'grand',kind:'removed' },{ id:'child',kind:'changed' }], added_edges: [], removed_edges: [['child','grand']] } });
  const answer = shot('1', ['root','child','grand','sibling','absent']); delete answer.workspace;
  answer.comparison = { base: 'a'.repeat(40), target: 'b'.repeat(40) };
  send({ type: 'annotations', shots: [answer] }); $('annotations-toggle').click(); labels()[0].click();
  for (const id of ['root','child','grand','sibling']) assert.ok(card(id).dataset.annotationLabel);
  assert.equal(saved().annotationHighlights.length, 5);
  assert.match($('annotation-list').textContent, /1 absent/);
  assert.match($('annotation-list').textContent, /aaaaaaaaaa → bbbbbbbbbb/);
  assert.equal($('annotation-list').querySelector('.annotation-members'), null);
  assert.equal($('save').disabled, true); assert.equal($('annotation-flush').disabled, false);
});

test('invalid workspace fallback highlights IDs without enabling managed edits', t => {
  const answer=shot('1',['child']);
  const {send,card,$}=annotationsFixture(t,[answer]);card('child').click();
  send({type:'annotation-applied',shot:answer,invalid:true,warning:'Workspace files need repair; using displayed graph.'});
  assert.equal($('save').disabled,true);assert.equal($('sync-notice').hidden,false);
  assert.equal(card('child').dataset.annotationLabel,'highlight');assert.match($('annotation-warning').textContent,/need repair/);
});

test('selection requests its comparison and waits for host application before framing', t => {
  const answer = shot('1', ['sibling']);
  const { $, labels, messages, saved, send, card, snapshot } = annotationsFixture(t, [answer], false);
  const pose = $('graph').style.transform;
  $('annotations-toggle').click(); labels()[0].click();
  assert.equal($('annotations-panel').hidden,true);
  assert.deepEqual(JSON.parse(JSON.stringify(messages.at(-1))), {type:'annotation-select',shot:answer.id});
  assert.equal(saved().annotationHighlights.length,0); assert.equal($('graph').style.transform,pose);
  send({type:'snapshot',snapshot,diagnostics:[],readonly:false,workspace_state:workspaceState});
  send({type:'annotation-applied',shot:answer});
  assert.equal(card('sibling').dataset.annotationLabel,'highlight'); assert.equal(saved().view,'overview');
});

test('editable highlights restore independently of shots; flush keeps them until whole-set clear', t => {
  const { $, send, saved, labels } = annotationsFixture(t); const answer = shot(), newer = shot('2');
  send({ type: 'annotations', shots: [answer] }); $('annotations-toggle').click(); labels()[0].click();
  send({ type: 'annotations', shots: [newer, answer] }); assert.equal($('spotlights-count').textContent, '1');
  const restored = structuredClone(saved()), next = fixture(t, { restored });
  assert.equal('annotationSeen' in restored, false);
  next.send({ type:'snapshot',snapshot:next.snapshot,workspace_state:workspaceState,diagnostics:[],readonly:false });
  next.send({ type:'annotations',shots:[newer, answer] });
  assert.equal(next.$('spotlights-count').hidden, true); assert.equal(next.$('annotations-panel').hidden, true);
  assert.equal(next.$('cards').querySelectorAll('[data-annotation-label]').length, 2);
  for (const mode of model.COLOR_MODES) { next.$('color-mode').value=mode; next.$('color-mode').dispatchEvent(new next.dom.window.Event('change')); assert.equal(next.$('cards').querySelectorAll('[data-annotation-label]').length, 2); }
  next.send({ type:'annotations',shots:[] }); assert.equal(next.$('cards').querySelectorAll('[data-annotation-label]').length, 2);
  assert.equal(next.saved().annotationHighlights.length, 2); assert.equal(next.$('spotlights-count').hidden, true);
  next.$('annotations-toggle').click(); next.$('annotation-clear').click();
  assert.equal(next.$('cards').querySelector('[data-annotation-label]'), null);
});

test('selecting a spotlight frames its union while retaining an edited focused draft', t => {
  const { dom, $, send, labels, card, saved } = annotationsFixture(t);
  card('child').click(); const body = $('body'); body.value='# Retained draft'; body.dispatchEvent(new dom.window.Event('input')); body.setSelectionRange(2,5);
  const answer = shot('1', ['root','sibling']);
  send({type:'annotations',shots:[answer]}); $('annotations-toggle').click(); labels()[0].click();
  assert.equal(saved().view, 'overview'); assert.equal(saved().dirty, true); assert.equal($('body'), body); assert.equal(body.value, '# Retained draft');
  assert.ok(card('root').dataset.annotationLabel); assert.ok(card('sibling').dataset.annotationLabel);
  assert.equal($('annotations-panel').hidden, true);
  const boxes = ['root','sibling'].map(id => card(id)).map(c => ({ x: parseFloat(c.style.left), y: parseFloat(c.style.top), width: parseFloat(c.style.width), height: parseFloat(c.style.height) }));
  const x = Math.min(...boxes.map(b => b.x)), y = Math.min(...boxes.map(b => b.y));
  const bounds = { x, y, width: Math.max(...boxes.map(b => b.x+b.width))-x, height: Math.max(...boxes.map(b => b.y+b.height))-y };
  const expected = dom.window.SpecSpecCamera.frameTransform(bounds,1000,650);
  assert.deepEqual({ x: Number($('viewport').dataset.cameraX), y: Number($('viewport').dataset.cameraY), k: Number($('viewport').dataset.scale) }, { ...expected });
  assert.equal($('resume').hidden, false); $('resume').click(); assert.equal(saved().view, 'focus'); assert.equal($('body'), body); assert.deepEqual([body.selectionStart,body.selectionEnd], [2,5]);
});

test('keyboard and outside dismissal preserve rings/camera; errors keep the list and flush stays explicit', t => {
  const { dom, $, send, labels, messages, saved, card } = annotationsFixture(t);
  send({type:'annotations',shots:[shot(), shot('2', ['child'])]});
  const key = (target, key) => target.dispatchEvent(new dom.window.KeyboardEvent('keydown',{key,bubbles:true,cancelable:true}));
  key($('annotations-toggle'), 'ArrowDown'); assert.equal(dom.window.document.activeElement, labels()[0]);
  key(labels()[0], 'ArrowDown'); assert.equal(dom.window.document.activeElement, labels()[1]);
  key(labels()[1], 'Home'); assert.equal(dom.window.document.activeElement, labels()[0]);
  labels()[0].click(); const camera = $('graph').style.transform;
  $('annotations-toggle').click(); key(labels()[0], 'Escape');
  assert.equal(saved().annotationPanelOpen,false); assert.equal(dom.window.document.activeElement,$('annotations-toggle'));
  $('annotations-toggle').click(); $('viewport').dispatchEvent(new dom.window.Event('pointerdown',{bubbles:true}));
  assert.equal($('annotations-panel').hidden, true); assert.equal($('graph').style.transform,camera); assert.ok(card('root').dataset.annotationLabel);
  $('annotations-toggle').click(); key(labels()[0], 'End'); assert.equal(dom.window.document.activeElement,$('annotation-flush'));
  $('refresh').focus(); assert.equal($('annotations-panel').hidden,true); assert.equal(dom.window.document.activeElement,$('refresh'));
  send({type:'annotations-error',message:'Malformed local shot; retained for repair'});
  assert.equal(labels().length,2); assert.ok(card('root').dataset.annotationLabel); assert.match($('annotation-error').textContent,/List out of date/);
  assert.equal($('new').disabled,false); $('annotations-toggle').click(); $('annotation-flush').click();
  assert.equal(messages.at(-1).type,'annotation-flush'); assert.equal($('annotations-panel').hidden,true);
});

test('selection frames after closing the dropdown at all widths, with unchanged world layout', t => {
  const { dom, $, send, labels, card, resize, saved } = annotationsFixture(t);
  send({ type: 'annotations', shots: [shot('1', ['child'])] });
  Object.defineProperty($('annotations-panel'), 'offsetWidth', { value: 370 });
  const world = [...$('cards').children].map(c => [c.style.left,c.style.top,c.style.width,c.style.height]);
  const pose = () => ({ x: Number($('viewport').dataset.cameraX), y: Number($('viewport').dataset.cameraY), k: Number($('viewport').dataset.scale) });
  for (const width of [1000,400]) {
    resize(width); $('annotations-toggle').click(); labels()[0].click();
    const bounds = { x: parseFloat(card('child').style.left), y: parseFloat(card('child').style.top), width: 264, height: 112 };
    assert.equal($('annotations-panel').hidden, true); assert.equal(saved().annotationPanelOpen, false);
    assert.deepEqual(pose(), { ...dom.window.SpecSpecCamera.frameTransform(bounds, width, 650) });
    assert.deepEqual([...$('cards').children].map(c => [c.style.left,c.style.top,c.style.width,c.style.height]), world);
  }
});

test('spotlight rings use camera-scaled equal inset paint with independent focus and a plain red count badge', t => {
  const { dom, $, labels, card } = annotationsFixture(t, [shot('1', ['child'])]);
  const css=readFileSync(join(__dirname,'../media/graph.css'),'utf8');
  assert.match(css, /#cards \.card\[data-annotation-label\] \{ outline: var\(--annotation-ring-width, 5px\) solid var\(--spotlight-color\); outline-offset: var\(--annotation-ring-offset, -5px\); \}/);
  assert.match(css, /#cards \.card\[data-annotation-label\]:focus-visible \{ box-shadow: 0 0 0 2px var\(--vscode-focusBorder\)/);
  assert.match(css, /\.spotlights-count \{[^}]*border-radius: 999px; background: #c62828; color: #fff/);
  assert.doesNotMatch(css, /annotation-arriv|@keyframes/);
  assert.match(css, /:root \{ --spotlight-color: #ffffff; \}/);
  $('annotations-toggle').click(); labels()[0].click(); $('zoom-reset').click();
  assert.ok(card('child').dataset.annotationLabel);
  assert.equal($('cards').style.getPropertyValue('--annotation-ring-width'), '5px');
  assert.equal($('cards').style.getPropertyValue('--annotation-ring-offset'), '-5px');
  for (let index = 0; index < 60; index++) $('zoom-out').click();
  const scale = Number($('viewport').dataset.scale);
  const width = parseFloat($('cards').style.getPropertyValue('--annotation-ring-width'));
  assert.equal(scale, 0.12);
  assert.ok(width > 5);
  assert.ok(width * scale >= model.MIN_ANNOTATION_RING_PIXELS - 1e-9);
  assert.equal(parseFloat($('cards').style.getPropertyValue('--annotation-ring-offset')), -width);
});

function shiftClick(dom, target, modifiers = {}) {
  const event = new dom.window.MouseEvent('click', { bubbles: true, cancelable: true, button: 0, shiftKey: true, ...modifiers });
  target.dispatchEvent(event); return event;
}

test('manual toggles consume node clicks without navigation or draft changes', t => {
  const { dom, $, card, saved, messages } = annotationsFixture(t);
  card('child').click(); const body = $('body'); body.value = '# Keep draft'; body.dispatchEvent(new dom.window.Event('input'));
  body.focus(); body.setSelectionRange(2, 5);
  const pose = $('graph').style.transform, selected = saved().selected, count = messages.length;
  for (const on of [true,false,true,false]) {
    assert.equal(shiftClick(dom, card('root').querySelector('strong')).defaultPrevented, true);
    assert.equal(Boolean(card('root').dataset.annotationLabel), on);
    assert.equal(saved().selected, selected); assert.equal(saved().view, 'focus');
    assert.equal($('graph').style.transform, pose); assert.equal($('body'), body); assert.equal(body.value, '# Keep draft');
    assert.deepEqual([body.selectionStart,body.selectionEnd], [2,5]);
  }
  assert.equal(saved().annotationHighlights.length, 0); assert.equal(messages.length, count);
  shiftClick(dom, $('title')); assert.equal(card('child').dataset.annotationLabel, 'highlight');
  for (const target of [body, $('sources'), $('save'), $('parent-candidate')])
    assert.equal(shiftClick(dom, target, {ctrlKey: true}).defaultPrevented, false, 'Native controls retain modified clicks.');
});

test('loaded and manual highlights share toggles/removal/clear and never modify retained shots', t => {
  const answer = shot('1', ['root'], 'From agent');
  const { dom, $, card, labels, saved, send } = annotationsFixture(t, [answer]);
  const original = JSON.stringify(answer);
  $('annotations-toggle').click(); labels()[0].click(); shiftClick(dom, card('root'));
  assert.equal(card('root').dataset.annotationLabel, undefined);
  shiftClick(dom, card('root')); shiftClick(dom, card('child')); assert.equal(saved().annotationHighlights.length, 2);
  shiftClick(dom, card('root'), {ctrlKey:true}); assert.equal(card('root').dataset.annotationLabel, undefined);
  shiftClick(dom, card('child'), {metaKey:true}); assert.equal(saved().annotationHighlights.length, 0, 'Synthetic macOS Command+Shift removes too.');
  $('annotations-toggle').click(); labels()[0].click(); shiftClick(dom, card('child'));
  $('annotations-toggle').click(); $('annotation-clear').click();
  assert.equal($('cards').querySelector('[data-annotation-label]'), null);
  send({type:'annotations', shots:[answer]}); assert.equal(saved().annotationHighlights.length, 0);
  assert.equal(JSON.stringify(answer), original);
  $('annotations-toggle').click(); labels()[0].click(); assert.equal(card('root').dataset.annotationLabel, 'highlight');
});

test('workspace drift and HEAD movement warn visibly while identity rings remain useful', t => {
  const answer = shot('1', ['child']);
  const { $, card, send, snapshot, labels, saved } = annotationsFixture(t, [answer]);
  $('annotations-toggle').click(); labels()[0].click();
  const before = JSON.stringify(saved().annotationHighlights);
  const refresh = workspace_state => send({type:'snapshot',snapshot,workspace_state,diagnostics:[],readonly:false});
  refresh({head:workspaceState.head,changes:{child:'9'.repeat(64)}});
  assert.equal(card('child').dataset.annotationLabel,'highlight'); assert.equal(JSON.stringify(saved().annotationHighlights),before);
  assert.equal($('annotation-warning').hidden,false); assert.match($('annotation-warning').textContent,/Workspace nodes changed.*child/);
  assert.equal($('annotations-panel').hidden,true);
  refresh({head:'f'.repeat(40),changes:{}}); assert.match($('annotation-warning').textContent,/HEAD moved/);
  refresh(workspaceState); assert.equal($('annotation-warning').hidden,true);
  refresh(null); assert.match($('annotation-warning').textContent,/unavailable/);
  send({type:'annotation-context'}); assert.equal($('annotation-warning').hidden,true); assert.ok(card('child').dataset.annotationLabel);
});

test('manual highlights include historical ghosts; anonymous drafts have no identity', t => {
  const {dom, $, card, send, snapshot, saved} = annotationsFixture(t);
  send({type:'snapshot',snapshot:{...snapshot,nodes:[root],edges:[]},diagnostics:[],readonly:true,
    diff:{base:snapshot,changes:[{id:'child',kind:'removed'}],added_edges:[],removed_edges:snapshot.edges}});
  shiftClick(dom,card('child')); assert.equal(saved().annotationHighlights[0], 'child');
  assert.equal($('save').disabled,true);
  send({type:'snapshot',snapshot,diagnostics:[],readonly:false});
  shiftClick(dom,card('root')); assert.equal(saved().annotationHighlights.length,2);
  $('new').click(); const draft = $('cards').querySelector('[data-node-id="__draft__"]');
  assert.equal(shiftClick(dom,draft).defaultPrevented,false); assert.equal(saved().annotationHighlights.length,2);
});

test('create dialog cancels safely, sends one frozen ID/message set and retains retry/draft/camera state', t => {
  const {dom,$,card,labels,saved,messages,send} = annotationsFixture(t,[shot('1',['root'])]);
  assert.equal($('annotation-create').disabled,true);
  $('annotations-toggle').click(); labels()[0].click(); shiftClick(dom,card('child'));
  card('child').click(); const body=$('body'); body.value='# Keep this'; body.dispatchEvent(new dom.window.Event('input'));
  const pose=$('graph').style.transform, refs=JSON.stringify(saved().annotationHighlights);
  $('annotations-toggle').click(); $('annotation-create').click();
  assert.equal($('annotations-panel').hidden,true); assert.equal($('annotation-compose').hasAttribute('open'),true);
  assert.equal(dom.window.document.activeElement,$('annotation-message'));
  $('annotation-compose-cancel').click(); assert.equal(messages.filter(m=>m.type==='annotation-create').length,0);
  $('annotations-toggle').click(); $('annotation-create').click();
  const submit=()=> $('annotation-compose-form').dispatchEvent(new dom.window.Event('submit',{bubbles:true,cancelable:true}));
  $('annotation-message').value='  '; submit(); assert.match($('annotation-compose-error').textContent,/1–500/);
  $('annotation-message').value='x'.repeat(501); submit(); assert.equal(messages.filter(m=>m.type==='annotation-create').length,0);
  $('annotation-message').value='Please revise <img onerror="bad()">'; submit(); submit();
  const requests=messages.filter(m=>m.type==='annotation-create'); assert.equal(requests.length,1);
  assert.deepEqual(JSON.parse(JSON.stringify(requests[0])), {type:'annotation-create',message:'Please revise <img onerror="bad()">',nodes:['root','child']});
  assert.equal($('annotation-compose-save').disabled,true);
  send({type:'annotation-create-error',message:'Version unavailable; refresh and retry.'});
  assert.equal($('annotation-compose').hasAttribute('open'),true); assert.equal($('annotation-compose-save').disabled,false);
  assert.match($('annotation-message').value,/Please revise/); assert.match($('annotation-compose-error').textContent,/unavailable/);
  submit(); assert.equal(messages.filter(m=>m.type==='annotation-create').length,2);
  send({type:'annotations',shots:[shot('2',['child'],'Please revise <img>'),shot('1',['root'])]});
  send({type:'annotation-created'}); assert.equal($('annotation-compose').hasAttribute('open'),false);
  assert.equal($('annotation-list').querySelector('img'),null); assert.match($('annotation-live').textContent,/agent can read/);
  assert.equal(JSON.stringify(saved().annotationHighlights),refs); assert.equal($('graph').style.transform,pose);
  assert.equal($('body'),body); assert.equal(body.value,'# Keep this'); assert.equal(saved().dirty,true); assert.equal(saved().view,'focus');
});

function highlightedEdges($) {
  return [...$('edges').querySelectorAll('.link.incident-highlight')].map(p => `${p.dataset.parent}>${p.dataset.child}`).sort();
}

function assertPairedHighlights($) {
  const paths = [...$('edges').querySelectorAll('.link')], heads = [...$('edges').querySelectorAll('.arrow-head')];
  for (const path of paths) {
    const head = heads.find(h => h.dataset.parent === path.dataset.parent && h.dataset.child === path.dataset.child);
    assert.equal(head.classList.contains('incident-highlight'), path.classList.contains('incident-highlight'));
    assert.equal(head.classList.contains('hover-darkened'), path.classList.contains('hover-darkened'));
    assert.ok(!path.classList.contains('incident-highlight') || !path.classList.contains('hover-darkened'));
  }
}

function assertDarkening($, cards, edges) {
  assert.ok($('cards').querySelectorAll('.node-hovered').length <= 1);
  assert.ok(!cards.some(id => $('cards').querySelector(`[data-node-id="${id}"]`).classList.contains('node-hovered')));
  assert.deepEqual([...$('cards').querySelectorAll('.hover-darkened')].map(c => c.dataset.nodeId).sort(), cards);
  assert.deepEqual([...$('edges').querySelectorAll('.link.hover-darkened')].map(p => `${p.dataset.parent}>${p.dataset.child}`).sort(), edges);
  assertPairedHighlights($);
}

test('all types share transient hover state while the manifesto retains its square circular box', t => {
  const { dom, $, card } = hoverFixture(t);
  assert.equal(model.CARD_WIDTH, 264); assert.equal(model.CARD_HEIGHT, 112);
  assert.equal(model.DETAIL_WIDTH, 860);
  for (const id of ['root', 'child', 'grand']) {
    hoverEvent(dom, card(id));
    assert.deepEqual([...$('cards').querySelectorAll('.node-hovered')].map(c => c.dataset.nodeId), [id]);
    assert.equal(card(id).style.width, '264px'); assert.equal(card(id).style.height, id === 'root' ? '264px' : '112px');
    card(id).click(); hoverEvent(dom, $('body'));
    assert.equal(card(id).style.width, id === 'root' ? `${model.manifestoDiameter(822,720)}px` : '860px');
    if(id === 'root') assert.equal(card(id).style.height,card(id).style.width);
    assert.ok(card(id).classList.contains('node-hovered'));
    $('viewport').dispatchEvent(new dom.window.Event('pointerleave'));
    assert.equal($('cards').querySelector('.node-hovered'), null);
    $('back').click();
  }
});

test('type radii survive expansion and circle sizing preserves native content, colors and draft identity', t => {
  const f=fixture(t),{dom,$,snapshot,send,saved}=f;
  const style=dom.window.document.createElement('style');
  style.textContent=readFileSync(join(__dirname,'../media/graph.css'),'utf8');dom.window.document.head.append(style);
  const implementation={...child,id:'implementation',type:'implementation',parents:['child']};
  send({type:'snapshot',snapshot:{...snapshot,nodes:[root,child,implementation],edges:[['root','child'],['child','implementation']]},diagnostics:[],readonly:false});
  const card=id=>dom.window.document.querySelector(`[data-node-id="${id}"]`);
  for(const [id,radius] of [['root','50%'],['child','24px'],['implementation','0px']]) {
    assert.equal(dom.window.getComputedStyle(card(id)).borderRadius,radius);
    const accent=card(id).style.getPropertyValue('--node-accent');
    card(id).click();assert.equal(dom.window.getComputedStyle(card(id)).borderRadius,radius);
    assert.equal(card(id).style.getPropertyValue('--node-accent'),accent);
    $('back').click();
  }
  card('root').click();const body=$('body'),settings=$('node-details');
  body.value='# Native circular draft';body.dispatchEvent(new dom.window.Event('input'));body.focus();body.setSelectionRange(2,8);
  const state=saved();let height=900;
  Object.defineProperty(settings,'offsetHeight',{get:()=>height});
  Object.defineProperty(settings,'scrollHeight',{get:()=>height});
  for(height of [900,1450,600]) {
    $('color-mode').value='type';$('color-mode').dispatchEvent(new dom.window.Event('change'));
    assert.equal(card('root').style.width,`${model.manifestoDiameter(822,height)}px`);
    assert.equal(card('root').style.height,card('root').style.width);
    assert.equal(card('root').style.getPropertyValue('--detail-content-width'),'822px');
    assert.equal($('body'),body);assert.equal($('node-details'),settings);
    assert.equal(body.value,'# Native circular draft');assert.deepEqual([body.selectionStart,body.selectionEnd],[2,8]);
    assert.equal(saved().draft.body,state.draft.body);
  }
});

test('shared CSS keeps gray cards tinted and increases corner letters without ordinary compact-card growth', () => {
  const css = readFileSync(join(__dirname, '../media/graph.css'), 'utf8');
  assert.match(css, /\.card:hover, \.card\.node-hovered \{ background: color-mix/);
  assert.match(css, /#cards \.card:hover, #cards \.card\.node-hovered \{ --card-border-ink: oklch\(from var\(--node-accent, #8993a4\) min\(0\.95, calc\(l \+ 0\.10\)\) calc\(c \* 1\.30\) h\)/);
  assert.match(css, /#cards \.card\.manifesto:not\(\.revision-colored\):hover, #cards \.card\.manifesto:not\(\.revision-colored\)\.node-hovered \{ --card-border-ink: #fff/);
  assert.doesNotMatch(css, /#cards \.card:hover[^}]*border-color: #fff/);
  assert.doesNotMatch(css, /\.card\.manifesto[^}]*background:/);
  assert.doesNotMatch(css, /\.card\.manifesto[^}]*(?:\{ |; )color:/);
  assert.match(css, /\.git-corner \{[^}]*font-size: 20px; font-weight: 800/);
  assert.match(css, /\.badges \{[^}]*padding-right: 26px/);
  assert.match(css, /textarea, pre \{ font-family: var\(--vscode-editor-font-family, monospace\)/);
});

test('colored incident curves and heads share hue-preserving lightness/chroma emphasis, not foreground mixing', () => {
  const css = readFileSync(join(__dirname, '../media/graph.css'), 'utf8');
  assert.match(css, /\.link\.added, \.arrow-head\.added, \.link\.removed, \.arrow-head\.removed, \.link\.draft, \.arrow-head\.draft \{ --edge-hover-ink: oklch\(from var\(--edge-ink\) min\(0\.95, calc\(l \+ 0\.10\)\) calc\(c \* 1\.30\) h\)/);
  assert.match(css, /\.link\.incident-highlight \{ stroke: var\(--edge-hover-ink, color-mix[^}]*opacity: 1/);
  assert.match(css, /\.arrow-head\.incident-highlight \{ fill: var\(--edge-hover-ink, color-mix/);
  assert.match(css, /\.link\.normal, \.arrow-head\.normal \{ --edge-ink: color-mix\(in srgb, var\(--edge-normal\) var\(--normal-edge-strength, 70%\), #000\); --edge-hover-ink: color-mix\(in srgb, var\(--edge-normal\) 50%/);
  assert.doesNotMatch(css, /\.link\.normal \{ opacity:/);
});

test('hover darkens only outside direct displayed neighbors, including the unrelated manifesto', t => {
  const { dom, $, card, snapshot, send } = hoverFixture(t);
  hoverEvent(dom, card('child'));
  assertDarkening($, ['sibling'], ['root>sibling']);
  hoverEvent(dom, card('grand'));
  assertDarkening($, ['root', 'sibling'], ['root>child', 'root>sibling']);
  assert.equal(card('root').style.getPropertyValue('--node-accent'), '#d3d3d3');
  // A link between two immediate neighbors is still non-incident.
  const target = { ...snapshot, edges: [...snapshot.edges, ['root', 'grand']] };
  send({ type: 'snapshot', snapshot: target, diagnostics: [], readonly: false });
  hoverEvent(dom, card('child'));
  assertDarkening($, ['sibling'], ['root>grand', 'root>sibling']);
  const isolated = { ...child, id: 'isolated', parents: [] };
  send({ type: 'snapshot', snapshot: { ...target, nodes: [...target.nodes, isolated] }, diagnostics: [], readonly: true });
  hoverEvent(dom, card('isolated'));
  assert.deepEqual(highlightedEdges($), []);
  assertDarkening($, ['child', 'grand', 'root', 'sibling'], ['child>grand', 'root>child', 'root>grand', 'root>sibling']);
});

test('hover darkening clears on exit, blur, cancel and touch and survives redraw with the same identity', t => {
  const { dom, $, card, snapshot, send } = hoverFixture(t);
  dom.window.document.elementFromPoint = () => card('child');
  hoverEvent(dom, card('child'));
  send({ type: 'snapshot', snapshot, diagnostics: [], readonly: false });
  assertDarkening($, ['sibling'], ['root>sibling']);
  const target = { ...snapshot, edges: [...snapshot.edges, ['sibling', 'child']] };
  send({ type: 'snapshot', snapshot: target, diagnostics: [], readonly: false });
  assertDarkening($, [], ['root>sibling']);
  const clear = [
    () => hoverEvent(dom, card('child'), 'pointerout', $('viewport')),
    () => $('viewport').dispatchEvent(new dom.window.Event('pointerleave')),
    () => $('viewport').dispatchEvent(new dom.window.Event('pointercancel')),
    () => dom.window.dispatchEvent(new dom.window.Event('blur')),
    () => hoverEvent(dom, card('child'), 'pointerover', null, 'touch'),
  ];
  for (const action of clear) {
    hoverEvent(dom, card('child')); action();
    assertDarkening($, [], []);
    assert.deepEqual(highlightedEdges($), []);
  }
  hoverEvent(dom, card('sibling'));
  card('grand').click();
  assertDarkening($, [], []);
});

test('historical reversed links and expanded native forms use the displayed neighborhood', t => {
  const { dom, $, card, snapshot, send, saved, messages } = hoverFixture(t);
  const target = { ...snapshot, nodes: [root, { ...child, parents: ['root', 'sibling'] }, snapshot.nodes[3]],
    edges: [['root', 'child'], ['root', 'sibling'], ['sibling', 'child']] };
  send({ type: 'snapshot', snapshot: target, diagnostics: [], readonly: false, diff: {
    base: snapshot, changes: [{ id: 'grand', kind: 'removed' }], added_edges: [['sibling', 'child']],
    removed_edges: [['child', 'grand'], ['grand', 'child']],
  } });
  hoverEvent(dom, card('grand'));
  assertDarkening($, ['root', 'sibling'], ['root>child', 'root>sibling', 'sibling>child']);
  assert.ok($('edges').querySelector('.link.added.hover-darkened'));
  assert.ok($('edges').querySelector('.link.removed.incident-highlight'));
  card('child').click();
  const body = $('body'); body.value = '# Retained draft'; body.dispatchEvent(new dom.window.Event('input'));
  body.focus(); body.setSelectionRange(2, 5, 'backward');
  const draft = saved(), count = messages.length, cards = [...$('cards').children];
  hoverEvent(dom, card('root'));
  assertDarkening($, ['grand'], ['child>grand', 'grand>child', 'sibling>child']);
  hoverEvent(dom, body);
  assertDarkening($, [], ['root>sibling']);
  assert.deepEqual([...$('cards').children], cards);
  assert.equal(saved(), draft); assert.equal(messages.length, count);
  assert.ok(body.contains(dom.window.document.activeElement));
  assert.deepEqual([body.selectionStart, body.selectionEnd, body.selectionDirection], [2, 5, 'backward']);
});

test('unsaved draft neighbors darken without changing parents or host state', t => {
  const { dom, $, card, saved, messages } = hoverFixture(t);
  $('new').click();
  for (const id of ['root', 'sibling']) {
    $('parent-candidate').value = id; $('parent-candidate').dispatchEvent(new dom.window.Event('change')); $('add-parent').click();
  }
  const draft = saved(), count = messages.length;
  hoverEvent(dom, card('root'));
  assertDarkening($, ['sibling'], ['sibling>__draft__']);
  assert.ok($('edges').querySelector('.link.draft.hover-darkened'));
  hoverEvent(dom, $('body'));
  assertDarkening($, [], []);
  assert.equal(saved(), draft); assert.equal(messages.length, count);
});

test('manifesto cards and legends stay gray across modes, focus and Git overlays', t => {
  const { dom, $, snapshot, send } = fixture(t);
  send({ type: 'snapshot', snapshot, diagnostics: [], readonly: false,
    diff: { base: snapshot, changes: [{ id: 'root', kind: 'changed' }], added_edges: [], removed_edges: [] } });
  for (const mode of ['distance', 'max-distance', 'type']) {
    $('color-mode').value = mode; $('color-mode').dispatchEvent(new dom.window.Event('change'));
    let rootCard = dom.window.document.querySelector('.card.manifesto');
    assert.equal(rootCard.style.getPropertyValue('--node-accent'), '#d3d3d3');
    assert.ok(rootCard.querySelector('.git-corner.changed'));
    const swatch = [...$('legend').children].find(c => /manifesto/i.test(c.textContent)).querySelector('i');
    assert.equal(swatch.style.backgroundColor, 'rgb(211, 211, 211)');
    rootCard.click(); rootCard = dom.window.document.querySelector('.card.manifesto.expanded');
    assert.equal(rootCard.style.getPropertyValue('--node-accent'), '#d3d3d3');
    $('back').click();
  }
});

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
  assert.equal(saved().originalNode, child);
  assert.equal(messages.length, count);
  assert.ok(body.contains(dom.window.document.activeElement));
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
  const target = { ...snapshot, nodes: snapshot.nodes.map(n => n.id === 'child' ? { ...n, parents: ['root', 'sibling'] } : n), edges: [...snapshot.edges, ['sibling', 'child']] };
  send({ type: 'snapshot', snapshot: target, diagnostics: [], readonly: false });
  assert.deepEqual(highlightedEdges($), ['child>grand', 'root>child', 'sibling>child']);
  hit = 'sibling';
  $('viewport').dispatchEvent(new dom.window.WheelEvent('wheel', { bubbles: true, cancelable: true, deltaY: -100, clientX: 300, clientY: 200 }));
  assert.deepEqual(highlightedEdges($), ['root>sibling', 'sibling>child']);
  assertDarkening($, ['grand'], ['child>grand', 'root>child']);
  hit = undefined;
  send({ type: 'snapshot', snapshot: target, diagnostics: [], readonly: false });
  assert.deepEqual(highlightedEdges($), []);
  assertDarkening($, [], []);
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
  assertDarkening($, [], []);
});

test('nodes are editable without approval states or an acceptance action', t => {
  const { dom, $, saved } = fixture(t);
  assert.equal($('accept'), null);
  assert.equal($('save').textContent, 'Save node');
  assert.deepEqual([...$('color-mode').options].map(option => option.value), ['distance', 'max-distance', 'absolute-influence', 'relative-influence', 'log-absolute-influence', 'log-relative-influence', 'type', 'git-revision']);
  assert.equal(saved().colorMode, 'distance');
  for (const card of $('cards').children) {
    assert.equal('status' in card.dataset, false);
    assert.doesNotMatch(card.textContent, /proposed|accepted/);
  }
  dom.window.document.querySelector('[data-node-id="child"]').click();
  assert.equal($('body').disabled, false);
  assert.equal($('save').disabled, false);
  assert.equal($('delete').disabled, false);
  assert.equal($('retire'), null); assert.equal($('restore'), null);
  assert.doesNotMatch($('identity').textContent, /proposed|accepted/);
});

test('delete sends a physical deletion action; HEAD ghosts are copyable but never editable and vanish after commit', t => {
  const { dom, snapshot, send, messages, $, saved } = fixture(t);
  dom.window.document.querySelector('[data-node-id="child"]').click();
  $('delete').click();
  assert.equal(messages.at(-1).type, 'delete');
  assert.equal('expect' in messages.at(-1), false);
  assert.equal($('save').disabled, true);
  const target = { ...snapshot, nodes: [root], edges: [] };
  const diff = { base: snapshot, target, changes: [{ id: 'child', kind: 'removed' }], added_edges: [], removed_edges: snapshot.edges, base_ref: 'HEAD', target_ref: 'workspace' };
  send({ type: 'snapshot', snapshot: target, diff, diagnostics: [], readonly: false, force: true, selectedId: 'child' });
  assert.match($('identity').textContent, /deleted/);
  assert.equal($('delete').disabled, true); assert.equal($('save').disabled, true);
  assert.equal($('body').disabled, false); assert.equal($('body').readOnly, true);
  assert.equal($('body').value, child.body);
  assert.equal(dom.window.document.querySelector('.expanded .git-corner').textContent, 'D');
  // Staging alone changes no HEAD/base membership.
  send({ type: 'snapshot', snapshot: target, diff, diagnostics: [], readonly: false });
  assert.ok(dom.window.document.querySelector('[data-node-id="child"]'));
  send({ type: 'snapshot', snapshot: target, diff: { ...diff, base: target, changes: [], removed_edges: [] }, diagnostics: [], readonly: false });
  assert.equal(dom.window.document.querySelector('[data-node-id="child"]'), null);
  assert.equal(saved().view, 'overview'); assert.equal(saved().selected, undefined);
});

test('unsupported snapshots have no conversion controls and retain a disabled draft', t => {
  const { dom, snapshot, send, $, saved } = fixture(t);
  dom.window.document.querySelector('[data-node-id="child"]').click();
  $('body').value = '# Still my draft\n'; $('body').dispatchEvent(new dom.window.Event('input'));
  send({ type: 'snapshot', snapshot: { ...snapshot, format_version: 999 }, diagnostics: [], readonly: false });
  assert.equal($('migrate'), null);
  assert.equal($('schema-notice'), null);
  assert.equal($('new').disabled, true);
  assert.equal($('save').disabled, true);
  assert.equal($('body').value, '# Still my draft\n');
  assert.equal(saved().originalNode, child);
  send({ type: 'snapshot', snapshot, diagnostics: [], readonly: false });
  assert.equal($('body').value, '# Still my draft\n');
});

test('restored obsolete status colors fall back to distance without losing a draft or camera', t => {
  const { $, saved } = fixture(t, { restored: {
    colorMode: 'status', selected: 'child', view: 'focus', dirty: true,
    originalNode: child, creating: false,
    cameras: { 'focus:child': { x: 30, y: -50, k: 0.8 } },
    draft: { body: '# My draft\n', sources: '[]', nodeType: 'requirement', parents: ['root'] },
  } });
  assert.equal(saved().colorMode, 'distance');
  assert.equal($('body').value, '# My draft\n');
  assert.equal(saved().originalNode, child);
  assert.deepEqual({ ...saved().cameras['focus:child'] }, { x: 30, y: -50, k: 0.8 });
});

test('graph renders and new-node creation goes through a typed message', t => {
  const { dom, messages, $ } = fixture(t);
  assert.equal(dom.window.document.querySelectorAll('.card').length, 2);
  assert.equal($('new').disabled, false);
  $('new').click();
  assert.equal($('slug'), null);
  $('body').value = '# New\n';
  $('parent-candidate').value = 'root';
  $('parent-candidate').dispatchEvent(new dom.window.Event('change'));
  $('add-parent').click();
  $('editor').dispatchEvent(new dom.window.Event('submit', { cancelable: true }));
  const message = messages.at(-1);
  assert.equal(message.type, 'add');
  assert.equal('expect' in message, false);
  assert.equal(message.body, '# New\n');
  assert.equal('slug' in message, false);
  assert.deepEqual([...message.parents], ['root']);
  assert.equal($('save').disabled, true);
});

test('manifesto shows no parents or candidate choices while its body remains editable', t => {
  const { dom, messages, $ } = fixture(t);
  dom.window.document.querySelector('.card.manifesto').click();
  assert.equal($('parent-links').children.length, 0);
  assert.equal($('parents-summary').textContent, 'Manifesto root');
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
  assert.equal($('delete').disabled, true);
  assert.ok(![...$('parent-candidate').options].some(option => option.value === 'branch'));
  $('parent-links').querySelector('button').click();
  assert.equal($('parent-links').firstElementChild.dataset.parentId, 'branch');
  $('editor').dispatchEvent(new dom.window.Event('submit', { cancelable: true }));
  assert.deepEqual([...messages.at(-1).parents], ['branch']);
  assert.equal(messages.at(-1).originalNode, child);
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

test('parent drafts survive refresh and can be discarded without losing the original contents', t => {
  const { dom, messages, snapshot, send, $ } = fixture(t);
  dom.window.document.querySelector('.card.requirement').click();
  $('parent-links').querySelector('button').click();
  send({ type: 'snapshot', snapshot, diagnostics: [], readonly: false });
  assert.equal($('parent-links').children.length, 0);
  $('editor').dispatchEvent(new dom.window.Event('submit', { cancelable: true }));
  assert.deepEqual([...messages.at(-1).parents], []);
  assert.equal(messages.at(-1).originalNode, child);
  send({ type: 'error', message: 'Graph is stale' });
  $('discard').click();
  assert.equal($('parent-links').firstElementChild.dataset.parentId, 'root');
});

test('restored parent drafts retain original contents and do not turn candidates into links', t => {
  const { dom, messages, $ } = fixture(t, { restored: {
    selected: 'child', dirty: true, creating: false, originalNode: child,
    draft: { body: '# Unsaved\n', sources: '[]', nodeType: 'requirement', parents: [] },
  } });
  assert.equal($('parent-links').children.length, 0);
  assert.ok([...$('parent-candidate').options].some(option => option.value === 'root'));
  $('editor').dispatchEvent(new dom.window.Event('submit', { cancelable: true }));
  assert.equal(messages.at(-1).originalNode, child);
  assert.deepEqual([...messages.at(-1).parents], []);
});

test('old invalid manifesto parent drafts cannot restore editable root links', t => {
  const { dom, messages, $ } = fixture(t, { restored: {
    selected: 'root', dirty: true, creating: false, originalNode: root,
    draft: { body: '# Unsaved purpose\n', sources: '[]', nodeType: 'requirement', parents: ['child'] },
  } });
  assert.equal($('body').value, '# Unsaved purpose\n');
  assert.equal($('parent-links').children.length, 0);
  assert.equal($('parent-add-controls').hidden, true);
  $('editor').dispatchEvent(new dom.window.Event('submit', { cancelable: true }));
  assert.deepEqual([...messages.at(-1).parents], []);
});

test('external refresh preserves unsaved text and its original contents', t => {
  const { dom, messages, snapshot, send, $ } = fixture(t);
  dom.window.document.querySelector('.card.requirement').click();
  $('body').value = '# Unsaved\n';
  $('body').dispatchEvent(new dom.window.Event('input'));
  assert.equal($('delete').disabled, true);
  send({ type: 'snapshot', snapshot: { ...snapshot, nodes: [root, { ...child, body: '# External\n' }] }, diagnostics: [], readonly: false });
  assert.equal($('body').value, '# Unsaved\n');
  assert.match($('message').textContent, /changed outside/);
  $('editor').dispatchEvent(new dom.window.Event('submit', { cancelable: true }));
  assert.equal(messages.at(-1).originalNode, child);
  send({ type: 'error', message: 'Save failed' });
  assert.equal($('body').value, '# Unsaved\n');
  $('discard').click();
  assert.equal($('body').value, '# External\n');
});

test('invalid external files keep the last graph and draft selectable until a valid refresh', t => {
  const { dom, snapshot, send, $, saved } = fixture(t);
  dom.window.document.querySelector('[data-node-id="child"]').click();
  const body = $('body'); body.value = '# Retained'; body.dispatchEvent(new dom.window.Event('input'));
  body.focus(); body.setSelectionRange(2, 6);
  const cards = $('cards').children.length, camera = $('graph').style.transform;
  send({ type: 'sync-error', message: 'Files are invalid; displayed graph is out of date. YAML: incomplete' });
  assert.equal($('cards').children.length, cards); assert.equal($('body'), body);
  assert.equal(body.value, '# Retained'); assert.equal(body.disabled, false); assert.equal(body.readOnly, true);
  assert.equal($('save').disabled, true); assert.equal($('new').disabled, true);
  assert.match($('message').textContent, /out of date/); assert.equal(saved().originalNode, child);
  $('back').click(); $('resume').click();
  assert.equal($('sync-notice').hidden, false, 'Invalid-data warning survives draft navigation and notices.');
  send({ type: 'snapshot', snapshot, diagnostics: [], readonly: false });
  assert.equal($('sync-notice').hidden, true);
  assert.equal(body.readOnly, false); assert.equal($('save').disabled, false);
  assert.equal(body.value, '# Retained'); assert.equal($('graph').style.transform, camera);
  assert.deepEqual([body.selectionStart, body.selectionEnd], [2, 6]);
});

test('deleted edited nodes retain a visible copyable draft without inventing a canonical node', t => {
  const { dom, snapshot, send, $, saved, messages } = fixture(t);
  dom.window.document.querySelector('[data-node-id="child"]').click();
  const body = $('body'); body.value = '# Deleted draft'; body.dispatchEvent(new dom.window.Event('input'));
  const target = { ...snapshot, nodes: [root], edges: [] };
  send({ type: 'snapshot', snapshot: target, diagnostics: [], readonly: false });
  assert.equal($('body'), body); assert.equal(body.value, '# Deleted draft');
  assert.equal($('save').disabled, true); assert.equal(body.disabled, false);
  assert.ok($('cards').contains(body)); assert.match($('message').textContent, /Deleted node draft/);
  assert.equal(saved().originalNode, child); assert.ok(model.renderMatches({ snapshot: target }, messages.at(-1)));
  $('back').click(); $('resume').click(); assert.equal(body.value, '# Deleted draft');
  $('discard').click(); assert.equal(saved().dirty, false); assert.equal(saved().view, 'overview');
});

test('pre-hash-removal drafts keep their text but do not manufacture an original node record', t => {
  const { $, saved, messages, dom } = fixture(t, { restored: {
    selected: 'child', dirty: true, formFingerprint: 'obsolete',
    draft: { body: '# Legacy draft', sources: '[]', parents: ['root'], nodeType: 'requirement' },
  } });
  assert.equal($('body').value, '# Legacy draft'); assert.equal(saved().originalNode, undefined);
  assert.equal('formFingerprint' in saved(), false); assert.match($('message').textContent, /changed outside/);
  $('editor').dispatchEvent(new dom.window.Event('submit', { cancelable: true }));
  assert.equal(messages.at(-1).originalNode, undefined); assert.equal('expect' in messages.at(-1), false);
});

test('historical and removed nodes are read-only, with old text visible', t => {
  const { dom, snapshot, send, $ } = fixture(t);
  const target = { ...snapshot, nodes: [root], edges: [] };
  send({ type: 'snapshot', snapshot: target, diagnostics: [], readonly: true, diff: {
    base: snapshot, target, changes: [{ id: 'child', kind: 'removed', fields: [] }],
    added_edges: [], removed_edges: [['root', 'child']], base_ref: 'older', target_ref: 'newer',
  } });
  dom.window.document.querySelector('.card.removed').click();
  assert.equal($('body').disabled, false);
  assert.equal($('body').readOnly, true);
  assert.equal($('save').disabled, true); assert.equal($('delete').disabled, true);
  assert.equal($('new').disabled, true);
  assert.equal($('body').value, '# Child\n');
  assert.equal($('before-section'), null);
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
  assert.equal($('annotations-panel').hidden, true);
  assert.equal($('annotations-panel').contains($('editor')), false);
  const expanded = dom.window.document.querySelector('.expanded[data-node-id="child"]');
  assert.ok(expanded.contains($('editor')));
  const parent = dom.window.document.querySelector('[data-node-id="root"]');
  assert.equal(parent.querySelector('.distance-badge'), null);
  assert.equal(parent.dataset.minDistance, '0');
  assert.doesNotMatch($('focus-context').textContent, /distance|hops/i);
  const childCard = dom.window.document.querySelector('[data-node-id="grand"]');
  assert.equal(childCard.dataset.downstream, '2');
  assert.match(childCard.textContent, /2 downstream/);
  assert.match(childCard.querySelector('.downstream-badge').title, /Unique descendants at all depths/);
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
  assert.equal(messages.at(-1).originalNode, child);
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
  const target = { ...snapshot, nodes: [root, { ...child, body: '# Changed child' }] };
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
  assert.equal($('legend').textContent, 'manifestorequirementimplementation');
  assert.equal(saved().colorMode, 'type');
  assert.equal('retired' in target.nodes[1], false);
  assert.equal('retired' in card.dataset, false);
  assert.equal(card.querySelector('.retired-badge'), null);
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
  assert.deepEqual([...$('color-mode').options].map(o => o.textContent), ['Min. Distance to Manifesto', 'Max. Distance to Manifesto', 'Absolute influence', 'Relative influence', 'Log Absolute Influence', 'Log Relative Influence', 'Node type', 'Git/Revision Status']);
  const world = [...$('cards').children].map(c => [c.dataset.nodeId, c.style.left, c.style.top, c.style.height]);
  const camera = $('graph').style.transform, before = JSON.stringify(snapshot);
  assert.equal(card('child').style.getPropertyValue('--node-accent'), model.color('distance', child, 1));
  assert.match($('legend').textContent, /Manifesto · 0 hops1 hop2 hops/);
  $('color-mode').value = 'max-distance'; $('color-mode').dispatchEvent(new dom.window.Event('change'));
  assert.equal(card('child').style.getPropertyValue('--node-accent'), model.color('max-distance', child, 3));
  assert.equal(card('child').dataset.minDistance, '1');
  assert.equal(card('child').dataset.maxDistance, '3');
  assert.match($('legend').textContent, /3 hops/);
  assert.equal($('legend').querySelector('.legend-help'),null);
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

test('revision fills include changed manifesto, added/removed/source-only and unchanged nodes in overview and focus', t => {
  const { dom, $, snapshot, send, saved, messages } = fixture(t);
  const extra=(id,fields={})=>({...child,id,body:'# '+id,...fields});
  const old=extra('old'),added=extra('new'),source=extra('source'),plain=extra('plain');
  const base={...snapshot,nodes:[root,child,old,source,plain],edges:[...snapshot.edges,['root','old'],['root','source'],['root','plain']]};
  const target={...base,nodes:[root,child,added,source,plain],edges:base.edges.filter(e=>e[1]!=='old').concat([['root','new']])};
  const diff={base,target,changes:[{id:'root',kind:'changed'},{id:'child',kind:'changed'},{id:'old',kind:'removed'},{id:'new',kind:'added'}],source_affected:['source','child'],added_edges:[['root','new']],removed_edges:[['root','old']]};
  send({type:'snapshot',snapshot:target,diagnostics:[],readonly:false,diff});
  const card=id=>dom.window.document.querySelector(`[data-node-id="${id}"]`);
  const kinds={root:'changed',child:'changed',old:'removed',new:'added',source:'source-changed',plain:'unchanged'};
  const world=()=>[...$('cards').children].map(c=>[c.dataset.nodeId,c.style.left,c.style.top,c.style.width,c.style.height]);
  const before=JSON.stringify(target),positions=world(),camera=$('graph').style.transform;
  $('color-mode').value='git-revision';$('color-mode').dispatchEvent(new dom.window.Event('change'));
  for(const [id,kind] of Object.entries(kinds)) {
    assert.equal(card(id).style.getPropertyValue('--node-accent'),model.REVISION_COLORS[kind]);
    assert.ok(card(id).classList.contains('revision-colored'));
  }
  assert.deepEqual(world(),positions);assert.equal($('graph').style.transform,camera);
  assert.match($('legend').textContent,/A · Added.*M · Modified.*D · Deleted.*Linked source changed.*Same as base/);
  assert.doesNotMatch($('legend').textContent,/Manifesto|hops|No comparison/);
  assert.equal(saved().colorMode,'git-revision');
  assert.equal(card('source').querySelector('.git-corner'),null);
  assert.equal(card('plain').querySelector('.git-corner'),null);
  assert.equal(card('plain').querySelector('.retired-badge'), null);
  for(const [id,kind] of Object.entries(kinds)) {
    card(id).click();assert.equal(card(id).style.getPropertyValue('--node-accent'),model.REVISION_COLORS[kind]);
    assert.equal(card(id).style.width,id === 'root' ? `${model.manifestoDiameter(822,720)}px` : '860px');$('back').click();
  }
  send({type:'snapshot',snapshot:target,diagnostics:[],readonly:true,diff:{...diff,changes:[{id:'root',kind:'added'}],source_affected:[]}});
  assert.equal(card('root').style.getPropertyValue('--node-accent'),model.REVISION_COLORS.added);
  assert.equal(card('child').style.getPropertyValue('--node-accent'),model.REVISION_COLORS.unchanged);
  $('color-mode').value='distance';$('color-mode').dispatchEvent(new dom.window.Event('change'));
  assert.equal(card('root').style.getPropertyValue('--node-accent'),'#d3d3d3');
  assert.ok(!card('root').classList.contains('revision-colored'));
  assert.equal(JSON.stringify(target),before);
  assert.ok(messages.every(m=>['ready','rendered'].includes(m.type)));
});

test('revision mode switches and restores without disturbing a native draft, caret, camera or original contents', t => {
  const restored={colorMode:'git-revision',selected:'child',view:'focus',dirty:true,originalNode:child,
    cameras:{'focus:child':{x:40,y:-70,k:1.6}},draft:{body:'# Draft',sources:'[]',nodeType:'requirement',parents:['root']}};
  const { dom, $, saved, snapshot, send }=fixture(t,{restored});
  assert.equal($('color-mode').value,'git-revision');
  assert.match($('legend').textContent,/Workspace/);
  const body=$('body');body.focus();body.setSelectionRange(2,5,'backward');
  const camera=$('graph').style.transform;
  const diff={base:snapshot,changes:[{id:'root',kind:'changed'},{id:'child',kind:'changed'}],added_edges:[],removed_edges:[]};
  send({type:'snapshot',snapshot,diagnostics:[],readonly:false,diff});
  for(const mode of model.COLOR_MODES) {
    $('color-mode').value=mode;$('color-mode').dispatchEvent(new dom.window.Event('change'));
    assert.equal($('body'),body);assert.equal(body.value,'# Draft');assert.ok(body.contains(dom.window.document.activeElement));
    assert.deepEqual([body.selectionStart,body.selectionEnd,body.selectionDirection],[2,5,'backward']);
    assert.equal($('graph').style.transform,camera);assert.equal(saved().originalNode,child);
  }
  send({type:'snapshot',snapshot,diagnostics:[],readonly:false});
  assert.equal($('legend').textContent,'WorkspaceDraft');
  assert.equal(dom.window.document.querySelector('.card.expanded').style.getPropertyValue('--node-accent'),model.NEUTRAL_COLOR);
  assert.equal(saved().colorMode,'git-revision');
});

test('unsaved new and orphaned drafts use neutral revision fills, not invented Git statuses', t => {
  const { dom, $, snapshot, send }=fixture(t);
  $('color-mode').value='git-revision';$('color-mode').dispatchEvent(new dom.window.Event('change'));
  $('new').click();
  assert.equal(dom.window.document.querySelector('.card.expanded').style.getPropertyValue('--node-accent'),model.REVISION_COLORS.draft);
  assert.equal(dom.window.document.querySelector('.card.expanded .git-corner'),null);
  $('discard').click();
  dom.window.document.querySelector('[data-node-id="child"]').click();
  $('body').value='# Keep me';$('body').dispatchEvent(new dom.window.Event('input'));
  send({type:'snapshot',snapshot:{...snapshot,nodes:[root],edges:[]},diagnostics:[],readonly:false});
  assert.equal(dom.window.document.querySelector('.card.expanded').style.getPropertyValue('--node-accent'),model.REVISION_COLORS.draft);
  assert.equal($('body').value,'# Keep me');
});

test('distance switches and refreshed path bounds retain the same dirty form, caret, baseline and camera', t => {
  const { dom, $, card, snapshot, send, saved } = distanceFixture(t);
  card('child').click();
  const body = $('body'); body.value = '# Draft'; body.dispatchEvent(new dom.window.Event('input'));
  body.focus(); body.setSelectionRange(2, 5, 'backward');
  const camera = $('graph').style.transform;
  $('color-mode').value = 'max-distance'; $('color-mode').dispatchEvent(new dom.window.Event('change'));
  assert.equal($('body'), body);
  assert.ok(body.contains(dom.window.document.activeElement));
  assert.deepEqual([body.selectionStart, body.selectionEnd, body.selectionDirection], [2, 5, 'backward']);
  assert.equal(saved().originalNode, snapshot.nodes[1]);
  assert.equal($('graph').style.transform, camera);
  // Bounds come from the whole snapshot: b remains at distance two in this focus.
  assert.equal(card('b').dataset.maxDistance, '2');
  send({ type: 'snapshot', snapshot, diagnostics: [], readonly: false });
  assert.equal(saved().colorMode, 'max-distance');
  assert.equal(saved().originalNode, snapshot.nodes[1]);
  assert.equal($('body').value, '# Draft');
  assert.deepEqual([body.selectionStart, body.selectionEnd], [2, 5]);
});

test('maximum-distance preference restores without rebasing a draft or camera', t => {
  const { $, saved } = fixture(t, { restored: {
    colorMode: 'max-distance', selected: 'child', view: 'focus', dirty: true,
    originalNode: child, cameras: { 'focus:child': { x: 40, y: -70, k: 1.6 } },
    draft: { body: '# Restored', sources: '[]', nodeType: 'requirement', parents: ['root'] },
  } });
  assert.equal($('color-mode').value, 'max-distance');
  assert.equal(saved().colorMode, 'max-distance');
  assert.equal(saved().originalNode, child);
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
  assert.equal(dom.window.getComputedStyle(dom.window.document.querySelector('.card.manifesto')).height, '264px');
  assert.equal(dom.window.getComputedStyle(dom.window.document.querySelector('.card.requirement')).height, '112px');
  dom.window.document.querySelector('[data-node-id="child"]').click();
  const headline = $('title'), body = $('body'), card = headline.closest('.card'), width = card.style.width;
  body.value = '# Native draft'; body.dispatchEvent(new dom.window.Event('input')); body.focus(); body.setSelectionRange(2, 7);
  $('viewport').dispatchEvent(new dom.window.WheelEvent('wheel', { bubbles: true, cancelable: true, deltaY: -6000, clientX: 400, clientY: 250 }));
  assert.equal(Number($('viewport').dataset.scale), 2.5);
  assert.equal($('title'), headline); assert.equal($('body'), body);
  assert.equal(card.style.width, width);
  assert.equal(dom.window.getComputedStyle(headline).fontSize, '18px');
  assert.deepEqual([body.selectionStart, body.selectionEnd], [2, 7]);
  assert.equal(saved().originalNode, child);
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

function influenceFixture(t) {
  const f = fixture(t);
  const edges = [['root','a'],['root','b'],['root','c'],['a','left'],['a','right'],
    ['left','shared'],['right','shared'],['b','shared'],['shared','tail']];
  const nodes = [...new Set(edges.flat())].map(id => id === 'root' ? root : { ...child,id,
    type: id === 'tail' ? 'implementation' : 'requirement',body:`# ${id}\n`,path:`_specspec/${id}.md`,
    parents:edges.filter(([,b])=>b===id).map(([a])=>a) });
  f.snapshot = {...f.snapshot,nodes,edges};
  f.send({type:'snapshot',snapshot:f.snapshot,diagnostics:[],readonly:false});
  f.card = id => f.dom.window.document.querySelector(`[data-node-id="${id}"]`);
  f.mode = mode => { f.$('color-mode').value=mode;f.$('color-mode').dispatchEvent(new f.dom.window.Event('change')); };
  return f;
}

const influenceMiddleColor = mode => model.influenceColor(mode.startsWith('log-') ? Math.log(3)/Math.log(5) : 0.5);

test('logarithmic influence modes paint and persist alongside linear modes without disturbing the current draft', t => {
  const {dom,$,card,mode,saved}=influenceFixture(t);
  card('b').click();const body=$('body');body.value='# Compare scales';body.dispatchEvent(new dom.window.Event('input'));
  body.focus();body.setSelectionRange(2,7);const camera=$('graph').style.transform;
  for(const kind of ['log-absolute-influence','log-relative-influence']) {
    mode(kind);
    assert.equal(card('b').style.getPropertyValue('--node-accent'),influenceMiddleColor(kind));
    assert.notEqual(card('b').style.getPropertyValue('--node-accent'),'#e8d62c','Logarithmic and linear fills visibly differ for intermediate counts.');
    assert.equal(card('root').style.getPropertyValue('--node-accent'),'#d3d3d3');
    assert.equal($('legend').querySelector('.legend-help'),null);
    assert.ok($('legend').querySelector('.influence-gradient'));
    assert.equal(saved().colorMode,kind);assert.equal($('body'),body);assert.equal(body.value,'# Compare scales');
    assert.deepEqual([body.selectionStart,body.selectionEnd],[2,7]);assert.equal($('graph').style.transform,camera);
  }
  mode('absolute-influence');assert.equal(card('b').style.getPropertyValue('--node-accent'),'#e8d62c');
});

test('continuous influence colors and gradient legends retain full-revision domains in focused dirty forms', t => {
  const { dom,$,snapshot,send,card,mode,saved,messages } = influenceFixture(t);
  send({type:'snapshot',snapshot,diagnostics:[],readonly:false,diff:{base:snapshot,changes:[{id:'b',kind:'changed'}],added_edges:[],removed_edges:[]}});
  const before=JSON.stringify(snapshot);
  for (const kind of model.INFLUENCE_MODES) {
    mode(kind);
    assert.equal(card('a').style.getPropertyValue('--node-accent'),'#ba2208');
    assert.equal(card('b').style.getPropertyValue('--node-accent'),influenceMiddleColor(kind));
    assert.equal(card('tail').style.getPropertyValue('--node-accent'),'#4df884');
    assert.equal(card('root').style.getPropertyValue('--node-accent'),'#d3d3d3');
    assert.match(card('b').title,/Influence: 2 unique descendants/);
    assert.match($('legend').querySelector('.influence-gradient').style.backgroundImage,/linear-gradient\(to right in srgb,.*#ba2208.*#e8d62c.*#4df884/);
    assert.match($('legend').querySelector('.influence-gradient').getAttribute('aria-label'),/red highest.*green lowest/);
    assert.match($('legend').textContent,kind.endsWith('relative-influence')?/Group maximum.*Group minimum/:/Maximum.*0 descendants/);
    assert.equal($('legend').querySelector('.legend-help'),null);
    assert.equal(saved().colorMode,kind);
  }
  card('b').click();const body=$('body');body.value='# Retain draft';body.dispatchEvent(new dom.window.Event('input'));
  body.focus();body.setSelectionRange(2,6,'backward');
  const camera=$('graph').style.transform,baseline=saved().originalNode;
  const positions=()=>[...$('cards').children].map(c=>[c.dataset.nodeId,c.style.left,c.style.top,c.style.width,c.style.height]);
  const world=positions(),routes=[...$('edges').children].map(p=>p.getAttribute('d'));
  for (const kind of model.INFLUENCE_MODES) {
    mode(kind);
    assert.equal(card('b').style.getPropertyValue('--node-accent'),influenceMiddleColor(kind),'Hidden a/c remain part of both normalization domains.');
    assert.equal(card('b').querySelector('.git-corner').textContent,'M');
    assert.equal($('body'),body);assert.ok(body.contains(dom.window.document.activeElement));
    assert.equal(body.value,'# Retain draft');assert.deepEqual([body.selectionStart,body.selectionEnd,body.selectionDirection],[2,6,'backward']);
    assert.equal($('graph').style.transform,camera);assert.deepEqual(positions(),world);
    assert.deepEqual([...$('edges').children].map(p=>p.getAttribute('d')),routes);assert.equal(saved().originalNode,baseline);
  }
  assert.equal(JSON.stringify(snapshot),before);
  assert.ok(messages.every(m=>['ready','rendered'].includes(m.type)));
});

test('influence normalization refreshes when an unseen higher-influence branch disappears without rebasing a draft', t => {
  for (const kind of model.INFLUENCE_MODES) {
    const {dom,$,snapshot,send,card,mode,saved}=influenceFixture(t);
    mode(kind);card('b').click();const body=$('body');body.value='# Keep';body.dispatchEvent(new dom.window.Event('input'));
    body.focus();body.setSelectionRange(1,4);const camera=$('graph').style.transform,baseline=saved().originalNode;
    assert.equal(card('b').style.getPropertyValue('--node-accent'),influenceMiddleColor(kind));
    const nodes=snapshot.nodes.filter(n=>!['a','left','right'].includes(n.id)).map(n=>n.id==='shared'?{...n,parents:['b']}:n);
    const edges=snapshot.edges.filter(([a,b])=>nodes.some(n=>n.id===a)&&nodes.some(n=>n.id===b));
    send({type:'snapshot',snapshot:{...snapshot,nodes,edges},diagnostics:[],readonly:false});
    assert.equal(card('b').style.getPropertyValue('--node-accent'),'#ba2208');
    assert.equal($('body'),body);assert.equal(body.value,'# Keep');assert.deepEqual([body.selectionStart,body.selectionEnd],[1,4]);
    assert.equal(saved().originalNode,baseline);assert.equal(saved().colorMode,kind);assert.equal($('graph').style.transform,camera);
  }
});

test('influence uses independent base/target revisions even when the display union contains a cycle', t => {
  const {dom,$,snapshot,send}=fixture(t);
  const make=edges=>({...snapshot,edges,nodes:[...new Set(edges.flat())].map(id=>id==='root'?root:{...child,id,
    parents:edges.filter(([,b])=>b===id).map(([a])=>a),body:`# ${id}\n`})});
  const base=make([['root','a'],['a','old'],['old','b'],['b','leaf'],['root','peer'],['peer','peerLeaf']]);
  const target=make([['root','b'],['b','a'],['a','leaf'],['root','peer'],['peer','peerLeaf']]);
  const added_edges=target.edges.filter(e=>!base.edges.some(b=>JSON.stringify(b)===JSON.stringify(e)));
  const removed_edges=base.edges.filter(e=>!target.edges.some(b=>JSON.stringify(b)===JSON.stringify(e)));
  send({type:'snapshot',snapshot:target,diagnostics:[],readonly:true,diff:{base,target,added_edges,removed_edges,changes:[{id:'old',kind:'removed'}]}});
  const card=id=>dom.window.document.querySelector(`[data-node-id="${id}"]`);
  const mode=kind=>{$('color-mode').value=kind;$('color-mode').dispatchEvent(new dom.window.Event('change'));};
  for (const kind of model.INFLUENCE_MODES) {
    mode(kind);
    const absolute=kind.endsWith('absolute-influence'),logarithmic=kind.startsWith('log-');
    const oldRatio=absolute?(logarithmic?Math.log(3)/Math.log(4):2/3):1;
    const liveRatio=absolute?(logarithmic?Math.log(2)/Math.log(3):0.5):1;
    assert.equal(card('old').style.getPropertyValue('--node-accent'),model.influenceColor(oldRatio),'Removed nodes use base counts, maximum and cohorts.');
    assert.equal(card('a').style.getPropertyValue('--node-accent'),model.influenceColor(liveRatio),'Surviving nodes use target counts, maximum and cohorts.');
    card('old').click();
    assert.equal(card('old').style.getPropertyValue('--node-accent'),model.influenceColor(oldRatio));
    assert.equal(card('b').style.getPropertyValue('--node-accent'),'#ba2208','A live neighbor still uses target metrics in a removed node focus.');
    assert.equal($('save').disabled,true);
    $('back').click();
  }
});

test('all four influence preferences restore with recovered drafts and existing per-view cameras', t => {
  for (const colorMode of model.INFLUENCE_MODES) {
    const {$,saved}=fixture(t,{restored:{colorMode,selected:'child',view:'focus',dirty:true,originalNode:child,
      cameras:{'focus:child':{x:40,y:-70,k:1.6}},draft:{body:'# Restored',sources:'[]',nodeType:'requirement',parents:['root']}}});
    assert.equal($('color-mode').value,colorMode);assert.equal(saved().colorMode,colorMode);
    assert.equal($('body').value,'# Restored');assert.equal(saved().originalNode,child);
    assert.deepEqual({...saved().cameras['focus:child']},{x:40,y:-70,k:1.6});
  }
});

test('new and orphaned influence drafts are neutral rather than pretending to be zero-influence saved nodes', t => {
  for (const kind of model.INFLUENCE_MODES) {
    const {dom,$,snapshot,send,card,mode}=influenceFixture(t);
    mode(kind);$('new').click();
    assert.equal(dom.window.document.querySelector('.expanded').style.getPropertyValue('--node-accent'),model.NEUTRAL_COLOR);
    $('discard').click();card('b').click();$('body').value='# Copy this';$('body').dispatchEvent(new dom.window.Event('input'));
    const nodes=snapshot.nodes.filter(n=>n.id!=='b').map(n=>n.id==='shared'?{...n,parents:['left','right']}:n);
    send({type:'snapshot',snapshot:{...snapshot,nodes,edges:snapshot.edges.filter(e=>!e.includes('b'))},diagnostics:[],readonly:false,
      diff:{base:snapshot,changes:[{id:'b',kind:'removed'}],added_edges:[],removed_edges:snapshot.edges.filter(e=>e.includes('b'))}});
    assert.equal(dom.window.document.querySelector('.expanded').style.getPropertyValue('--node-accent'),model.NEUTRAL_COLOR);
    assert.equal($('body').value,'# Copy this');assert.equal($('save').disabled,true);
  }
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

test('refresh retains native textarea focus, selection and the original draft baseline', t => {
  const { dom, snapshot, send, $, saved } = fixture(t);
  dom.window.document.querySelector('[data-node-id="child"]').click();
  $('body').value = '# Draft in progress'; $('body').dispatchEvent(new dom.window.Event('input'));
  $('body').focus(); $('body').setSelectionRange(3, 8, 'backward');
  send({ type: 'snapshot', snapshot, diagnostics: [], readonly: false });
  assert.ok($('body').contains(dom.window.document.activeElement));
  assert.equal($('body').selectionStart, 3);
  assert.equal($('body').selectionEnd, 8);
  assert.equal($('body').selectionDirection, 'backward');
  assert.equal(saved().originalNode, child);
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

test('overview and focused cameras survive back, resume and refresh with the draft baseline', t => {
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
  send({ type: 'snapshot', snapshot, diagnostics: [], readonly: false });
  assert.deepEqual(cameraValue()['focus:child'], focused);
  assert.equal(saved().originalNode, child);
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

test('connections darken at low zoom while retaining screen strength and tangent joins without endpoint circles', t => {
  const { dom, $, messages } = fixture(t);
  assert.equal(parseFloat($('edges').style.getPropertyValue('--normal-edge-strength')), 70);
  $('zoom-out').click();
  assert.equal(parseFloat($('edges').style.getPropertyValue('--normal-edge-strength')), 70);
  $('zoom-out').click();
  assert.ok(parseFloat($('edges').style.getPropertyValue('--normal-edge-strength')) < 70);
  $('zoom-reset').click();
  assert.equal(parseFloat($('edges').style.getPropertyValue('--normal-edge-strength')), 70);
  const world = [...$('cards').children].map(card => [card.style.left, card.style.top]);
  const paths = [...$('edges').querySelectorAll('.link')];
  for (let n = 0; n < 60; n++) $('zoom-out').click();
  const k = Number($('viewport').dataset.scale);
  assert.equal(k, 0.12);
  assert.equal($('edges').querySelectorAll('circle, marker').length, 0);
  assert.equal(parseFloat($('edges').style.getPropertyValue('--normal-edge-strength')), 35);
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


test('Git A/M/D corners match semantic kinds in compact and expanded cards', t => {
  const {dom,snapshot,send,$}=fixture(t);
  const added={...child,id:'added',body:'# Added'},removed={...child,id:'removed',body:'# Deleted'};
  const base={...snapshot,nodes:[root,child,removed],edges:[['root','child'],['root','removed']]};
  const target={...snapshot,nodes:[root,{...child,body:'# Modified child'},added],edges:[['root','child'],['root','added']]};
  send({type:'snapshot',snapshot:target,readonly:false,diagnostics:[],diff:{base,target,changes:[{id:'child',kind:'changed'},{id:'added',kind:'added'},{id:'removed',kind:'removed'}],added_edges:[['root','added']],removed_edges:[['root','removed']]}});
  for(const [id,letter] of [['child','M'],['added','A'],['removed','D']]){
    const card=dom.window.document.querySelector(`[data-node-id="${id}"]`);
    assert.equal(card.querySelector('.git-corner').textContent,letter);assert.match(card.querySelector('.git-corner').getAttribute('aria-label'),/comparison base/);
  }
  assert.equal('retired' in dom.window.document.querySelector('[data-node-id="child"]').dataset,false);
  dom.window.document.querySelector('[data-node-id="child"]').click();
  assert.equal(dom.window.document.querySelector('.expanded .git-corner').textContent,'M');
  assert.equal($('title').textContent,'Modified child');
});

test('source-only impact never invents M or D corner letters', t => {
  const {dom,snapshot,send}=fixture(t);
  const target={...snapshot,nodes:[root,child]};
  send({type:'snapshot',snapshot:target,readonly:false,diagnostics:[],diff:{base:target,target,changes:[],added_edges:[],removed_edges:[],source_affected:['child']}});
  const card=dom.window.document.querySelector('[data-node-id="child"]');
  assert.ok(card.classList.contains('source-changed'));assert.equal(card.querySelector('.git-corner'),null);
  assert.equal(card.querySelector('.retired-badge'),null);assert.match(card.querySelector('.git-badge').textContent,/source changed/);
});

test('Git refresh changes presentation without rebasing a dirty draft or its native caret', t => {
  const {dom,snapshot,send,$,saved,messages}=fixture(t);
  dom.window.document.querySelector('[data-node-id="child"]').click();const body=$('body');
  body.value='# Dirty';body.dispatchEvent(new dom.window.Event('input'));body.focus();body.setSelectionRange(1,4,'backward');
  const camera=$('graph').style.transform,old=saved().originalNode;
  send({type:'snapshot',snapshot,readonly:false,diagnostics:[],diff:{base:snapshot,target:snapshot,changes:[{id:'child',kind:'changed'}],added_edges:[],removed_edges:[]}});
  assert.equal($('body'),body);assert.equal(body.value,'# Dirty');assert.deepEqual([body.selectionStart,body.selectionEnd,body.selectionDirection],[1,4,'backward']);
  assert.equal(saved().originalNode,old);assert.equal($('graph').style.transform,camera);
  assert.equal(dom.window.document.querySelector('.expanded .git-corner').textContent,'M');
  assert.ok(!messages.some(m=>['save','add','delete'].includes(m.type)));
});

test('shared Git CSS reads theme tokens with Dark Modern defaults, separate from edge ink', () => {
  const css=readFileSync(join(__dirname,'../media/graph.css'),'utf8');
  for(const text of ['--vscode-gitDecoration-addedResourceForeground, #81b88b','--vscode-editorGutter-modifiedBackground, #0078d4','--vscode-gitDecoration-deletedResourceForeground, #c74e39'])assert.ok(css.includes(text));
  assert.match(css,/\.git-corner \{[^}]*right: 10px; bottom: 8px/);
  assert.match(css,/\.card\.changed strong/);assert.match(css,/\.card\.removed h2/);
  assert.match(css,/--edge-added: #42b68b/);
});

function nativeFixture(t) {
  const f = fixture(t);
  f.document = { nodeId: 'child', path: child.path, version: 1, dirty: false };
  f.send({ type: 'snapshot', snapshot: f.snapshot, document: f.document, selectedId: 'child', diagnostics: [], readonly: false });
  return f;
}
test('native intermediate form records preserve actual empty input and permit repair without canonical membership', t => {
  const f=nativeFixture(t);f.$('body').value='';f.$('body').dispatchEvent(new f.dom.window.Event('input'));
  f.send({type:'document-status',document:{...f.document,version:2,dirty:true},editSequence:1});
  const partial={...child,body:'',sources_text:'[]',repairForm:true};
  f.send({type:'snapshot',snapshot:{...f.snapshot,valid:false,complete:false,nodes:[root],edges:[],inventory:[root.path,child.path],unreadable_paths:[child.path]},repair_forms:[partial],document:{...f.document,version:2,dirty:true},diagnostics:[{code:'SCHEMA',message:'Body must be non-empty'}],readonly:false});
  assert.equal(f.$('body').value,'');assert.equal(f.$('body').readOnly,false);assert.equal(f.$('save').disabled,false);
  assert.equal(f.$('delete').disabled,true);assert.match(f.$('message').textContent,/Graph INVALID/);
  assert.equal(f.$('sync-notice').hidden,true);
  f.$('body').value='# Repaired';f.$('body').dispatchEvent(new f.dom.window.Event('input'));
  assert.equal(f.messages.at(-1).type,'edit');assert.equal(f.messages.at(-1).body,'# Repaired');assert.equal(f.messages.at(-1).documentVersion,2);
});

test('native document forms send edits immediately; graph navigation opens the other node file', t => {
  const { dom, $, messages, saved } = nativeFixture(t);
  assert.equal($('title').textContent, 'Child'); assert.equal($('save').textContent, 'Save file');
  assert.equal($('new').disabled, true); assert.equal($('discard').hidden, true);
  $('body').value = '# Native typing'; $('body').dispatchEvent(new dom.window.Event('input'));
  const edit = messages.find(m => m.type === 'edit');
  assert.equal(edit.id, 'child'); assert.equal(edit.body, '# Native typing'); assert.equal(edit.documentVersion, 1);
  assert.equal(saved().dirty, true);
  dom.window.document.querySelector('[data-node-id="root"]').click();
  assert.equal(messages.at(-1).type, 'open-node'); assert.equal(messages.at(-1).id, 'root');
  assert.equal($('title').textContent, 'Child');
});
test('acknowledged native edits retain caret, while older acknowledgements cannot clear newer input', t => {
  const { dom, $, messages, saved, send, snapshot, document } = nativeFixture(t);
  const body = $('body'); body.value = '# First'; body.dispatchEvent(new dom.window.Event('input'));
  body.value = '# Second'; body.dispatchEvent(new dom.window.Event('input')); body.focus(); body.setSelectionRange(1, 4, 'backward');
  send({ type: 'document-status', document: { ...document, version: 2, dirty: true }, editSequence: 1 });
  assert.equal(saved().dirty, true);
  send({ type: 'document-status', document: { ...document, version: 3, dirty: true }, editSequence: 2 });
  assert.equal(saved().dirty, false); assert.equal(saved().draft, undefined);
  send({ type: 'snapshot', snapshot: { ...snapshot, nodes: [root, { ...child, body: '# Second' }] }, document: { ...document, version: 3, dirty: true }, diagnostics: [], readonly: false });
  assert.equal($('body'), body); assert.equal(body.value, '# Second');
  assert.deepEqual([body.selectionStart, body.selectionEnd, body.selectionDirection], [1, 4, 'backward']);
  body.dispatchEvent(new dom.window.KeyboardEvent('keydown', { key: 'z', ctrlKey: true, bubbles: true }));
  assert.equal(messages.at(-1).type, 'undo');
});
test('late native acknowledgements cannot relabel a newer peer snapshot or overwrite its form', t => {
  const f = nativeFixture(t);
  f.$('body').value = '# Mine'; f.$('body').dispatchEvent(new f.dom.window.Event('input'));
  f.send({ type: 'snapshot', snapshot: { ...f.snapshot, nodes: [root, { ...child, body: '# Peer' }] }, document: { ...f.document, version: 3 }, diagnostics: [], readonly: false });
  assert.equal(f.$('body').value, '# Mine');
  f.send({ type: 'document-status', document: { ...f.document, version: 2 }, editSequence: 1 });
  assert.equal(f.$('body').value, '# Peer'); assert.equal(f.saved().dirty, false);
  f.$('body').value = '# Peer + mine'; f.$('body').dispatchEvent(new f.dom.window.Event('input'));
  assert.equal(f.messages.at(-1).documentVersion, 3);
});
test('invalid native graph overlays retain editable form text for repair; managed Electron forms remain blocked', t => {
  const f = nativeFixture(t);
  f.$('body').value = ''; f.$('body').dispatchEvent(new f.dom.window.Event('input'));
  f.send({ type: 'sync-error', message: 'Invalid buffer' });
  assert.equal(f.$('body').disabled, false); assert.equal(f.$('body').readOnly, false);
  f.$('body').value = '# Repair'; f.$('body').dispatchEvent(new f.dom.window.Event('input'));
  assert.equal(f.messages.at(-1).type, 'edit');
  const managed = fixture(t); managed.dom.window.document.querySelector('[data-node-id="child"]').click();
  managed.send({ type: 'sync-error', message: 'Invalid file' }); assert.equal(managed.$('body').readOnly, true);
});
test('unapplied native recovery is visible/copyable, never auto-applied, and can be discarded explicitly', t => {
  const f = nativeFixture(t);
  f.send({ type: 'snapshot', snapshot: f.snapshot, document: { ...f.document, recoveredForm: {
    id: 'child', body: '# Unapplied recovered form', parents: ['root'], sources: '[]',
  } }, diagnostics: [], readonly: false });
  assert.equal(f.$('body').value, '# Unapplied recovered form'); assert.equal(f.saved().dirty, true);
  assert.equal(f.$('discard').hidden, false); assert.equal(f.$('discard').textContent, 'Discard recovered form');
  assert.ok(!f.messages.some(m => m.type === 'edit'));
  f.$('discard').click(); assert.equal(f.messages.some(m => m.type === 'discard-form'), true);
  assert.equal(f.$('body').value, child.body); assert.equal(f.saved().dirty, false);
});
