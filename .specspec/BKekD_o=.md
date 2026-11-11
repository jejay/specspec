---
id: BKekD_o=
type: requirement
parents:
- rgGL5FY=
---
# Take node text from literal message paragraphs or, without them, from standard input

`init`, `add` and `update` accept `-m`/`--message` any number of times, one paragraph each. The values are joined with exactly two LF characters, and their words, their Unicode and their whitespace are kept literally. The newline encoding follows the document that is written, and serialization appends a final newline only where the complete document lacks one. A file name or a dash given to `-m` is literal text.

Without messages, `init` and `add` read the text from standard input, as UTF-8 within the size limit of a node. An `update` without messages and without replacements takes the text on standard input as its whole new body. When standard input is empty and the update names parents or sources, the body stays as it is, and at an interactive terminal such an update proceeds without waiting for text. An `-m` with empty text counts as an edit and is checked against the schema like any other, so an empty body is rejected. `--replace` works on selected passages of the original body and leaves standard input unread. A file supplies the text through shell redirection, which is the only way a file comes in. In a chain, nonempty text on standard input needs exactly one step that can take it, and every step is parsed and checked before anything is read or written. A chain that changes only metadata works without any input.

Both graph editors pass the complete body on standard input when they save through the writer, and they use no option for the body. A form of a VS Code node document receives an edit plan that writes nothing, and VS Code saves the document. A reviewed deletion plan and the private application channel have inputs of their own. The limits on arguments, on one body and on all the text of an invocation are separate, each with an error of its own, and the limit of an operating system on a command line applies apart from them.
