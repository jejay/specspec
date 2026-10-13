---
id: EpO6sR4=
type: implementation
parents:
- YaXJpGE=
- 3fWBW_g=
sources:
- path: electron/test-host/run.cjs
- path: example/gantt/AGENTS.md
- path: example/gantt/README.md
- path: example/gantt/history/WALKTHROUGH.md
- path: example/gantt/history/checkout.py
- path: example/gantt/history/cli.jsonl
- path: example/gantt/history/gantt.bundle
- path: example/gantt/history/revisions.json
- path: example/gantt/history/verify.py
- path: example/gantt/test/browser.cjs
- path: graph-ui-common/test-host/fixture.cjs
- path: tests/test_example_checkout.py
- path: tests/test_gantt_example.py
- path: tests/test_gantt_git.py
- path: tests/test_repository_spec.py
- path: vscode/test-host/run.cjs
- path: .github/workflows/ci.yml
- path: example/gantt/STORY.md
- path: example/gantt/app.js
- path: example/gantt/model.js
- path: example/gantt/test/model.test.cjs
---
# Maintain actual Gantt planning, code and verification stages

The complete standalone bundle has an empty predecessor, three specification/code
pairs and an audit. The local browser planner's independent graph maps intentions
through manual-date/weekday/baseline/JSON choices to actual model/browser code.
Each stage's positive binding text precedes its runnable code. Redirect commits
explain removed branches and predecessor trees retain their reasoning.

`cli.jsonl` contains actual managed CLI inputs/results; `revisions.json` records
stage commits and receipt ordinals. The verifier checks all retained refs, current
schema/DAG/source retention, exact indexes, recorded context/impact, stage order,
semantic/edge/source deltas, redirects and isolated model stages. Runtime/snapshot
agreement is checked byte-for-byte. Browser tests cover real local planning/input/
file/storage behavior. Independent corpus clones supply Git and host integration.
