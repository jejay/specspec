# Local comparison spotlights

A spotlight exchanges one message, selected node IDs and a revision comparison
between an owner and an external coding agent. It is a local helper, not a node
archive. Git supplies committed contents; the workspace remains live.

## CLI

```sh
# Default: live workspace versus fresh HEAD
specspec spotlight add DG-JpDc= rvz48KY= "These nodes explain spotlights"

# Review a committed change, including deleted or unchanged nodes
specspec spotlight add DG-JpDc= rvz48KY= "Why did one change but not the other?" \
  --base main~2 --target main

# Compare saved workspace files with another branch
specspec spotlight add DG-JpDc= "Please review this against the release branch" \
  --base release --target workspace

specspec spotlight show
specspec spotlight show <full-spotlight-id> --json
specspec spotlight flush --yes
```

Use your project's full canonical IDs, including the final `=`. `add` reads the
leading IDs and joins the remaining message words. Quote the message, especially
when it starts with an ID. Dash-leading canonical IDs work. There are **no color
arguments**: color names after the IDs are ordinary message text. Duplicate IDs,
missing members and blank/over-500-character messages reject the entire addition.
The selected IDs may come from **either side**, including deleted base nodes and
unchanged nodes; they need not all share one change status.

`--base REV` and `--target REV|workspace` select the comparison. Explicit Git refs,
including branch names and `HEAD`, resolve to full immutable commit IDs at capture.
The implicit default stores `HEAD → workspace`, following fresh HEAD on display.
Thus explicitly adding `--base HEAD` pins that base, while omitting it in the
default workspace comparison leaves it live. An explicit committed target also
pins the default HEAD base. No checkout, branch switch, staging or Git-object write
is involved. `workspace` is the reserved live target spelling.

`show` resolves **each spotlight's own comparison**, not arbitrary extra revisions:

```text
1 local spotlight(s) · retained until explicit flush

Spotlight <32-hex-id> · <capture-time>
  <base-commit> → <target-commit>
  Explain the changes and this unchanged intention
  D abcdefg=  Removed conclusion
  A hijklmo=  Added conclusion
  M pqrstuw=  Changed requirement
  = xyzABCA=  Unchanged intention
```

The markers are **A** added, **D** deleted, **M** changed,
**=** unchanged, **?** absent and **!** unavailable context. Status follows the
shared semantic graph comparison; literal-byte-only drift can warn without an M.
Titles and paths are derived on display, not retained copies. JSON keeps the
stored record and adds `members` (`id`, `kind`, `title`, `path`) and `warnings`.
Advisory drift or unavailable comparisons do not turn `show` into a failing command;
malformed local records do. `add --json` returns the same resolved presentation.

CLI capture reads **saved files**, not unsaved native documents or managed forms.
UI capture includes trusted native open-document overlays without saving them.

## UI

- **Shift-click node chrome** toggles its highlight. Ctrl+Shift-click, or macOS
  Command+Shift-click, removes it directly. Native inputs, links and form controls
  keep their normal modified clicks. Anonymous new-node drafts have no selectable ID.
- All highlights use **one white ink**. To try another color, edit
  `--spotlight-color` in `graph-ui-common/media/graph.css` and rebuild the host.
  Semantic fills and Git/status colors stay independent.
- Manual and spotlight-applied highlights are one editable per-view ID set.
  **Clear highlight** clears it. Modified or missing versions do not erase IDs.
- **Spotlights → Create spotlight from highlights…** asks for a message and saves
  the IDs with the **current comparison**. Cancel writes nothing; failure keeps
  the input for retry. Saving never saves a native document or managed form draft
  and does not move the camera. The agent reads it with `spotlight show --json`.
- The newest-first dropdown has one text entry per spotlight, with time,
  comparison and member count. Selecting an entry closes it, switches to that
  comparison, then highlights and frames the available union in the full canvas.
  Surviving target nodes and deleted base nodes both receive rings. Focused drafts
  remain available through **Resume draft**. Selecting again frames again.
- Highlighting is **best-effort by identity**, not an exact-version gate. Missing
  IDs stay selected; a selection with no available nodes leaves the camera alone.
  Changed workspace versions still receive rings. If Git context cannot load, the
  UI explicitly warns and uses the last usable displayed graph (or workspace/HEAD
  on restoration), never claiming it loaded the missing comparison.
- Workspace drift warnings stay **visible outside the closed dropdown**. Choosing
  another comparison or HEAD/workspace releases the active spotlight context but
  keeps the editable IDs. Active spotlight identity and IDs restore per view.
- Rings use `max(5, 3 / k)` world units at camera scale `k`, with negative equal
  inset: 5 units at actual size and at least 3 CSS screen pixels when zoomed out.
  Node geometry, type shape, focus cues and native editors remain independent.

