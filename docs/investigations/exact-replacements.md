# Exact selected-passage body updates

The [selected-passage intention](../../_specspec/kiRE62k=.md) supports concise agent
and human edits while retaining unrelated binding text. The
[replacement choice](../../_specspec/1GJRSPU=.md) uses explicit OLD/NEW arguments on
`update`, within the existing [editing invocation](editing-chains.md) boundary.
See [usage and quoting](../cli.md#replace-selected-body-text).

## Choice and matching

`update NODE_ID --replace OLD NEW` is repeatable. Each nonempty OLD must have exactly
one literal occurrence in the original current body. Checking uniqueness includes
overlapping occurrences: `aaa` in `aaaa` is ambiguous. Every pair matches the same
original body; insertion order does not cascade or make another pair applicable.
Matched ranges must be disjoint; adjacent ranges are permitted. Equal OLD/NEW is
an explicit body no-op, and empty NEW removes a passage. The final body still satisfies
ordinary nonempty/schema/size rules.

This is literal, case-sensitive text replacement, with no regular expression,
fuzzy match, patch grammar or automatic global replacement. Context supplied in OLD
identifies the passage. Unicode normalization, whitespace cleanup and line-ending
conversion are not performed. Untouched body characters remain exact; inserted NEW
is literal, including supplied LF/CRLF and final newlines. Frontmatter is outside
the matching surface, and metadata uses its existing serializer and explicit flags.

Whole-body `-m/--message` and integration `--body FILE|-` remain alternatives;
combining either with replacements is an invocation error. Replacement syntax,
source conflicts and input limits across all steps are checked before body input
reads. Matching happens against the fresh identified document inside the existing
workspace lock. An unrelated intervening body edit remains present when the selected
OLD still matches uniquely. Failed matching rejects the complete candidate before
journaling/writing; it does not undo independent successful earlier invocations.

## Implementation and bounds

- `body_replacements.py` validates pairs, finds unique original-body spans, rejects
  overlaps and bounds the UTF-8 result before joining it. Diagnostics identify the
  failing pair and canonical target without echoing body text.
- `cli.py` exposes the two-value repeatable option only on update, preflights sources
  and routes replacement updates through the existing explicit-candidate planner.
- `edit_cli.py` uses the option's declared arity, including one attached value in
  `--replace=OLD NEW`, so both values can literally equal commands or flags.
- `batch.py` accounts for both sides of each pair with other supplied body input,
  resolves each selected body's replacements under lock and retains one candidate,
  deletion consent, optional validity boundary and recoverable journal scope.

An invocation has at most 1024 replacement pairs across its 1–1024 editing steps.
Each OLD/NEW value stays within 1 MiB, and both values count against the existing
16 MiB aggregate authoring-text budget, together with messages and decoded body
files/stdin. File loading stops on exceeding that combined budget. Each complete
canonical node is still bounded at 1 MiB, including its header. Existing argument
and platform limits remain independent; long argv can fail before the CLI starts.
There is no additional replacement file/stdin/JSON interface or size fallback.
Large full-body inputs retain their existing explicit integration sources.

API and node format remain 7. Both hosts retain their ordinary single-edit
argv/stdin, reviewed deletion and application channels, and native/managed save
owners. No API request fields, host products, transaction-writer behavior, hooks
or automatic Git staging/commits are introduced. Because this is an additive
argument option rather than a schema or existing-command cutover, the maintained
Gantt bundle/receipts/ledger remain unchanged and are validated with current tools.

## Verification scope

Focused tests cover original-body/non-cascading semantics, adjacent/overlapping and
missing/multiple matches, repeated/empty/no-op inputs, Unicode/case/normalization,
LF/CRLF/final newlines, metadata boundaries, parents/sources, both option spellings,
literal command/flag values, complete preflight, combined budgets and output size.
Integration tests cover dry-run, invalid-graph boundaries, one alias/deletion/repair
candidate, fresh under-lock matching, original-byte races, interruption recovery and
shell-free Windows subprocesses with ASCII/cp1252 output configurations.

The complete Python suite passes **729 tests**, including **55 replacement tests**.
The focused authoring/transaction/documentation group passes 202 tests. Ruff, format
and whitespace checks pass. Shared UI passes 254 tests, VS Code 46 and Electron nine.
Actual Windows subprocesses pass with ASCII/cp1252 output encodings, and an actual
Git Bash invocation passes repeated Unicode replacements plus chained alias creation.

The complete 18-file candidate was first checked through a separate temporary Git
index: **210 project nodes and 22 example nodes, zero errors/warnings**, including
staged source checks. The real staging area remained untouched during that pass.
The owner-authorized commit repeats graph/source checks against the actual index.
All 203 original canonical
files outside the four deliberately revised bindings retain their original bytes,
including existing line-ending-only differences. The current-tool Gantt history
verifier passes all eight retained refs and runnable stages 01–03: 123 actual recorded
CLI operations, 22 current nodes and 22 historical deletions. Its maintained files
are unchanged.

Local evidence remains under `.specspec-local/exact-replacements/`, including
`python-final.log`, `focused.log`, the three npm `*-final.log` files,
`history-final.log`, `bash-probe.json`, `review.diff` and `candidate.json`.
The complete installed-host suites were not rerun for this additive CLI option;
no host product or private transport files changed. Physical Linux/macOS and every
PowerShell/cmd native-argument quoting variant remain outside this verification.
Staging and committing this slice follow the owner's explicit request; product
commands continue to leave those Git operations under the caller's control.
