# Working with a specspec Graph

## Purpose

A **specification spectrum**, or **specspec**, organizes a product's current specification by justification: why the product exists, what it should achieve, which approaches serve those intentions, and how actual artifacts realize them.

The product can be software, a Markdown book, a LaTeX slideshow with SVG figures, an exhibition, or another deliverable. Implementation means producing that product, not necessarily writing code.

Keep intentions and consequential choices independently revisable. Trying a solution should not make it indistinguishable from the outcome it serves. The graph supports shared understanding, informed revision and traceability; it is neither a task board nor proof of correctness.

## Structure and rationale

Three node types form one rooted directed acyclic graph:

- **Manifesto:** the unique root, without parents, stating the product's core purpose, audience and defining commitments.
- **Requirement:** a minimal coherent outcome, constraint, refinement or solution choice, with one or more manifesto or requirement parents.
- **Implementation:** an explanation of existing artifacts and their bounded realization, with requirement parents and no children.

Every node is reachable from the manifesto, keeping its justification accountable to the product's purpose. Acyclicity prevents circular reasoning; it does not prohibit iterative development or cyclic product behavior. Implementation explanations are terminal because further requirements should rest on explicit specification decisions, not incidental artifacts. A requirement can remain a leaf without implying completion.

Edges point **parent -> child**, from intention toward conclusion. Multiple parents, including parents at different depths, allow shared reasoning without duplication. Multiple parents combine reasons; they are not alternatives. A child need not fulfill a parent alone: several realizations can jointly contribute. Links imply neither implementation order, containment, approval nor completeness. Use ordinary references for related topics without justification relationships.

Keep the graph **shortcut-free**: if A reaches C through B, omit the additional direct edge from A to C. Ancestor bindings remain inherited; immediate links retain their explanatory meaning.

Canonical `.specspec/` contains one Markdown file per node, named exactly `<id>.md`. Frontmatter records identity, type and parent references; the body carries binding text. Names are stable full IDs, including the final `=`, not title summaries. Find readable headings through query or the visual editor. Prefer graph-aware tools, permit manual Markdown edits and validate the complete graph. The reserved `.specspec/local/` subtree holds runtime state, outside node membership; initialization protects it with a checkout-local Git exclusion.

## Intention and conclusion

Intention and conclusion are relationships, not additional node types. A requirement can be a conclusion relative to its parents and an intention relative to its children. Depth measures neither confidence nor authority.

Ask: **What should survive if this approach changes? What question does the approach answer? Could another approach achieve the same outcome?** Separate that outcome from meaningful choices.

Neither authorship nor specificity settles the distinction. Owners propose solutions; agents help articulate intentions. An exact color, language or medium can itself be essential. "Use LaTeX" might suggest typography tooling or express a publisher's mandatory delivery constraint. Clarify consequential ambiguity rather than inventing motivation.

Intentions can change with the owner's goals. Conclusions remain current commitments until revised; successful implementation does not make them inevitable or authorize rewriting their parents.

Read an edge as: **the child is a reasoned refinement, choice or realization serving the parent within inherited bindings**. Explain that contribution. A conclusion is usually justified, not logically entailed. Constraints limit acceptable realizations: record their scope and known rationale, distinguishing imposed requirements from chosen trade-offs. Consider relevant constraints beyond ancestors too. Expose incompatible bindings instead of silently weakening them.

## Splitting, joining and merging

Split elements when separate identities enable meaningful replacement, review, reuse or implementation mapping. Separate desired outcomes from consequential means, and statements with different justifications or scopes.

Choose relationships by meaning:

- Parent and child when one justifies the other.
- Siblings when both independently serve a common intention.
- Multiple parents when one coherent conclusion jointly serves distinct intentions.

Convergence preserves separate intentions; merging those intentions would erase their distinction. Merge duplicates or fragments sharing one coherent contract and revision boundary, not merely vocabulary or implementation files. Keep a choice with its rationale. Headings, lists, examples and related cases can structure one node. Avoid both monolithic nodes hiding independent decisions and tiny nodes fragmenting one thought.

For a field-guide book, beginner identification and grayscale reproducibility can jointly justify monochrome diagnostic drawings. A LaTeX delivery constraint and that illustration choice can jointly justify an entry macro. Implementation leaves identify actual chapters, drawings, macros and reviewed proofs. Replacing the macro preserves earlier intentions.

## Binding text, realization and maturity

State current goals, contracts, boundaries and realizations positively. Preserve necessary prohibitions precisely. Explain scope, assumptions, trade-offs and deliberately open choices without mandatory templates. Git retains superseded decisions and change history; active nodes retain current rationale and limitations.

Requirements describe the target; implementation leaves describe actual artifacts. Link sources and explain bounded contributions. Reveal gaps rather than weakening requirements to match existing work. Compilation proves neither a book's argument nor audience understanding; qualitative assessment needs appropriate judgment.

