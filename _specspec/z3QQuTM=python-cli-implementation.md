---
id: z3QQuTM=
type: implementation
parents:
- LvYBN_4=
- -9Up2uc=
- apEb_pM=
- WpYvGUo=
sources:
- path: pyproject.toml
- path: src/specspec/__main__.py
- path: src/specspec/cli.py
  symbol: context
- path: src/specspec/cli.py
  symbol: delete
- path: src/specspec/cli.py
  symbol: main
- path: src/specspec/cli.py
  symbol: migrate_command
- path: tests/test_api.py
- path: tests/test_core.py
- path: tests/test_ids.py
  symbol: current-only commands, physical deletion and removed legacy filters
---
## Current cascade implementation

fuyy0Lk=/AuhoBoU= supersede named-files-only deletion. The shared backend now
removes every directed descendant, including shared children, with per-node
uncommitted warnings/confirmation before unlinking and reviewed-scope rechecking.
See huB7hcg= for current code, 182 Python/141 shared/37 VS Code/nine Electron
checks and full real-host evidence, including earlier failures. PfJv45U= separately
justifies aligning the outer smoke budget; individual deadlines/assertions remain.
The earlier deletion/retirement/schema/count checkpoints below are history, not
current cascade or warning contracts. No node schema conversion is introduced.

## Current deletion-only correction

xu6W0c4=/5d5oDCM= supersede the earlier retired/withdrawal workflow below.
Current schema/API 5 removes the flag and all retire/restore/filter/metadata/badge
paths. Managed delete physically unlinks an explicit batch after DAG checks,
with journal new=null and original-byte/recovery safeguards. Default HEAD-relative
UI ghosts are derived base records, read-only/copyable through staging and gone
after commit; Git HEAD/ref watching refreshes both hosts. Native Delete requires
clean project documents; deleted buffers never resurrect files in overlay reads.
All earlier workflow/schema/test counts below are historical evidence. Gantt's
entire current corpus is rebuilt with 22 physical deletions/reasons in prior Git
commits and a 22-node HEAD, no flagged retained nodes. Earlier root explanations
are in Git, not retained retired files. Source regions/colors/shapes/camera/native
Save remain in scope; the separate current implementation record links actual tests.

# Package the hash-free Python CLI and JSON interface

Hatchling packages src/specspec and exposes specspec.cli:main. Click delegates to
the shared model/graph/workspace/Git backend. JSON API 3 exposes normalized node
records, withdrawal booleans, graph format versions and structured diagnostics,
without managed_hash or fingerprint fields. --expect is removed from every command
and the library; there is no accept command, status filter or approval step.

add/update, explicit withdrawal batches, live/retired listing, complete ancestor
context and byte budgets remain. migrate converts valid v1/v2 files to v3 without
checking obsolete hashes. Body input uses UTF-8 stdin/files. Normal tool writes
reject unmigrated workspaces with guidance, but valid manual edits are readable
and usable before/after migration. CLI export/show/list/context/impact/validation
and staged checks emit no fingerprints.

Tests cover hash-free outputs, removed options, manual changes, legacy conversion,
idempotence, withdrawal, parent-before-child context, UTF-8/CRLF and exact budgets.
No new distribution publication or production correctness claim is made.
