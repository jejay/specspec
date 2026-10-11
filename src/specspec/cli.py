"""CLI surface shared by people, agents, hooks, and the VS Code extension."""

from __future__ import annotations

import json
import sys
from functools import wraps
from pathlib import Path
from typing import Any

import click

from . import __version__
from .editor import MAX_REQUEST_BYTES, editor_request
from .format import safe_source_path
from .git import git_snapshot, install_hook, semantic_diff, source_change_impact
from .model import API_VERSION, Diagnostic, SpecError
from .workspace import (
    Snapshot,
    add_node,
    discover_root,
    initialize,
    load_snapshot,
    recover,
    require_node,
    set_retired,
    update_node,
)


def emit(
    result: Any,
    diagnostics: list[Diagnostic] | None = None,
    *,
    as_json: bool = False,
    ok: bool = True,
) -> None:
    diagnostics = diagnostics or []
    envelope = {
        "api_version": API_VERSION,
        "ok": ok,
        "result": result,
        "diagnostics": [diagnostic.to_dict() for diagnostic in diagnostics],
    }
    if as_json:
        click.echo(json.dumps(envelope, ensure_ascii=True, indent=2))
    else:
        if result is not None:
            click.echo(
                result
                if isinstance(result, str)
                else json.dumps(result, ensure_ascii=True, indent=2)
            )
        for diagnostic in diagnostics:
            location = f" ({diagnostic.path})" if diagnostic.path else ""
            click.echo(
                f"{diagnostic.severity}: {diagnostic.code}{location}: {diagnostic.message}",
                err=True,
            )


