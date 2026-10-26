# Selected-passage updates with newline-tolerant matching

The [selected-passage intention](../../_specspec/kiRE62k=.md) supports concise edits
while retaining unrelated binding text. The [replacement contract](../../_specspec/1GJRSPU=.md)
uses the existing `update --replace OLD NEW` input. Its
[default layout choice](../../_specspec/EcEFfgg=.md) keeps words exact while tolerating
line endings and ordinary prose wrapping. See [usage](../cli.md#replace-selected-body-text).

## One default comparison

Every nonempty OLD needs exactly one admissible original-body span. LF, CRLF and bare
CR line endings compare equally. Within source-mapped Markdown paragraph text, a
soft line break compares like one ASCII space, in either direction. Wrapping can
move between words. All other characters, spaces, tabs, indentation, punctuation,
case and Unicode normalization retain their literal significance.

CommonMark plus table recognition distinguishes paragraph soft breaks from headings,
blank-line paragraph boundaries, tables, fenced/indented code, inline code, HTML
syntax and explicit hard breaks. These structures keep their newlines significant
apart from line-ending encoding. Container markers and continuation indentation
stay literal. Paragraphs whose inline content cannot be mapped contiguously to their
actual source retain line-ending-only matching; prefixes and indentation are never
guessed away. This is conservative source matching, not rendered-Markdown equivalence.
For example, ordinary `alpha\nbeta` can match `alpha beta`, but a code block with
those two lines cannot be selected by the single-line phrase.

Collect line-ending-only and wrapping-aware candidates together. An exact-layout
occurrence never takes precedence over another admissible differently wrapped one.
Deduplicate identical original spans, require uniqueness and include overlapping
occurrences. All pairs address that same original body; their ranges must be disjoint
and can be adjacent. Insertions do not cascade into another pair's matching.

NEW always remains literal. Unmatched source characters/EOLs stay unchanged. Empty
NEW deletes the matched passage. Equal OLD/NEW preserves a literally matched passage,
but can change a tolerantly matched passage's physical layout: replacing wrapped
`alpha\nbeta` with `alpha beta` deliberately produces one line. Comparison never
reflows the whole body, adjusts NEW or edits frontmatter. Parent/source flags and
metadata serialization retain their existing owners.

## Implementation and safety

- `replacement_matching.py` creates line-ending comparison text with original
  character-boundary offsets. An on-demand `markdown-it-py` 4.x parser records
  ordinary text-space and soft-break positions from paragraph inline rules. Nested
  image/HTML/code syntax is not treated as ordinary prose. Source correspondence is
  verified before any soft-break positions are used.
- The two comparison views have equal normalized character counts. Match spans map
  back to original offsets before overlap checks and UTF-8 result accounting.
  Whole-body exact and literal word matches can prove their result without loading
  the Markdown parser. Ordinary help, messages and private API startup stay lazy.
- `body_replacements.py` validates bounded pairs and constructs one result from the
  original slices plus literal NEW. Its size calculation subtracts the actual
  consumed source bytes, including CRLF, rather than OLD's comparison spelling.
- `cli.py` retains the same repeatable two-value option, source-conflict preflight
  and existing planner. `edit_cli.py` protects complete canonical IDs from short-
  option interpretation; values consumed by options remain literal. `batch.py`
  still combines input budgets, aliases, whole-graph validity, deletion consent
  and one recoverable transaction.

Matching occurs on the fresh identified body inside the writer lock. Missing,
ambiguous, overlapping or analysis-limited matches reject the whole invocation before
journaling/writing. Independent earlier invocations are not undone. Original-byte
rechecks and recovery still protect external edits after matching.

Input bounds stay at 1024 pairs per invocation, 1 MiB per OLD/NEW value and canonical
node, and 16 MiB aggregate supplied body/OLD/NEW material. Shell/OS argv limits are
separate. Each comparison projection is bounded at 32,768 newline-delimited lines.
Emitted Markdown tokens are bounded at 131,072, nesting at 20, wrapping candidates
at 8,192 and metered analysis work at 64 Mi units per selected body, including its
OLD projections. Exhaustion
reports an explicit analysis-budget error rather than treating an incomplete search
as unique. Full-body input remains available. These are work guards, not runtime or
memory guarantees for every Markdown input.

There are no extra match options, modes, fuzzy spelling rules, regular expressions,
patch language or replacement file/JSON transport. `-m/--message` and integration
`--body` remain mutually exclusive whole-body alternatives. API and node format stay
7. Both hosts, their argv/stdin/private channels and native/managed persistence owners
remain unchanged. The maintained Gantt schema/history/receipts need no reconstruction
for this matching-policy change and are checked with current tools.

## Verification scope

Tests cover line-ending permutations, reflow in both directions, original Unicode
spans, all-layout ambiguity, exact-match non-precedence, same-span deduplication,
literal NEW, original-byte size accounting, overlap/non-cascading behavior and
protected Markdown structures. Deterministic prose-layout combinations check
unselected bytes. Adversarial tokens, nesting, candidates and work budgets reject
explicitly without canonical writes; cached parser state remains isolated. CLI
checks cover preview, alias/deletion chains and Windows Unicode subprocesses with
ASCII/cp1252 output. A fresh subprocess checks lazy dependency loading.

The first full run exposed an existing ID-parsing bug: a generated ID such as
`-amuwNs=` was split into an unknown short flag and `-m`, producing a spurious body-
source conflict. The saved failed fixture reproduced it deterministically. Valid
full IDs now enter Click's positional data stream before option-cluster parsing;
explicit message and replacement values keep their ordinary option arities. Tests
cover leading/mid-cluster m, double hyphens, standalone stdin/message updates,
replacement chains and ID-looking literal values. This repairs the existing
canonical-ID contract rather than adding syntax or relaxing ID validation.

The final complete Python run passes **808 tests**, after the ID fix; all three npm
suites pass again: shared UI 254, VS Code 46 and Electron nine. Ruff/format and
whitespace checks pass. Actual Windows subprocesses preserve Unicode arguments and
literal output with ASCII/cp1252 stdout. A Git Bash invocation matches flat OLD to
wrapped CRLF prose while retaining literal Unicode NEW and a chained alias. A separate
Click 8.1.8 probe verifies the supported minimum-series parser with the deterministic
hyphen-ID case, literal values and composed tolerant replacement. The development
installation resolves `markdown-it-py` 4.2.0 through the declared 4.x dependency.

The complete 17-file slice is staged only after the owner's explicit commit request.
Exact actual-index graph/source checks cover **211 project nodes and 22 example
nodes with zero errors/warnings**. All 208 original canonical files outside the two
revised bindings retain their original bytes, including existing line-ending-only
differences. Current Gantt verification passes all eight refs and stages 01–03:
123 recorded CLI operations, 22 current nodes and 22 historical deletions. Its
bundle, receipts, ledger, snapshot and manual clones remain unchanged.

Evidence and byte snapshots remain in `.specspec-local/replacement-tolerance/`,
including `python-final.log`, `python-before-id-fix.log`, `id-fix.log`, the three npm
`*-final.log` files, `history-final.log`, `bash-probe.json`, `click81-probe.log` and
the final review artifacts. The complete installed-host suites and physical
Linux/macOS gestures are outside this focused CLI qualification; host products and
private transports are unchanged. Unrelated history, source anchors and earlier
local evidence remain preserved. Product commands still perform no implicit Git
staging, commits, hook installation or release.
