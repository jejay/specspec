---
id: 1aSOZOs=
type: requirement
parents:
- ALlkmT0=
- f5_ViWE=
---
# Preserve original assets and scope machine-local settings

Version the supplied loose PNG/SVG under their original filenames. Preserve the
exact SVG import and derived icons. Mark the supplied/imported SVGs as Git non-text
assets so their checkout bytes remain identical. Check the import and PNG signature.

Retain the generated root `.vscode/settings.json` discovery list locally, with an
ignore rule specific to that file. Track shared launch/tasks/workspace files.
Keep local experiments, diagnostic profiles and recovery records available.
