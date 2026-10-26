---
id: 1GJRSPU=
type: requirement
parents:
- kiRE62k=
- 4626uI8=
---
# Select unique original-body passages for bounded update replacements

update accepts repeatable --replace OLD NEW pairs as an alternative to whole-body
message or integration input. OLD is nonempty and has exactly one original-body
match under the default line-ending and prose-wrapping comparison rules. Include
overlapping occurrences and all permitted layouts when checking uniqueness. All
pairs refer to that same original body, have disjoint matched ranges and produce
one candidate without cascading into inserted text. NEW may be empty to remove a
passage, and is always inserted literally.

Preserve untouched body characters, line endings and final-newline state literally.
Words, case and Unicode characters remain exact; comparison alone tolerates standard
line endings and Markdown prose soft breaks. Match and transform under the existing
writer lock against the fresh identified node. Parents, sources and other metadata
retain their existing separate edit owners. Missing, multiple or overlapping matches
reject the complete invocation before canonical writes, with a target diagnostic.

Replacement, message and integration body sources are mutually exclusive within
an update. Validate syntax, body-source conflicts and replacement input limits
across all steps before opening body files or stdin. Both values of each pair stay
literal even when they equal command names or flags. The existing chain candidate,
preview, optional final validity, deletion consent, byte guards and journal recovery
remain authoritative. Full-body replacement and existing UI transports remain usable.

An invocation contains at most 1024 replacement pairs across its editing steps.
Count OLD and NEW UTF-8 bytes together with other body input against the 16 MiB
authoring budget; each replacement value and resulting canonical node retains the
1 MiB bound. Operating-system argument limits remain independent. OLD/NEW remain
explicit argument text. The same replacement option provides its complete default
matching behavior. API and node format remain 7.
