"""Open tasks: an owner's message that a model answers freely.

Each task has a brief in ``quizzes/NAME.md``. A task that is graded names a rubric file
and what its answer contains: a drawn graph (``nodes``), operations on the base graph of
the revision tasks, or plain text.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

FOLDER = Path(__file__).resolve().parent / "quizzes"


@dataclass(frozen=True)
class Task:
    name: str
    answer: str  # "graph", "operations", "commands" or "text"
    rubric: str | None = None  # stem of the rubric file; None for answers read by a person
    root_names: frozenset[str] = frozenset()
    about: str = ""
    base: str | None = None  # stem of the graph that operations apply to


TASKS = {
    task.name: task
    for task in (
        Task(
            "clinic",
            "graph",
            "clinic",
            frozenset({"Kq3x9bA="}),
            "Draw the graph for a physiotherapy practice's appointment app.",
        ),
        Task(
            "bakery",
            "graph",
            "bakery",
            frozenset({"Bk2rPm8="}),
            "Draw the graph for a bakery's pre-orders; no purpose is given in the manifesto.",
        ),
        Task(
            "toolshed",
            "graph",
            "toolshed",
            frozenset({"Tl8bRw4="}),
            "Draw the graph for a tool library; ways without a stated intention, and a "
            "manifesto with a conclusion in its wording.",
        ),
        Task(
            "revise",
            "operations",
            "revise",
            about="Replace a conclusion, add two more; an unrelated sentence sits in one node.",
            base="revise",
        ),
        Task(
            "revise-phones",
            "operations",
            "revise",
            about="As revise, with a request that most models read as keeping both views.",
            base="revise",
        ),
        Task("review", "text", "review", about="Review a graph with thirteen planted problems."),
        Task(
            "owner-edits",
            "text",
            "owner-edits",
            about="The owner edited nodes by hand; six edits have a planted problem.",
        ),
        Task(
            "owner-edits-review",
            "operations",
            "owner-edits-review",
            about="As owner-edits, answered with the commits made now and a report.",
            base="owner-edits",
        ),
        Task(
            "owner-edits-apply",
            "operations",
            about="The owner accepts three suggestions and declines three; then plan.",
            base="owner-edits",
        ),
        Task(
            "owner-edits-unanswered",
            "operations",
            about="The owner accepts three suggestions and leaves three unanswered; then plan.",
            base="owner-edits",
        ),
        Task(
            "owner-edits-commands",
            "commands",
            about="As owner-edits-apply, answered with specspec commands that are then run.",
            base="owner-edits",
        ),
        Task(
            "owner-edits-plan",
            "operations",
            "owner-edits-plan",
            about="The owner edited nodes by hand and asks for one more thing; then plan.",
            base="owner-edits",
        ),
        Task(
            "manual-plan",
            "operations",
            "manual-plan",
            about="The owner committed nodes by hand and asks for one more thing; then plan.",
            base="owner-edits",
        ),
        Task(
            "sealed-plan",
            "operations",
            "sealed-plan",
            about="The same nodes, sealed by an agent planning commit; the request is unrelated.",
            base="owner-edits",
        ),
        Task(
            "sealed-feature",
            "operations",
            about="A request needs a sealed node restructured: NFC stickers replace QR tags.",
            base="owner-edits",
        ),
        Task(
            "discuss",
            "text",
            "discuss",
            about="The bakery brief as a round of tandem planning: discuss, change nothing.",
        ),
        Task(
            "discuss-game",
            "text",
            "discuss-game",
            about="A party game in tandem planning: one statement works against the manifesto, "
            "one leaves open how firmly it holds.",
        ),
        Task(
            "explain-cases", "text", about="One node, siblings or parent and child, in own words."
        ),
        Task("explain-rules", "text", about="The structure rules the model will follow."),
    )
}


def brief(name: str) -> str:
    return (FOLDER / f"{name}.md").read_text(encoding="utf-8").replace("\r\n", "\n")


def mark(name: str) -> str:
    """Identifies the wording of a brief; every answer keeps the mark of the brief it got."""
    return hashlib.sha256(brief(name).encode("utf-8")).hexdigest()[:12]


def current(records: list[dict]) -> list[dict]:
    """The answers given to each brief as it reads now; an answer without a mark is kept."""
    marks = {name: mark(name) for name in TASKS}
    return [r for r in records if r.get("brief") in (None, marks.get(r.get("task")))]


def rubric(task: Task) -> str:
    return (FOLDER / f"{task.rubric}.rubric.md").read_text(encoding="utf-8").strip()


def parse(text: str | None) -> dict | None:
    """The JSON object of a reply, with or without a code fence.

    A reply whose brackets do not match is salvaged item by item: every node or
    operation, the list of commands and the report are decoded on their own.
    """
    if not text:
        return None
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    candidate = fenced.group(1) if fenced else text[text.find("{") : text.rfind("}") + 1]
    try:
        return json.loads(candidate, strict=False)
    except ValueError:
        pass
    decoder = json.JSONDecoder(strict=False)

    def decoded(pattern: str):
        marker = re.search(pattern, text)
        try:
            return decoder.raw_decode(text, marker.end())[0] if marker else None
        except ValueError:
            return text[marker.end() :] if pattern == REPORT else None

    found = []
    for match in re.finditer(r'\{\s*"(?:key|op)"\s*:', text):
        try:
            found.append(decoder.raw_decode(text, match.start())[0])
        except ValueError:
            continue
    name = "operations" if any("op" in item for item in found) else "nodes"
    if not found:
        name, found = "commands", decoded(r'"commands"\s*:\s*(?=\[)')
    if not found:
        return None
    salvaged = {name: found, "report": decoded(REPORT) or "", "salvaged": True}
    commits = decoded(r'"commits"\s*:\s*(?=\[)')
    return {**salvaged, "commits": commits} if isinstance(commits, list) else salvaged


REPORT = r'"report"\s*:\s*(?=")'
