---
id: 7c9750b8-c8da-46a6-9248-c409da45cf19
type: requirement
parents:
- 95287a17-697f-43ad-80b0-140d5e0ec058
---
# Replace bulky UUIDs with compact random full identifiers

Use a slimmer, self-made identifier for nodes instead of the long UUID. The user
requests seven Base64 characters followed by one standard-compliant equals sign,
for eight characters total. The trailing equals sign belongs to the full identity:
keep it in frontmatter, parent references, CLI/API arguments and displayed IDs.
Use that same equals sign as the natural boundary before the filename summary,
without an additional double-hyphen separator.

Generate IDs from random bytes, using the full entropy available to the seven
Base64 characters. The user asks whether that is 42 bits; that is a question to
resolve, not an established encoding fact. Check for collisions within the project
and regenerate when a collision occurs, rather than overwriting another node.

Document the work in this self-hosted specification and commit in sensible steps.

Origin: the user's compact-ID request in this conversation. Alphabet, actual bit
capacity, compatibility and conversion mechanics need separate technical reasoning;
do not silently reinterpret the requested standards compliance or entropy.
