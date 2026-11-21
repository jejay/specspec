---
id: Vrh8YAI=
type: requirement
parents:
- IMRW29M=
---
# Keep the guide in one instructions file and import it into CLAUDE.md where needed

init and specspec guide put the guide into one file in the project root: the file among AGENTS.md, CLAUDE.md and .claude/CLAUDE.md that already holds a specspec guide, otherwise the first of them that exists in this order. A project with none of them gets a new AGENTS.md.

When the guide is in AGENTS.md and the project also has a CLAUDE.md, .claude/CLAUDE.md or CLAUDE.local.md, Claude Code reads only those. The first of them that exists then gets an import line appended in its own line endings: @AGENTS.md, or @../AGENTS.md in .claude/CLAUDE.md, because Claude Code resolves an import relative to the file that holds it. Nothing is appended when one of them already holds such an import outside backticks or is the same file as AGENTS.md.

Both commands name the file that holds the guide and the file that received the import.
