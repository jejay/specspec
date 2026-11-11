"""A short scorecard: the behaviours the quizzes look for, each in plain words.

A row names one behaviour, says what the model was asked and what is counted, and takes
its figure from the criteria that ``report`` prints in full. A cell reads "17 of 20"
(answers or graphs that show the behaviour) or gives a mean with the number of answers
behind it.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import dilemmas, report

DRAWING = ("clinic", "bakery")


@dataclass(frozen=True)
class Row:
    label: str
    meaning: str
    tasks: tuple[str, ...]  # empty for the dilemmas
    kind: str  # "pass", "counts", "numbers" or "dilemmas"
    keys: tuple[str, ...] = ()


GROUPS: tuple[tuple[str, tuple[Row, ...]], ...] = (
    (
        "Drawing a graph from an owner's brief (two briefs)",
        (
            Row(
                "A way and its purpose become two nodes",
                "The brief has sentences such as 'an e-mail when the order is ready, so nobody "
                "waits for nothing'. Counted: how often the purpose became a node of its own with "
                "the way beneath it. Each graph has two such sentences.",
                DRAWING,
                "counts",
                (
                    "an owner's way and its purpose are two nodes",
                    "the same, with the purpose also in the manifesto",
                ),
            ),
            Row(
                "Own choices recorded per graph",
                "Nodes for decisions the brief left to the agent, such as how an order is found at "
                "the counter. More of them means the graph says more of what building needs.",
                DRAWING,
                "numbers",
                ("nodes that record a choice of the agent's own",),
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
                DRAWING,
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
                "You replace QR tags by NFC stickers; the sealed QR node blends the tag with its "
                "purpose. Counted: answers that give the purpose a node of its own with the NFC "
                "choice beneath it.",
                ("sealed-feature",),
                "pass",
                ("its purpose is a node of its own above the NFC choice",),
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
                "Tells what you want apart from the way you named",
                "Counted: answers that separate at least one want from the way you suggested for "
                "it, such as bakers knowing what to bake and the board on a screen.",
                ("discuss",),
                "pass",
                ("it tells a want apart from the way the owner named",),
            ),
            Row(
                "Gives an overview of its understanding",
                "Counted: answers that say in a few lines how the agent understood you.",
                ("discuss",),
                "pass",
                ("it gives an overview of its understanding",),
            ),
            Row(
                "Answers most of its own questions",
                "Counted: answers in which at least half of the questions come with the agent's "
                "tentative answer, so that you can simply agree.",
                ("discuss",),
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
                "Right choice in short cases",
                "Multiple-choice questions about structure, phases, commands and wording. Share "
                "of answers that pick the keyed option.",
                (),
                "dilemmas",
            ),
        ),
    ),
)


def cell(row: Row, scores: dict, answered: list[dict], model: str, guide: str) -> str:
    if row.kind == "dilemmas":
        mine = [r for r in answered if r["model"] == model and r["guide"] == guide]
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
    width = 58
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
