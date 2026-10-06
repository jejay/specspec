/* Native local UI. Canonical specifications are never mutated by the app. */
(() => {
  'use strict';
  const m = GanttModel, $ = id => document.getElementById(id), KEY = 'specspec-gantt-plan', WIDTH = 28;
  let plan = m.validate(m.demo), selected, editorOriginal = '', preview, protectedBytes, storageBlocked = false, importRead = 0;
  const el = (tag, text, cls) => { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (cls) n.className = cls; return n; };
  const notice = text => { $('message').textContent = text; };
  function download(text, filename) {
    const url = URL.createObjectURL(new Blob([text], { type: 'application/json' })), a = el('a');
    a.href = url; a.download = filename; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function persist() {
    if (storageBlocked) { $('storage-status').textContent = 'Session only: original stored bytes are protected. Preview/apply or explicitly reset to replace them.'; return; }
    try { localStorage.setItem(KEY, JSON.stringify(plan)); $('storage-status').textContent = 'Saved in this browser. Export JSON for a portable backup; this is not synchronization.'; }
    catch (error) { $('storage-status').textContent = `Session only: local storage failed (${error.message}). Export JSON before closing.`; }
  }
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      try { plan = m.validate(JSON.parse(raw)); }
      catch (error) {
        protectedBytes = raw; storageBlocked = true;
        $('storage-status').textContent = `Stored plan was not loaded (${error.message}). Original bytes are protected; this demo is session-only.`;
        $('preview-saved').hidden = false; $('backup-saved').hidden = false;
      }
    }
  } catch (error) { storageBlocked = true; $('storage-status').textContent = `Session only: local storage is unavailable (${error.message}). Export your work.`; }
  function formTask() {
    return { id: $('task-id').value, title: $('task-name').value, duration: Number($('task-duration').value), earliest: $('task-earliest').value || null, dependsOn: [...$('prerequisites').querySelectorAll('input:checked')].map(input => input.value) };
  }
  const dirty = () => JSON.stringify(formTask()) !== editorOriginal;
  const mayDiscard = () => !dirty() || confirm('Discard unsaved task edits?');
  const dirtySettings = () => $('plan-name').value !== plan.title || $('plan-start').value !== plan.start;
  const mayReplace = () => !(dirty() || dirtySettings()) || confirm('Discard unsaved task and plan-setting edits?');
  function loadEditor(id) {
    selected = id; const task = plan.tasks.find(t => t.id === id);
    $('task-id').value = task?.id || ''; $('task-name').value = task?.title || ''; $('task-duration').value = task?.duration || 1; $('task-earliest').value = task?.earliest || '';
    $('task-identity').textContent = task ? `Editing ${task.id}` : 'New task · ID assigned when saved'; $('delete-task').disabled = !task;
    $('prerequisites').replaceChildren();
    for (const candidate of plan.tasks.filter(t => t.id !== id)) {
      const label = el('label'), input = el('input'); input.type = 'checkbox'; input.value = candidate.id; input.checked = task?.dependsOn.includes(candidate.id) || false;
      label.append(input, el('span', candidate.title)); $('prerequisites').append(label);
    }
    if (!plan.tasks.some(t => t.id !== id)) $('prerequisites').append(el('span', 'No other tasks yet.', 'muted'));
    editorOriginal = JSON.stringify(formTask());
    for (const button of document.querySelectorAll('.task-label[data-id]')) button.classList.toggle('selected', button.dataset.id === id);
  }
  function select(id) { if (mayDiscard()) loadEditor(id); }
  function render() {
    $('plan-title').textContent = plan.title; $('clear-baseline').disabled = !plan.baseline;
    $('capture-baseline').textContent = plan.baseline ? 'Replace baseline' : 'Capture baseline';
    $('baseline-status').textContent = plan.baseline ? `Baseline retained: ${plan.baseline.tasks.length} saved tasks. Edits do not replace it.` : 'No baseline yet. Capture the saved plan before trying a change.';
    const chart = m.chart(plan), ends = chart.rows.filter(r => r.current).map(r => r.current.end).sort();
    $('schedule-summary').textContent = `${plan.tasks.length} tasks · ${m.iso(chart.first)} → ${ends.at(-1) || m.iso(chart.first)} · forecast, not appointments`;
    $('timeline').replaceChildren(); $('task-table').replaceChildren();
    // CSS changes the sticky label width on small screens, never task dates.
    const labelWidth = matchMedia('(max-width: 620px)').matches ? 180 : 220;
    $('timeline').style.width = `${labelWidth + chart.dayCount * WIDTH}px`;
    const header = el('div', undefined, 'timeline-row header'); header.append(el('span', 'Task / calendar days', 'task-label'));
    for (let n = chart.first; n <= chart.last; n++) {
      const tick = el('span', undefined, `day-tick${m.weekday(n) ? '' : ' weekend'}`); tick.title = m.iso(n);
      tick.append(el('small', ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][new Date(n * 86400000).getUTCDay()]), el('span', m.iso(n).slice(8))); header.append(tick);
    }
    $('timeline').append(header);
    if (!chart.rows.length) $('timeline').append(el('p', 'No tasks yet. Add your first task.', 'empty'));
    for (const row of chart.rows) {
      const line = el('div', undefined, `timeline-row${row.current ? '' : ' baseline-only'}`);
      const label = el(row.current ? 'button' : 'span', row.title, `task-label${row.current ? '' : ' removed'}${row.id === selected ? ' selected' : ''}`);
      if (row.current) { label.type = 'button'; label.dataset.id = row.id; label.setAttribute('aria-label', `Edit ${row.title}`); label.addEventListener('click', () => select(row.id)); }
      else label.title = 'Only in the baseline; removed from the current plan.';
      line.append(label); const track = el('div', undefined, 'track'); track.style.width = `${chart.dayCount * WIDTH}px`;
      for (let n = chart.first; n <= chart.last; n++) track.append(el('span', undefined, `day-cell${m.weekday(n) ? '' : ' weekend'}`));
      for (const [task, kind] of [[row.current,'current'],[row.baseline,'baseline']]) if (task) {
        const bar = el('span', `${task.duration}d`, `bar ${kind}`); bar.dataset.id = row.id; bar.style.left = `${(m.day(task.start) - chart.first) * WIDTH}px`; bar.style.width = `${(m.day(task.end) - m.day(task.start) + 1) * WIDTH}px`;
        bar.title = `${kind}: ${task.start} → ${task.end} (${task.duration} workdays)`; track.append(bar);
      }
      line.append(track); $('timeline').append(line);
      const tr = el('tr'); tr.dataset.id = row.id; const name = el('td');
      if (row.current) { const button = el('button', row.title, 'table-task'); button.addEventListener('click', () => select(row.id)); name.append(button); }
      else name.textContent = `${row.title} (baseline only)`;
      tr.append(name, el('td', row.current?.start || '—'), el('td', row.current?.end || '—'), el('td', row.baseline?.end || '—'));
      const delta = row.delta === null ? (row.current ? (plan.baseline ? 'Added' : 'No baseline') : 'Removed') : row.delta === 0 ? 'Unchanged' : `${row.delta > 0 ? '+' : ''}${row.delta}d`;
      tr.append(el('td', delta, row.delta > 0 ? 'later' : row.delta < 0 ? 'earlier' : '')); $('task-table').append(tr);
    }
  }
  function settings() { $('plan-name').value = plan.title; $('plan-start').value = plan.start; }
  function apply(next, message) { plan = m.validate(next); render(); persist(); notice(message); }
  $('plan-form').addEventListener('submit', event => {
    event.preventDefault(); try { apply({ ...plan, title: $('plan-name').value, start: $('plan-start').value }, 'Plan settings saved; forecast updated.'); settings(); }
    catch (error) { notice(error.message); }
  });
  $('task-form').addEventListener('submit', event => {
    event.preventDefault(); const task = formTask();
    if (!task.id) { let index = 1; while (plan.tasks.some(t => t.id === `task-${index}`)) index++; task.id = `task-${index}`; }
    try { const next = m.saveTask(plan, task); apply(next, 'Task saved. Forecast recalculated; baseline unchanged.'); loadEditor(task.id); }
    catch (error) { notice(error.message); }
  });
  $('new-task').addEventListener('click', () => { if (mayDiscard()) { loadEditor(); $('task-name').focus(); } });
  $('delete-task').addEventListener('click', () => {
    try { const next = m.removeTask(plan, selected); if (confirm('Remove this task from the current plan? The baseline stays unchanged.')) { apply(next, 'Task removed; baseline retained.'); loadEditor(); } }
    catch (error) { notice(error.message); }
  });
  $('capture-baseline').addEventListener('click', () => {
    try { if (!plan.baseline || confirm('Replace the existing baseline with the saved current plan?')) apply(m.captureBaseline(plan), 'Baseline captured from saved data. Unsaved task edits were not included.'); }
    catch (error) { notice(error.message); }
  });
  $('clear-baseline').addEventListener('click', () => { if (plan.baseline && confirm('Clear the baseline?')) apply(m.clearBaseline(plan), 'Baseline cleared explicitly.'); });
  function cancelPreview() { importRead++; preview = undefined; $('import-preview').hidden = true; }
  function showPreview(raw) {
    cancelPreview();
    try {
      const candidate = m.previewImport(raw), chart = m.chart(candidate.plan);
      preview = candidate.plan; $('import-json').value = raw;
      $('import-summary').textContent = `${preview.title} · ${preview.tasks.length} tasks · ${m.iso(chart.first)} → ${m.iso(chart.last)} · ${preview.baseline ? 'includes baseline' : 'no baseline'}. Current work is not changed yet.`;
      $('import-warnings').replaceChildren(...candidate.warnings.map(w => el('li', w)));
      if (!candidate.warnings.length) $('import-warnings').append(el('li', 'Valid version-two plan. Applying will replace the current plan and saved data.'));
      $('import-preview').hidden = false; notice('Import preview ready. Review it, then Apply or Cancel.');
    } catch (error) { notice(`Import rejected: ${error.message}`); }
  }
  $('import-form').addEventListener('submit', event => { event.preventDefault(); showPreview($('import-json').value); });
  $('import-json').addEventListener('input', cancelPreview);
  $('import-file').addEventListener('change', async () => {
    cancelPreview(); const request = importRead, file = $('import-file').files[0]; if (!file) return;
    try {
      if (file.size > 1000000) throw Error('File exceeds one million bytes.');
      const raw = await file.text(); if (request === importRead) showPreview(raw);
    } catch (error) { if (request === importRead) { cancelPreview(); notice(`Import rejected: ${error.message}`); } }
  });
  $('apply-import').addEventListener('click', () => {
    if (!preview || !mayReplace() || !confirm('Replace the current plan AND saved data with this preview? Download protected original bytes first if you need them.')) return;
    const next = m.validate(preview); storageBlocked = false; protectedBytes = undefined; $('preview-saved').hidden = true; $('backup-saved').hidden = true;
    apply(next, 'Imported plan applied explicitly.'); cancelPreview(); settings(); loadEditor(plan.tasks[0]?.id);
  });
  $('cancel-import').addEventListener('click', () => { cancelPreview(); notice('Import cancelled; current work unchanged.'); });
  $('export-plan').addEventListener('click', () => { const raw = JSON.stringify(plan, null, 2); $('import-json').value = raw; cancelPreview(); download(raw, 'workshop-plan-v2.json'); notice('Exported saved plan and baseline. Unsaved task edits are not included.'); });
  $('preview-saved').addEventListener('click', () => showPreview(protectedBytes));
  $('backup-saved').addEventListener('click', () => download(protectedBytes, 'protected-original-plan.json'));
  $('reset-demo').addEventListener('click', () => {
    if (!mayReplace() || !confirm('Replace the current plan, baseline, and stored bytes with the demo?')) return;
    storageBlocked = false; protectedBytes = undefined; $('preview-saved').hidden = true; $('backup-saved').hidden = true;
    apply(m.demo, 'Demo restored explicitly.'); cancelPreview(); settings(); loadEditor(plan.tasks[0]?.id);
  });
  window.addEventListener('beforeunload', event => { if (dirty() || dirtySettings()) { event.preventDefault(); event.returnValue = ''; } });
  matchMedia('(max-width: 620px)').addEventListener('change', render);
  settings(); render(); loadEditor(plan.tasks[0]?.id);
})();
