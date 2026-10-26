---
id: w7A25ZA=
type: requirement
parents:
- 0dvOn3A=
---
# Keep node meaning independent of checkout newline conventions

Owners and agents work with specification text independently of the newline
encoding supplied by their operating system, editor or Git checkout. Ordinary
reads, comparisons and mutation feedback describe meaningful node content.
Spaces, indentation, wording and intentional blank lines keep their meaning.

SpecSpec works with each repository's existing Git settings and attributes while
leaving those files and settings under owner control. Existing documents and
native editors retain their local newline convention. Raw inspection and physical
transaction safeguards retain exact bytes. Linked implementation files retain
their own formatting and source-tracking contracts.
