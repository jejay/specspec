"""The guide quiz's own logic, checked without calling a model."""

import json
import subprocess
import tomllib
from pathlib import Path

import pytest

from tools.guide_quiz import dilemmas, grading, graphs, guides, models, report, results, tasks

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


def test_guide_versions_resolve_by_name():
    names = guides.names()
    assert names[0] == guides.SHIPPED and len(names) == len(set(names))
    template = (ROOT / "src/specspec/templates/AGENTS.md").read_bytes().replace(b"\r\n", b"\n")
    assert guides.text(guides.SHIPPED).encode("utf-8") == template
    for name in names:
        text = guides.text(name)
        assert text.strip() and "\r" not in text, name
    assert guides.size("five-lines") < 1000 < guides.size("2026-11-10-before-structure-rules")
    with pytest.raises(ValueError, match="Unknown guide"):
        guides.text("no-such-guide")


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
        assert task.answer in {"graph", "operations", "text"}
        if task.rubric:
            assert tasks.rubric(task) and name in grading.SCORERS
        if task.answer == "graph":
            assert task.root_names and name in grading.PROBES
    assert grading.context().startswith("You grade one answer")


def test_answers_are_parsed_with_or_without_a_fence_and_salvaged_when_broken():
    plain = '{"nodes": [{"key": "a", "parents": ["manifesto"]}], "report": "done"}'
    assert tasks.parse(plain)["nodes"][0]["key"] == "a"
    assert tasks.parse(f"Here it is:\n```json\n{plain}\n```\nThanks")["report"] == "done"
    broken = '{"nodes": [{"key": "a", "title": "A"}, {"key": "b", "title": "B"}]], "report": "r"}'
    salvaged = tasks.parse(broken)
    assert salvaged["salvaged"] and [n["key"] for n in salvaged["nodes"]] == ["a", "b"]
    assert salvaged["report"] == "r"
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
        for record in json.loads(graphs.BASE_FILE.read_text(encoding="utf-8")):
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
        "limits": {"nodes": [], "all_three_stated": False},
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
