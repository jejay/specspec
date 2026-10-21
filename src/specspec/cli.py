"""One compact CLI for people and agents; a bounded internal application adapter."""

from __future__ import annotations

import json
import sys
from functools import wraps
from pathlib import Path
from typing import Any

import click

from . import __version__, wire
from .annotation_commands import register as register_annotations
from .application import compare
from .application import request as application_request
from .deletion import deletion_plan, deletion_warnings
from .editor import MAX_REQUEST_BYTES
from .model import MAX_FILE_BYTES, Diagnostic, SpecError
from .output import (
    envelope,
    json_text,
    render_context,
    render_diff,
    render_listing,
    render_node,
    render_plan,
    render_receipt,
    safe_text,
)
from .query import read_query, render_query
from .source_commands import register as register_sources
from .source_commands import target_graph
from .source_schema import MAX_REFERENCES, validate_source
from .workspace import (
    Snapshot,
    add_node,
    delete_nodes,
    discover_root,
    initialize,
    load_snapshot,
    recover,
    require_node,
    slugify,
    update_node,
)


def emit(result: Any, diagnostics=None, *, as_json=False, ok=True, text=None):
    diagnostics = diagnostics or []
    if as_json:
        click.echo(json_text(envelope(result, diagnostics, ok)).encode("utf8"))
        return
    if result is not None:
        value = (
            text(result)
            if text
            else result
            if isinstance(result, str)
            else "\n".join(f"{key}: {json_text(val)}" for key, val in result.items())
        )
        click.echo(safe_text(value).encode("utf8"))
    for d in diagnostics:
        location = f" ({d.path})" if d.path else ""
        click.echo(
            safe_text(f"{d.severity}: {d.code}{location}: {d.message}").encode("utf8"), err=True
        )


