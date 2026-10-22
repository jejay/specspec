"""Validate current binding graphs and usable context while choices evolve."""

import json
import re
from dataclasses import replace
from pathlib import Path

import pytest
from click.testing import CliRunner

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
        main, ["--root", str(ROOT), "check", "--warnings-as-errors", "--json"]
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["ok"]


def test_repository_graph_is_usable_as_agent_context():
    snapshot = load_snapshot(ROOT)
    graph = snapshot.require_valid()
    # Exercise a real implementation record while allowing identities to evolve.
    implementation = next(node for node in snapshot.nodes if node.type == "implementation")
    result = CliRunner().invoke(
        main,
        [
            "--root",
            str(ROOT),
            "query",
            implementation.id,
            "--max-distance",
            "0",
            "--with-ancestors",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    context = json.loads(result.output)["result"]
    required = graph.closure(implementation.id, ancestors=True) | {implementation.id}
    assert set(context["selection"]["ids"]) == required
    assert context["selection"]["matched_ids"] == [implementation.id]
    assert required == {node["id"] for node in context["target"]["nodes"]}
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


def test_current_bindings_keep_revision_and_run_diaries_in_git(gantt_verifier):
    for root in [ROOT, ROOT / "example/gantt"]:
        nodes = load_snapshot(root).nodes
        gantt_verifier.assert_current_bindings(nodes)
        for node in nodes:
            # Runtime read supersession is current error handling, not withdrawn
            # design history. The shared guard above catches retired-design sections.
            assert not re.search(r"\b(?:formerly|previously)\b", node.body), node.id
            assert not re.search(r"\b\d+ (?:Python|shared UI|VS Code) tests passed", node.body)
            assert not re.search(r"\b(?:format/API|API-)\s*[1-4]\b", node.body), node.id


def test_binding_guard_allows_runtime_supersession_but_rejects_retired_design_sections(
    workspace, gantt_verifier
):
    node = load_snapshot(workspace[0]).nodes[0]
    current = replace(
        node,
        body="# Retry superseded reads\n\n"
        "Discard generation-changed results and read current input.\n",
    )
    gantt_verifier.assert_current_bindings([current])
    gantt_verifier.assert_current_bindings(
        [replace(node, body="Complete binding text can stand without a heading.\n")]
    )
    for section in ["## Superseded design", "## Resolved follow-up", "## Later correction"]:
        with pytest.raises(AssertionError):
            gantt_verifier.assert_current_bindings([replace(current, body=current.body + section)])


def test_implementation_links_use_current_descriptions_and_preserve_blob_anchors():
    snapshot = load_snapshot(ROOT)
    anchored = []
    for node in snapshot.nodes:
        for source in node.sources:
            description = source.get("symbol", "")
            assert not re.search(r"API [1-4]|migrate_command|nine RAINBOW", description)
            if "blob" in source:
                anchored.append(source)
    assert {source["mode"] for source in anchored} == {"strict", "expanding"}
