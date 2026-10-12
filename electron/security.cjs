/* Fixed asset/protocol/message allowlists. No renderer-supplied executable or path. */
const APP_URL = 'specspec://app/index.html';
const ASSETS = new Set(['graph.js', 'graph.css', 'graph-model.js', 'graph-camera.js', 'host.js', 'host.css', 'specspec.svg', 'vendor/graph-vendor.js']);
const ACTIONS = new Set(['ready', 'rendered', 'client-error', 'refresh', 'compare', 'workspace', 'select-project', 'save', 'add', 'retire', 'restore', 'source-view', 'source-capture']);
function assetName(value) {
  try { const u = new URL(value); if (u.protocol !== 'specspec:' || u.hostname !== 'app' || u.port || u.username || u.password) return;
    const name = decodeURIComponent(u.pathname.slice(1)); if (name === 'index.html' || ASSETS.has(name)) return name;
  } catch { /* Malformed URL is not an asset. */ }
}
function trustedSender(event, contents) {
  return event.sender === contents && Boolean(event.senderFrame) && event.senderFrame === contents.mainFrame && event.senderFrame.url === APP_URL;
}
function validMessage(value) {
  try { return value && typeof value === 'object' && !Array.isArray(value) && ACTIONS.has(value.type)
    && Buffer.byteLength(JSON.stringify(value), 'utf8') <= 3 * 1024 * 1024; } catch { return false; }
}
const webPreferences = preload => ({ preload, contextIsolation: true, sandbox: true, nodeIntegration: false, webSecurity: true, allowRunningInsecureContent: false });
module.exports = { APP_URL, ASSETS, assetName, trustedSender, validMessage, webPreferences };
