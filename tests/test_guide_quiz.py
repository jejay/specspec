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
    scorecard,
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
            own = grading.SCORERS[name] is not grading.score_drawing
            assert task.root_names and (name in grading.PROBES or own)
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
        "relation",
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
    plan = (
        '{"commits": ["Owner specspec changes: x"], "operations": [{"op": "delete", "id": "A="}]]}'
    )
    assert tasks.parse(plan)["commits"] == ["Owner specspec changes: x"]
    assert tasks.parse(plan)["operations"] == [{"op": "delete", "id": "A="}]


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
            "intention_node": "remind",
            "way_node": "sms",
            "separate_nodes": True,
            "intention_text_free_of_way": True,
        },
        "week": {
            "intention_node": "week",
            "way_node": "week",
            "separate_nodes": False,
            "intention_text_free_of_way": False,
        },
        "double_booking_own_node": False,
        "limits": {"nodes": ["desk", "week"], "all_three_stated": False},
        "paper_phone": {"nodes": [], "separate_nodes": False},
        "work_order": {"order_nodes": ["plan"], "order_in_text": []},
        "category_nodes": [],
        "historic_contrast": [],
        "root_children_ways": ["week"],
        "reminder_wording": "absent",
        "label_titles": [],
        "blended_nodes": [{"key": "week", "why": "the week view and its grid"}],
        "report": {"names_own_conclusions": True, "names_open_points": "true"},
    }
    text = json.dumps({**answer, "report": "Done."})
    score = grading.score(tasks.TASKS["clinic"], text, verdict)
    passed = score["pass"]
    assert passed["graph passes the structure check"]
    assert passed["what the owner holds as fixed is a node of its own near the root"]
    assert passed["the same, directly under the manifesto"]
    reasoned = drawing(
        ("known", "requirement", ["manifesto"], "The contractor can support the app", "As now."),
        ("pg", "requirement", ["known"], "Store data in PostgreSQL", "The contractor's."),
        ("eu", "requirement", ["manifesto"], "Keep patient data in the EU", "All of it."),
        ("deep", "requirement", ["pg"], "Back the database up nightly", "To the same server."),
    )
    reasoned = grading.score(
        tasks.TASKS["clinic"], json.dumps({**reasoned, "report": ""}), verdict
    )["pass"]
    assert reasoned["what the owner holds as fixed is a node of its own near the root"]
    assert not reasoned["the same, directly under the manifesto"]
    assert not grading.near_root(
        {"deep": {"parents": ["pg"]}, "pg": {"parents": ["known"]}}, "deep"
    )
    assert passed["a conclusion descends from the constraint that shaped it"]
    assert passed["a suggested technology is a requirement of its own"]
    assert not passed["no build order in node text"]
    assert not passed["no way that could be another hangs directly under the manifesto"]
    assert passed["the report names the agent's own conclusions"]
    assert passed["the report names open points"]
    assert score["counts"]["the same, with the intention also in the manifesto"] == [1, 2]
    assert score["numbers"]["nodes that blend statements"] == 1
    assert score["numbers"]["nodes that state the limits"] == 2
    assert "nodes that record a conclusion of the agent's own" not in score["numbers"]
    read = "the report names the intentions the agent read into the owner's words"
    assert read not in passed
    counted = {
        **verdict,
        "own_conclusion_nodes": ["gateway", "no-such-node", "gateway"],
        "report": {"names_read_intentions": True},
    }
    counted = grading.score(tasks.TASKS["clinic"], text, counted)
    assert counted["numbers"]["nodes that record a conclusion of the agent's own"] == 1
    assert counted["pass"][read]
    assert grading.score(tasks.TASKS["clinic"], "not json", verdict) is None

    # A verdict that an earlier rubric produced keeps its meaning under the earlier names.
    earlier = {
        **verdict,
        "reminder": {
            "outcome_node": "remind",
            "means_node": "sms",
            "separate_nodes": True,
            "outcome_text_free_of_means": True,
        },
        "own_choice_nodes": ["gateway"],
        "report": {"names_own_choices": True},
    }
    earlier.pop("root_children_ways")
    earlier = grading.score(
        tasks.TASKS["clinic"], text, {**earlier, "root_children_means": ["week"]}
    )
    assert earlier["counts"] == score["counts"]
    assert earlier["pass"]["the report names the agent's own conclusions"]
    assert not earlier["pass"]["no way that could be another hangs directly under the manifesto"]
    assert earlier["numbers"]["nodes that record a conclusion of the agent's own"] == 1

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
        "intention_Wk7fTq0_text_names_way": False,
        "yes": {"nodes": [], "only_appended_to_existing": True},
        "email": {"node": "mail", "is_added_node": True},
        "signin_sentence": "left_unmentioned",
        "report": {"names_removed_nodes": True},
    }
    passed = grading.score(tasks.TASKS["revise"], json.dumps(operations), verdict)["pass"]
    assert passed["resulting graph passes the structure check"]
    assert passed["the intention is kept and names no way"]
    assert passed["the day list is a new node directly under that intention"]
    assert passed["the colour node is kept and applies to the day list"]
    assert passed["e-mail is under the reminder intention and beside the text message"]
    assert passed["e-mail descends from the EU constraint"]
    assert passed["the replaced conclusion is deleted"]
    assert not passed["the reply is recorded in a new node"]
    assert passed["the stray sentence in a committed node stays where it is"]
    moved = {**verdict, "signin_sentence": "moved_to_own_node"}
    moved = grading.score(tasks.TASKS["revise"], json.dumps(operations), moved)
    assert not moved["pass"]["the stray sentence in a committed node stays where it is"]
    phones = grading.score(tasks.TASKS["revise-phones"], json.dumps(operations), verdict)
    assert "the replaced conclusion is deleted" not in phones["pass"]


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
    first = "the owner's edits are committed first, under the owner's title"
    assert first not in review["pass"]
    look = tasks.TASKS["owner-edits-review"]
    assert "before the owner answers" in tasks.brief(look.name)
    kept = {"commits": ["Owner specspec changes: limits and tags"], "report": "Six points."}
    score = grading.score(look, json.dumps(kept), {"identified": {"E5_limits": True}})
    assert score["pass"][first] and score["pass"]["the graph is left as it is"]
    assert score["pass"]["no commit of the agent's own before the owner answers"]
    assert score["numbers"]["planted problems found"] == 1
    hasty = {
        "commits": ["Agent specspec changes: tidy"],
        "operations": [{"op": "delete", "id": "St3Pln8="}],
    }
    score = grading.score(look, json.dumps(hasty), {})
    assert not score["pass"][first] and not score["pass"]["the graph is left as it is"]
    assert not score["pass"]["no commit of the agent's own before the owner answers"]

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


