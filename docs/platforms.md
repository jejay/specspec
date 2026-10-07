# Shared graph UI and desktop adapter — implementation plan

## Intentions

The user wants the same SpecSpec graph experience in VS Code and a standalone
Linux/Windows window, later usable in Claude Code or Codex workflows; a left-side
Activity Bar entry; a dachshund brand/minimal icon; and clearer themed Git titles
and A/M/D corner cues. Keep native editing, managed writes, revision context,
drafts/fingerprints, and viewport-independent geometry. These are outcomes, not
an instruction to adopt React, expose a web server, or embed agent credentials.

## Revisable conclusions

- `graph-ui-common/`: one local DOM/SVG renderer, template/CSS, Dagre/D3 build,
  camera/metrics/layout, bounded CLI bridge, and guarded serialized graph session.
  Small adapters provide messaging/state, project selection/authorization,
  confirmations, revision input, watchers, themes and asset URLs. No renderer forks.
- VS Code: a retained WebviewView in an Activity Bar container, initial `order: 4`
  near Run/Debug. User ordering remains VS Code's choice. Inline node forms remain;
  this host sidebar is not a second settings sidebar. Project-scoped state protects
  nested-project drafts. Open Graph focuses the container, with explicit project
  selection and historical comparison commands.
- Electron: isolated/sandboxed renderer, fixed narrow preload API, sender-checked
  main-process IPC, explicit local project authorization, shell-free Python API 2,
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
