/* Private presentation storage only; never a canonical graph write path.
 * Each window process merges its own updated projects into the file's current entries. */
const fs = require('node:fs');
const { dirname } = require('node:path');
const { randomUUID } = require('node:crypto');
const LIMIT = 32 * 1024 * 1024;
class PresentationStore {
  constructor(path, filesystem = fs) {
    this.path = path; this.fs = filesystem; this.projects = Object.create(null); this.changed = new Set();
    try { this.projects = this.read(); }
    catch (error) { this.error = `Presentation storage is protected: ${error.message} Move the file aside explicitly before retrying.`; }
  }
  read() {
    try {
      if (this.fs.statSync(this.path).size > LIMIT) throw new Error('Presentation file exceeds 32 MiB.');
      const value = JSON.parse(this.fs.readFileSync(this.path, 'utf8'));
      if (!value || Array.isArray(value) || typeof value !== 'object') throw new Error('Invalid presentation storage.');
      return Object.assign(Object.create(null), value);
    } catch (error) { if (error.code === 'ENOENT') return Object.create(null); throw error; }
  }
  get(scope) {
    // Another window process may have saved this project since this one started.
    if (!this.error && !this.changed.has(scope)) {
      try { const stored = this.read(); if (Object.hasOwn(stored, scope)) this.projects[scope] = stored[scope]; else delete this.projects[scope]; }
      catch { /* Keep the loaded entry; the next write reports the file. */ }
    }
    return this.projects[scope];
  }
  set(scope, value) {
    if (this.error) throw new Error(this.error);
    if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('Invalid presentation state.');
    const json = JSON.stringify(value);
    if (Buffer.byteLength(json, 'utf8') > 3 * 1024 * 1024) throw new Error('Project presentation exceeds 3 MiB.');
    const candidate = { ...this.projects, [scope]: JSON.parse(json) };
    if (Buffer.byteLength(JSON.stringify(candidate), 'utf8') > LIMIT) throw new Error('Presentation storage is full; retained drafts are preserved.');
    this.projects = Object.assign(Object.create(null), candidate); this.changed.add(scope); clearTimeout(this.timer);
    this.timer = setTimeout(() => this.save(), 200);
  }
  /** Writes now; a failure is reported once and the retained updates retry with the next write. */
  save() {
    try { this.flush(); } catch (error) { this.onError?.(`Presentation save failed: ${error.message} Retained changes retry with the next update.`); }
  }
  flush() {
    clearTimeout(this.timer); if (this.error || !this.changed.size) return;
    // Re-read so other windows' projects survive; only this window's updated entries replace theirs.
    const stored = this.read();
    for (const scope of this.changed) stored[scope] = this.projects[scope];
    const json = JSON.stringify(stored);
    if (Buffer.byteLength(json, 'utf8') > LIMIT) throw new Error('Presentation storage is full; retained drafts are preserved.');
    this.fs.mkdirSync(dirname(this.path), { recursive: true });
    const temp = `${this.path}.${process.pid}.${randomUUID()}.tmp`;
    try { this.fs.writeFileSync(temp, json, { encoding: 'utf8', mode: 0o600, flag: 'wx' }); this.fs.renameSync(temp, this.path); }
    catch (error) { try { this.fs.rmSync(temp, { force: true }); } catch { /* The next write uses a new name. */ } throw error; }
    this.changed.clear(); this.projects = stored;
  }
}
module.exports = { PresentationStore };
