# SpecSpec's own specification

This checkout is a ready-to-use example. Its working graph is in [`_specspec/`](../_specspec/);
do **not** run `init` here. All initial canonical files and status transitions were
created through the Python CLI, not handwritten frontmatter or ad hoc hash updates.

## Review status

The initial graph contains one manifesto, twelve accepted requirement nodes
transcribed from the user's intentions/self-hosting request, ten proposed technical
requirements, one retired candidate, and seven implementation records. It has
multi-parent relationships, including parents at different distances from the root.
These counts describe the initial migration, not invariants for future edits.

- **Accepted:** the user's stated project constraints, not blanket approval of an
  architecture. The manifesto summarizes `INTENTION_SPEC.md`.
- **Proposed:** technical choices and implementation mappings awaiting individual
  review. A proposal can have working code and tests without being approved.
- **Retired:** the original TypeScript CLI candidate, withdrawn when the user required
  Python. This is actual design history, not a dummy node added solely for display.

[`INTENTION_SPEC.md`](../INTENTION_SPEC.md) and
[`CONCLUSION_SPEC.md`](../CONCLUSION_SPEC.md) remain the original intention/design
context. Their contents were not wholesale converted into accepted decisions.
The canonical nodes carry provenance and explicit parent relationships; follow them
when reviewing a particular feature. Deferred review receipts have a proposed node
but no implementation record claiming that they exist.

## Neighborhood UI revision

The subsequent user-requested UI revision adds four accepted product intentions,
kept distinct from two proposed technical conclusions:

- [Focused editing without a sidebar](../_specspec/ee57a451-059d-426b-868e-e898c2503082--focused-node-editing.md).
- [Relationship context and potential downstream impact](../_specspec/2f6ee5bd-9014-4a0c-8677-53ecbab93f92--visible-relationship-context.md).
- [Selectable graph colors](../_specspec/fc78af57-8c98-4dc5-9cc4-e590d4594cf2--selectable-graph-colors.md).
- [Readable arrows](../_specspec/e3494686-5da4-40f5-a622-f823c2e0c9b2--readable-relationship-arrows.md).
- Proposed: [local focus and derived context](../_specspec/2b6a0e4e-f07f-4932-b58b-40348d4c3ac1--local-focus-and-derived-context.md).
- Proposed: [semantic colors and boundary routing](../_specspec/1f2e42c3-331f-4c1c-adc7-897f9bf2e004--semantic-colors-and-boundary-routing.md).

The user clarified that the child count includes **all deeper descendant subgraphs**,
not only the next generation. The chosen DAG convention counts unique downstream
IDs per child, excluding that child; overlapping child totals are not additive.
The editor implementation now links these conclusions as well as its previous
requirements. Working code and tests do not accept the technical proposals.

## Blender-style canvas revision

The next editor request introduces three accepted intentions, without approving
an implementation library:

- [Left-to-right graph development](../_specspec/c93ab412-77b7-4849-a556-d8e3994b825b--left-to-right-graph-flow.md).
- [Viewport-independent relational layout](../_specspec/18d1da0d-8bc3-4d58-8720-8ce194a74d1b--viewport-independent-relational-layout.md).
- [Smooth panning and zooming](../_specspec/a723adc8-d69d-4e60-8b4f-0997ab8f4d1d--smooth-node-canvas-navigation.md).

The existing [arrow intention](../_specspec/e3494686-5da4-40f5-a622-f823c2e0c9b2--readable-relationship-arrows.md)
now prefers curves. Two separate **proposed** conclusions link the new intentions
to [Dagre/D3 layered routing](../_specspec/fbaee7c1-4c20-47ab-afd2-ae0503d428b5--dagre-layered-world-and-curved-links.md)
and [a separate edit-safe camera](../_specspec/d70cdad5-5e03-4200-ac75-74cf6514e56c--d3-camera-and-edit-safe-gestures.md).
Earlier neighborhood/routing conclusions were amended to remove obsolete row and
orthogonal-link choices, while preserving metric and editing behavior. The editor
implementation links both new proposals. The current graph has 42 nodes; that is
not a fixed requirement. [Library research/rationale](node-canvas.md) is noncanonical
implementation context, not an additional source of approval.

## Entry points

| What to inspect | Node |
| --- | --- |
| Project purpose | [Manifesto](../_specspec/b8983d8c-3dc0-4588-b74f-17721bfc4f5c--specspec-manifesto.md) |
| User-controlled exploration | [Revisable conclusions](../_specspec/c0943883-e3cb-4de9-8c5e-6aeb4a37dd06--revisable-conclusions.md) |
| File-format proposal | [Version-one schema](../_specspec/d51d6da3-4142-4fc7-b593-d935ee5fdf6f--version-one-node-schema.md) |
| Managed-write proposal | [Recoverable mutations](../_specspec/624d0f3c-391d-4575-be87-3001f16052f6--recoverable-workspace-mutations.md) |
| Backend shared with VS Code | [Python JSON backend](../_specspec/6c457b0a-654e-4545-a4b4-667f467be4f3--shared-python-json-backend.md) |
| Real Git code and tests | [Git adapter implementation](../_specspec/cc058342-0f01-4dc1-99bc-439b445c5a04--git-adapter-implementation.md) |
| Real editor code and tests | [VS Code implementation](../_specspec/bf8d3c4f-8d01-4e66-9ff4-9413deffef78--vscode-editor-implementation.md) |
| Self-validation and documentation | [Repository dogfooding](../_specspec/36c1ce4f-e242-494c-9566-e462b51a053e--repository-dogfooding-implementation.md) |
| An unimplemented candidate | [Review-context receipts](../_specspec/4607b83d-48dc-4452-a65f-bbd97209e46c--review-context-receipts.md) |
| A withdrawn candidate | [TypeScript CLI](../_specspec/d570abae-219c-4f3b-a5e4-3a4144fdfcee--typescript-cli-candidate.md) |

