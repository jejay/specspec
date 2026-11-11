---
id: Pek6TGE=
type: requirement
parents:
- qTT_OhY=
---
# End every tool-written node document with a newline and keep its trailing content

A consistent final newline makes the Markdown that tools generate ordinary line-oriented text, and the configuration of checkout and editor stays under the owner's control.

Every node document that `init`, `add`, `update`, a combined edit or an edit plan for an editor form produces ends with a newline. The newline of the document's own style is appended only when the complete text has no final newline of any kind, and a new document uses LF. A final newline that exists, trailing spaces and deliberate trailing blank lines are kept. The rule belongs to serialization and applies whichever field of body or metadata was edited, also to the replacement of a selected passage and to an update of metadata alone.

The newline ends the complete Markdown document and adds no text to its body. An empty body in an editor's repair form stays empty when the closing frontmatter delimiter already ends the document. An appended newline counts toward the byte limit of the serialized or planned document, which is checked before a write or a document edit.

Raw reads, comparisons, the checks of original bytes and recovery see exactly how a document ends. A node without a final newline that was written by hand, staged or committed is readable and valid in the current format, and an explicit write by a tool applies the rule to it. A missing final newline that a write adds is a real change of the logical text. A save in a raw text editor belongs to the host. The rule lives in specspec's own writes alone: the settings of repository and editor and the Git attributes stay as the owner has them. Linked implementation files keep their format.
