import { lstat } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';

/** Match the CLI's nearest-workspace discovery, including invalid nearest entries. */
export async function findProjectRoot(start: string): Promise<string> {
  let current = resolve(start);
  const selected = await lstat(current);
  if (selected.isFile()) current = dirname(current);
  while (true) {
    try {
      await lstat(join(current, '_specspec'));
      // Let the Python backend diagnose files/symlinks/invalid graphs. Never
      // silently fall back past an existing but invalid nearest workspace.
      return current;
    } catch (error) {
      const code = (error as NodeJS.ErrnoException).code;
      if (code !== 'ENOENT') throw error;
    }
    const parent = dirname(current);
    if (parent === current) break;
    current = parent;
  }
  throw new Error(`No _specspec directory found at or above ${start}. Select a SpecSpec project folder, or initialize it with specspec init first.`);
}

export interface Invocation {
  command: string;
  args: string[];
}

/** Development launches use an explicit interpreter instead of depending on PATH. */
export function resolveInvocation(configured: Invocation, developmentPython?: string,
  explicitlyConfigured = false): Invocation {
  if (developmentPython && !explicitlyConfigured) {
    return { command: developmentPython, args: ['-m', 'specspec'] };
  }
  return configured;
}
