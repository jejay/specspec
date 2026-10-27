/* Build once from shared sources; hosts receive self-contained runtime copies. */
const { build } = require('esbuild');
const { readFileSync, writeFileSync, mkdirSync, renameSync, readdirSync, copyFileSync } = require('node:fs');
const { join, resolve, sep } = require('node:path');

/* esbuild reports paths relative to this workspace, including hoisted ../node_modules.
 * Retain notices for every actually bundled package/version, independent of layout. */
function dependencyNotices(inputs, root) {
  const directories = new Set();
  for (const input of inputs) {
    const full = resolve(root, input), marker = `${sep}node_modules${sep}`;
    const index = full.lastIndexOf(marker);
    if (index < 0) continue;
    const rest = full.slice(index + marker.length).split(sep);
    const count = rest[0].startsWith('@') ? 2 : 1;
    directories.add(join(full.slice(0, index + marker.length), ...rest.slice(0, count)));
  }
  const packages = [...directories].map(directory => {
    const metadata = JSON.parse(readFileSync(join(directory, 'package.json'), 'utf8'));
    const licenses = readdirSync(directory).filter(name => /^(?:licen[sc]e|copying)(?:[.-].*)?$/i.test(name)).sort();
    if (!licenses.length) throw new Error(`Missing bundled dependency license: ${metadata.name}`);
    return { key: `${metadata.name}@${metadata.version}`, text: `\n=== ${metadata.name} ${metadata.version} (${metadata.license}) ===\n` + licenses.map(name => readFileSync(join(directory, name), 'utf8')).join('\n') };
  }).sort((a, b) => a.key.localeCompare(b.key));
  return { count: packages.length, text: ['Third-party libraries bundled into graph-vendor.js.\nRebuild from graph-ui-common. No runtime network access.\n', ...packages.map(p => p.text)].join('\n') };
}

async function buildGraph(media = resolve(__dirname, '../media'), runtime) {
  const root = resolve(__dirname, '..'); media = resolve(media);
  const result = await build({
    absWorkingDir: root, entryPoints: ['src/graph-vendor.js'], outfile: join(media, 'vendor/graph-vendor.js'),
    bundle: true, platform: 'browser', format: 'iife', globalName: 'specspecVendor', target: ['es2020'],
    minify: true, legalComments: 'linked', metafile: true, write: false,
    footer: { js: 'if (typeof module === "object" && module.exports) module.exports = specspecVendor; else globalThis.specspecVendor = specspecVendor;' },
  });
  function publish(path, content) {
    mkdirSync(resolve(path, '..'), { recursive: true });
    const temporary = `${path}.${process.pid}.tmp`;
    writeFileSync(temporary, content); renameSync(temporary, path);
  }
  for (const file of result.outputFiles) publish(file.path, file.contents);
  const notices = dependencyNotices(Object.keys(result.metafile.inputs), root);
  publish(join(media, 'vendor/THIRD_PARTY_NOTICES.txt'), notices.text);
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
  console.log(`Built shared graph assets with ${notices.count} dependency license notices.`);
}
module.exports = { buildGraph, dependencyNotices };
if (require.main === module) buildGraph().catch(error => { console.error(error); process.exitCode = 1; });