The remaining implementation records cover parsing/integrity, graph traversal,
workspace transactions, and Python CLI packaging. Each references actual project
files and verification rather than embedding source-code copies.

## Explore from the repository root

Install the development environment as described in the [README](../README.md), then:

```sh
python -m specspec validate --warnings-as-errors
python -m specspec list --status proposed --json
python -m specspec show b8983d8c-3dc0-4588-b74f-17721bfc4f5c --descendants --json
python -m specspec context cc058342-0f01-4dc1-99bc-439b445c5a04 --json
python -m specspec impact 003d697b-4104-4fdf-8e05-0db572c436d0 --json
python -m specspec export --format mermaid
python -m specspec diff --base HEAD --json
```

The Git implementation's context is a useful multi-parent example: it includes
both an accepted Git-comparison requirement and more detailed proposed parents.
The managed-edit requirement's impact reaches multiple code modules and the editor.
Source-file edits also appear in `diff` through the implementation records.

Until the first graph commit, the HEAD comparison shows the graph as newly added.
After committing it normally, the same command compares incremental changes.
Commit-to-commit comparisons use `diff --base <ref> --target <ref> --json`.

## Edit and review

Use the graph editor, or prepare replacement **body text** in a file outside
`_specspec` and apply it through the CLI:

```sh
python -m specspec update <node-id> --body <body-file> --expect <displayed-fingerprint>
python -m specspec validate --warnings-as-errors
python -m specspec diff --base HEAD --json
```

Use `add --parent <id> ...` for a new candidate rather than rewriting a parent to
make one solution unavoidable. Updating `--parent` replaces the entire parent list.
Update implementation `--sources` when their code or tests move.

After explicit human review, `accept <id>...` names the decisions being approved;
proposed parents must be accepted first or named in the same reviewed batch.
The tool does not silently accept ancestors. Retire withdrawn candidates without
leaving live descendants dependent on them. Do not approve a whole subtree merely
because one of its implementation tests passed.

Keep the canonical node changes and linked implementation/documentation changes
in the same review. [`AGENTS.md`](../AGENTS.md) describes the corresponding agent
workflow. No additional index, sidecar, or generated diagram is canonical.

## Git and CI

CI runs `python -m specspec validate --warnings-as-errors` after installing this
checkout's package. `tests/test_repository_spec.py` validates and consumes the real
graph, checks unmanaged-edit detection in memory, and checks staged copies in a
disposable Git repository. It does not freeze UUIDs, counts, or approval states.

Local hooks remain opt-in:

```sh
python -m specspec hook install
# Stage the complete intended specification change and its linked files normally.
python -m specspec hook check
```

The checker validates the index, so unstaged new nodes are not a staged graph.
On this initial migration, stage all interdependent node files together. Installation
preserves any existing hook and respects `core.hooksPath`; chain the command manually
if necessary. Neither the migration nor these tests install a hook, stage files,
or create a commit on your behalf.

## Open the actual graph in VS Code

From the repository root, after installing `.[dev]` into `.venv`:

```sh
npm --prefix vscode ci
```

Open this root folder in VS Code and launch **Run SpecSpec on this repository**
(F5). The launch compiles the extension and opens `specspec-dev.code-workspace` in a
separate development profile under the ignored `.vscode-test/` directory. It selects
the local virtual-environment Python explicitly rather than relying on PATH. Trust
this repository if VS Code asks, then run **SpecSpec: Open Graph** in that window.
Use **Compare revisions** for historical graph overlays.

Stop old debug sessions before relaunching after configuration changes. An empty
window now offers a filesystem folder picker; selecting a subfolder resolves its
containing SpecSpec project. Startup failures are shown in notifications and
**View → Output → SpecSpec**, not silently swallowed.

The editor opens a neighborhood view when a node is clicked. The expanded selected
node contains the existing binding-text/parent/source and lifecycle controls; its
neighbors remain compact, with parents left and children right. The layout is
relation-derived and independent of viewport size. Middle-drag/background drag
pans; wheel/pinch zooms; navigation buttons and keyboard actions frame the view.
The separate camera never stores positions in canonical files. Parent cards show manifesto distance; child cards show
all-depth downstream counts. **Total graph** goes back, **Resume draft** restores
editing, and **Color by** selects status or distance fills. Git badges are separate.
Historical comparisons remain read-only.

`npm --prefix vscode run test:host` checks project loading, the Python backend, and
real webview interactions in the installed VS Code with a disposable profile and
loopback Chromium debugger (Node 22+). Focus/back navigation, color modes, root
controls, viewport-size invariance, cursor-anchored zoom, panning, curve/content
clearance, and resized side-port endpoints have passed on Windows. Screenshots were
captured and visually inspected in the ignored local state directory. Full manual
mutation and revision-picker interaction checks remain outstanding.
