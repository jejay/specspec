---
id: 83D9YWw=
type: requirement
parents:
- TAvql3w=
- YaXJpGE=
- 3fWBW_g=
---
# Distribute portable history and clone examples into independent workspaces

Keep the Gantt snapshot, complete Git bundle and stage/receipt ledger versioned as
reviewable fixture artifacts in SpecSpec. The tracked example/gantt directory is
not the example's Git workspace: ordinary Git there resolves to the enclosing
development repository. Do not install nested Git metadata, use a submodule tied
to a remote service, or move the only test corpus to an untracked local directory.

Provide a repository-development checkout helper, not a new production SpecSpec
command or schema converter. Clone the bundle by default into
~/Projects/specspec-examples/gantt (Windows: ~\Projects\specspec-examples\gantt).
Allow explicit external destinations for CI and disposable tests; resolve paths,
refuse destinations inside this development Git worktree and refuse every existing
destination rather than resetting or overwriting local work. Persist LF checkout
configuration so index/worktree comparisons remain meaningful across platforms.
Open the cloned project itself in either host for manual Git/temporal experiments.

All substantial Git, host and application integration fixtures clone this complete
history, retaining its actual stage tags, ancestry and independent index. Add
A/M/D display changes only to a disposable clone's worktree; do not replace history
with a copied graph plus a new single-commit baseline. Keep focused current-schema
synthetic graphs for narrow native-document or nested-project unit tests. The
self-specification receives working graph/source validation, not compatibility
checks against obsolete development commits. CI needs only the tracked bundle,
not a full fetch of SpecSpec development history or a preexisting home-directory
clone. Verify the bundle's runtime/tests against the tracked snapshot to catch drift.

On each schema change, reconstruct every example revision in a fresh independent
repository through current tools, consistently mapping identities/references and
regenerating real CLI receipts. Preserve credible graph emergence and redirects,
not fictional dialogue requirements. Refresh all stage tags, commit ledgers,
current snapshots and the complete bundle together, and validate all retained
refs. Save local experiments before explicitly recreating stale manual clones;
never silently reset them or force-push unrelated SpecSpec development history.

Origin: a revisable bundle/distribution/checkout choice implementing TAvql3w=.
The full-history rewrite obligation is the user's intention; storage location,
helper shape and fixture packaging are independently revisable mechanisms.
