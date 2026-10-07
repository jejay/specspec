const shared: { findProjectRoot(start: string): Promise<string> } = require('./common/host/project.cjs');

/** Match the CLI's nearest-workspace discovery, including invalid nearest entries. */
export const findProjectRoot = shared.findProjectRoot;

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
