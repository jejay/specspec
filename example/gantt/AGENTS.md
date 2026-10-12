# Working on the Gantt example

In the SpecSpec checkout, this folder is a tracked graph/runtime fixture snapshot,
not an independent Git workspace: Git here finds the parent's development history.
For manual Git/UI experiments, run `python example/gantt/history/checkout.py` from
the SpecSpec root and open the resulting `~/Projects/specspec-examples/gantt` clone.
Tests clone `history/gantt.bundle` into independent disposable repositories. Do not
add nested `.git` here or reinitialize the graph. The parent's instructions apply
when editing its tracked fixture; in a standalone clone, use that clone's own index.

Read `_specspec` via `list`, `context`, and `impact` before changing code. Use
`add`, `update`, and `retire` for this checkout; format/API 4 has no `--expect` or
fingerprints. Manual changes are permitted by the product, not recommended. Intentions and conclusions
are distinguished by reasoning/relationships, not approval statuses. Withdraw the
complete obsolete dependent branch, retaining its explanations and original IDs.

No fabricated AI conversation is required: plausible graph construction/revision
is enough. The retained `STORY.md` is optional fictional illustration, not actual
user authorization or a prerequisite for additional example projects.
`history/cli.jsonl` records real CLI operations; `history/revisions.json` records
actual rebuilt fixture Git revisions and receipt ordinals. The fixture was
explicitly reconstructed through current CLI executions, not represented as the
untouched original history. Never invent receipts, backdate commits or claim
unrun checks. Implementation nodes link actual code/tests and explain omissions.

Use canonical five-byte padded Base64url IDs (40 bits, full trailing `=`) and
`<id><slug>.md` filenames. Keep only the current SpecSpec schema in tooling.
Obsolete surrounding SpecSpec graph revisions need not work. This Gantt history
is the rigorous Git regression corpus; every maintained commit must be compliant.
Whenever the node schema changes, reconstruct the ENTIRE maintained history as if
all stages had always used today's SpecSpec. Refresh all refs, retired nodes,
receipts, ledgers, bundle and tracked snapshot together, then verify every revision.
Updating only HEAD is insufficient. See `history/WALKTHROUGH.md`. Save experiments
before explicitly recreating stale clones; never reset them automatically or
rewrite unrelated SpecSpec development history.

Before an authorized commit, stage the complete intended change and run BOTH:

```sh
python -m specspec hook check
python -m specspec --root example/gantt hook check
```

(Both commands above are from the SpecSpec root for its tracked fixture change.)
In a standalone example clone, validate only its own staged graph. No hooks are installed.
Browser runtime uses local files only; do not add remote scripts or executable
project HTML. Tests run without installing app dependencies.
