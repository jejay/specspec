---
id: Q7FDb7A=
type: requirement
parents:
- DFS2oJM=
---
# Keep local release dependencies pinned and qualification scoped

One root npm lock records registry addresses/integrity and private workspaces.
Pinned root script approvals cover Electron, esbuild and the VSIX signature helper.
Actual esbuild input paths determine every bundled dependency/version license notice,
including hoisted/scoped/nested packages. Packaging retains project and upstream
licenses and allowlists application runtime files; the portable runtime remains
unpacked and directly inspectable.

The root manifest pins the Electron runtime and overrides selected transitive
versions: undici, and the VSIX tool's MSAL dependency for local VSIX creation.
Build dependencies stay out of both shipped UI runtimes. Audit findings are
reported with their scope, and overrides follow compatible upstream releases.
