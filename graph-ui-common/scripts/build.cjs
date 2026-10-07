/* Build once from shared sources; hosts receive self-contained runtime copies. */
const { build } = require('esbuild');
const { readFileSync, writeFileSync, mkdirSync, renameSync, readdirSync, copyFileSync } = require('node:fs');
const { join, resolve } = require('node:path');

async function buildGraph(media = resolve(__dirname, '../media'), runtime) {
  const root = resolve(__dirname, '..'); media = resolve(media);
  const result = await build({
    absWorkingDir: root, entryPoints: ['src/graph-vendor.js'], outfile: join(media, 'vendor/graph-vendor.js'),
    bundle: true, platform: 'browser', format: 'iife', globalName: 'SpecSpecVendor', target: ['es2020'],
    minify: true, legalComments: 'linked', metafile: true, write: false,
    footer: { js: 'if (typeof module === "object" && module.exports) module.exports = SpecSpecVendor; else globalThis.SpecSpecVendor = SpecSpecVendor;' },
  });
  function publish(path, content) {
    mkdirSync(resolve(path, '..'), { recursive: true });
    const temporary = `${path}.${process.pid}.tmp`;
    writeFileSync(temporary, content); renameSync(temporary, path);
  }
  for (const file of result.outputFiles) publish(file.path, file.contents);
  const packages = [...new Set(Object.keys(result.metafile.inputs)
    .filter(path => path.startsWith('node_modules/'))
    .map(path => { const parts = path.split('/'); return parts[1].startsWith('@') ? `${parts[1]}/${parts[2]}` : parts[1]; }))].sort();
  const notices = ['Third-party libraries bundled into graph-vendor.js.\nRebuild from graph-ui-common. No runtime network access.\n'];
  for (const name of packages) {
    const directory = join(root, 'node_modules', name);
    const metadata = JSON.parse(readFileSync(join(directory, 'package.json'), 'utf8'));
    notices.push(`\n=== ${name} ${metadata.version} (${metadata.license}) ===\n`, readFileSync(join(directory, 'LICENSE'), 'utf8'));
  }
  publish(join(media, 'vendor/THIRD_PARTY_NOTICES.txt'), notices.join('\n'));
  for (const name of readdirSync(join(root, 'media'))) {
    if (!/\.(js|css)$/.test(name)) continue;
    const from = join(root, 'media', name), to = join(media, name);
    if (from !== to) publish(to, readFileSync(from));
  }
  if (runtime) {
    mkdirSync(join(runtime, 'host'), { recursive: true });
    for (const name of readdirSync(join(root, 'host'))) copyFileSync(join(root, 'host', name), join(runtime, 'host', name));
    copyFileSync(join(root, 'view.cjs'), join(runtime, 'view.cjs'));
  }
  console.log(`Built shared graph assets with ${packages.length} dependency license notices.`);
}
module.exports = { buildGraph };
if (require.main === module) buildGraph().catch(error => { console.error(error); process.exitCode = 1; });
