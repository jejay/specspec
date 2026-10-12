
export interface Diagnostic {
  code: string;
  message: string;
  severity: string;
  path?: string;
  node_id?: string;
}

export interface SpecNode {
  id: string;
  type: 'manifesto' | 'requirement' | 'implementation';
  retired: boolean;
  parents: string[];
  body: string;
  sources: { path: string; symbol?: string; blob?: string; mode?: 'strict' | 'expanding'; ranges?: [number, number][] }[];
  path: string;
}

export interface Snapshot {
  format_version: number | null;
  nodes: SpecNode[];
  edges: [string, string][];
  valid: boolean;
  changed_ids?: string[];
}

export interface GraphDiff {
  base: Snapshot;
  target: Snapshot;
  changes: { id: string; kind: string; fields: string[] }[];
  added_edges: [string, string][];
  removed_edges: [string, string][];
  base_ref: string;
  target_ref: string;
  source_changes: { path: string; implementation_ids: string[] }[];
  source_affected: string[];
}

export interface Envelope<T> {
  api_version: number;
  ok: boolean;
  result: T;
  diagnostics: Diagnostic[];
}

const shared: { invoke: typeof invoke } = require('./common/host/cli.cjs');

export function invoke<T>(command: string, prefix: string[], root: string, args: string[], input?: string,
  timeoutMs = 120_000, maxOutputBytes = 16 * 1024 * 1024): Promise<Envelope<T>> {
  return shared.invoke(command, prefix, root, args, input, timeoutMs, maxOutputBytes);
}
