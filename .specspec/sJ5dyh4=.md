---
id: sJ5dyh4=
type: requirement
parents:
- 0dvOn3A=
---
# Render concise readable results by default

Results are plain readable text and Markdown, for a person at a terminal and for a language model alike, and they are the same whether the output goes to a terminal or is redirected. A reading of nodes gives for each node the full ID, the type, the heading and its relationships. A read of a single node, or of nodes with their ancestors, shows the metadata under labels and the complete text of each node. A query with ancestors includes the ancestors it needs in the fixed order of the graph and names the further surrounding nodes by ID alone, with their text left out. A byte limit that is given explicitly counts the output as it is actually written, and a result beyond the limit fails as a whole.

An edit names the changed nodes by full ID and reports the affected scope and the warnings, and a check reports counts and diagnostics. Results go to standard output and diagnostics for people to standard error. Terminal control characters in project text are printed in a visible escaped form, so that a terminal shows them and never acts on them. Whitespace that belongs to the content is kept. The text before and after an edit to an editor's own document is given exactly, and the editor writes those bytes. Node records and review patches use LF line ends, and a change of the newline encoding alone is reported as no change. Raw reads, the checks of original bytes in a transaction and recovery work on the exact bytes. The machine form is chosen explicitly with `--json`: a pipe gets the same text as a terminal, and people, agents and language models share one interface.
