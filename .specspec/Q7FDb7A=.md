---
id: Q7FDb7A=
type: requirement
parents:
- DFS2oJM=
---
# Pin the build dependencies and ship only allowlisted runtime files with complete license notices

One npm lockfile at the root records the registry address and the integrity hash of every dependency, and the private workspaces. The root manifest approves the install scripts of Electron, esbuild and the signature helper of the VSIX tool, each at a pinned version. The license notices name every bundled dependency with its version. They are derived from the input paths that esbuild actually read, so that hoisted, scoped and nested packages are all covered. A package contains the license of the project and the licenses of its dependencies, and its application files come from an allowlist of runtime files. The portable desktop runtime is an unpacked directory whose files can be inspected directly.

The root manifest pins the Electron runtime and overrides the versions of selected transitive dependencies: undici, and the MSAL library of the VSIX tool, which the local creation of the VSIX needs. Build dependencies are part of neither shipped editor. An audit finding is reported together with its scope, and an override is revisited when upstream publishes a compatible release.
