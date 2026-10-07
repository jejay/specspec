/* Private presentation storage only; never a canonical graph write path. */
const { readFileSync, writeFileSync, renameSync, mkdirSync, statSync } = require('node:fs');
const { dirname } = require('node:path');
const { randomUUID } = require('node:crypto');
class PresentationStore {
  constructor(path) {
    this.path = path; this.projects = Object.create(null);
    try {
      if (statSync(path).size > 32 * 1024 * 1024) throw new Error('Presentation file exceeds 32 MiB.');
      const value = JSON.parse(readFileSync(path, 'utf8'));
      if (!value || Array.isArray(value) || typeof value !== 'object') throw new Error('Invalid presentation storage.');
      this.projects = Object.assign(Object.create(null), value);
    } catch (error) { if (error.code !== 'ENOENT') this.error = `Presentation storage is protected: ${error.message} Move the file aside explicitly before retrying.`; }
  }
  get(scope) { return this.projects[scope]; }
  set(scope, value) {
    if (this.error) throw new Error(this.error);
    if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('Invalid presentation state.');
    const json = JSON.stringify(value);
    if (Buffer.byteLength(json, 'utf8') > 3 * 1024 * 1024) throw new Error('Project presentation exceeds 3 MiB.');
    const candidate = { ...this.projects, [scope]: JSON.parse(json) };
    if (Buffer.byteLength(JSON.stringify(candidate), 'utf8') > 32 * 1024 * 1024) throw new Error('Presentation storage is full; no retained drafts were removed.');
    this.projects = Object.assign(Object.create(null), candidate); clearTimeout(this.timer);
    this.timer = setTimeout(() => { try { this.flush(); } catch (error) { this.error = `Cannot save presentation: ${error.message}`; this.onError?.(this.error); } }, 200);
  }
  flush() {
    clearTimeout(this.timer); if (this.error) return;
    mkdirSync(dirname(this.path), { recursive: true });
    const temp = `${this.path}.${process.pid}.${randomUUID()}.tmp`;
    writeFileSync(temp, JSON.stringify(this.projects), { encoding: 'utf8', mode: 0o600, flag: 'wx' }); renameSync(temp, this.path);
  }
}
module.exports = { PresentationStore };
