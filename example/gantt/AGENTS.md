# Working on the Gantt example

This folder is an independent SpecSpec project inside the parent Git repository.
Do not initialize it again, create a nested repository, or edit canonical Markdown.
Run the installed CLI from here, or `python -m specspec --root example/gantt ...`
from the repository root. The parent project's agent instructions also apply.

Read `_specspec` via `list`, `context`, and `impact` before changing code. Use
`add`, `update`, and `retire` for this checkout; format/API 3 has no `--expect` or
fingerprints. Manual changes are permitted by the product, not recommended. Intentions and conclusions
are distinguished by reasoning/relationships, not approval statuses. Withdraw the
complete obsolete dependent branch, retaining its explanations and original IDs.

`STORY.md` is explicitly fictional dialogue, not actual user authorization.
`history/cli.jsonl` records real CLI operations; `history/revisions.json` records
real Git revisions. Never invent receipts, backdate commits, or claim unrun checks.
Implementation nodes link actual code/tests and explain omissions.

Before an authorized commit, stage the complete intended change and run BOTH:

```sh
python -m specspec hook check
python -m specspec --root example/gantt hook check
```

(The first command is from the parent repository root.) No hooks are installed.
Browser runtime uses local files only; do not add remote scripts or executable
project HTML. Tests run without installing app dependencies.
