"""The worked example uses its own graph and real, inspectable Git development history."""

import json
from pathlib import Path

from click.testing import CliRunner
from test_git import git

from specspec.cli import main
from specspec.git import git_snapshot
from specspec.workspace import discover_root, initialize, load_snapshot

ROOT = Path(__file__).resolve().parents[1]
GANTT = ROOT / "example/gantt"


def invoke(root, *args):
    result = CliRunner().invoke(main, ["--root", str(root), *args, "--json"])
    return result.exit_code, json.loads(result.output)


def test_example_graph_is_independent_and_usable_as_complete_agent_context(gantt_history):
    parent = load_snapshot(ROOT)
    example = load_snapshot(gantt_history)
    graph = example.require_valid()
    assert not example.diagnostics
    assert {n.id for n in parent.nodes}.isdisjoint({n.id for n in example.nodes})
    assert discover_root(gantt_history / "history") == gantt_history
    assert (
        Path(git(gantt_history, "rev-parse", "--show-toplevel").decode().strip()) == gantt_history
    )
    implementation = next(n for n in example.nodes if n.type == "implementation")
    code, envelope = invoke(
        gantt_history, "query", implementation.id, "--max-distance", "0", "--with-ancestors"
    )
    assert code == 0 and envelope["ok"]
    required = graph.closure(implementation.id, ancestors=True) | {implementation.id}
    assert set(envelope["result"]["selection"]["ids"]) == required
    assert required == {n["id"] for n in envelope["result"]["target"]["nodes"]}
    assert "fingerprint" not in envelope["result"]


def test_example_receipts_and_all_three_real_git_stage_pairs_are_verified(gantt_verifier):
    result = gantt_verifier.verify(GANTT, history=True)
    assert result["ok"]
    assert result["verified_git_stages"] == ["01", "02", "03"]
    assert result["deleted_in_history"] == 22
    assert result["node_count"] == 22


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
    assert invoke(tmp_path, "check", "--staged")[0] == 0
    assert invoke(nested, "check", "--staged")[0] == 0

    node = next(n for n in original.nodes if n.type == "requirement")
    file = nested / node.path
    file.write_bytes(original.files[node.path].replace(b"parents:", b"unknown:"))
    assert invoke(nested, "check")[0] == 1
    assert invoke(nested, "check", "--staged")[0] == 0, "Unstaged corruption is not in the index."
    git(tmp_path, "add", "example/gantt/" + node.path)
    code, envelope = invoke(nested, "check", "--staged")
    assert code == 1 and any(d["code"] == "SCHEMA" for d in envelope["diagnostics"])
    assert invoke(tmp_path, "check", "--staged")[0] == 0, "The parent graph was not corrupted."
    assert load_snapshot(GANTT).files == original.files


def test_deleted_example_reasoning_lives_in_previous_commits_not_current_context(gantt_history):
    before = load_snapshot(gantt_history)
    previous = git_snapshot(gantt_history, "stage/01-code")
    removed = next(
        n for n in previous.nodes if n.id not in before.graph.nodes and n.type == "requirement"
    )
    args = ["query", removed.id, "--max-distance", "0", "--with-ancestors"]
    assert invoke(gantt_history, *args)[0] == 2
    code, response = invoke(
        gantt_history, *args, "--base", "stage/01-code", "--target", "stage/01-code"
    )
    assert code == 0 and removed.id in response["result"]["selection"]["matched_ids"]
    assert {n["id"] for n in response["result"]["target"]["nodes"]} == previous.graph.closure(
        removed.id, ancestors=True
    ) | {removed.id}
    assert not (gantt_history / removed.path).exists()
    assert (
        git(gantt_history, "show", f"stage/01-code:{removed.path}") == previous.files[removed.path]
    )
    assert load_snapshot(gantt_history).files == before.files
