---
id: ME4UXTA=
type: requirement
parents:
- XV5_rPQ=
---
# Recommend graph-aware specification edits without forbidding manual edits

The command-line tool and visual editor are the recommended ways to change the
specification graph. The visual editor shares the backend's graph rules and
Markdown edit planning rather than implementing an independent canonical model.
Manual edits to canonical Markdown are permitted and validated on their actual
contents, not rejected for their provenance.

Origin: INTENTION_SPEC.md originally required tool-managed changes; the user's
later consenting-adults correction explicitly permits manual edits and removes
fingerprinting and managed_hash enforcement. The original source remains unchanged.

Later clarification: the user explicitly authorized trying native VS Code text
documents alongside the existing Electron host. This permits host-native persistence
of backend-planned file edits; it does not require all hosts to adopt that mechanism,
replace the shared domain backend, or claim Python transaction guarantees for native
text saves. The separate native-document conclusion records that revisable choice.
