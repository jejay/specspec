"""Grade open answers: what a grader model is asked, and how its verdict becomes criteria.

The grader sees the task, the answer and a rubric, and never which model or guide version
produced the answer. Whatever the tool can decide from the graph itself, it decides
without the grader: the structure check, ancestry and the scan for build order.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from . import graphs, tasks

GRADER = "claude-opus-5-5"


def context() -> str:
    """The grader's system prompt."""
    return (tasks.FOLDER / "grader.md").read_text(encoding="utf-8").strip()


def answer_id(task: str, text: str) -> str:
    """Names an answer independently of the run that produced it."""
    return hashlib.sha256((task + text).encode("utf-8")).hexdigest()[:16]


def prompt(task: tasks.Task, text: str) -> str | None:
    """What the grader reads for one answer; None when the answer cannot be read."""
    rubric, brief = tasks.rubric(task), tasks.brief(task.name)
    head = f"{rubric}\n\n<brief>\n{brief}\n</brief>\n\n"
    if task.answer == "text":
        return f"{head}<review>\n{text}\n</review>"
    data = tasks.parse(text)
    if not data:
        return None
    report = f"<report>\n{data.get('report', '')}\n</report>"
    if task.answer == "graph":
        nodes = graphs.drawn(data, set(task.root_names))
        return f"{head}<graph>\n{graphs.dump(nodes)}\n</graph>\n\n{report}"
    nodes, summary = graphs.revised(data, task.base)
    deleted = json.dumps(summary["deleted"])
    return (
        f"{head}<deleted_nodes>\n{deleted}\n</deleted_nodes>\n\n"
        f"<resulting_graph>\n{graphs.dump(nodes)}\n</resulting_graph>\n\n{report}"
    )


def yes(value) -> bool:
    return value is True or (isinstance(value, str) and value.strip().lower() == "true")


def found(nodes: dict, key) -> str | None:
    """A node key from a verdict, when the graph has that node."""
    return str(key) if key is not None and str(key) in nodes else None


@dataclass(frozen=True)
class Probes:
    """Where a drawing rubric keeps its findings, so that briefs share their criteria."""

    constraints: tuple[str, ...]  # the owner's constraints
    shaping: str  # the constraint that shaped a choice
    shaped: tuple[tuple[str, ...], ...]  # paths to the shaped node's key, best first
    suggested: str  # a technology the owner merely suggested
    splits: dict[str, bool]  # a "way, so that purpose" each; True: manifesto omits the purpose
    rule: str  # a rule that deserves a node of its own
    separate: str  # two needs that deserve a node each
    wording: str  # a choice the owner left to the agent


PROBES = {
    "clinic": Probes(
        constraints=("pg", "eu"),
        shaping="eu",
        shaped=(("sms_provider", "node"), ("reminder", "means_node")),
        suggested="sms_provider",
        splits={"reminder": False, "week": False},
        rule="double_booking_own_node",
        separate="paper_phone",
        wording="reminder_wording",
    ),
    "bakery": Probes(
        constraints=("pc", "lang"),
        shaping="lang",
        shaped=(("email_wording_node",), ("ready", "means_node")),
        suggested="mail_sender",
        splits={"ready": True, "board": True},
        rule="handout_once_own_node",
        separate="slip_phone",
        wording="email_wording",
    ),
}


def lookup(verdict: dict, path: tuple[str, ...]):
    value = verdict
    for part in path:
        value = value.get(part) if isinstance(value, dict) else None
    return value


