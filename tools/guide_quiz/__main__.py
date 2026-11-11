"""Command line of the guide quiz. Run ``python -m tools.guide_quiz --help``."""

from __future__ import annotations

import argparse
import concurrent.futures
import random
import sys

from . import commands, dilemmas, grading, guides, models, report, results, scorecard, tasks

HAIKU = "claude-haiku-5-5"


def listed(value: str) -> list[str]:
    return [part for part in value.split(",") if part]


def frames_of(names: str) -> dict[str, str]:
    """The system prompt per kept guide name; ``shipped`` becomes the name of its kept copy."""
    try:
        kept = [guides.resolve(name) for name in listed(names)]
    except ValueError as problem:
        raise SystemExit(str(problem)) from problem
    return {name: models.frame(guides.text(name)) for name in kept}


def run(jobs: list, work, workers: int) -> None:
    """Run the jobs in a shuffled order, a few at a time."""
    random.Random(0).shuffle(jobs)
    print(f"{len(jobs)} calls to make", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(work, jobs))


def ask_dilemmas(arguments) -> None:
    """Every dilemma in a call of its own, per model, guide and repetition."""
    done = {
        (r["model"], r["guide"], r["item"], r["repetition"])
        for r in results.load("dilemmas")
        if r.get("picked") is not None
    }
    wanted = set(listed(arguments.items)) if arguments.items else None
    frames = frames_of(arguments.guides)
    log = results.Log("dilemmas")

    def work(job) -> None:
        model, guide, item, repetition = job
        answer = models.ask(model, frames[guide], dilemmas.prompt(item, repetition))
        picked = dilemmas.picked(item, repetition, answer.text)
        log.append(
            {
                "model": model,
                "guide": guide,
                "item": item["id"],
                "repetition": repetition,
                "picked": picked,
                "correct": None if picked is None else picked == 0,
                "text": answer.text,
                "error": answer.error,
                "cost": answer.cost,
                "tokens": answer.tokens,
                "served": answer.served,
            }
        )
        mark = "??" if picked is None else ("ok" if picked == 0 else "no")
        print(f"{mark} {model} {guide} {item['id']} r{repetition}", flush=True)

    jobs = [
        (model, guide, item, repetition)
        for model in listed(arguments.models)
        for guide in frames
        for item in dilemmas.items()
        for repetition in range(arguments.repetitions)
        if (model, guide, item["id"], repetition) not in done
        and (wanted is None or item["id"] in wanted)
    ]
    run(jobs, work, arguments.workers)


def ask_tasks(arguments) -> None:
    """Every open task once per model, guide and repetition."""
    names = listed(arguments.tasks)
    unknown = [name for name in names if name not in tasks.TASKS]
    if unknown:
        raise SystemExit(f"Unknown task: {', '.join(unknown)}. Known: {', '.join(tasks.TASKS)}")
    done = {
        (r["task"], r["model"], r["guide"], r["repetition"])
        for r in results.load("tasks")
        if r.get("text")
    }
    frames = frames_of(arguments.guides)
    log = results.Log("tasks")

    def work(job) -> None:
        name, model, guide, repetition = job
        answer = models.ask(model, frames[guide], tasks.brief(name))
        log.append(
            {
                "task": name,
                "model": model,
                "guide": guide,
                "repetition": repetition,
                "text": answer.text,
                "error": answer.error,
                "cost": answer.cost,
                "tokens": answer.tokens,
                "served": answer.served,
            }
        )
        readable = tasks.TASKS[name].answer == "text" or tasks.parse(answer.text)
        state = "failed" if answer.text is None else ("ok" if readable else "unreadable")
        print(f"{state} {name} {model} {guide} r{repetition}", flush=True)

    jobs = [
        (name, model, guide, repetition)
        for name in names
        for model in listed(arguments.models)
        for guide in frames
        for repetition in range(arguments.repetitions)
        if (name, model, guide, repetition) not in done
    ]
    run(jobs, work, arguments.workers)


def grade(arguments) -> None:
    """Judge every answer that has no verdict yet: by the grader, or by running its commands."""
    done = {
        (grade["answer"], grade.get("grader"))
        for grade in results.load("grades")
        if grade.get("verdict")
    }
    pending = {}
    wanted = set(listed(arguments.tasks))
    for answer in chosen(results.load("tasks"), arguments):
        task = tasks.TASKS.get(answer["task"])
        if wanted and answer["task"] not in wanted:
            continue
        if task and grading.judged(task) and answer.get("text"):
            identity = grading.answer_id(task.name, answer["text"])
            judge = commands.GRADER if task.answer == "commands" else arguments.grader
            if (identity, judge) not in done or task.name in listed(arguments.again):
                pending[identity] = (task, answer["text"])
    system = grading.context()
    log = results.Log("grades")

    def work(job) -> None:
        identity, (task, text) = job
        if task.answer == "commands":
            data = tasks.parse(text)
            if not data:
                return
            record = {"grader": commands.GRADER, "verdict": commands.run(data, task.base)}
        else:
            question = grading.prompt(task, text)
            if question is None:
                return
            answer = models.ask(arguments.grader, system, question)
            verdict = tasks.parse(answer.text)
            record = {
                "grader": arguments.grader,
                "verdict": verdict,
                "text": None if verdict else answer.text,
                "error": answer.error,
                "cost": answer.cost,
            }
        log.append({"answer": identity, "task": task.name, **record})
        print(f"{'ok' if record['verdict'] else 'failed'} {task.name} {identity}", flush=True)

    run(list(pending.items()), work, arguments.workers)


