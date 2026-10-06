# SpecSpec's own specification

This checkout is a ready-to-use example. Its working graph is in [`_specspec/`](../_specspec/);
do **not** run `init` here. Canonical nodes and schema conversion are maintained
through the Python CLI, not handwritten frontmatter or ad hoc hash updates.

## Review is a spectrum, not a node workflow

The [risk-proportionate review intention](../_specspec/a3cad33b-c1f9-4903-8394-9e6cd3cc5b73--risk-proportionate-review.md)
records the user's correction: review effort and confidence are not binary stages.
Users will often spend more attention on earlier intentions near the manifesto and
less on later, readily revisable conclusions. This is an expected allocation of
attention, not a depth-based score, quota, or guarantee that a deep choice is safe.
Risky or consequential details can deserve extra scrutiny anywhere.

When the user judges an implementation attempt worth its uncertainty and token
cost, the developed graph is as reviewed as needed for that attempt. There is no
additional individual node sign-off gate. Implementation and feedback can inform
the next revision; proceeding does not make a conclusion permanent or correct.

The graph keeps intentions and conclusions separately addressable through their
relationships, explanations, and provenance. [`INTENTION_SPEC.md`](../INTENTION_SPEC.md)
is the original, unchanged source. [`CONCLUSION_SPEC.md`](../CONCLUSION_SPEC.md)
records technical reasoning, not an approval queue. Git shows newness and changes
relative to the selected base; linked-source impact is informational review context.

## Approval-free schema revision

The separate [Git-newness and withdrawal conclusion](../_specspec/ca580dc7-c7fa-48bc-91b1-59243144a0bf--git-newness-and-withdrawal-schema.md)
chooses format/API version 2, an explicit managed migration, and a withdrawal flag:

- No `status: proposed` / `status: accepted`, accept command, approval filter,
  parent-approval dependency, or confidence slider.
- Ordinary nodes have no stored review stage. Optional `retired: true` means
  withdrawn, retained as design history. Restoration does not claim approval.
- A live node cannot depend on a retired parent; the manifesto cannot be retired.
  These are withdrawal/structure rules, not review obligations.
- Git added/changed/removed/renamed labels and source-impact hints stay derived.
- Old version-one Git revisions remain readable. Their original hashes are checked
  before approval fields are normalized away. No historical bytes are rewritten.
- `migrate --expect <fingerprint>` converts a valid v1 workspace in one journaled
  transaction, preserving IDs, paths, body bytes, links, sources, extensions, and
  unaffected comments. Ordinary writes require the explicit conversion first.

The repository's current graph was converted through that command. It retains
withdrawn explanations of the old [approval lifecycle](../_specspec/ff0c8e51-7aaa-4b13-97db-9623dc70d87c--proposal-lifecycle.md),
[version-one schema](../_specspec/d51d6da3-4142-4fc7-b593-d935ee5fdf6f--version-one-node-schema.md),
[review receipts](../_specspec/4607b83d-48dc-4452-a65f-bbd97209e46c--review-context-receipts.md),
and [TypeScript CLI candidate](../_specspec/d570abae-219c-4f3b-a5e4-3a4144fdfcee--typescript-cli-candidate.md).
Live dependents were explicitly reconnected before retiring superseded choices.
This is actual design history, not dummy display data or a new approval taxonomy.

## Neighborhood UI revision

The user-requested intentions remain separate from the implementation conclusions:

- [Focused editing without a sidebar](../_specspec/ee57a451-059d-426b-868e-e898c2503082--focused-node-editing.md).
- [Relationship context and all-depth downstream impact](../_specspec/2f6ee5bd-9014-4a0c-8677-53ecbab93f92--visible-relationship-context.md).
- [Selectable, non-approval graph colors](../_specspec/fc78af57-8c98-4dc5-9cc4-e590d4594cf2--selectable-graph-colors.md).
- [Readable arrows](../_specspec/e3494686-5da4-40f5-a622-f823c2e0c9b2--readable-relationship-arrows.md).
- Conclusions: [local focus/derived context](../_specspec/2b6a0e4e-f07f-4932-b58b-40348d4c3ac1--local-focus-and-derived-context.md)
  and [semantic fills/boundary routing](../_specspec/1f2e42c3-331f-4c1c-adc7-897f9bf2e004--semantic-colors-and-boundary-routing.md).

