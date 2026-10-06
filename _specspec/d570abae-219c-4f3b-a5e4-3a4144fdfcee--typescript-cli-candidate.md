---
id: d570abae-219c-4f3b-a5e4-3a4144fdfcee
type: requirement
status: retired
parents:
- 003d697b-4104-4fdf-8e05-0db572c436d0
managed_hash: 153491fd8920029aa82fd9fd3de4daf569f6885b7a8ba9e1858418de20d16257
---
# Retain the withdrawn TypeScript CLI candidate

Early design discussions proposed a TypeScript/Node.js command-line backend.
That candidate was withdrawn when the user explicitly required a Python tool
usable through pipx and uvx in `INTENTION_SPEC.md`.

Retain the reason for the discarded choice without making it part of the current
implementation scope. TypeScript remains an extension-host language, not the
canonical CLI/backend language.
