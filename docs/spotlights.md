# Local spotlights

Ask an external coding agent a question such as “Which nodes describe remote
execution?” The agent reads `show` / `context`, chooses the relevant nodes, and
submits one complete answer through the CLI. SpecSpec displays the answer in either
UI; it does not embed an agent or evaluate a live semantic query.

## Add directly

```sh
specspec spotlight add purple DG-JpDc= blue rvz48KY= "Agent answers and their presentation"
# Without a color, initial IDs use purple:
specspec spotlight add DG-JpDc= rvz48KY= "These nodes describe spotlights"
# Capture a committed graph instead of saved workspace files:
specspec spotlight add purple DG-JpDc= "Committed design" --ref HEAD --json
# Read retained spotlights and check workspace + current HEAD:
specspec spotlight show
# Also check exact membership in selected historical trees:
specspec spotlight show --ref main~2 --ref a-tag --json
```

Syntax: `specspec spotlight add [[color-name] [node-id]+]+ MESSAGE`.
The IDs above belong to SpecSpec's own graph; use your project's full IDs,
including the final `=`. No input file or JSON payload is needed.

Colors are `red`, `blue`, `green`, `purple`, `turquoise` and `yellow`. Each color
applies to following node IDs until another color appears. Initial IDs without a
color use purple. Each explicit color needs at least one ID. Each node appears
only once in a new spotlight. These named inks are separate from semantic fills.

The parser recognizes the leading color names and canonical IDs, including IDs
starting with `-`. The first other argument begins the message; remaining words
are joined with spaces. Normally quote the message, especially if it contains
color names or IDs. A message must contain 1–500 characters. A standalone color
name or canonical ID in the prefix is structural rather than message text.

Each addition creates one immutable **spotlight** with one message and all its
colored sets. The backend captures node IDs, exact Git blob addresses, paths/titles
and node bytes together. One invalid member rejects the whole addition. There is
no update or individual-membership editor. Commit captures retain the immutable
commit ID, not a moving `HEAD`. Internal ordered groups repeat the shared message;
existing retained submissions keep their original bytes.

**Default capture reads saved files, not VS Code's unsaved documents or managed
form drafts.** Coordinate saving with the document owner, or choose a committed
revision. UI matching does account for native open-document overlays; unsaved
versions can therefore correctly differ from a spotlight captured by the CLI.

## Attention and the whole list

- **Spotlights** has a round red badge containing only the number of new spotlight
  batches since this view last opened its list. A batch counts once, regardless of
  how many labels or nodes it contains. Zero hides the badge. The retained total
  belongs inside the list, not in the badge.
- The first successful list load establishes the existing baseline with zero new
  entries. Duplicate refreshes add nothing. Opening the list resets the count;
  arrivals while it stays open count until the next opening. Counts and New cues
  live only in renderer memory, so reloads start with a fresh baseline. Stored
  spotlight contents, dropdown choice and active-spotlight selection have their own
  lifetimes.
- The count badge is the visible arrival notice. A polite live region announces
  arrivals accessibly. Arrivals preserve the panel's open/closed choice, active
  spotlight, editing focus/caret, camera and drafts. An open dropdown keeps older entries
  and its reading position as new spotlights arrive.
- A compact context-menu-style dropdown is anchored below **Spotlights**. It shows
  every spotlight newest first as one message entry, with time and compact version
  counts. Entries have no color icon, search field or expanded member/detail view.
- Choose a spotlight to turn on **all its colored sets together**. Rings paint
  first; the dropdown closes, then the matching nodes are framed in the **full
  canvas**, like the existing frame action. This enters the overview, retaining
  any focused draft and surrounding graph context. Choosing it again frames again.
- Solid **8px inset rings** mark exact versions, including removed comparison-base
  cards. Each member uses its set's color. Width is in world units and follows the
  camera scale. Compact counts report different versions, absent nodes and
  unavailable metadata. Version state refers to the displayed snapshot, not an
  unsaved managed form layered over it. A spotlight with no exact matches still
  activates and closes the menu, leaving the camera unchanged.
- **Clear highlight** removes rings explicitly. Escape, outside click or tabbing
  outside dismisses the dropdown without clearing rings or moving the camera.
  Arrow keys, Home and End navigate the menu; Enter/Space activates a button.
  Long lists scroll and the dropdown stays within the window.
- There is no captured-text preview UI. Exact retained bytes remain part of the
  local storage/version-resolution machinery. Existing shots with different texts
  in their internal groups show those texts together in one entry; overlapping
  retained groups use the later group's color.

