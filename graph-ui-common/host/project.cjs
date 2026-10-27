const { lstat } = require('node:fs/promises');
const { dirname, join, resolve } = require('node:path');

async function findProjectRoot(start) {
  let current = resolve(start);
  if ((await lstat(current)).isFile()) current = dirname(current);
  const selected = current;
  while (true) {
    try { await lstat(join(current, '.specspec')); return current; }
    catch (error) { if (error.code !== 'ENOENT') throw error; }
    const parent = dirname(current);
    if (parent === current) break;
    current = parent;
  }
  return selected;
}
module.exports = { findProjectRoot };
