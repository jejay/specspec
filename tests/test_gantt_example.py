"""The worked example uses its own graph and real, inspectable Git development history."""

import importlib.util
import json
from pathlib import Path

from click.testing import CliRunner
from test_git import git

from specspec.cli import main
from specspec.workspace import discover_root, initialize, load_snapshot

ROOT = Path(__file__).resolve().parents[1]
GANTT = ROOT / "example/gantt"


def invoke(root, *args):
    result = CliRunner().invoke(main, ["--root", str(root), *args, "--json"])
    return result.exit_code, json.loads(result.output)


def test_example_graph_is_independent_and_usable_as_complete_agent_context():
    parent = load_snapshot(ROOT)
    example = load_snapshot(GANTT)
    graph = example.require_valid()
    assert not example.diagnostics
    assert {n.id for n in parent.nodes}.isdisjoint({n.id for n in example.nodes})
    assert discover_root(GANTT / "history") == GANTT
    implementation = next(n for n in example.nodes if n.type == "implementation" and not n.retired)
    code, envelope = invoke(GANTT, "context", implementation.id)
    assert code == 0 and envelope["ok"]
    required = graph.closure(implementation.id, ancestors=True) | {implementation.id}
    assert set(envelope["result"]["required_ids"]) == required
    assert required <= {n["id"] for n in envelope["result"]["nodes"]}
    assert "fingerprint" not in envelope["result"]


def test_example_receipts_and_all_three_real_git_stage_pairs_are_verified():
    spec = importlib.util.spec_from_file_location(
        "gantt_history_verify", GANTT / "history/verify.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.verify(GANTT, history=True)
    assert result["ok"]
    assert result["verified_git_stages"] == ["01", "02", "03"]
    assert result["withdrawn_count"] > 0


def test_nested_graph_staged_validation_is_independent_and_reads_the_exact_index(tmp_path):
    # The maintained Gantt graph, not root graph history, is the Git corpus.
    original = load_snapshot(GANTT)
    initialize(tmp_path, "# Independent synthetic parent\n")
    for relative, raw in original.files.items():
        file = tmp_path / "example/gantt" / relative
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(raw)
    nested = tmp_path / "example/gantt"
    git(tmp_path, "init")
    git(tmp_path, "config", "core.autocrlf", "false")
    git(tmp_path, "add", "_specspec", "example/gantt/_specspec")
    assert invoke(tmp_path, "hook", "check")[0] == 0
    assert invoke(nested, "hook", "check")[0] == 0

    node = next(n for n in original.nodes if n.type == "requirement" and not n.retired)
    file = nested / node.path
    file.write_bytes(original.files[node.path].replace(b"parents:", b"unknown:"))
    assert invoke(nested, "validate")[0] == 1
    assert invoke(nested, "hook", "check")[0] == 0, "Unstaged corruption is not in the index."
    git(tmp_path, "add", "example/gantt/" + node.path)
    code, envelope = invoke(nested, "hook", "check")
    assert code == 1 and any(d["code"] == "SCHEMA" for d in envelope["diagnostics"])
    assert invoke(tmp_path, "hook", "check")[0] == 0, "The parent graph was not corrupted."
    assert load_snapshot(GANTT).files == original.files


def test_withdrawn_example_reasoning_requires_explicit_history_context():
    before = load_snapshot(GANTT)
    withdrawn = next(n for n in before.nodes if n.retired and n.type == "requirement")
    assert invoke(GANTT, "context", withdrawn.id)[0] == 1
    code, envelope = invoke(GANTT, "context", withdrawn.id, "--include-retired")
    assert code == 0
    required = before.require_valid().closure(withdrawn.id, ancestors=True) | {withdrawn.id}
    assert set(envelope["result"]["required_ids"]) == required
    assert load_snapshot(GANTT).files == before.files
