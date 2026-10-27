/* Portable current-platform app; no installer, signing, publication or Python bundle. */
const { resolve } = require('node:path');
const metadata = require('../package.json');
const runtime = new Set(['package.json', 'main.cjs', 'preload.cjs', 'security.cjs', 'store.cjs', 'launch.cjs', 'build']);
function ignored(path) {
  const parts = path.split(/[\\/]/).filter(Boolean);
  return parts.length > 0 && !runtime.has(parts[0]);
}
async function packageApp() {
  if (!['win32', 'linux'].includes(process.platform)) throw new Error('Portable desktop packaging currently targets Windows and Linux. Use VS Code on macOS.');
  const { packager } = await import('@electron/packager');
  const paths = await packager({
    dir: resolve(__dirname, '..'),
    name: 'specspec-desktop',
    appVersion: metadata.version,
    out: resolve(__dirname, '../../dist/desktop'),
    overwrite: true,
    asar: false, // Keep the allowlisted local runtime directly inspectable in 0.1.
    prune: false, // No runtime npm dependencies: the shared adapter/renderer is built locally.
    ignore: ignored,
    icon: resolve(__dirname, '../../branding', process.platform === 'win32' ? 'app-icon.ico' : 'app-icon.png'),
    win32metadata: { CompanyName: 'specspec contributors', FileDescription: 'specspec-desktop', ProductName: 'specspec-desktop' },
  });
  for (const path of paths) console.log(`Portable specspec ${metadata.version}: ${path}`);
}
module.exports = { ignored };
if (require.main === module) packageApp().catch(error => { console.error(error); process.exitCode = 1; });
