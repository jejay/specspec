# Build and qualify a local 0.1 release

This procedure prepares artifacts; **nothing here publishes to PyPI, GitHub Releases,
npm or the VS Code Marketplace**. Tags, commits, signing, owner installation and
publication require separate explicit authorization. No Marketplace submission is
part of 0.1 preparation.

## Outputs

From one checkout, with the development Python environment active and Node 22.12+ /
npm 10+ installed:

```sh
python -m pip install -e '.[dev]'
npm ci
npm run package:all
```

Version metadata is aligned at **0.1.0** across the Python project/runtime and all
npm workspaces. Output under ignored `dist/`:

| Artifact | Use |
| --- | --- |
| `specspec-0.1.0-py3-none-any.whl` | Install the global CLI with uv tools or pipx |
| `specspec-0.1.0.tar.gz` | Python source distribution, including the init guide |
| `specspec-vscode-0.1.0.vsix` | Install into an ordinary VS Code instance locally |
| `specspec-desktop-0.1.0-win32-x64.zip` | Current Windows portable app, architecture-dependent |
| `specspec-desktop-0.1.0-linux-x64.tar.gz` | Current Linux portable app, architecture-dependent |
| `desktop/specspec-PLATFORM-ARCH/` | Unpacked current-platform Electron runtime |
| `release-manifest.json`, `SHA256SUMS` | Artifact versions, sizes and SHA-256 addresses |

A local build makes **one** platform's desktop archive, not both. The source monorepo
for UI development comes from the repository, not the Python-only sdist. Root npm
scripts do not install the resulting VSIX into an owner's profile.

`npm run verify:packages` rechecks version alignment, packaged Python resources and
console entry point, VSIX runtime/shared assets/notices and canonical selector,
desktop runtime allowlist/licenses and archive contents. The Linux archive preserves
executable modes. These checks do not establish signing, every-platform execution,
semantic correctness or deterministic identical bytes across build machines.

## Qualification checklist

1. Inspect owner status, full graph/code diffs and untracked files. Keep existing
   experiments, drafts and journals. Record the intended source revision and tools.
2. Run the working graph/source, Ruff, formatting, Python and npm checks in
   [contributing](../CONTRIBUTING.md). Verify every maintained Gantt ref and runnable
   stage; do not use obsolete specspec development schemas as compatibility fixtures.
   Inspect skip reasons with `python -m pytest -ra`. Permission-sensitive Linux
   archive tests need a POSIX filesystem: use native Linux or an isolated WSL
   checkout on its Linux filesystem, not `/mnt/c`. A Windows skip leaves that
   contract unverified until the unchanged case runs there. Disposable Git tests
   configure their own identities; do not set an owner's global identity to pass
   tests. See the [permission-test investigation](investigations/final-newline.md).
3. Run a clean root `npm ci`; inspect `npm audit` and the actual built dependency
   notices. Record findings and mitigations, not a timeless “secure” claim.
4. Build all local artifacts, run `verify:packages`, and retain its manifest/digests.
5. Install the wheel with **isolated tool directories** outside the checkout, put its
   executable on a disposable PATH, and run version/help/init/query/add/update/check.
   Confirm `.specspec/` and the exact packaged root `AGENTS.md`; test preservation of
   existing instructions. Do not replace the owner's global installation for a test.
6. Rebuild/install a wheel from the sdist independently. This catches an omitted
   template that editable or direct-wheel tests could miss.
7. Install the VSIX into a **disposable VS Code profile/extensions directory** and
   test it there, not only via `--extensionDevelopmentPath`. Point it at the isolated
   CLI. Verify the packaged native custom editor, managed save, sources, repairs,
   watchers, comparisons and existing trust/dirty/consent guards.
8. Run the actual unpacked desktop executable against an external disposable graph,
   using the isolated global-style CLI path. Confirm its assets/shared adapter are
   self-contained and repeat the real desktop regression suite. Retain sandbox and
   permission restrictions. `SPECSPEC_DESKTOP_EXECUTABLE` selects this artifact in
   the existing runner; `SPECSPEC_PYTHON` selects fixture construction/inspection.
9. Report executed operating systems, input/filesystem limits and unexecuted targets.
   CI declarations, cross-builds and screenshots are not substitutes for execution.
10. If a commit is authorized, stage the complete intended graph/code slice and run
    exact-index source checks for both this graph and the example. Verify the
    committed tree is the validated index. Preparing artifacts alone does not
    authorize this step or create a tag.

The manual **Build release artifacts** workflow performs builds/checks and uploads
workflow artifacts on Windows/Linux. It is not a publishing workflow; running it
requires a pushed source revision and is not claimed by local preparation.

## Dependency boundaries

The single root lock pins all UI/build dependencies. Root npm 12 script approvals
are pinned for Electron, esbuild and the VSIX signature helper; older npm versions
use their own installation-script behavior. Dependency installation can download
the pinned framework/tools. Application renderers do not use remote/CDN code.

Electron is pinned to a patched 44.9 release. The root overrides pin `undici` to
7.30.1 and the VSIX tool's otherwise vulnerable MSAL dependency to 7.1.1. That MSAL
major override is **build-tool-only**: local VSIX creation is tested, while Azure
login, Marketplace publishing and authentication compatibility are not offered or
qualified by this setup. Neither VSCE nor its auth dependencies enter the VSIX or
desktop runtime. Reassess the override when upstream VSCE/Identity adopts a fixed
compatible range; do not infer general publishing support from a clean audit.

The [release investigation](investigations/release-0.1.md) records actual commands,
failures/corrections and qualification. Keep it current before calling preparation
complete. Preserve original branding/draft inputs and unrelated development history.
