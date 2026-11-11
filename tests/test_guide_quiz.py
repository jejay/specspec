"""The guide quiz's own logic, checked without calling a model."""

import argparse
import json
import subprocess
import tomllib
from pathlib import Path

import pytest

from tools.guide_quiz import __main__ as command_line
from tools.guide_quiz import (
    commands,
    dilemmas,
    grading,
    graphs,
    guides,
    models,
    report,
    results,
    tasks,
)

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/guide_quiz"


def test_quiz_stays_out_of_every_shipped_artifact():
    build = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["tool"]["hatch"]
    assert build["build"]["targets"]["wheel"]["packages"] == ["src/specspec"]
    assert build["build"]["targets"]["sdist"]["include"] == [
        "/src/specspec",
        "/pyproject.toml",
        "/README.md",
        "/LICENSE",
    ]
    workspaces = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["workspaces"]
    packaged = [ROOT / "src", *(ROOT / name for name in workspaces)]
    assert not any(TOOL.is_relative_to(folder) for folder in packaged)
    for folder in packaged:
        for path in folder.rglob("*"):
            if path.suffix in {".py", ".cjs", ".js", ".ts", ".json"} and "node_modules" not in (
                path.parts
            ):
                assert "guide_quiz" not in path.read_text(encoding="utf-8", errors="replace"), path


def test_raw_answers_are_ignored_by_git():
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "tools/guide_quiz/results/tasks-1.jsonl"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert result.stdout.strip() == "tools/guide_quiz/results/tasks-1.jsonl"


def test_guide_versions_resolve_by_name(tmp_path, monkeypatch):
    names = guides.names()
    assert len(names) == len(set(names)) >= 10 and guides.SHIPPED not in names
    for name in names:
        text = guides.text(name)
        assert text.strip() and "\r" not in text and guides.resolve(name) == name, name
    assert guides.size("five-lines") < 1000 < guides.size("2026-11-10-before-structure-rules")
    with pytest.raises(ValueError, match="Unknown guide"):
        guides.text("no-such-guide")

    # A result names a text that stays: the shipped guide counts through its kept copy.
    kept = guides.FOLDER / "2026-11-10-before-structure-rules.md"
    template = tmp_path / "AGENTS.md"
    template.write_bytes(kept.read_bytes().replace(b"\n", b"\r\n"))
    monkeypatch.setattr(guides, "TEMPLATE", template)
    assert guides.resolve(guides.SHIPPED) == kept.stem
    assert guides.text(guides.SHIPPED) == guides.text(kept.stem)
    template.write_text("A guide that nobody kept.\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no kept copy"):
        guides.resolve(guides.SHIPPED)


def test_dilemmas_have_one_key_and_a_stable_order():
    items = dilemmas.items()
    assert len({item["id"] for item in items}) == len(items) >= 22
    for item in items:
        assert len(item["options"]) == 4 == len(set(item["options"])), item["id"]
        assert item["stated"] in {"yes", "partly", "no"} and item["rule"] and item["stem"]
        order = dilemmas.order(item, 3)
        assert sorted(order) == [0, 1, 2, 3] and order == dilemmas.order(item, 3)
        prompt = dilemmas.prompt(item, 3)
        assert all(option in prompt for option in item["options"])
        key_letter = dilemmas.LETTERS[order.index(0)]
        assert dilemmas.picked(item, 3, f"{key_letter}\nBecause.") == 0
    orders = {tuple(dilemmas.order(items[0], repetition)) for repetition in range(12)}
    assert len(orders) > 1


@pytest.mark.parametrize(
    ("reply", "letter"),
    [
        ("B\nBecause it is.", "B"),
        ("**C**\nReason", "C"),
        ("Answer: D", "D"),
        ("A) the first option", "A"),
        ("\n\nb", "B"),
        ("The best option is A", None),
        ("", None),
        (None, None),
    ],
)
def test_the_letter_is_read_from_the_first_line(reply, letter):
    assert dilemmas.letter(reply) == letter


