---
id: YOPhqYc=
type: requirement
parents:
- PL1IogE=
---
# Build both graph editors from one shared renderer and session behind small adapters

The directory `graph-ui-common` holds what both graph editors share: the rendering of cards as DOM elements and of links as SVG, the pure functions for layout and metrics, the camera, the HTML and CSS, the invocation of the command line within limits of time and output, the discovery of the project and a session that checks every request and handles one operation after another. Each editor adds an adapter that supplies the exchange of messages and the stored view state, the trusted configuration of the executable, the selection of a project, confirmations, the input of revisions, file watchers, themes and the addresses of assets. Both editors are built from this common source into self-contained outputs, which include libraries of pinned versions that work offline and their license notices.

State is kept per project and per view. The views of one project share the text of the open documents, and each view has its own focus, cameras, comparison and recovery of form input that is not applied yet. The renderer acknowledges every snapshot with its token and the complete list of the nodes it shows, and the session checks both. An adapter may connect the open documents of its editor: their text is laid over the files for reading, and the Python planner plans every edit to them without writing. Without that connection, as in a graph panel and in the desktop app, a save goes through the Python writer. An adapter for the transport of a coding agent can use the same interface.
