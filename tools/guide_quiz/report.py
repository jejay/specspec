"""Tables over the collected answers: one column per model and guide version."""

from __future__ import annotations

from collections import defaultdict

from . import commands, dilemmas, grading, tasks


def short(model: str) -> str:
    return model.removeprefix("claude-")


def columns(cells) -> tuple[list[tuple[str, str]], str]:
    """Numbered columns for (model, guide) pairs, with the legend that explains them."""
    found = sorted(set(cells))
    legend = "\n".join(
        f"  {number}: {short(model)} with guide {guide}"
        for number, (model, guide) in enumerate(found, 1)
    )
    return found, legend


def row(label: str, values: list[str], width: int = 56) -> str:
    return f"{label[:width]:{width}}" + "".join(f"{value:>9}" for value in values)


def latest(records: list[dict], key) -> dict:
    """One record per cell; a later record replaces an earlier one."""
    return {key(record): record for record in records}


def dilemma_report(records: list[dict], reasons: bool = False) -> str:
    answered = latest(
        [record for record in records if record.get("picked") is not None],
        lambda r: (r["model"], r["guide"], r["item"], r["repetition"]),
    ).values()
    if not answered:
        return "No dilemma answers yet."
    cells, legend = columns((r["model"], r["guide"]) for r in answered)
    by_cell = defaultdict(list)
    for record in answered:
        by_cell[(record["model"], record["guide"], record["item"])].append(record)
    lines = ["Dilemmas: answers that match the key, of those given", legend, ""]
    lines.append(
        row(
            "item, and whether the 2026-11-10 guide states its rule",
            [str(n) for n in range(1, len(cells) + 1)],
        )
    )
    totals = defaultdict(lambda: [0, 0])
    for item in dilemmas.items():
        values = []
        part = item["topic"] if item["topic"] in ("structure", "relation") else "procedure"
        for cell in cells:
            group = by_cell.get((*cell, item["id"]), [])
            right = sum(record["correct"] for record in group)
            for key in (cell, (cell, part)):
                totals[key][0] += right
                totals[key][1] += len(group)
            values.append(f"{right}/{len(group)}" if group else "-")
        lines.append(row(f"{item['id']} {item['stated']:6} {item['rule']}", values))
    lines.append(row("all items", [f"{a}/{b}" for a, b in (totals[cell] for cell in cells)]))
    for label, keys in (
        ("percent", cells),
        ("percent, intention and conclusion", [(cell, "relation") for cell in cells]),
        ("percent, structure of a graph", [(cell, "structure") for cell in cells]),
        ("percent, routine, phases, commands and wording", [(c, "procedure") for c in cells]),
    ):
        shares = [f"{round(100 * a / b)}%" if b else "-" for a, b in (totals[k] for k in keys)]
        lines.append(row(label, shares))
    if reasons:
        lines += ["", "Answers that differ from the key:"]
        by_id = {item["id"]: item for item in dilemmas.items()}
        for record in answered:
            if not record["correct"]:
                option = by_id[record["item"]]["options"][record["picked"]]
                text = " ".join((record.get("text") or "").split())
                lines.append(
                    f"- {record['item']} {short(record['model'])} {record['guide']}: "
                    f'chose "{option[:60]}" | {text[:300]}'
                )
    return "\n".join(lines)


def scored(answers: list[dict], grades: list[dict], grader: str) -> dict:
    """Scores per (task, model, guide): one per repetition that has an answer and a grade."""
    verdicts = {
        (grade["answer"], grade.get("grader")): grade["verdict"]
        for grade in grades
        if grade.get("verdict")
    }
    cells = latest(
        [answer for answer in answers if answer.get("text")],
        lambda a: (a["task"], a["model"], a["guide"], a["repetition"]),
    )
    result = defaultdict(list)
    for (name, model, guide, _), answer in cells.items():
        task = tasks.TASKS.get(name)
        judge = commands.GRADER if task and task.answer == "commands" else grader
        verdict = verdicts.get((grading.answer_id(name, answer["text"]), judge))
        if task and (verdict if grading.judged(task) else name in grading.AUTOMATIC):
            result[(name, model, guide)].append(grading.score(task, answer["text"], verdict))
    return result