def chosen(records: list[dict], arguments) -> list[dict]:
    """The records of the named models and guides; without names, all of them."""
    try:
        kept = {guides.resolve(name) for name in listed(arguments.guides)}
    except ValueError as problem:
        raise SystemExit(str(problem)) from problem
    wanted = set(listed(arguments.models))
    return [
        record
        for record in records
        if (not kept or record["guide"] in kept) and (not wanted or record["model"] in wanted)
    ]


def show(arguments) -> None:
    answers = chosen(results.load("dilemmas"), arguments)
    print(report.dilemma_report(answers, reasons=arguments.reasons))
    print()
    answers = chosen(results.load("tasks"), arguments)
    print(report.task_report(answers, results.load("grades"), arguments.grader))


def show_scorecard(arguments) -> None:
    """The behaviours in plain words, one column per named guide."""
    try:
        kept = [guides.resolve(name) for name in listed(arguments.guides)]
    except ValueError as problem:
        raise SystemExit(str(problem)) from problem
    scores = report.scored(results.load("tasks"), results.load("grades"), arguments.grader)
    print(scorecard.table(scores, results.load("dilemmas"), arguments.model, kept))


def show_spending(arguments) -> None:
    print(report.spending({kind: results.load(kind) for kind in results.KINDS}))


def compare_graders(arguments) -> None:
    first, second = listed(arguments.graders)
    answers, grades = results.load("tasks"), results.load("grades")
    print(report.agreement(answers, grades, first, second))


def list_guides(arguments) -> None:
    try:
        shipped = guides.resolve(guides.SHIPPED)
    except ValueError as problem:
        shipped = None
        print(problem)
    for name in guides.names():
        mark = "  (shipped)" if name == shipped else ""
        print(f"{guides.size(name):6} bytes  {name}{mark}")


def parser() -> argparse.ArgumentParser:
    main = argparse.ArgumentParser(prog="python -m tools.guide_quiz", description=__doc__)
    commands = main.add_subparsers(required=True)

    def command(name: str, function, text: str) -> argparse.ArgumentParser:
        sub = commands.add_parser(name, help=text, description=text)
        sub.set_defaults(function=function)
        return sub

    def calls(sub: argparse.ArgumentParser) -> None:
        sub.add_argument("--models", default=HAIKU, help="model IDs, comma-separated")
        sub.add_argument("--guides", default=guides.SHIPPED, help="guide names, comma-separated")
        sub.add_argument("--repetitions", type=int, default=5)
        sub.add_argument("--workers", type=int, default=4)

    command("guides", list_guides, "List the guide versions and their sizes.")
    sub = command("dilemmas", ask_dilemmas, "Ask the dilemmas; answers already given are kept.")
    calls(sub)
    sub.add_argument("--items", default="", help="item IDs, comma-separated; default: all")
    sub = command("tasks", ask_tasks, "Run open tasks; answers already given are kept.")
    calls(sub)
    sub.add_argument("--tasks", required=True, help=f"comma-separated: {', '.join(tasks.TASKS)}")
    sub = command("grade", grade, "Grade the open answers that have no grade yet.")
    sub.add_argument("--grader", default=grading.GRADER)
    sub.add_argument("--workers", type=int, default=4)
    sub.add_argument("--again", default="", help="tasks to judge anew, comma-separated")
    sub.add_argument("--models", default="", help="only answers of these models")
    sub.add_argument("--guides", default="", help="only answers given with these guides")
    sub.add_argument("--tasks", default="", help="only answers to these tasks")
    sub = command("report", show, "Print the result tables.")
    sub.add_argument("--grader", default=grading.GRADER)
    sub.add_argument("--reasons", action="store_true", help="list answers that miss the key")
    sub.add_argument("--models", default="", help="only these model IDs, comma-separated")
    sub.add_argument("--guides", default="", help="only these guide names, comma-separated")
    sub = command("agreement", compare_graders, "Compare two graders on the answers both graded.")
    sub.add_argument("--graders", required=True, help="two model IDs, comma-separated")
    command("costs", show_spending, "Count the recorded calls and add up their cost.")
    sub = command("scorecard", show_scorecard, "Print the main behaviours in plain words.")
    sub.add_argument("--guides", required=True, help="guide names, comma-separated")
    sub.add_argument("--model", default=HAIKU)
    sub.add_argument("--grader", default=grading.GRADER)
    return main


def main(argv: list[str] | None = None) -> None:
    arguments = parser().parse_args(argv)
    arguments.function(arguments)


if __name__ == "__main__":
    main(sys.argv[1:])