def score_drawing(task: tasks.Task, data: dict, verdict: dict) -> dict:
    nodes = graphs.drawn(data, set(task.root_names))
    probes = PROBES[task.name]
    measured = graphs.metrics(nodes)
    constraint_nodes = {
        name: found(nodes, (verdict.get(name) or {}).get("node")) for name in probes.constraints
    }
    at_root = [
        bool(key) and yes(verdict[name].get("own_node")) and nodes[key]["parents"] == [graphs.ROOT]
        for name, key in constraint_nodes.items()
    ]
    shaping = constraint_nodes[probes.shaping]
    shaped = next(
        (key for path in probes.shaped if (key := found(nodes, lookup(verdict, path)))), None
    )
    suggested = verdict.get(probes.suggested) or {}
    suggested_node = found(nodes, suggested.get("node"))
    split = {
        name: yes((verdict.get(name) or {}).get("separate_nodes"))
        and bool((verdict.get(name) or {}).get("outcome_node"))
        and yes((verdict.get(name) or {}).get("outcome_text_free_of_means"))
        for name in probes.splits
    }
    limits = verdict.get("limits") or {}
    order = verdict.get("work_order") or {}
    report = verdict.get("report") or {}
    blended = verdict.get("blended_nodes") or []
    passed = {
        "graph passes the structure check": not graphs.problems(nodes),
        "no implementation node for unbuilt work": measured["implementation nodes"] == 0,
        "no build order in node text": not graphs.build_order(nodes),
        "constraints are nodes directly under the manifesto": all(at_root),
        "a choice descends from the constraint that shaped it": bool(shaping and shaped)
        and shaping in graphs.ancestors(nodes, shaped),
        "a suggested technology is a requirement of its own": yes(
            suggested.get("left_open_explicitly")
        )
        or (
            yes(suggested.get("own_node"))
            and bool(suggested_node)
            and nodes[suggested_node]["type"] == "requirement"
        ),
        "a rule of its own has a node of its own": yes(verdict.get(probes.rule)),
        "a list of limits is in at most two nodes": yes(limits.get("all_three_stated"))
        and len(limits.get("nodes") or []) <= 2,
        "separate needs have separate nodes": yes(
            (verdict.get(probes.separate) or {}).get("separate_nodes")
        ),
        "no work order, by the grader": not (
            order.get("order_nodes") or order.get("order_in_text")
        ),
        "no node is only a topic": not verdict.get("category_nodes"),
        "no contrast with the past": not verdict.get("historic_contrast"),
        "the manifesto's children are outcomes or constraints": not verdict.get(
            "root_children_means"
        ),
        "an open wording is decided or named as open": verdict.get(probes.wording)
        in ("decided", "left_open_stated"),
        "titles are statements": not verdict.get("label_titles"),
        "no node blends decisions": not blended,
        "the report names the agent's own choices": yes(report.get("names_own_choices")),
        "the report names open points": yes(report.get("names_open_points")),
    }
    clean = [split[name] for name, is_clean in probes.splits.items() if is_clean]
    stated = [split[name] for name, is_clean in probes.splits.items() if not is_clean]
    counts = {
        "an owner's way and its purpose are two nodes": [sum(clean), len(clean)],
        "the same, with the purpose also in the manifesto": [sum(stated), len(stated)],
    }
    numbers = {**measured, "nodes that blend decisions": len(blended)}
    return {"pass": passed, "counts": counts, "numbers": numbers}


def score_revision(task: tasks.Task, data: dict, verdict: dict) -> dict:
    nodes, summary = graphs.revised(data, task.base)
    outcome, grid, slots, colour = "Wk7fTq0=", "Gr1dCc4=", "Sl0tRw8=", "C0lrTy2="
    text_message, reminder, europe = "SmsDay6=", "Rm1ndR3=", "EuData9="
    day = verdict.get("day_list") or {}
    day_node = found(nodes, day.get("node"))
    confirm = verdict.get("yes") or {}
    mechanism = found(nodes, confirm.get("mechanism_node"))
    email = verdict.get("email") or {}
    email_node = found(nodes, email.get("node"))
    email_above = graphs.ancestors(nodes, email_node) if email_node else set()
    report = verdict.get("report") or {}
    colour_parents = nodes[colour]["parents"] if colour in nodes else []
    views = [key for key in (day_node, grid) if key and key in nodes]
    passed = {
        "resulting graph passes the structure check": not graphs.problems(nodes),
        "the outcome is kept and names no way": outcome in nodes
        and not yes(verdict.get("outcome_Wk7fTq0_text_names_means")),
        "the day list is a new node directly under the outcome": day.get("how") == "new_node"
        and bool(day_node)
        and outcome in nodes[day_node]["parents"],
        "the colour node is kept and applies to the day list": bool(colour_parents)
        and all(parent in nodes for parent in colour_parents)
        and (day_node in colour_parents or outcome in colour_parents),
        "no view hangs beneath the colour node": not any(
            colour in graphs.ancestors(nodes, key) for key in views
        ),
        "the reply is recorded in a new node": bool(confirm.get("nodes"))
        and not yes(confirm.get("only_appended_to_existing")),
        "the reply's purpose is an outcome of its own": yes(
            confirm.get("outcome_and_mechanism_separate")
        ),
        "the reply descends from the text-message node": bool(mechanism)
        and text_message in graphs.ancestors(nodes, mechanism) | {mechanism},
        "e-mail is a new node": yes(email.get("is_added_node")),
        "e-mail is under the reminder outcome and beside the text message": bool(email_node)
        and reminder in email_above
        and text_message not in email_above,
        "e-mail descends from the EU constraint": europe in email_above,
        "the unrelated sentence is split out or named": verdict.get("signin_sentence")
        in ("moved_to_own_node", "flagged_in_report"),
        "no contrast with the past": not verdict.get("historic_contrast"),
        "no implementation node for unbuilt work": not verdict.get("added_implementation_nodes"),
        "titles are statements": not verdict.get("label_titles"),
        "the report names open points": yes(report.get("names_open_points")),
    }
    if task.name == "revise":  # only this request drops the grid on every screen
        passed["the replaced choice is deleted"] = grid not in nodes
        passed["the report names the removed nodes"] = yes(report.get("names_removed_nodes"))
    numbers = {
        "nodes added": len(summary["added"]),
        "nodes updated": len(summary["updated"]),
        "nodes deleted": len(summary["deleted"]),
        "slot node kept": int(slots in nodes),
    }
    return {"pass": passed, "counts": {}, "numbers": numbers}


