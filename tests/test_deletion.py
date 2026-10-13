"""Physical deletion, current-schema HEAD comparisons and native overlay boundaries."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from test_git import git

from specspec.cli import main
from specspec.editor import editor_request
from specspec.git import git_snapshot, semantic_diff
from specspec.model import SpecError
from specspec.workspace import add_node, delete_nodes, load_snapshot, recover


def test_default_head_delta_keeps_deleted_file_until_commit_including_staging(workspace):
    root, manifesto = workspace
    snapshot, child = add_node(root, "requirement", [manifesto], "# Earlier rationale\n", "child")
    git(root, "init")
    git(root, "config", "core.autocrlf", "false")
    git(root, "add", "_specspec")
    git(root, "commit", "-m", "Record an experiment")
    path = root / snapshot.graph.nodes[child].path
    delete_nodes(root, [child])
    assert not path.exists()
    runner = CliRunner()
    for staged in [False, True]:
        if staged:
            git(root, "add", "-u", "_specspec")
        response = runner.invoke(main, ["--root", str(root), "diff", "--base", "HEAD", "--json"])
        assert response.exit_code == 0, response.output
        result = json.loads(response.output)["result"]
        assert result["changes"] == [{"id": child, "kind": "removed", "fields": []}]
        assert child in {n["id"] for n in result["base"]["nodes"]}
        assert child not in {n["id"] for n in result["target"]["nodes"]}
    assert git_snapshot(root, staged=True).valid
    git(root, "commit", "-m", "Drop the experiment because its approach is no longer needed")
    assert semantic_diff(git_snapshot(root, "HEAD"), load_snapshot(root))["changes"] == []
    assert child in git_snapshot(root, "HEAD^").require_valid().nodes
    assert child not in git_snapshot(root, "HEAD").require_valid().nodes


def test_unborn_head_is_empty_but_arbitrary_bad_refs_and_non_git_are_not(workspace):
    root, manifesto = workspace
    runner = CliRunner()
    args = ["--root", str(root), "diff", "--base", "HEAD", "--json"]
    assert runner.invoke(main, args).exit_code == 2
    git(root, "init")
    result = runner.invoke(main, args)
    assert result.exit_code == 0, result.output
    diff = json.loads(result.output)["result"]
    assert diff["base"]["nodes"] == [] and diff["base"]["valid"]
    assert diff["changes"] == [{"id": manifesto, "kind": "added", "fields": []}]
    assert (
        runner.invoke(main, ["--root", str(root), "diff", "--base", "missing", "--json"]).exit_code
        == 2
    )


def test_uncommitted_created_then_deleted_node_has_no_head_ghost(workspace):
    root, manifesto = workspace
    git(root, "init")
    git(root, "add", "_specspec")
    git(root, "commit", "-m", "Root")
    _, child = add_node(root, "requirement", [manifesto], "# Trial\n", "trial")
    delete_nodes(root, [child])
    assert semantic_diff(git_snapshot(root, "HEAD"), load_snapshot(root))["changes"] == []


def test_deleted_open_buffer_does_not_resurrect_a_file_or_poison_other_documents(workspace):
    root, manifesto = workspace
    snapshot, child = add_node(root, "requirement", [manifesto], "# Original\n", "child")
    node = snapshot.graph.nodes[child]
    text = (root / node.path).read_text(encoding="utf-8")
    delete_nodes(root, [child])
    read = editor_request(root, {"documents": {node.path: text + "\nUnsaved retained text"}})
    assert read["snapshot"]["valid"] and not read["diagnostics"]
    assert child not in {n["id"] for n in read["snapshot"]["nodes"]}
    assert not (root / node.path).exists()
    with pytest.raises(SpecError, match="not be recreated"):
        editor_request(
            root,
            {
                "documents": {node.path: text},
                "edit": {"path": node.path, "id": child, "body": "# Recreate"},
            },
        )


def test_partial_delete_recovery_refuses_a_new_external_file(workspace, monkeypatch):
    root, manifesto = workspace
    _, one = add_node(root, "requirement", [manifesto], "# One\n", "one")
    before, two = add_node(root, "requirement", [manifesto], "# Two\n", "two")
    original = Path.unlink
    removed = []

    def interrupted(path, *args, **kwargs):
        if path.parent == root / "_specspec":
            if removed:
                raise OSError("Interrupted deletion")
            removed.append(path)
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", interrupted)
    with pytest.raises(OSError, match="Interrupted"):
        delete_nodes(root, [one, two])
    monkeypatch.setattr(Path, "unlink", original)
    removed[0].write_bytes(b"External content must not be replaced")
    with pytest.raises(SpecError, match="External edit"):
        recover(root)
    assert removed[0].read_bytes() == b"External content must not be replaced"
    assert (root / ".specspec-local/journal.json").exists()
    removed[0].unlink()
    recover(root)
    assert load_snapshot(root).files == before.files
