---
id: Ryqivvg=
type: implementation
parents:
- Pxcs6Oc=
sources:
- path: docs/architecture-interfaces.svg
- path: docs/architecture.md
- path: tests/test_repository_docs.py
---
# Document and verify the CLI-library-UI interface zoom

`docs/architecture-interfaces.svg` names the three interface contracts, groups the
CLI facade with its Python library in one process, shows direct agent CLI calls
and alternative library embedding, and illustrates message/argv/stdin/JSON payloads.
A native editor sequence follows non-writing plans and host acknowledgement before
separate native Save. A route sidebar identifies saved-file reads, buffer overlays,
commit targets, managed mutations and source-preview/capture behavior.

`docs/architecture.md` links both diagrams and explains the exact transport/library
and caller-control distinctions. Repository documentation tests check both SVGs'
self-contained accessible resources and local guide links. The detail diagram's
labelled contracts and parseable response example are checked against API_VERSION.
Offline resvg full-page and detail renders support visual checks of hierarchy,
text, ports and sequence arrows. This documentation retains the overview and the
existing runtime behavior while exposing the interface and persistence seams.
