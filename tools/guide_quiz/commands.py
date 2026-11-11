"""Run the specspec commands of an answer on a throwaway copy of a base graph.

A task of this kind asks for the editing commands as a model would type them. Every line
is split into words the way a POSIX shell splits it and handed to specspec's own command
line in a process of its own. Only ``add``, ``update`` and ``delete`` run, and the project
is a temporary folder with the base graph committed in it.

Of the shell itself the quiz knows quoting, ``&&`` and ``;`` between commands, and
``NAME=$(specspec ...)``, which keeps what the command printed. A line that puts an
editing command into any other construct counts as a command that fails.
"""

from __future__ import annotations

import json
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

from specspec.format import serialize
from specspec.model import FORMAT_VERSION, SpecNode
from specspec.workspace import SPEC_DIR, load_snapshot

from . import graphs

GRADER = "specspec"  # the name under which a run is kept beside the graders' verdicts
EDITING = ("add", "update", "delete")
VARIABLE = re.compile(r"\$(?:\{(\w+)\}|([A-Za-z_]\w*))")
ASSIGNMENT = re.compile(r"\s*([A-Za-z_]\w*)=\$\((.*)\)\s*$", re.S)
EDITING_COMMAND = re.compile(r"\bspecspec\s+(?:add|update|delete)\b")
COMMIT = ("-c", "user.name=guide quiz", "-c", "user.email=quiz@example.invalid")
COMMIT += ("-c", "commit.gpgsign=false", "-c", "core.hooksPath=.no-hooks", "commit", "--quiet")
UNSUPPORTED = "The quiz runs plain specspec command lines only."


def words(line: str, variables: dict[str, str] | None = None) -> tuple[list[str], int]:
    """A command line as a POSIX shell passes it on, and how many unset variables it used.

    A ``$name`` outside single quotes is replaced by the variable's value. An unset one
    becomes nothing, as it does for an agent that forgets the quotes around a reference
    to a new node.
    """
    variables = variables or {}
    kept, unset, quote, position = [], 0, None, 0
    line = line.replace("\\\n", " ")
    while position < len(line):
        character = line[position]
        if character == "\\" and quote != "'" and position + 1 < len(line):
            kept.append(line[position : position + 2])
            position += 2
            continue
        if character in "'\"" and quote in (None, character):
            quote = None if quote else character
        reference = VARIABLE.match(line, position) if quote != "'" else None
        if reference:
            name = reference.group(1) or reference.group(2)
            value = variables.get(name, "")
            unset += name not in variables
            if quote:
                kept.append(re.sub(r'(["\\$`])', r"\\\1", value))
            else:
                kept.append(" ".join(shlex.quote(part) for part in value.split()))
            position = reference.end()
            continue
        kept.append(character)
        position += 1
    return shlex.split("".join(kept)), unset


def invocations(line: str, variables: dict[str, str] | None = None) -> tuple[list[list[str]], int]:
    """The specspec editing invocations of one line, each without the program's name."""
    found, unset = words(line, variables)
    groups: list[list[str]] = [[]]
    for word in found:
        if word in ("&&", ";"):
            groups.append([])
        else:
            groups[-1].append(word)
    editing = []
    for group in groups:
        if group[:3] in (["python", "-m", "specspec"], ["python3", "-m", "specspec"]):
            group = group[2:]
        if group[:1] == ["specspec"] and group[1:2] and group[1] in EDITING:
            editing.append(group[1:])
    return editing, unset


def project(name: str, folder: Path) -> None:
    """Write a base graph into an empty folder as node files and commit them."""
    records = json.loads((graphs.QUIZZES / f"{name}.graph.json").read_text(encoding="utf-8"))
    (folder / SPEC_DIR).mkdir()
    for record in records:
        path = f"{SPEC_DIR}/{record['id']}.md"
        text = f"# {record['title']}\n\n{record['body']}\n"
        version = FORMAT_VERSION if record["type"] == "manifesto" else None
        node = SpecNode(record["id"], record["type"], list(record["parents"]), text, path, version)
        (folder / path).write_bytes(serialize(node))
    for arguments in (("init", "--quiet"), ("add", "--all"), (*COMMIT, "-m", "Base graph")):
        subprocess.run(["git", *arguments], cwd=folder, check=True, capture_output=True)


def parts(text: str) -> tuple[str, str]:
    """The heading and the text below it."""
    first, _, rest = text.replace("\r\n", "\n").strip().partition("\n")
    return first.lstrip("# ").strip(), rest.strip()


def result(folder: Path, name: str) -> tuple[dict[str, dict], dict[str, list[str]], list[str]]:
    """The graph in a project, what changed against the base graph, and what check reports."""
    original, root_names = graphs.base(name)
    snapshot = load_snapshot(folder)
    nodes: dict[str, dict] = {}
    for found in snapshot.nodes:
        key = graphs.key_of(found.id, root_names)
        title, body = parts(found.body)
        parents = [graphs.key_of(parent, root_names) for parent in found.parents]
        nodes[key] = graphs.node(found.type, parents, title, body, "added")
    summary: dict[str, list[str]] = {
        "added": [key for key in nodes if key not in original],
        "updated": [],
        "deleted": [key for key in original if key not in nodes],
    }
    for key, record in nodes.items():
        if key in original:
            changed = [
                part for part in ("parents", "title", "body") if record[part] != original[key][part]
            ]
            record["origin"] = "updated:" + "+".join(changed) if changed else "base"
            summary["updated"] += [key] if changed else []
    errors = [d for d in snapshot.diagnostics if d.severity == "error"]
    return nodes, summary, [f"{d.code} {d.node_id or ''}".strip() for d in errors]


def specspec(folder: Path, arguments: list[str]) -> tuple[int, str, str]:
    """One invocation in the project: its exit code, what it printed, and that with errors."""
    command = [sys.executable, "-m", "specspec", "--root", str(folder), *arguments]
    try:
        done = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return 124, "", "The command did not end within two minutes."
    return done.returncode, done.stdout, done.stdout + done.stderr


def run(data: dict, name: str) -> dict:
    """What an answer's ``commands`` do to the base graph."""
    runs, ignored, unset = [], [], 0
    variables: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="guide-quiz-", ignore_cleanup_errors=True) as path:
        folder = Path(path)
        project(name, folder)
        for line in map(str, data.get("commands") or []):
            assignment = ASSIGNMENT.match(line)
            try:
                editing, missing = invocations(
                    assignment.group(2) if assignment else line, variables
                )
            except ValueError as problem:
                runs.append({"line": line, "exit": 2, "output": str(problem)})
                continue
            unset += missing
            printed = []
            for arguments in editing:
                exit_code, stdout, output = specspec(folder, arguments)
                printed.append(stdout)
                runs.append(
                    {"line": shlex.join(arguments), "exit": exit_code, "output": output[-600:]}
                )
            if assignment:
                variables[assignment.group(1)] = "\n".join(printed).strip()
            if not editing and EDITING_COMMAND.search(line):
                runs.append({"line": line, "exit": 2, "output": UNSUPPORTED})
            elif not editing:
                ignored.append(line)
        nodes, summary, problems = result(folder, name)
    return {
        "nodes": nodes,
        "summary": summary,
        "problems": problems,
        "runs": runs,
        "ignored": ignored,
        "expanded": unset,
    }
