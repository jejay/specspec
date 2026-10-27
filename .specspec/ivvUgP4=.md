---
id: ivvUgP4=
type: requirement
parents:
- DOqGIio=
- 7tMgRa8=
---
# Explain ordinary commands with concise static terminal help

Keep root, command and subgroup help task-oriented, ASCII-safe and project-independent.
Reduce explanatory bodies to 50–70 percent of their prior length while retaining
purpose, defaults, complete useful examples and critical safety distinctions. Option
descriptions can carry local detail. Help does not read stdin, payloads or projects.

Normal usage runs from the intended directory, like Git. Root-selection and structured
output switches remain hidden integration controls and never appear in help text,
examples or option listings, including private transport help. Internal format/API
versions stay out of normal agent/human help and readable query headers; incompatible
versions still produce actionable diagnostics. Pipes do not change output mode.

Explain message/stdin input, complete-body versus passage edits, parent-list
replacement, invocation-wide flags, exact deletion/consent, final validity, recovery,
query selection/ancestors and deliberate source metadata. Link technical guides for
integration detail rather than exposing transport mechanics in everyday examples.