Downstream counts include every deeper descendant, not just the next generation.
Count unique IDs per child, excluding that child; overlapping child totals are not
additive. Metrics are potential impact, not a declaration of invalidation or review.
Distance-first fills and the existing node types replace the obsolete status mode.

## Blender-style canvas revision

Three user intentions describe the outcome without prescribing a library:

- [Left-to-right development](../_specspec/c93ab412-77b7-4849-a556-d8e3994b825b--left-to-right-graph-flow.md).
- [Viewport-independent arrangement](../_specspec/18d1da0d-8bc3-4d58-8720-8ce194a74d1b--viewport-independent-relational-layout.md).
- [Smooth navigation](../_specspec/a723adc8-d69d-4e60-8b4f-0997ab8f4d1d--smooth-node-canvas-navigation.md).

Separate conclusions choose [Dagre/D3 layered routing](../_specspec/fbaee7c1-4c20-47ab-afd2-ae0503d428b5--dagre-layered-world-and-curved-links.md)
and [an edit-safe camera](../_specspec/d70cdad5-5e03-4200-ac75-74cf6514e56c--d3-camera-and-edit-safe-gestures.md).
The [library rationale](node-canvas.md) documents alternatives and limitations.
A library choice remains revisable without rewriting the user intention.

## Origin density and connection correction

The follow-up intention asks for [dense development near the manifesto](../_specspec/cbcde9ec-5c0b-480e-9401-cf50a4bfeb96--manifesto-centered-graph-density.md).
The [arrow intention](../_specspec/e3494686-5da4-40f5-a622-f823c2e0c9b2--readable-relationship-arrows.md)
asks for minimum visible strength at low zoom, no round connectors, and natural
curved-to-arrow transitions. Separate conclusions choose:

- [Earliest source ranks](../_specspec/4254f33d-ce29-4e33-830e-28a8edd2a51c--root-anchored-earliest-ranks.md).
- [Compact rank-preserving placement](../_specspec/c2ed5444-b7b2-4c2a-901c-ab1ba64e5e54--compact-rank-backbone-placement.md).
- [Scale-stable tangent arrows](../_specspec/10ef1cdc-62a6-4212-8387-704d3cbbeeb4--scale-stable-tangent-arrow-connections.md).

The earlier 42-node snapshot's six immediate root children occupy rank one rather
than ranks 1–5 under the preceding heuristic. This is observed improvement, not a
universal density guarantee or a review score. Ranking respects every parent and
remains distinct from shortest-hop context. All relationships remain rendered.

## Entry points

| What to inspect | Node |
| --- | --- |
| Project purpose | [Manifesto](../_specspec/b8983d8c-3dc0-4588-b74f-17721bfc4f5c--specspec-manifesto.md) |
| Review budget and implementation risk | [Risk-proportionate review](../_specspec/a3cad33b-c1f9-4903-8394-9e6cd3cc5b73--risk-proportionate-review.md) |
| User-controlled exploration | [Revisable conclusions](../_specspec/c0943883-e3cb-4de9-8c5e-6aeb4a37dd06--revisable-conclusions.md) |
| Current file/API/migration choice | [Approval-free schema](../_specspec/ca580dc7-c7fa-48bc-91b1-59243144a0bf--git-newness-and-withdrawal-schema.md) |
| Managed writes | [Recoverable mutations](../_specspec/624d0f3c-391d-4575-be87-3001f16052f6--recoverable-workspace-mutations.md) |
| Shared backend | [Python JSON backend](../_specspec/6c457b0a-654e-4545-a4b4-667f467be4f3--shared-python-json-backend.md) |
| Git code and tests | [Git adapter](../_specspec/cc058342-0f01-4dc1-99bc-439b445c5a04--git-adapter-implementation.md) |
| Editor code and tests | [VS Code implementation](../_specspec/bf8d3c4f-8d01-4e66-9ff4-9413deffef78--vscode-editor-implementation.md) |
| Self-validation and documentation | [Repository dogfooding](../_specspec/36c1ce4f-e242-494c-9566-e462b51a053e--repository-dogfooding-implementation.md) |

## Explore and edit

Install the development environment as described in the [README](../README.md):

