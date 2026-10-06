/* Stage 02: independent manual dates, including weekends. */
(function (root) {
  'use strict';
  const DAY = 86400000;
  function day(value) {
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) throw Error('Use an ISO date.');
    const stamp = Date.parse(value + 'T00:00:00Z');
    if (!Number.isFinite(stamp) || new Date(stamp).toISOString().slice(0, 10) !== value || value < '2000-01-01' || value > '2100-12-31') throw Error('Invalid calendar date (2000–2100).');
    return stamp / DAY;
  }
  const iso = n => new Date(n * DAY).toISOString().slice(0, 10);
  function text(value, field) { if (typeof value !== 'string' || !value.trim() || value.length > 120) throw Error(`${field} must be 1–120 characters.`); return value.trim(); }
  function validate(raw) {
    if (!raw || raw.version !== 1) throw Error('Expected a version-one personal plan.');
    if (!Array.isArray(raw.tasks) || raw.tasks.length > 100) throw Error('Use up to 100 tasks.');
    const ids = new Set();
    const tasks = raw.tasks.map(t => {
      if (!t || typeof t.id !== 'string' || !/^[a-zA-Z0-9_-]{1,40}$/.test(t.id) || ids.has(t.id)) throw Error('Invalid or duplicate task ID.');
      ids.add(t.id); const start = day(t.start), end = day(t.end);
      if (end < start) throw Error('Finish must not precede start.');
      if (!['low', 'normal', 'high'].includes(t.priority)) throw Error('Invalid priority.');
      return { id: t.id, title: text(t.title, 'Task name'), start: t.start, end: t.end, priority: t.priority };
    });
    if (tasks.length && Math.max(...tasks.map(t => day(t.end))) - Math.min(...tasks.map(t => day(t.start))) >= 730) throw Error('The chart must fit 730 calendar days.');
    return { version: 1, title: text(raw.title, 'Plan title'), tasks };
  }
  const span = task => day(task.end) - day(task.start) + 1;
  const demo = { version: 1, title: 'Our home renovation', tasks: [
    { id: 'clear', title: 'Clear the room (weekend)', start: '2026-04-04', end: '2026-04-05', priority: 'high' },
    { id: 'paint', title: 'Paint the walls', start: '2026-04-08', end: '2026-04-12', priority: 'normal' },
    { id: 'shelves', title: 'Install shelves', start: '2026-04-18', end: '2026-04-19', priority: 'low' }
  ] };
  const api = { day, iso, validate, span, demo };
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.GanttModel = api;
})(globalThis);
