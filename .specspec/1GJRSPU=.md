---
id: 1GJRSPU=
type: requirement
parents:
- kiRE62k=
- 4626uI8=
---
# Replace passages that each match exactly one place of the original body

`update` accepts `--replace OLD NEW` any number of times, in place of a whole body from messages or from standard input. OLD is nonempty and matches exactly one place of the original body under the default comparison rules for line ends and for the wrapping of prose. Occurrences that overlap and every layout that the rules permit count when uniqueness is checked. All pairs of an update refer to that same original body, match ranges that are disjoint and produce one candidate, so that no pair matches text that another pair inserted. An empty NEW removes the passage. NEW is taken literally, with its newlines turned into the encoding of the document.

Every logical character of the body outside the matches stays as it is, trailing blank lines included, and the document ends with the final newline that the tools write. Words, case, Unicode, indentation and blank lines are compared exactly. The comparison of OLD tolerates the standard line ends and the soft line breaks of Markdown prose, and storing adapts the newline encoding alone. Matching and replacing happen under the writer lock, on the node as it is freshly read and identified there. A replacement changes the body alone, and parents, sources and other metadata are edited through their own options. An OLD that is missing, that matches more than once or that overlaps another match rejects the complete invocation before any node file is written, with a diagnostic that names the node file.

An update takes its new body from one source alone: from replacements, from messages or from standard input. The syntax, a conflict between these sources and the limits on replacement input are checked for all steps before standard input is read. Both values of a pair are literal even when they equal a command name or a flag. A step with replacements is part of the same candidate as the other steps of its chain, with the same preview, the same optional check of the final graph, the same consent to deletions, the same checks of original bytes and the same recovery from the journal.

These limits apply:

- at most 1024 replacement pairs in one invocation, counted over all its editing steps
- 16 MiB for the UTF-8 bytes of all OLD and NEW values together with the other body input of the invocation
- 1 MiB for each OLD or NEW value and for the resulting node file

The limit of an operating system on arguments applies independently. OLD and NEW are always given as argument text. The one option `--replace` provides this default comparison completely, and no further option is needed for it.
