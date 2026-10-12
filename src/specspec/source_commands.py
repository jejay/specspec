"""CLI source lifecycle. Canonical writes are explicit; previews/checks are read-only."""

import json

import click

from .git import git_snapshot
from .model import Diagnostic, SpecError
from .sources import BAD_OUTCOMES, SourceReader, check_results, resolve_nodes, text_lines
from .workspace import load_snapshot, require_node, update_node


def register(main, root_path, emit, guarded, json_option):
    @main.group(name="sources")
    def group():
        """Capture, resolve, check, view or deliberately reanchor implementation links."""

    def target_options(function):
        for decorator in [
            click.option("--ref", help="Immutable code/graph revision."),
            click.option("--staged", is_flag=True, help="Use exact staged bytes."),
            click.option(
                "--graph-ref", help="Override metadata revision; code target stays --ref/--staged."
            ),
        ]:
            function = decorator(function)
        return function

    def graph(root, ref, staged, graph_ref):
        if ref and staged:
            raise SpecError([Diagnostic("SOURCES", "Do not combine --ref and --staged.")], 2)
        return (
            git_snapshot(root, graph_ref)
            if graph_ref
            else git_snapshot(root, ref)
            if ref
            else git_snapshot(root, staged=True)
            if staged
            else load_snapshot(root)
        )

    def checked(operation):
        try:
            return operation()
        except (ValueError, UnicodeError) as error:
            raise SpecError([Diagnostic("SOURCES", str(error))]) from error

    def intervals(values):
        try:
            return [[int(n) for n in value.split(":")] for value in values]
        except ValueError as error:
            raise SpecError(
                [Diagnostic("SOURCES", "Use --range START:END with inclusive integer lines.")]
            ) from error

    for action in ["resolve", "check"]:

        def command(root, node_id, ref, staged, graph_ref, as_json, action=action):
            project = root_path(root)
            snapshot = graph(project, ref, staged, graph_ref)
            snapshot.require_valid()
            nodes = (
                [require_node(snapshot, node_id)]
                if node_id
                else [n for n in snapshot.nodes if not n.retired]
            )
            result = checked(
                lambda: resolve_nodes(
                    project, nodes, ref=ref, staged=staged, retention=action == "check"
                )
            )
            diagnostics = check_results(result) if action == "check" else []
            emit({"sources": result}, diagnostics, as_json=as_json, ok=not diagnostics)
            if diagnostics:
                raise click.exceptions.Exit(1)

        command.__name__ = "source_" + action
        command = guarded(command)
        command = click.pass_obj(command)
        command = json_option(command)
        command = target_options(command)
        command = click.argument("node_id", required=False)(command)
        group.command(name=action, context_settings={"ignore_unknown_options": True})(command)

    @group.command(name="capture", context_settings={"ignore_unknown_options": True})
    @click.argument("node_id")
    @click.argument("path")
    @click.option(
        "--range",
        "ranges",
        multiple=True,
        required=True,
        help="Inclusive START:END, repeat for separate regions.",
    )
    @click.option("--mode", type=click.Choice(["strict", "expanding"]), required=True)
    @click.option("--symbol")
    @click.option("--ref", help="Capture committed source; default HEAD.")
    @click.option("--staged", is_flag=True)
    @click.option(
        "--replace",
        "replace_number",
        type=click.IntRange(min=1),
        help="Replace a 1-based source number instead of appending.",
    )
    @click.option(
        "--preview", is_flag=True, help="Return metadata without changing a node/document."
    )
    @json_option
    @click.pass_obj
    @guarded
    def capture(
        root, node_id, path, ranges, mode, symbol, ref, staged, replace_number, preview, as_json
    ):
        project = root_path(root)
        node = require_node(load_snapshot(project), node_id)
        if node.type != "implementation" or node.retired:
            raise SpecError([Diagnostic("SOURCES", "Capture requires a live implementation node.")])
        source = checked(
            lambda: SourceReader(
                project, ref=ref or (None if staged else "HEAD"), staged=staged
            ).capture(path, intervals(ranges), mode, symbol)
        )
        values = node.semantic()["sources"]
        if replace_number:
            if replace_number > len(values):
                raise SpecError([Diagnostic("SOURCES", "Source number does not exist.")])
            values[replace_number - 1] = source
        else:
            values.append(source)
        if not preview:
            update_node(project, node_id, sources=values)
        emit({"reference": source, "sources": values, "written": not preview}, as_json=as_json)

    @group.command(name="reanchor", context_settings={"ignore_unknown_options": True})
    @click.argument("node_id")
    @click.option("--source", "number", type=click.IntRange(min=1), required=True)
    @click.option(
        "--range",
        "ranges",
        multiple=True,
        help="Explicit replacement ranges for conflicting/ambiguous content.",
    )
    @click.option("--ref", help="Committed target; default HEAD.")
    @click.option("--staged", is_flag=True)
    @click.option("--preview", is_flag=True)
    @json_option
    @click.pass_obj
    @guarded
    def reanchor(root, node_id, number, ranges, ref, staged, preview, as_json):
        project = root_path(root)
        node = require_node(load_snapshot(project), node_id)
        values = node.semantic()["sources"]
        if node.type != "implementation" or node.retired or number > len(values):
            raise SpecError(
                [Diagnostic("SOURCES", "Select a source on a live implementation node.")]
            )
        old = values[number - 1]
        if "blob" not in old:
            raise SpecError([Diagnostic("SOURCES", "Use capture for a whole-file reference.")])
        reader = checked(
            lambda: SourceReader(project, ref=ref or (None if staged else "HEAD"), staged=staged)
        )
        resolution = reader.resolve(old)
        if not ranges and resolution["outcome"] in BAD_OUTCOMES:
            raise SpecError(
                [
                    Diagnostic(
                        "SOURCES",
                        "Supply explicit --range replacements; this mapping is not trustworthy.",
                    )
                ]
            )
        source = checked(
            lambda: reader.capture(
                resolution["path"],
                intervals(ranges) if ranges else resolution["ranges"],
                old["mode"],
                old.get("symbol"),
            )
        )
        values[number - 1] = source
        if not preview:
            update_node(project, node_id, sources=values)
        emit({"reference": source, "sources": values, "written": not preview}, as_json=as_json)

    @group.command(name="view")
    @click.option(
        "--reference",
        required=True,
        help="One validated source object as JSON; supports unsaved document previews.",
    )
    @click.option("--ref")
    @click.option("--staged", is_flag=True)
    @json_option
    @click.pass_obj
    @guarded
    def view(root, reference, ref, staged, as_json):
        from .source_schema import validate_source

        try:
            source = json.loads(reference)
            validate_source(source)
        except (ValueError, TypeError) as error:
            raise SpecError([Diagnostic("SOURCES", str(error))]) from error
        reader = checked(lambda: SourceReader(root_path(root), ref=ref, staged=staged))
        resolution = reader.resolve(source)
        original = resolution["outcome"] in BAD_OUTCOMES and "blob" in source
        lines = checked(
            lambda: text_lines(
                reader.blob(source["blob"]) if original else reader.data(resolution["path"])
            )
        )
        spans = source.get("ranges", []) if original else resolution["ranges"]
        if not spans:
            spans = [[1, min(len(lines), 200)]] if lines else []
        chunks = []
        for start, end in spans:
            lo, hi = max(1, start - 3), min(len(lines), end + 3)
            chunks.append({"start": lo, "selected": [start, end], "lines": lines[lo - 1 : hi]})
        emit({"resolution": resolution, "original": original, "chunks": chunks}, as_json=as_json)
