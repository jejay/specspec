---
id: 3SfTeOo=
type: requirement
parents:
- YOPhqYc=
---
# Run the desktop app in an isolated Electron window that works on authorized local projects

The standalone app for Linux and Windows is built with Electron. Its renderer is sandboxed and context-isolated, runs with `nodeIntegration` disabled and reaches the main process through one fixed preload interface for messages and view state. The main process authorizes each local project that the owner selects, takes the command-line executable from the trusted launch configuration alone, validates the sender and the content of every IPC message and passes graph operations on to the shared session and the Python tool, which are the authority for them. Navigation, new windows, requests and permissions are confined to the local application.

The app asks through the system's own dialogs before it opens a project, before a destructive action and before it overwrites a node that changed. The input of revisions is limited in length. Presentation state and drafts are stored per project, and a stored file with corrupt bytes is protected from being overwritten. The app checks the current authorization and the current files again before it acts, and it shows errors of launching, of the command-line process and of rendering.

A path to the executable that comes from the trusted launch options or the environment is resolved once, against the directory the app was launched from. An absolute path keeps its meaning, and a bare name is looked up on PATH. Project operations work on the selected project. Python and Git are prerequisites that are installed apart from the app; the delivery targets are a portable desktop app and local host integration.
