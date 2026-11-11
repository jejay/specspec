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
# Resolve strict and expanding source links against Git and show them in both graph editors

`source_schema.py` validates links to whole files and anchored links. `SourceReader` in `sources.py` checks and reads Git objects in batches, caches mappings and resolves a link against the working tree, the index or a commit. A batch counts toward its total only the blobs that it accepts: a blob over the size limit is reported as such and leaves the total to the other blobs. A strict link reports edits inside its region, and an expanding link takes in insertions inside its region and replacements wholly within it. Both keep separate regions apart and leave out insertions at the outer edge and the gaps between regions. Ambiguity, deletion, a wrong or missing blob and problems of entry type, path, UTF-8, binary or LFS content and limits stay visible in the result. The text of a region, its context and a limited search for renames help to find it again, and an uncertain result is reported as uncertain.

`source_commands.py` provides capture, resolution, check, reanchor and view, and an optional check of retention on the exact index: Git keeps a blob through the trees that contain it. The forms that both graph editors share, in `graph-ui-common/media/graph.js` and `graph-ui-common/host/session.cjs`, show literal previews, show the originally anchored content when a mapping is unreliable, and put a captured link into the open form, which is saved by its usual owner, VS Code or the writer. The sources of an earlier revision can be viewed. A change anywhere in a linked file counts as possible impact on the implementations that link it. Two identical versions of a source resolve before the limit on the size of a diff applies. A source line ends only at LF, CRLF or CR, like a line of logical node text. `SourceReader` looks up the referenced paths in chunks and loads a complete tree listing only to search for renames and to check retention. A failed Git read becomes an unavailable result for the object concerned, with a `SOURCE_LINK` diagnostic.

The reader and the schema work within these limits:

- 2 MiB for one source file or blob
- 32 MiB for the blobs of one batch, for the target files of one request and for the output of one Git listing, history or diff command
- 10,000 lines for one source
- 20,000,000 line pairs for the diff of two versions
- 128 commits for one rename search
- 20 seconds for one Git call
- 256 sources for one node, 64 ranges for one source and line numbers up to 2,147,483,647

`tests/test_sources.py` exercises the feature, and so do the links of this node itself: a strict anchor on `source_schema.py` and expanding anchors on `sources.py` and `source_commands.py`. `example/gantt/history/verify.py` resolves the source links of every commit of the example's history together with the retention check.