```sh
python -m specspec validate --warnings-as-errors
python -m specspec list --live --json
python -m specspec list --retired --json
python -m specspec context cc058342-0f01-4dc1-99bc-439b445c5a04 --json
python -m specspec impact 003d697b-4104-4fdf-8e05-0db572c436d0 --json
python -m specspec export --format mermaid
python -m specspec diff --base HEAD --json
```

Prepare replacement body text outside `_specspec`, then apply it through the CLI:

```sh
python -m specspec update <node-id> --body <body-file> --expect <displayed-fingerprint>
python -m specspec validate --warnings-as-errors
python -m specspec diff --base HEAD --json
```

Use `add --parent <id> ...` for a separate conclusion rather than rewriting an
intention to make one solution inevitable. `update --parent` replaces the complete
parent list. Keep implementation `--sources` current when code/tests move.

Review the graph/code diff to the level warranted by uncertainty and impact. There
is no accept step. Use `retire <id>...` for withdrawn explanations and `restore`
when reconsidering them; batches must leave live dependencies valid. Withdrawal
is not a statement that the node did not receive enough review.

Use `context --include-retired` to inspect a withdrawn node's full ancestry.
Commit-to-commit comparisons use `diff --base <ref> --target <ref> --json` without
checkout. Legacy revisions render through the normalized model, read-only.

## Git, checks, and recovery

CI validates this repository graph with warnings as errors. Repository tests
exercise the real graph without freezing its UUIDs, counts, or design choices.
Migration tests use original tool-managed v1 fixture blobs, check their old hashes,
exercise interrupted conversion/recovery, and compare staged/historical v1 and v2
snapshots in disposable repositories. No test installs hooks in this checkout.

Local hooks remain opt-in:

```sh
python -m specspec hook install
# Stage the complete intended graph and linked implementation change normally.
python -m specspec hook check
```

The checker validates the exact index, not unstaged working files. Stage all
interdependent schema changes together. Installation preserves existing hooks and
respects `core.hooksPath`; chain the check manually when another hook exists.
Neither the CLI nor editor automatically stages, commits, or changes branches.

If interrupted, retain `.specspec-local/` and run `recover`. Confirm no writer is
running before `recover --force-lock`. A migration journal restores the original
whole schema; mixed partially converted files are never blessed by a read.

## Open the graph in VS Code

After installing `.[dev]` into `.venv`, run `npm --prefix vscode ci`, open the
repository root, and launch **Run SpecSpec on this repository** (F5). Alternatively
launch **Run SpecSpec Extension** from `vscode/`. Both use a dedicated development
workspace/profile and explicitly select the local Python interpreter. Normal
launches retain workspace trust; trust this repository when prompted.

Stop old sessions before relaunching changed code. Empty windows offer a folder
picker, subfolders resolve the nearest project, and startup errors appear in
notifications and **View → Output → SpecSpec**. CLI and extension must both use
JSON API 2. Legacy workspaces offer a confirmed **Migrate specification** action,
but history is never migrated and dirty drafts never silently rebase.

Click a node to edit inside its expanded neighborhood card. **Save node** writes
without approval metadata. **Retire**/**Restore** change withdrawal only. Parent
cards show manifesto distance; child cards show all-depth downstream impact.
**Total graph**/**Resume draft** preserve the same form, caret, and original
fingerprint. **Color by** selects distance or existing node type. Git badges and
withdrawn labels are separate; green arrows mean added relationships, not approval.

Arrangement remains relation-derived and viewport-independent. Middle/background
drag pans, wheel/pinch zooms, and buttons/keyboard actions frame the view. Cameras,
colors, ranks, and counts remain presentation state, not canonical metadata.

`npm --prefix vscode test` covers host/DOM/model regressions. `npm --prefix vscode
run test:host` drives installed VS Code through a loopback Chromium debugger with
a disposable profile, requiring Node 22+. It checks approval-free controls,
withdrawn labels, both fill modes, canvas geometry, pan/zoom, drafts, native gestures,
and resized curve clearance. Only this isolated automated host disables trust.
Screenshots can be saved with `SPECSPEC_SCREENSHOT_DIR`. Full manual mutation and
revision-picker workflows and remote CI remain separate verification boundaries.
