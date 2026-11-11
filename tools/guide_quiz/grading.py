"""Grade open answers: what a grader model is asked, and how its verdict becomes criteria.

The grader sees the task, the answer and a rubric, and never which model or guide version
produced the answer. Whatever the tool can decide from the graph itself, it decides
without the grader: the structure check, ancestry and the scan for build order.
"""

from __future__ import annotations

import hashlib
import json
import re
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


def pick(verdict: dict, *names: str):
    """The first of several fields that a verdict holds; earlier rubrics used earlier names."""
    return next((verdict[name] for name in names if name in verdict), None)


def separated(probe: dict | None) -> bool:
    """Whether an intention and the way to it are two nodes, the intention's text free of it."""
    probe = probe or {}
    return (
        yes(probe.get("separate_nodes"))
        and bool(pick(probe, "intention_node", "outcome_node"))
        and yes(pick(probe, "intention_text_free_of_way", "outcome_text_free_of_means"))
    )


def near_root(nodes: dict, key: str | None) -> bool:
    """Directly under the manifesto, or under nodes that are: the owner's reason may sit between."""
    return bool(key) and all(
        parent == graphs.ROOT or nodes.get(parent, {}).get("parents") == [graphs.ROOT]
        for parent in nodes[key]["parents"]
    )


def whole(verdict: dict, name: str) -> int:
    """A count from a verdict; anything that is no number counts as zero."""
    value = verdict.get(name)
    return int(value) if isinstance(value, int | float) else 0


@dataclass(frozen=True)
class Probes:
    """Where a drawing rubric keeps its findings, so that briefs share their criteria."""

    constraints: tuple[str, ...]  # the owner's constraints
    shaping: str  # the constraint that shaped a conclusion
    shaped: tuple[tuple[str, ...], ...]  # paths to the shaped node's key, best first
    suggested: str  # a technology the owner merely suggested
    splits: dict[str, bool]  # a "way, so that intention" each; True: manifesto omits it
    rule: str  # a rule that deserves a node of its own
    separate: str  # two needs that deserve a node each
    wording: str  # a wording the owner left to the agent