The round red badge counts **new records since opening the list**, not total
members. First load and renderer reload establish zero baselines; repeated reads
add nothing. Opening clears the count. Arrivals preserve focus/caret, drafts,
camera, editable highlights, dropdown choice and older entries. Counts/New cues
live in renderer memory. Escape/outside dismissal leaves highlights alone;
keyboard navigation and scrolling keep all entries reachable.

Both hosts independently watch spotlight metadata, including historical views.
Refresh and optional polling remain fallbacks. Local-store errors preserve the
last loaded list independently of specification validity.

## Data structures and drift

One immutable local-format-2 JSON file holds:

```json
{
  "spotlight_version": 2,
  "id": "0123456789abcdef0123456789abcdef",
  "created_at": "2026-01-01T12:00:00+00:00",
  "message": "Why did this intention stay unchanged?",
  "comparison": {"base": "HEAD", "target": "workspace"},
  "nodes": ["abcdefg="],
  "workspace": {
    "head": "<full capture HEAD commit, or null>",
    "changes": {"hijklmo=": "<literal-byte SHA-256>", "pqrstuw=": null}
  }
}
```

Committed comparisons omit `workspace` entirely and contain only commit/ID
references. Workspace comparisons keep a **sparse summary of all uncommitted node
changes**, including unselected nodes so context drift is noticeable:

- Clean committed nodes have **no saved checksum**. Their commit supplies contents.
- Added or modified workspace nodes have a SHA-256 of literal UTF-8 file bytes,
  including comments and line endings. Git determines whether saved tracked files
  are dirty, so a clean CRLF/clean-filter checkout does not hash every node.
  Native overlays participate when they differ from saved contents.
- Deleted nodes use `null`, a deletion marker, not a checksum.
- IDs determine canonical paths; binding and heading edits keep those paths stable.

On display, compare the capture HEAD and sparse changes with current workspace
state. HEAD movement, changed sparse entries and unavailable state produce
warnings. This is advisory context detection, not a reconstruction of unsaved
history, an edit lock or a correctness guarantee. New commits can warn even when
node text remains the same. Staging alone does not change the workspace snapshot.
No node bytes, committed-node hashes, per-color groups, blob archive or captured-
text preview are stored. Local drift checks leave canonical schema/edit protection
unchanged. Node format is 7; API remains 6; the separate local spotlight format is 2.

## Storage and lifetime

```text
<project>/.specspec-local/annotations/<spotlight-id>.json
```

The CLI and both hosts share this ignored store for the **same checkout**. Separate
clones/worktrees have separate stores. Records persist across sessions and branch
changes until explicit flush. The tool uses Git's local `info/exclude` if needed,
refuses tracked local state, and never stages, commits, installs hooks, writes Git
objects or pins refs. Deleted or garbage-collected Git revisions can therefore
become unavailable: that is a diagnostic, not a reason to archive nodes locally.

Publication validates before an atomic metadata-file replacement under the existing
workspace writer lock. Recovery and confirmed stale-lock handling retain their
ordinary rules. Limits are 512 selected IDs and 512 KiB metadata per spotlight,
256 records and 4 MiB total metadata per checkout. Exceeding limits rejects new
records rather than evicting old ones. These are local process-interruption guards,
not adversarial or full power-loss durability guarantees.

**The old colored/blob-copy local format is unsupported.** Existing local records
are left untouched with an actionable diagnostic. Clear them deliberately using
`specspec spotlight flush --yes`; this also deletes obsolete `blobs/` files.
Malformed metadata is likewise preserved until repair or explicit flush. Unsafe
entries/symlinks require filesystem repair. Flush touches only spotlight files,
not specification files, Git, drafts, recovery journals or other local notes.
UI flush confirms and rechecks the reviewed ID set, rejecting intervening arrivals.
Editable highlight IDs remain until Clear highlight. External deletion or
`git clean -fdx` can independently remove ignored state.

## Verification

Backend tests cover dirty-only literal checksums, clean CRLF/native boundaries,
workspace/branch/committed comparisons, A/M/D/= statuses, absent/unavailable nodes,
HEAD/context drift, atomic validation, immutable records, exclusion, limits and
reviewed flush. Temporal tests use an independent maintained current-schema Gantt
clone. Shared renderer/session tests cover comparison-before-framing, identity
rings, advisory warnings, restoration/fallback, arrival baselines, toggles, compose/
retry/cancel, retained drafts/caret/cameras and guarded historical native writes.
Host adapters and installed probes exercise the shared backchannel. See
[installed-host evidence](investigations/host-smoke.md) for the qualified runs.
Physical macOS modifiers and arbitrary filesystem/theme behavior remain unverified.
