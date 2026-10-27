"""Physical deletion, current-schema HEAD comparisons and native overlay boundaries."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from test_git import git, setup_repository

from specspec.cli import main
from specspec.editor import editor_request
from specspec.git import git_snapshot, semantic_diff
from specspec.model import SpecError
from specspec.wire import expand_comparison
from specspec.workspace import add_node, delete_nodes, load_snapshot, recover


@pytest.fixture
def unconfigured_git(tmp_path, monkeypatch):
    """These commit fixtures must work without the owner's identity or Git setup."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(tmp_path / "absent-global-gitconfig"))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    for role in ["AUTHOR", "COMMITTER"]:
        for field in ["NAME", "EMAIL"]:
            monkeypatch.delenv(f"GIT_{role}_{field}", raising=False)
    monkeypatch.delenv("EMAIL", raising=False)


def test_default_head_delta_keeps_deleted_file_until_commit_including_staging(
    workspace, unconfigured_git
):
    root, manifesto = workspace
    snapshot, child = add_node(root, "requirement", [manifesto], "# Earlier rationale\n")
    setup_repository(root)
    path = root / snapshot.graph.nodes[child].path
    delete_nodes(root, [child])
    assert not path.exists()
    runner = CliRunner()
    for staged in [False, True]:
        if staged:
            git(root, "add", "-u", ".specspec")
        response = runner.invoke(main, ["--root", str(root), "diff", "HEAD", "--json"])
        assert response.exit_code == 0, response.output
        result = expand_comparison(json.loads(response.output)["result"])
        assert result["changes"] == [{"id": child, "kind": "removed", "fields": []}]
        assert child in {n["id"] for n in result["base"]["nodes"]}
        assert child not in {n["id"] for n in result["target"]["nodes"]}
    assert git_snapshot(root, staged=True).valid
    git(root, "commit", "-m", "Drop the experiment because its approach is no longer needed")
    assert semantic_diff(git_snapshot(root, "HEAD"), load_snapshot(root))["changes"] == []
    assert child in git_snapshot(root, "HEAD^").require_valid().nodes
    assert child not in git_snapshot(root, "HEAD").require_valid().nodes


def test_unborn_head_is_known_empty_non_git_is_incomplete_and_bad_refs_fail(workspace, without_git):
    root, manifesto = workspace
    runner = CliRunner()
    args = ["--root", str(root), "diff", "HEAD", "--json"]
    unavailable = runner.invoke(main, args)
    assert unavailable.exit_code == 1
    evidence = json.loads(unavailable.stdout)
    assert not evidence["ok"] and evidence["result"]["target"]["valid"]
    assert not evidence["result"]["impact_complete"]
    assert evidence["result"]["changes"][0]["kind"] == "unavailable"
    git(root, "init")
    result = runner.invoke(main, args)
    assert result.exit_code == 0, result.output
    diff = expand_comparison(json.loads(result.output)["result"])
    assert diff["base"]["nodes"] == [] and diff["base"]["valid"]
    assert diff["changes"] == [{"id": manifesto, "kind": "added", "fields": []}]
    assert runner.invoke(main, ["--root", str(root), "diff", "missing", "--json"]).exit_code == 2


def test_uncommitted_created_then_deleted_node_has_no_head_ghost(workspace, unconfigured_git):
    root, manifesto = workspace
    setup_repository(root)
    _, child = add_node(root, "requirement", [manifesto], "# Trial\n")
    delete_nodes(root, [child], allow_uncommitted=True)
    assert semantic_diff(git_snapshot(root, "HEAD"), load_snapshot(root))["changes"] == []


def test_deleted_open_buffer_does_not_resurrect_a_file_or_poison_other_documents(workspace):
    root, manifesto = workspace
    snapshot, child = add_node(root, "requirement", [manifesto], "# Original\n")
    node = snapshot.graph.nodes[child]
    text = (root / node.path).read_text(encoding="utf-8")
    delete_nodes(root, [child], allow_uncommitted=True)
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
    _, one = add_node(root, "requirement", [manifesto], "# One\n")
    before, two = add_node(root, "requirement", [manifesto], "# Two\n")
    original = Path.unlink
    removed = []

    def interrupted(path, *args, **kwargs):
        if path.parent == root / ".specspec":
            if removed:
                raise OSError("Interrupted deletion")
            removed.append(path)
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", interrupted)
    with pytest.raises(OSError, match="Interrupted"):
        delete_nodes(root, [one, two], allow_uncommitted=True)
    monkeypatch.setattr(Path, "unlink", original)
    removed[0].write_bytes(b"External content must not be replaced")
    with pytest.raises(SpecError, match="External edit"):
        recover(root)
    assert removed[0].read_bytes() == b"External content must not be replaced"
    assert (root / ".specspec/local/journal.json").exists()
    removed[0].unlink()
    recover(root)
    assert load_snapshot(root).files == before.files
