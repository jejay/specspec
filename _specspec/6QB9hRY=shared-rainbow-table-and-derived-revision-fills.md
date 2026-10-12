---
id: 6QB9hRY=
type: requirement
parents:
- Rg30CXs=
- bLBNk80=
- l3vgxN4=
- qnGsij4=
- gfAxHps=
---
# Share the user's exact seven-step table and comparison-derived fills

Use the seven exact swatches from gfAxHps=: #bc82c9, #7e97e6, #1facce,
#37b390, #92a64b, #ca8d3e and #dc7b7c. The user's pasted CSS is authoritative.
Map one-based CSS references to zero-based model indices: requirement 3,
implementation 0, added 4, changed/renamed 1, removed 6 and source-changed 5.
The existing pure shared model remains the single node-palette source; translating
the CSS into that table/mapping avoids unused variables or a second color authority.

For min/max distance, one hop uses violet and (distance-1) modulo seven cycles
the table; gray manifesto zero stays outside the spectrum. Unknown/invalid paths
use neutral gray. Type mode uses table teal for requirements and violet for
implementations, with light-gray manifesto. Derived metrics stay revision-local.

Add persisted mode git-revision, labeled "Git/Revision Status". Fill from the
existing node comparison kind: A/added table green, M/changed and R/renamed table
blue, D/removed table red, source-only affected table amber, unchanged neutral gray.
Show R/source labels separately; withdrawal is not deletion, and source-only impact
is not node modification. Direct diff kinds take precedence over source impact.
Absent comparison is explicitly labeled no comparison, with neutral fills rather
than claiming unchanged. Unsaved new/orphaned drafts use neutral/draft presentation,
not fictitious Git additions/deletions. Keep title/corner theme tokens and edge
colors/dashes independent of fill; they are not recolored by selecting this mode.

Apply status fills equally to compact/expanded cards and the manifesto, including
history/read-only/removed nodes. Only distance/type modes retain the neutral-root
white-hover override. A status-colored root retains stronger status-hue hover like
other cards; status-mode neutral fills use ordinary semantic hover too. The previous
all-mode fixed-gray/root-white statements are superseded only for the new mode.

Keep exact informative legends for all meanings, explain cycle/repetition and the
selected comparison rather than storing status in canonical nodes. Persist the
mode in host state; continue rejecting obsolete approval-status preferences.
Mode switches retain native form DOM/caret/drafts/baselines, geometry and camera.
Verify palette hue order/lightness/chroma and wrap, type/status table membership,
all comparison kinds including root changes, no comparison, drafts, restoration,
revision switching and actual host fill/hover/legend paint. No schema change or
example-history rewrite, approval status, host/domain-rule fork or new Git writer.

## Earlier nine-color tuning (superseded)

l3vgxN4= requests fewer, slightly stronger colors. Keep L=.73, increase C=.11
to .12 and spread nine hues evenly over the same violet-to-red range. Remap type
teal/violet to indices 4/0; revision green/blue/red/amber to 5/1/8/7, with R sharing
blue. The prior thirteen-color selection and actual checks remain in Flf59Uc= as
history, not the current palette. Cycle after nine hops, not thirteen. This tuning
changes only shared palette samples/indices, not fill modes or interaction rules.

## User-selected playground result

gfAxHps= replaces the previous count, samples and indices with the explicit
seven-color result. Current playground reset defaults use count 7, L=.69, C=.12,
hue 320 to 20: actually running the generator reproduces all seven exact hex
values and mappings. This reproducibility is evidence, not authority to change
any supplied byte. Preserve the earlier nine-color choice/evidence as history.
No production CSS configuration/import system, label persistence, schema change
or example-history rewrite is introduced for this palette application.