def task_report(answers: list[dict], grades: list[dict], grader: str = grading.GRADER) -> str:
    result = scored(answers, grades, grader)
    if not result:
        return "No graded answers yet."
    lines = [f"Open tasks, graded by {short(grader)}"]
    for name in tasks.TASKS:
        cells, legend = columns((model, guide) for task, model, guide in result if task == name)
        if not cells:
            continue
        groups = [result[(name, *cell)] for cell in cells]
        readable = [[score for score in group if score] for group in groups]
        lines += ["", f"== {name}: {tasks.TASKS[name].about}", legend, ""]
        lines.append(row("criterion", [str(n) for n in range(1, len(cells) + 1)]))
        lines.append(
            row(
                "answers (of these unreadable)",
                [
                    f"{len(group)} ({len(group) - len(good)})"
                    for group, good in zip(groups, readable, strict=True)
                ],
            )
        )
        for kind, render in (("pass", pass_cell), ("counts", count_cell), ("numbers", number_cell)):
            names = []
            for group in readable:
                for score in group:
                    names += [key for key in score[kind] if key not in names]
            for key in names:
                lines.append(row(key, [render(group, key) for group in readable]))
    return "\n".join(lines)


def pass_cell(group: list[dict], key: str) -> str:
    values = [score["pass"][key] for score in group if key in score["pass"]]
    return f"{sum(values)}/{len(values)}" if values else "-"


def count_cell(group: list[dict], key: str) -> str:
    pairs = [score["counts"][key] for score in group if key in score["counts"]]
    total = sum(b for _, b in pairs)
    return f"{sum(a for a, _ in pairs)}/{total}" if total else "-"


def number_cell(group: list[dict], key: str) -> str:
    values = [score["numbers"][key] for score in group if key in score["numbers"]]
    return f"{sum(values) / len(values):.1f}" if values else "-"


def spending(kinds: dict[str, list[dict]]) -> str:
    """Calls and their cost at list prices, per kind of record and model."""
    tally: dict[tuple[str, str], list[float]] = defaultdict(lambda: [0, 0.0])
    for kind, records in kinds.items():
        for record in records:
            cell = tally[(kind, short(record.get("model") or record.get("grader") or "?"))]
            cell[0] += 1
            cell[1] += record.get("cost") or 0.0
    lines = [row("recorded calls, with their cost at list prices", ["calls", "USD"])]
    for (kind, model), (calls, cost) in sorted(tally.items()):
        lines.append(row(f"{kind} by {model}", [str(calls), f"{cost:.2f}"]))
    calls, cost = (sum(cell[index] for cell in tally.values()) for index in (0, 1))
    lines.append(row("all", [str(calls), f"{cost:.2f}"]))
    return "\n".join(lines)


def agreement(answers: list[dict], grades: list[dict], first: str, second: str) -> str:
    """Per criterion, how often two graders come to the same result on the same answer."""
    verdicts = {
        grader: {
            g["answer"]: g["verdict"] for g in grades if g.get("verdict") and g["grader"] == grader
        }
        for grader in (first, second)
    }
    texts = {
        (answer["task"], grading.answer_id(answer["task"], answer["text"])): answer["text"]
        for answer in answers
        if answer.get("text") and answer["task"] in tasks.TASKS
    }
    tally: dict[tuple[str, str], list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    for (name, identity), text in texts.items():
        task = tasks.TASKS[name]
        if not task.rubric or not all(identity in verdicts[grader] for grader in (first, second)):
            continue
        one = grading.score(task, text, verdicts[first][identity])
        two = grading.score(task, text, verdicts[second][identity])
        if not one or not two:
            continue
        found = {key: (value, two["pass"][key]) for key, value in one["pass"].items()}
        found.update(
            {
                key: (count, two["counts"][key][0])
                for key, (count, of) in one["counts"].items()
                if of
            }
        )
        for key, (value, other) in found.items():
            cell = tally[(name, key)]
            cell[0] += 1
            cell[1] += value == other
            cell[2] += value
            cell[3] += other
    if not tally:
        return f"No answer has grades from both {short(first)} and {short(second)}."
    lines = [
        f"Agreement of {short(second)} with {short(first)}, per criterion",
        row("criterion", ["answers", "same", f"{short(first)[:8]}", f"{short(second)[:8]}"]),
    ]
    for name in tasks.TASKS:
        keys = [key for task, key in tally if task == name]
        if keys:
            lines += ["", f"== {name}"]
        for key in keys:
            total, same, passed_one, passed_two = tally[(name, key)]
            lines.append(
                row(
                    key,
                    [str(total), f"{round(100 * same / total)}%", str(passed_one), str(passed_two)],
                )
            )
    return "\n".join(lines)
