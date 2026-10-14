"""Human presentation and compact, explicit machine serialization."""

from __future__ import annotations

import difflib
import json
from typing import Any

from .model import API_VERSION


def json_text(value: Any) -> str:
    # Invalid filesystem names in diagnostics can contain surrogateescape values.
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        .encode("utf-8", "backslashreplace")
        .decode("utf-8")
    )


def envelope(result, diagnostics=(), ok=True):
    return {
        "api_version": API_VERSION,
        "ok": ok,
        "result": result,
        "diagnostics": [d.to_dict() for d in diagnostics],
    }


def safe_text(text: str) -> str:
    result = []
    for c in text.replace("\r\n", "\n"):
        n = ord(c)
        if (
            (n < 32 and c not in "\n\t")
            or 127 <= n < 160
            or 0x202A <= n <= 0x202E
            or 0x2066 <= n <= 0x2069
        ):
            result.append(f"\\u{n:04x}")
        else:
            result.append(c)
    return "".join(result)


def title(node):
    return next(
        (s.lstrip("# ").strip() for s in node.get("body", "").splitlines() if s.startswith("#")),
        node.get("type", "node"),
    )


def node_label(node):
    return f"{node['id']} · {title(node)}"


def render_node(node):
    lines = [
        f"## {node_label(node)}",
        f"Type: {node['type']}",
        f"File: {node['path']}",
        "Parents: " + (", ".join(node["parents"]) or "none"),
    ]
    if "format_version" in node:
        lines.append(f"Node format: {node['format_version']}")
    if node.get("sources"):
        lines.append("Sources: " + json_text(node["sources"]))
    if node.get("extensions"):
        lines.append("Extensions: " + json_text(node["extensions"]))
    return "\n".join(lines) + "\n\n" + node["body"].rstrip("\n") + "\n"


def render_listing(snapshot):
    return "\n".join(
        [
            f"{len(snapshot['nodes'])} nodes",
            *[
                f"{n['id']}  {n['type']:14}  {title(n)}  ({len(n['parents'])} parents)"
                for n in snapshot["nodes"]
            ],
        ]
    )


def render_context(result):
    parts = [
        f"Binding context for {result['selected']} · {len(result['required_ids'])} required nodes"
    ]
    parts.extend(render_node(n) for n in result["nodes"])
    if result["omitted_ids"]:
        parts.append("Surrounding nodes (bodies not included): " + ", ".join(result["omitted_ids"]))
    return "\n\n".join(parts)


def render_receipt(result, verb="Changed"):
    lines = [f"{verb}: " + ", ".join(result["changed_ids"])]
    lines += [f"  {n['id']}  {n['path']}" for n in result.get("nodes", [])]
    lines.append(
        f"Affected: {len(result.get('affected', []))} nodes "
        "(potential scope, not proof of invalidity)"
    )
    return "\n".join(lines)


def render_plan(plan):
    lines = [f"Delete {len(plan['deleted_ids'])} nodes, including all shared descendants:"]
    lines += [f"  {n['id']}  {n['path']}" for n in plan["nodes"]]
    return "\n".join(lines)


def line_endings(raw: bytes):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    cr = raw.count(b"\r") - crlf
    return {"crlf": crlf, "lf": lf, "cr": cr, "final_newline": raw.endswith((b"\n", b"\r"))}


def file_patches(base, target):
    result = []
    for path in sorted(base.files.keys() | target.files.keys()):
        old, new = base.files.get(path), target.files.get(path)
        if old == new:
            continue
        entry = {
            "path": path,
            "kind": "added" if old is None else "removed" if new is None else "changed",
        }
        try:
            a, b = (old or b"").decode("utf8"), (new or b"").decode("utf8")
            patch = []
            for line in difflib.unified_diff(
                a.splitlines(keepends=True),
                b.splitlines(keepends=True),
                fromfile="/dev/null" if old is None else "a/" + path,
                tofile="/dev/null" if new is None else "b/" + path,
                lineterm="\n",
            ):
                if line.endswith("\n"):
                    patch.append(line)
                else:
                    patch.append(line + "\n\\ No newline at end of file\n")
            entry["patch"] = "".join(patch)
            entry["line_endings"] = {
                "before": line_endings(old or b""),
                "after": line_endings(new or b""),
            }
        except UnicodeError:
            entry["note"] = "Non-UTF-8 canonical bytes; textual patch unavailable."
        result.append(entry)
    return result


