"""Graphs as models return them: build, check with specspec's validator, measure, render.

A drawn graph is a dictionary from node key to ``type``, ``parents``, ``title`` and
``body``. The manifesto has the key ``ROOT``, whatever name or ID an answer used for it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from specspec.graph import build_graph
from specspec.model import SpecNode

ROOT = "ROOT"
BASE_FILE = Path(__file__).resolve().parent / "quizzes" / "revise.graph.json"

# Phrases that state when something gets built. Checked by text, because a grader reads
# "what to bake first" or "the day before" as an order of work too easily.
BUILD_ORDER = re.compile(
    r"\b(?:phase|stage|step)\s+(?:\d|one|two|three)\b|\bdeferred\b|\bthree stages\b"
    r"|\bin (?:two|three) (?:stages|phases|steps)\b|\bbuild order\b|\bdelivery order\b"
    r"|\bbuil[dt] (?:first|later|last|after|before|in this order|in the order)\b"
    r"|\bbefore any feature\b|\bfirst component\b|\bwill be built\b|\bfor later implementation\b"
    r"|\bin place before the\b|\bproject first\b|\bestablished first\b|\bcomes? (?:later|last)\b"
    r"|\bdelivered (?:first|later|last|in)\b"
    r"|\b(?:first|second|third|last) (?:stage|phase|step|increment|milestone)\b",
    re.I,
)


def key_of(name, root_names: set[str], known: set[str] | frozenset[str] = frozenset()) -> str:
    """One spelling per node: the manifesto is ROOT, and IDs may lack ``$`` or ``=``."""
    name = str(name).strip().lstrip("$")
    if name.lower() == "manifesto" or name in root_names or name + "=" in root_names:
        return ROOT
    return name + "=" if name + "=" in known else name


def node(kind: str, parents: list[str], title: str, body: str, origin: str | None = None) -> dict:
    record = {"type": kind, "parents": parents, "title": title, "body": body}
    return {**record, "origin": origin} if origin else record


def drawn(data: dict, root_names: set[str]) -> dict[str, dict]:
    """The graph of an answer that lists ``nodes``."""
    nodes = {ROOT: node("manifesto", [], "", "")}
    for raw in data.get("nodes") or []:
        key = key_of(raw.get("key", ""), root_names)
        if key == ROOT:
            continue
        nodes[key] = node(
            str(raw.get("type", "requirement")).strip().lower(),
            [key_of(parent, root_names) for parent in raw.get("parents") or []],
            str(raw.get("title", "")).lstrip("# ").strip(),
            str(raw.get("body", "")),
        )
    return nodes


def base() -> tuple[dict[str, dict], set[str]]:
    """The graph that the revision tasks start from, and the names of its manifesto."""
    records = json.loads(BASE_FILE.read_text(encoding="utf-8"))
    root_names = {record["id"] for record in records if record["type"] == "manifesto"}
    nodes = {}
    for record in records:
        key = key_of(record["id"], root_names)
        parents = [key_of(parent, root_names) for parent in record["parents"]]
        nodes[key] = node(record["type"], parents, record["title"], record["body"], "base")
    return nodes, root_names


def revised(data: dict) -> tuple[dict[str, dict], dict[str, list[str]]]:
    """Apply an answer's ``operations`` to the base graph."""
    nodes, root_names = base()
    known = frozenset(nodes)
    summary: dict[str, list[str]] = {"added": [], "updated": [], "deleted": [], "unknown": []}
    for operation in data.get("operations") or []:
        kind = str(operation.get("op", "")).lower()
        if kind == "add":
            key = key_of(operation.get("key", f"new{len(nodes)}"), root_names, known)
            nodes[key] = node(
                str(operation.get("type", "requirement")).strip().lower(),
                [key_of(parent, root_names, known) for parent in operation.get("parents") or []],
                str(operation.get("title", "")).lstrip("# ").strip(),
                str(operation.get("body", "")),
                "added",
            )
            summary["added"].append(key)
            continue
        key = key_of(operation.get("id", ""), root_names, known)
        if key not in nodes or kind not in ("update", "delete"):
            summary["unknown"].append(key)
        elif kind == "delete":
            del nodes[key]
            summary["deleted"].append(key)
        else:
            changed = []
            if operation.get("parents") is not None:
                nodes[key]["parents"] = [
                    key_of(parent, root_names, known) for parent in operation["parents"]
                ]
                changed.append("parents")
            if operation.get("title"):
                nodes[key]["title"] = str(operation["title"]).lstrip("# ").strip()
                changed.append("title")
            if operation.get("body") is not None:
                nodes[key]["body"] = str(operation["body"])
                changed.append("body")
            nodes[key]["origin"] = "updated:" + "+".join(changed)
            summary["updated"].append(key)
    return nodes, summary


