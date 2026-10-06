const { build } = require('esbuild');
const { readFileSync, writeFileSync, mkdirSync, renameSync } = require('node:fs');
const { join, resolve } = require('node:path');

(async () => {
  const root = resolve(__dirname, '..');
  const result = await build({
    absWorkingDir: root, entryPoints: ['src/graph-vendor.js'], outfile: 'media/vendor/graph-vendor.js',
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
  const notices = ['Third-party libraries bundled into graph-vendor.js.\nRebuild with npm run compile. No runtime network access.\n'];
  for (const name of packages) {
    const directory = join(root, 'node_modules', name);
    const metadata = JSON.parse(readFileSync(join(directory, 'package.json'), 'utf8'));
    notices.push(`\n=== ${name} ${metadata.version} (${metadata.license}) ===\n`, readFileSync(join(directory, 'LICENSE'), 'utf8'));
  }
  mkdirSync(join(root, 'media/vendor'), { recursive: true });
  publish(join(root, 'media/vendor/THIRD_PARTY_NOTICES.txt'), notices.join('\n'));
  console.log(`Bundled graph libraries with ${packages.length} license notices.`);
})().catch(error => { console.error(error); process.exitCode = 1; });
