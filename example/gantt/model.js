/* Stage 01: portfolio calendar experiment, not a hosted service. */
(function (root) {
  'use strict';
  const DAY = 86400000;
  function day(value) {
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) throw Error('Use an ISO date.');
    const stamp = Date.parse(value + 'T00:00:00Z');
    if (!Number.isFinite(stamp) || new Date(stamp).toISOString().slice(0, 10) !== value) throw Error('Invalid calendar date.');
    return stamp / DAY;
  }
  const iso = n => new Date(n * DAY).toISOString().slice(0, 10);
  const weekday = n => ![0, 6].includes(new Date(n * DAY).getUTCDay());
  function next(n) { while (!weekday(n)) n++; return n; }
  function finish(n, duration) { for (let i = 1; i < duration; i++) n = next(n + 1); return n; }
  function forecast(start, tasks) {
    const first = next(day(start)), nodes = new Map(), result = new Map();
    for (const task of tasks) {
      if (!task.id || nodes.has(task.id) || !Number.isInteger(task.duration) || task.duration < 1 || task.duration > 100 || !Array.isArray(task.dependsOn)) throw Error('Invalid task or duplicate ID.');
      if (!Number.isFinite(task.progress) || task.progress < 0 || task.progress > 100) throw Error('Progress must be 0-100.');
      nodes.set(task.id, task);
    }
    for (const task of tasks) for (const parent of task.dependsOn) if (!nodes.has(parent)) throw Error('Missing prerequisite.');
    for (let pass = 0; pass < tasks.length; pass++) for (const task of tasks) {
      if (result.has(task.id) || !task.dependsOn.every(id => result.has(id))) continue;
      const begins = Math.max(first, ...task.dependsOn.map(id => next(day(result.get(id).end) + 1)));
      result.set(task.id, { ...task, start: iso(begins), end: iso(finish(begins, task.duration)) });
    }
    if (result.size !== tasks.length) throw Error('Dependency cycle.');
    return tasks.map(task => result.get(task.id));
  }
  function rollups(tasks) {
    const projects = new Map();
    for (const task of tasks) {
      const row = projects.get(task.project) || { project: task.project, finish: task.end, progress: 0, count: 0 };
      row.finish = row.finish > task.end ? row.finish : task.end;
      row.progress += task.progress; row.count++; projects.set(task.project, row);
    }
    return [...projects.values()].map(row => ({ ...row, progress: Math.round(row.progress / row.count) }));
  }
  const demo = { start: '2026-04-06', tasks: [
    { id: 'brief', title: 'Agree launch brief', project: 'Website relaunch', owner: 'Sam', duration: 2, dependsOn: [], progress: 100 },
    { id: 'design', title: 'Design the pages', project: 'Website relaunch', owner: 'Lee', duration: 4, dependsOn: ['brief'], progress: 25 },
    { id: 'build', title: 'Build and check', project: 'Website relaunch', owner: 'Sam', duration: 5, dependsOn: ['design'], progress: 0 },
    { id: 'space', title: 'Prepare the studio', project: 'Open studio', owner: 'Sam', duration: 3, dependsOn: [], progress: 50 },
    { id: 'invite', title: 'Invite visitors', project: 'Open studio', owner: 'Lee', duration: 2, dependsOn: ['space'], progress: 0 }
  ] };
  const api = { day, iso, forecast, rollups, demo };
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.GanttModel = api;
})(globalThis);
