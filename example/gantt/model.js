/* Stage 03: workshop forecasts. No DOM, storage, network, or external packages. */
(function (root) {
  'use strict';
  const DAY = 86400000, MAX_TASKS = 100, MAX_DURATION = 60, MAX_DAYS = 730;
  function day(value) {
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) throw Error('Use an ISO date (YYYY-MM-DD).');
    const stamp = Date.parse(value + 'T00:00:00Z');
    if (!Number.isFinite(stamp) || new Date(stamp).toISOString().slice(0, 10) !== value || value < '2000-01-01' || value > '2100-12-31') throw Error('Use a real calendar date between 2000 and 2100.');
    return stamp / DAY;
  }
  const iso = n => new Date(n * DAY).toISOString().slice(0, 10);
  const weekday = n => ![0, 6].includes(new Date(n * DAY).getUTCDay());
  function nextWorkday(n) { while (!weekday(n)) n++; return n; }
  function finish(n, duration) { for (let i = 1; i < duration; i++) n = nextWorkday(n + 1); return n; }
  function text(value, field) {
    if (typeof value !== 'string' || !value.trim() || value.length > 120) throw Error(`${field} must be 1–120 characters.`);
    return value.trim();
  }
  function object(value, field) { if (!value || typeof value !== 'object' || Array.isArray(value)) throw Error(`${field} must be an object.`); }
  function normalizePlan(raw) {
    object(raw, 'Plan'); text(raw.title, 'Plan title'); day(raw.start);
    if (!Array.isArray(raw.tasks) || raw.tasks.length > MAX_TASKS) throw Error(`Use at most ${MAX_TASKS} tasks.`);
    const ids = new Set();
    const tasks = raw.tasks.map(task => {
      object(task, 'Task');
      if (typeof task.id !== 'string' || !/^[a-zA-Z0-9_-]{1,40}$/.test(task.id) || ids.has(task.id)) throw Error('Use unique task IDs (1–40 letters, numbers, _ or -).');
      ids.add(task.id);
      if (!Number.isInteger(task.duration) || task.duration < 1 || task.duration > MAX_DURATION) throw Error(`Duration must be 1–${MAX_DURATION} whole workdays.`);
      if (!Array.isArray(task.dependsOn) || task.dependsOn.length > MAX_TASKS || task.dependsOn.some(id => typeof id !== 'string') || new Set(task.dependsOn).size !== task.dependsOn.length) throw Error('Prerequisites must be a list of distinct task IDs.');
      const earliest = task.earliest === '' || task.earliest == null ? null : task.earliest;
      if (earliest !== null) day(earliest);
      return { id: task.id, title: text(task.title, 'Task name'), duration: task.duration, earliest, dependsOn: [...task.dependsOn] };
    });
    for (const task of tasks) for (const id of task.dependsOn) {
      if (!ids.has(id)) throw Error(`Missing prerequisite ${id} for ${task.id}.`);
      if (id === task.id) throw Error(`Task ${id} cannot depend on itself.`);
    }
    return { title: raw.title.trim(), start: raw.start, tasks };
  }
  function schedule(plan) {
    const first = nextWorkday(day(plan.start)), nodes = new Map(plan.tasks.map(t => [t.id, t]));
    const children = new Map(plan.tasks.map(t => [t.id, []])), remaining = new Map(plan.tasks.map(t => [t.id, t.dependsOn.length]));
    for (const task of plan.tasks) for (const parent of task.dependsOn) children.get(parent).push(task.id);
    const ready = plan.tasks.filter(t => !remaining.get(t.id)).map(t => t.id), results = new Map();
    for (let index = 0; index < ready.length; index++) {
      const task = nodes.get(ready[index]);
      const begins = Math.max(first, task.earliest === null ? first : nextWorkday(day(task.earliest)), ...task.dependsOn.map(id => nextWorkday(day(results.get(id).end) + 1)));
      const end = iso(finish(begins, task.duration)); day(end);
      results.set(task.id, { ...task, dependsOn: [...task.dependsOn], start: iso(begins), end });
      for (const child of children.get(task.id)) { remaining.set(child, remaining.get(child) - 1); if (!remaining.get(child)) ready.push(child); }
    }
    if (results.size !== plan.tasks.length) throw Error('Dependency cycle: remove a circular prerequisite.');
    return plan.tasks.map(t => results.get(t.id));
  }
  function axis(plan, baseline, currentRows, baselineRows) {
    const first = Math.min(nextWorkday(day(plan.start)), ...(baseline ? [nextWorkday(day(baseline.start))] : []), ...currentRows.map(t => day(t.start)), ...baselineRows.map(t => day(t.start)));
    const last = Math.max(first, ...currentRows.map(t => day(t.end)), ...baselineRows.map(t => day(t.end)));
    if (last - first + 1 > MAX_DAYS) throw Error(`Current and baseline together must fit ${MAX_DAYS} calendar days.`);
    return { first, last, dayCount: last - first + 1 };
  }
  function validate(raw) {
    object(raw, 'File'); if (raw.version !== 2) throw Error('Expected workshop JSON version 2. Preview version 1 to convert it.');
    const plan = normalizePlan(raw), baseline = raw.baseline == null ? null : normalizePlan(raw.baseline);
    axis(plan, baseline, schedule(plan), baseline ? schedule(baseline) : []);
    return { version: 2, ...plan, baseline };
  }
  function forecast(raw) {
    const plan = normalizePlan(raw), rows = schedule(plan); axis(plan, null, rows, []); return rows;
  }
  function chart(raw) {
    const plan = validate(raw), current = schedule(plan), before = plan.baseline ? schedule(plan.baseline) : [];
    const old = new Map(before.map(t => [t.id, t])), now = new Map(current.map(t => [t.id, t]));
    const ids = [...now.keys(), ...[...old.keys()].filter(id => !now.has(id))];
    const rows = ids.map(id => ({ id, title: now.get(id)?.title || old.get(id).title, current: now.get(id) || null, baseline: old.get(id) || null, delta: now.has(id) && old.has(id) ? day(now.get(id).end) - day(old.get(id).end) : null }));
    return { ...axis(plan, plan.baseline, current, before), rows };
  }
  function captureBaseline(raw) { const plan = validate(raw); return validate({ ...plan, baseline: normalizePlan(plan) }); }
  function clearBaseline(raw) { return validate({ ...raw, baseline: null }); }
  function saveTask(raw, task) {
    const plan = validate(raw), exists = plan.tasks.some(t => t.id === task.id);
    return validate({ ...plan, tasks: exists ? plan.tasks.map(t => t.id === task.id ? task : t) : [...plan.tasks, task] });
  }
  function removeTask(raw, id) {
    const plan = validate(raw);
    if (!plan.tasks.some(t => t.id === id)) throw Error('Task no longer exists.');
    const references = plan.tasks.filter(t => t.dependsOn.includes(id));
    if (references.length) throw Error(`Cannot remove ${id}: required by ${references.map(t => t.id).join(', ')}. Edit those prerequisites first.`);
    return validate({ ...plan, tasks: plan.tasks.filter(t => t.id !== id) });
  }
  function convertV1(raw) {
    object(raw, 'Personal file'); text(raw.title, 'Plan title');
    if (!Array.isArray(raw.tasks) || raw.tasks.length > MAX_TASKS) throw Error(`Use at most ${MAX_TASKS} tasks.`);
    const tasks = raw.tasks.map(task => {
      object(task, 'Personal task'); const first = day(task.start), last = day(task.end);
      if (last < first || last - first + 1 > MAX_DAYS) throw Error('Invalid version-one manual range.');
      if (!['low', 'normal', 'high'].includes(task.priority)) throw Error('Invalid version-one priority.');
      let duration = 0; for (let n = first; n <= last; n++) if (weekday(n)) duration++;
      return { id: task.id, title: task.title, duration: Math.max(1, duration), earliest: task.start, dependsOn: [] };
    });
    const start = tasks.length ? tasks.map(t => t.earliest).sort()[0] : '2026-04-06';
    const plan = validate({ version: 2, title: raw.title, start, tasks, baseline: null });
    return { plan, warnings: [
      'Version 1 conversion: manual start becomes an earliest bound; end is replaced by a weekday-duration forecast.',
      'Weekends are excluded; weekend-only spans become one workday and may move to Monday. No prerequisites are inferred.',
      'Priority labels are discarded. This is not an exact preservation of the personal schedule.'
    ] };
  }
  function previewImport(rawText) {
    if (typeof rawText !== 'string' || rawText.length > 1000000) throw Error('Import must contain at most one million characters.');
    const raw = JSON.parse(rawText);
    object(raw, 'File');
    return raw.version === 1 ? convertV1(raw) : { plan: validate(raw), warnings: [] };
  }
  const demo = { version: 2, title: 'Build a better workshop', start: '2026-04-06', baseline: null, tasks: [
    { id: 'outline', title: 'Shape the workshop', duration: 2, earliest: null, dependsOn: [] },
    { id: 'materials', title: 'Prepare materials', duration: 3, earliest: null, dependsOn: ['outline'] },
    { id: 'signups', title: 'Open participant signups', duration: 5, earliest: null, dependsOn: ['outline'] },
    { id: 'setup', title: 'Set up the makerspace', duration: 2, earliest: null, dependsOn: ['materials'] },
    { id: 'dryrun', title: 'Run a rehearsal', duration: 1, earliest: null, dependsOn: ['setup', 'signups'] },
    { id: 'workshop', title: 'Welcome the participants', duration: 1, earliest: '2026-04-20', dependsOn: ['dryrun'] }
  ] };
  const api = { MAX_TASKS, MAX_DURATION, MAX_DAYS, day, iso, weekday, nextWorkday, validate, forecast, chart, captureBaseline, clearBaseline, saveTask, removeTask, previewImport, demo };
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.GanttModel = api;
})(globalThis);
