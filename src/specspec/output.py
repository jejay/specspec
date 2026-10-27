"""Human presentation and compact, explicit machine serialization."""

from __future__ import annotations

import difflib
import json
from typing import Any

from .model import API_VERSION
from .node_text import logical_bytes, logical_text


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
    if node.get("sources"):
        lines.append("Sources: " + json_text(node["sources"]))
    if node.get("extensions"):
        lines.append("Extensions: " + json_text(node["extensions"]))
    return "\n".join(lines) + "\n\n" + node["body"].rstrip("\n") + "\n"


def render_listing(snapshot):
    return "\n".join(
        [
            f"{len(snapshot['nodes'])} nodes"
            + (" · graph INVALID" if not snapshot.get("valid", True) else ""),
            *[
                f"{n['id']}  {n['type']:14}  {title(n)}  ({len(n['parents'])} parents)"
                for n in snapshot["nodes"]
            ],
        ]
    )


def action_lines(actions, *, dry_run=False):
    labels = [
        ("added", "Added", "Would add"),
        ("modified", "Modified", "Would modify"),
        ("deleted", "Deleted", "Would delete"),
        ("unchanged", "Unchanged", "Unchanged"),
    ]
    return [
        f"{preview if dry_run else actual}: " + ", ".join(actions[action])
        for action, actual, preview in labels
        if actions.get(action)
    ]


def render_receipt(result, actions, *, dry_run=False):
    lines = action_lines(actions, dry_run=dry_run)
    if instructions := result.get("agent_instructions"):
        status = "created" if instructions["created"] else "template appended"
        lines.append(f"Agent instructions: {instructions['path']} ({status})")
    if result.get("aliases"):
        lines.append(
            "Aliases: "
            + ", ".join(f"${name} -> {id}" for name, id in sorted(result["aliases"].items()))
        )
    lines.append(
        f"Affected: {len(result.get('affected', []))} nodes "
        "(potential scope, not proof of invalidity)"
    )
    if result.get("graph_valid") is False:
        label = "Saved" if result.get("applied", True) else "Proposed"
        lines.append(f"{label} graph is INVALID. Surviving conclusions need reconsideration.")
        for ref in result.get("broken_references", []):
            lines.append(f"Unresolved: {ref['parent']} -> {ref['child']} ({ref['reason']})")
    if result.get("analysis_complete") is False:
        lines.append("Analysis incomplete; unreadable material remains explicit.")
    return "\n".join(lines)


def render_plan(plan):
    lines = [
        *action_lines({"deleted": plan["deleted_ids"]}, dry_run=True),
        "Descendants and their parent declarations remain.",
    ]
    for ref in plan.get("broken_references", []):
        lines.append(
            f"Retained unresolved reference: {ref['parent']} -> {ref['child']} ({ref['reason']})"
        )
    lines.append(
        "Potential surviving downstream scope: "
        + (", ".join(plan.get("potentially_affected", [])) or "none")
    )
    lines.append("Resulting graph: " + ("valid" if plan.get("graph_valid") else "INVALID"))
    if plan.get("analysis_complete") is False:
        lines.append("Analysis incomplete; see diagnostics.")
    return "\n".join(lines)


def physical_lines(text: str) -> list[str]:
    """LF-delimited file lines, retaining CR and Unicode separators as payload."""
    parts = text.split("\n")
    return [part + "\n" for part in parts[:-1]] + ([parts[-1]] if parts[-1] else [])


def line_endings(raw: bytes):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    cr = raw.count(b"\r") - crlf
    return {"crlf": crlf, "lf": lf, "cr": cr, "final_newline": raw.endswith((b"\n", b"\r"))}


def file_patches(base, target):
    result = []
    for path in sorted(base.files.keys() | target.files.keys()):
        old, new = base.files.get(path), target.files.get(path)
        if logical_bytes(old) == logical_bytes(new):
            continue
        entry = {
            "path": path,
            "kind": "added" if old is None else "removed" if new is None else "changed",
        }
        try:
            a, b = (logical_text(raw.decode("utf8")) for raw in [old or b"", new or b""])
            left, right = physical_lines(a), physical_lines(b)
            fromfile = "/dev/null" if old is None else "a/" + path
            tofile = "/dev/null" if new is None else "b/" + path
            rows = difflib.unified_diff(
                left, right, fromfile=fromfile, tofile=tofile, lineterm="\n"
            )
            patch = []
            for line in rows:
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
    codes = {"added": "A", "changed": "M", "removed": "D", "unavailable": "?"}
    counts = {kind: sum(c["kind"] == kind for c in result["changes"]) for kind in codes}
    lines = [
        f"{result.get('base_ref', 'base')} → {result.get('target_ref', 'workspace')}",
        "Nodes: " + " · ".join(f"{counts[k]} {k}" for k in codes),
        f"Relationships: +{len(result['added_edges'])} -{len(result['removed_edges'])}",
    ]
    lines.extend("NOTE: " + note for note in result.get("notes", []))
    old = {n["id"]: n for n in result["base"]["nodes"]}
    new = {n["id"]: n for n in result["target"]["nodes"]}
    changes = {c["id"]: c for c in result["changes"]}
    for c in result["changes"]:
        n = new.get(c["id"], old.get(c["id"]))
        lines += ["", f"{codes[c['kind']]} {node_label(n)} · {n['type']}"]
        if c["fields"]:
            lines.append("  Changed: " + ", ".join(c["fields"]))
    if not summary:
        # Logical patches contain frontmatter/body and retain comment/whitespace
        # changes. Newline encodings are storage details; raw reads retain bytes.
        path_nodes = {n["path"]: n for n in [*old.values(), *new.values()]}
        for f in result["file_changes"]:
            n = path_nodes.get(f["path"])
            lines += [
                "",
                (f"File patch: {node_label(n)}" if n else "File patch") + f" · {f['path']}",
            ]
            if n and n["id"] not in changes:
                lines.append("  File-only change; canonical node meaning unchanged.")
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
    if result.get("graph_valid") is False:
        lines.append(
            "Target graph INVALID; observed edits are not a semantic-justification verdict."
        )
    unresolved = result.get("unresolved_references", {}).get("target", [])
    if unresolved:
        lines += ["", "Unresolved current declarations (not implicitly removed parent links):"]
        lines += [f"  {r['parent']} -> {r['child']}" for r in unresolved]
    if context := result.get("context"):
        lines += ["", "Justification context:", context["interpretation"]]
        for record in context["records"]:
            lines += [
                "",
                f"Context {record['id']}" + (" · unchanged" if record["unchanged"] else ""),
            ]
            if not record["unchanged"]:
                lines.append("Before:")
                lines.append(
                    render_node(record["before"])
                    if record.get("before")
                    else "Earlier binding unavailable."
                )
            lines.append("Current:")
            lines.append(
                render_node(record["current"])
                if record.get("current")
                else "No identifiable current binding; inspect inventory/history."
            )
        for witness in context["cause_paths"]:
            lines.append(witness["basis"] + " potential path: " + " -> ".join(witness["path"]))
        if context["unavailable_ids"]:
            lines.append("Bindings unavailable: " + ", ".join(context["unavailable_ids"]))
        if not context["complete"]:
            lines.append(
                "Context incomplete; unavailable documents/history are not empty evidence."
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
