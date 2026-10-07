const { resolve } = require('node:path');
const { copyFileSync } = require('node:fs');
const { buildGraph } = require('../../graph-ui-common/scripts/build.cjs');
const root = resolve(__dirname, '..');
buildGraph(resolve(root, 'media'), resolve(root, 'out/common')).then(() => {
  copyFileSync(resolve(root, 'src/host.js'), resolve(root, 'media/host.js'));
}).catch(error => { console.error(error); process.exitCode = 1; });