def render_diff(result, summary=False):
    codes = {"added": "A", "changed": "M", "removed": "D", "renamed": "R"}
    counts = {kind: sum(c["kind"] == kind for c in result["changes"]) for kind in codes}
    lines = [
        f"{result.get('base_ref', 'base')} → {result.get('target_ref', 'workspace')}",
        "Nodes: " + " · ".join(f"{counts[k]} {k}" for k in codes),
        f"Relationships: +{len(result['added_edges'])} -{len(result['removed_edges'])}",
    ]
    old = {n["id"]: n for n in result["base"]["nodes"]}
    new = {n["id"]: n for n in result["target"]["nodes"]}
    changes = {c["id"]: c for c in result["changes"]}
    for c in result["changes"]:
        n = new.get(c["id"], old.get(c["id"]))
        lines += ["", f"{codes[c['kind']]} {node_label(n)} · {n['type']}"]
        if c["fields"]:
            lines.append("  Changed: " + ", ".join(c["fields"]))
        if c["id"] in old and c["id"] in new and old[c["id"]]["path"] != new[c["id"]]["path"]:
            lines.append(f"  File: {old[c['id']]['path']} → {new[c['id']]['path']}")
    if not summary:
        # Canonical patches contain frontmatter and body. Their complete set also
        # includes comment/whitespace changes with no semantic node modification.
        path_nodes = {n["path"]: n for n in [*old.values(), *new.values()]}
        for f in result["file_changes"]:
            n = path_nodes.get(f["path"])
            lines += [
                "",
                (f"File patch: {node_label(n)}" if n else "File patch") + f" · {f['path']}",
            ]
            if n and n["id"] not in changes:
                lines.append("  File-only change; canonical node meaning unchanged.")
            endings = f.get("line_endings")

            def ending_style(value):
                return ([k for k in ("crlf", "lf", "cr") if value[k]], value["final_newline"])

            if endings and ending_style(endings["before"]) != ending_style(endings["after"]):
                lines.append("  Line endings/newline: " + json_text(endings))
            lines.append(f.get("patch", f.get("note", "")))
        if result["added_edges"] or result["removed_edges"]:
            lines += ["", "Relationship changes:"]
            for sign, key, nodes in [("-", "removed_edges", old), ("+", "added_edges", new)]:
                for parent, child in result[key]:
                    left = node_label(nodes[parent]) if parent in nodes else parent
                    right = node_label(nodes[child]) if child in nodes else child
                    lines.append(f"{sign} {left} → {right}")
    if result.get("source_changes"):
        lines += ["", "Linked-source changes (informational; not specification modifications):"]
        for source in result["source_changes"]:
            lines.append(
                f"  {source['path']} · implementations: {', '.join(source['implementation_ids'])}"
            )
    if not result["impact_complete"]:
        lines.append("Comparison/impact incomplete; see diagnostics.")
    elif not result["changes"] and not result["file_changes"] and not result.get("source_changes"):
        lines.append("No specification or linked-source changes.")
    return "\n".join(lines)


def render_sources(result):
    if "resolution" in result:
        r = result["resolution"]
        lines = [
            f"{r['path']} · {r['outcome']}"
            + (" · original anchor preview" if result["original"] else "")
        ]
        for chunk in result["chunks"]:
            lines += [f"{chunk['start'] + i:5}  {line}" for i, line in enumerate(chunk["lines"])]
        return "\n".join(lines)
    if "reference" in result:
        return (
            ("Source captured" if result["written"] else "Source preview — no files written")
            + "\n"
            + json_text(result["reference"])
        )
    lines = []
    for row in result["sources"]:
        ranges = ", ".join(f"{a}:{b}" for a, b in row.get("ranges", []))
        lines.append(
            f"{row['id']} · source {row['source']} · {row['path']} · {row['outcome']}"
            + (f" · lines {ranges}" if ranges else "")
        )
        if row.get("message"):
            lines.append("  " + row["message"])
    return "\n".join(lines) or "No source references."
