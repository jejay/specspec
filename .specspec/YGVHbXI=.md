---
id: YGVHbXI=
type: requirement
parents:
- qY3YIpQ=
---
# Attach the editor packages to the GitHub release of each version

Pushing the tag vX.Y.Z builds the VSIX and the portable desktop archives for Windows x64 and Linux x64 from that tag, after the same checks as CI. The tag matches the version in all package metadata and points to a commit on main. The GitHub release for the tag carries the VSIX, both desktop archives and a SHA256SUMS file, and its notes are the version's CHANGELOG section. The desktop archives are unsigned.

The README and the editor guide link the release downloads and keep building from source as the alternative.