def guarded(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        as_json = kwargs.get("as_json", False) or kwargs.get("output_format") == "json"
        try:
            return function(*args, **kwargs)
        except SpecError as error:
            emit(None, error.diagnostics, as_json=as_json, ok=False)
            raise click.exceptions.Exit(error.exit_code) from error
        except (OSError, UnicodeError) as error:
            emit(None, [Diagnostic("IO", str(error))], as_json=as_json, ok=False)
            raise click.exceptions.Exit(2) from error

    return wrapper


json_option = click.option("--json", "as_json", is_flag=True, help="Emit the versioned JSON API.")


def root_path(explicit: Path | None) -> Path:
    return explicit.absolute() if explicit is not None else discover_root()


def read_body(path: str) -> str:
    # Decode bytes directly to preserve CRLF and all binding Markdown whitespace.
    if path == "-":
        return sys.stdin.buffer.read().decode("utf-8")
    return Path(path).read_bytes().decode("utf-8")


def source_input(value: str | None) -> list[dict[str, str]] | None:
    if value is None:
        return None
    try:
        sources = json.loads(value)
        if not isinstance(sources, list):
            raise ValueError("Expected an array.")
        for source in sources:
            if not isinstance(source, dict) or not set(source) <= {"path", "symbol"}:
                raise ValueError("Each source needs path and an optional symbol.")
            if not isinstance(source.get("path"), str) or not safe_source_path(source["path"]):
                raise ValueError("Unsafe source path.")
            if "symbol" in source and not isinstance(source["symbol"], str):
                raise ValueError("symbol must be a string.")
        return sources
    except (ValueError, TypeError) as error:
        raise SpecError([Diagnostic("SOURCES", f"Invalid sources JSON: {error}")]) from error


def mutation_output(snapshot: Snapshot, ids: list[str], as_json: bool) -> None:
    graph = snapshot.require_valid()
    affected = set().union(*(graph.closure(node_id) for node_id in ids)) if ids else set()
    emit(
        {**snapshot.to_dict(), "changed_ids": ids, "affected": sorted(affected)},
        snapshot.diagnostics,
        as_json=as_json,
    )


@click.group()
@click.option(
    "--root", type=click.Path(path_type=Path, file_okay=False), help="Explicit project root."
)
@click.version_option(__version__)
@click.pass_context
def main(context: click.Context, root: Path | None) -> None:
    """Manage an intention–conclusion specification graph."""
    context.obj = root


@main.command()
@click.option("--manifesto", required=True, help="Markdown body file, or - for stdin.")
@click.option("--slug", default="project-manifesto", show_default=True)
@json_option
@click.pass_obj
@guarded
def init(root: Path | None, manifesto: str, slug: str, as_json: bool) -> None:
    """Initialize a workspace from supplied manifesto text."""
    snapshot = initialize(
        root.absolute() if root is not None else Path.cwd(), read_body(manifesto), slug
    )
    mutation_output(snapshot, [snapshot.nodes[0].id], as_json)


@main.command()
@json_option
@click.option("--warnings-as-errors", is_flag=True)
@click.pass_obj
@guarded
def validate(root: Path | None, as_json: bool, warnings_as_errors: bool) -> None:
    """Check the working specification without changing it."""
    snapshot = load_snapshot(root_path(root))
    ok = snapshot.valid and not (warnings_as_errors and snapshot.diagnostics)
    emit(
        {"node_count": len(snapshot.nodes)},
        snapshot.diagnostics,
        as_json=as_json,
        ok=ok,
    )
    if not ok:
        raise click.exceptions.Exit(1)


@main.command(name="add")
@click.option(
    "--type",
    "node_type",
    type=click.Choice(["requirement", "implementation"]),
    default="requirement",
)
@click.option("--parent", "parents", multiple=True, required=True)
@click.option("--slug", required=True)
@click.option("--body", required=True, help="Markdown body file, or - for stdin.")
@click.option("--sources", help="JSON array of implementation source references.")
@json_option
@click.pass_obj
@guarded
def add(
    root: Path | None,
    node_type: str,
    parents: tuple[str, ...],
    slug: str,
    body: str,
    sources: str | None,
    as_json: bool,
) -> None:
    """Create a node without an approval stage."""
    snapshot, node_id = add_node(
        root_path(root),
        node_type,
        list(parents),
        read_body(body),
        slug,
        source_input(sources),
    )
    mutation_output(snapshot, [node_id], as_json)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("node_id")
@click.option("--body", help="Replacement Markdown body file, or - for stdin.")
@click.option("--parent", "parents", multiple=True, help="Replace the complete parent list.")
@click.option("--clear-parents", is_flag=True)
@click.option("--sources", help="Replace source references with this JSON array.")
@json_option
@click.pass_obj
@guarded
def update(
    root: Path | None,
    node_id: str,
    body: str | None,
    parents: tuple[str, ...],
    clear_parents: bool,
    sources: str | None,
    as_json: bool,
) -> None:
    """Edit binding text or relationships through validated writes."""
    if clear_parents and parents:
        raise SpecError([Diagnostic("ARGUMENT", "Do not combine --parent and --clear-parents.")], 2)
    if body is None and not parents and not clear_parents and sources is None:
        raise SpecError(
            [Diagnostic("ARGUMENT", "Supply --body, --parent, --clear-parents or --sources.")], 2
        )
    parent_list = [] if clear_parents else list(parents) if parents else None
    snapshot = update_node(
        root_path(root),
        node_id,
        body=read_body(body) if body is not None else None,
        parents=parent_list,
        sources=source_input(sources),
    )
    mutation_output(snapshot, [node_id], as_json)


def withdrawal_command(name: str, retired: bool):
    @main.command(name=name, context_settings={"ignore_unknown_options": True})
    @click.argument("ids", nargs=-1, required=True)
    @json_option
    @click.pass_obj
    @guarded
    def command(root: Path | None, ids: tuple[str, ...], as_json: bool) -> None:
        mutation_output(set_retired(root_path(root), list(ids), retired), list(ids), as_json)

    command.help = (
        "Withdraw nodes, retaining their history."
        if retired
        else "Restore withdrawn nodes; this is not approval."
    )
    return command


withdrawal_command("retire", True)
withdrawal_command("restore", False)


@main.command(name="list")
@click.option("--retired", "only_retired", is_flag=True, help="List withdrawn nodes only.")
@click.option("--live", "only_live", is_flag=True, help="Exclude withdrawn nodes.")
@json_option
@click.pass_obj
@guarded
def list_nodes(root: Path | None, only_retired: bool, only_live: bool, as_json: bool) -> None:
    """List nodes in the current specification graph."""
    if only_retired and only_live:
        raise SpecError([Diagnostic("ARGUMENT", "Do not combine --retired and --live.")], 2)
    snapshot = load_snapshot(root_path(root))
    snapshot.require_valid()
    result = snapshot.to_dict()
    if only_retired or only_live:
        result["nodes"] = [node for node in result["nodes"] if node["retired"] == only_retired]
        visible = {node["id"] for node in result["nodes"]}
        result["edges"] = [edge for edge in result["edges"] if set(edge) <= visible]
    emit(result, snapshot.diagnostics, as_json=as_json)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("node_id")
@click.option("--ancestors", is_flag=True)
@click.option("--descendants", is_flag=True)
@json_option
@click.pass_obj
@guarded
def show(
    root: Path | None, node_id: str, ancestors: bool, descendants: bool, as_json: bool
) -> None:
    """Show a node, optionally with its graph context."""
    snapshot = load_snapshot(root_path(root))
    node = require_node(snapshot, node_id)
    graph = snapshot.require_valid()
    related = (graph.closure(node_id, ancestors=True) if ancestors else set()) | (
        graph.closure(node_id) if descendants else set()
    )
    emit(
        {
            "node": node.to_dict(),
            "related": [graph.nodes[key].to_dict() for key in graph.order if key in related],
        },
        snapshot.diagnostics,
        as_json=as_json,
    )


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("node_id")
@json_option
@click.pass_obj
@guarded
def impact(root: Path | None, node_id: str, as_json: bool) -> None:
    """Report structural dependents of a node."""
    snapshot = load_snapshot(root_path(root))
    require_node(snapshot, node_id)
    emit(
        {
            "id": node_id,
            "affected": sorted(snapshot.require_valid().closure(node_id)),
        },
        snapshot.diagnostics,
        as_json=as_json,
    )


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("node_id")
@click.option("--max-bytes", type=click.IntRange(min=1))
@click.option("--include-retired", is_flag=True)
@json_option
@click.pass_obj
@guarded
def context(
    root: Path | None, node_id: str, max_bytes: int | None, include_retired: bool, as_json: bool
) -> None:
    """Export complete binding context, never silently truncated."""
    snapshot = load_snapshot(root_path(root))
    node = require_node(snapshot, node_id)
    graph = snapshot.require_valid()
    if node.retired and not include_retired:
        raise SpecError([Diagnostic("RETIRED", "Use --include-retired to export a retired node.")])
    required = graph.closure(node_id, ancestors=True) | {node_id}
    children = {
        key for key in graph.children[node_id] if include_retired or not graph.nodes[key].retired
    }
    siblings = {
        child
        for parent in graph.parents[node_id]
        for child in graph.children[parent]
        if include_retired or not graph.nodes[child].retired
    } - required
    optional = (children | siblings) - required
    result = {
        "selected": node_id,
        "required_ids": sorted(required),
        "child_ids": sorted(children),
        "sibling_ids": sorted(siblings),
        "nodes": [graph.nodes[key].to_dict() for key in graph.order if key in required],
        "omitted_ids": sorted(optional),
    }

    def output_size(payload: dict[str, Any]) -> int:
        displayed = payload
        if as_json:
            displayed = {
                "api_version": API_VERSION,
                "ok": True,
                "result": payload,
                "diagnostics": [item.to_dict() for item in snapshot.diagnostics],
            }
        return len(json.dumps(displayed, ensure_ascii=True, indent=2).encode("utf-8")) + 1

    if max_bytes and output_size(result) > max_bytes:
        raise SpecError(
            [
                Diagnostic(
                    "BUDGET",
                    f"Required context and omission metadata need {output_size(result)} "
                    "bytes; increase --max-bytes.",
                )
            ]
        )
    for key in graph.order:
        if key not in optional:
            continue
        candidate = {
            **result,
            "nodes": [*result["nodes"], graph.nodes[key].to_dict()],
            "omitted_ids": [item for item in result["omitted_ids"] if item != key],
        }
        if max_bytes is None or output_size(candidate) <= max_bytes:
            result = candidate
    emit(result, snapshot.diagnostics, as_json=as_json)


@main.command(name="export")
@click.option("--format", "output_format", type=click.Choice(["json", "mermaid"]), default="json")
@click.pass_obj
@guarded
def export_graph(root: Path | None, output_format: str) -> None:
    """Export graph data or a Mermaid diagram to stdout."""
    snapshot = load_snapshot(root_path(root))
    graph = snapshot.require_valid()
    if output_format == "json":
        emit(snapshot.to_dict(), snapshot.diagnostics, as_json=True)
    else:

        def mermaid_id(node_id: str) -> str:
            return "n_" + node_id.encode("ascii").hex()

        lines = ["graph TD"]
        for node_id in graph.order:
            node = graph.nodes[node_id]
            title = next(
                (line.lstrip("# ") for line in node.body.splitlines() if line.startswith("#")),
                node.type,
            )
            title = (
                title.replace("&", "&amp;")
                .replace('"', "&quot;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            suffix = " (retired)" if node.retired else ""
            lines.append(f'  {mermaid_id(node_id)}["{title}{suffix}"]')
        lines.extend(
            f"  {mermaid_id(parent)} --> {mermaid_id(child)}" for parent, child in graph.edges()
        )
        click.echo("\n".join(lines))


@main.command(name="editor")
@click.option("--base", help="Optional Git base for an overlay comparison.")
@json_option
@click.pass_obj
@guarded
def editor(root: Path | None, base: str | None, as_json: bool) -> None:
    """Read document overlays / plan an edit from JSON stdin, without writing files."""
    raw = sys.stdin.buffer.read(MAX_REQUEST_BYTES + 1)
    if len(raw) > MAX_REQUEST_BYTES:
        raise SpecError([Diagnostic("EDITOR", "Editor request exceeds the 16 MiB limit.")], 2)
    try:
        request = json.loads(raw)
    except (ValueError, UnicodeError) as error:
        raise SpecError([Diagnostic("EDITOR", f"Invalid editor JSON: {error}")], 2) from error
    result = editor_request(root_path(root), request, base)
    # Invalid buffers are a successful read/plan with explicit schema/DAG diagnostics.
    emit(result, [Diagnostic(**entry) for entry in result["diagnostics"]], as_json=as_json)


@main.command()
@click.option("--base", required=True)
@click.option("--target", help="Target commit; defaults to working files.")
@json_option
@click.pass_obj
@guarded
def diff(root: Path | None, base: str, target: str | None, as_json: bool) -> None:
    """Compare graphs by identity without checking out another revision."""
    project = root_path(root)
    old = git_snapshot(project, base, allow_empty=True)
    new = git_snapshot(project, target) if target else load_snapshot(project)
    diagnostics = old.diagnostics + new.diagnostics
    result = semantic_diff(old, new)
    result.update(source_change_impact(project, base, target, old, new))
    result["affected"] = sorted(set(result["affected"]) | set(result["source_affected"]))
    result.update({"base_ref": base, "target_ref": target or "workspace"})
    emit(result, diagnostics, as_json=as_json, ok=old.valid and new.valid)
    if not old.valid or not new.valid:
        raise click.exceptions.Exit(1)


@main.group()
def hook() -> None:
    """Install or run staged-content validation."""


@hook.command(name="install")
@json_option
@click.pass_obj
@guarded
def hook_install(root: Path | None, as_json: bool) -> None:
    project = root_path(root)
    load_snapshot(project).require_valid()
    path = install_hook(project)
    emit({"hook": str(path)}, as_json=as_json)


@hook.command(name="check")
@json_option
@click.pass_obj
@guarded
def hook_check(root: Path | None, as_json: bool) -> None:
    snapshot = git_snapshot(root_path(root), staged=True)
    emit(
        {"node_count": len(snapshot.nodes)},
        snapshot.diagnostics,
        as_json=as_json,
        ok=snapshot.valid,
    )
    if not snapshot.valid:
        raise click.exceptions.Exit(1)


@main.command(name="recover")
@click.option(
    "--force-lock",
    is_flag=True,
    help="Remove a stale lock only after confirming no writer is running.",
)
@json_option
@click.pass_obj
@guarded
def recover_command(root: Path | None, force_lock: bool, as_json: bool) -> None:
    emit(recover(root_path(root), force_lock=force_lock), as_json=as_json)
