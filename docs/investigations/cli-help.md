# One inspection command and task-oriented terminal help

The owner requested removal of the top-level `show` command and substantially
more useful help for every command. [Inspection intention](../../_specspec/2FfVd-Y=.md)
and [help intention](../../_specspec/DOqGIio=.md) separate these outcomes from the
[query consolidation](../../_specspec/aILBxDs=.md) and
[help presentation](../../_specspec/ivvUgP4=.md) choices.

## Interface and evidence

The everyday vocabulary is init, query, add, update, delete, check and diff.
`query ID --max-distance 0` reads one binding; `query ID` reads descendant scope;
`--with-ancestors` completes justification. Normal parsed graph readings retain
their HEAD/workspace or explicit revision comparison, selection, source evidence,
invalid-state and compact/human/JSON contracts. The former top-level command is
removed, not a hidden alias. Source/spotlight groups retain their domain-specific
show subcommands.

`query --raw` reads literal documents by ID or direct canonical path, including
malformed YAML, original EOLs and non-UTF-8 Base64. `--target` selects a commit;
`--staged` is a raw exact-index read. Neither raw nor staged inspection claims to
be a parsed graph comparison. Selection/comparison/presentation flags that do not
apply to raw input are rejected, not silently ignored. Shared backend path, schema
and byte bounds remain authoritative. Strict staged graph/source validation stays
`check --staged --sources`.

One managed host preflight used the removed command. It now sends the existing
API-7 `read` request with no base, documents, target or cache hints, obtaining fresh
saved snapshot context rather than comparison or dirty-buffer data. Mutation body
stdin, reviewed deletion, source/spotlight APIs, native document save ownership,
trust and dirty guards remain unchanged. The protocol and canonical format stay 7.

## Help design

`cli_help.py` keeps purpose/argument explanations, examples, defaults, effects and
safety notes together. Every command/group, including explicitly requested private
API help, has a substantive task guide. Root command summaries are not ellipsized.
Help is static and ASCII-safe through legacy Windows stdout encodings. A scoped
formatter preserves command examples and avoids splitting option spellings while
wrapping prose; it does not change ordinary result formatting.

The expanded guides explain whole-body versus selected-passage updates, complete
parent-list replacement, aliases, editing-chain flag scope, deletion consent and
invalid-result boundaries. Query explains one-node/descendant/ancestor readings,
shortest versus longest distances, self-inclusive influence, percentage rounding,
union selection, raw repair and incomplete evidence. Source and spotlight guides
explain their own IDs, version choices, mutation effects and uncertainty.
Less-prominent integration inputs remain explicit without becoming alternate
public command vocabularies. Help itself never opens a project or consumes stdin.

## Integration and verification scope

Tests exercise every help path without a project, examples/semantic explanations,
removed-command rejection, intact option spellings, all help under ASCII/cp1252
subprocess pipes, malformed raw bytes, staged/historical reads, conflicting raw
selectors and no filesystem/index/ref mutation. Host regressions require a fresh
saved API read before managed mutation, retaining overwrite confirmation and stdin.
Existing CLI, graph, transaction and application suites remain applicable.

The maintained Gantt corpus is refreshed through actual current CLI executions at
all retained revisions, substituting descendant queries for removed-command reads.
Its independent oracle checks ancestor and descendant selection separately. IDs,
application bytes, redirects, ordering, manual experiments and unrelated SpecSpec
history are preserved. The tracked fixture remains free of nested Git metadata.

Final verification passes **881 Python tests**, including 72 help/raw-inspection
cases; shared UI passes 255 tests, VS Code 46 and Electron nine. Ruff, formatting
and whitespace checks pass. The first complete run found one old read in the shared
host fixture (880 other tests passed); after migrating that fixture and platform
probes, the complete Python suite was rerun successfully. Earlier logs are retained.

Complete installed Windows Electron and VS Code suites pass, including actual
managed saves using the new preflight, exact deletion/repair, original-byte checks,
source/spotlight behavior, watchers and historical switching. Electron also checks
reload/persisted drafts and sandbox boundaries. VS Code checks native dirty/Save/
undo/redo, raw/split views, independent cameras, invalid buffers and Unicode/CRLF.
Shared UI phases were approximately 146 seconds Electron and 229 seconds VS Code;
these are local observations, not responsiveness guarantees. Individual/aggregate
guards and production behavior remain unchanged.

All eight retained Gantt refs were reconstructed externally through **123 actual
CLI executions**: 65 query readings (43 ancestor and 22 descendant), 45 literal body
authoring calls and null stdin throughout. Bundle, receipts, ledgers, current source
anchors and tracked snapshot were refreshed together. All three runnable stages
validate. The development repository and manual clones were not rewritten.

The complete slice was first validated through a separate temporary index,
including graph/source checks for 215 project and 22 example nodes with no errors
or warnings. The real staging area remained untouched during that pass. The owner's
subsequent commit request authorizes staging; graph/source checks are repeated
against the actual index before commit. All 204 original canonical files outside
the deliberately updated bindings retain their exact bytes.

Logs, original-byte snapshots and external reconstruction locations are retained in
`.specspec-local/cli-help/`: `python-final.log`, `python-before-fixture-fix.log`,
`help-final.log`, the three npm `*-final.log` files, `electron-host.log`,
`vscode-host.log`, `history-rebuild.log` and final review/candidate reports.
Physical Linux/macOS and remote SSH/tunnel execution were not rerun for this slice.
Passing tests remain bounded evidence, not proof of semantic correctness or universal
responsiveness. No release or owner hook installation is part of this work.