def problems(nodes: dict[str, dict]) -> list[str]:
    """What ``specspec check`` would report about the structure, as ``CODE node`` lines."""
    found = [
        f"TYPE {key}"
        for key, record in nodes.items()
        if key != ROOT and record["type"] not in ("requirement", "implementation")
    ]
    spec_nodes = [
        SpecNode(key, record["type"], list(record["parents"]), record["body"], f"{key}.md")
        for key, record in nodes.items()
        if key == ROOT or record["type"] in ("requirement", "implementation")
    ]
    _, diagnostics = build_graph(spec_nodes)
    return found + [f"{d.code} {d.node_id or ''}".strip() for d in diagnostics]


def children(nodes: dict[str, dict]) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {key: [] for key in nodes}
    for key, record in nodes.items():
        for parent in record["parents"]:
            if parent in found:
                found[parent].append(key)
    return found


def ancestors(nodes: dict[str, dict], key: str) -> set[str]:
    seen: set[str] = set()
    pending = list(nodes[key]["parents"]) if key in nodes else []
    while pending:
        current = pending.pop()
        if current not in seen and current in nodes:
            seen.add(current)
            pending.extend(nodes[current]["parents"])
    return seen


def depth(nodes: dict[str, dict]) -> int:
    """The longest path from the manifesto, cycles counted once."""
    memo: dict[str, int] = {}

    def longest(key: str, trail: tuple[str, ...]) -> int:
        if key in memo or key in trail:
            return memo.get(key, 0)
        parents = [parent for parent in nodes[key]["parents"] if parent in nodes]
        memo[key] = 1 + max(longest(p, (*trail, key)) for p in parents) if parents else 0
        return memo[key]

    return max((longest(key, ()) for key in nodes), default=0)


def build_order(nodes: dict[str, dict]) -> list[str]:
    """Keys of nodes whose text says when something gets built."""
    return [
        key
        for key, record in nodes.items()
        if BUILD_ORDER.search(record["title"] + ". " + record["body"])
    ]


def metrics(nodes: dict[str, dict]) -> dict[str, float]:
    below = children(nodes)
    requirements = [key for key, record in nodes.items() if record["type"] == "requirement"]
    words = [
        len(re.findall(r"\S+", nodes[key]["title"] + " " + nodes[key]["body"]))
        for key in requirements
    ]
    return {
        "nodes": len(nodes) - 1,
        "implementation nodes": sum(r["type"] == "implementation" for r in nodes.values()),
        "children of the manifesto": len(below.get(ROOT, [])),
        "depth": depth(nodes),
        "nodes with two or more parents": sum(len(r["parents"]) > 1 for r in nodes.values()),
        "words per requirement": round(sum(words) / len(words), 1) if words else 0,
    }


def outline(nodes: dict[str, dict], body_characters: int = 300) -> str:
    """An indented outline for reading; a node with several parents is shown in full once."""
    below = children(nodes)
    lines: list[str] = []
    shown: set[str] = set()

    def walk(key: str, indent: int) -> None:
        record = nodes[key]
        tag = "" if record["type"] == "requirement" else f"[{record['type']}] "
        origin = record.get("origin")
        mark = f" <{origin}>" if origin and origin != "base" else ""
        parents = ", ".join(record["parents"])
        head = f"{'  ' * indent}- {key}{mark} (parents: {parents}) {tag}# {record['title']}"
        if key in shown:
            lines.append(head + "  [shown above]")
            return
        shown.add(key)
        lines.append(head)
        body = " ".join(record["body"].split())
        if body:
            cut = "…" if len(body) > body_characters else ""
            lines.append(f"{'  ' * indent}    {body[:body_characters]}{cut}")
        for child in below.get(key, []):
            walk(child, indent + 1)

    walk(ROOT, 0)
    lines += [f"- [not reached] {key} # {nodes[key]['title']}" for key in nodes if key not in shown]
    return "\n".join(lines)


def dump(nodes: dict[str, dict]) -> str:
    """The graph as a grader reads it: every node with all its ancestors listed."""
    rows = []
    for key, record in nodes.items():
        if key == ROOT:
            continue
        row = {"key": key}
        if record.get("origin"):
            row["origin"] = record["origin"]
        row.update(
            type=record["type"],
            parents=record["parents"],
            ancestors=sorted(ancestors(nodes, key)),
            title=record["title"],
            body=record["body"],
        )
        rows.append(row)
    return json.dumps(rows, ensure_ascii=False, indent=1)
