---
id: 7tMgRa8=
type: requirement
parents:
- 0dvOn3A=
---
# Expose eight everyday commands and focused advanced tools

The everyday vocabulary is init, show, context, add, update, delete, check and diff.
Show without an ID lists concise node summaries; show ID reads its complete record;
show ID --dependents reports structural descendants. Context supplies complete selected
and ancestor binding text, with surrounding IDs identified separately. Check covers
working files, --staged exact-index files and optional --sources mapping/retention;
--warnings-as-errors remains available. Diff accepts optional positional BASE/TARGET,
defaulting to freshly resolved HEAD versus working files. Root selection stays --root.

Init takes a manifesto body file or stdin; add/update use --body FILE|- and explicit
repeated --parent full IDs. Add defaults to requirement, supports --type implementation,
and derives an optional summary from its heading with an advanced --slug override.
Updates replace the supplied parent list; valid manifesto parents stay empty.
Delete retains --dry-run and --yes with its complete descendant and warning contract.

Advanced sources show/capture/reanchor and recover retain source and recovery controls.
Sources show consolidates resolution and optional literal preview; capture/reanchor
use --dry-run for non-writing previews. Source number, mode, ranges, explicit revision
and staged selection remain meaningful. Raw source JSON, mixed graph/code revision
selection, reviewed deletion plans and cache hints belong to advanced/integration
usage. A hidden api command accepts bounded structured application read/plan/source
requests. Basic help separates the everyday vocabulary from advanced tooling.

One spelling serves each operation. The current CLI exposes text and --json output;
Git hook/CI setup calls check --staged through owner-controlled Git tooling. Mermaid
export and automatic hook installation are outside the public command surface.
