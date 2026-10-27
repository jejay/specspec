/* Spotlight arrivals are independent of immutable revision graphs and native saves. */
const fs = require('node:fs');
const { join } = require('node:path');

class AnnotationWatcher {
  constructor(root, changed, failed, filesystem = fs) {
    this.root = root; this.changed = changed; this.failed = failed; this.fs = filesystem; this.watches = new Map();
    this.paths = [root, join(root, '.specspec'), join(root, '.specspec', 'local'), join(root, '.specspec', 'local', 'annotations')];
    this.reconcile();
  }
  report(error) {
    if (!this.closed) this.failed(new Error(`Spotlight watching failed: ${error.message}. Use Refresh or enable optional polling.`));
  }
  reconcile() {
    if (this.closed) return;
    this.paths.forEach((path, index) => {
      let key;
      try { if (index === 0 || this.watches.has(this.paths[index - 1])) {
        const stat = this.fs.lstatSync(path); if (stat.isDirectory() && !stat.isSymbolicLink()) key = `${stat.dev}:${stat.ino}`;
      } }
      catch (error) { if (error.code !== 'ENOENT') this.report(error); }
      const previous = this.watches.get(path);
      if (key && previous?.key === key) return;
      previous?.watcher.close(); this.watches.delete(path);
      if (!key) return;
      try {
        const watcher = this.fs.watch(path, (_event, name) => {
          if (this.closed) return;
          const expected = ['.specspec', 'local', 'annotations'][index];
          if (name != null && (expected ? String(name) !== expected : !String(name).endsWith('.json'))) return;
          this.reconcile(); this.changed();
        });
        this.watches.set(path, { key, watcher });
        watcher.on('error', error => {
          if (this.watches.get(path)?.watcher === watcher) { watcher.close(); this.watches.delete(path); }
          this.report(error);
        });
      } catch (error) { this.report(error); }
    });
  }
  close() { this.closed = true; for (const { watcher } of this.watches.values()) watcher.close(); this.watches.clear(); }
}
module.exports = { AnnotationWatcher };
