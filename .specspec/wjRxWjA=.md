---
id: wjRxWjA=
type: implementation
parents:
- YGhmCrA=
sources:
- path: tools/readme_figures.py
- path: docs/images/spectrum-light.svg
- path: docs/images/spectrum-dark.svg
- path: docs/images/revise-light.svg
- path: docs/images/revise-dark.svg
- path: docs/images/direct-light.svg
- path: docs/images/direct-dark.svg
- path: README.md
- path: tests/test_repository_docs.py
---
# Draw the README figures with a deterministic outlining script

tools/readme_figures.py instances Manrope at weights 500, 650 and 700 with fontTools,
applies GPOS pair kerning and balanced title wrapping, and emits compact relative path
data on a 0.1 px grid; DejaVu Sans Mono outlines file references. It writes
docs/images/{spectrum,revise,direct}-{light,dark}.svg with identical geometry per
theme and repeatable bytes. The default Manrope path is the sibling brand kit; options
select other font files. README.md embeds each pair. When fontTools and the fonts are available, a
repository test regenerates the figures and compares them byte for byte.

The repository documentation test checks every figure as an accessible SVG image with
a labelled title and description, unique IDs and only local gradient references,
without scripts, foreign content or external links.
