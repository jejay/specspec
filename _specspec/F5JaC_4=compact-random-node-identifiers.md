---
id: F5JaC_4=
type: requirement
parents:
- _yahyM4=
---
# Use compact random full node identifiers

Use seven Base64url payload symbols followed by one standard padding equals sign,
for eight characters total. Generate from random bytes and retry project-local
collisions. The full identity includes `=` in frontmatter, parents, commands,
API messages and the UI. That equals sign also separates identity from the English
filename summary. The canonical byte encoding and portable collision policy are
specified by the encoding conclusion.
