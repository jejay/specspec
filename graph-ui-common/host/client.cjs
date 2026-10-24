/* Project-scoped API transport. Files/refs are read afresh by each application request. */
const { spawn } = require('node:child_process');
const { invoke } = require('./cli.cjs');
const { expandResult } = require('./wire.cjs');
const LIMIT = 16 * 1024 * 1024;
const uncertain = (error, job) => job?.sent && ['annotation-create', 'annotation-flush'].includes(job.op)
  ? new Error(`${error.message} The action result needs verification; inspect project/recovery state before retrying.`) : error;

class Channel {
  constructor(command, prefix, root) {
    this.queue = []; this.parts = []; this.bytes = 0; this.output = 0; this.errors = [];
    this.child = spawn(command, [...prefix, '--root', root, 'api', '--stream'], { cwd: root, shell: false, windowsHide: true });
    this.child.on('spawn', () => { this.started = true; });
    this.child.stdout.on('data', chunk => this.data(chunk));
    this.child.stderr.on('data', chunk => {
      this.output += chunk.length;
      if (this.output > (this.active?.limit || LIMIT)) this.fail(new Error('SpecSpec response exceeds the output limit.'));
      else this.errors.push(chunk);
    });
    this.child.on('error', error => this.fail(new Error(`CLI launch failed for ${command}: ${error.message}. Install/configure the matching Python CLI.`)));
    this.child.stdin.on('error', error => this.fail(error));
    this.child.on('close', code => this.fail(new Error(Buffer.concat(this.errors).toString('utf8') || `SpecSpec API channel closed (${code}).`)));
  }
  request(value, timeout, limit) {
    if (this.closed) return Promise.reject(new Error('SpecSpec API channel is closed.'));
    if (this.queue.length >= 32) return Promise.reject(new Error('SpecSpec API request queue is full.'));
    const raw = Buffer.from(JSON.stringify(value) + '\n');
    if (raw.length > LIMIT + 1) return Promise.reject(new Error('Application request exceeds the 16 MiB input limit.'));
    return new Promise((resolve, reject) => {
      const job = { raw, op: value?.op, limit, resolve, reject };
      job.timer = setTimeout(() => {
        if (this.active === job) this.fail(new Error('SpecSpec CLI timed out.'));
        else { this.queue = this.queue.filter(j => j !== job); reject(new Error('SpecSpec CLI timed out before dispatch.')); }
      }, timeout);
      this.queue.push(job); this.pump();
    });
  }
  pump() {
    if (this.closed || this.active || !this.queue.length) return;
    const job = this.active = this.queue.shift(); this.output = 0; this.errors = [];
    job.sent = true;
    try { this.child.stdin.write(job.raw); } catch (error) { this.fail(error); }
  }
  data(chunk) {
    if (this.closed) return;
    this.output += chunk.length;
    if (!this.active) { this.fail(new Error('Unsolicited SpecSpec API output.')); return; }
    if (this.output > this.active.limit) { this.fail(new Error('SpecSpec response exceeds the output limit.')); return; }
    let offset = 0;
    while (offset < chunk.length && !this.closed) {
      const end = chunk.indexOf(10, offset), stop = end < 0 ? chunk.length : end;
      this.parts.push(chunk.subarray(offset, stop)); this.bytes += stop - offset;
      offset = stop + (end < 0 ? 0 : 1);
      if (end < 0) break;
      if (!this.active) { this.fail(new Error('Unsolicited SpecSpec API response frame.')); return; }
      let value;
      try {
        value = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(Buffer.concat(this.parts, this.bytes)));
        if (value?.api_version !== 7 || typeof value.ok !== 'boolean' || !Array.isArray(value.diagnostics))
          throw new Error('Unsupported SpecSpec JSON API. This graph UI requires the matching API 7 CLI.');
        if (value.ok) value = { ...value, result: expandResult(value.result) };
      } catch (error) { this.fail(new Error(`Invalid SpecSpec API response: ${error.message}`)); return; }
      this.parts = []; this.bytes = 0;
      const job = this.active; this.active = undefined; clearTimeout(job.timer);
      if (value.ok) job.resolve(value);
      else job.reject(new Error(value.diagnostics.map(d => `${d.code}: ${d.message}`).join('\n') || 'CLI failed.'));
      queueMicrotask(() => this.pump());
    }
  }
  fail(error) {
    if (this.closed) return;
    this.closed = true;
    for (const job of [this.active, ...this.queue].filter(Boolean)) {
      clearTimeout(job.timer); job.reject(this.started ? uncertain(error, job) : error);
    }
    this.active = undefined; this.queue = []; this.parts = []; this.errors = [];
    // EOF also reaches Windows venv redirector children; no idle interpreter is retained.
    this.child.stdin.end(); this.child.kill();
  }
  dispose() { this.fail(new Error('SpecSpec API channel disposed.')); }
}

class CliClient {
  constructor() { this.channels = new Map(); }
  invoke(command, prefix, root, args, input, timeout = 120000, maxOutput = LIMIT) {
    if (this.closed) return Promise.reject(new Error('Project CLI is closed.'));
    const signature = JSON.stringify([command, prefix, root]);
    if (signature !== this.signature) { this.clear(); this.signature = signature; }
    if (args.length !== 1 || args[0] !== 'api') return invoke(command, prefix, root, args, input, timeout, maxOutput);
    let value;
    try { value = JSON.parse(input); } catch { return Promise.reject(new Error('Invalid application JSON.')); }
    // Warm the independent preview channel during the initial authorized graph read.
    for (const lane of ['main', 'source']) {
      if (!this.channels.has(lane)) this.channels.set(lane, new Channel(command, prefix, root));
    }
    const lane = value?.op === 'source-view' ? 'source' : 'main';
    if (this.channels.get(lane).closed) this.channels.set(lane, new Channel(command, prefix, root));
    return this.channels.get(lane).request(value, timeout, maxOutput);
  }
  clear() { for (const channel of this.channels.values()) channel.dispose(); this.channels.clear(); }
  dispose() { this.closed = true; this.clear(); }
}
module.exports = { CliClient };
