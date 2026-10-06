const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const m = require('../model.js');
const data = () => structuredClone(m.demo);
const task = (id, duration = 1, dependsOn = [], earliest = null) => ({id,title:id,duration,dependsOn,earliest});
const plan = tasks => ({version:2,title:'Test workshop',start:'2026-04-06',tasks,baseline:null});
const dates = rows => new Map(rows.map(t=>[t.id,[t.start,t.end]]));

test('demo forecasts a complete workshop, with explicit earliest bound',()=>{
  const rows=m.forecast(data());assert.equal(rows.length,6);
  assert.deepEqual(dates(rows).get('materials'),['2026-04-08','2026-04-10']);
  assert.deepEqual(dates(rows).get('workshop'),['2026-04-20','2026-04-20']);
});
test('duration counts working days inclusively and Friday successors start Monday',()=>{
  const p={...plan([task('a'),task('b',2,['a'])]),start:'2026-04-10'};
  assert.deepEqual(dates(m.forecast(p)).get('b'),['2026-04-13','2026-04-14']);
  assert.deepEqual(dates(m.forecast({...p,tasks:[task('a',2)]})).get('a'),['2026-04-10','2026-04-13']);
});
test('weekend project and earliest bounds advance, and never precede project start',()=>{
  const p={...plan([task('a',1,[],'2026-04-11'),task('b',1,[],'2000-01-01')]),start:'2026-04-05'};
  const d=dates(m.forecast(p));assert.equal(d.get('a')[0],'2026-04-13');assert.equal(d.get('b')[0],'2026-04-06');
});
test('all prerequisites matter independently of input order',()=>{
  const p=plan([task('c',1,['a','b']),task('b',5),task('a',2)]);
  assert.equal(dates(m.forecast(p)).get('c')[0],'2026-04-13');
  assert.deepEqual(dates(m.forecast(p)),dates(m.forecast({...p,tasks:[...p.tasks].reverse()})));
});
test('UTC arithmetic crosses daylight-saving boundaries without shifting dates',()=>{
  const p={...plan([task('a'),task('b',1,['a'])]),start:'2026-03-06'};
  assert.deepEqual(dates(m.forecast(p)).get('b'),['2026-03-09','2026-03-09']);
  assert.equal(m.iso(m.day('2024-02-29')+1),'2024-03-01');
});
test('invalid calendar dates and date types are rejected',()=>{
  for(const value of ['2026-02-29','2026-04-31','2026-4-06','1999-12-31','2101-01-01',null,0])assert.throws(()=>m.day(value));
  assert.doesNotThrow(()=>m.day('2024-02-29'));
});
test('missing, self, repeated and circular prerequisites reject atomically',()=>{
  for(const tasks of [[task('a',1,['missing'])],[task('a',1,['a'])],[task('a'),task('b',1,['a','a'])],[task('a',1,['b']),task('b',1,['a'])]]){
    const raw=plan(tasks),before=JSON.stringify(raw);assert.throws(()=>m.validate(raw));assert.equal(JSON.stringify(raw),before);
  }
});
test('schema rejects duplicate IDs, malformed containers, names and durations',()=>{
  for(const raw of [null,[],{}, {...data(),version:3}, {...data(),tasks:null},plan([task('a'),task('a')]),plan([task('!')]),plan([{...task('a'),title:''}]),plan([task('a',0)]),plan([task('a',1.5)]),plan([task('a',61)]),plan([{...task('a'),dependsOn:'a'}]),{...data(),baseline:[]}])assert.throws(()=>m.validate(raw));
});
test('bounded deep graphs are iterative and reject excessive task counts',()=>{
  const tasks=Array.from({length:100},(_,i)=>task(`t${i}`,1,i?[`t${i-1}`]:[]));
  assert.equal(m.forecast(plan(tasks)).length,100);assert.throws(()=>m.validate(plan([...tasks,task('extra')])),/100/);
});
test('the 730-day combined horizon and final year bounds are enforced',()=>{
  const p=plan([task('a',1,[],m.iso(m.day('2026-04-06')+731))]);assert.throws(()=>m.validate(p),/730/);
  const current=data(), baseline={...data(),start:'2000-01-03'};baseline.tasks=[];
  assert.throws(()=>m.validate({...current,baseline}),/730/);
  assert.throws(()=>m.validate({...plan([task('a',60)]),start:'2100-12-31'}),/2100/);
});
test('baseline capture is explicit, deeply copied, and unchanged by later edits',()=>{
  const raw=data(),captured=m.captureBaseline(raw),original=JSON.stringify(captured.baseline);
  raw.tasks[0].title='mutated outside';raw.tasks[1].dependsOn.length=0;
  const changed=m.saveTask(captured,{...captured.tasks[1],duration:6});
  assert.equal(JSON.stringify(changed.baseline),original);assert.equal(JSON.stringify(captured.baseline),original);
  assert.equal(changed.baseline.tasks[0].title,'Shape the workshop');
  assert.equal(m.chart(changed).rows.find(r=>r.id==='workshop').delta,1);
});
test('added and removed tasks have an explicit baseline comparison',()=>{
  let p=m.captureBaseline(plan([task('a'),task('b')]));p=m.removeTask(p,'b');p=m.saveTask(p,task('c'));
  const rows=m.chart(p).rows;
  assert.equal(rows.find(r=>r.id==='b').current,null);assert.ok(rows.find(r=>r.id==='b').baseline);
  assert.equal(rows.find(r=>r.id==='c').baseline,null);assert.equal(rows.find(r=>r.id==='c').delta,null);
});
test('clearing and replacing baselines are separate model actions',()=>{
  const p=m.captureBaseline(data()),changed=m.saveTask(p,{...p.tasks[1],duration:6}),replaced=m.captureBaseline(changed);
  assert.equal(replaced.baseline.tasks[1].duration,6);assert.equal(p.baseline.tasks[1].duration,3);
  const cleared=m.clearBaseline(changed);assert.equal(cleared.baseline,null);assert.deepEqual(cleared.tasks,changed.tasks);
});
test('removing a referenced prerequisite fails without silently detaching it',()=>{
  const p=data(),before=JSON.stringify(p);assert.throws(()=>m.removeTask(p,'outline'),/required by/);
  assert.equal(JSON.stringify(p),before);assert.throws(()=>m.removeTask(p,'missing'),/no longer/);
});
test('JSON v2 round-trip preserves baseline, task identity and literal project text',()=>{
  const p=m.captureBaseline(data());p.title='<img src=x onerror=alert(1)>';
  assert.deepEqual(m.previewImport(JSON.stringify(p)).plan,m.validate(p));
  assert.equal(m.previewImport(JSON.stringify(p)).warnings.length,0);
  assert.equal(m.validate(p).title,p.title);
});
test('the real stage-two v1 export converts with explicit lossy warnings',()=>{
  const raw=fs.readFileSync(path.join(__dirname,'../history/personal-v1.json'),'utf8');
  const {plan:p,warnings}=m.previewImport(raw),rows=m.forecast(p);
  assert.equal(p.version,2);assert.equal(p.baseline,null);assert.equal(warnings.length,3);
  assert.deepEqual(dates(rows).get('clear'),['2026-04-06','2026-04-06']);
  assert.equal(p.tasks.find(t=>t.id==='paint').duration,3);assert.equal(p.tasks[0].earliest,'2026-04-04');
  assert.ok(p.tasks.every(t=>!('priority' in t)&&t.dependsOn.length===0));
  assert.equal(fs.readFileSync(path.join(__dirname,'../history/personal-v1.json'),'utf8'),raw);
});
test('invalid imports, huge files and unsupported legacy data reject without conversion',()=>{
  for(const raw of ['{',JSON.stringify({version:9}),'x'.repeat(1000001),JSON.stringify({version:1,title:'X',tasks:[{id:'a',title:'A',start:'2026-04-10',end:'2026-04-09',priority:'normal'}]})])assert.throws(()=>m.previewImport(raw));
  assert.throws(()=>m.previewImport(JSON.stringify({version:1,title:'X',tasks:[{id:'a',title:'A',start:'2026-01-01',end:'2026-08-01',priority:'normal'}]})),/60/);
});
test('empty plans and baseline-only plans are valid, finite and readable',()=>{
  const p=plan([]);assert.equal(m.chart(p).dayCount,1);assert.equal(m.chart(p).rows.length,0);
  const old=m.captureBaseline(plan([task('a')])),empty=m.removeTask(old,'a');assert.equal(m.chart(empty).rows.length,1);
});
test('save/validate/forecast/chart never mutate valid inputs or shared dependency arrays',()=>{
  const p=m.captureBaseline(data()),before=JSON.stringify(p);m.forecast(p);m.chart(p);m.validate(p);m.saveTask(p,{...p.tasks[1],duration:4});
  assert.equal(JSON.stringify(p),before);const copy=m.validate(p);copy.tasks[1].dependsOn.push('changed');assert.equal(JSON.stringify(p),before);
});
test('seeded DAGs agree with an independent slow calendar reference',()=>{
  let seed=2026;const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
  const next=n=>{while([0,6].includes(new Date(n*86400000).getUTCDay()))n++;return n;};
  for(let sample=0;sample<40;sample++){
    const tasks=[];for(let i=0;i<20;i++)tasks.push(task(`t${i}`,1+Math.floor(random()*7),tasks.filter(()=>random()<.15).map(t=>t.id)));
    const p=plan(tasks),reference=new Map();
    for(const t of tasks){const start=Math.max(m.day(p.start),...t.dependsOn.map(id=>next(reference.get(id)[1]+1)));let end=start;for(let n=1;n<t.duration;n++)end=next(end+1);reference.set(t.id,[start,end]);}
    for(const t of m.forecast({...p,tasks:[...tasks].reverse()}))assert.deepEqual([m.day(t.start),m.day(t.end)],reference.get(t.id));
  }
});
