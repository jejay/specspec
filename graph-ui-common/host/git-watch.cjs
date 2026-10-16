/* HEAD/ref notifications only; no index writes, recursive watch or polling.
 * Directory watches survive atomic ref replacement. Linked worktrees have a
 * private HEAD and shared refs. A refresh always resolves HEAD again in Python.
 */
const fs = require('node:fs');
const { execFileSync } = require('node:child_process');
const { join, resolve, relative, sep } = require('node:path');

class GitWatcher {
  constructor(root, changed, failed, filesystem = fs, execute = execFileSync) {
    this.root = root; this.changed = changed; this.failed = failed; this.fs = filesystem; this.execute = execute;
    this.watches = new Map();
    // Also notice init/replacement of .git in a formerly non-Git project root.
    try {
      this.parent = this.fs.watch(root, (_event, name) => {
        if (this.closed || (name != null && String(name) !== '.git')) return;
        this.discover(); this.changed();
      });
      this.parent.on('error', error => this.report(error));
    } catch (error) { this.report(error); }
    this.discover();
  }
  report(error) { if (!this.closed) this.failed(new Error(`Git watching failed: ${error.message}. Use Refresh or optional polling if needed.`)); }
  discover() {
    if (this.closed) return;
    try {
      const output = this.execute('git', ['-C', this.root, 'rev-parse', '--path-format=absolute', '--git-dir', '--git-common-dir'],
        { encoding: 'utf8', timeout: 3000, maxBuffer: 65536, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] });
      const paths = output.trim().split(/\r?\n/);
      if (paths.length !== 2) throw new Error('Git metadata discovery failed.');
      [this.directory, this.common] = paths.map(p => resolve(p));
    } catch (error) {
      this.directory = this.common = undefined;
      // Non-Git is a supported mode; the graph reports unavailable comparison.
      if (error.code === 'ENOENT' || error.signal || error.status !== 128) this.report(error);
    }
    this.reconcile();
  }
  reconcile() {
    if (this.closed) return;
    const desired = new Map();
    const add = (directory, name) => {
      if (!desired.has(directory)) desired.set(directory, new Set());
      desired.get(directory).add(name);
    };
    if (this.directory) {
      add(this.directory, 'HEAD'); add(this.directory, 'index');
      add(this.common, 'packed-refs'); add(this.common, 'refs');
      try {
        const head = this.fs.readFileSync(join(this.directory, 'HEAD'), 'utf8').trim();
        if (head.startsWith('ref: ')) {
          const ref = head.slice(5), parts = ref.split('/');
          // Only bounded project Git paths, not arbitrary text interpreted as a path.
          const target = resolve(this.common, ref), inside = relative(this.common, target);
          if (!ref.startsWith('refs/') || ref.includes('\\') || parts.some(p => !p || p === '.' || p === '..') ||
              inside.startsWith(`..${sep}`) || inside === '..' || parts.length > 128) throw new Error('Unsupported symbolic HEAD path.');
          let directory = this.common;
          for (const part of parts) { add(directory, part); directory = join(directory, part); }
        }
      } catch (error) { if (error.code !== 'ENOENT') this.report(error); }
    }
    for (const [directory, entry] of this.watches) {
      let key;
      try { const stat = this.fs.statSync(directory); if (stat.isDirectory()) key = `${stat.dev}:${stat.ino}`; }
      catch (error) { if (error.code !== 'ENOENT') this.report(error); }
      if (!desired.has(directory) || key !== entry.key) { entry.watcher.close(); this.watches.delete(directory); }
    }
    for (const [directory, names] of desired) {
      const existing = this.watches.get(directory);
      if (existing) { existing.names = names; continue; }
      try {
        const stat = this.fs.statSync(directory); if (!stat.isDirectory()) continue;
        const entry = { names, key: `${stat.dev}:${stat.ino}` };
        entry.watcher = this.fs.watch(directory, (_event, name) => {
          if (this.closed || (name != null && !entry.names.has(String(name)))) return;
          this.reconcile(); this.changed();
        });
        this.watches.set(directory, entry);
        entry.watcher.on('error', error => {
          entry.watcher.close(); this.watches.delete(directory); this.report(error);
        });
      } catch (error) { if (error.code !== 'ENOENT') this.report(error); }
    }
  }
  close() {
    this.closed = true; this.parent?.close(); this.parent = undefined;
    for (const entry of this.watches.values()) entry.watcher.close();
    this.watches.clear();
  }
}
module.exports = { GitWatcher };
