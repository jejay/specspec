/* Locate the installed Code CLI without assuming one vendor installation layout. */
const { existsSync, readdirSync } = require('node:fs');
const { dirname, join, resolve } = require('node:path');
function codeCli(executable) {
  const root = dirname(executable);
  const direct = [join(root, 'resources/app/out/cli.js'), resolve(root, '../Resources/app/out/cli.js')].find(existsSync);
  if (direct) return direct;
  // Current Windows installs can keep app resources under a version/hash folder.
  const candidates = readdirSync(root, { withFileTypes: true }).filter(entry => entry.isDirectory())
    .map(entry => join(root, entry.name, 'resources/app/out/cli.js')).filter(existsSync);
  if (candidates.length !== 1) throw new Error('Cannot identify one installed Code CLI beside the selected executable; use a complete VS Code installation.');
  return candidates[0];
}
module.exports = { codeCli };
