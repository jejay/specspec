/* Portable project read coordination: saved files plus optional native overlays. */
const { isDeepStrictEqual } = require('node:util');
class SupersededReadError extends Error {
  constructor() { super('Documents changed during graph loading; retry with current text.'); this.name = 'SupersededReadError'; }
}
class ProjectReads {
  constructor(host) { this.host = host; this.queue = Promise.resolve(); this.listeners = new Set(); this.generation = 0; this.reads = new Map(); }
  run(operation) { const result = this.queue.then(operation); this.queue = result.catch(() => {}); return result; }
  idle() { return this.queue; }
  subscribe(listener) { this.listeners.add(listener); return { dispose: () => this.listeners.delete(listener) }; }
  changed() { this.generation++; this.listeners.forEach(listener => listener()); }
  documents() { return (this.host.documents?.() || []).filter(d => !d.closed); }
  stamp() { return this.documents().map(d => [d.path, d.text, d.version, d.dirty, d.eol]).sort(([a],[b]) => a.localeCompare(b)); }
  async request(edit, base, target) {
    if (this.disposed) throw new Error('Project documents are closed.');
    const value = { api_version: 6, op: edit ? 'plan' : 'read', ...(!target ? { documents: Object.fromEntries(this.documents().map(d => [d.path,d.text])) } : {}),
      ...(edit ? { edit } : {}), ...(base ? { base } : {}), ...(target ? { target } : {}),
      ...(!edit && base && !target ? { cache: true, ...(this.baseCache ? { base_cache: this.baseCache } : {}) } : {}) };
    const response = await this.host.cli(['api'], JSON.stringify(value));
    const { base_cache, ...loaded } = response.result;
    if (!this.disposed && base_cache && Buffer.byteLength(JSON.stringify(base_cache)) <= 3 * 1024 * 1024) this.baseCache = base_cache;
    return { ...loaded, diagnostics: response.diagnostics || [] };
  }
  async readGraph(base, allowInvalid = false, target) {
    const before = target ? [] : this.stamp(), generation = this.generation;
    const key = JSON.stringify([base,target,generation,before]);
    let pending = this.reads.get(key);
    if (!pending) {
      pending = this.request(undefined,base,target);
      if (this.reads.size < 32) this.reads.set(key,pending);
      const clear = () => { if (this.reads.get(key) === pending) this.reads.delete(key); };
      pending.then(clear,clear);
    }
    const result = await pending;
    if (this.disposed) throw new Error('Project documents are closed.');
    if (generation !== this.generation || (!target && !isDeepStrictEqual(before,this.stamp()))) throw new SupersededReadError();
    if (!allowInvalid && !result.snapshot.valid) throw new Error(result.diagnostics.map(d => `${d.code}: ${d.message}`).join('\n') || 'Invalid open specification documents.');
    return structuredClone(result);
  }
  async bootstrap() {
    for (let attempt = 0; ; attempt++) {
      const stamp = this.stamp(), generation = this.generation;
      try { return { result: await this.readGraph(undefined,true), stamp, generation }; }
      catch (error) {
        if (!(error instanceof SupersededReadError) || attempt >= 2 || this.disposed) throw error;
      }
    }
  }
  async initial(lease) {
    if (lease && !this.disposed && lease.generation === this.generation && isDeepStrictEqual(lease.stamp,this.stamp()) && lease.result.snapshot.valid) return structuredClone(lease.result);
    return this.readGraph();
  }
  dispose() { this.disposed = true; this.generation++; this.reads.clear(); this.baseCache = undefined; this.listeners.clear(); }
}
module.exports = { ProjectReads, SupersededReadError };
