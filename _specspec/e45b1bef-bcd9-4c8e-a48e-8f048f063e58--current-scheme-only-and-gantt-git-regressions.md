---
id: e45b1bef-bcd9-4c8e-a48e-8f048f063e58
type: requirement
parents:
- 7c9750b8-c8da-46a6-9248-c409da45cf19
- 1fb70961-678b-4c03-a58c-8bcc98345501
- 5e6030af-efb6-4123-a354-1afd099c5fce
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
