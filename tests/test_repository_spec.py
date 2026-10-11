"""Dogfood the real graph without fixing its choices or withdrawal history."""

import json
from pathlib import Path

from click.testing import CliRunner
from test_git import git

from specspec.cli import main
from specspec.workspace import load_snapshot, snapshot_from_files

ROOT = Path(__file__).resolve().parents[1]


def test_repository_spec_is_valid_and_has_no_missing_sources():
    snapshot = load_snapshot(ROOT)
    snapshot.require_valid()
    assert not snapshot.diagnostics
    assert {node.type for node in snapshot.nodes} == {"manifesto", "requirement", "implementation"}
    for node in snapshot.nodes:
        assert Path(node.path).parent.as_posix() == "_specspec"
        if node.type == "implementation":
            assert node.sources, f"Implementation {node.id} needs real code or verification links."
    result = CliRunner().invoke(
        main, ["--root", str(ROOT), "validate", "--warnings-as-errors", "--json"]
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["ok"]


def test_repository_graph_is_usable_as_agent_context():
    snapshot = load_snapshot(ROOT)
    graph = snapshot.require_valid()
    # Exercise a real implementation record; do not freeze its ID or withdrawal flag.
    implementation = next(node for node in snapshot.nodes if node.type == "implementation")
    result = CliRunner().invoke(main, ["--root", str(ROOT), "context", implementation.id, "--json"])
    assert result.exit_code == 0, result.output
    context = json.loads(result.output)["result"]
    required = graph.closure(implementation.id, ancestors=True) | {implementation.id}
    assert set(context["required_ids"]) == required
    assert required <= {node["id"] for node in context["nodes"]}
    assert "fingerprint" not in context


def test_repository_accepts_manual_edits_without_touching_files():
    before = load_snapshot(ROOT)
    node = next(node for node in before.nodes if node.type == "requirement")
    edited = dict(before.files)
    edited[node.path] += b"\nAn unmanaged change.\n"
    candidate = snapshot_from_files(ROOT, edited)
    assert candidate.valid
    assert candidate.graph.nodes[node.id].body.endswith("An unmanaged change.\n")
    assert load_snapshot(ROOT).files == before.files


def test_actual_repository_graph_passes_staged_validation_in_a_disposable_repo(tmp_path):
    original = load_snapshot(ROOT)
    for path, raw in original.files.items():
        target = tmp_path / path
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(raw)
    git(tmp_path, "init")
    git(tmp_path, "config", "core.autocrlf", "false")
    git(tmp_path, "add", "_specspec")
    args = ["--root", str(tmp_path), "hook", "check", "--json"]
    result = CliRunner().invoke(main, args)
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["result"]["node_count"] == len(original.nodes)

    # Deliberately corrupt only the disposable copy, then stage that exact blob.
    node = next(node for node in original.nodes if node.type == "requirement")
    (tmp_path / node.path).write_bytes(original.files[node.path].replace(b"parents:", b"unknown:"))
    git(tmp_path, "add", "_specspec")
    result = CliRunner().invoke(main, args)
    assert result.exit_code == 1
    assert any(item["code"] == "SCHEMA" for item in json.loads(result.output)["diagnostics"])
    assert load_snapshot(ROOT).files == original.files
