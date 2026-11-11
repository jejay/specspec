---
id: uY3KPsM=
type: requirement
parents:
- CmZafVM=
- GQdmCrA=
---
# Run the extension and the command line on the workspace host and rely on the connection of VS Code

The extension runs in Node and is declared a workspace extension, and its manifest states accurately that it needs a real file system. Execution and the saving of node files happen beside the workspace, while the graph is drawn and gestures are handled in the client. The VSIX and a matching specspec command line on Python 3.11 or newer are installed on the workspace host that executes, and the executable is configured in the settings of the remote machine. VS Code owns the authentication of SSH and tunnels, the routing of resources and the lifecycle of the connection. The bundled assets of the webview are addressed through `asWebviewUri`, and dynamic content travels as messages.

A file URI on the executing host names a resource of the file system of that host. VS Code normally maps remote URIs to file URIs inside that host. A virtual resource, and a resource of the client machine that is presented to a remote host, is rejected with a message that says what to do. Whether a document belongs to a project, and where the project is, is verified on that host. A failure of the place of execution, of a dependency or of trust is reported with a usable diagnostic. When a delivery fails, the recovery data and the original input are kept, and after a reconnect the current state is read before any further change. A destructive request is executed once and deliberately: an unknown outcome is reported for inspection and is never repeated automatically.

The setup for remote use is documented, and an opt-in path qualifies the installed extension on a remote host. The actual coverage of SSH, of a desktop client over a tunnel and of a browser client over a tunnel is reported for each separately, with the limitations of the environment. Browsing a virtual repository needs an execution of its own, which is left open here.
