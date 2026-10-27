/* Directory notifications are hints, never a replacement for backend validation.
 * Watch the parent too: atomic saves and directory replacement invalidate watches
 * tied to old inodes on some platforms. No recursive fs.watch or implicit polling.
 */
const fs = require('node:fs');
const { join } = require('node:path');

class GraphWatcher {
  constructor(root, changed, failed, filesystem = fs) {
    this.root = root; this.directory = join(root, '.specspec');
    this.changed = changed; this.failed = failed; this.fs = filesystem;
    try {
      this.parent = this.fs.watch(root, (_event, name) => {
        if (this.closed) return;
        if (name != null && String(name) !== '.specspec') return;
        this.reconcile(); this.changed();
      });
      this.parent.on('error', error => this.report(error));
    } catch (error) { this.report(error); }
    this.reconcile();
  }
  report(error) { if (!this.closed) this.failed(new Error(`File watching failed: ${error.message}. Use Refresh or enable optional polling if needed.`)); }
  reconcile() {
    if (this.closed) return;
    let key;
    try {
      const stat = this.fs.lstatSync(this.directory);
      if (stat.isDirectory() && !stat.isSymbolicLink()) key = `${stat.dev}:${stat.ino}`;
    } catch (error) { if (error.code !== 'ENOENT') this.report(error); }
    if (key === this.key && this.nodes) return;
    this.nodes?.close(); this.nodes = undefined; this.key = key;
    if (!key) return;
    try {
      const watcher = this.fs.watch(this.directory, (event, name) => {
        if (this.closed || (name != null && String(name) === 'local')) return;
        if (event === 'rename') this.reconcile();
        this.changed();
      });
      this.nodes = watcher;
      watcher.on('error', error => {
        if (this.nodes === watcher) { watcher.close(); this.nodes = undefined; this.key = undefined; }
        this.report(error);
      });
    } catch (error) { this.report(error); }
  }
  close() { this.closed = true; this.parent?.close(); this.nodes?.close(); this.parent = this.nodes = undefined; }
}
module.exports = { GraphWatcher };
