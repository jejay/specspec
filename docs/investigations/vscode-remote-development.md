# Investigation: SpecSpec over VS Code Remote SSH and Remote Tunnels

## Scope and evidence

This report preserves the remote-development assessment so it survives conversation
compaction. It is descriptive investigation, not a new binding feature contract or
an implementation-completion claim. Repository baseline: `829a306`. No actual Remote
SSH or Remote Tunnels session has been tested in this investigation. Existing local
Windows host tests and CI configuration do not establish remote compatibility.

The owner asks about using SpecSpec through VS Code's remote execution extensions,
including SSH and tunneling. Distinguish these environments:

| Environment | Assessment |
| --- | --- |
| VS Code desktop connected through Remote SSH | Strong architectural fit; may already work with the extension installed remotely; needs an actual session test. |
| VS Code desktop connected through Remote Tunnels | Same workspace-host architecture; needs separate connection/recovery qualification. |
| Browser VS Code connected through a tunnel to VS Code Server | Plausible without a browser-only backend rewrite: the Node extension host runs on the server, the webview in the browser. Test asset/CSP delivery, editor APIs and reconnection. |
| Plain `github.dev`, disconnected `vscode.dev`, virtual Remote Repositories | Different scope: no usable remote Python process/filesystem is supplied merely by opening a virtual repository. Current backend requires a real filesystem and execution environment. |
| Local extension using SSHFS/mounted remote files | Not the recommended architecture. Repeated filesystem/Git operations cross the mount; watcher delivery and transaction behavior depend on that filesystem. |

## Intended execution placement

```text
Client desktop/browser
  graph DOM/SVG, forms, camera, hover, local presentation
                    |
       VS Code webview messages and asset routing
       over VS Code's authenticated SSH/tunnel connection
                    |
Remote VS Code workspace extension host
  SpecSpec adapter, document coordination, notifications
                    |
           shell-free subprocess / UTF-8 JSON
                    |
Remote Python CLI + Git + repository + .specspec-local
```

Run SpecSpec's extension, Python and Git beside the remote repository. VS Code owns
SSH/tunnel authentication, transport and server lifecycle. SpecSpec does not need
its own HTTP server, exposed service port, SSH subprocess wrapper or file-sync layer.
The webview does not directly execute Python or read remote files.

Rendering is not remote pixel streaming. Pan/zoom/hover stay on the client; backend
reads, native edit planning, mutations, comparisons and source previews incur
backend work and message latency. Large full snapshots and open-document overlays
also consume bandwidth. Responsive camera movement does not establish fast loading
or low-latency edit acknowledgement.

## Existing code that helps

- `vscode/package.json` supplies a Node `main` entry point. VS Code normally infers
  a workspace extension for this shape; explicit `extensionKind` is currently absent.
- `vscode/src/extension.ts` invokes Python from `root.fsPath`, uses VS Code native
  TextDocuments/WorkspaceEdit/Save, watches canonical files through VS Code and Git
  metadata through the shared watcher, and checks workspace trust.
- Webview resources use `context.extensionUri`, `Uri.joinPath`, `asWebviewUri` and
  `webview.cspSource`. Dynamic content uses webview message passing. These are the
  patterns recommended by Microsoft's remote-extension guidance.
- `graph-ui-common/host/cli.cjs` uses bounded shell-free child processes with the
  project as cwd. Running it in the remote Node host puts execution on the right side.
- `graph-ui-common/host/documents.cjs` and `session.cjs` retain the existing native
  versus managed persistence owners, sequencing, dirty-document protections and
  reviewed deletion plans. Remote execution should preserve these contracts.
- Presentation/recovery uses VS Code webview state and workspaceState rather than
  a hardcoded client-side VS Code storage directory.
- Python is external, not a platform-specific bundled runtime. `pyproject.toml`
  requires Python 3.11+. The extension expects CLI API 5. Git features require Git
  and the anchor objects/history to be available on that remote host.

## URI nuance: a file-only check is not proof that SSH is blocked

`GraphEditors.project` and `GraphProject.documentPath` currently accept only `file:`
URIs. The adapter test explicitly rejects a supplied `vscode-remote:` project URI.
That test does not reproduce a real remote workspace extension host.

