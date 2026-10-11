# Shared graph UI and desktop adapter — implementation plan

## Intentions

The user wants the same SpecSpec graph experience in VS Code and a standalone
Linux/Windows window, later usable in Claude Code or Codex workflows; a left-side
Activity Bar entry; a dachshund brand/minimal icon; and clearer themed Git titles
and A/M/D corner cues. Keep native editing, managed writes, revision context,
drafts/original node contents, and viewport-independent geometry. These are outcomes, not
an instruction to adopt React, expose a web server, or embed agent credentials.

## Revisable conclusions

- `graph-ui-common/`: one local DOM/SVG renderer, template/CSS, Dagre/D3 build,
  camera/metrics/layout, bounded CLI bridge, and guarded serialized graph session.
  Small adapters provide messaging/state, project selection/authorization,
  confirmations, revision input, watchers, themes and asset URLs. No renderer forks.
- VS Code: a retained WebviewView in an Activity Bar container. The initial
  `order: 4` proposal was corrected after inspecting the supported contribution API
  and a real launch: custom containers are assigned after built-ins, and a manifest
  order field is ignored. Users can drag the icon below Run/Debug; don't use private
  APIs or rewrite their layout to force it. Inline node forms remain;
  this host sidebar is not a second settings sidebar. Project-scoped state protects
  nested-project drafts. Open Graph focuses the container, with explicit project
  selection and historical comparison commands.
- Electron: isolated/sandboxed renderer, fixed narrow preload API, sender-checked
  main-process IPC, explicit local project authorization, shell-free Python API 3,
  bounded process/render checks, no remote navigation/popups/renderer filesystem.
  No bundled Python, installer/signing/updater, secret integration or production
  security certification in the initial slice.
- Branding: exact original SVG copy, a separate monochrome 24x24 puppy-face icon;
  command-line `resvg` miniature and enlarged light/dark renders are inspected.
- Git: title + bottom-right A/M/D (and R for pure rename), relative to chosen base.
  Added/deleted use `gitDecoration` theme foregrounds; M uses the theme's blue
  `editorGutter.modifiedBackground`, because VS Code modified-file foreground is
  often amber. Standalone uses VS Code dark defaults. Source-only changes do not
  invent a node M; retirement is not deletion. Semantic fills remain independent.

## Implemented first slice

The shared extraction, Activity Bar view, minimal/full branding, themed A/M/D/R
cues and initial Electron adapter are implemented. The real Windows hosts passed
on disposable CLI-managed/Git fixtures; screenshots and miniature resvg renders
were inspected. Tests cover 72 shared cases, 27 editor-adapter cases, six desktop
security/state cases, and 72 Python cases. A Windows portable package and VSIX
are inspected separately for shared bytes/offline assets/licenses. Electron's
first runtime install may download the pinned framework; the application renderer
has no remote dependencies or requests.

Earlier desktop checks included an actual UI save and the now-withdrawn backend
stale-fingerprint rejection; the hash-free revision replaces that gate with watcher
synchronization and same-node overwrite confirmation. Current checks cover
retained/reloaded native drafts and actual historical/workspace switching. The
historical test polls completion rather than assuming a Git diff completes in five
seconds. Root selection/authorization/native confirmations are covered by adapter
and shared-session tests, not a claim of exhaustive manual dialog workflows. The
same Chromium harness now selects the renderer's main-world port (not Electron's
isolated preload world) and tests only actually visible hover targets in the clipped
sidebar, while checking geometry/metrics for every displayed node/edge.

## Hash-free Markdown synchronization revision

The user's later correction permits manual changes, removes fingerprint/managed_hash
gates, and asks for file-watcher synchronization with configurable default-off
polling. Both hosts use API 3. VS Code watches canonical-directory/file changes;
Electron watches the parent and canonical directory and reattaches on replacement.
`specspec.pollIntervalMs` / `--poll-interval-ms` (or `SPECSPEC_POLL_INTERVAL_MS`) use
milliseconds with zero as default. The shared session coalesces events, retries
incomplete reads, compares records directly, and retains invalid views/drafts.
Watchers are OS/filesystem-dependent hints; no universal delivery/race guarantee
or silent fallback polling is claimed. See README for the conflict/recovery policy.

## Milestones and verification boundaries

1. Commit this intention/conclusion plan before the extraction.
2. Extract common renderer/session while preserving existing tests and draft safety;
   commit that semantically independent shared foundation.
3. Add Activity Bar/branding/Git cues and initial Electron adapter; verify bounded
   host messaging, stale/legacy/history/trust safety, theme/default colors, scoped
   drafts and complete rendering; capture/inspect installed-host screenshots.
4. Refresh managed implementation/source evidence and docs; validate both root and
   Gantt working/index graphs and commit completed changes. Unrelated local settings,
   original artwork/PNG, intention and license are not overwritten or staged.

Linux/Windows are target platforms. Local execution is Windows; Linux smoke tests
should run under CI/Xvfb, not be claimed locally verified without a Linux run.
Claude Code/Codex adapters are deliberately later work, not implemented by naming a
shared package. Existing large-graph/full-manual/platform limits remain explicit.
