---
id: Oou-SvU=
type: requirement
parents:
- F5JaC_4=
- f5_ViWE=
- 7CXCJO4=
---
# Maintain current-scheme tooling and a compliant Gantt regression history

Use padded Base64url for the compact node IDs and convert existing working nodes.
This confirms the recommended canonical five-byte encoding (40 random bits).

SpecSpec's own graph is self-referencing evolving design documentation. The Git
versioning tooling need not work or be tested against older revisions of that
graph. Obsolete node schemes may be rejected as invalid/noise by current tooling;
that is expected, not a reason to retain superseded readers or migration paths.
Do not keep old overwritten or reverted schemes in production code.

Use the example Gantt project for rigorous Git regression tests. Rewrite its
maintained history so all tested revisions comply with the current node scheme,
settings and tooling. Keep its substantial redirects, spec-before-code sequence,
withdrawn reasoning and runnable stages, but not obsolete SpecSpec machinery.

Origin: the user's Base64url/conversion confirmation and explicit current-only
compatibility/testing correction in this conversation. This is not a removal of
Git functionality or a requirement to rewrite unrelated SpecSpec development.
