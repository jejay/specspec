const { resolve } = require('node:path');

/* Capture explicit executable paths in the launch directory, before project cwd. */
function resolveExecutable(command, launchDirectory) {
  // Bare executable names still use PATH (python, specspec, uvx).
  return /[\/\\]/.test(command) ? resolve(launchDirectory, command) : command;
}
module.exports = { resolveExecutable };
