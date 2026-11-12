---
id: x1WCLls=
type: implementation
parents:
- 49Qjg3U=
sources:
- path: .github/workflows/pipy_publish.yaml
- path: src/specspec/cli.py
- path: src/specspec/cli_help.py
- path: src/specspec/guide.py
- path: src/specspec/templates/earlier/0.0.1.md
- path: tests/test_guide_refresh.py
- path: tests/test_release.py
- path: tools/pypi_release.py
---
# Find and replace shipped guides in specspec guide

guide.place_guide searches AGENTS.md for the packaged guide and for each file in templates/earlier, both in LF and in CRLF form, and replaces an earlier guide once, in the line endings it was found in. A file whose lines include the first line of a shipped guide, compared without case, but none of the exact texts counts as edited. refresh_guide writes through an fsynced temporary file and os.replace after checking that AGENTS.md did not change meanwhile. specspec guide reports created, appended, replaced or current with the release version, fails with a GUIDE diagnostic for an edited guide, and --print writes the packaged guide bytes.

templates/earlier/0.0.1.md holds the guide of the 0.0.1 wheel on PyPI. tools/pypi_release.py guides downloads the wheel of the newest release on PyPI, checks it against its published digest and fails when its guide is neither the current one nor carried; the build job of pipy_publish.yaml runs it. Tests cover replacement between owner text, CRLF files, a hand-edited guide, creation, appending, --print, every carried guide and the release check.
