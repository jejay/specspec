# Working on the Gantt specification and app

The graph records current owner outcomes, separately reasoned conclusions and
actual implementation mappings in positive language. Git predecessor trees and
commit messages carry changed reasoning, removal explanations and execution history.
The manifesto defines the planning purpose; requirement relationships express the
intention-conclusion spectrum; implementation leaves link actual code/tests.

## Planning phases

Inspect owner working/index specification changes before action. Preserve manual
owner input before agent edits with a separate `Owner specspec changes: <understanding>`
commit. Validate its exact intended staged graph.

In tandem planning, understand the product brief and distinguish intention from
suggested solution. Discuss significant removals/splits/modifications promptly,
offer concise corrected overviews and deepen consequential reasoning. Graph edits
belong to requested agent planning; rounds may be skipped with sufficient context.

On a request to change the specification, use saved graph/context/impact and owner
understanding to plan a precise implementation-mature graph through `add`, `update`
and `delete`. Keep positive current bindings and independently revisable choices.
Delete exactly selected files. Inspect retained faults with query --issues and diff
--with-context; rewrite, split, relink or explicitly remove conclusions deliberately.
Validate the exact intended index and commit `Agent specspec changes: <description>`.

Implementation closes depth gaps under existing intentions with conclusions and
code mappings. Owner planning decides breadth/removal changes. Report contradictions,
consistent-subset decisions and consequences; a proposal branch can hold a suggested
resolution. Working tests give bounded evidence for review.

## Independent workspace and portable fixture

In the SpecSpec checkout, `example/gantt` is a tracked fixture snapshot. Git here
uses SpecSpec's development repository. Its parent instructions apply. For temporal
experiments, run `python example/gantt/history/checkout.py <new-external-destination>`
and open that independent clone. Tests/CI clone `history/gantt.bundle`. Existing
manual experiments remain preserved; the helper reserves new destinations and
retains partial clones. Independent clones own their Git metadata/index.

Use the global `specspec` command installed with uv tools or pipx. The canonical
`.specspec/` directory contains direct node files; `.specspec-local/` is runtime state.
Init supplies a packaged root `AGENTS.md` when absent and preserves existing instructions.
Ordinary authoring supplies literal `-m/--message` paragraphs to init/add/update.
Combine add/update/delete steps in one invocation and transaction; `add --as NAME`
and `--parent '$NAME'` connect new nodes, including forward references. Other commands
stay standalone. Explicit integration body inputs and the UI's existing transports
retain their roles.

Use `query ID --max-distance 0 --with-ancestors` and `query ID`
before code changes. Query's optional ancestor completion follows every parent path
after selection; added bindings consume no metric quota. `specspec diff` supplies
canonical-file hunks; ordinary `git diff` supplies code patches. Read untracked
files explicitly and coordinate with unsaved native documents.
Canonical node format 7 and application API 7 use
canonical padded Base64url IDs over five bytes, including `=`, and `<id>.md`
files. Each direct parent adds ancestry: a direct parent cannot already be an
indirect parent. Review ripple effects using both old and new graphs, including
ancestry lost by reparenting. Implementation leaves contribute bounded realization.
Valid manual Markdown is usable; graph-aware CLI/UI edits are recommended.
Delete removes exactly selected files, preserving descendants and their parent
references. Uncommitted selected files warn; --require-valid checks a complete final
candidate. Invalid intermediate graphs remain inspectable/editable. Explain reasons in Git. Default workspace compares
to HEAD, keeping committed D ghosts through staging until commit.

`history/cli.jsonl` contains actual current CLI inputs/results. `revisions.json`
records actual stage commits/receipt ordinals. Agent specification checkpoints
precede each runnable stage's code. `STORY.md` is optional fictional product-brief
illustration; artifact checks supply execution evidence. Preserve stage reasoning
in Git and scope future candidates distinctly from delivered prototype behavior.

Every node-schema change reconstructs the entire maintained example history under
today's grammar: all refs, predecessor/deleted nodes, source anchors, actual receipts,
ledger, bundle and tracked snapshot. Validate every revision with current tools.
See `history/WALKTHROUGH.md`. SpecSpec development history retains its original
commits, and existing clones retain their experiments.

Before an authorized SpecSpec-checkout commit, run from its root:

```sh
specspec check --staged --sources
specspec --root example/gantt check --staged --sources
```

In a standalone clone, check its own exact index. Git hook/CI setup is owner-managed;
call check --staged while preserving existing hook commands. Browser runtime uses local scripts and literal project
text; model tests run with Node and browser tests use an installed browser.
