# VS Code remote workspaces

specspec is a **workspace extension**: its Node adapter, Python CLI and Git execute
where the real repository filesystem lives. The graph/webview renders in your
VS Code desktop or connected browser. VS Code owns authentication, SSH/tunnel
transport, resource routing and reconnection. specspec requires no extra web server,
exposed port, credential store or remote shell wrapper.

## Setup

1. Connect with Remote SSH or Remote Tunnels and open the remote project folder.
2. Install the specspec VSIX **in that connected window**, on the workspace host.
   Use Developer: Show Running Extensions to check placement. A local-only install
   is not a substitute for the remote installation. This application is not yet a
   published Marketplace/PyPI release.
3. Install Python 3.11+, the matching application protocol specspec application and Git on that host.
   Use an isolated installation from your authorized checkout/Git URL. Confirm the
   CLI works from the remote terminal before opening a graph.
4. Trust that workspace if appropriate. Use Remote Settings for the executable:

```json
{
  "specspec.command": "/home/me/.venvs/specspec/bin/python",
  "specspec.args": ["-m", "specspec"]
}
```

The remote server's PATH can differ from an interactive terminal's PATH. Use an
absolute path; keep personal executable paths out of shared project policy.
`SPECSPEC_PYTHON` is a development launch override, not production configuration.

Node-file editors retain native Save/autosave/undo/recovery. Python plans their
edits; project actions retain the managed writer. Git/status/source previews use
the remote repository, index and locally available objects. Staging remains distinct
from committing. Native dirty descendant tabs still block managed deletion.

## Resource and connection boundaries

VS Code normally translates client `vscode-remote:` resources to `file:` resources
inside the remote Node host. specspec accepts that executing host's real files;
client-local resources presented there and virtual repository providers receive
an actionable filesystem error. Plain `github.dev`/disconnected `vscode.dev` lacks
the required Python execution environment. Browser clients connected to a real
VS Code Server through a tunnel have a different, suitable execution architecture.

Webview assets use VS Code resource routing and strict CSP. Input is literal data.
Cameras stay client-side; reads/plans/saves incur backend and transport latency.
See [loading and diagnostics](loading.md).

If the connection or a command reply is lost, retain drafts and inspect the current
remote files and recovery state before retrying an action. A missing reply is not
proof that a mutation failed. specspec does not automatically replay destructive
commands. Reconnect/Refresh performs current reads. Native recovery and managed
journal recovery remain separate; see [native persistence](native-editors.md).

## Qualification

The manifest and adapter target real Remote SSH/Tunnel workspaces. Local adapter
checks are not a transport qualification. Record actual desktop SSH, desktop tunnel
and browser tunnel runs separately, including version/platform and connection loss.

`vscode/test-host/remote.cjs` is an opt-in `--extensionTestsPath` module executed in
an actual remote extension host. Use a **disposable external clone** of the maintained
Gantt bundle, never a development worktree or an existing experiment. Give that
clone a `.specspec-remote-smoke.json` containing the host's absolute `python` path
and expected `remoteName` (`ssh-remote`, `tunnel`, or `wsl`, as applicable). Configure
specspec in that clone's settings and launch the installed/development extension
with the remote folder and test module through VS Code. It verifies actual execution
placement, working graph rendering, native dirty/save/Unicode overlays and an anchored
source preview, and writes `.specspec-remote-result.json` in the disposable clone.
It performs a temporary node-body edit and restores it after the successful checks.
It does not install services, credentials or Git hooks.

This smoke path is narrower than the full shared/native/deletion local-host suite.
An interrupted smoke may leave its disposable edit for inspection. SSH/tunnel
credentials and an accessible host must be supplied by the operator; transport
coverage must be stated from actual results rather than inferred from WSL or local
Windows passes.

### Current dispatched evidence

The preceding API-5 build's Windows VS Code 1.141.1 desktop client connected to a
real Linux WSL workspace host passed this smoke: 22-node completed graph render (3.09 seconds in that run),
native dirty/save/Unicode overlays and an anchored source-object preview. The test
used a new persistent-home Gantt clone and an isolated client profile. It is narrower
than the complete local Windows host regressions and is not SSH/tunnel qualification.

Earlier attempts are retained in diagnostics: missing temporary fixture, failed
background launches, and remote asset HTTP 401/ready timeouts. A fresh foreground
launch with normalized `wsl+ubuntu` authority passed; profile/launch differences mean
this is not proof of a single cause. Keep connection authority/resource routing
consistent and inspect webview resource errors rather than loosening CSP or resource
roots. application protocol remote sessions and SSH/desktop/browser tunnel runs still require fresh
qualification with operator-supplied endpoints and authentication. The current application protocol
Windows installed-host regression uses an isolated portable VS Code Insiders build;
it does not prove any remote transport. No server service, SSH keys or global Python packages were installed.

Background rationale: [remote investigation](investigations/vscode-remote-development.md).
