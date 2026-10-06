const test = require('node:test');
const assert = require('node:assert/strict');
const m = require('../model.js');
const task = (id, duration = 1, dependsOn = []) => ({ id, duration, dependsOn, progress: 0, project: 'Test', title: id, owner: 'Sam' });
test('demo forecasts every task and both projects', () => {
  const rows = m.forecast(m.demo.start, m.demo.tasks);
  assert.equal(rows.length, 5); assert.equal(m.rollups(rows).length, 2);
  assert.equal(rows.find(t => t.id === 'design').start, '2026-04-08');
});
test('Friday successors and durations skip weekends', () => {
  const rows = m.forecast('2026-04-10', [task('a'), task('b', 2, ['a'])]);
  assert.equal(rows[1].start, '2026-04-13'); assert.equal(rows[1].end, '2026-04-14');
});
test('task order does not change dependency dates', () => {
  assert.equal(m.forecast('2026-04-06', [task('b', 1, ['a']), task('a')])[0].start, '2026-04-07');
});
test('cycles and missing prerequisites fail', () => {
  assert.throws(() => m.forecast('2026-04-06', [task('a', 1, ['b']), task('b', 1, ['a'])]), /cycle/);
  assert.throws(() => m.forecast('2026-04-06', [task('a', 1, ['missing'])]), /Missing/);
});
test('malformed dates, duplicate IDs, durations and progress fail', () => {
  assert.throws(() => m.day('2026-02-30'), /Invalid/);
  assert.throws(() => m.forecast('2026-04-06', [task('a'), task('a')]), /duplicate/);
  assert.throws(() => m.forecast('2026-04-06', [task('a', 0)]), /Invalid/);
  assert.throws(() => m.forecast('2026-04-06', [{...task('a'), progress: 101}]), /Progress/);
});
test('project rollups are unweighted means and latest finishes', () => {
  assert.deepEqual(m.rollups([{project:'P',end:'2026-04-10',progress:100},{project:'P',end:'2026-04-14',progress:0}]), [{project:'P',finish:'2026-04-14',progress:50,count:2}]);
});