PROBES = {
    "clinic": Probes(
        constraints=("pg", "eu"),
        shaping="eu",
        shaped=(("sms_provider", "node"), ("reminder", "way_node"), ("reminder", "means_node")),
        suggested="sms_provider",
        splits={"reminder": False, "week": False},
        rule="double_booking_own_node",
        separate="paper_phone",
        wording="reminder_wording",
    ),
    "bakery": Probes(
        constraints=("pc", "lang"),
        shaping="lang",
        shaped=(("email_wording_node",), ("ready", "way_node"), ("ready", "means_node")),
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
    own = {name: yes((verdict.get(name) or {}).get("own_node")) for name in constraint_nodes}
    at_root = [
        own[name] and bool(key) and nodes[key]["parents"] == [graphs.ROOT]
        for name, key in constraint_nodes.items()
    ]
    near = [own[name] and near_root(nodes, key) for name, key in constraint_nodes.items()]
    shaping = constraint_nodes[probes.shaping]
    shaped = next(
        (key for path in probes.shaped if (key := found(nodes, lookup(verdict, path)))), None
    )
    suggested = verdict.get(probes.suggested) or {}
    suggested_node = found(nodes, suggested.get("node"))
    split = {name: separated(verdict.get(name)) for name in probes.splits}
    limits = verdict.get("limits") or {}
    order = verdict.get("work_order") or {}
    report = verdict.get("report") or {}
    blended = verdict.get("blended_nodes") or []
    passed = {
        "graph passes the structure check": not graphs.problems(nodes),
        "no implementation node for unbuilt work": measured["implementation nodes"] == 0,
        "no build order in node text": not graphs.build_order(nodes),
        "what the owner holds as fixed is a node of its own near the root": all(near),
        "the same, directly under the manifesto": all(at_root),
        "a conclusion descends from the constraint that shaped it": bool(shaping and shaped)
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
        "no way that could be another hangs directly under the manifesto": not pick(
            verdict, "root_children_ways", "root_children_means"
        ),
        "an open wording is decided or named as open": verdict.get(probes.wording)
        in ("decided", "left_open_stated"),
        "titles are statements": not verdict.get("label_titles"),
        "no node blends statements that could be replaced separately": not blended,
        "the report names the agent's own conclusions": yes(
            pick(report, "names_own_conclusions", "names_own_choices")
        ),
        "the report names open points": yes(report.get("names_open_points")),
    }
    if "names_read_intentions" in report:  # asked since the rubric looks for it
        passed["the report names the intentions the agent read into the owner's words"] = yes(
            report["names_read_intentions"]
        )
    clean = [split[name] for name, is_clean in probes.splits.items() if is_clean]
    stated = [split[name] for name, is_clean in probes.splits.items() if not is_clean]
    counts = {
        "an intention and the owner's way to it are two nodes": [sum(clean), len(clean)],
        "the same, with the intention also in the manifesto": [sum(stated), len(stated)],
    }
    numbers = {
        **measured,
        "nodes that state the limits": len(limits.get("nodes") or []),
        "nodes that blend statements": len(blended),
    }
    if {"own_conclusion_nodes", "own_choice_nodes"} & set(verdict):  # asked since counted
        own = pick(verdict, "own_conclusion_nodes", "own_choice_nodes") or []
        kept = {found(nodes, key) for key in own} - {None}
        numbers["nodes that record a conclusion of the agent's own"] = len(kept)
    return {"pass": passed, "counts": counts, "numbers": numbers}


# Ways in the tool-library brief; True where the owner says nothing of what the way is for.
UNSAID = {"scan": True, "sheet": True, "due": False, "broken": False}


def score_toolshed(task: tasks.Task, data: dict, verdict: dict) -> dict:
    """A brief whose owner names ways and leaves most intentions unsaid.

    Two ways come without a word about what they are for, one has its intention in the
    manifesto and one states it. The manifesto's wording holds a conclusion, a calendar
    view, and one sentence leaves open how firmly it holds.
    """
    nodes = graphs.drawn(data, set(task.root_names))
    measured = graphs.metrics(nodes)
    split = {name: separated(verdict.get(name)) for name in UNSAID}
    server = verdict.get("server") or {}
    server_node = found(nodes, server.get("node"))
    vue = verdict.get("vue") or {}
    limits = verdict.get("limits") or {}
    order = verdict.get("work_order") or {}
    report = verdict.get("report") or {}
    passed = {
        "graph passes the structure check": not graphs.problems(nodes),
        "no implementation node for unbuilt work": measured["implementation nodes"] == 0,
        "what the owner holds as fixed is a node of its own near the root": yes(
            server.get("own_node")
        )
        and near_root(nodes, server_node),
        "the report says how it read a statement of unclear firmness": vue.get("reading")
        == "asked_or_flagged",
        "the report names the intentions the agent read into the owner's words": yes(
            report.get("names_read_intentions")
        ),
        "the report points out a conclusion in the manifesto's wording": yes(
            report.get("points_out_manifesto_conclusion")
        ),
        "a rule of its own has a node of its own": yes(verdict.get("safety_own_node")),
        "a list of limits is in at most two nodes": yes(limits.get("all_three_stated"))
        and len(limits.get("nodes") or []) <= 2,
        "no work order, by the grader": not (
            order.get("order_nodes") or order.get("order_in_text")
        ),
        "no contrast with the past": not verdict.get("historic_contrast"),
        "the report names the agent's own conclusions": yes(report.get("names_own_conclusions")),
        "the report names open points": yes(report.get("names_open_points")),
    }
    unsaid = [split[name] for name, silent in UNSAID.items() if silent]
    said = [split[name] for name, silent in UNSAID.items() if not silent]
    counts = {
        "an intention the owner left unsaid is a node above the owner's way": [
            sum(unsaid),
            len(unsaid),
        ],
        "the same, with the intention in the manifesto or in the owner's sentence": [
            sum(said),
            len(said),
        ],
    }
    own = {found(nodes, key) for key in verdict.get("own_conclusion_nodes") or []} - {None}
    numbers = {
        **measured,
        "nodes that state the limits": len(limits.get("nodes") or []),
        "nodes that record a conclusion of the agent's own": len(own),
    }
    return {"pass": passed, "counts": counts, "numbers": numbers}


def score_revision(task: tasks.Task, data: dict, verdict: dict) -> dict:
    nodes, summary = graphs.revised(data, task.base)
    seen, grid, slots, colour = "Wk7fTq0=", "Gr1dCc4=", "Sl0tRw8=", "C0lrTy2="
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
        "the intention is kept and names no way": seen in nodes
        and not yes(
            pick(verdict, "intention_Wk7fTq0_text_names_way", "outcome_Wk7fTq0_text_names_means")
        ),
        "the day list is a new node directly under that intention": day.get("how") == "new_node"
        and bool(day_node)
        and seen in nodes[day_node]["parents"],
        "the colour node is kept and applies to the day list": bool(colour_parents)
        and all(parent in nodes for parent in colour_parents)
        and (day_node in colour_parents or seen in colour_parents),
        "no view hangs beneath the colour node": not any(
            colour in graphs.ancestors(nodes, key) for key in views
        ),
        "the reply is recorded in a new node": bool(confirm.get("nodes"))
        and not yes(confirm.get("only_appended_to_existing")),
        "the reply's intention is a node of its own": yes(
            pick(confirm, "intention_and_mechanism_separate", "outcome_and_mechanism_separate")
        ),
        "the reply descends from the text-message node": bool(mechanism)
        and text_message in graphs.ancestors(nodes, mechanism) | {mechanism},
        "e-mail is a new node": yes(email.get("is_added_node")),
        "e-mail is under the reminder intention and beside the text message": bool(email_node)
        and reminder in email_above
        and text_message not in email_above,
        "e-mail descends from the EU constraint": europe in email_above,
        "the stray sentence in a committed node stays where it is": verdict.get("signin_sentence")
        in ("left_unmentioned", "flagged_in_report"),
        "no contrast with the past": not verdict.get("historic_contrast"),
        "no implementation node for unbuilt work": not verdict.get("added_implementation_nodes"),
        "titles are statements": not verdict.get("label_titles"),
        "the report names open points": yes(report.get("names_open_points")),
    }
    if task.name == "revise":  # only this request drops the grid on every screen
        passed["the replaced conclusion is deleted"] = grid not in nodes
        passed["the report names the removed nodes"] = yes(report.get("names_removed_nodes"))
    numbers = {
        "nodes added": len(summary["added"]),
        "nodes updated": len(summary["updated"]),
        "nodes deleted": len(summary["deleted"]),
        "slot node kept": int(slots in nodes),
        "share of reports that mention the stray sentence": int(
            verdict.get("signin_sentence") == "flagged_in_report"
        ),
    }
    return {"pass": passed, "counts": {}, "numbers": numbers}


def score_review(task: tasks.Task, data: str, verdict: dict) -> dict:
    identified = {
        name: yes(value) for name, value in sorted((verdict.get("identified") or {}).items())
    }
    numbers = {
        "planted problems found": sum(identified.values()),
        "further points": len(verdict.get("other_points") or []),
        "wrong claims": len(verdict.get("wrong_claims") or []),
    }
    return {"pass": identified, "counts": {}, "numbers": numbers}


def score_discussion(task: tasks.Task, data: str, verdict: dict) -> dict:
    """A round of tandem planning: the answer discusses the product and changes nothing."""

    passed = {
        "the answer leaves the graph as it is": yes(verdict.get("leaves_graph")),
        "it talks about the product rather than about nodes": yes(verdict.get("about_product")),
        "it gives an overview of its understanding": yes(verdict.get("overview")),
        "it tells an intention apart from the way the owner named": yes(
            pick(verdict, "separates_intention_from_conclusion", "separates_want_from_way")
        ),
        "it challenges a conclusion the owner suggested": yes(
            pick(verdict, "challenges_a_conclusion", "challenges_a_choice")
        ),
        "it proposes conclusions of its own": yes(verdict.get("own_conclusions")),
        "it asks questions and answers most of them itself": answers_own_questions(verdict),
    }
    if "says_how_it_reads" in verdict:  # asked since the rubric looks for it
        passed["it says which statements it reads as fixed and which as open"] = yes(
            verdict["says_how_it_reads"]
        )
    return {"pass": passed, "counts": {}, "numbers": discussion_numbers(data, verdict)}


def answers_own_questions(verdict: dict) -> bool:
    asked = whole(verdict, "questions")
    return asked > 0 and 2 * whole(verdict, "questions_with_own_answer") >= asked


def discussion_numbers(data: str, verdict: dict) -> dict:
    return {
        "words": len(data.split()),
        "questions": whole(verdict, "questions"),
        "questions with a tentative answer": whole(verdict, "questions_with_own_answer"),
        "wrong claims": len(verdict.get("wrong_claims") or []),
    }


# Ways in the party-game brief whose intention the owner states or implies.
GAME_WAYS = ("room_code", "timer", "host_phone")


def score_game(task: tasks.Task, data: str, verdict: dict) -> dict:
    """Tandem planning with three planted statements.

    A timeline of who did what works against the manifesto's secret roles, "written in
    Kotlin" leaves open how firmly it holds, and working without internet is fixed by the
    place while the host's phone as the server is one way to it. The manifesto's wording
    holds a way too, the players' own phones.
    """
    timeline = verdict.get("timeline") or {}
    named = verdict.get("intentions_named") or {}
    passed = {
        "the answer leaves the graph as it is": yes(verdict.get("leaves_graph")),
        "it gives an overview of its understanding": yes(verdict.get("overview")),
        "it raises the statement that works against the manifesto": yes(
            timeline.get("raises_conflict")
        ),
        "it proposes another conclusion for that intention": yes(
            timeline.get("proposes_alternative")
        ),
        "it asks whether an unclear statement is fixed": verdict.get("kotlin") == "asks",
        "it asks that, or says how it reads the statement": verdict.get("kotlin")
        in ("asks", "states_reading"),
        "it keeps what the circumstances fix": verdict.get("offline") == "kept",
        "it leaves the manifesto's intention alone": not yes(verdict.get("challenges_manifesto")),
        "it points out a conclusion in the manifesto's wording": yes(
            verdict.get("manifesto_wording")
        ),
        "it says which statements it reads as fixed and which as open": yes(
            verdict.get("says_how_it_reads")
        ),
        "it proposes conclusions of its own": yes(verdict.get("own_conclusions")),
        "it asks questions and answers most of them itself": answers_own_questions(verdict),
    }
    counts = {
        "the intention behind a stated way is named": [
            sum(yes(named.get(way)) for way in GAME_WAYS),
            len(GAME_WAYS),
        ]
    }
    return {"pass": passed, "counts": counts, "numbers": discussion_numbers(data, verdict)}


def score_owner_review(task: tasks.Task, data: str | dict, verdict: dict) -> dict:
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
    if isinstance(data, dict):  # the review as a dry run: commits, operations, report
        _, summary = graphs.revised(data, task.base)
        commits = [str(title) for title in data.get("commits") or []]
        passed = {
            "the owner's edits are committed first, under the owner's title": bool(commits)
            and commits[0].startswith("Owner specspec changes:"),
            "no commit of the agent's own before the owner answers": not any(
                title.startswith("Agent specspec changes:") for title in commits
            ),
            "the graph is left as it is": not any(
                summary[kind] for kind in ("added", "updated", "deleted")
            ),
            **passed,
        }
    numbers = {
        "planted problems found": sum(identified.values()),
        "further suggestions": len(verdict.get("other_suggestions") or []),
        "wrong claims": len(verdict.get("wrong_claims") or []),
    }
    return {"pass": passed, "counts": {}, "numbers": numbers}


def score_owner_apply(task: tasks.Task, data: dict, verdict: dict) -> dict:
    """Planning after a structure review, decided from the resulting graph alone.

    The owner accepted three suggestions (split the QR tag node, drop the work order,
    merge the three limits). The other three (the invoice sentence, the wording of the
    text-message node, the parent of the warranty slip) the owner declined in one task
    and left unanswered in the other; either way they stay as the owner wrote them. An
    answer in commands is judged on the graph that their run left behind.
    """
    left = "unanswered" if task.name == "owner-edits-unanswered" else "declined"
    ran = task.answer == "commands"
    if ran:
        nodes = verdict.get("nodes") or {}
        summary = {"added": [], "deleted": [], **(verdict.get("summary") or {})}
    else:
        nodes, summary = graphs.revised(data, task.base)
    original, _ = graphs.base(task.base)
    commits = [str(title) for title in data.get("commits") or []]
    runs = verdict.get("runs") or []
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
        f"{left}: the invoice sentence stays where the owner put it": "Jb1Brd8=" in nodes
        and "Invoices are numbered per year." in nodes["Jb1Brd8="]["body"],
        f"{left}: the text-message node keeps the owner's words": "Sm5Txt4=" in nodes
        and nodes["Sm5Txt4="]["body"] == original["Sm5Txt4="]["body"]
        and nodes["Sm5Txt4="]["title"] == original["Sm5Txt4="]["title"],
        f"{left}: the warranty slip stays under the card view": "Wr8Nty0=" in nodes
        and nodes["Wr8Nty0="]["parents"] == ["Jb1Brd8="],
    }
    accepted = {
        "accepted: the QR tag hangs beneath its purpose": tag_split,
        "accepted: the work order is gone from the graph": "St3Pln8=" not in nodes,
        "accepted: the three limits are one node": sum(key in nodes for key in limits) <= 1
        and any(all(part in words for part in ("500", "20", "10 MB")) for words in text.values()),
    }
    if ran:
        passed = {
            "every editing command runs": bool(runs) and all(run["exit"] == 0 for run in runs),
            "specspec check passes on the resulting graph": bool(nodes)
            and not verdict.get("problems"),
        }
    else:
        passed = {
            "resulting graph passes the structure check": not graphs.problems(nodes),
            "the owner's edits are committed first, under the owner's title": bool(commits)
            and commits[0].startswith("Owner specspec changes:"),
            "the agent's changes follow under the agent's title": len(commits) > 1
            and commits[1].startswith("Agent specspec changes:"),
        }
    passed |= {
        **declined,
        **accepted,
        "the edit without a problem is untouched": nodes.get("Du2Srt4=") == original["Du2Srt4="],
    }
    numbers = {
        f"{left} suggestions left as written": sum(declined.values()),
        "accepted suggestions carried out": sum(accepted.values()),
        "nodes added": len(summary["added"]),
        "nodes deleted": len(summary["deleted"]),
    }
    if ran:
        numbers |= {
            "editing invocations": len(runs),
            "invocations that fail": sum(run["exit"] != 0 for run in runs),
            "references to new nodes that a shell expands": verdict.get("expanded", 0),
        }
    return {"pass": passed, "counts": {}, "numbers": numbers}


