"""CLI source lifecycle. Canonical writes are explicit; previews/checks are read-only."""

import click

from .git import git_snapshot
from .model import Diagnostic, SpecError
from .source_schema import validate_source
from .sources import BAD_OUTCOMES, SourceReader, resolve_nodes, text_lines
from .workspace import load_snapshot, require_node, update_node


def checked(operation):
    try:
        return operation()
    except (ValueError, TypeError, UnicodeError) as error:
        raise SpecError([Diagnostic("SOURCES", str(error))]) from error


def intervals(values):
    if not isinstance(values, (list, tuple)) or any(not isinstance(v, str) for v in values):
        raise SpecError([Diagnostic("SOURCES", "Ranges must be START:END strings.")], 2)
    try:
        return [[int(n) for n in value.split(":")] for value in values]
    except ValueError as error:
        raise SpecError([Diagnostic("SOURCES", "Use inclusive --range START:END.")], 2) from error


def target_graph(root, ref=None, staged=False, graph_ref=None):
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


def preview_source(root, source, *, ref=None, staged=False):
    if type(staged) is not bool or (ref is not None and (not isinstance(ref, str) or not ref)):
        raise SpecError([Diagnostic("SOURCES", "Invalid source target.")], 2)
    checked(lambda: validate_source(source))
    reader = checked(lambda: SourceReader(root, ref=ref, staged=staged))
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
    return {"resolution": resolution, "original": original, "chunks": chunks}


def capture_source(
    root,
    node_id,
    path,
    ranges,
    mode,
    *,
    symbol=None,
    ref=None,
    staged=False,
    replace_number=None,
    dry_run=False,
):
    if type(staged) is not bool or (ref and staged):
        raise SpecError([Diagnostic("SOURCES", "Select committed ref or staged bytes.")], 2)
    node = require_node(load_snapshot(root), node_id)
    if node.type != "implementation":
        raise SpecError([Diagnostic("SOURCES", "Capture requires a live implementation node.")])
    source = checked(
        lambda: SourceReader(root, ref=ref or (None if staged else "HEAD"), staged=staged).capture(
            path, intervals(ranges), mode, symbol
        )
    )
    values = node.semantic()["sources"]
    if replace_number:
        if replace_number > len(values):
            raise SpecError([Diagnostic("SOURCES", "Source number does not exist.")])
        values[replace_number - 1] = source
    else:
        values.append(source)
    if not dry_run:
        update_node(root, node_id, sources=values)
    return {"reference": source, "sources": values, "written": not dry_run}


def register(main, root_path, emit, guarded, json_option):
    from .output import render_sources

    @main.group(name="sources")
    def group():
        """Advanced: inspect, capture and deliberately reanchor source regions."""

    def target_options(function):
        for decorator in [
            click.option("--ref", help="Code revision; also graph revision unless overridden."),
            click.option("--staged", is_flag=True),
            click.option("--graph-ref", hidden=True),
        ]:
            function = decorator(function)
        return function

    @group.command(name="show", context_settings={"ignore_unknown_options": True})
    @click.argument("node_id", required=False)
    @click.option(
        "--source",
        "number",
        type=click.IntRange(min=1),
        help="Preview this 1-based source on the selected node.",
    )
    @target_options
    @json_option
    @click.pass_obj
    @guarded
    def show(root, node_id, number, ref, staged, graph_ref, as_json):
        project = root_path(root)
        snapshot = target_graph(project, ref, staged, graph_ref)
        nodes = [require_node(snapshot, node_id)] if node_id else snapshot.nodes
        if number:
            if not node_id or number > len(nodes[0].sources):
                raise SpecError(
                    [Diagnostic("SOURCES", "Select an existing source with NODE_ID --source N.")], 2
                )
            result = preview_source(project, nodes[0].sources[number - 1], ref=ref, staged=staged)
        else:
            result = {
                "sources": checked(lambda: resolve_nodes(project, nodes, ref=ref, staged=staged))
            }
        emit(result, as_json=as_json, text=render_sources)

    @group.command(name="capture", context_settings={"ignore_unknown_options": True})
    @click.argument("node_id")
    @click.argument("path")
    @click.option(
        "--range",
        "ranges",
        multiple=True,
        required=True,
        help="Inclusive START:END; repeat for separate regions.",
    )
    @click.option("--mode", type=click.Choice(["strict", "expanding"]), required=True)
    @click.option("--symbol", hidden=True)
    @click.option("--ref", help="Committed source; default HEAD.")
    @click.option("--staged", is_flag=True)
    @click.option("--replace", "replace_number", type=click.IntRange(min=1), hidden=True)
    @click.option("--dry-run", is_flag=True, help="Preview metadata without writing the node.")
    @json_option
    @click.pass_obj
    @guarded
    def capture(
        root, node_id, path, ranges, mode, symbol, ref, staged, replace_number, dry_run, as_json
    ):
        result = capture_source(
            root_path(root),
            node_id,
            path,
            ranges,
            mode,
            symbol=symbol,
            ref=ref,
            staged=staged,
            replace_number=replace_number,
            dry_run=dry_run,
        )
        emit(result, as_json=as_json, text=render_sources)

    @group.command(name="reanchor", context_settings={"ignore_unknown_options": True})
    @click.argument("node_id")
    @click.option("--source", "number", type=click.IntRange(min=1), required=True)
    @click.option(
        "--range",
        "ranges",
        multiple=True,
        help="Explicit replacement ranges for uncertain mappings.",
    )
    @click.option("--ref", help="Committed target; default HEAD.")
    @click.option("--staged", is_flag=True)
    @click.option("--dry-run", is_flag=True)
    @json_option
    @click.pass_obj
    @guarded
    def reanchor(root, node_id, number, ranges, ref, staged, dry_run, as_json):
        project = root_path(root)
        node = require_node(load_snapshot(project), node_id)
        values = node.semantic()["sources"]
        if node.type != "implementation" or number > len(values):
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
        if not dry_run:
            update_node(project, node_id, sources=values)
        emit(
            {"reference": source, "sources": values, "written": not dry_run},
            as_json=as_json,
            text=render_sources,
        )
