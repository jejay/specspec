(() => {
  'use strict';
  const m = GanttModel, $ = id => document.getElementById(id), KEY = 'specspec-gantt-plan';
  let plan = m.validate(m.demo), blocked = false;
  const notice = text => { $('message').textContent = text; };
  const el = (tag, text, cls) => { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (cls) n.className = cls; return n; };
  try { const stored = localStorage.getItem(KEY); if (stored) plan = m.validate(JSON.parse(stored)); }
  catch (error) { blocked = true; notice(`Saved data/storage could not be loaded: ${error.message} Original bytes are untouched; this demo is session-only until an explicit reset.`); }
  function persist() {
    if (blocked) return notice('Session only: saved bytes are protected until you explicitly reset.');
    try { localStorage.setItem(KEY, JSON.stringify(plan)); notice('Saved in this browser. Export a file for backup.'); }
    catch (error) { notice(`Session only: storage failed (${error.message}). Export a file.`); }
  }
  function edit(task) {
    $('task-id').value = task?.id || ''; $('name').value = task?.title || '';
    $('start').value = task?.start || '2026-04-06'; $('end').value = task?.end || '2026-04-06'; $('priority').value = task?.priority || 'normal';
    $('delete').disabled = !task;
  }
  function draw() {
    $('plan-title').textContent = plan.title; $('tasks').replaceChildren(); $('chart').replaceChildren();
    if (!plan.tasks.length) { $('chart').append(el('p', 'No tasks yet. Add one below.')); return; }
    const first = Math.min(...plan.tasks.map(t => m.day(t.start))), last = Math.max(...plan.tasks.map(t => m.day(t.end)));
    $('chart').style.width = `${240 + (last - first + 1) * 32}px`;
    const header = el('div', undefined, 'chart-row'); header.append(el('strong', 'Task', 'label'));
    for (let n = first; n <= last; n++) header.append(el('span', m.iso(n).slice(5), 'tick')); $('chart').append(header);
    for (const task of plan.tasks) {
      const row = el('div', undefined, 'chart-row'); row.append(el('span', task.title, 'label')); const track = el('div', undefined, 'track');
      const bar = el('span', `${m.span(task)}d`, `bar ${task.priority}`); bar.style.left = `${(m.day(task.start) - first) * 32}px`; bar.style.width = `${m.span(task) * 32}px`; bar.title = `${task.start} → ${task.end}`; track.append(bar); row.append(track); $('chart').append(row);
      const tr = el('tr'); for (const v of [task.title, task.start, task.end, m.span(task), task.priority]) tr.append(el('td', v));
      const cell = el('td'), button = el('button', 'Edit'); button.addEventListener('click', () => edit(task)); cell.append(button); tr.append(cell); $('tasks').append(tr);
    }
  }
  function apply(candidate) { plan = m.validate(candidate); draw(); persist(); }
  $('editor').addEventListener('submit', event => {
    event.preventDefault();
    const id = $('task-id').value || `task-${Date.now()}`, task = { id, title: $('name').value, start: $('start').value, end: $('end').value, priority: $('priority').value };
    try { const tasks = plan.tasks.some(t => t.id === id) ? plan.tasks.map(t => t.id === id ? task : t) : [...plan.tasks, task]; apply({ ...plan, tasks }); edit(task); }
    catch (error) { notice(error.message); }
  });
  $('new').addEventListener('click', () => edit());
  $('delete').addEventListener('click', () => { try { apply({ ...plan, tasks: plan.tasks.filter(t => t.id !== $('task-id').value) }); edit(); } catch (error) { notice(error.message); } });
  $('export').addEventListener('click', () => {
    const raw = JSON.stringify(plan, null, 2); $('json').value = raw; const url = URL.createObjectURL(new Blob([raw], { type: 'application/json' })); const a = el('a'); a.href = url; a.download = 'personal-plan-v1.json'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  $('import').addEventListener('click', () => { try { const next = m.validate(JSON.parse($('json').value)); if (confirm('Replace this plan with the imported plan?')) { apply(next); edit(); } } catch (error) { notice(`Import rejected: ${error.message}`); } });
  $('reset').addEventListener('click', () => { if (confirm('Replace this session and stored plan with the demo?')) { blocked = false; apply(m.demo); edit(); } });
  draw(); edit();
})();
