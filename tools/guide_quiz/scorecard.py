"""A short scorecard: the behaviours the quizzes look for, each in plain words.

A row names one behaviour, says what the model was asked and what is counted, and takes
its figure from the criteria that ``report`` prints in full. A cell reads "17 of 20"
(answers or graphs that show the behaviour) or gives a mean with the number of answers
behind it. The first group holds what counts most: whether the agent tells intention
from conclusion.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import dilemmas, report

DRAWING = ("clinic", "bakery")
OTHER_TOPICS = ("structure", "phases", "commands", "routine", "writing")


@dataclass(frozen=True)
class Row:
    label: str
    meaning: str
    tasks: tuple[str, ...]  # empty for the dilemmas
    kind: str  # "pass", "counts", "numbers" or "dilemmas"
    keys: tuple[str, ...] = ()  # criteria; for the dilemmas, their topics


GROUPS: tuple[tuple[str, tuple[Row, ...]], ...] = (
    (
        "Telling intention from conclusion (what counts most)",
        (
            Row(
                "Your way and its intention become two nodes",
                "Two briefs have sentences such as 'an e-mail when the order is ready, so "
                "nobody waits for nothing'. Counted: how often the intention became a node of "
                "its own, in words that name no way, with your way beneath it. Each graph has "
                "two such sentences.",
                DRAWING,
                "counts",
                (
                    "an intention and the owner's way to it are two nodes",
                    "the same, with the intention also in the manifesto",
                ),
            ),
            Row(
                "An intention you left unsaid is worded above your way",
                "A third brief names ways without a reason, such as a sheet on the shed door. "
                "Counted: how often the agent worded what the way is for as a node of its own "
                "above it. Each graph has two such sentences.",
                ("toolshed",),
                "counts",
                ("an intention the owner left unsaid is a node above the owner's way",),
            ),
            Row(
                "The summary names the intentions it read into your words",
                "Same brief. Counted: summaries that tell you which intentions the agent "
                "worded itself, so that you can correct them.",
                ("toolshed",),
                "pass",
                ("the report names the intentions the agent read into the owner's words",),
            ),
            Row(
                "A conclusion in the manifesto's wording is pointed out",
                "The manifesto of that brief says 'a web app with a calendar view'. Counted: "
                "summaries that tell you the calendar view is one way among others and suggest "
                "a node beneath the manifesto for it, or ask whether it is fixed.",
                ("toolshed",),
                "pass",
                ("the report points out a conclusion in the manifesto's wording",),
            ),
            Row(
                "The same in a discussion",
                "The game's manifesto says the friends play 'on their own phones'. Counted: "
                "answers that tell you this is a way that could move beneath the manifesto, or "
                "ask whether it is fixed.",
                ("discuss-game",),
                "pass",
                ("it points out a conclusion in the manifesto's wording",),
            ),
            Row(
                "A statement that works against the manifesto is raised",
                "You describe a party game with secret roles and want a timeline of who did "
                "what on the TV. Counted: answers that tell you the timeline gives the roles "
                "away.",
                ("discuss-game",),
                "pass",
                ("it raises the statement that works against the manifesto",),
            ),
            Row(
                "It asks whether an unclear statement is fixed",
                "Same discussion; you say 'it should be written in Kotlin' without a reason. "
                "Counted: answers that ask whether Kotlin is fixed or open.",
                ("discuss-game",),
                "pass",
                ("it asks whether an unclear statement is fixed",),
            ),
            Row(
                "It says which statements it reads as fixed and which as open",
                "Both discussions. Counted: answers that say this for several of your statements.",
                ("discuss-game", "discuss"),
                "pass",
                ("it says which statements it reads as fixed and which as open",),
            ),
            Row(
                "The intention behind a way you stated is named",
                "The game discussion names three ways: a room code, a 90-second timer and the "
                "host's phone as the server. Counted: how often the answer says what the way "
                "is for and treats the way as one of several.",
                ("discuss-game",),
                "counts",
                ("the intention behind a stated way is named",),
            ),
            Row(
                "An intention is told apart from the way you named",
                "The bakery discussion. Counted: answers that separate at least one intention "
                "from the way you suggested for it, such as bakers knowing what to bake and "
                "the board on a screen.",
                ("discuss",),
                "pass",
                ("it tells an intention apart from the way the owner named",),
            ),
            Row(
                "The manifesto's intention is left alone",
                "The game discussion. Counted: answers that do not argue against secret "
                "roles or against playing together in one room.",
                ("discuss-game",),
                "pass",
                ("it leaves the manifesto's intention alone",),
            ),
            Row(
                "Right answer in short cases about intention and conclusion",
                "Eleven multiple-choice questions, such as what a node in the middle is and "
                "what happens beneath a node that is replaced. Share of answers that pick the "
                "keyed option.",
                (),
                "dilemmas",
                ("relation",),
            ),
        ),
    ),
    (
        "Drawing a graph from an owner's brief",
        (
            Row(
                "Own conclusions recorded per graph",
                "Nodes for what the brief left to the agent, such as how an order is found at "
                "the counter. More of them means the graph says more of what building needs.",
                DRAWING,
                "numbers",
                ("nodes that record a conclusion of the agent's own",),
            ),
            Row("Nodes per graph", "The size of the drawn graph.", DRAWING, "numbers", ("nodes",)),
            Row(
                "Graphs free of the old way",
                "Graphs whose nodes say what the product does, without 'no more phone calls' or "
                "'now ... instead of ...'.",
                DRAWING,
                "pass",
                ("no contrast with the past",),
            ),
            Row(
                "Graphs that keep a list of limits together",
                "The brief sets three limits in one sentence. Counted: graphs that state them in "
                "one or two nodes.",
                DRAWING,
                "pass",
                ("a list of limits is in at most two nodes",),
            ),
            Row(
                "Valid graphs",
                "Graphs in which specspec's own check finds no error and no warning.",
                (*DRAWING, "toolshed"),
                "pass",
                ("graph passes the structure check",),
            ),
        ),
    ),
    (
        "Your own hand edits (a bike-shop graph; six of nine edits have a planted problem)",
        (
            Row(
                "Problems found in your edits, of 6",
                "You ask the agent to have a look at your uncommitted edits. Counted: how many of "
                "the six planted problems it points out.",
                ("owner-edits-review",),
                "numbers",
                ("planted problems found",),
            ),
            Row(
                "Your words are committed before the questions",
                "Same situation. Counted: answers that first commit your edits as you wrote "
                "them, as 'Owner specspec changes:', and then put their points to you.",
                ("owner-edits-review",),
                "pass",
                ("the owner's edits are committed first, under the owner's title",),
            ),
            Row(
                "Your edits left as you wrote them, of 7",
                "You edit nodes and ask for something else in the same message. Counted: how many "
                "of your edits are unchanged after the agent's planning.",
                ("owner-edits-plan",),
                "numbers",
                ("owner's edits left as written, of 7",),
            ),
            Row(
                "Your words are committed before its own planning",
                "Same situation. Counted: answers whose first commit is 'Owner specspec changes:' "
                "with your edits, before a commit of the agent's own.",
                ("owner-edits-plan",),
                "pass",
                ("the owner's edits are committed first, under the owner's title",),
            ),
            Row(
                "Suggestions are left to you",
                "Same situation. Counted: answers whose summary names problems in your edits and "
                "asks you, instead of having changed them.",
                ("owner-edits-plan",),
                "pass",
                ("the report leaves the raised changes to the owner",),
            ),
            Row(
                "Problems raised in edits you committed yourself, of 6",
                "You committed your edits by hand and ask for something else. They are still open "
                "for review, so more is better. Counted: planted problems the summary raises.",
                ("manual-plan",),
                "numbers",
                ("planted problems raised in the report, of 6",),
            ),
        ),
    ),
    (
        "Sealed nodes (the same nodes beneath an agent planning commit)",
        (
            Row(
                "Sealed nodes left as they are, of 7",
                "You ask for something that has nothing to do with them. Counted: how many of the "
                "seven nodes are unchanged.",
                ("sealed-plan",),
                "numbers",
                ("sealed nodes left as written, of 7",),
            ),
            Row(
                "Summaries without a remark about sealed nodes",
                "Same situation. Counted: answers whose summary brings up none of the planted "
                "problems. Remarks here are the repeated nitpicking to be stopped.",
                ("sealed-plan",),
                "pass",
                ("the report makes no remark about the sealed nodes",),
            ),
            Row(
                "A sealed node is restructured when the request needs it",
                "You replace QR tags by NFC stickers; the sealed QR node blends the tag with "
                "what it is for. Counted: answers that give that intention a node of its own "
                "with the NFC sticker beneath it.",
                ("sealed-feature",),
                "pass",
                ("its intention is a node of its own above the NFC sticker",),
            ),
            Row(
                "A stray sentence in an old node stays where it is",
                "The agent adds a child beneath an old node that contains an out-of-place "
                "sentence. Counted: answers that leave the sentence there; a line about it in the "
                "summary is allowed.",
                ("revise",),
                "pass",
                ("the stray sentence in a committed node stays where it is",),
            ),
        ),
    ),
    (
        "Discussion before any planning (you describe what you want)",
        (
            Row(
                "Gives an overview of its understanding",
                "Counted: answers that say in a few lines how the agent understood you.",
                ("discuss", "discuss-game"),
                "pass",
                ("it gives an overview of its understanding",),
            ),
            Row(
                "Answers most of its own questions",
                "Counted: answers in which at least half of the questions come with the agent's "
                "tentative answer, so that you can simply agree.",
                ("discuss", "discuss-game"),
                "pass",
                ("it asks questions and answers most of them itself",),
            ),
        ),
    ),
    (
        "Commands and short cases",
        (
            Row(
                "All its command lines run",
                "The agent writes the specspec commands for three accepted changes and the tool "
                "runs them on a copy of the graph. Counted: answers in which every command works.",
                ("owner-edits-commands",),
                "pass",
                ("every editing command runs",),
            ),
            Row(
                "Right answer in the other short cases",
                "Multiple-choice questions about structure, phases, commands and wording. Share "
                "of answers that pick the keyed option.",
                (),
                "dilemmas",
                OTHER_TOPICS,
            ),
        ),
    ),
)


def cell(row: Row, scores: dict, answered: list[dict], model: str, guide: str) -> str:
    if row.kind == "dilemmas":
        topics = {item["id"]: item["topic"] for item in dilemmas.items()}
        mine = [
            r
            for r in answered
            if r["model"] == model and r["guide"] == guide and topics[r["item"]] in row.keys
        ]
        right = sum(r["correct"] for r in mine)
        return f"{round(100 * right / len(mine))} % of {len(mine)}" if mine else "-"
    group = [s for task in row.tasks for s in scores.get((task, model, guide), []) if s]
    if row.kind == "counts":
        pairs = [s["counts"][key] for s in group for key in row.keys if key in s["counts"]]
        total = sum(of for _, of in pairs)
        return f"{sum(done for done, _ in pairs)} of {total}" if total else "-"
    values = [s[row.kind][key] for s in group for key in row.keys if key in s[row.kind]]
    if not values:
        return "-"
    if row.kind == "pass":
        return f"{sum(values)} of {len(values)}"
    return f"{sum(values) / len(values):.1f} (n={len(values)})"


def table(scores: dict, answered: list[dict], model: str, guides: list[str]) -> str:
    """The scorecard for one model and the guides in the order given."""
    known = {item["id"] for item in dilemmas.items()}
    answered = list(
        report.latest(
            [r for r in answered if r.get("picked") is not None and r["item"] in known],
            lambda r: (r["model"], r["guide"], r["item"], r["repetition"]),
        ).values()
    )
    width = 62
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lines = [f"Scorecard for {report.short(model)}"]
    lines += [f"  {letter}: {guide}" for letter, guide in zip(letters, guides, strict=False)]
    for title, rows in GROUPS:
        head = "".join(f"{letter:>16}" for letter in letters[: len(guides)])
        lines += ["", title, " " * width + head]
        for row in rows:
            cells = [cell(row, scores, answered, model, guide) for guide in guides]
            lines.append(f"{row.label[:width]:{width}}" + "".join(f"{c:>16}" for c in cells))
    lines += ["", "What the rows mean"]
    for _, rows in GROUPS:
        lines += [f"- {row.label}: {row.meaning}" for row in rows]
    return "\n".join(lines)
