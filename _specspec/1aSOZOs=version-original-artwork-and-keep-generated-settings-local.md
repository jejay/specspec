---
id: 1aSOZOs=
type: requirement
parents:
- ALlkmT0=
- f5_ViWE=
- DB21zn8=
---
# Account for original artwork and machine-generated development settings

Version the original supplied loose PNG/SVG under their existing filenames instead
of leaving brand inputs untracked. Keep branding/dachshund.svg byte-identical to
the supplied SVG and existing derivative/icons unchanged. Mark original/imported
SVGs as non-text for Git so checkout line-ending conversion cannot change input
bytes. Document the relationship; asset preservation is not a new runtime palette
or renderer import feature. Test the exact import and original PNG signature.

Preserve the existing generated .vscode/settings.json Python Environments discovery
list locally, but ignore only that root settings file: it is machine-local discovery,
not a shared project environment assignment. Keep tracked launch/tasks/workspace
configuration available and do not hide all of .vscode, rewrite the local list,
install hooks or clear diagnostic/recovery state. No canonical node fields change.

Origin: a revisable repository-input/local-state choice finishing the pending files
under the original-brand/self-hosting intentions and backlog request.
