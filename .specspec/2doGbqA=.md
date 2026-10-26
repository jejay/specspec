---
id: 2doGbqA=
type: requirement
parents:
- jWl96h0=
---
# Batch known query source blobs within each invocation

Use each selected committed tree's existing regular-file entries to collect the
Git blob addresses of referenced paths, alongside recorded region anchors. Fetch
those addresses together into the existing reader-local immutable blob cache before
resolving individual references. Deduplicate addresses and retain individual source
rows, per-path safety checks and exact contract/raw comparison facts. Reuse the
same code-version reader when both selected commits are identical.

Caches live only within this source comparison. Resolve refs and saved files freshly
for every invocation. Workspace target bytes come from saved files, not staged/index
blob addresses; anchor blobs remain immutable Git reads. Missing/wrong-type/oversized
objects and exhausted budgets stay explicit. Oversized objects reserve no content
bytes and do not consume the admission budget of unrelated eligible blobs. Existing
per-object, request, mapping, rename, entry/path and UTF-8 limits stay in force.

Prefer bulk population of the existing per-call cache over cross-call persistence
or changes to source semantics. Measure fresh-process CLI output and instrumented
read/render/Git-process costs separately. Verify output equivalence on fixed
current-schema workspaces and use process-count regressions instead of flaky wall
clock limits. Report local timings as observations, including platform/cache scope,
not universal performance guarantees. Shared mapping/check/preview and Git/node/API
formats retain their contracts.