Ordinary, unhovered neutral curves and arrowheads use darker shared ink: 70% theme
neutral ink mixed with black at 100% zoom and above, decreasing continuously to
35% at 12% zoom. Diff/draft colors and incident-hover emphasis keep their separate
paint. Minimum stroke/head dimensions, world layout and native forms stay intact.
This makes the zoomed-out relationship mesh quieter beside spotlight batches.

Both hosts watch spotlight files independently of graph reloads, including in
historical comparisons. Explicit **Refresh** and configured polling remain
fallbacks for filesystems with unreliable watcher delivery. Local spotlight errors
preserve the last loaded list and do not invalidate the specification graph.

## Storage and lifetime

```text
<project>/
  _specspec/                       # Binding nodes only
  .specspec-local/annotations/
    <shot-id>.json                 # One complete immutable spotlight
    blobs/<full-blob-id>           # Exact retained UTF-8 node bytes
```

Public naming is independent of the internal storage directory and JSON keys.
Existing immutable submissions use the same store and keep their original bytes.
This store is shared by the CLI, VS Code and Electron **for the same project
checkout**, across sessions and branch changes. Separate clones and worktrees have
separate stores. It is not UI-private application data or specification metadata.
The node schema remains format 5; spotlight files have their own local format.
The CLI uses Git's local `info/exclude` when existing ignore rules do not protect
`.specspec-local`, without modifying tracked `.gitignore`. Writes refuse Git-tracked
local-state files. It never stages, commits, creates refs, writes Git objects or
installs hooks.

A blob address hashes the exact captured node file, including frontmatter/comments
and line endings. Workspace addresses use literal saved bytes without Git clean
filters or line-ending normalization. Computing an address does not imply that an
object exists in Git. A filename-only rename preserves a node/blob match; changed
bytes do not. SHA-1 and SHA-256 Git object formats are supported.

A blob has no intrinsic containing-commit list. Membership is derived by inspecting
the workspace, current HEAD or requested revision trees. The UI checks its actual
native-overlay target and comparison base; it does not scan all Git history on
every arrival. Capture provenance helps locate the original context. The local
copies preserve original evidence through branch changes, rewritten history and
Git object garbage collection without pinning Git refs.

Spotlights do not expire or disappear when members change or are deleted. To
explicitly clear all local spotlights and retained contents:

```sh
specspec spotlight flush --yes
```

The UI's **Flush local spotlights…** asks for confirmation and rechecks the reviewed
shot-ID set under the writer lock. An intervening arrival requires another review
rather than being silently flushed. Flush touches only spotlight files/content,
not node files, transaction journals, unapplied forms or other local notes.
`--yes` is the CLI's explicit consent to flushing the current whole list.

Publication uses the cooperating workspace writer lock, retained blobs first and
one atomic shot-file replacement last. Interrupted unpublished copies can remain
until flush. Normal `recover` / confirmed `recover --force-lock` retains the existing
writer-recovery rules. These are process-interruption safeguards, not full
power-loss durability or adversarial filesystem protection. Deleting the local
directory, recreating the checkout or `git clean -fdx` can of course remove ignored
local data independently of SpecSpec.

Limits reject further submissions rather than evicting retained answers: 64 groups,
512 total members and 512 KiB metadata per spotlight; 256 spotlights, 4 MiB total
metadata and 64 MiB retained node bytes per checkout. Malformed data is protected
and diagnosed; explicit CLI flush can clear malformed shot JSON. Symlink/unsafe-entry
diagnostics require explicit filesystem repair.

## Verification boundaries

Backend tests cover joint publication/validation, literal content addresses,
workspace-only retention, native-overlay identity metadata, SHA-256, exclusion,
flush races, corruption and storage limits. Temporal coverage uses an independent
clone of the maintained current-schema Gantt history. Shared DOM/session/watcher
and host-adapter tests cover arrivals, initial baselines, batch counts/reset/reload,
the whole dropdown, whole-shot multicolor exact-only rings, full-canvas framing,
keyboard/outside dismissal, drafts/caret/cameras, revision views and guarded
actions. Real-host probes add spotlights through the CLI and wait for watchers,
then sample actual badge/ring paint and zoom-dependent neutral-arrow darkening.
The Python, shared renderer and both host-adapter unit suites pass. Installed-window
runs reach the spotlight arrival/ring/framing assertions, but complete broader smoke
runs time out later in shared descendant-deletion checks. Full host integration,
including the final persisted-list reload assertions, remains unconfirmed.
Their platform and filesystem scope is bounded; they do not establish universal
watcher delivery, perceptual suitability for every theme or large-list performance.
