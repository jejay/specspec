"""Open tasks: an owner's message that a model answers freely.

Each task has a brief in ``quizzes/NAME.md``. A task that is graded names a rubric file
and what its answer contains: a drawn graph (``nodes``), operations on the base graph of
the revision tasks, or plain text.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

FOLDER = Path(__file__).resolve().parent / "quizzes"


@dataclass(frozen=True)
class Task:
    name: str
    answer: str  # "graph", "operations" or "text"
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
            "revise",
            "operations",
            "revise",
            about="Replace a choice, add two decisions; an unrelated sentence sits in one node.",
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
            "owner-edits-apply",
            "operations",
            about="The owner accepts three suggestions and declines three; then plan.",
            base="owner-edits",
        ),
        Task("discuss", "text", about="The bakery brief as a discussion round; read by a person."),
        Task(
            "explain-cases", "text", about="One node, siblings or parent and child, in own words."
        ),
        Task("explain-rules", "text", about="The structure rules the model will follow."),
    )
}


def brief(name: str) -> str:
    return (FOLDER / f"{name}.md").read_text(encoding="utf-8").replace("\r\n", "\n")


def rubric(task: Task) -> str:
    return (FOLDER / f"{task.rubric}.rubric.md").read_text(encoding="utf-8").strip()


def parse(text: str | None) -> dict | None:
    """The JSON object of a reply, with or without a code fence.

    A reply whose brackets do not match is salvaged item by item: every node or
    operation and the report are decoded on their own.
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
    found = []
    for match in re.finditer(r'\{\s*"(?:key|op)"\s*:', text):
        try:
            found.append(decoder.raw_decode(text, match.start())[0])
        except ValueError:
            continue
    if not found:
        return None
    report = ""
    marker = re.search(r'"report"\s*:\s*(?=")', text)
    if marker:
        try:
            report = decoder.raw_decode(text, marker.end())[0]
        except ValueError:
            report = text[marker.end() :]
    name = "operations" if any("op" in item for item in found) else "nodes"
    return {name: found, "report": report, "salvaged": True}
