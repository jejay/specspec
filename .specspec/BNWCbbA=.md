---
id: BNWCbbA=
type: implementation
parents:
- _LWxOi0=
sources:
- path: graph-ui-common/test/git-watch.test.cjs
- path: graph-ui-common/test/annotations.test.cjs
- path: graph-ui-common/test/watch.test.cjs
- path: vscode/test/extension.test.cjs
---
# Scripted hints, settled watches and awaited cleanup in the watcher tests

`scripted(hints)` in git-watch.test.cjs returns Node's `fs` with `watch` replaced by
an inert emitter that records each hint callback. The four discovery tests with
scripted Git replies pass it to `GitWatcher`. The coalescing test sends twenty `.git`
hints along with its twenty direct requests and expects one follow-up discovery. The
VS Code fixture in extension.test.cjs gives `GitWatcher` and `AnnotationWatcher` the
same kind of watch, and the external-spotlight test sends the `local` hint itself
after writing its shot.

The tests of real watching in annotations.test.cjs, watch.test.cjs and
git-watch.test.cjs call `started()`, a 200 ms wait, after a watch begins or
reattaches.

The VS Code fixture removes its project after real Git discovery has ended, using
`rm()` with retries. Windows reports a directory as busy while a Git process has it
as working directory, and Node 22's `rmSync()` passes that error on at once.
