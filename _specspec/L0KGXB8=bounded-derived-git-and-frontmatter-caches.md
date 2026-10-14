---
id: L0KGXB8=
type: requirement
parents:
- tGpRMLM=
- LvYBN_4=
- Yfy0414=
---
# Reuse bounded derived Git bytes and parsed frontmatter

Use transient project/request/library caches around existing Snapshot and Graph
structures. Resolve refs freshly and verify tree/index entries and object metadata.
A host may return bounded immutable baseline bytes as a warm read hint; verify each
hint against the current Git blob address before reuse, fetch mismatches normally,
and observe missing objects. Keep hints scoped to repository/subtree/resolved commit;
HEAD movement changes applicability while staging preserves HEAD membership.

Memoize round-trip frontmatter by exact header bytes and parser version with bounded
bytes/counts and isolated mutable copies. Body edits retain native bytes and comments.
Validate node fields, graph, source paths and runtime lock/journal state against each
current read. Cache eviction preserves correctness. Derived caching introduces
neither canonical metadata nor node edit gates; managed writers and exact-index
checks retain their authoritative current-file/object checks. Keep the CLI usable
as a bounded one-shot process.
