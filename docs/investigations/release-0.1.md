# Preparing the first local release

> Historical release-preparation evidence. Current initialization, stdin, storage,
> naming and startup behavior follows [the owner-experience revision](owner-experience.md).
> Recorded counts/outcomes below belong to that earlier checkpoint; diagnostic paths
> use their preserved current location after the runtime-directory move.

The owner requested `.specspec/`, an installable monorepo-style 0.1 CLI/VS Code/
Electron delivery, a clearer branded introduction and agent guidance created with
new projects. The changes preserve the current intention/conclusion model, full
IDs, format/API 7, native versus managed save ownership and explicit Git control.

## Choices and boundaries

- `.specspec/` is the sole canonical directory; `.specspec/local/` remains runtime
  state. Discovery, literal paths/placeholders, Git/source roots, spotlights,
  watchers and both editors change together. Regex dots are literal. There is no
  permanent conversion command or fallback reader.
- The global isolated CLI is the normal prerequisite for both UIs. Python packaging
  remains independent; CLI users need no Node. One private root npm workspace/lock
  provides UI development, tests, local VSIX creation and portable desktop builds.
- A normal local VSIX install replaces the need for an F5-only workflow. No
  Marketplace/publishing step or owner extension installation is performed by builds.
- Portable Electron packages allowlist runtime files, retain their local assets and
  licenses and use the selected launcher. Python/Git are external. ZIP serves Windows;
  tar preserves Linux executable modes. Cross-building is not qualification.
- The packaged root agent guide adapts the supplied conceptual/CLI drafts and current
  process. Existing AGENTS.md entries are preserved, never merged. New instructions
  share initialization journaling, exclusive publication and external-byte protection;
  they do not enter canonical graph membership or imply agent execution.
- The introduction uses the exact selected primary logo exports, not reconstructed
  lettering or historical proposals. Brand gradients remain separate from graph
  semantics. Original owner artwork and sibling draft/branding workspaces remain intact.

The root release inspector checks Python resources/current code, VSIX contents/
selector/assets/notices, runtime allowlists, versions and archives, then records
hashes. It never publishes, stages, commits, tags or installs owner hooks/extensions.

## Integration findings

The first initialization-test run used a 1 MiB string as a parameter ID. That
exceeded practical Windows test-path limits before the oversized-input assertions
could run; explicit short test IDs fix the harness, retaining the actual size test.
The full initialization suite then passed all 28 cases.

The first npm workspace lock reused incomplete metadata from the separate installed
trees, leaving missing resolved/integrity identities and skipped pinned install
scripts. A fresh root lock/install, with the three obsolete nested locks removed,
produces one registry-addressed dependency tree. Script approvals are root-scoped.
The shared license collector now follows actual esbuild input paths, including
hoisted dependencies, rather than losing notices outside a workspace's own
node_modules. Both UI builds report 24 bundled dependency notices.

An initial dependency audit found four high findings, including Electron's
certificate mitigation and build-tool MSAL/undici advisories. The final root lock
pins patched Electron 44.9.3, undici 7.30.1 and build-tool MSAL 7.1.1. The latter is
a deliberate major override for local VSIX creation only; Marketplace/Azure login
compatibility is not claimed. A fresh `npm ci`/audit reports zero current findings,
which is not a permanent security guarantee.

Actual packaging also exposed new upstream/tool-layout assumptions: Packager 20
exports a named function and defaults to ASAR; this delivery explicitly selects its
named API and a directly inspectable unpacked runtime. VSCE 4 emits `readme.md` and
`LICENSE.txt`, which the inspector checks as actually packaged. Earlier failed logs
remain available. These corrections preserve runtime allowlisting, not a fallback
that bundles development material.

The installed VSIX probe first assumed a direct Code resources directory; the local
installation uses a version-folder layout. A tested locator handles direct or one
unambiguous version folder. A subsequent harness assertion used a property not on
VS Code's public Extension object; it was replaced by exact installed-directory
ownership checks. The actual product is installed by the normal CLI into a disposable
extension directory; only a separate tiny test controller is a development extension.
The complete successful suite follows both failed setup attempts in retained logs.

Fresh global-style CLI qualification separately checks parsed and physical text.
An initial assertion incorrectly expected literal CRLF in parsed node JSON, whose
existing API-7 semantic projection normalizes it to LF. Saved bytes and raw query
text preserve the literal CRLF replacement. The probe, current descriptions and
separate conclusion now make that distinction explicit; no runtime/protocol change
was introduced to make the assertion pass.

## Maintained history

All eight retained Gantt revisions/refs are reconstructed externally through 123
actual current CLI operations, not edited old receipts. Every earlier/deleted node,
source anchor, ledger and bundle uses `.specspec/`. Node identities, chronology,
redirects, parent topology and application behavior remain intact. The only intended
application-byte adjustment is literal canonical-directory wording in the HTML
footer; the models, scripts and runtime behavior are unchanged. Existing manual
clones and unrelated specspec history remain preserved, with no nested Git metadata
installed in the tracked snapshot.

