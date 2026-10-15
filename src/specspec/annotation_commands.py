"""Spotlight CLI: add colored node sets directly, inspect or explicitly flush."""

import sys

import click

from . import annotations
from .model import ID_RE, Diagnostic, SpecError


def render_shots(result):
    shots = result["shots"]
    lines = [f"{len(shots)} local spotlight(s) · retained until explicit flush"]
    for shot in shots:
        origin = shot["origin"]
        context = (
            "owner highlights"
            if origin["kind"] == "highlights"
            else origin.get("commit") or "saved workspace"
        )
        lines.append(f"\nSpotlight {shot['id']} · {shot['created_at']} · {context}")
        lines.append("  " + " · ".join(dict.fromkeys(g["text"] for g in shot["groups"])))
        for group in shot["groups"]:
            lines.append(f"  {group['color']} · {len(group['nodes'])} nodes")
            for member in group["nodes"]:
                resolution = ", ".join(
                    f"{ref}: {state}" for ref, state in member.get("resolution", {}).items()
                )
                lines.append(
                    f"    {member['id']}  {member['blob']}  {member['title']}"
                    + (f" ({resolution})" if resolution else "")
                )
    return "\n".join(lines)


def parse_arguments(parts):
    """Read the color/ID prefix, then the single spotlight message."""
    groups = []
    color, nodes, seen = "purple", [], set()
    message = ""
    for index, part in enumerate(parts):
        if part in annotations.INKS:
            if nodes:
                groups.append({"color": color, "nodes": nodes})
            elif index:
                annotations.fail("Each color needs at least one following node ID.")
            color, nodes = part, []
        elif ID_RE.fullmatch(part):
            if part in seen:
                annotations.fail("Each node may occur only once in a spotlight.")
            seen.add(part)
            nodes.append(part)
        else:
            message = " ".join(parts[index:]).strip()
            break
    if not nodes:
        annotations.fail("Supply full node IDs after each color, including the final '='.")
    if not message or len(message) > 500:
        annotations.fail("Finish with a spotlight message of 1–500 characters.")
    groups.append({"color": color, "nodes": nodes})
    return {"groups": [{"text": message, **group} for group in groups]}


def register(main, root_path, emit, guarded, json_option):
    @main.group(name="spotlight")
    def group():
        """Advanced: add local spotlights, inspect or flush them."""

    @group.command(name="add", context_settings={"ignore_unknown_options": True})
    @click.argument("parts", nargs=-1, required=True, metavar="[[COLOR] NODE_ID...]+ MESSAGE")
    @click.option("--ref", help="Capture this committed revision instead of saved workspace files.")
    @json_option
    @click.pass_obj
    @guarded
    def add(root, parts, ref, as_json):
        """Add one message with colored node sets, without creating an input file.

        Colors: red, blue, green, purple, turquoise, yellow. Each color applies
        to following full node IDs; omitted initial color defaults to purple.
        Finish with the message (normally quoted).
        """
        shot = annotations.submit(root_path(root), parse_arguments(parts), ref=ref)
        emit({"shots": [shot]}, as_json=as_json, text=render_shots)

    @group.command(name="show")
    @click.option(
        "--ref",
        "refs",
        multiple=True,
        help="Also check exact presence in this revision; repeat as needed.",
    )
    @json_option
    @click.pass_obj
    @guarded
    def show(root, refs, as_json):
        """Read the retained list and resolve workspace, HEAD and selected revisions."""
        emit(annotations.listing(root_path(root), refs), as_json=as_json, text=render_shots)

    @group.command(name="flush")
    @click.option(
        "--yes",
        is_flag=True,
        help="Explicitly consent to clearing all local spotlights and captured contents.",
    )
    @json_option
    @click.pass_obj
    @guarded
    def flush(root, yes, as_json):
        """Clear spotlights/content only; specification and recovery stay intact."""
        if not yes and (as_json or not sys.stdin.isatty()):
            raise SpecError(
                [Diagnostic("SPOTLIGHTS", "Review spotlight show, then use flush --yes.")]
            )
        if not yes and not click.confirm(
            "Flush all local spotlights and captured contents?", default=False
        ):
            return
        emit(
            annotations.flush(root_path(root)),
            as_json=as_json,
            text=lambda r: f"Flushed {r['flushed']} local spotlight(s).",
        )
