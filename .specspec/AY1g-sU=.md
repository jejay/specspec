---
id: AY1g-sU=
type: requirement
parents:
- h3zqGZU=
---
# Print each node's text on one line with a pilcrow between paragraphs

By default the readable `query` prints the text of each current or deleted node on one line. Every character of the content is kept, and only the runs of newlines are replaced. Newline encodings are normalized to LF, a single LF becomes one space, and a run of two or more LFs becomes a pilcrow `¶` with one space on each side. The same rule applies to runs at the start and at the end of the text. All other whitespace, the Markdown markers, Unicode and a text without a heading stay as they are.

The space at a soft line break keeps the neighbouring words apart. The line is a compact reading of the text and takes Markdown as literal text: list items, lines of a code block and hard breaks follow the same rule for newlines. The complete logical layout is in the structured records of the comparison, with CRLF turned into LF. The node files and a raw `query` have the body with its physical line ends, and `diff` shows the changes of the logical content whatever the newline encoding. The line holds the complete text, however long, and passes through the shared escaping of terminal control characters.
