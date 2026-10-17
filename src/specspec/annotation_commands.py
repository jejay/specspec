"""Color-free comparison spotlight CLI."""

import sys

import click

from . import annotations
from .model import ID_RE, Diagnostic, SpecError

STATUS = {
    "added": "A",
    "removed": "D",
    "changed": "M",
    "renamed": "R",
    "unchanged": "=",
    "absent": "?",
    "unavailable": "!",
}


def render_shots(result):
    shots = result["shots"]
    lines = [f"{len(shots)} local spotlight(s) · retained until explicit flush"]
    for shot in shots:
        context = shot["comparison"]
        lines.append(f"\nSpotlight {shot['id']} · {shot['created_at']}")
        lines.append(f"  {context['base']} → {context['target']}")
        lines.append("  " + shot["message"])
        for warning in shot.get("warnings", []):
            lines.append("  WARNING: " + warning)
        for member in shot.get("members", []):
            kind = member["kind"]
            lines.append(f"  {STATUS[kind]} {member['id']}  {member['title'] or kind}")
    return "\n".join(lines)


def parse_arguments(parts):
    if any(part.startswith("--") and not ID_RE.fullmatch(part) for part in parts):
        annotations.fail("Unknown spotlight option; use --base and --target for comparisons.")
    ids = []
    for index, part in enumerate(parts):
        if not ID_RE.fullmatch(part):
            return {
                "nodes": annotations.node_ids(ids),
                "message": annotations.message(" ".join(parts[index:]).strip()),
            }
        ids.append(part)
    annotations.fail("Finish with a spotlight message of 1–500 characters.")


def register(main, root_path, emit, guarded, json_option):
    @main.group(name="spotlight")
    def group():
        """Advanced: add local comparison spotlights, inspect or flush them."""

    @group.command(name="add", context_settings={"ignore_unknown_options": True})
    @click.argument("parts", nargs=-1, required=True, metavar="NODE_ID... MESSAGE")
    @click.option("--base", help="Base commit/ref; explicit refs are pinned. Default: live HEAD.")
    @click.option("--target", help="Target commit/ref or workspace (default).")
    @json_option
    @click.pass_obj
    @guarded
    def add(root, parts, base, target, as_json):
        """Add one message and node IDs in a revision comparison.

        Select IDs from either side, including deleted and unchanged nodes.
        Finish with the message (normally quoted). No colors or node copies.
        """
        path = root_path(root)
        shot = annotations.submit(path, parse_arguments(parts), base=base, target=target)
        emit(annotations.listing(path, shot["id"]), as_json=as_json, text=render_shots)

    @group.command(name="show")
    @click.argument("shot_id", required=False)
    @json_option
    @click.pass_obj
    @guarded
    def show(root, shot_id, as_json):
        """Show all spotlights (or one ID), their comparison statuses and drift warnings."""
        emit(annotations.listing(root_path(root), shot_id), as_json=as_json, text=render_shots)

    @group.command(name="flush")
    @click.option(
        "--yes", is_flag=True, help="Explicitly consent to clearing all local spotlights."
    )
    @json_option
    @click.pass_obj
    @guarded
    def flush(root, yes, as_json):
        """Clear spotlight metadata and obsolete copies; keep specification/recovery."""
        if not yes and (as_json or not sys.stdin.isatty()):
            raise SpecError(
                [Diagnostic("SPOTLIGHTS", "Review spotlight show, then use flush --yes.")]
            )
        if not yes and not click.confirm("Flush all local spotlights?", default=False):
            return
        emit(
            annotations.flush(root_path(root)),
            as_json=as_json,
            text=lambda r: f"Flushed {r['flushed']} local spotlight(s).",
        )
