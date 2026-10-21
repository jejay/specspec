---
id: vQFml0Y=
type: implementation
parents:
- VnSF9BE=
sources:
- path: src/specspec/source_schema.py
  blob: 28a84673073469bd31f455da908bcb50fd93af77
  mode: strict
  ranges:
  - - 1
    - 65
- path: src/specspec/sources.py
  blob: b00f5093dd1edc637e75d71f961651204d1e52a3
  mode: expanding
  ranges:
  - - 1
    - 443
- path: src/specspec/source_commands.py
  blob: d564a9e7646fb4b182193e66c818a8d1c714df3e
  mode: expanding
  ranges:
  - - 1
    - 220
- path: docs/source-regions.md
- path: electron/test-host/run.cjs
- path: example/gantt/history/cli.jsonl
- path: example/gantt/history/gantt.bundle
- path: example/gantt/history/revisions.json
- path: example/gantt/history/verify.py
- path: graph-ui-common/host/session.cjs
- path: graph-ui-common/media/graph-model.js
- path: graph-ui-common/media/graph.js
- path: graph-ui-common/test-host/ui.cjs
- path: graph-ui-common/test/graph.test.cjs
- path: graph-ui-common/test/session.test.cjs
- path: graph-ui-common/view.cjs
- path: src/specspec/cli.py
- path: src/specspec/editor.py
- path: src/specspec/format.py
- path: src/specspec/model.py
- path: tests/test_sources.py
- path: vscode/test-host/smoke.cjs
---
# Resolve strict/expanding Git blob source hints through shared hosts

`source_schema` validates whole-file and anchored hints. `SourceReader` batches
object checks/bytes, caches mappings and resolves worktree/index/commit targets.
Batch admission reserves only eligible content bytes; oversized objects stay
explicit without starving unrelated bounded blobs.
Strict reports internal edits; expanding absorbs internal/contained changes; both
preserve separate regions and exclude outer insertions/gaps. Ambiguity, deletion,
wrong/missing blobs, entry/path/UTF-8/binary/LFS/budget problems remain visible.
Text/context and bounded rename evidence aid relocation with explicit uncertainty.

`source_commands` provides capture/resolve/check/reanchor/view and optional exact-
index retention checks. Tree membership supplies Git retention. Shared forms show
literal previews, original contents when mapping is unreliable, and capture into
native/managed forms with normal save ownership. Historical sources are viewable.
Source impact stays conservative per file. Tests and retained strict-schema/
expanding-resolver anchors exercise the feature's own addressing contract.
