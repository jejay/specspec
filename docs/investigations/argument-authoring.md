# Argument-first authoring and the retained UI seam

The [direct-authoring intention](../../_specspec/rgGL5FY=.md) and
[message choice](../../_specspec/BKekD_o=.md) separate ordinary invocation
arguments from bulk integration transport. [Implementation](../../_specspec/Fy-_P9A=.md)
links the parser, tests and maintained examples. See the [command guide](../cli.md)
and [coherent editing grammar](../invalid-graphs.md#one-coherent-multi-node-change).
[Editing-chain verification](editing-chains.md) records the current composition
implementation and checks.

## Current interface

- Init/add/update take repeatable `-m/--message`. One argument is exact literal
  text; repeated arguments join with two LF characters without trimming or Git
  message cleanup. No implicit editor or backslash escape expansion is involved.
- Add/update/delete steps combine directly in one invocation and transaction.
  `add --as NAME` and `--parent '$NAME'` provide ephemeral new-node references,
  including forward declarations. Read/init/recovery/API commands stay standalone.
- Explicit hidden `--body FILE|-` on init/add/update retains bulk UTF-8 body input.
  Chains can use body files and at most one stdin body. Missing/mixed body sources
  fail before input reads or writes. Positional init payloads are rejected; there
  is no separate JSON batch-plan input or `apply` command.
- Managed UI add/update still use `--body -`. Reviewed deletion plans and the
  API-7 one-shot/stream channels retain their existing stdin contracts. No host
  product code or persistence ownership changes. The native test fixture's init
  bootstrap uses explicit integration `--body -`.
- API and canonical node format remain 7. All edits retain the existing schema,
  transaction, consent, alias, dry-run and optional whole-candidate validity rules.

## Input and platform boundaries

A shell-free Windows Python subprocess probe preserved multiline CRLF text,
Unicode, quotes, backslashes, dollar signs and backticks exactly. A 30,000-character
ASCII argument launched; a 32,768-character argument and a 1 MiB argument failed
before Python started. These are observations for this environment, not portable
payload guarantees. The actual CLI regression repeats Unicode/CRLF argument input
with ASCII/cp1252 output configuration and checks canonical saved bytes.

[CreateProcessW](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw)
limits the entire command line to 32,767 UTF-16 units including its terminator;
[cmd.exe](https://learn.microsoft.com/en-us/troubleshoot/windows-client/shell-experience/command-line-string-limitation)
has an 8,191-character limit. Executable paths, other options and quoting count.
Unix systems have their own argument/environment bounds. Repeated options cannot
remove aggregate limits, and argument text can appear in history/process listings.
Shell quoting is a caller responsibility; parent aliases use Bash single quotes.
PowerShell native argument behavior varies with version/passing mode. These shell
variants and physical Linux/macOS execution have not all been qualified here.

The retained bulk path avoids shrinking the existing 1 MiB document/16 MiB request
limits. A real subprocess regression supplies a 128 KiB body on integration stdin;
there is no automatic truncation, fallback, splitting or mutation replay.

## Maintained corpus and checks

All eight independent Gantt commits/refs were reconstructed externally, preserving
historical identities, meaningful redirects, app bytes and spec-before-code order.
The 123 real CLI executions include 45 literal `-m` body payloads and no stdin
payloads. The independent receipt oracle reconstructs bodies from arguments.
Source anchors, receipts, ledger, bundle and tracked snapshot were refreshed
together. Every retained revision validates; the three historical model stages
pass. Existing manual clones, earlier diagnostics and unrelated SpecSpec history
remain preserved.

Focused tests cover literal filename/dash/option-like text, Markdown/control text,
Unicode/EOL/whitespace, repeated/omitted/empty/conflicting messages, UTF-8/join
budgets, ASCII-safe primary help, chained aliases/dry-run/rejection, relative bulk
files, retained stdin and actual argv subprocesses. Existing invalid-graph and
transaction tests exercise the unchanged batch writer.

The argument-message baseline at commit `0f9f75e` passed **609 Python tests**,
254 shared UI tests, 46 VS Code and nine Electron tests, plus Ruff/format checks.
Its complete installed Windows Electron and VS Code suites passed, including
real managed saves, reviewed deletion/repair, native dirty/Save/undo/redo/split/raw
editing, invalid-buffer repair, Unicode/CRLF, source/spotlight/watch behavior and
reload/revision switching. Shared UI phases took about 155 seconds (Electron) and
212 seconds (VS Code), with existing per-operation/aggregate guards retained.
These timings are observations rather than production responsiveness guarantees.

That baseline's exact-index graph/source checks are recorded in its commit; the
current chain checks are recorded in [editing-chains.md](editing-chains.md). Local logs
remain under `.specspec-local/argv-inputs/`, including `python-final.log`, the three
`*-final.log` npm runs, `electron-host.log`, `vscode-host.log` and
`history-rebuild.log`. No release publication or owner hook installation is part
of this change.