def test_every_task_has_its_files_and_every_graded_task_a_scorer():
    for name, task in tasks.TASKS.items():
        assert tasks.brief(name).strip(), name
        assert task.answer in {"graph", "operations", "commands", "text"}
        if grading.judged(task):
            assert name in grading.SCORERS and bool(task.rubric) != (task.answer == "commands")
        if task.rubric:
            assert tasks.rubric(task)
        if task.answer == "graph":
            assert task.root_names and name in grading.PROBES
        if task.answer in ("operations", "commands"):
            base, _ = graphs.base(task.base)
            assert graphs.problems(base) == []
            for key, record in base.items():
                assert key == graphs.ROOT or key in tasks.brief(name), (name, key)
                assert record["title"] in tasks.brief(name), (name, key)
    assert grading.AUTOMATIC <= set(grading.SCORERS)
    assert all(not tasks.TASKS[name].rubric for name in grading.AUTOMATIC)
    assert grading.context().startswith("You grade one answer")
    assert {item["topic"] for item in dilemmas.items()} == {
        "structure",
        "routine",
        "phases",
        "commands",
        "writing",
    }


def test_answers_are_parsed_with_or_without_a_fence_and_salvaged_when_broken():
    plain = '{"nodes": [{"key": "a", "parents": ["manifesto"]}], "report": "done"}'
    assert tasks.parse(plain)["nodes"][0]["key"] == "a"
    assert tasks.parse(f"Here it is:\n```json\n{plain}\n```\nThanks")["report"] == "done"
    broken = '{"nodes": [{"key": "a", "title": "A"}, {"key": "b", "title": "B"}]], "report": "r"}'
    salvaged = tasks.parse(broken)
    assert salvaged["salvaged"] and [n["key"] for n in salvaged["nodes"]] == ["a", "b"]
    assert salvaged["report"] == "r"
    stray = '{"commands": ["specspec delete A=", "specspec add -m \'# B\'"], "report": "r"]}'
    assert tasks.parse(stray) == {
        "commands": ["specspec delete A=", "specspec add -m '# B'"],
        "report": "r",
        "salvaged": True,
    }
    assert tasks.parse('{"commands": "none", "report": "r"]}') is None
    assert tasks.parse("no json here") is None and tasks.parse(None) is None


def drawing(*nodes):
    return {
        "nodes": [
            {"key": key, "type": kind, "parents": parents, "title": title, "body": body}
            for key, kind, parents, title, body in nodes
        ]
    }


def test_drawn_graphs_are_checked_with_the_rules_of_specspec_check():
    good = drawing(
        ("outcome", "requirement", ["manifesto"], "See the week", "Everyone sees it."),
        ("grid", "requirement", ["outcome"], "Show a grid", "One column each."),
        ("limit", "requirement", ["Kq3x9bA="], "Stay in the EU", "Data stays."),
        ("host", "requirement", ["grid", "limit"], "Host in Frankfurt", "A server."),
    )
    nodes = graphs.drawn(good, {"Kq3x9bA="})
    assert graphs.problems(nodes) == []
    assert nodes["limit"]["parents"] == [graphs.ROOT]
    assert graphs.ancestors(nodes, "host") == {"grid", "limit", "outcome", graphs.ROOT}
    measured = graphs.metrics(nodes)
    assert measured["nodes"] == 4 and measured["depth"] == 3
    assert measured["nodes with two or more parents"] == 1
    assert "- host (parents: grid, limit) # Host in Frankfurt" in graphs.outline(nodes)

    shortcut = drawing(*[tuple(n.values()) for n in good["nodes"]])
    shortcut["nodes"][3]["parents"] = ["grid", "outcome"]
    assert graphs.problems(graphs.drawn(shortcut, {"Kq3x9bA="})) == ["REDUNDANT_PARENT host"]
    flawed = drawing(
        ("code", "implementation", ["manifesto"], "Code", "Files."),
        ("lost", "requirement", ["nowhere"], "Lost", "No parent exists."),
        ("odd", "choice", ["manifesto"], "Odd", "Unknown type."),
    )
    found = graphs.problems(graphs.drawn(flawed, set()))
    assert "TYPE odd" in found and "PARENT_TYPE code" in found and "REFERENCE lost" in found