def score_review(task: tasks.Task, data: None, verdict: dict) -> dict:
    identified = {
        name: yes(value) for name, value in sorted((verdict.get("identified") or {}).items())
    }
    numbers = {
        "planted problems found": sum(identified.values()),
        "further points": len(verdict.get("other_points") or []),
        "wrong claims": len(verdict.get("wrong_claims") or []),
    }
    return {"pass": identified, "counts": {}, "numbers": numbers}


def score_owner_review(task: tasks.Task, data: None, verdict: dict) -> dict:
    """The structure review of the owner's edits: found problems and how they are put."""
    identified = {
        name: yes(value) for name, value in sorted((verdict.get("identified") or {}).items())
    }
    passed = {
        **identified,
        "the edit without a problem is left alone": yes(verdict.get("clean_edit_left_alone")),
        "the answer suggests and leaves the graph as it is": yes(verdict.get("suggests_only")),
        "it says that what is not accepted stays": yes(verdict.get("says_declined_stays")),
    }
    numbers = {
        "planted problems found": sum(identified.values()),
        "further suggestions": len(verdict.get("other_suggestions") or []),
        "wrong claims": len(verdict.get("wrong_claims") or []),
    }
    return {"pass": passed, "counts": {}, "numbers": numbers}


def score_owner_apply(task: tasks.Task, data: dict, verdict: dict) -> dict:
    """Planning after a structure review, decided from the returned operations alone.

    The owner accepted three suggestions (split the QR tag node, drop the work order,
    merge the three limits) and declined three (the invoice sentence, the wording of the
    text-message node, the parent of the warranty slip).
    """
    nodes, summary = graphs.revised(data, task.base)
    original, _ = graphs.base(task.base)
    commits = [str(title) for title in data.get("commits") or []]
    text = {key: f"{record['title']} {record['body']}" for key, record in nodes.items()}
    limits = ("Lm1Nte0=", "Lm2Prt4=", "Lm3Pht8=")
    tag_nodes = [key for key, words in text.items() if "qr" in words.lower()]
    tag_split = any(
        parent != graphs.ROOT and (parent == "Qr5Tag0=" or nodes[parent].get("origin") == "added")
        for key in tag_nodes
        for parent in nodes[key]["parents"]
        if parent in nodes
    )
    declined = {
        "declined: the invoice sentence stays where the owner put it": "Jb1Brd8=" in nodes
        and "Invoices are numbered per year." in nodes["Jb1Brd8="]["body"],
        "declined: the text-message node keeps the owner's words": "Sm5Txt4=" in nodes
        and nodes["Sm5Txt4="]["body"] == original["Sm5Txt4="]["body"]
        and nodes["Sm5Txt4="]["title"] == original["Sm5Txt4="]["title"],
        "declined: the warranty slip stays under the card view": "Wr8Nty0=" in nodes
        and nodes["Wr8Nty0="]["parents"] == ["Jb1Brd8="],
    }
    accepted = {
        "accepted: the QR tag hangs beneath its purpose": tag_split,
        "accepted: the work order is gone from the graph": "St3Pln8=" not in nodes,
        "accepted: the three limits are one node": sum(key in nodes for key in limits) <= 1
        and any(all(part in words for part in ("500", "20", "10 MB")) for words in text.values()),
    }
    passed = {
        "resulting graph passes the structure check": not graphs.problems(nodes),
        "the owner's edits are committed first, under the owner's title": bool(commits)
        and commits[0].startswith("Owner specspec changes:"),
        "the agent's changes follow under the agent's title": len(commits) > 1
        and commits[1].startswith("Agent specspec changes:"),
        **declined,
        **accepted,
        "the edit without a problem is untouched": nodes.get("Du2Srt4=") == original["Du2Srt4="],
    }
    numbers = {
        "declined suggestions left as written": sum(declined.values()),
        "accepted suggestions carried out": sum(accepted.values()),
        "nodes added": len(summary["added"]),
        "nodes deleted": len(summary["deleted"]),
    }
    return {"pass": passed, "counts": {}, "numbers": numbers}


SCORERS = {"clinic": score_drawing, "bakery": score_drawing, "review": score_review}
SCORERS.update({"revise": score_revision, "revise-phones": score_revision})
SCORERS.update({"owner-edits": score_owner_review, "owner-edits-apply": score_owner_apply})
# Scored from the answer alone, without a grader.
AUTOMATIC = frozenset({"owner-edits-apply"})


def score(task: tasks.Task, text: str, verdict: dict | None = None) -> dict | None:
    """Criteria for one answer; None when the answer cannot be read."""
    data = None if task.answer == "text" else tasks.parse(text)
    if task.answer != "text" and not data:
        return None
    return SCORERS[task.name](task, data, verdict or {})
