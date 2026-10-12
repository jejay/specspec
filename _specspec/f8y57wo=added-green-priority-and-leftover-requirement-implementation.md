---
id: f8y57wo=
type: implementation
parents:
- 6QB9hRY=
- IAy2dGI=
sources:
- path: graph-ui-common/media/graph-model.js
  symbol: Requirement rainbow[4], Added rainbow[3]
- path: tools/rainbow-playground/palette.js
  symbol: 'generate: Added 149.5-degree target and leftover Requirement selection'
- path: tools/rainbow-playground/index.html
  symbol: mapping-logic explanation
- path: tools/rainbow-playground/README.md
  symbol: selection priority and fixed text reference
- path: graph-ui-common/test/rainbow.test.cjs
  symbol: exact production role colors
- path: graph-ui-common/test/playground.test.cjs
  symbol: default CSS/JSON, selection priority, narrow fallback and visible labels
- path: graph-ui-common/test-host/playground.cjs
  symbol: real default/reset exports and labels
- path: docs/own-spec.md
  symbol: Added/Requirement swap and current evidence
---
# Swap Added/Requirement and prioritize the text-green cue in selection

Implement B87C_kI= through 6QB9hRY= and IAy2dGI=. Change only the two shared-model
indices: TYPE_COLORS.requirement is rainbow[4] (#92a64b) and REVISION_COLORS.added
is rainbow[3] (#37b390). Seven exact hex values, distance order/cycle, parameters,
other role indices, neutral/manifesto exceptions, themed title/corner/edge ink,
hover, labels, forms, geometry and persistence remain unchanged.

The offline generator targets Added at OKLCH hue 149.5 degrees, the approximate
hue of the existing fallback Git added text #81b88b (independent sRGB conversion:
149.4964 degrees). This is a fixed reference, not live host-theme introspection or
perceptual/display certification. Preserve the other role targets and intentional
changed/renamed reuse. Assign Requirement after those roles: pick the available
index closest to hue 165; if all indices are used, pick the nearest from the full
table. Equal-distance ties keep the earlier entry. Do not generate or retune a
new base palette to obtain the swap. At current defaults this gives exactly
Requirement color 5, Added color 4 and all other original mappings.

Explain the priority, leftover rule, reuse fallback and default-not-theme reference
in the visible playground and guide. CSS/full-JSON exports, reset and suggestions
now carry the new indices. Parameter-only exports remain unchanged. Update literal
production colors/mappings and full CSS/default JSON expectations, while preserving
the original user's pasted outputs and earlier actual check counts as history.

Add a selection regression over counts 2..32 with forward/reversed/narrow/near-wrap
hue intervals, asserting nearest Added target, Requirement availability/nearest
leftover (or no-free-entry fallback), valid indices and renamed/changed equality.
The explicit two-entry 120..170 case verifies Added chooses the greener 170-degree
sample and Requirement reuses only when all entries are already assigned. DOM
checks verify both exact labels and explanatory text. Real file browser checks
verify exact default/reset JSON and CSS mappings as well as visible labels.

Actual local Windows evidence: 128 common UI, 34 VS Code adapter, nine Electron
and 111 Python tests pass, as do Ruff lint/format and working validators. The first
Python run, concurrent with browser/build/host work, hit its 150-second outer tool
limit partway through Gantt tests with no final result; the unchanged sequential
rerun passed all 111. The standalone file:// browser suite passed, and its default
screenshot was inspected. Electron build and the complete direct Electron host
runner passed; VS Code compilation and the complete direct VS Code host runner
passed. These include all existing fill/hover/legend/root/label/geometry/form/draft,
watcher repair, native document lifecycle, sandbox/save/reload/history assertions.
No internal test timeouts or assertions were weakened and no production camera change was made.
Logs and optional screenshots remain ignored local evidence.

Update current README, technical conclusions, canvas guide and own-spec context.
The new intention B87C_kI= records the user's request, not an approval gate; the
separate IAy2dGI= selection conclusion remains revisable. Graph/schema format and
maintained example histories are unchanged. Existing unrelated checkout edits
(including fixture/history/workspace-policy work) were present during verification
and remain outside this palette slice. Stage only intended graph/code/docs and
validate the exact index; install no hooks and preserve unrelated work.
