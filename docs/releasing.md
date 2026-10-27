# Release and publish specspec

The current product version is **0.0.1** across the CLI, VS Code extension, desktop
and private shared/root workspaces. The **CLI publishes to PyPI**; the VSIX and
portable desktop remain local artifacts. Normal installation is
`uv tool install specspec` or `pipx install specspec`.

Local build/test/package commands never publish, create tags, stage, commit or
install into an owner's profile. Publication uses an explicit GitHub workflow run.
Marketplace/npm publication, GitHub Releases, signing and tags are separate actions.

## PyPI Trusted Publisher setup

These exact values bind the owner's publisher:

| Setting | Value |
| --- | --- |
| PyPI project | `specspec` |
| GitHub repository | `jejay/specspec` |
| Workflow filename | `pipy_publish.yaml` |
| Workflow path | `.github/workflows/pipy_publish.yaml` |
| GitHub environment | `pypi` |
| Release branch | `main` |

Keep the filename spelling exactly as registered, even though it says `pipy`.
Configure the GitHub environment to allow deployments from `main`; retain existing
protection rules and optionally require a reviewer. A required approval must be
completed by an authorized person; the workflow does not bypass it.

GitHub signs a short-lived identity token with its private key. PyPI verifies that
signature through GitHub's public OIDC keys, then checks issuer, audience, expiry and
repository/workflow/environment identity against this publisher. PyPI grants a
short-lived upload token, not permanent account access. No long-lived PyPI token is
stored in the repository or GitHub secrets. A pending publisher neither publishes
nor reserves a project name; the first successful upload creates the project and
converts it to a regular publisher.

## Publish the CLI

1. Prepare a coherent release revision on `main`. Update `pyproject.toml`, runtime
   `__version__`, all four npm metadata files, their local lock entries and current
   versioned documentation/examples together. Keep third-party dependencies and
   internal schema/protocol numbers separate. Do not reuse an uploaded version.
2. Review all owner/agent changes and complete the qualification below. Before an
   authorized commit, stage the whole intended graph/code slice and check exact
   staged graph/source bytes. Commit and push that reviewed revision to `main`.
   Publishing authorization does not authorize force-pushing unrelated history.
3. On GitHub, open **Actions → Publish CLI to PyPI → Run workflow**. Select `main`
   and enter the exact expected version, initially `0.0.1`. The workflow is manual:
   ordinary pushes, pull requests, local builds and application actions do not upload.
4. Wait for both jobs. `build` checks metadata/lock alignment, specification/source
   mappings, maintained history, Ruff and Python tests; builds only wheel/sdist;
   verifies exact membership/source/resources/metadata; runs strict Twine validation;
   and exercises fresh isolated installations of both artifacts. Node supplies
   integration-test subprocesses, not a CLI runtime or npm publication.
5. Only after success does `publish` download those same two artifacts. It has no
   project checkout or project-code execution, but alone receives `id-token: write`.
   Pinned actions publish through the `pypi` environment with attestations. Artifacts
   are retained for 14 days. Duplicate uploads fail; nothing silently overwrites a
   release. Local qualification cannot substitute for observing this remote run.
