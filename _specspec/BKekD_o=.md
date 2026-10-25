---
id: BKekD_o=
type: requirement
parents:
- rgGL5FY=
- 7tMgRa8=
- 0piRXe0=
---
# Use literal message paragraphs and explicit integration body inputs

init/add/update expose repeatable -m/--message arguments. One message is preserved
literally; repeated values are joined with exactly two LF characters, preserving
all supplied whitespace, Markdown headings and line endings. Values such as dash
or a filename are text. Omitting the body on update retains its current bytes;
explicit empty text remains an explicit schema-checked edit. Combined message and
integration body sources fail before reads or writes. Document size checks apply.

Less-prominent integration --body FILE|- on init/add/update supplies explicit UTF-8
body inputs. Help focuses on literal messages. Positional init payloads are rejected,
keeping text and file interpretation explicit. Reviewed single-deletion-plan stdin
and API-7 one-shot/stream channels retain their current contracts and both host
adapters retain their communication and persistence owners.

Argument transport has operating-system/shell limits independent of the 1 MiB node
and 16 MiB aggregate body/request limits. Long argv may fail before the tool starts.
Explicit body files/stdin accommodate large bodies without splitting, truncating or
silently redirecting edits. The current protocol is API 7 and node format is 7.
