---
id: AY1g-sU=
type: requirement
parents:
- h3zqGZU=
---
# Read each query binding on one line with paragraph separators

The ordinary readable query projects each current or deleted binding into one line,
retaining every content character while replacing its newline runs. Normalize CRLF
to LF, replace a single LF with one space and replace a run of two or more LFs with
" ¶ ". Apply the same rule to leading and trailing runs. Retain other whitespace,
Markdown markers, Unicode and headless text. The one-line projection is the default
presentation. Version selection and complete structured output retain their contracts.

A space at a soft line break keeps adjacent words separate. The projection is a
compact text reading, rather than a Markdown renderer: list items, code lines and
hard breaks follow the same literal newline rule. Exact original bodies and layout
remain in structured comparison records and node files; diff supplies literal changes.
Keep shared terminal-control escaping, complete untruncated text, full parent headers,
last-occurrence placement, selected-record deletion context and source semantics.
