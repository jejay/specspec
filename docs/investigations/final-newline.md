# Tool-written final newlines and complete test coverage

The owner requested a final newline on complete tool-written node documents, using
existing local style and preserving intentional trailing blank lines. The shared
serializer and native form planner append a terminator only when absent, before
checking the final byte limit. This applies to body and metadata updates alike.
Native empty repair bodies remain empty when their frontmatter already terminates
the document. Reads, raw-editor persistence and existing unterminated manual or
historical nodes retain their contracts. Git settings and attributes stay untouched.

The choice is `Pek6TGE=`. Related message/replacement/storage contracts and the CLI
realization are reconciled with it. `tests/test_final_newline.py` covers LF/CRLF/CR,
messages and stdin, existing blank lines and spaces, replacements/composed adds,
metadata-only repairs/no-ops, exact raw reads, empty native bodies and size limits.
Installed Windows host probes enter an unterminated native VS Code draft and an
unterminated managed Electron draft and assert the resulting termination.

## Investigating the skipped permission test

The Windows suite reported one skipped case:
`test_local_artifacts_get_hashes_and_preserve_target_archive_semantics[linux]`.
That leaves a real qualification gap; a successful Windows archive test does not
verify Linux executable permissions.

An explicit unskipped Windows diagnostic reproduces the failure. A file remains
mode `0666` after `chmod(0755)` on this Windows filesystem. The generated Linux tar
therefore lacks execute bits, and the unchanged release inspector correctly raises
`Linux portable archive lost executable permissions.` The production packager builds
current-platform applications; this is not evidence of a working Linux cross-build.
Neither its permission assertion nor the test's platform applicability was weakened.

The unchanged case is executed on **Ubuntu under WSL2, on ext4**, not `/mnt/c`.
It passes there. The final complete Python suite also runs there with **1057 passed,
zero failures, zero errors and zero skipped tests**; its JUnit result is checked for
zero skips. This establishes the tested Python/archive semantics in that environment,
not a qualified Linux graphical application or macOS/remote-host execution.

## Failures exposed by the complete Linux run

The first full Linux run had four failures. Two deletion tests committed disposable
repositories without configuring an identity, relying on the developer's global
Git configuration. They now use the existing repository setup helper, which sets a
fixture-only identity. Both tests explicitly exclude global/system configuration
and clear inherited author/committer identity variables, so the regression is also
exercised on a configured Windows development machine. Owner Git configuration is
not changed.

The other two failures were Gantt/host-fixture integrations requiring Node, which
was absent from Ubuntu. A checksum-verified official Node 24.21.0 distribution is
unpacked into the disposable test workspace and added only to the test process's
PATH. Python dependencies use an isolated environment there. No system packages,
owner global tools or profiles are installed or replaced. The complete rerun passes
all four cases along with the rest of the suite.

## Verification and retained evidence

- Windows Python: 1056 passed; the one POSIX-only case is separately executed above.
- Ubuntu/WSL2 Python 3.12.3, Git 2.43.0, Node 24.21.0: 1057 passed, none skipped.
- Shared UI / VS Code / Electron unit suites: 257 / 49 / 10 passed.
- Both complete installed Windows artifact-host suites pass against the freshly
  installed wheel, including the missing-terminator probes.
- Ruff and formatting checks pass. The maintained Gantt history verifies its 22
  current nodes, 22 historical deletions, 123 actual CLI receipts and three stages.
- The current wheel/sdist are rebuilt and package inspection passes. VSIX and desktop
  runtime inputs are unchanged by this backend rule; their installed artifacts are
  exercised with the new isolated CLI. No owner installation is performed.
- Exact-index graph/source checks run for both the 230-node self-graph and 22-node
  tracked example before the authorized commit. Its tree must match that index.

Logs, original bytes, failed diagnostics, the isolated Linux workspace location,
JUnit results and artifact digests remain in `.specspec-local/final-newline/`.
Key files include `windows-mode-probe.json`, `windows-unskipped-diagnosis.log`,
`posix-mode-case.log`, `posix-python-first.log`, `posix-python-final.log`,
`posix-python-result.json`, `posix-python.xml`, `posix-environment.json`,
`posix-node.json` and both `*-artifact-host.log` files. Initial launcher/setup failures
are retained separately as well. No failures are reclassified as passing checks.
