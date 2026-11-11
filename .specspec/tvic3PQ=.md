---
id: tvic3PQ=
type: requirement
parents:
- Bnr6yZY=
- YOPhqYc=
---
# Reload on file and Git notifications and keep drafts through every reload

A watcher event is a hint to reload. The session coalesces events, runs reads and writes one after another, retries a transient failure of a read a limited number of times and compares the loaded records directly, so that an unchanged graph is left as it is drawn. VS Code uses its filesystem watchers. The desktop app watches the project directory and the `.specspec` directory in it and attaches again after the directory is recreated. Errors of a watcher are reported. Refresh reloads on request, and polling at a configurable interval is an optional addition: its default is 0, which means off, and it is disposed when the project is switched and when the view closes.

A form without unsaved changes is refreshed. A form with unsaved changes keeps its original record, its text, its text cursor and its camera; changes to other nodes refresh the context around it, and the draft stays savable. A change to the same node requires a confirmation before the draft overwrites it. The draft of a deleted node stays copyable and cannot be saved. A reload that finds a graph breaking a rule shows the actual current relationships and diagnostics and permits the local edits that are safe. A file that cannot be read stays reachable as raw Markdown for repair. A load that is unavailable keeps the last graph that loaded, clearly marked, and enables no write that rests on that old state. A comparison between commits keeps its selected revisions. The renderer acknowledges each rendering with its sequence token and the full list of visible nodes. Watchers depend on the file system and give hints alone; the writer's check of file bytes is a separate safeguard for saving.