An implementation-mature graph makes material decisions explicit while leaving intentional freedom. Metaphorical compiler-level determinism means reducing accidental interpretation, not prescribing identical creative outputs. Review proportionately to uncertainty and impact. Before revising relationships, inspect old and new ancestry and descendants. Structural validation establishes consistency, not semantic fulfillment.

## Working phases

### Owner planning

Before acting, inspect Git status, full specification/code differences and untracked files for owner changes. CLI reads saved files, not unsaved editor buffers. Preserve the owner's input and infer its intention/conclusion meaning before changing it. When history is unavailable or uses an unsupported scheme, use saved current context and explain the limit rather than guessing older bindings.

### Tandem planning

Discuss intentions, proposed solutions, consequential ambiguity and alternatives. The owner focuses on breadth; the agent deepens reasoning and can surface obviously missing breadth. Give a concise overview ready for correction, not an interrogation or an attempt to steer the owner. Guidance questions can include tentative answers.

Discuss potential removals, splits and modifications promptly. Leave graph manipulation to the requested planning phase rather than narrating proposed new nodes during every discussion. Tandem planning may take several rounds or be skipped when the request is clear.

### Agent planning

A request to draw or change the specification authorizes graph planning. Use existing bindings, usable history, saved owner changes and tandem understanding. Distinguish owner intentions, owner-suggested conclusions and agent conclusions through relationships and rationale. Use managed add/update/delete to deepen and reconcile the graph, then inspect its complete result and report choices, gaps and material uncertainty.

Follow the owner's Git authorization. When separate specification commits are requested, preserve owner changes before agent changes, using `Owner specspec changes: <understanding>` and `Agent specspec changes: <description>`. Stage only the intended coherent slice and validate that exact index before committing. Do not silently stage, commit, install hooks or publish artifacts.

### Implementation

Read the relevant nodes and every ancestor before changing artifacts. Add conclusions and implementation explanations when more depth is needed; keep meaningful choices separate from the intentions they serve. Do not unilaterally add breadth or remove scope. A contradiction calls for a simple, broad, contradiction-free subset whose boundaries and consequences are communicated, not manufactured agreement. Propose substantial improvements or scope changes for owner discussion; use a proposal branch only when authorized.

Keep source links and realization explanations current. Passing checks are evidence, not proof. A graph lets an unfamiliar reader trace details to purpose, replace a solution without erasing its outcome, and distinguish desired behavior from delivered evidence.

## CLI: read the context you need

Use the globally installed `specspec` command from the intended project or its subdirectories, like Git. Every command and subgroup has concise `--help`. In a new directory, `specspec init -m "Test"` initializes Git and a manifesto, and creates this guide or appends it after existing AGENTS.md content. Git must be installed. Initialization does not stage, commit or configure identity/hooks.

Copy full case-sensitive IDs, including `=`. Uppercase IDs below are placeholders; examples use Bash quoting.

```sh
specspec query --max-distance 2
specspec query ID --max-distance 0 --with-ancestors
specspec query ID --max-distance 2 --with-ancestors
specspec query ID
specspec query --human
```

Query reads complete bindings and source locations, comparing HEAD -> saved workspace by default. `query ID` selects ID and descendants. Metrics start at ID; the default root is the manifesto. `--with-ancestors` adds every selected node's parent paths, including each branch justifying a shared conclusion. Added ancestors do not consume selection quotas. Read this combined justification before editing; skip redundant readings only when the complete bindings have already been read.

Distances count directed edges from the query root, whose distance is zero:

| Option | Nodes selected |
| --- | --- |
| `--min-distance N` | Shortest path <= N |
| `--max-distance N` | Longest path <= N |
| `--influence N` | Self plus unique descendants >= N |

A node reached along paths of lengths two and four has minimum distance two and maximum distance four. Influence counts a shared descendant once. Percentages select `ceil(population * percentage / 100)` nodes by smallest distance or highest influence, with full-ID tie-breaks. Criteria use one complete reachable population; their results form a union.

Default output puts complete bodies on one line with paragraph separators. `--human` preserves body lines and lists sources individually. Shared nodes have one reading plus pointers. Headers carry parent IDs/change hints; source rows give locations and mapping findings. Nearby child/sibling IDs help choose the next reading.

```sh
specspec query --max-distance 50%
specspec query ID --influence 5 --with-ancestors
specspec query --min-distance 25% --influence 25%
specspec query ID --base REV --target REV --max-distance 0 --with-ancestors
```

`--base BASE --target TARGET` selects other comparisons; TARGET can be a revision or `workspace`. A same-revision comparison reads its historical justification. Surviving nodes carry target bindings; deleted nodes carry base bindings, which remain historical context rather than restored current justification.

## Follow and maintain implementation sources

```sh
specspec sources show IMPL_ID
specspec sources show IMPL_ID --source 1
specspec check IMPL_ID --sources
```

Numbered source entries link explanations to project-relative artifacts. Whole-file references follow artifacts; region references anchor inclusive lines to immutable Git blobs and a tracking mode. Symbols are descriptive, not language-resolved.