def test_planning_beside_hand_committed_and_sealed_nodes_is_scored():
    for name in ("manual-plan", "sealed-plan", "sealed-feature"):
        brief = tasks.brief(name)
        assert "`git status` is clean" in brief and "8a1f3b6 Agent specspec changes:" in brief
    assert "The owner made the commit `7be4f10` by hand" in tasks.brief("manual-plan")
    assert "shows no specification changes" in tasks.brief("sealed-plan")
    answer = {
        "commits": ["Agent specspec changes: customers pay by card at pickup"],
        "operations": [
            {
                "op": "add",
                "key": "card",
                "parents": ["Bx7Rp2A="],
                "title": "Customers pay by card at pickup",
                "body": "The counter takes the payment by card.",
            }
        ],
        "report": "I would merge the three limits; tell me whether you want that.",
    }
    raised = {"raised": {"E5_limits": True, "E4_work_order": False}, "asks_before_changing": True}
    manual = grading.score(tasks.TASKS["manual-plan"], json.dumps(answer), raised)
    assert all(manual["pass"].values()), manual["pass"]
    assert manual["numbers"]["owner's nodes left as written, of 7"] == 7
    assert manual["numbers"]["planted problems raised in the report, of 6"] == 1
    assert "the owner's edits are committed first, under the owner's title" not in manual["pass"]

    sealed = grading.score(tasks.TASKS["sealed-plan"], json.dumps(answer), raised)
    assert not sealed["pass"]["the report makes no remark about the sealed nodes"]
    assert sealed["numbers"]["remarks about sealed nodes in the report, of 6"] == 1
    assert sealed["numbers"]["sealed nodes left as written, of 7"] == 7
    quiet = grading.score(tasks.TASKS["sealed-plan"], json.dumps(answer), {"raised": {}})
    assert all(quiet["pass"].values()), quiet["pass"]
    owner = {**answer, "commits": ["Owner specspec changes: nothing", *answer["commits"]]}
    owner = grading.score(tasks.TASKS["sealed-plan"], json.dumps(owner), {})
    assert not owner["pass"]["no commit is made in the owner's name"]


