---
id: BKekD_o=
type: requirement
parents:
- rgGL5FY=
- 7tMgRa8=
- 0piRXe0=
---
# Use literal message paragraphs and inline JSON batches

init/add/update expose repeatable -m/--message arguments. One message is preserved
literally; repeated values are joined with exactly two LF characters, preserving
all supplied whitespace, Markdown headings and line endings. Values such as dash
or a filename are text. Omitting the body on update retains its current bytes;
explicit empty text remains an explicit schema-checked edit. Combined message and
integration body sources fail before reads or writes. Document size checks apply.

apply --edits-json accepts one bounded JSON object with the existing explicit edit
and ephemeral alias grammar. Inline edits supply body text. Reject body_file in
this argument mode before opening a file. Duplicate JSON fields, conflicting edits,
normal deletion consent, dry-run, optional whole-result validity and recoverable
transaction boundaries retain their established meanings.

Less-prominent integration options are --body FILE|- on init/add/update and
apply --plan FILE|-. File-based plans retain body_file paths relative to their plan;
stdin plans use the launch directory. Public help focuses on messages/inline JSON.
Positional init/apply payloads are rejected, keeping text and file interpretation
explicit. Reviewed deletion-plan stdin and API-7 one-shot/stream channels retain
their current contracts and both host adapters remain unchanged.

Argument transport has operating-system/shell limits independent of the 1 MiB node
and 16 MiB bulk/request limits. Long argv may fail before the tool starts. Bulk
integration inputs remain available without splitting or silently truncating edits.
The current protocol remains API 7 and canonical node format remains 7.
