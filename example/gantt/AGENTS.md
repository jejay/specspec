# Working on the Gantt example

This folder has an independent SpecSpec graph inside the parent checkout. Its
maintained standalone Git history is `history/gantt.bundle`; tests clone it into
disposable repositories. Do not add a nested `.git` here or reinitialize the graph.
Run the installed CLI from here, or `python -m specspec --root example/gantt ...`
from the repository root. The parent project's agent instructions also apply.

Read `_specspec` via `list`, `context`, and `impact` before changing code. Use
`add`, `update`, and `retire` for this checkout; format/API 3 has no `--expect` or
fingerprints. Manual changes are permitted by the product, not recommended. Intentions and conclusions
are distinguished by reasoning/relationships, not approval statuses. Withdraw the
complete obsolete dependent branch, retaining its explanations and original IDs.

`STORY.md` is explicitly fictional dialogue, not actual user authorization.
`history/cli.jsonl` records real CLI operations; `history/revisions.json` records
actual rebuilt fixture Git revisions and receipt ordinals. The fixture was
explicitly reconstructed through current CLI executions, not represented as the
untouched original history. Never invent receipts, backdate commits or claim
unrun checks. Implementation nodes link actual code/tests and explain omissions.

Use canonical five-byte padded Base64url IDs (40 bits, full trailing `=`) and
`<id><slug>.md` filenames. Keep only the current SpecSpec schema in tooling.
Obsolete surrounding SpecSpec graph revisions need not work. This Gantt history
is the rigorous Git regression corpus; every maintained commit must be compliant.

Before an authorized commit, stage the complete intended change and run BOTH:

```sh
python -m specspec hook check
python -m specspec --root example/gantt hook check
```

(The first command is from the parent repository root.) No hooks are installed.
Browser runtime uses local files only; do not add remote scripts or executable
project HTML. Tests run without installing app dependencies.
