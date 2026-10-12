---
id: ezKCR3w=
type: implementation
parents:
- 6QB9hRY=
sources:
- path: graph-ui-common/media/graph-model.js
  symbol: nine RAINBOW_COLORS and remapped TYPE_COLORS/REVISION_COLORS
- path: graph-ui-common/test/rainbow.test.cjs
  symbol: nine-color OKLCH, cycle and shared mappings
- path: graph-ui-common/test-host/ui.cjs
  symbol: palette probes and model-relative expanded root color
- path: docs/own-spec.md
  symbol: nine-color rainbow tuning
---
# Tune the shared rainbow to nine slightly stronger colors

Implement l3vgxN4= through the revised 6QB9hRY= palette choice. Keep OKLCH
lightness .73; increase chroma .11 to .12 (about 9%) and space nine hues 33.75
degrees apart from 300/violet to 30/red. All base samples are in sRGB gamut and
rounded to hex bytes. Replace the shared table, not card tint or hover constants.
One hop is violet, nine red and ten violet again. Remap type teal/violet to 4/0
and revision green/blue/red/amber to 5/1/8/7, with renamed sharing modified blue.
No fill-mode, gray/colored manifesto, comparison, edge, draft or schema behavior
changes; no example-history rewrite is needed. Older thirteen-color evidence is
explicitly historical rather than silently rewritten into a nine-color claim.

Update independent OKLCH regression expectations for nine unique colors, .12
chroma at .73 lightness, wider even hue intervals, cycle wrap and shared-table
mappings. The real-host expanded-root assertion now compares with the model's
modified swatch rather than the previous hard-coded hex. Palette size in legends
already derives from table length. Refresh README, technical conclusion, canvas
guide and own-spec tour, while keeping unrelated pre-existing edits unstaged.

Actual Windows checks passed: 115 common, 34 VS Code, nine Electron and 111 Python
tests; Ruff lint/format and both working graph validators with warnings as errors.
Both host assets were rebuilt. Full Electron with screenshots passed, including
all nine palette probes, dark/light/contrast fill/hover checks, colored expanded
manifesto, routing/camera/native editing and historical/workspace switching.
The first screenshot-enabled VS Code run failed in optional Page.captureScreenshot:
"Command can only be executed on top-level targets". No palette assertion failed
before that error. Retain that failed log/profile; no production or harness target
selection was changed for this tuning. The unchanged full suite rerun without
screenshot capture passed canvas/paint plus native save/undo/redo/split/CRLF/Unicode
checks. Electron revision/expanded-root screenshots were inspected. Logs/images
stay in ignored local state, not canonical graph artifacts.

Keep earlier suite evidence separate from these actual runs. Tests use independent
disposable maintained-history clones in the current working tree; unrelated existing
fixture/history/workspace-policy changes are not part of this palette commit.
Validate the exact intended staged graph before the separate implementation commit;
install/replace no hooks. Constants remain revisable and local Chromium evidence
is not certification of every platform/theme/display gamut or accessibility.
