import { spawn } from 'node:child_process';

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
  status: 'proposed' | 'accepted' | 'retired';
  parents: string[];
  body: string;
  sources: { path: string; symbol?: string }[];
  path: string;
}

export interface Snapshot {
  fingerprint: string;
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

export function invoke<T>(
  command: string, prefix: string[], root: string, args: string[], input?: string,
  timeoutMs = 120_000, maxOutputBytes = 16 * 1024 * 1024,
): Promise<Envelope<T>> {
  return new Promise((resolve, reject) => {
    const child = spawn(command, [...prefix, '--root', root, ...args], {
      cwd: root, shell: false, windowsHide: true,
    });
    const stdout: Buffer[] = [];
    const stderr: Buffer[] = [];
    let size = 0;
    let settled = false;
    let failure: Error | undefined;
    const fail = (error: Error) => {
      if (settled || failure) return;
      failure = error;
      clearTimeout(timer);
      // Wait for close before settling: Windows keeps the cwd locked until exit.
      child.kill();
    };
    const timer = setTimeout(() => fail(new Error('SpecSpec CLI timed out.')), timeoutMs);
    child.on('error', (error) => fail(new Error(
      `Cannot run ${command}: ${error.message}. Install the Python CLI or configure specspec.command/specspec.args.`,
    )));
    for (const [stream, collection] of [[child.stdout, stdout], [child.stderr, stderr]] as const) {
      stream.on('data', (chunk: Buffer) => {
        size += chunk.length;
        if (size > maxOutputBytes) fail(new Error('SpecSpec response exceeds the output limit.'));
        else collection.push(chunk);
      });
    }
    child.stdin.on('error', (error) => fail(error));
    child.stdin.end(input ?? '');
    child.on('close', (code) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      if (failure) { reject(failure); return; }
      const output = Buffer.concat(stdout).toString('utf8');
      const errors = Buffer.concat(stderr).toString('utf8');
      let envelope: Envelope<T>;
      try { envelope = JSON.parse(output) as Envelope<T>; }
      catch { reject(new Error(errors || output || `CLI exited with ${code} without JSON.`)); return; }
      if (envelope.api_version !== 1 || typeof envelope.ok !== 'boolean' || !Array.isArray(envelope.diagnostics)) {
        reject(new Error('Unsupported SpecSpec JSON API.')); return;
      }
      if (code !== 0 || !envelope.ok) {
        reject(new Error(envelope.diagnostics.map(d => `${d.code}: ${d.message}`).join('\n') || errors || 'CLI failed.'));
      } else resolve(envelope);
    });
  });
}
