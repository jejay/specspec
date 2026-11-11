---
id: xakKaOA=
type: requirement
parents:
- eZq6RCw=
- PL1IogE=
---
# Show one blocking startup screen in both graph editors that checks the command line and offers initialization

Both graph editors show the same startup screen, and the actions on a graph are unavailable while it is up. An editor probes the configured command line before it reads a graph, and the desktop app does so before a project is chosen. The probe starts the command line without a shell, with a deadline and a limit on its output, on the host where the workspace lives. When the executable or the Python module is missing, the screen shows a prominent installation message with a Retry button. A protocol that does not match and every other failure appear with their own accurate diagnostic. A project counts as having no graph only when its directory shows that, and a read that fails for another reason is reported as an error.

The trusted part of the editor, which has access to the file system, looks at the actual entries of the selected directory. When `.specspec` is absent, or is a real directory that is empty or holds nothing but `local`, the screen offers a centered form for the manifesto with the button Initialize specspec. The action is explicit, runs one at a time, applies to the selected project alone and requires that the project is trusted. It calls `init` with the manifesto on standard input and loads the graph only after `init` has succeeded. The backend protects the action as it protects every write: against a graph that appears at the same moment, against unsaved documents, against an interrupted transaction and against unsafe paths. Choosing a project, Retry and the error messages are usable throughout, and the controls that change a graph are disabled as long as no current graph is shown.
