const { lstat } = require('node:fs/promises');
const { dirname, join, resolve } = require('node:path');

async function findProjectRoot(start) {
  let current = resolve(start);
  if ((await lstat(current)).isFile()) current = dirname(current);
  while (true) {
    try { await lstat(join(current, '_specspec')); return current; }
    catch (error) { if (error.code !== 'ENOENT') throw error; }
    const parent = dirname(current);
    if (parent === current) break;
    current = parent;
  }
  throw new Error(`No _specspec directory found at or above ${start}. Select a SpecSpec project folder, or initialize it with specspec init first.`);
}
module.exports = { findProjectRoot };
