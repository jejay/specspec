const { resolve } = require('node:path');
const { copyFileSync } = require('node:fs');
const { buildGraph } = require('../../graph-ui-common/scripts/build.cjs');
const root = resolve(__dirname, '..');
buildGraph(resolve(root, 'media'), resolve(root, 'out/common')).then(() => {
  copyFileSync(resolve(root, 'src/host.js'), resolve(root, 'media/host.js'));
  copyFileSync(resolve(root, 'src/host.css'), resolve(root, 'media/host.css'));
  copyFileSync(resolve(root, '../branding/activity-icon.svg'), resolve(root, 'media/specspec.svg'));
  copyFileSync(resolve(root, '../branding/app-icon.png'), resolve(root, 'media/app-icon.png'));
}).catch(error => { console.error(error); process.exitCode = 1; });
