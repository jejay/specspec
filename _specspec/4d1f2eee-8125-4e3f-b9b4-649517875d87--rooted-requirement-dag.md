---
id: 4d1f2eee-8125-4e3f-b9b4-649517875d87
type: requirement
status: accepted
parents:
- c0943883-e3cb-4de9-8c5e-6aeb4a37dd06
managed_hash: 9da91a7f15e127a2475c5eab1f7e2e4cb08101733e3bee2a1f89deec09598b98
---
# Represent justifications with a rooted requirement DAG

The specification has one manifesto root, requirement nodes with one or more
manifesto or requirement parents, and terminal implementation nodes. All nodes
belong to a connected acyclic graph. Multiple parents may occupy different
relative positions. A requirement records a minimal coherent specification
element; an implementation records how a realization relates to its requirements.

Origin: [INTENTION_SPEC.md](../INTENTION_SPEC.md), graph description.