- `strict`: a specific selection whose internal changes deserve renewed review.
- `expanding`: a broader region that includes reliably mapped contained edits.

Both follow reliable relocation, preserve separate gaps and exclude insertions at outer boundaries. Ambiguity, missing objects, deleted files and exhausted mapping budgets remain explicit. Source evidence does not establish semantic fulfillment.

```sh
specspec sources capture IMPL_ID src/app.py \
  --range 10:20 --range 30:35 --mode strict --dry-run
specspec sources capture IMPL_ID src/app.py \
  --range 15:25 --mode expanding --staged
specspec check --staged --sources
```

Capture writes a reference on the current implementation; HEAD is the default code source, `--ref REV` selects a commit, and `--staged` selects exact index bytes. Use ranges from that chosen snapshot. Stage code before staged capture and the updated specification before staged validation. Retain anchors through commit trees or code entering the next commit. Capture/reanchor only when authorized to edit the specification.

For `conflict`, review selected artifacts against their explanation. For `missing`, find the surviving realization. For `ambiguous`, inspect and select explicit ranges. For `unavailable`, read its diagnostic first. Align explanation and artifacts before reanchoring.

```sh
specspec sources reanchor IMPL_ID --source 1 --staged --dry-run
specspec sources reanchor IMPL_ID --source 1 --range 20:35 --staged
```

Reanchor preserves mode and description while moving blob/path/ranges. `sources capture --replace N` deliberately replaces an existing occurrence, including its tracking mode. Read the numbered source list again after editing references.

## Edit, repair and verify

```sh
specspec add --parent PARENT_ID -m '# Conclusion' -m 'Reasoning.'
specspec add --type implementation --parent REQUIREMENT_ID -m '# Realization'
specspec update ID --replace 'old passage' 'revised passage'
specspec update ID --parent FIRST_ID --parent SECOND_ID
```

Repeated `-m` joins literal paragraphs with a blank line; `update ID -m TEXT` replaces the whole body. `update --parent` supplies the complete parent set. Implementation leaves have requirement parents.

Each replacement OLD must identify one original-body span across all supported layouts; repeated pairs must be disjoint and do not cascade. Matching tolerates LF/CRLF/CR and ordinary Markdown prose soft wrapping, not changes to words, case, Unicode normalization, indentation or structural boundaries. NEW is literal in content; newline encoding follows the existing document (LF for new nodes). Unmatched logical text stays unchanged. Ambiguity or analysis limits reject the candidate. Without messages or replacements, body input comes from UTF-8 stdin; use shell redirection such as `specspec update ID < binding.md` for large text. Empty stdin with explicit metadata edits preserves the body. A nonempty stdin stream can target only one step; give the other steps messages. Replacements do not consume stdin.

Combine add/update/delete for one candidate and recoverable transaction. `--as goal` names a new node locally and quoted `--parent '$goal'` links it, including forward references. Preview IDs are not reservations.

```sh
specspec add --as goal --parent ROOT_ID -m '# Goal' \
  add --parent '$goal' -m '# Detail' \
  update CHILD_ID --parent '$goal' --dry-run --require-valid
```

Apply by removing `--dry-run`. `--require-valid` checks the complete final graph before writes. Other commands remain standalone.

Deletion removes **exactly selected files**, retaining descendants and their parent declarations. Preview scope first; loss of justification does not authorize deleting a conclusion. The manifesto cannot be deleted or reparented. Resolve surviving missing-parent declarations deliberately. A successful intermediate edit can leave an invalid graph; `check` remains strict.

```sh
specspec delete ID --dry-run
specspec query --issues --with-ancestors
specspec query ID --raw
specspec diff --with-context --node ID
specspec check --sources --warnings-as-errors
```

Node reads/diffs compare logical LF text independently of Git settings. Existing-document writes/native plans retain local newline style; new nodes use LF. Spaces and blank lines stay meaningful. Complete tool-written/planned node documents receive a final newline only when missing, using local style and preserving existing trailing blank lines. Reads and raw-editor saves do not impose formatting; raw query, byte guards and recovery retain exact physical evidence. Leave repository Git settings and attributes under owner control.

Inspect full logical canonical hunks with `diff` and artifact patches with Git; query hints are orientation, not a patch review. Deleted HEAD nodes remain D through staging and vanish from the default comparison after commit. Earlier text remains available through explicit historical comparisons. There are no stored approval statuses, confidence scores or parent-review gates.

Before an authorized commit, stage the complete intended graph/artifact slice and run:

```sh
specspec check --staged --sources --warnings-as-errors
```

This checks the exact index, including partial staging; working-tree validation cannot substitute for it. Account for all remaining changes, including earlier agent work. Install or modify Git hooks only with explicit owner authorization.

If a managed edit is interrupted, retain `.specspec/local/` and run `specspec recover`. Recovery restores known transaction originals, not arbitrary previous successful edits; external changes remain protected. Use `recover --force-lock` only after confirming no writer is running. Native VS Code document saves retain VS Code's own persistence/undo ownership and are not Python-journaled transactions.
