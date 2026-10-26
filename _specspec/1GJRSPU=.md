---
id: 1GJRSPU=
type: requirement
parents:
- kiRE62k=
- 4626uI8=
---
# Match exact original-body passages for bounded update replacements

update accepts repeatable --replace OLD NEW pairs as an alternative to whole-body
message or integration input. OLD is nonempty and each OLD has exactly one literal
occurrence in the current original body, including overlapping occurrences when
checking uniqueness. All pairs refer to that same original body, have disjoint
matched ranges and produce one candidate without cascading into inserted text.
NEW may be empty to remove the matched passage. Equal OLD/NEW is an explicit body no-op.

Preserve untouched body characters, line endings and final-newline state literally;
insert NEW exactly as supplied. Matching is case-sensitive and Unicode-literal.
Body matching and transformation occur under the existing writer lock against the
fresh identified node. Parents, sources and other metadata retain their existing
separate edit owners. Missing, multiple or overlapping matches reject the complete
invocation before canonical writes, with an actionable target diagnostic.

Replacement, message and integration body sources are mutually exclusive within
an update. Validate syntax, body-source conflicts and replacement input limits
across all steps before opening body files or stdin. Both values of each pair stay
literal even when they equal command names or flags. The existing chain candidate,
preview, optional final validity, deletion consent, byte guards and journal recovery
remain authoritative. Full-body replacement and existing UI transports remain usable.

An invocation contains at most 1024 replacement pairs across its editing steps.
Count OLD and NEW UTF-8 bytes together with other body input against the 16 MiB
authoring budget; each replacement value and resulting canonical node retains the
1 MiB bound. Operating-system argument limits remain independent. Replacement input
is explicit argument text, with no file autodetection, patch language, regular
expression matching or whitespace cleanup. API and node format remain 7.
