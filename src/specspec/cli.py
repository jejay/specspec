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
from .batch import apply_edits, prepare
from .deletion import deletion_plan, deletion_warnings
from .editor import MAX_REQUEST_BYTES
from .inspection import findings, raw_document, walks
from .model import ID_RE, MAX_FILE_BYTES, Diagnostic, SpecError
from .output import (
    envelope,
    json_text,
    render_diff,
    render_listing,
    render_node,
    render_plan,
    render_receipt,
    safe_text,
    title,
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
    update_node,
)


def emit(result: Any, diagnostics=None, *, as_json=False, ok=True, text=None, max_bytes=None):
    diagnostics = diagnostics or []
    value = None
    if as_json:
        value = json_text(envelope(result, diagnostics, ok))
    elif result is not None:
        value = safe_text(
            text(result)
            if text
            else result
            if isinstance(result, str)
            else "\n".join(f"{key}: {json_text(val)}" for key, val in result.items())
        )
    if value is not None:
        raw = value.encode("utf8")
        size = len(raw) + 1
        if max_bytes is not None and size > max_bytes:
            raise SpecError(
                [Diagnostic("BUDGET", f"Query response needs {size} bytes; increase --max-bytes.")]
            )
        click.echo(raw)
    if as_json:
        return
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
                ["init", "show", "query", "add", "update", "delete", "check", "diff"],
            ),
            ("Advanced tools", ["apply", "sources", "spotlight", "recover"]),
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


def parent_input(parents, encoded):
    if encoded is None:
        return list(parents) if parents else None
    if parents:
        raise SpecError([Diagnostic("ARGUMENT", "Use --parent or --parents-json, not both.")], 2)
    try:
        values = json.loads(encoded)
        if not isinstance(values, list) or any(
            not isinstance(p, str) or not ID_RE.fullmatch(p) for p in values
        ):
            raise ValueError("Expected full canonical IDs.")
        return values
    except (ValueError, TypeError) as error:
        raise SpecError([Diagnostic("PARENTS", str(error))], 2) from error


def mutation_output(snapshot: Snapshot, ids, as_json):
    affected = walks(snapshot.graph, ids)
    emit(
        {
            "changed_ids": ids,
            "nodes": [{"id": i, "path": require_node(snapshot, i).path} for i in ids],
            "affected": sorted(affected),
            "applied": True,
            **findings(snapshot),
        },
        snapshot.diagnostics,
        as_json=as_json,
        text=render_receipt,
    )


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
@json_option
@click.pass_obj
@guarded
def init(root, manifesto, as_json):
    """Create a graph from manifesto body FILE (or - for stdin)."""
    body = read_body(manifesto)
    snapshot = initialize(root.absolute() if root is not None else Path.cwd(), body)
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
    help="Full parent ID; repeat for multiple parents.",
)
@click.option(
    "--parents-json", hidden=True, help="Explicit complete parent array, including empty."
)
@click.option("--body", required=True, help="Body FILE, or - for stdin.")
@click.option("--sources", hidden=True)
@click.option(
    "--require-valid", is_flag=True, help="Require a valid complete candidate before writing."
)
@json_option
@click.pass_obj
@guarded
def add(root, node_type, parents, parents_json, body, sources, require_valid, as_json):
    """Create a schema-checked node and report graph findings."""
    text = read_body(body)
    snapshot, node_id = add_node(
        root_path(root),
        node_type,
        parent_input(parents, parents_json) or [],
        text,
        source_input(sources),
        require_valid=require_valid,
    )
    mutation_output(snapshot, [node_id], as_json)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("node_id")
