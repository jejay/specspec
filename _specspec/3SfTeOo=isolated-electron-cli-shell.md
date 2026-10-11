---
id: 3SfTeOo=
type: requirement
parents:
- YOPhqYc=
- ME4UXTA=
---
# Start with a sandboxed Electron shell and explicit project authorization

Use Electron for a first Linux/Windows standalone shell. A sandboxed, context-isolated renderer with nodeIntegration disabled gets a fixed preload messaging/state API, never filesystem/spawn/credential access. The main process chooses/authorizes a local project explicitly, fixes the CLI executable from trusted launch configuration, validates IPC sender/allowed messages, denies remote requests/navigation/popups and delegates all graph writes to the guarded Python API. Native confirmations cover withdrawal/migration; revision input is bounded text. Persist presentation/drafts outside canonical data, scoped by project. Recheck authorization and current files; retain drafts and confirm same-node overwrite conflicts and report process/render errors. No installer, signing, update service, bundled Python, credential integration or production security certification is claimed in this first slice.

Origin: the user's cross-platform/sidebar/branding request in this conversation. Technical choices remain revisable.


Resolve explicit executable paths from trusted launch options/environment against the Electron launch directory before the CLI subprocess changes cwd to a selected project. Project selection must not rebase an interpreter or CLI path. Preserve bare executable names for PATH lookup. This corrects the user-reported relative-interpreter ENOENT and implements the launch-directory semantics already documented, without moving executable configuration into project/renderer data.
