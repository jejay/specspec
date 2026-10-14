"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.invoke = invoke;
const node_child_process_1 = require("node:child_process");
function invoke(command, prefix, root, args, input, timeoutMs = 120000, maxOutputBytes = 16 * 1024 * 1024) {
    return new Promise((resolve, reject) => {
        const child = (0, node_child_process_1.spawn)(command, [...prefix, '--root', root, ...args], {
            cwd: root, shell: false, windowsHide: true,
        });
        const stdout = [];
        const stderr = [];
        let size = 0;
        let settled = false;
        let failure;
        let started = false;
        child.on('spawn', () => { started = true; });
        const uncertain = error => started && ['add', 'update', 'delete'].includes(args[0])
            ? new Error(`${error.message} The action outcome was not confirmed; inspect current project/recovery state before retrying.`) : error;
        const fail = (error) => {
            if (settled || failure)
                return;
            failure = error;
            clearTimeout(timer);
            // Wait for close before settling: Windows keeps the cwd locked until exit.
            child.kill();
        };
        const timer = setTimeout(() => fail(new Error('SpecSpec CLI timed out.')), timeoutMs);
        child.on('error', (error) => fail(new Error(`Cannot run ${command}: ${error.message}. Install the Python CLI or configure specspec.command/specspec.args.`)));
        for (const [stream, collection] of [[child.stdout, stdout], [child.stderr, stderr]]) {
            stream.on('data', (chunk) => {
                size += chunk.length;
                if (size > maxOutputBytes)
                    fail(new Error('SpecSpec response exceeds the output limit.'));
                else
                    collection.push(chunk);
            });
        }
        child.stdin.on('error', (error) => fail(error));
        child.stdin.end(input ?? '');
        child.on('close', (code) => {
            if (settled)
                return;
            settled = true;
            clearTimeout(timer);
            if (failure) {
                reject(uncertain(failure));
                return;
            }
            const output = Buffer.concat(stdout).toString('utf8');
            const errors = Buffer.concat(stderr).toString('utf8');
            let envelope;
            try {
                envelope = JSON.parse(output);
            }
            catch {
                reject(uncertain(new Error(errors || output || `CLI exited with ${code} without JSON.`)));
                return;
            }
            if (envelope.api_version !== 5 || typeof envelope.ok !== 'boolean' || !Array.isArray(envelope.diagnostics)) {
                reject(uncertain(new Error('Unsupported SpecSpec JSON API. This graph UI requires API 5; upgrade the Python CLI.')));
                return;
            }
            if (code !== 0 || !envelope.ok) {
                reject(new Error(envelope.diagnostics.map(d => `${d.code}: ${d.message}`).join('\n') || errors || 'CLI failed.'));
            }
            else
                resolve(envelope);
        });
    });
}
