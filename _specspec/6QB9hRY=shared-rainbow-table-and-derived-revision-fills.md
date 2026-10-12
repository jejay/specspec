---
id: 6QB9hRY=
type: requirement
parents:
- Rg30CXs=
- qnGsij4=
- bLBNk80=
---
# Share a thirteen-step violet-to-red table and comparison-derived fills

Use thirteen sRGB hex swatches sampled from OKLCH L=0.73, C=0.11, H=300 down to
30 in 22.5-degree steps, rounded to bytes. They are in sRGB gamut, with broadly
similar lightness/chroma to the existing gentle colors. Violet, indigo, blue,
azure, sky, cyan, teal, green, lime, yellow, amber, orange and red are ordered
rainbow entries, not confidence levels. These colors/constants are revisable.

For min/max distance, one hop uses violet and (distance-1) modulo thirteen cycles
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
