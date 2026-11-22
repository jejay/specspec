---
id: _EoFFPs=
type: implementation
parents:
- aJeGE5M=
sources:
- path: .github/workflows/release-build.yml
- path: CONTRIBUTING.md
- path: README.md
- path: tests/test_release_workflow.py
- path: tools/release.py
- path: vscode/README.md
---
# Build the editor packages on version tags and attach them to the release

release-build.yml runs on manual dispatch and on tags v*.*.*. Its Windows and Linux jobs read the version with tools.release.version, which needs only the standard library, and for a tag check, before installing anything, that the tag is v plus that version, that the tagged commit is an ancestor of origin/main, that CHANGELOG.md has a section for the version and that https://pypi.org/pypi/specspec/VERSION/json answers; otherwise the job fails with an error that says to run Publish CLI to PyPI first. They then install the dependencies and run the graph checks, the history verification, lint, pytest, npm test and npm audit, and upload the output of npm run package:all.

The github-release job, the only one with contents: write, takes the VSIX from the Linux job, the win32-x64 zip from the Windows job and the linux-x64 tar.gz from the Linux job, writes SHA256SUMS and runs gh release create --verify-tag with the title specspec VERSION and the output of tools/release.py notes VERSION as notes. The README, the editor guide and the release procedure in CONTRIBUTING describe the downloads and the tag step.