VS Code's remote URI transformation normally represents a client-side
`vscode-remote:` resource as a remote-host `file:` URI. Conversely, a client-local
`file:` resource becomes `vscode-local:` on the remote side. Consequently Node fs,
`fsPath`, `Uri.file` and the current file guard can be appropriate **when the
extension actually runs beside the workspace**. A client-local UI extension cannot
use those same filesystem paths to reach the remote repository.

Do not blindly allow every remote/virtual URI or strip an authority into a path.
First observe actual URI schemes and execution placement in installed sessions.
Verify discovery, native document membership/overlays, configuration lookup, node
navigation, assets and watchers. Retain actionable rejection for resources outside
the executing host's filesystem.

This transformation was checked against current upstream VS Code implementation;
that is explanatory evidence, not a guarantee for every VS Code version/provider.

## Small proposed hardening and deployment slice

1. Declare `"extensionKind": ["workspace"]` in the extension manifest. This states
   the hard requirement rather than depending solely on inference or user overrides.
2. Declare virtual-workspace support accurately, likely unsupported for this slice.
   A real remote disk workspace and a virtual repository are different capabilities.
3. Package/install the VSIX into the **connected remote window**, not only locally.
   Confirm placement with **Developer: Show Running Extensions**. The package is not
   yet a published release; remote installation must not assume Marketplace availability.
4. Install the matching Python application remotely, using its checkout or an
   authorized Git/package installation. Configure an absolute remote executable if
   the server's PATH differs from the interactive terminal's PATH. Production does
   not use the development-only `SPECSPEC_PYTHON` override.
5. Document remote setup, dependency/version errors and the supported client/host
   matrix. Check current Git capability requirements rather than assuming every old
   system Git supports all source/metadata operations.

Example **Remote Settings**, with the Python package installed in that environment:

```json
{
  "specspec.command": "/home/me/.venvs/specspec/bin/python",
  "specspec.args": ["-m", "specspec"]
}
```

Do not commit a personal client/remote executable path as shared project policy.
No node-schema change, history conversion or renderer fork is implied by this slice.

## Qualification checklist

Start with an installed VSIX, a Windows client and Linux SSH host, using a fresh
external checkout of the maintained current-schema Gantt history. Broaden the matrix
explicitly rather than treating the first successful connection as universal proof.

- Verify the extension and Python/Git processes really run remotely.
- Open Graph, nearest-project discovery, multi-root selection and canonical native
  custom editors; raw Markdown and neighbor-file navigation.
- Native dirty state, form/raw edits, Save/autosave/undo/redo, split synchronization,
  independent cameras, Unicode/CRLF and repairable invalid buffers.
- Source previews/capture and actual Git object availability/retention.
- Manual/agent edits on the server, canonical directory replacement and HEAD/index/
  ref notifications; keep polling default-off and explicit Refresh available.
- Full/shared cascade preview, uncommitted warnings, dirty descendant protection,
  locked reviewed-plan rechecking and HEAD ghosts through staging/commit.
- Slow links, reduced bandwidth, large overlays and render acknowledgements.
- Disconnect while editing, planning, saving and deleting; reconnect with retained
  drafts and fresh remote state. A lost reply does not establish that a mutation
  failed. Do not automatically replay a destructive command. Managed recovery and
  native document recovery keep their separate owners and safety limits.
- Desktop tunnel client and browser tunnel client: asset routing/CSP, native
  gestures, editor lifecycle, browser reload and extension-host restart.

Current readiness: **good architectural fit, unqualified remote deployment**.
Expect targeted deployment/adapter hardening and integration work, not a new server
architecture. Any latency or recovery changes need their own measured justification.

## References

- [Microsoft: supporting Remote Development and Codespaces](https://code.visualstudio.com/api/advanced-topics/remote-extensions)
- [Microsoft: extension-host placement](https://code.visualstudio.com/api/advanced-topics/extension-host)
- [Microsoft: Remote SSH](https://code.visualstudio.com/docs/remote/ssh)
- [Microsoft: Remote Tunnels](https://code.visualstudio.com/docs/remote/tunnels)
- [VS Code URI transformer](https://github.com/microsoft/vscode/blob/main/src/vs/base/common/uriTransformer.ts)
- [VS Code manifest-kind inference](https://github.com/microsoft/vscode/blob/main/src/vs/workbench/services/extensions/common/extensionManifestPropertiesService.ts)
- [Current native persistence semantics](../native-editors.md)
- [Current specification tour](../own-spec.md)
