---
id: BKekD_o=
type: requirement
parents:
- rgGL5FY=
- 7tMgRa8=
- 0piRXe0=
---
# Use literal message paragraphs or automatic standard input

Init/add/update accept repeatable -m/--message paragraphs. Join repeated values with
exactly two LF characters, preserving literal words, Unicode and whitespace. Newline
encoding follows the target document, and serialization appends only a missing
complete-document terminator. A filename or dash passed to -m is literal text.

When messages are absent, init and add read bounded UTF-8 standard input. Updates
without messages or replacements accept a whole-body stdin replacement. Empty stdin
with explicit metadata edits retains the body; a metadata-only interactive update
need not wait for text. Explicit empty -m remains a schema-checked edit. --replace
uses selected original passages and does not consume stdin. There is no body-file
option: shell redirection supplies files. Multiple eligible steps cannot share a
nonempty stdin payload ambiguously; parse and preflight every step before reads or
writes. Metadata-only chains with no input remain possible.

Both managed UIs pass complete body text on stdin without a body option. Native VS
Code forms retain non-writing plans and native persistence. Reviewed deletion plans
and private application channels retain their independent inputs. Argument, body,
aggregate and operating-system limits remain separate and explicit.
