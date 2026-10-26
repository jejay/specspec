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

Electron uses patched 44.9.3; overrides select undici 7.30.1 and build-tool MSAL
7.1.1. The MSAL major override serves tested local VSIX creation; Azure login and
Marketplace publication are outside this local release qualification. Those build
dependencies enter neither shipped UI runtime. Report current audit findings as
bounded observations and revisit the override with compatible upstream updates.