def test_operations_are_applied_to_the_base_graph_of_the_revision_tasks():
    base, root_names = graphs.base()
    assert graphs.problems(base) == [] and root_names == {"Kq3x9bA="}
    for name in ("revise", "revise-phones"):
        brief = tasks.brief(name)
        for record in json.loads(
            (graphs.QUIZZES / "revise.graph.json").read_text(encoding="utf-8")
        ):
            assert record["id"] in brief and record["title"] in brief, (name, record["id"])
    answer = {
        "operations": [
            {"op": "add", "key": "list", "parents": ["Wk7fTq0"], "title": "# Show a day list"},
            {"op": "update", "id": "C0lrTy2=", "parents": ["$list"]},
            {"op": "delete", "id": "Sl0tRw8="},
            {"op": "delete", "id": "ImGr1d5="},
            {"op": "delete", "id": "Gr1dCc4="},
            {"op": "delete", "id": "unknown="},
        ]
    }
    nodes, summary = graphs.revised(answer)
    assert summary == {
        "added": ["list"],
        "updated": ["C0lrTy2="],
        "deleted": ["Sl0tRw8=", "ImGr1d5=", "Gr1dCc4="],
        "unknown": ["unknown="],
    }
    assert nodes["list"]["parents"] == ["Wk7fTq0="] and nodes["list"]["title"] == "Show a day list"
    assert nodes["C0lrTy2="]["origin"] == "updated:parents"
    assert graphs.problems(nodes) == []
    dumped = json.loads(graphs.dump(nodes))
    assert {row["key"]: row["ancestors"] for row in dumped}["C0lrTy2="] == [
        graphs.ROOT,
        "Wk7fTq0=",
        "list",
    ]


@pytest.mark.parametrize(
    ("text", "flagged"),
    [
        ("The project is delivered in three stages.", True),
        ("Stage one sets up the project with continuous integration.", True),
        ("Reminders are built after the booking features.", True),
        ("Implementation deferred to a second phase.", True),
        ("The board shows what to bake first.", False),
        ("Texts go out at 18:00 on the day before the appointment.", False),
        ("Every change is checked before it is merged.", False),
    ],
)
def test_build_order_is_found_by_text(text, flagged):
    nodes = graphs.drawn(drawing(("a", "requirement", ["manifesto"], "A node", text)), set())
    assert (graphs.build_order(nodes) == ["a"]) is flagged


def test_a_drawing_is_scored_from_the_graph_and_the_graders_findings():
    answer = drawing(
        ("pg", "requirement", ["manifesto"], "Store data in PostgreSQL", "The contractor's."),
        ("eu", "requirement", ["manifesto"], "Keep patient data in the EU", "All of it."),
        ("remind", "requirement", ["manifesto"], "Patients are reminded in time", "Fewer forget."),
        ("sms", "requirement", ["remind"], "Send a text the day before", "At 18:00."),
        ("gateway", "requirement", ["sms", "eu"], "Use a gateway in Frankfurt", "EU hosted."),
        ("week", "requirement", ["manifesto"], "Show the week in a grid", "Therapists as columns."),
        ("plan", "requirement", ["manifesto"], "Build in three stages", "CI comes first."),
    )
    verdict = {
        "pg": {"node": "pg", "own_node": True, "has_descendants": False},
        "eu": {"node": "eu", "own_node": True},
        "sms_provider": {"node": "gateway", "own_node": True, "left_open_explicitly": False},
        "reminder": {
            "outcome_node": "remind",
            "means_node": "sms",
            "separate_nodes": True,
            "outcome_text_free_of_means": True,
        },
        "week": {
            "outcome_node": "week",
            "means_node": "week",
            "separate_nodes": False,
            "outcome_text_free_of_means": False,
        },
        "double_booking_own_node": False,
        "limits": {"nodes": ["desk", "week"], "all_three_stated": False},
        "paper_phone": {"nodes": [], "separate_nodes": False},
        "work_order": {"order_nodes": ["plan"], "order_in_text": []},
        "category_nodes": [],
        "historic_contrast": [],
        "root_children_means": ["week"],
        "reminder_wording": "absent",
        "label_titles": [],
        "blended_nodes": [{"key": "week", "why": "outcome and grid"}],
        "report": {"names_own_choices": True, "names_open_points": "true"},
    }
    text = json.dumps({**answer, "report": "Done."})
    score = grading.score(tasks.TASKS["clinic"], text, verdict)
    passed = score["pass"]
    assert passed["graph passes the structure check"]
    assert passed["constraints are nodes directly under the manifesto"]
    assert passed["a choice descends from the constraint that shaped it"]
    assert passed["a suggested technology is a requirement of its own"]
    assert not passed["no build order in node text"]
    assert not passed["the manifesto's children are outcomes or constraints"]
    assert passed["the report names open points"]
    assert score["counts"]["the same, with the purpose also in the manifesto"] == [1, 2]
    assert score["numbers"]["nodes that blend decisions"] == 1
    assert score["numbers"]["nodes that state the limits"] == 2
    assert "nodes that record a choice of the agent's own" not in score["numbers"]
    counted = {**verdict, "own_choice_nodes": ["gateway", "no-such-node", "gateway"]}
    numbers = grading.score(tasks.TASKS["clinic"], text, counted)["numbers"]
    assert numbers["nodes that record a choice of the agent's own"] == 1
    assert grading.score(tasks.TASKS["clinic"], "not json", verdict) is None

    question = grading.prompt(tasks.TASKS["clinic"], text)
    assert tasks.rubric(tasks.TASKS["clinic"]) in question and '"key": "gateway"' in question
    assert "haiku" not in question.lower() and "guide" not in question.lower()
    assert grading.answer_id("clinic", text) != grading.answer_id("bakery", text)