def guarded(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        as_json = kwargs.get("as_json", False) or function.__name__ == "api"
        try:
            return function(*args, **kwargs)
        except SpecError as error:
            emit(None, error.diagnostics, as_json=as_json, ok=False)
            raise click.exceptions.Exit(error.exit_code) from error
        except (OSError, UnicodeError) as error:
            emit(None, [Diagnostic("IO", str(error))], as_json=as_json, ok=False)
            raise click.exceptions.Exit(2) from error

    return wrapper


json_option = click.option(
    "--json", "as_json", is_flag=True, help="Emit compact versioned JSON instead of readable text."
)


class Commands(click.Group):
    def format_commands(self, ctx, formatter):
        for label, names in [
            (
                "Everyday commands",
                ["init", "show", "context", "query", "add", "update", "delete", "check", "diff"],
            ),
            ("Advanced tools", ["sources", "spotlight", "recover"]),
        ]:
            with formatter.section(label):
                formatter.write_dl(
                    [(name, self.get_command(ctx, name).get_short_help_str()) for name in names]
                )


def root_path(explicit):
    return explicit.absolute() if explicit is not None else discover_root()


def read_body(path):
    if path == "-":
        raw = sys.stdin.buffer.read(MAX_FILE_BYTES + 1)
    else:
        with Path(path).open("rb") as stream:
            raw = stream.read(MAX_FILE_BYTES + 1)
    if len(raw) > MAX_FILE_BYTES:
        raise SpecError([Diagnostic("FORMAT", "Body exceeds the 1 MiB node limit.")], 2)
    return raw.decode("utf8")


def source_input(value):
    if value is None:
        return None
    try:
        sources = json.loads(value)
        if not isinstance(sources, list) or len(sources) > MAX_REFERENCES:
            raise ValueError("Expected a bounded source array.")
        for source in sources:
            validate_source(source)
        return sources
    except (ValueError, TypeError) as error:
        raise SpecError([Diagnostic("SOURCES", f"Invalid sources JSON: {error}")]) from error


def mutation_output(snapshot: Snapshot, ids, as_json):
    graph = snapshot.require_valid()
    affected = set().union(*(graph.closure(i) for i in ids)) if ids else set()
    emit(
        {
            "changed_ids": ids,
            "nodes": [{"id": i, "path": graph.nodes[i].path} for i in ids],
            "affected": sorted(affected),
        },
        snapshot.diagnostics,
        as_json=as_json,
        text=render_receipt,
    )


def summary_slug(body):
    heading = next((s.lstrip("# ").strip() for s in body.splitlines() if s.startswith("#")), "node")
    try:
        return slugify(heading)
    except SpecError:
        return "node"


@click.group(cls=Commands)
@click.option(
    "--root", type=click.Path(path_type=Path, file_okay=False), help="Explicit project root."
)
@click.version_option(__version__)
@click.pass_context
def main(context, root):
    """Manage an intention-conclusion specification graph."""
    context.obj = root


@main.command()
@click.argument("manifesto")
@click.option("--slug", hidden=True)
@json_option
@click.pass_obj
@guarded
def init(root, manifesto, slug, as_json):
    """Create a graph from manifesto body FILE (or - for stdin)."""
    body = read_body(manifesto)
    snapshot = initialize(
        root.absolute() if root is not None else Path.cwd(), body, slug or summary_slug(body)
    )
    mutation_output(snapshot, [snapshot.nodes[0].id], as_json)


@main.command(name="add")
@click.option(
    "--type",
    "node_type",
    type=click.Choice(["requirement", "implementation"]),
    default="requirement",
    show_default=True,
)
@click.option(
    "--parent",
    "parents",
    multiple=True,
    required=True,
    help="Full parent ID; repeat for multiple parents.",
)
@click.option("--slug", hidden=True)
@click.option("--body", required=True, help="Body FILE, or - for stdin.")
@click.option("--sources", hidden=True)
@json_option
@click.pass_obj
@guarded
def add(root, node_type, parents, slug, body, sources, as_json):
    """Create a node with validated relationships."""
    text = read_body(body)
    snapshot, node_id = add_node(
        root_path(root),
        node_type,
        list(parents),
        text,
        slug or summary_slug(text),
        source_input(sources),
    )
    mutation_output(snapshot, [node_id], as_json)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("node_id")
@click.option("--body", help="Replacement body FILE, or - for stdin.")
@click.option(
    "--parent", "parents", multiple=True, help="Replace the complete parent list; repeat per ID."
)
@click.option("--sources", hidden=True)
@json_option
@click.pass_obj
@guarded
def update(root, node_id, body, parents, sources, as_json):
    """Change binding text, parent relationships or source references."""
    if body is None and not parents and sources is None:
        raise SpecError(
            [Diagnostic("ARGUMENT", "Supply --body, --parent or advanced --sources.")], 2
        )
    snapshot = update_node(
        root_path(root),
        node_id,
        body=read_body(body) if body is not None else None,
        parents=list(parents) if parents else None,
        sources=source_input(sources),
    )
    mutation_output(snapshot, [node_id], as_json)


def interactive_stdin():
    return sys.stdin.isatty()


def read_deletion_plan(path):
    if path == "-":
        raw = sys.stdin.buffer.read(MAX_REQUEST_BYTES + 1)
    else:
        with Path(path).open("rb") as stream:
            raw = stream.read(MAX_REQUEST_BYTES + 1)
    try:
        if len(raw) > MAX_REQUEST_BYTES:
            raise ValueError("Plan exceeds the 16 MiB limit.")
        plan = json.loads(raw)
        if not isinstance(plan, dict) or type(plan.get("git_available")) is not bool:
            raise ValueError("Expected the deletion plan object, not a response envelope.")
        return plan
    except (ValueError, TypeError) as error:
        raise SpecError(
            [Diagnostic("DELETE_PLAN", f"Invalid reviewed plan: {error}")], 2
        ) from error


@main.command(name="delete", context_settings={"ignore_unknown_options": True})
@click.argument("ids", nargs=-1, required=True)
@click.option(
    "--dry-run", is_flag=True, help="Preview the full descendant scope and warnings; no writes."
)
@click.option("--yes", is_flag=True, help="Consent to warned deletion; warnings remain visible.")
@click.option("--reviewed-plan", hidden=True)
@json_option
@click.pass_obj
@guarded
def delete(root, ids, dry_run, yes, reviewed_plan, as_json):
    """Delete nodes AND all descendants, including shared children."""
    project = root_path(root)
    if dry_run:
        if reviewed_plan is not None:
            raise SpecError(
                [Diagnostic("ARGUMENT", "Do not combine --dry-run and --reviewed-plan.")], 2
            )
        snapshot = load_snapshot(project)
        plan = deletion_plan(snapshot, list(ids))
        emit(
            plan,
            [*snapshot.diagnostics, *deletion_warnings(plan)],
            as_json=as_json,
            text=render_plan,
        )
        return
    reviewed = read_deletion_plan(reviewed_plan) if reviewed_plan is not None else None
    actual = {}
    warned = []

    def confirm(plan):
        nonlocal actual, warned
        actual = plan
        warnings = deletion_warnings(plan)
        if warnings and not yes and (as_json or not interactive_stdin()):
            emit(
                plan,
                [
                    *warnings,
                    Diagnostic(
                        "DELETE_CONFIRMATION",
                        "No files removed. Review --dry-run, then use --yes "
                        "or an interactive terminal.",
                    ),
                ],
                as_json=as_json,
                ok=False,
                text=render_plan,
            )
            raise click.exceptions.Exit(1)
        if warnings:
            emit(None, warnings)
            warned = warnings
            if not yes:
                return click.confirm(
                    f"Delete all {len(plan['deleted_ids'])} nodes, including shared descendants?",
                    default=False,
                )
        return True

    snapshot = delete_nodes(project, list(ids), confirm=confirm, reviewed_plan=reviewed)
    diagnostics = (
        snapshot.diagnostics if as_json else [d for d in snapshot.diagnostics if d not in warned]
    )
    emit(
        {**actual, "changed_ids": actual["deleted_ids"], "affected": actual["deleted_ids"]},
        diagnostics,
        as_json=as_json,
        text=lambda r: render_receipt(r, "Deleted"),
    )


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("node_id", required=False)
@click.option("--dependents", is_flag=True, help="Show structural descendants of this node.")
@json_option
@click.pass_obj
@guarded
def show(root, node_id, dependents, as_json):
    """List node summaries, or read one complete node."""
    snapshot = load_snapshot(root_path(root))
    graph = snapshot.require_valid()
    if dependents and node_id is None:
        raise SpecError([Diagnostic("ARGUMENT", "--dependents requires a node ID.")], 2)
    if node_id is None:
        emit(
            wire.snapshot(snapshot.to_dict()),
            snapshot.diagnostics,
            as_json=as_json,
            text=render_listing,
        )
        return
    node = require_node(snapshot, node_id)
    if dependents:
        ids = sorted(graph.closure(node_id))
        emit(
            {"id": node_id, "affected": ids},
            snapshot.diagnostics,
            as_json=as_json,
            text=lambda r: (
                f"Dependents of {r['id']} (potential structural scope):\n"
                + "\n".join(f"  {i}  {summary_slug(graph.nodes[i].body)}" for i in ids)
            ),
        )
    else:
        emit(
            {"node": node.to_dict()},
            snapshot.diagnostics,
            as_json=as_json,
            text=lambda r: render_node(r["node"]),
        )


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("node_id", required=False)
@click.option("--base", help="Base commit/ref (default: fresh HEAD).")
@click.option("--target", help="Target commit/ref or workspace (default).")
@click.option("--min-distance", help="Inclusive maximum shortest path, or population percentage.")
@click.option("--max-distance", help="Inclusive maximum longest path, or population percentage.")
@click.option(
    "--influence", help="Inclusive minimum self-inclusive influence, or population percentage."
)
@click.option(
    "--human", is_flag=True, help="Preserve multiline bodies and list sources individually."
)
@json_option
@click.pass_obj
@guarded
def query(root, node_id, base, target, min_distance, max_distance, influence, human, as_json):
    """Read complete bindings or a rooted subgraph; default HEAD to workspace."""
    comparison = read_query(
        root_path(root),
        base,
        target,
        node_id=node_id,
        min_distance=min_distance,
        max_distance=max_distance,
        influence=influence,
    )
    emit(
        wire.comparison(comparison.result) if as_json else render_query(comparison, human=human),
        comparison.diagnostics,
        as_json=as_json,
    )


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("node_id")
@click.option("--max-bytes", type=click.IntRange(min=1), hidden=True)
@json_option
@click.pass_obj
@guarded
def context(root, node_id, max_bytes, as_json):
    """Read complete selected/ancestor bindings, never silently truncated."""
    snapshot = load_snapshot(root_path(root))
    require_node(snapshot, node_id)
    graph = snapshot.require_valid()
    required = graph.closure(node_id, ancestors=True) | {node_id}
    children = graph.children[node_id]
    siblings = {
        child for parent in graph.parents[node_id] for child in graph.children[parent]
    } - required
    result = {
        "selected": node_id,
        "required_ids": sorted(required),
        "child_ids": sorted(children),
        "sibling_ids": sorted(siblings),
        "nodes": [graph.nodes[i].to_dict() for i in graph.order if i in required],
        "omitted_ids": sorted((children | siblings) - required),
    }
    actual = (
        json_text(envelope(result, snapshot.diagnostics))
        if as_json
        else safe_text(render_context(result))
    )
    size = len(actual.encode("utf8")) + 1
    if max_bytes is not None and size > max_bytes:
        raise SpecError(
            [
                Diagnostic(
                    "BUDGET",
                    f"Required context and omission metadata need {size} bytes; "
                    "increase --max-bytes.",
                )
            ]
        )
    emit(result, snapshot.diagnostics, as_json=as_json, text=render_context)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("node_id", required=False)
@click.option("--staged", is_flag=True, help="Validate exact index bytes, not working files.")
@click.option(
    "--sources", "check_sources", is_flag=True, help="Also check source mappings and Git retention."
)
@click.option("--ref", help="Validate an immutable graph/code revision.")
@click.option("--graph-ref", hidden=True)
@click.option("--warnings-as-errors", is_flag=True, hidden=True)
@json_option
@click.pass_obj
@guarded
def check(root, node_id, staged, check_sources, ref, graph_ref, warnings_as_errors, as_json):
    """Check graph consistency and optional source mappings."""
    project = root_path(root)
    snapshot = target_graph(project, ref, staged, graph_ref)
    diagnostics = list(snapshot.diagnostics)
    result = {"node_count": len(snapshot.nodes)}
    if node_id:
        node = require_node(snapshot, node_id)
    if check_sources and snapshot.valid:
        from .sources import check_results, resolve_nodes

        result["sources"] = resolve_nodes(
            project, [node] if node_id else snapshot.nodes, ref=ref, staged=staged, retention=True
        )
        diagnostics.extend(check_results(result["sources"]))
    ok = (
        snapshot.valid
        and not any(d.severity == "error" for d in diagnostics)
        and not (warnings_as_errors and diagnostics)
    )
    emit(
        result,
        diagnostics,
        as_json=as_json,
        ok=ok,
        text=lambda r: (
            f"{'OK' if ok else 'FAILED'} · {r['node_count']} nodes · "
            f"{sum(d.severity == 'error' for d in diagnostics)} errors · "
            f"{sum(d.severity == 'warning' for d in diagnostics)} warnings"
            + (" · exact staged bytes" if staged else "")
        ),
    )
    if not ok:
        raise click.exceptions.Exit(1)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("base", default="HEAD")
@click.argument("target", required=False)
@click.option(
    "--summary", is_flag=True, help="Show an explicitly abridged review instead of full patches."
)
@json_option
@click.pass_obj
@guarded
def diff(root, base, target, summary, as_json):
    """Show a full node-aware diff; default HEAD to working files."""
    result, diagnostics = compare(root_path(root), base, target, patches=not summary)
    emit(
        wire.comparison(result) if as_json else result,
        diagnostics,
        as_json=as_json,
        ok=result["impact_complete"],
        text=lambda r: render_diff(r, summary),
    )
    if not result["impact_complete"]:
        raise click.exceptions.Exit(1)


@main.command(name="recover")
@click.option(
    "--force-lock",
    is_flag=True,
    help="Clear a stale lock only after confirming no writer is running.",
)
@json_option
@click.pass_obj
@guarded
def recover_command(root, force_lock, as_json):
    """Advanced: recover an interrupted managed edit."""
    emit(recover(root_path(root), force_lock=force_lock), as_json=as_json)


@main.command(hidden=True)
@click.option("--stream", is_flag=True, help="Serve bounded newline-delimited API requests.")
@click.pass_obj
@guarded
def api(root, stream):
    """Internal API 6 transport with bounded JSON input and ordinary envelopes."""
    from .api_transport import decode_request, serve

    project = root_path(root)
    if stream:
        raise click.exceptions.Exit(serve(project, sys.stdin.buffer, sys.stdout.buffer))
    value = decode_request(sys.stdin.buffer.read(MAX_REQUEST_BYTES + 1))
    result, diagnostics = application_request(project, value)
    emit(result, diagnostics, as_json=True)


register_sources(main, root_path, emit, guarded, json_option)
register_annotations(main, root_path, emit, guarded, json_option)
