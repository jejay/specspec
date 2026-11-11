---
id: Pek6TGE=
type: requirement
parents:
- qTT_OhY=
---
# Terminate tool-written node documents without trimming trailing content

A consistent terminator makes generated Markdown ordinary line-oriented text while
leaving checkout and editor configuration under owner control.

Every canonical node document produced by managed init/add/update, composed edits
or native form edit plans ends with a newline. Append the document's local newline
only when its complete text lacks any final newline; new documents use LF.
Preserve existing terminators, trailing spaces and intentional trailing blank lines.
The convention applies to serialization, independently of which body/metadata field
was edited, including selected-passage replacement and metadata-only updates.

Terminate the complete Markdown document, rather than inventing text in its body.
An empty native repair body remains empty when the closing frontmatter delimiter
already terminates the document. Include any appended terminator in the final
serialized/planned byte limit before writes or document edits.

Raw reads, comparison, original-byte guards and recovery retain exact EOF evidence.
Existing unterminated manual, staged or historical nodes remain readable and valid
under the current schema; an explicit tool write applies the output convention.
A repaired missing terminator is a real logical text change. Native raw-editor
saves retain host ownership; no repository/editor settings or Git attributes are
installed to impose this convention. Linked implementation files keep their format.