def test_review_and_revision_answers_are_scored():
    review = grading.score(
        tasks.TASKS["review"],
        "Free text.",
        {"identified": {"F01_category": True, "F10_steps": "false"}, "wrong_claims": ["x"]},
    )
    assert review["numbers"] == {
        "planted problems found": 1,
        "further points": 0,
        "wrong claims": 1,
    }
    operations = {
        "operations": [
            {"op": "add", "key": "day", "parents": ["Wk7fTq0="], "title": "Show one day as a list"},
            {"op": "update", "id": "C0lrTy2=", "parents": ["day"]},
            {"op": "delete", "id": "Gr1dCc4="},
            {"op": "delete", "id": "Sl0tRw8="},
            {"op": "delete", "id": "ImGr1d5="},
            {
                "op": "add",
                "key": "mail",
                "parents": ["Rm1ndR3=", "EuData9="],
                "title": "Remind patients without a mobile phone by e-mail",
            },
        ],
        "report": "Removed the grid.",
    }
    verdict = {
        "day_list": {"how": "new_node", "node": "day"},
        "outcome_Wk7fTq0_text_names_means": False,
        "yes": {"nodes": [], "only_appended_to_existing": True},
        "email": {"node": "mail", "is_added_node": True},
        "signin_sentence": "left_unmentioned",
        "report": {"names_removed_nodes": True},
    }
    passed = grading.score(tasks.TASKS["revise"], json.dumps(operations), verdict)["pass"]
    assert passed["resulting graph passes the structure check"]
    assert passed["the day list is a new node directly under the outcome"]
    assert passed["the colour node is kept and applies to the day list"]
    assert passed["e-mail is under the reminder outcome and beside the text message"]
    assert passed["e-mail descends from the EU constraint"]
    assert passed["the replaced choice is deleted"]
    assert not passed["the reply is recorded in a new node"]
    assert not passed["the unrelated sentence is split out or named"]
    phones = grading.score(tasks.TASKS["revise-phones"], json.dumps(operations), verdict)
    assert "the replaced choice is deleted" not in phones["pass"]


class Done:
    def __init__(self, stdout):
        self.stdout = stdout


def test_a_model_is_asked_in_isolation_and_asked_again_after_a_failure(monkeypatch):
    monkeypatch.setattr(models.shutil, "which", lambda name: "claude")
    monkeypatch.setenv("CLAUDE_EFFORT", "max")
    replies = [
        json.dumps({"is_error": True, "api_error_status": 529, "result": "overloaded"}),
        json.dumps(
            {
                "result": "B\nBecause.",
                "total_cost_usd": 0.001,
                "usage": {"input_tokens": 2, "cache_read_input_tokens": 40, "output_tokens": 7},
                "modelUsage": {"claude-haiku-5-5": {}},
                "duration_ms": 900,
            }
        ),
    ]
    calls, waits = [], []

    def run(arguments, **options):
        calls.append((arguments, options))
        return Done(replies[len(calls) - 1])

    answer = models.ask("claude-haiku-5-5", "system text", "prompt", run=run, wait=waits.append)
    assert answer.text == "B\nBecause." and answer.tokens == {"in": 42, "out": 7, "thinking": 0}
    assert answer.served == ["claude-haiku-5-5"] and waits == [5]
    arguments, options = calls[0]
    assert arguments[arguments.index("--tools") + 1] == ""
    assert arguments[arguments.index("--effort") + 1] == "medium"
    assert "--safe-mode" in arguments and options["input"] == "prompt"
    assert not any(key.upper().startswith("CLAUDE") for key in options["env"])
    system_path = Path(arguments[arguments.index("--system-prompt-file") + 1])
    assert system_path.read_text(encoding="utf-8") == "system text"
    assert "--effort" not in models.command("claude-haiku-4-5", system_path, None)
    assert "<AGENTS.md>\nGuide\n</AGENTS.md>" in models.frame("Guide\n")

    failed = models.ask("claude-haiku-5-5", "s", "p", attempts=2, run=run_out, wait=waits.append)
    assert failed.text is None and failed.error == "timeout"


