---
id: v6xn2GU=
type: requirement
parents:
- DiIJxaQ=
---
# Link implementations to precise or growing regions of Git-tracked code

An implementation links the code that realizes it: several regions in several files. A link stays useful when lines merely shift, because it addresses file content through Git. A precise link reports changes inside its region, and a broad link can take in additions and changes inside it. Regions that were selected separately stay separate, and a mapping that is unavailable or ambiguous is shown as such.

Links are captured and reanchored by deliberate operations, the linked source can be read in a preview, and a check against Git is available on request. A source link gives context for an implementation, and review decides whether the code still fulfills its intention.