def score_owner_plan(task: tasks.Task, data: dict, verdict: dict) -> dict:
    """Planning a new request beside nodes with planted problems.

    The owner asked for payment by card and for the specification to be changed. In one
    task the flawed nodes are the owner's uncommitted edits, in one the owner committed
    them by hand, in one an agent planning commit has sealed them. They stay as written
    every time. Open nodes get suggestions in the report; sealed ones get no remark,
    because the request has nothing to do with them. The graph is judged from the
    operations and the report by the grader.
    """
    situation = {"manual-plan": "manual", "sealed-plan": "sealed"}.get(task.name, "open")
    nodes, summary = graphs.revised(data, task.base)
    original, _ = graphs.base(task.base)
    commits = [str(title) for title in data.get("commits") or []]

    def written(*keys: str) -> bool:
        return all(
            key in nodes
            and all(
                nodes[key][part] == original[key][part] for part in ("title", "body", "parents")
            )
            for key in keys
        )

    kept = {
        "as written: the QR tag node": written("Qr5Tag0="),
        "as written: the card view with the invoice sentence": written("Jb1Brd8="),
        "as written: the text-message node": written("Sm5Txt4="),
        "as written: the node about the order of work": written("St3Pln8="),
        "as written: the three limit nodes": written("Lm1Nte0=", "Lm2Prt4=", "Lm3Pht8="),
        "as written: the warranty slip under the card view": written("Wr8Nty0="),
        "as written: the edit without a problem": written("Du2Srt4="),
    }
    added = [f"{nodes[key]['title']} {nodes[key]['body']}".lower() for key in summary["added"]]
    raised = [yes(value) for value in (verdict.get("raised") or {}).values()]
    passed = {"resulting graph passes the structure check": not graphs.problems(nodes)}
    if situation == "open":
        passed |= {
            "the owner's edits are committed first, under the owner's title": bool(commits)
            and commits[0].startswith("Owner specspec changes:"),
            "the agent's changes follow under the agent's title": len(commits) > 1
            and commits[1].startswith("Agent specspec changes:"),
        }
    else:
        passed |= {
            "the planning is committed under the agent's title": any(
                title.startswith("Agent specspec changes:") for title in commits
            ),
            "no commit is made in the owner's name": not any(
                title.startswith("Owner specspec changes:") for title in commits
            ),
        }
    passed |= {
        "payment by card is a new node": any("card" in text and "pay" in text for text in added),
        **kept,
    }
    if situation == "sealed":
        passed["the report makes no remark about the sealed nodes"] = not any(raised)
    else:
        passed |= {
            "the report raises at least one of the planted problems": any(raised),
            "the report leaves the raised changes to the owner": yes(
                verdict.get("asks_before_changing")
            ),
        }
    if situation == "open":
        passed["the report says that the owner's edits are kept"] = yes(
            verdict.get("says_edits_kept")
        )
    labels = {
        "open": (
            "owner's edits left as written, of 7",
            "planted problems raised in the report, of 6",
        ),
        "manual": (
            "owner's nodes left as written, of 7",
            "planted problems raised in the report, of 6",
        ),
        "sealed": (
            "sealed nodes left as written, of 7",
            "remarks about sealed nodes in the report, of 6",
        ),
    }[situation]
    numbers = {
        labels[0]: sum(kept.values()),
        labels[1]: sum(raised),
        "nodes added": len(summary["added"]),
        "nodes updated": len(summary["updated"]),
        "nodes deleted": len(summary["deleted"]),
        "wrong claims": len(verdict.get("wrong_claims") or []),
    }
    return {"pass": passed, "counts": {}, "numbers": numbers}