def run_out(arguments, **options):
    raise subprocess.TimeoutExpired(arguments, options["timeout"])


def test_results_are_kept_per_process_and_reported_per_model_and_guide(tmp_path):
    log = results.Log("dilemmas", tmp_path)
    item = dilemmas.items()[0]
    for repetition, picked in enumerate([0, 0, 2]):
        log.append(
            {
                "model": "claude-haiku-5-5",
                "guide": "shipped",
                "item": item["id"],
                "repetition": repetition,
                "picked": picked,
                "correct": picked == 0,
                "text": "A\nSome reason.",
            }
        )
    log.path.open("a", encoding="utf-8").write("{damaged\n")
    records = results.load("dilemmas", tmp_path)
    assert len(records) == 3 and results.load("tasks", tmp_path) == []
    table = report.dilemma_report(records, reasons=True)
    assert "1: haiku-5-5 with guide shipped" in table and "2/3" in table and "67%" in table
    assert f"- {item['id']} haiku-5-5 shipped: chose" in table
    shares = {line[:56].strip(): line[56:].strip() for line in table.splitlines()}
    assert shares["percent, structure of a graph"] == "67%"
    assert shares["percent, routine, phases, commands and wording"] == "-"

    other = [{**record, "guide": "five-lines", "model": "claude-sonnet-5-5"} for record in records]
    named = argparse.Namespace(models="claude-sonnet-5-5", guides="five-lines")
    assert command_line.chosen(records + other, named) == other
    everything = argparse.Namespace(models="", guides="")
    assert command_line.chosen(records + other, everything) == records + other
    with pytest.raises(SystemExit, match="Unknown guide"):
        command_line.chosen(records, argparse.Namespace(models="", guides="no-such-guide"))

    spent = report.spending(
        {
            "dilemmas": [{"model": "claude-haiku-5-5", "cost": 0.25}, *records],
            "grades": [{"grader": "claude-opus-5-5", "cost": 1.5}],
        }
    )
    assert "dilemmas by haiku-5-5" in spent and "grades by opus-5-5" in spent
    assert spent.splitlines()[-1].split() == ["all", "5", "1.75"]
    with pytest.raises(ValueError):
        results.Log("other", tmp_path)

    answer = "A review."
    answers = [
        {"task": "review", "model": "claude-haiku-5-5", "guide": "shipped", "repetition": 0}
        | {"text": answer}
    ]
    grades = [
        {
            "answer": grading.answer_id("review", answer),
            "grader": grading.GRADER,
            "verdict": {"identified": {"F01_category": True}, "other_points": ["a", "b"]},
        }
    ]
    table = report.task_report(answers, grades)
    assert "== review" in table and "F01_category" in table and "1/1" in table and "2.0" in table
    assert report.task_report(answers, grades, grader="another") == "No graded answers yet."

    second = {**grades[0], "grader": "another", "verdict": {"identified": {"F01_category": False}}}
    compared = report.agreement(answers, [*grades, second], grading.GRADER, "another")
    assert "Agreement of another with opus-5-5" in compared and "0%" in compared
    assert "No answer has grades from both" in report.agreement(answers, grades, "a", "b")


def test_negative_wording_is_counted_without_bounds():
    nodes = graphs.drawn(
        drawing(
            ("a", "requirement", ["manifesto"], "Keep data", "The app never deletes a row."),
            ("b", "requirement", ["manifesto"], "Limit hours", "It ends no later than 20:00."),
            ("c", "requirement", ["manifesto"], "Stay simple", "Customers don't need an account."),
        ),
        set(),
    )
    assert [len(graphs.NEGATION.findall(n["body"])) for n in list(nodes.values())[1:]] == [1, 0, 1]
    assert graphs.metrics(nodes)["negations per 100 words"] > 0


