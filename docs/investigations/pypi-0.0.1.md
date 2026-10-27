# First public CLI release: 0.0.1

The owner requested PyPI publication, a known repeatable workflow, the default CLI
installation path everywhere, and product versions aligned at 0.0.1. They supplied
repository `jejay/specspec`, workflow `pipy_publish.yaml` and environment `pypi`, and
authorized proceeding after discussing OIDC identity/signature verification.

## Choices and scope

- Python metadata/runtime, root/shared/VS Code/desktop package metadata and their
  local lock entries use 0.0.1. Third-party versions, internal node/protocol fields
  and the independent Gantt product's version are separate. This is not a schema
  migration or a reason to rewrite unrelated development history.
- PyPI is the default for human/agent/remote guides, packaged project instructions
  and both normal/native-editor missing-CLI screens: `uv tool install specspec`, or
  `pipx install specspec`. Explicit source/wheel alternatives remain. Older local
  0.1.0 installations may need explicit replacement rather than numerical upgrade.
- The README uses absolute project-documentation links so its PyPI rendering works
  without a checkout. UIs install independently; this does not publish npm packages,
  a Marketplace extension, GitHub Releases or portable desktop binaries.
- `.github/workflows/pipy_publish.yaml` intentionally matches the registered spelling.
  It is manually dispatched on main with an expected version. Source/lock/runtime
  agreement precedes graph/source/history checks, lint/tests and fresh CLI builds.
- The standard-library verifier accepts exactly the named CLI wheel/sdist, checks
  source/resource/identity metadata and rejects unsafe paths, links, duplicates,
  stale content and unintended upload-directory files. Strict Twine validation and
  isolated wheel/sdist installations precede the artifact handoff.
- Only the separate publisher job has OIDC permission. It does not check out or run
  project source, but downloads the same verified artifact and uses pinned PyPA
  tooling with attestations and duplicate rejection. GitHub signs short-lived
  identity; PyPI verifies issuer/audience/expiry and the registered claims before
  granting a temporary upload token. Existing environment protections are retained.
- Builds and ordinary pushes do not publish. The pending publisher alone neither
  reserves a name nor proves availability. Failed/partial upload states require
  inspection, not overwriting an immutable version or claiming atomic publication.

## Compatibility findings

The initial strict check selected Twine 6, which rejected the fresh backend's
valid metadata version 2.5. Inspection of the pinned PyPA action showed Twine 7.0.0
and packaging 26.2; a fresh isolated Twine 7.0.0 check passed both exact same
artifacts. Build verification now pins Twine 7.0.0 to match publication, rather
than weakening validation, rewriting metadata or claiming the failed check passed.
The CLI/runtime, wheel/sdist bytes and installed-host inputs are unchanged by this
validator correction. Both logs are retained.

The first focused run also exposed a Windows test using the locale encoding to
read UTF-8 UI source. It now names UTF-8 explicitly; the production encoding and
assertions remain unchanged.

## Qualification and publication record

Before first dispatch, the complete Windows suite passed **1123 tests**, with only
the POSIX executable-mode case skipped there. The required Linux publishing build
executes that unchanged case before upload; its actual results remain a separate
record, not an inference from Windows. Shared/VS Code/Electron unit suites passed
**267 / 53 / 11**. Ruff and formatting passed. Fresh isolated wheel and independently
installed source-distribution CLIs passed init/Git/guide-prefix/stdin/help/raw/newline
checks. The rebuilt 0.0.1 wheel/sdist/VSIX/desktop inspection passed; strict Twine
7.0.0 validation passed both exact Python artifacts. Both complete installed Windows
VSIX and portable-desktop suites passed sequentially against the fresh isolated CLI,
including the exact PyPI installation command and startup/initialization probes.

The complete 46-path candidate passes private-index graph/source checks for **239
project / 22 example nodes**, with zero errors/warnings. Four original bindings are
intentionally revised; all **231 other original node files retain exact bytes**.
The owner authorized publication after discussing its identity boundary, including
the needed reviewed commit/push/dispatch. Before that commit, the same checks run
against the actual staged index; its committed tree must equal the validated tree.
No owner installation, hook replacement, tag or unrelated history rewrite is needed.

The GitHub `pypi` environment was absent. It was created with a custom deployment
branch policy allowing only `main`; there were no existing protection rules to
remove. No reviewer/approval bypass was configured. Environment and API reports
contain configuration facts, not credentials.

The maintained Gantt corpus still verifies **8 revisions, 22 current nodes, 22
historical deletions, 123 actual operations and all three runnable stages**. Only its
final guide-audit commit was refreshed for current PyPI installation instructions;
the earlier stage commits/refs, actual CLI receipts, ledger, canonical node bytes
and application code remain unchanged. The previous bundle and fresh external clone
are retained. This is documentation alignment, not a schema/history migration.

The initial public `specspec` JSON endpoint returned 404, consistent with an unused
pending publisher. No successful upload or public installation is claimed by that
preflight. The source revision, workflow result, Linux case report and public-index
installation are recorded after they occur.

Local scripts, original bytes, failed runs, artifacts, GitHub/API reports and final
checks are retained in `.specspec/local/pypi-0.0.1/`. Credentials remain in existing
credential management or transient CI identity, never these reports. Original
artwork, archival owner inputs, manual clones and unrelated history remain preserved.