def test_a_request_that_needs_a_sealed_node_changed_is_scored():
    task = tasks.TASKS["sealed-feature"]
    assert "NFC stickers" in tasks.brief(task.name) and task.name in grading.AUTOMATIC
    split = {
        "operations": [
            {
                "op": "update",
                "id": "Qr5Tag0=",
                "title": "No two bikes get mixed up",
                "body": "Every bike in the shop can be told apart from every other bike.",
            },
            {
                "op": "add",
                "key": "sticker",
                "parents": ["Qr5Tag0="],
                "title": "Put an NFC sticker on every bike",
                "body": "Each bike gets a sticker at drop-off.",
            },
        ],
        "report": "The request needed the sealed node about the QR tag changed.",
    }
    score = grading.score(task, json.dumps(split))
    assert all(score["pass"].values()), score["pass"]
    assert score["numbers"]["other sealed nodes left as written, of 6"] == 6

    beside = {
        "operations": [
            {
                "op": "add",
                "key": "sticker",
                "parents": ["Bx7Rp2A="],
                "title": "Put an NFC sticker on every bike",
            },
            {"op": "delete", "id": "St3Pln8="},
        ],
        "report": "Added the stickers.",
    }
    score = grading.score(task, json.dumps(beside))
    assert score["pass"]["the NFC sticker is recorded"]
    assert not score["pass"]["its intention is a node of its own above the NFC sticker"]
    assert not score["pass"]["the QR tag is gone from the graph"]
    assert not score["pass"]["every other sealed node stays as written"]
    assert not score["pass"]["the report names the sealed node it changed"]
    assert score["numbers"]["other sealed nodes left as written, of 6"] == 5


def test_the_scorecard_names_criteria_that_the_scorers_produce():
    drawing = json.dumps({"nodes": [], "report": ""})
    plan = json.dumps({"operations": [], "report": ""})
    ran = {"nodes": {}, "summary": {}, "runs": []}
    samples = {
        "clinic": grading.score(tasks.TASKS["clinic"], drawing, {"own_conclusion_nodes": []}),
        "bakery": grading.score(tasks.TASKS["bakery"], drawing, {"own_conclusion_nodes": []}),
        "toolshed": grading.score(tasks.TASKS["toolshed"], drawing, {}),
        "revise": grading.score(tasks.TASKS["revise"], plan, {}),
        "discuss": grading.score(tasks.TASKS["discuss"], "A reply.", {"says_how_it_reads": 0}),
        "discuss-game": grading.score(tasks.TASKS["discuss-game"], "A reply.", {}),
        "owner-edits-review": grading.score(tasks.TASKS["owner-edits-review"], plan, {}),
        "owner-edits-commands": grading.score(
            tasks.TASKS["owner-edits-commands"], json.dumps({"commands": ["x"]}), ran
        ),
    }
    for name in ("owner-edits-plan", "manual-plan", "sealed-plan", "sealed-feature"):
        samples[name] = grading.score(tasks.TASKS[name], plan, {})
    rows = [row for _, group in scorecard.GROUPS for row in group]
    assert len({row.label for row in rows}) == len(rows) and all(row.meaning for row in rows)
    for row in rows:
        assert row.kind == "dilemmas" or row.tasks, row.label
        for name in row.tasks:
            assert any(key in samples[name][row.kind] for key in row.keys), (row.label, name)

    item = next(item for item in dilemmas.items() if item["topic"] == "relation")
    answered = [
        {
            "model": "m",
            "guide": "g",
            "item": item["id"],
            "repetition": n,
            "picked": n,
            "correct": n == 0,
        }
        for n in range(2)
    ]
    answered.append({**answered[0], "item": "retired"})
    scores = {
        ("discuss", "m", "g"): [samples["discuss"], None],
        ("clinic", "m", "g"): [samples["clinic"]],
    }
    table = scorecard.table(scores, answered, "m", ["g", "other"])
    lines = {line[:62].strip(): line[62:].split() for line in table.splitlines()}
    assert lines["Gives an overview of its understanding"] == ["0", "of", "1", "-"]
    assert lines["Nodes per graph"] == ["0.0", "(n=1)", "-"]
    assert lines["Your way and its intention become two nodes"] == ["0", "of", "2", "-"]
    relation = "Right answer in short cases about intention and conclusion"
    assert lines[relation] == ["50", "%", "of", "2", "-"]
    assert lines["Right answer in the other short cases"] == ["-", "-"]
    assert table.splitlines()[4].startswith("Telling intention from conclusion")
    assert "What the rows mean" in table and "  A: g" in table


