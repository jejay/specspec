/* Trusted-host startup checks. No project mutation or implicit package installation. */
const { spawn } = require('node:child_process');
const { lstat, readdir } = require('node:fs/promises');
const { join } = require('node:path');

class CliUnavailableError extends Error {
  constructor(message) { super(message); this.code = 'CLI_UNAVAILABLE'; }
}
function probeCli(command, prefix, cwd, timeout = 10000) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, [...prefix, 'api', '--probe'], { cwd, shell: false, windowsHide: true });
    let output = '', failure, bytes = 0;
    const stop = error => { failure ||= error; child.kill(); };
    const timer = setTimeout(() => stop(new Error('The configured specspec CLI did not respond. Check its configuration and retry.')), timeout);
    child.on('error', error => stop(new CliUnavailableError(`Cannot launch ${command}: ${error.message}`)));
    for (const stream of [child.stdout, child.stderr]) stream.on('data', chunk => {
      bytes += chunk.length;
      if (bytes > 65536) stop(new Error('CLI availability response exceeds its limit.'));
      else output += chunk.toString('utf8');
    });
    child.stdin.on('error', error => stop(error)); child.stdin.end();
    child.on('close', code => {
      clearTimeout(timer);
      if (failure) { reject(failure); return; }
      if (code !== 0) {
        reject(/No module named ['"]?specspec|ModuleNotFoundError.*specspec/i.test(output)
          ? new CliUnavailableError(output.trim()) : new Error(/No such option.*--probe/.test(output)
            ? 'The installed specspec CLI is older than this UI. Update the CLI and retry.'
            : output.trim() || `CLI availability check failed (${code}).`));
      } else {
        let response;
        try { response = JSON.parse(output); } catch { reject(new Error('The configured command is not a compatible specspec CLI. Update the CLI to match this UI.')); return; }
        if (!response || typeof response !== 'object' || Array.isArray(response) || response.api_version !== 7 || response.ok !== true || !Array.isArray(response.diagnostics) || !Array.isArray(response.result?.features) ||
            !['stdin-body', 'project-init', 'nested-local-state'].every(feature => response.result?.features?.includes(feature))) {
          reject(new Error('The specspec CLI and UI are incompatible. Update both before opening this project.')); return;
        }
        resolve();
      }
    });
  });
}
async function inspectProject(root) {
  const path = join(root, '.specspec');
  let stat;
  try { stat = await lstat(path); }
  catch (error) { if (error.code === 'ENOENT') return { kind: 'initialize', root }; throw error; }
  if (!stat.isDirectory() || stat.isSymbolicLink()) return { kind: 'graph', root };
  const entries = await readdir(path);
  if (entries.some(name => name !== 'local')) return { kind: 'graph', root };
  if (entries.includes('local')) {
    const local = join(path, 'local'), info = await lstat(local);
    if (!info.isDirectory() || info.isSymbolicLink()) return { kind: 'graph', root };
    if ((await readdir(local)).some(name => name === 'lock' || name === 'journal.json' || name.startsWith('stage-')))
      throw new Error('Initialization was interrupted. Run specspec recover in this directory before retrying.');
  }
  return { kind: 'initialize', root };
}
module.exports = { CliUnavailableError, probeCli, inspectProject };
