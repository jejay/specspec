---
id: yWTbmx4=
type: requirement
parents:
- ME4UXTA=
retired: true
---
# Retain the withdrawn TypeScript CLI candidate

Early design discussions proposed a TypeScript/Node.js command-line backend.
That candidate was withdrawn when the user explicitly required a Python tool
usable through pipx and uvx in `INTENTION_SPEC.md`.

Retain the reason for the discarded choice without making it part of the current
implementation scope. TypeScript remains an extension-host language, not the
canonical CLI/backend language.
