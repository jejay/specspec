---
id: 9oE6Ia4=
type: implementation
parents:
- SRsw2W0=
- tvic3PQ=
- apEb_pM=
- Yfy0414=
sources:
- path: src/specspec/git.py
  symbol: git_snapshot, semantic_diff, source_change_impact, install_hook
- path: tests/test_git.py
- path: tests/test_additional.py
- path: tests/test_ids.py
  symbol: canonical IDs, current-only validation and collision retry
- path: tests/test_markdown.py
---
## Current compact-ID and history correction

The implementation/verification below records earlier revisions. Its legacy-reader,
schema-migration, original API-2 receipt and root-history compatibility descriptions
are superseded by qowy5AI= and YaXJpGE=. Current production code supports only the
canonical Base64url node scheme, with no old-schema reader or migration command.
The default node-editor association is **/_specspec/???????=*.md. Gantt's maintained
history is rewritten and bundled; tests do not require old root graph revisions.
Earlier run counts are historical evidence, not claims about this revision. The
separate current implementation record documents the new checks and limitations.

# Load staged and historical graph snapshots without provenance enforcement

git_snapshot reads exact index/commit node blobs with NUL-delimited Git output,
without a shell or checkout. Each snapshot selects its own v1/v2/v3 manifesto
version. Obsolete legacy hash fields are ignored, not exposed or checked. Manual
body/metadata changes are valid when their actual schema/graph is consistent.

semantic_diff compares normalized node contents by ID, withdrawal, paths and
old/new edges. file_changes compares raw bytes directly, not byte hashes. Legacy
approval labels aren't invented review stages. Migration changes only the root
version semantically; raw frontmatter removals remain visible. Linked source impact
uses both revisions and is informational review context, not approval evidence.

Disposable tests stage schema corruption masked by a repaired worktree, and allow
valid manual edits including legacy blobs. Partial staging, empty baselines,
renames/edges, source impact and v1/v2-to-v3 history remain covered. Hooks are opt-in,
preserve existing/custom hooks, and check the exact index. No staging/committing,
branch switching, or historical blob rewriting is introduced.