6. Check [the public project](https://pypi.org/project/specspec/) and release file
   hashes against the verified workflow artifacts. Test a fresh isolated install
   from the index, not the checkout or a local wheel. Confirm `specspec --version`,
   `init -m "Test"`, Git/guide creation, stdin editing and graph checks. Only then
   report public availability. Retain the run URL, source commit and artifact hashes.

If identity fails, check the exact repository, filename, environment and job-level
permission; do not add a personal token as an unnoticed workaround. If upload fails
partway, inspect PyPI's actual files/hashes before retrying. Registry publication is
not an all-or-nothing transaction; strict duplicate rejection can make a blind rerun
fail. Preserve existing files and diagnose the missing work rather than overwriting
bytes or claiming success from a dispatched workflow alone.

## Build and inspect locally

With the developer environment active and Node 22.12+ / npm 10+ available:

```sh
python -m pip install -e '.[dev]'
npm ci
npm run package:all
```

Ignored `dist/` contains:

| Artifact | Use |
| --- | --- |
| `specspec-0.0.1-py3-none-any.whl` | Exact-artifact CLI installation/qualification |
| `specspec-0.0.1.tar.gz` | Python source distribution, including the init guide |
| `specspec-vscode-0.0.1.vsix` | Ordinary local VS Code installation |
| `specspec-desktop-0.0.1-win32-x64.zip` | Windows portable app, architecture-dependent |
| `specspec-desktop-0.0.1-linux-x64.tar.gz` | Linux portable app, architecture-dependent |
| `desktop/specspec-desktop-PLATFORM-ARCH/` | Unpacked current-platform runtime |
| `release-manifest.json`, `SHA256SUMS` | Artifact sizes/versions/SHA-256 addresses |

A local build creates one platform's desktop archive, not both. `verify:packages`
checks version alignment, Python resources/entry point, VSIX assets/notices/selector,
portable runtime allowlist/licenses and archive contents. Linux tar preserves
executable modes. These checks do not establish every-platform execution, semantic
correctness, signing or byte-identical builds across machines. The Python sdist is
not the UI source monorepo.

To reproduce only the publisher's artifact checks, use a fresh `dist/pypi/` directory
containing exactly the intended pair, never stale UI/older-version artifacts:

```sh
python -m build --outdir dist/pypi
python -m tools.pypi_release verify --expected 0.0.1
python -m twine check --strict dist/pypi/*
python -m tools.pypi_release smoke --expected 0.0.1
```

Install Twine separately into the developer environment if needed (`twine==7.0.0`),
matching the pinned publishing action. This supports the backend's current metadata;
do not substitute an older validator or bypass strict validation.
`verify` is non-publishing; `smoke` creates disposable isolated environments/projects
and installs only there, preserving failed evidence for diagnosis. Successful smoke
resources are cleaned up. The manual **Build release artifacts** workflow still
builds/uploads local Windows/Linux artifacts and does not publish.

## Qualification checklist

1. Inspect status, complete graph/code diffs and untracked files. Preserve experiments,
   drafts and recovery journals. Record the intended source revision and tool versions.
2. Run working graph/source, Ruff, formatting, Python and npm checks from
   [contributing](../CONTRIBUTING.md). Verify every maintained Gantt ref/runnable stage;
   obsolete development schemas are not compatibility fixtures. Inspect skip reasons
   with `python -m pytest -ra`. Run POSIX archive-mode tests on native Linux or WSL's
   Linux filesystem, not `/mnt/c`; a Windows skip is not Linux qualification. Disposable
   Git tests own their identity/configuration, not an owner's global Git settings.
   See [permission-test evidence](investigations/final-newline.md).
3. Use the locked root npm installation, inspect audit findings and actual dependency
   notices. Record current findings as bounded observations, not a timeless assurance.
4. Build/reinspect artifacts and retain digests. Test fresh wheel and independently
   built sdist installations outside the checkout with version/help/init/query/update/
   check, exact existing-guide preservation, raw reads and automatic stdin.
5. Install the VSIX in disposable extensions/user-data directories and exercise the
   actual portable app against the isolated CLI. Preserve native Save/undo/dirty,
   managed consent, invalid-graph, source, watcher, comparison and trust safeguards.
   Do not replace owner installations to qualify a build.
6. Record executed operating systems and unexecuted targets. Cross-builds, declared CI
   jobs or screenshots are not execution. Before authorized commits, check both exact
   staged graphs/sources and verify the commit tree equals the validated index.

## Dependency and evidence boundaries

One root npm lock pins UI/build dependencies. Script approvals cover Electron,
esbuild and the VSIX signing helper; application renderers do not use remote/CDN
code. Electron 44.9.3, undici 7.30.1 and build-tool MSAL 7.1.1 retain their scoped
qualification. The MSAL major override supports local VSIX creation, not Azure login
or Marketplace authentication. Python Trusted Publishing does not establish those
unrelated publishing paths. Reassess overrides with compatible upstream releases.

[Earlier local release evidence](investigations/release-0.1.md) and
[onboarding qualification](investigations/owner-experience.md) retain their checkpoint
scope. [PyPI release evidence](investigations/pypi-0.0.1.md) records this release's
executed checks, workflow outcome and index verification. Preserve supplied artwork,
source drafts, experiments and unrelated development history.