@click.option(
    "--parents-json", hidden=True, help="Explicit complete parent array, including empty."
)
@click.option("--body", help="Replacement body FILE, or - for stdin.")
@click.option(
    "--parent", "parents", multiple=True, help="Replace the complete parent list; repeat per ID."
)
@click.option("--sources", hidden=True)
@click.option(
    "--require-valid", is_flag=True, help="Require a valid complete candidate before writing."
)
@json_option
@click.pass_obj
@guarded
def update(root, node_id, body, parents, parents_json, sources, require_valid, as_json):
    """Change binding text, parent relationships or source references."""
    if body is None and not parents and parents_json is None and sources is None:
        raise SpecError(
            [Diagnostic("ARGUMENT", "Supply --body, --parent or advanced --sources.")], 2
        )
    snapshot = update_node(
        root_path(root),
        node_id,
        body=read_body(body) if body is not None else None,
        parents=parent_input(parents, parents_json),
        sources=source_input(sources),
        require_valid=require_valid,
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
    "--dry-run",
    is_flag=True,
    help="Preview exact selected files, retained references and warnings.",
)
@click.option("--yes", is_flag=True, help="Consent to warned deletion; warnings remain visible.")
@click.option("--reviewed-plan", hidden=True)
@click.option(
    "--require-valid", is_flag=True, help="Require a valid complete candidate before writing."
)
@json_option
@click.pass_obj
@guarded
def delete(root, ids, dry_run, yes, reviewed_plan, require_valid, as_json):
    """Delete exactly named nodes; retain surviving references and conclusions."""
    project = root_path(root)
    if dry_run:
        if reviewed_plan is not None:
            raise SpecError(
                [Diagnostic("ARGUMENT", "Do not combine --dry-run and --reviewed-plan.")], 2
            )
        snapshot = load_snapshot(project)
        plan = deletion_plan(snapshot, list(ids))
        if require_valid and not plan["graph_valid"]:
            raise SpecError(
                [Diagnostic("GRAPH", "The proposed saved graph is invalid; no files removed.")]
            )
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
                    f"Delete exactly {len(plan['deleted_ids'])} selected nodes? "
                    "Descendants and their parent references remain.",
                    default=False,
                )
        return True

    snapshot = delete_nodes(
        project, list(ids), confirm=confirm, reviewed_plan=reviewed, require_valid=require_valid
    )
    diagnostics = (
        snapshot.diagnostics if as_json else [d for d in snapshot.diagnostics if d not in warned]
    )
    emit(
        {
            **actual,
            **findings(snapshot),
            "changed_ids": actual["deleted_ids"],
            "affected": sorted(set(actual["deleted_ids"]) | set(actual["potentially_affected"])),
            "applied": True,
        },
        diagnostics,
        as_json=as_json,
        text=lambda r: render_receipt(r, "Deleted"),
    )


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("node_id", required=False)
@click.option("--dependents", is_flag=True, help="Show structural descendants of this node.")
@click.option(
    "--raw", is_flag=True, help="Read literal canonical bytes, including malformed documents."
)
@click.option("--path", help="Direct canonical path for a raw read.")
@click.option("--ref", help="Read an immutable graph revision.")
@click.option("--staged", is_flag=True, help="Read exact staged documents.")
@json_option
@click.pass_obj
@guarded
def show(root, node_id, dependents, raw, path, ref, staged, as_json):
    """List or inspect saved nodes independently of surrounding graph validity."""
    snapshot = target_graph(root_path(root), ref, staged)
    graph = snapshot.graph
    if raw:
        if dependents or (node_id is None and path is None):
            raise SpecError(
                [
                    Diagnostic(
                        "ARGUMENT", "Raw reads need a node ID or --path, without --dependents."
                    )
                ],
                2,
            )
        value = raw_document(snapshot, node_id, path)
        emit(
            value, snapshot.diagnostics, as_json=as_json, text=lambda r: r.get("text", json_text(r))
        )
        return
    if path is not None:
        raise SpecError([Diagnostic("ARGUMENT", "--path requires --raw.")], 2)
    snapshot.require_current()
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
        ids = sorted(graph.closure(node_id)) if graph else []
        emit(
            {
                "id": node_id,
                "affected": ids,
                "graph_valid": snapshot.valid,
                "analysis_complete": snapshot.complete,
            },
            snapshot.diagnostics,
            as_json=as_json,
            text=lambda r: (
                f"Dependents of {r['id']} (potential structural scope):\n"
                + "\n".join(f"  {i}  {title(graph.nodes[i].to_dict())}" for i in ids)
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
@click.option(
    "--with-ancestors", is_flag=True, help="Add every ancestor after selecting the matched nodes."
)
@click.option(
    "--issues", is_flag=True, help="Select structural issues and their potential descendants."
)
@click.option("--max-bytes", type=click.IntRange(min=1), hidden=True)
@json_option
@click.pass_obj
@guarded
def query(
    root,
    node_id,
    base,
    target,
    min_distance,
    max_distance,
    influence,
    human,
    with_ancestors,
    issues,
    max_bytes,
    as_json,
):
    """Read complete bindings or a rooted subgraph; default HEAD to workspace."""
    comparison = read_query(
        root_path(root),
        base,
        target,
        node_id=node_id,
        min_distance=min_distance,
        max_distance=max_distance,
        influence=influence,
        with_ancestors=with_ancestors,
        issues=issues,
    )
    emit(
        wire.comparison(comparison.result) if as_json else render_query(comparison, human=human),
        comparison.diagnostics,
        as_json=as_json,
        max_bytes=max_bytes,
        ok=comparison.result["impact_complete"],
    )
    if not comparison.result["impact_complete"]:
        raise click.exceptions.Exit(1)


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
    result.update(
        graph_valid=snapshot.valid,
        analysis_complete=snapshot.complete,
        **{
            k: v
            for k, v in findings(snapshot).items()
            if k not in {"graph_valid", "analysis_complete"}
        },
    )
    if check_sources:
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
@click.option(
    "--with-context",
    is_flag=True,
    help="Include previous/current justification and cause evidence.",
)
@click.option(
    "--node", "node_ids", multiple=True, help="Focus contextual evidence on these full IDs."
)
@click.option("--max-bytes", type=click.IntRange(min=1), hidden=True)
@json_option
@click.pass_obj
@guarded
def diff(root, base, target, summary, with_context, node_ids, max_bytes, as_json):
    """Show a full node-aware diff; default HEAD to working files."""
    result, diagnostics = compare(
        root_path(root),
        base,
        target,
        patches=not summary,
        with_context=bool(with_context or node_ids),
        node_ids=node_ids,
    )
    emit(
        wire.comparison(result) if as_json else result,
        diagnostics,
        as_json=as_json,
        max_bytes=max_bytes,
        ok=result["impact_complete"],
        text=lambda r: render_diff(r, summary),
    )
    if not result["impact_complete"]:
        raise click.exceptions.Exit(1)


@main.command(name="apply")
@click.argument("plan_file")
@click.option("--dry-run", is_flag=True, help="Plan one explicit batch without canonical writes.")
@click.option(
    "--yes", is_flag=True, help="Consent to selected uncommitted deletions; retain warnings."
)
@click.option(
    "--require-valid", is_flag=True, help="Require the whole candidate to be valid before writing."
)
@json_option
@click.pass_obj
@guarded
def apply_command(root, plan_file, dry_run, yes, require_valid, as_json):
    """Advanced: apply explicit add/update/delete edits in one recoverable batch."""
    from .batch import MAX_BATCH_BYTES

    if plan_file == "-":
        raw = sys.stdin.buffer.read(MAX_BATCH_BYTES + 1)
        directory = Path.cwd()
    else:
        path = Path(plan_file).absolute()
        directory = path.parent
        with path.open("rb") as stream:
            raw = stream.read(MAX_BATCH_BYTES + 1)

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate field: " + key)
            result[key] = value
        return result

    try:
        if len(raw) > MAX_BATCH_BYTES:
            raise ValueError("Batch exceeds 16 MiB.")
        value = json.loads(raw, object_pairs_hook=pairs)
    except (ValueError, RecursionError) as error:
        raise SpecError([Diagnostic("BATCH", str(error))], 2) from error
    edits = prepare(value, directory)
    warnings = []

    def confirm(plan):
        nonlocal warnings
        warnings = deletion_warnings(plan)
        if warnings:
            emit(None, warnings)
            if not yes:
                if as_json or not interactive_stdin():
                    raise SpecError(
                        [
                            *warnings,
                            Diagnostic(
                                "DELETE_CONFIRMATION",
                                "No files changed. Review --dry-run and use --yes "
                                "for selected deletion.",
                            ),
                        ]
                    )
                return click.confirm(
                    f"Delete exactly {len(plan['deleted_ids'])} selected files "
                    "as part of this batch?",
                    default=False,
                )
        return True

    snapshot, receipt = apply_edits(
        root_path(root), edits, dry_run=dry_run, require_valid=require_valid, confirm=confirm
    )
    if dry_run and receipt["deletion_plan"]:
        warnings = deletion_warnings(receipt["deletion_plan"])
    emit(
        receipt,
        [*snapshot.diagnostics, *warnings],
        as_json=as_json,
        text=lambda r: render_receipt(r, "Planned" if dry_run else "Changed"),
    )


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
    """Internal API 7 transport with bounded JSON input and ordinary envelopes."""
    from .api_transport import decode_request, serve

    project = root_path(root)
    if stream:
        raise click.exceptions.Exit(serve(project, sys.stdin.buffer, sys.stdout.buffer))
    value = decode_request(sys.stdin.buffer.read(MAX_REQUEST_BYTES + 1))
    result, diagnostics = application_request(project, value)
    emit(result, diagnostics, as_json=True)


register_sources(main, root_path, emit, guarded, json_option)
register_annotations(main, root_path, emit, guarded, json_option)
