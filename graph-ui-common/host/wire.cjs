/* API 7 normalization. Complete revision graphs remain separate from display unions. */
function snapshot(value) {
  if (!value || !Array.isArray(value.nodes) || typeof value.valid !== 'boolean') throw new Error('Malformed graph snapshot.');
  return { ...value, edges: value.nodes.flatMap(n => {
    if (typeof n.id !== 'string' || !Array.isArray(n.parents) || n.parents.some(p => typeof p !== 'string')) throw new Error('Malformed node relationships.');
    return n.parents.map(p => [p, n.id]);
  }).sort(([a,b],[c,d]) => a < c ? -1 : a > c ? 1 : b < d ? -1 : b > d ? 1 : 0) };
}
function comparison(value, current) {
  const target = snapshot(current || value.target);
  if (!Array.isArray(value.before) || !Array.isArray(value.changes)) throw new Error('Malformed compact comparison.');
  const added = new Set(value.changes.filter(c => c.kind === 'added' || c.base_available === false).map(c => c.id));
  const previous = new Map(value.before.map(n => [n.id, n]));
  const base = new Map(target.nodes.filter(n => !added.has(n.id)).map(n => [n.id, n]));
  for (const [id, node] of previous) base.set(id, node);
  for (const c of value.changes) if (['changed','removed'].includes(c.kind) && !previous.has(c.id)) throw new Error('Incomplete previous node records.');
  const { before, ...rest } = value;
  return { ...rest, target, base: snapshot({ ...value.base, nodes: [...base.values()].sort((a,b) => a.id < b.id ? -1 : a.id > b.id ? 1 : 0) }) };
}
function expandResult(value) {
  if (!value || typeof value !== 'object') return value;
  if (value.snapshot) {
    const current = snapshot(value.snapshot);
    return { ...value, snapshot: current, ...(value.diff ? { diff: comparison(value.diff, current) } : {}) };
  }
  if (value.before) return comparison(value);
  if (value.nodes && typeof value.valid === 'boolean') return snapshot(value);
  return value;
}
module.exports = { snapshot, comparison, expandResult };
