---
id: iER7QwM=
type: implementation
parents:
- PfJv45U=
- 1aSOZOs=
- FU5NaYc=
- qwZfjCk=
- Skan1U4=
sources:
- path: .github/workflows/ci.yml
- path: .vscode/launch.json
- path: .vscode/tasks.json
- path: AGENTS.md
- path: README.md
- path: electron/test-host/run.cjs
- path: example/gantt/README.md
- path: example/gantt/history/verify.py
- path: graph-ui-common/host/session.cjs
- path: graph-ui-common/package.json
- path: graph-ui-common/test-host/ui.cjs
- path: graph-ui-common/view.cjs
- path: specspec-dev.code-workspace
- path: tests/test_gantt_example.py
- path: tests/test_ids.py
- path: tests/test_repository_spec.py
- path: vscode/.vscode/launch.json
- path: vscode/scripts/build-webview.cjs
- path: vscode/test-host/run.cjs
- path: vscode/test-host/smoke.cjs
- path: vscode/test-host/ui.cjs
- path: example/gantt/history/checkout.py
- path: example/gantt/history/gantt.bundle
- path: graph-ui-common/test-host/fixture.cjs
- path: tests/test_example_checkout.py
- path: tests/test_gantt_git.py
- path: tests/test_repository_docs.py
- path: .gitattributes
- path: .gitignore
- path: graph-ui-common/test-host/budgets.cjs
- path: vscode/test/budgets.test.cjs
- path: graph-ui-common/test/host-ui.test.cjs
- path: graph-ui-common/test-host/platform.cjs
---
# Validate and document the working graph and planning process

CI and repository tests validate this graph, its source references, complete agent
context and manual-edit behavior. Repository tests also check node text for doubled
words and lowercase sentence starts, keep AGENTS.md equal to a repository section
followed by the shipped guide, resolve local links in the kept documents and check
the README figures. Development launches open the working specification. AGENTS.md supplies the routine and phase rules, and its repository section names the checks that cover each kind of change; Git carries revision reasons and evidence.

Artifact tests check exact brand imports, non-text attributes and narrowly ignored
machine-local settings with shared launch files tracked. Independent example
histories supply temporal integration; local experiments and diagnostic/recovery
state stay intact.

The shared smoke budget module covers complete shared, native and desktop-reload
phases with separate bounded aggregate guards. CDP failure/foregrounding regressions
and explicit-value Code launch arguments protect diagnostic meaning and workspace
selection. Disposable profiles alone enable loading traces and background-throttling
controls. Complete installed Windows suites exercise all backchannel,
exact-deletion/repair/recovery and host-native checks. Node-text regression guards
recognize retired-design sections while permitting current runtime read-supersession
contracts. Static-help subprocess tests cover legacy Windows pipe encodings.