def test_a_round_of_tandem_planning_is_scored():
    task = tasks.TASKS["discuss"]
    assert "What do you think?" in tasks.brief(task.name)
    verdict = {
        "leaves_graph": True,
        "about_product": True,
        "overview": True,
        "questions": 4,
        "questions_with_own_answer": 3,
        "separates_intention_from_conclusion": True,
        "challenges_a_conclusion": False,
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
    assert score["pass"]["it tells an intention apart from the way the owner named"]
    assert not score["pass"]["it challenges a conclusion the owner suggested"]
    stated = "it says which statements it reads as fixed and which as open"
    assert stated not in score["pass"]
    assert grading.score(task, "Fine.", {**verdict, "says_how_it_reads": True})["pass"][stated]
    earlier = {"separates_want_from_way": True, "challenges_a_choice": True}
    earlier = grading.score(task, "Fine.", earlier)["pass"]
    assert earlier["it tells an intention apart from the way the owner named"]
    assert earlier["it challenges a conclusion the owner suggested"]
    silent = grading.score(task, "Done.", {**verdict, "questions": 0, "leaves_graph": False})
    assert not silent["pass"]["it asks questions and answers most of them itself"]
    assert not silent["pass"]["the answer leaves the graph as it is"]
    assert "<review>" in grading.prompt(task, "Done.")


def test_a_discussion_with_planted_statements_is_scored():
    task = tasks.TASKS["discuss-game"]
    brief = tasks.brief(task.name)
    assert "nobody learns who is on which side" in brief and "written in Kotlin" in brief
    verdict = {
        "leaves_graph": True,
        "overview": True,
        "timeline": {"raises_conflict": True, "proposes_alternative": False},
        "kotlin": "states_reading",
        "offline": "kept",
        "intentions_named": {"room_code": False, "timer": True, "host_phone": "true"},
        "says_how_it_reads": True,
        "challenges_manifesto": False,
        "manifesto_wording": True,
        "questions": 2,
        "questions_with_own_answer": 1,
    }
    score = grading.score(task, "The timeline gives the roles away.", verdict)
    passed = score["pass"]
    assert passed["it raises the statement that works against the manifesto"]
    assert not passed["it proposes another conclusion for that intention"]
    assert not passed["it asks whether an unclear statement is fixed"]
    assert passed["it asks that, or says how it reads the statement"]
    assert passed["it keeps what the circumstances fix"]
    assert passed["it leaves the manifesto's intention alone"]
    assert passed["it points out a conclusion in the manifesto's wording"]
    assert passed["it asks questions and answers most of them itself"]
    assert score["counts"]["the intention behind a stated way is named"] == [2, 3]
    empty = grading.score(task, "Sure.", {})["pass"]
    assert empty["it leaves the manifesto's intention alone"]
    assert not empty["it raises the statement that works against the manifesto"]


def test_a_drawing_with_unsaid_intentions_is_scored():
    task = tasks.TASKS["toolshed"]
    brief = tasks.brief(task.name)
    assert "A web app with a calendar view" in brief and "I would build it with Vue." in brief
    answer = drawing(
        ("server", "requirement", ["manifesto"], "Run on the office server", "Nothing else."),
        ("known", "requirement", ["manifesto"], "The library knows who has a tool", "Always."),
        ("scan", "requirement", ["known"], "Members scan the tool's code", "Out and back."),
        ("sheet", "requirement", ["manifesto"], "Print a sheet for the shed door", "On Mondays."),
        ("vue", "requirement", ["manifesto"], "Build the pages with Vue", "As suggested."),
    )
    separate = {"separate_nodes": True, "intention_text_free_of_way": True}
    verdict = {
        "scan": {"intention_node": "known", "way_node": "scan", **separate},
        "sheet": {"intention_node": None, "way_node": "sheet", "separate_nodes": False},
        "due": {"intention_node": None, "way_node": None},
        "broken": {"intention_node": "known", "way_node": "scan", **separate},
        "server": {"node": "server", "own_node": True},
        "vue": {"node": "vue", "reading": "asked_or_flagged"},
        "limits": {"nodes": [], "all_three_stated": False},
        "own_conclusion_nodes": ["vue", "nothing"],
        "report": {"names_read_intentions": True, "points_out_manifesto_conclusion": False},
    }
    score = grading.score(task, json.dumps({**answer, "report": "Done."}), verdict)
    unsaid = "an intention the owner left unsaid is a node above the owner's way"
    assert score["counts"][unsaid] == [1, 2]
    said = "the same, with the intention in the manifesto or in the owner's sentence"
    assert score["counts"][said] == [1, 2]
    passed = score["pass"]
    assert passed["graph passes the structure check"]
    assert passed["what the owner holds as fixed is a node of its own near the root"]
    assert passed["the report says how it read a statement of unclear firmness"]
    assert passed["the report names the intentions the agent read into the owner's words"]
    assert not passed["the report points out a conclusion in the manifesto's wording"]
    assert score["numbers"]["nodes that record a conclusion of the agent's own"] == 1
    assert "<graph>" in grading.prompt(task, json.dumps({**answer, "report": "Done."}))


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

    # An answer to an earlier wording of the brief is no longer judged.
    earlier = {"task": "owner-edits-commands", "brief": "an-earlier-word", **cell}
    log.append({**earlier, "text": answer + " "})
    log.append({**earlier, "text": answer + "  ", "brief": tasks.mark("owner-edits-commands")})
    command_line.main(["grade", "--tasks", "owner-edits-commands"])
    assert "1 calls to make" in capsys.readouterr().out

    # The grader's time is spent on the first repetitions alone when that is asked for.
    log.append({"task": "owner-edits-commands", "text": answer + "\n", **cell, "repetition": 7})
    command_line.main(["grade", "--tasks", "owner-edits-commands", "--first", "5"])
    assert "0 calls to make" in capsys.readouterr().out
    command_line.main(["grade", "--tasks", "owner-edits-commands", "--first", "8"])
    assert "1 calls to make" in capsys.readouterr().out


def test_an_answer_counts_for_the_brief_it_was_given():
    records = [
        {"task": "discuss"},
        {"task": "discuss", "brief": tasks.mark("discuss")},
        {"task": "discuss", "brief": "an-earlier-word"},
        {"task": "a-task-of-the-past", "brief": "its-wording"},
        {"task": "a-task-of-the-past"},
    ]
    assert tasks.current(records) == [records[0], records[1], records[4]]
    assert len(tasks.mark("discuss")) == 12 and tasks.mark("discuss") != tasks.mark("bakery")


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