def score_sealed_feature(task: tasks.Task, data: dict, verdict: dict) -> dict:
    """A request that needs a sealed node restructured: NFC stickers replace the QR tags.

    The sealed node blends the QR tag with its intention. The best graph gives the
    intention a node of its own with the NFC sticker beneath it, and every other sealed
    node stays as it is. Decided from the operations alone.
    """
    nodes, summary = graphs.revised(data, task.base)
    original, _ = graphs.base(task.base)
    text = {key: f"{record['title']} {record['body']}".lower() for key, record in nodes.items()}
    stickers = [key for key, words in text.items() if "nfc" in words]
    beneath_purpose = any(
        parent in nodes
        and parent != graphs.ROOT
        and "nfc" not in text[parent]
        and PURPOSE.search(text[parent]) is not None
        for key in stickers
        for parent in nodes[key]["parents"]
    )

    def written(*keys: str) -> bool:
        return all(nodes.get(key) == original[key] for key in keys)

    others = {
        "the card view": written("Jb1Brd8="),
        "the text-message node": written("Sm5Txt4="),
        "the node about the order of work": written("St3Pln8="),
        "the three limit nodes": written("Lm1Nte0=", "Lm2Prt4=", "Lm3Pht8="),
        "the warranty slip": written("Wr8Nty0="),
        "the overdue rule": written("Du2Srt4="),
    }
    passed = {
        "resulting graph passes the structure check": not graphs.problems(nodes),
        "the NFC sticker is recorded": bool(stickers),
        "its intention is a node of its own above the NFC sticker": beneath_purpose,
        "the QR tag is gone from the graph": not any("qr" in words for words in text.values()),
        "every other sealed node stays as written": all(others.values()),
        "the report names the sealed node it changed": "qr" in str(data.get("report")).lower(),
    }
    numbers = {
        "other sealed nodes left as written, of 6": sum(others.values()),
        "nodes added": len(summary["added"]),
        "nodes updated": len(summary["updated"]),
        "nodes deleted": len(summary["deleted"]),
    }
    return {"pass": passed, "counts": {}, "numbers": numbers}


