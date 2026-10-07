---
id: 449d5e44-2d5f-4c30-b4f3-9207b21b6286
type: requirement
parents:
- 65f28474-18be-46f8-89f6-b9ce30a0ec96
- 003d697b-4104-4fdf-8e05-0db572c436d0
managed_hash: a73175287001f052c2f2fe5f4ece036a69772a4eb3690e5f02d6b6e7be5cbcac
---
# Start with a sandboxed Electron shell and explicit project authorization

Use Electron for a first Linux/Windows standalone shell. A sandboxed, context-isolated renderer with nodeIntegration disabled gets a fixed preload messaging/state API, never filesystem/spawn/credential access. The main process chooses/authorizes a local project explicitly, fixes the CLI executable from trusted launch configuration, validates IPC sender/allowed messages, denies remote requests/navigation/popups and delegates all graph writes to the guarded Python API. Native confirmations cover withdrawal/migration; revision input is bounded text. Persist presentation/drafts outside canonical data, scoped by project. Recheck authorization/stale fingerprints and report process/render errors. No installer, signing, update service, bundled Python, credential integration or production security certification is claimed in this first slice.

Origin: the user's cross-platform/sidebar/branding request in this conversation. Technical choices remain revisable.