## Verification record

The final complete Python suite passes **941 tests with one POSIX-executable-mode
case skipped on Windows**. This includes the added logical/raw regression and broader
local-link coverage. The earlier complete run passed 935 before those additions.
All npm suites pass: **257 shared UI, 49 VS Code, 10 Electron**. Ruff, formatting
(365 Python files) and whitespace checks pass. The complete root `package:all` chain
builds and inspects wheel, sdist, VSIX and the Windows portable archive successfully.
Final desktop file bytes and uncompressed VSIX member bytes exactly match the
successfully host-qualified artifacts; archive/container timestamps can change their
outer hashes. Wheel/sdist digests remain identical to the freshly installed artifacts.

Fresh isolated uv-tool installations from both the wheel and sdist pass version/help,
Unicode authoring, newline-tolerant replacement, literal stored/raw CRLF, parsed logical
layout, generated-guide and non-UTF-8 owner-guide preservation checks. The module
origins are installed site-packages, not editable checkout imports. Node can invoke
the isolated executable as `specspec` from PATH. Owner tool/bin directories were not
replaced. A clean source archive outside this repository, with a spaced/non-ASCII
path, no .git and no sibling workspaces, builds CLI and VSIX successfully; its root
install also passes with explicitly probed **npm 10.9.4** on local Node 24.21.0.

Both **complete installed Windows artifact-host suites pass** against that isolated
CLI. VS Code confirms the actual VSIX installation path before running managed and
native save/undo/redo/split/raw/invalid-buffer/Unicode/CRLF, source, watcher, comparison,
exact deletion/repair and spotlight checks. The actual portable desktop executable
passes the shared suite, sandbox/request boundaries, persisted draft/list reload and
historical/workspace switching. Shared UI phases were approximately 161 seconds
VS Code and 156 seconds Electron: local observations, not responsiveness guarantees.
Test-controller setup is not Marketplace publication or owner-profile installation.

The complete candidate's **exact temporary index** passes graph/source checks for
**226 project and 22 example nodes**, with zero errors/warnings. All **199 other
original project node files retain exact saved bytes** after the directory move;
16 deliberately updated originals are reviewed separately. Git detects canonical
renames; a review-only alignment of saved old paths supplies semantic/ripple evidence
without adding a product compatibility reader. That preparation pass left the real
index untouched. The owner's subsequent GitHub push request authorizes staging and
committing the complete slice; graph/source checks are repeated against that actual
index before commit, with the committed tree checked against the validated index.

The Gantt snapshot is inside the development repository. During preparation its
new verifier/HTML source blobs were retained by the candidate's staged source tree,
not the unchanged real index, so plain snapshot source checks reported unretained
anchors. Staging the coherent corpus supplies their actual upcoming source tree.
Actual-index checks and every independent bundled revision validate that retention;
no source identity or retention rule is bypassed. The push sends the source history
without a force-push, release tag, registry/Marketplace publication or ignored build
artifacts.

Local diagnostic logs, input digests, clean-install evidence, preserved failed runs,
reconstruction locations and review/artifact reports live under
`.specspec/local/release-0.1/`. Notably: `python-final.log`, `npm-final.log`,
`cli-install-checks.json`, `vscode-artifact-host.log`, `electron-artifact-host.log`,
`history-final.log`, `candidate.json`, `review.diff` and `original-byte-review.json`.
Physical Linux/macOS and remote SSH/tunnel execution have not been rerun locally for
this slice; the POSIX archive-mode skip is not Linux qualification. No remote CI run,
publication, release tag, signing, owner-global-tool replacement or hook installation
is claimed. Passing tests remain bounded evidence rather than proof.

## Supplied input identities

The reviewed drafting/branding inputs remain unchanged in their sibling workspaces.
SHA-256 records (also retained as `input-digests.json`):

| Input | SHA-256 |
| --- | --- |
| `specspec-agentsmd/RESULT_AGENTS.md` | `76a6ef74014ad8b91679fb1a45adab90b05a7038bdde475c54d60cb4f7bed64f` |
| `specspec-agentsmd/CLI_COCS_7500.md` | `3e9c9d6d6b2999be975bdd35cb6436b29b724fc9c03229389af9cb68af27e33a` |
| `specspec-agentsmd/CLI_COCS_6000.md` | `4cf1cee770be26bb45c67c1badf6518165a483344208b80b3753b6954a5086c9` |
| `specspec-branding/FINAL.md` | `505abf13fe3b4e02eef7761d9ee829312d0c2048df1cb173aab53df11297564e` |
| `specspec-branding/final/BRAND-GUIDE.md` | `a8b99f093a3c9a21f3d1ec1626e636f752dc80dc6de66c266eb17362d5b4e137` |

The local brand manifest separately records exact production-asset import bytes.
The Windows ICO is a documented container derivative, not a byte-identical export.
