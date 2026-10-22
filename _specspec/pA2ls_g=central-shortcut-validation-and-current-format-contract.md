---
id: pA2ls_g=
type: requirement
parents:
- uAjln2M=
---
# Validate shortcut freedom centrally under the current node format

Node format 7 requires a rooted, transitively reduced intention-conclusion DAG.
Five-byte padded Base64url identities, node fields and source grammar retain their
contracts. Application API 6 retains its protocol. Current-only readers diagnose
other node versions explicitly. Maintained Gantt revisions and actual receipts use
this same current contract throughout; existing manual clones retain experiments.

The shared backend graph validator checks the whole graph after references, parent
types and acyclicity are sound. Each redundant parent produces REDUNDANT_PARENT
with the affected node, direct edge and a deterministic alternative path. Managed
add/update and other writes validate saved and complete candidate graphs before
canonical writes. Working, exact-index, revision and native-overlay reads use the
same rule. Owner-configured hooks and CI call check --staged against actual index
bytes. Native invalid text remains diagnosable and repairable.

Relationship edits can affect other nodes. Diagnostics expose every affected edge;
related changes are deliberate, and managed edits leave files intact on rejection.
Owners can prepare a coherent multi-file Markdown change and validate the complete
result or stage the complete intended graph. Ordinary CLI updates keep their
single-node contract. Validation never silently removes or normalizes relationships
and introduces no approval workflow or permanent compatibility/migration command.
