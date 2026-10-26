/* Local VSIX only: never invokes publish or modifies an installed extension. */
const { resolve } = require('node:path');
const { mkdirSync } = require('node:fs');
const { createVSIX } = require('@vscode/vsce');
const metadata = require('../package.json');
const directory = resolve(__dirname, '..');
const output = resolve(directory, '../dist');
mkdirSync(output, { recursive: true });
createVSIX({
  cwd: directory,
  packagePath: resolve(output, `specspec-vscode-${metadata.version}.vsix`),
  dependencies: false,
}).catch(error => { console.error(error); process.exitCode = 1; });
