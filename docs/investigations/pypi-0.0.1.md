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
subsequently executed that unchanged case before upload. Its actual results are
recorded separately below, not inferred from Windows. Shared/VS Code/Electron unit suites passed
**267 / 53 / 11**. Ruff and formatting passed. Fresh isolated wheel and independently
installed source-distribution CLIs passed init/Git/guide-prefix/stdin/help/raw/newline
checks. The rebuilt 0.0.1 wheel/sdist/VSIX/desktop inspection passed; strict Twine
7.0.0 validation passed both exact Python artifacts. Both complete installed Windows
VSIX and portable-desktop suites passed sequentially against the fresh isolated CLI,
including the exact PyPI installation command and startup/initialization probes.

The complete 46-path candidate passed private and actual-index graph/source checks
for **239 project / 22 example nodes**, with zero errors/warnings. Four original
bindings were intentionally revised; all **231 other original node files retained
exact bytes**. Commit `487240a103cfeac3115730505011555fbb46b85d` has the exact validated
tree `2a7b3dfa333c88e372e6d788b0c6b1a4214214e3`. The owner authorized publication after
discussing its identity boundary, including the reviewed commit/push/dispatch.
The push was a normal fast-forward, with no owner install, hook replacement,
release tag or unrelated history rewrite.

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

### Successful publication

The initial project endpoint returned 404. The explicit
[release run 40468093394](https://github.com/jejay/specspec/actions/runs/40468093394)
subsequently completed both build and publish jobs successfully on source commit
`487240a103cfeac3115730505011555fbb46b85d`. Its Linux Python 3.11 suite executed
**1124 tests, all passed, zero skipped**. The downloaded JUnit report has exactly the
same 1124 case identities as Windows; its sole skipped Windows permission case
passed on Linux. No suite case remains unexecuted across those runs.

PyPI accepted the wheel at **2026-10-27 07:38:07 UTC** and sdist a second later.
The public version endpoint confirms [specspec 0.0.1](https://pypi.org/project/specspec/0.0.1/)
and these non-yanked files. Downloaded verified workflow artifacts match PyPI's
sizes/SHA-256 values; all 31 packaged Python/resource files and the sdist README
also match the release commit's literal Git blobs.

| Public artifact | SHA-256 |
| --- | --- |
| `specspec-0.0.1-py3-none-any.whl` | `c35d9b4c5e1bc503d7072206618e2139cc7bb2648be25354e557724079d7bc40` |
| `specspec-0.0.1.tar.gz` | `88407daa88512f7081c3b27f2b2f4ccb6323eb74d645c2984b5c1f19e35f4955` |

Fresh isolated uv tools installed the ordinary unpinned `specspec` index default and
the actual public sdist URL independently. Both report runtime/distribution version
0.0.1 and import from isolated site-packages, not the checkout. Probe, init/Git,
exact guide-prefix append, stdin, replacement, metadata preservation, removed-flag
rejection, hidden help, raw reads and strict graph checks passed. Owner tools and
editor installations were not replaced.

PyPI's Integrity API serves provenance for both files, identifying repository
`jejay/specspec`, workflow `pipy_publish.yaml` and environment `pypi`. Each statement's
subject name/digest matches its public file. This inspects the server's published
provenance record; it does not claim a separate independent Sigstore chain audit.
Cross-machine build hashes can differ: the verified GitHub artifacts above, not the
locally built container hashes, identify the public release.

### General CI follow-up

The separate [general CI run 40468045255](https://github.com/jejay/specspec/actions/runs/40468045255)
failed while the dedicated publishing workflow passed. Windows compared a CRLF
tracked runtime checkout directly with an LF Git blob; Linux's Spotlight-only test
counted an independent late startup Git-discovery refresh. Matrix fail-fast cancelled
siblings, so those cancelled jobs are not qualification. Both Linux/Xvfb and Windows
source-desktop host/package jobs completed successfully, but that did not make the
entire general workflow pass.

The fixture verifier now compares saved files through the owning checkout's existing
Git clean policy when raw bytes differ, preserving exact expected blob bytes and
SHA-1/SHA-256 support. Four focused encoding/object-format regressions reject actual
text/blank-line/EOF changes and verify that file bytes, Git config and index remain
untouched. The product runtime and its byte-exact source/transaction rules do not
change. The maintained final audit carries this verification-tool correction while
retaining stage commits, receipts, ledger, canonical nodes and application bytes.

A controlled execution of the original Spotlight test holds Git discovery until its
read-count baseline, then completes that real watcher path. It reproduces the same
class of failure (6 versus 4 locally; 5 versus 4 in CI). The corrected test holds
that unrelated discovery pending until teardown; separate controlled-clock tests
still verify the legitimate late graph refresh. The production watcher, debounce,
read budgets and strict zero-extra-graph-read assertion remain unchanged. Details
also appear in [the scheduling investigation](polling-test-race.md).

A fresh external enclosing checkout configured with CRLF reproduces the original
raw comparison failure and passes the complete corrected history verifier. Its
runtime bytes, Git configuration and exact index bytes remain unchanged. The
corrected Spotlight test passes ten isolated repetitions; all 267/53/11 npm cases
and 73 focused Python/history/documentation cases pass. Follow-up exact-index
checks cover **240 project / 22 example nodes**, with no source warnings. These
verification-only changes leave the published 0.0.1 Python/guide/README bytes intact;
registry artifacts are not replaced.

The [next general run](https://github.com/jejay/specspec/actions/runs/40471258799)
passed the corrected Spotlight test and both Linux Python jobs, while exposing an
exact one-read native-bootstrap assumption. Initial Git discovery can invalidate
that pending context, legitimately requiring a second read before any redraw timer.
A causal regression now blocks the first read, completes real watcher discovery,
and asserts exactly two reads, fresh content and no error. Stable-input bootstrap,
canonical-watcher and Spotlight count tests explicitly hold only this unrelated
provider pending; other fixture cases retain real Git. The VS Code suite passes
**54** cases with the added regression, without weakening either exact count or
changing production scheduling. This is another test-oracle correction, not a
published runtime update.

Local scripts, original bytes, failed runs, artifacts, GitHub/API reports and final
checks are retained in `.specspec/local/pypi-0.0.1/`. Credentials remain in existing
credential management or transient CI identity, never these reports. Original
artwork, archival owner inputs, manual clones and unrelated history remain preserved.