def test_a_structure_review_and_the_planning_after_it_are_scored():
    review = grading.score(
        tasks.TASKS["owner-edits"],
        "I would suggest six changes.",
        {
            "identified": {"E1_way_and_purpose": True, "E4_work_order": True, "E6_parent": False},
            "clean_edit_left_alone": True,
            "suggests_only": True,
            "says_declined_stays": False,
        },
    )
    assert review["numbers"]["planted problems found"] == 2
    assert review["pass"]["the answer suggests and leaves the graph as it is"]
    assert not review["pass"]["it says that what is not accepted stays"]

    task = tasks.TASKS["owner-edits-apply"]
    obedient = {
        "commits": [
            "Owner specspec changes: QR tags, limits, texting and a warranty slip",
            "Agent specspec changes: split the QR tag, merge the limits",
        ],
        "operations": [
            {
                "op": "add",
                "key": "no-mix-ups",
                "parents": ["Bx7Rp2A="],
                "title": "No two bikes get mixed up",
            },
            {
                "op": "update",
                "id": "Qr5Tag0=",
                "parents": ["no-mix-ups"],
                "title": "Print a QR tag for every bike",
            },
            {"op": "delete", "id": "St3Pln8="},
            {"op": "delete", "id": "Lm2Prt4="},
            {"op": "delete", "id": "Lm3Pht8="},
            {
                "op": "update",
                "id": "Lm1Nte0=",
                "title": "Jobs stay within their limits",
                "body": "Notes have at most 500 characters, jobs 20 parts, photos 10 MB.",
            },
        ],
        "report": "Done.",
    }
    score = grading.score(task, json.dumps(obedient))
    assert all(score["pass"].values()), score["pass"]
    assert score["numbers"]["declined suggestions left as written"] == 3
    assert score["numbers"]["accepted suggestions carried out"] == 3

    eager = json.loads(json.dumps(obedient))
    eager["commits"] = ["Agent specspec changes: tidy the owner's edits"]
    eager["operations"] += [
        {"op": "update", "id": "Wr8Nty0=", "parents": ["Bx7Rp2A="]},
        {"op": "update", "id": "Sm5Txt4=", "body": "The text goes out when the job is done."},
        {"op": "update", "id": "Jb1Brd8=", "body": "A card shows the bike and the work to do."},
    ]
    score = grading.score(task, json.dumps(eager))
    assert score["numbers"]["declined suggestions left as written"] == 0
    assert not score["pass"]["the owner's edits are committed first, under the owner's title"]
    assert score["pass"]["accepted: the work order is gone from the graph"]

    answers = [
        {"task": task.name, "model": "claude-haiku-5-5", "guide": "shipped", "repetition": 0}
        | {"text": json.dumps(obedient)}
    ]
    assert "accepted: the three limits are one node" in report.task_report(answers, [])

    # The same planning when the owner answers three suggestions and is silent on the rest.
    silent = tasks.TASKS["owner-edits-unanswered"]
    assert "Leave 2, 3 and 6" in tasks.brief(task.name)
    assert "Leave 2, 3 and 6" not in tasks.brief(silent.name)
    assert "stays as you wrote it" not in tasks.brief(silent.name)
    score = grading.score(silent, json.dumps(obedient))
    assert all(score["pass"].values()), score["pass"]
    assert score["numbers"]["unanswered suggestions left as written"] == 3
    score = grading.score(silent, json.dumps(eager))
    assert score["numbers"]["unanswered suggestions left as written"] == 0
    assert not score["pass"]["unanswered: the warranty slip stays under the card view"]


def test_a_round_of_tandem_planning_is_scored():
    task = tasks.TASKS["discuss"]
    assert "What do you think?" in tasks.brief(task.name)
    verdict = {
        "leaves_graph": True,
        "about_product": True,
        "overview": True,
        "questions": 4,
        "questions_with_own_answer": 3,
        "separates_want_from_way": True,
        "challenges_a_choice": False,
        "own_conclusions": True,
    }
    score = grading.score(task, "I would use the mailbox. Which days are you closed?", verdict)
    assert score["numbers"] == {
        "words": 10,
        "questions": 4,
        "questions with a tentative answer": 3,
        "wrong claims": 0,
    }
    assert score["pass"]["it asks questions and answers most of them itself"]
    assert not score["pass"]["it challenges a choice the owner suggested"]
    silent = grading.score(task, "Done.", {**verdict, "questions": 0, "leaves_graph": False})
    assert not silent["pass"]["it asks questions and answers most of them itself"]
    assert not silent["pass"]["the answer leaves the graph as it is"]
    assert "<review>" in grading.prompt(task, "Done.")


