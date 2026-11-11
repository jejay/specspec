---
id: w7A25ZA=
type: requirement
parents:
- _wJJQko=
---
# Keep node meaning independent of checkout newline conventions

Owners and agents work with the text of the specification independently of the newline encoding that their operating system, editor or Git checkout supplies. Ordinary reads, comparisons and the reports of an edit describe the meaningful content of a node. Spaces, indentation, wording and deliberate blank lines carry meaning.

specspec works with the Git settings and attributes that a repository has and leaves those files and settings under the owner's control. An existing document keeps its newline convention, and so does a host's own text editor. A raw read and the byte checks that guard a write use exact bytes. Linked implementation files keep their own formatting, and source tracking follows its own rules.
