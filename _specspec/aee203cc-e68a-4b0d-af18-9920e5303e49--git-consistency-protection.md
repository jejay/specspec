---
id: aee203cc-e68a-4b0d-af18-9920e5303e49
type: requirement
parents:
- 003d697b-4104-4fdf-8e05-0db572c436d0
- 955b905a-6220-4d5c-b0ca-fab86b6b6db8
---
# Protect the Git-versioned graph against corruption

Keep the specification under Git and offer a Git hook that checks graph
consistency and catches corrupting manual edits before they enter a commit.
Consistency checking must remain usable alongside ordinary Git development.

Origin: [INTENTION_SPEC.md](../INTENTION_SPEC.md), Git and tool management.