def test_command_lines_are_split_as_a_shell_splits_them():
    line = "specspec add --as goal --parent Bx7Rp2A= -m '# No mix-ups' -m \"Two words\""
    assert commands.invocations(line) == (
        [["add", "--as", "goal", "--parent", "Bx7Rp2A=", "-m", "# No mix-ups", "-m", "Two words"]],
        0,
    )
    # Only single quotes keep a reference to a new node from the shell.
    assert commands.words("update Qr5Tag0= --parent '$goal'") == (
        ["update", "Qr5Tag0=", "--parent", "$goal"],
        0,
    )
    assert commands.words('update Qr5Tag0= --parent "$goal" -m \\$5') == (
        ["update", "Qr5Tag0=", "--parent", "", "-m", "$5"],
        1,
    )
    chained = "git add -A && specspec delete St3Pln8= ; python -m specspec update A --parent B"
    assert commands.invocations(chained)[0] == [
        ["delete", "St3Pln8="],
        ["update", "A", "--parent", "B"],
    ]
    assert commands.invocations("specspec query --max-distance 2") == ([], 0)
    assert commands.invocations("specspec add \\\n --parent A")[0] == [["add", "--parent", "A"]]
    with pytest.raises(ValueError):
        commands.words("specspec add -m 'no end")
    # A variable that holds what a command printed is split into words unless quoted.
    kept = {"NEW": "Added: AbCdEfg=\nAffected: 1 nodes"}
    assert commands.words("update A --parent $NEW", kept) == (
        ["update", "A", "--parent", "Added:", "AbCdEfg=", "Affected:", "1", "nodes"],
        0,
    )
    assert commands.words('update A -m "${NEW}"', kept)[0][-1] == kept["NEW"]


def test_the_commands_of_an_answer_run_on_a_copy_of_the_base_graph():
    task = tasks.TASKS["owner-edits-commands"]
    assert "`git status` is clean" in tasks.brief(task.name)
    answer = {
        "commands": [
            "specspec query --max-distance 2",
            "specspec add --as apart --parent Bx7Rp2A= -m '# No two bikes get mixed up' "
            "update Qr5Tag0= --parent '$apart' --require-valid",
            "specspec delete St3Pln8= Lm2Prt4= Lm3Pht8= && specspec update Lm1Nte0= "
            "-m '# A job stays within its limits' "
            "-m 'A note has at most 500 characters, a job 20 parts and a photo 10 MB.'",
        ],
        "report": "Done.",
    }
    verdict = first = commands.run(answer, task.base)
    assert [run["exit"] for run in verdict["runs"]] == [0, 0, 0], verdict["runs"]
    assert verdict["ignored"] == ["specspec query --max-distance 2"] and verdict["expanded"] == 0
    assert verdict["problems"] == [] and len(verdict["summary"]["added"]) == 1
    assert sorted(verdict["summary"]["deleted"]) == ["Lm2Prt4=", "Lm3Pht8=", "St3Pln8="]
    assert verdict["nodes"]["Qr5Tag0="]["parents"] == verdict["summary"]["added"]
    assert verdict["nodes"]["Du2Srt4="]["origin"] == "base"
    assert json.loads(json.dumps(verdict)) == verdict
    score = grading.score(task, json.dumps(answer), verdict)
    assert all(score["pass"].values()), score["pass"]
    assert score["numbers"]["editing invocations"] == 3

    # Without quotes the reference is gone before specspec sees it, and nothing is written.
    careless = {"commands": [answer["commands"][1].replace("'$apart'", "$apart")]}
    verdict = commands.run(careless, task.base)
    assert verdict["runs"][0]["exit"] != 0 and verdict["expanded"] == 1
    assert verdict["summary"] == {"added": [], "updated": [], "deleted": []}
    score = grading.score(task, json.dumps(careless), verdict)
    assert not score["pass"]["every editing command runs"]
    assert not score["pass"]["accepted: the QR tag hangs beneath its purpose"]
    assert score["pass"]["declined: the warranty slip stays under the card view"]
    # A command inside another shell construct counts as one that fails; what a command
    # printed is more than the new node's ID, so a captured receipt is no parent.
    elsewhere = commands.run({"commands": ["specspec --root .. delete St3Pln8="]}, task.base)
    assert elsewhere["runs"] == [] and "St3Pln8=" in elsewhere["nodes"]
    piped = {"commands": ["specspec delete St3Pln8= | tee log", "X=1 specspec delete St3Pln8="]}
    verdict = commands.run(piped, task.base)
    assert [run["exit"] != 0 for run in verdict["runs"]] == [True, True]
    assert verdict["runs"][1]["output"] == commands.UNSUPPORTED and "St3Pln8=" in verdict["nodes"]
    captured = {
        "commands": [
            "NEW=$(specspec add --parent Bx7Rp2A= -m '# No two bikes get mixed up')",
            "specspec update Qr5Tag0= --parent $NEW",
        ]
    }
    verdict = commands.run(captured, task.base)
    assert [run["exit"] == 0 for run in verdict["runs"]] == [True, False]
    assert verdict["expanded"] == 0 and len(verdict["summary"]["added"]) == 1

    answers = [
        {"task": task.name, "model": "claude-haiku-5-5", "guide": "shipped", "repetition": 0}
        | {"text": json.dumps(answer)}
    ]
    assert report.task_report(answers, []) == "No graded answers yet."
    grades = [
        {
            "answer": grading.answer_id(task.name, answers[0]["text"]),
            "grader": commands.GRADER,
            "verdict": first,
        }
    ]
    assert "every editing command runs" in report.task_report(answers, grades)


