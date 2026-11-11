"""Tables over the collected answers: one column per model and guide version."""

from __future__ import annotations

from collections import defaultdict

from . import dilemmas, grading, tasks


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
        for cell in cells:
            group = by_cell.get((*cell, item["id"]), [])
            right = sum(record["correct"] for record in group)
            totals[cell][0] += right
            totals[cell][1] += len(group)
            values.append(f"{right}/{len(group)}" if group else "-")
        lines.append(row(f"{item['id']} {item['stated']:6} {item['rule']}", values))
    lines.append(row("all items", [f"{a}/{b}" for a, b in (totals[cell] for cell in cells)]))
    lines.append(
        row(
            "percent",
            [f"{round(100 * a / b)}%" if b else "-" for a, b in (totals[c] for c in cells)],
        )
    )
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
        grade["answer"]: grade["verdict"]
        for grade in grades
        if grade.get("verdict") and grade.get("grader") == grader
    }
    cells = latest(
        [answer for answer in answers if answer.get("text")],
        lambda a: (a["task"], a["model"], a["guide"], a["repetition"]),
    )
    result = defaultdict(list)
    for (name, model, guide, _), answer in cells.items():
        task = tasks.TASKS.get(name)
        verdict = verdicts.get(grading.answer_id(name, answer["text"]))
        if task and task.rubric and verdict:
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
    return f"{sum(a for a, _ in pairs)}/{sum(b for _, b in pairs)}" if pairs else "-"


def number_cell(group: list[dict], key: str) -> str:
    values = [score["numbers"][key] for score in group if key in score["numbers"]]
    return f"{sum(values) / len(values):.1f}" if values else "-"
