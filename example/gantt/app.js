/* Local read-only experiment. Project strings are always text. */
(() => {
  'use strict';
  const m = GanttModel, rows = m.forecast(m.demo.start, m.demo.tasks);
  const element = (tag, text, cls) => { const node = document.createElement(tag); if (text !== undefined) node.textContent = text; if (cls) node.className = cls; return node; };
  for (const project of m.rollups(rows)) document.getElementById('projects').append(element('p', `${project.project}: finish ${project.finish} · ${project.progress}% complete`, 'summary'));
  const chart = document.getElementById('chart'), first = m.day(m.demo.start), last = Math.max(...rows.map(t => m.day(t.end)));
  chart.style.width = `${240 + (last - first + 1) * 32}px`;
  const head = element('div', undefined, 'chart-row'); head.append(element('strong', 'Task', 'label'));
  for (let n = first; n <= last; n++) head.append(element('span', m.iso(n).slice(5), 'tick'));
  chart.append(head);
  for (const task of rows) {
    const row = element('div', undefined, 'chart-row'); row.append(element('span', task.title, 'label'));
    const track = element('div', undefined, 'track');
    const bar = element('span', `${task.duration}d`, 'bar'); bar.style.left = `${(m.day(task.start) - first) * 32}px`; bar.style.width = `${(m.day(task.end) - m.day(task.start) + 1) * 32}px`; bar.title = `${task.start} → ${task.end}`;
    track.append(bar); row.append(track); chart.append(row);
    const tr = element('tr'); for (const value of [`${task.title} / ${task.project}`, task.owner, task.start, task.end, `${task.progress}%`]) tr.append(element('td', value)); document.getElementById('tasks').append(tr);
  }
})();