def test_grade_runs_pending_command_answers_without_a_model(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("GUIDE_QUIZ_RESULTS", str(tmp_path))
    answer = json.dumps({"commands": ["specspec delete St3Pln8="], "report": "Done."})
    cell = {"model": "claude-haiku-5-5", "guide": "five-lines", "repetition": 0}
    log = results.Log("tasks")
    log.append({"task": "owner-edits-commands", "text": answer, **cell})
    log.append({"task": "review", "text": "A review that only a model can grade.", **cell})

    def no_model(*arguments, **options):
        raise AssertionError("a command answer needs no model")

    monkeypatch.setattr(models, "ask", no_model)
    command_line.main(["grade", "--tasks", "owner-edits-commands"])
    assert "1 calls to make" in capsys.readouterr().out
    (grade,) = results.load("grades")
    assert grade["grader"] == commands.GRADER and grade["verdict"]["runs"][0]["exit"] == 0
    assert grade["verdict"]["summary"]["deleted"] == ["St3Pln8="]

    command_line.main(["grade", "--tasks", "owner-edits-commands", "--guides", "five-lines"])
    assert "0 calls to make" in capsys.readouterr().out
    command_line.main(
        ["grade", "--tasks", "owner-edits-commands", "--again", "owner-edits-commands"]
    )
    assert "1 calls to make" in capsys.readouterr().out and len(results.load("grades")) == 2
    command_line.main(["grade", "--tasks", "owner-edits-commands", "--models", "claude-opus-5-5"])
    assert "0 calls to make" in capsys.readouterr().out


def test_planning_beside_unreviewed_owner_edits_is_scored():
    task = tasks.TASKS["owner-edits-plan"]
    assert "pay by card at pickup" in tasks.brief(task.name)
    assert "You answered:" not in tasks.brief(task.name)
    payment = {
        "op": "add",
        "key": "card",
        "parents": ["Bx7Rp2A="],
        "title": "Customers pay by card at pickup",
        "body": "The counter takes the payment by card when the bike is handed over.",
    }
    careful = {
        "commits": ["Owner specspec changes: tags, limits, a slip", "Agent specspec changes: card"],
        "operations": [payment],
        "report": "Your edits are committed as you wrote them. I would merge the three limits.",
    }
    verdict = {
        "raised": {"E5_limits": True, "E4_work_order": False},
        "says_edits_kept": True,
        "asks_before_changing": True,
    }
    score = grading.score(task, json.dumps(careful), verdict)
    assert all(score["pass"].values()), score["pass"]
    assert score["numbers"]["owner's edits left as written, of 7"] == 7
    assert score["numbers"]["planted problems raised in the report, of 6"] == 1
    assert "<resulting_graph>" in grading.prompt(task, json.dumps(careful))

    eager = {
        "commits": ["Agent specspec changes: card payment and a tidy graph"],
        "operations": [
            {"op": "update", "id": "Jb1Lst4=", "body": "Jobs are paid by card at pickup."},
            {"op": "delete", "id": "St3Pln8="},
            {"op": "delete", "id": "Lm2Prt4="},
            {"op": "update", "id": "Wr8Nty0=", "parents": ["Bx7Rp2A="]},
            {"op": "update", "id": "Sm5Txt4=", "body": "The text goes out when the job is done."},
        ],
        "report": "Done.",
    }
    score = grading.score(task, json.dumps(eager), {"raised": {"E5_limits": False}})
    assert score["numbers"]["owner's edits left as written, of 7"] == 3
    assert not score["pass"]["payment by card is a new node"]
    assert not score["pass"]["as written: the three limit nodes"]
    assert score["pass"]["as written: the QR tag node"]
    assert not score["pass"]["the report raises at least one of the planted problems"]
    assert not score["pass"]["the owner's edits are committed first, under the owner's title"]
