---
id: AY1g-sU=
type: requirement
parents:
- h3zqGZU=
---
# Read each query binding on one line with paragraph separators

The ordinary readable query projects each current or deleted binding into one line,
retaining every content character while replacing its newline runs. Normalize newline encodings
to LF, replace a single LF with one space and replace a run of two or more LFs with
" ¶ ". Apply the same rule to leading and trailing runs. Retain other whitespace,
Markdown markers, Unicode and headless text. The one-line projection is the default presentation.

A space at a soft line break keeps adjacent words separate. The projection is a
compact text reading, rather than a Markdown renderer: list items, code lines and
hard breaks follow the same literal newline rule. Complete logical layout is in structured comparison records, with CRLF
normalized to LF. Canonical files/raw queries retain physical bodies and line endings; diff supplies
logical content changes independently of newline encoding.
Shared terminal-control escaping, complete untruncated text, full parent headers, last-occurrence placement, selected-record deletion context and source semantics hold here too.
