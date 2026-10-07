const { resolve } = require('node:path');
const { copyFileSync } = require('node:fs');
const { buildGraph } = require('../../graph-ui-common/scripts/build.cjs');
const root = resolve(__dirname, '..');
buildGraph(resolve(root, 'build/media'), resolve(root, 'build/common')).then(() => {
  for (const [from, to] of [
    ['renderer.js', 'build/media/host.js'], ['theme.css', 'build/media/host.css'],
    ['../branding/activity-icon.svg', 'build/media/specspec.svg'], ['../branding/app-icon.png', 'build/app-icon.png'],
    ['../LICENSE', 'build/LICENSE'],
  ]) copyFileSync(resolve(root, from), resolve(root, to));
}).catch(error => { console.error(error); process.exitCode = 1; });
