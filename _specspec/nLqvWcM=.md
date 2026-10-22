---
id: nLqvWcM=
type: requirement
parents:
- T693TDw=
---
# Keep compact query rails and complete parent headers

Use two-column tree indentation: pending siblings contribute │ and one space,
completed branches contribute two spaces. Branch markers ├─ and └─ touch the type
word or reference arrow. Root metadata and body align with the unbranched header
at column zero. Other metadata and body lines use their branch's continuation rail;
the body projection retains its own non-newline indentation and whitespace.

Each full header gives the lowercase type word manifesto/requirement/implementation
and its full node ID, then every direct parent in ascending case-sensitive full-ID
order after @, separated by a comma and one space in every presentation. Include
the parent under which the record is printed.
The manifesto ends at its ID before comparison status when present. Earlier shared
occurrences remain short unexpanded pointers. Lowercase status words identify node
change, contract-relevant linked-source changes and literal file change. The preamble
contains selected revisions and applicable notes; headers carry their own meaning.