# Words by which a node states why bikes carry a tag at all.
PURPOSE = re.compile(r"mix|confus|apart|identif|wrong bike|belongs to")
SCORERS = {"clinic": score_drawing, "bakery": score_drawing, "review": score_review}
SCORERS["owner-edits-plan"] = SCORERS["manual-plan"] = score_owner_plan
SCORERS["sealed-plan"] = score_owner_plan
SCORERS["sealed-feature"] = score_sealed_feature
SCORERS["discuss"] = score_discussion
SCORERS["discuss-game"] = score_game
SCORERS["toolshed"] = score_toolshed
SCORERS.update({"revise": score_revision, "revise-phones": score_revision})
SCORERS.update({"owner-edits": score_owner_review, "owner-edits-apply": score_owner_apply})
SCORERS["owner-edits-review"] = score_owner_review
SCORERS["owner-edits-unanswered"] = SCORERS["owner-edits-commands"] = score_owner_apply
# Scored from the answer alone, without a grader.
AUTOMATIC = frozenset({"owner-edits-apply", "owner-edits-unanswered", "sealed-feature"})


def judged(task: tasks.Task) -> bool:
    """Whether an answer needs a verdict: a grader's, or the run of its commands."""
    return bool(task.rubric) or task.answer == "commands"


def score(task: tasks.Task, text: str, verdict: dict | None = None) -> dict | None:
    """Criteria for one answer; None when the answer cannot be read."""
    data = text if task.answer == "text" else tasks.parse(text)
    if not data:
        return None
    return SCORERS[task.name](task, data, verdict or {})
