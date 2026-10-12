---
id: v6xn2GU=
type: requirement
parents:
- DiIJxaQ=
- ME4UXTA=
- SRsw2W0=
---
# Link implementation explanations to Git-tracked source regions

Enrich implementation source hints with multiple line-level regions in multiple
files. Use Git to keep references useful after code shifts, instead of making
users manually renumber every insertion. Prefer file-content objects to avoid
having to embed a not-yet-created commit's identity in that same commit.

Support both specific and broad references: specific references must not silently
accept additions or changes inside their selected regions; broad references may
include code added or changed inside them. Preserve the user's selected separate
regions rather than silently treating unrelated intervening code as implementation.
Expose problems and allow deliberate correction through SpecSpec commands; an
optional Git check may assist. Source tracing is not proof that changed code still
realizes its intention, an approval state or authorization to silently stage code.

Origin: the user's line-level/blame-like source-link discussion, endorsement of
blob-based anchoring and explicit request for both specific and broad references,
with intention, conclusion, detailed conclusion, implementation and sensible commits.
