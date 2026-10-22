"""Whole-descendant deletion and pre-write warnings, independent of review states."""

import json
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest
from click.testing import CliRunner
from test_git import git

from specspec import cli as cli_module
from specspec.cli import main
from specspec.deletion import deletion_plan, deletion_warnings
from specspec.git import git_snapshot, semantic_diff
from specspec.model import SpecError
from specspec.workspace import (
    add_node,
    delete_nodes,
    initialize,
    load_snapshot,
    new_node,
    serialize,
    snapshot_from_files,
    update_node,
)


def branch(root, manifesto):
    _, left = add_node(root, "requirement", [manifesto], "# Left\n")
    _, right = add_node(root, "requirement", [manifesto], "# Right\n")
    _, full = add_node(root, "requirement", [left], "# Full child\n")
    _, shared = add_node(root, "requirement", [left, right], "# Shared child\n")
    _, other = add_node(root, "requirement", [right], "# Outside parent\n")
    _, deep = add_node(root, "requirement", [shared, other], "# Deeper partial\n")
    before, code = add_node(root, "implementation", [full, deep], "# Shared realization\n")
    return before, left, right, full, shared, deep, code, other


def commit(root):
    git(root, "init")
    git(root, "config", "core.autocrlf", "false")
    git(root, "add", "_specspec")
    git(root, "commit", "-m", "Keep original specification")


def replace_leaf_identity(root, node):
    """A valid manual ID replacement can still be a Git-detected file rename."""
    replacement = new_node(node.type, node.parents, node.body)
    replacement = replace(node, id=replacement.id, path=replacement.path)
    (root / replacement.path).write_bytes(serialize(replacement))
    (root / node.path).unlink()
    load_snapshot(root).require_valid()
    return replacement.id, replacement.path


def invoke(root, *args, **kwargs):
    result = CliRunner().invoke(main, ["--root", str(root), "delete", *args, "--json"], **kwargs)
    return result, json.loads(result.stdout)


def test_cli_removes_full_and_partial_children_at_all_depths_and_reports_all_ids(workspace):
    root, manifesto = workspace
    before, left, right, full, shared, deep, code, other = branch(root, manifesto)
    commit(root)
    chosen = {left, full, shared, deep, code}
    result, response = invoke(root, left)
    assert result.exit_code == 0, result.output
    assert not response["diagnostics"]
    assert set(response["result"]["changed_ids"]) == chosen
    assert set(response["result"]["deleted_ids"]) == chosen
    after = load_snapshot(root)
    assert set(after.require_valid().nodes) == {manifesto, right, other}
    assert after.files == {p: raw for p, raw in before.files.items() if p in after.files}
    assert all(not (root / before.graph.nodes[key].path).exists() for key in chosen)
    for staged in [False, True]:
        if staged:
            git(root, "add", "-u", "_specspec")
        diff = semantic_diff(git_snapshot(root, "HEAD"), load_snapshot(root))
        assert chosen == {c["id"] for c in diff["changes"] if c["kind"] == "removed"}
    git(root, "commit", "-m", "Delete the branch because its assumptions no longer apply")
    assert not semantic_diff(git_snapshot(root, "HEAD"), load_snapshot(root))["changes"]
    assert chosen <= set(git_snapshot(root, "HEAD^").require_valid().nodes)


def test_overlapping_roots_deduplicate_shared_files_without_deleting_outside_parents(
    workspace, monkeypatch
):
    root, manifesto = workspace
    before, left, right, full, shared, deep, code, other = branch(root, manifesto)
    commit(root)
    removed = []
    original = Path.unlink

    def unlink(path, *args, **kwargs):
        if path.parent == root / "_specspec":
            removed.append(path.name)
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", unlink)
    after = delete_nodes(root, [left, shared, full])
    assert len(removed) == len(set(removed)) == 5
    assert set(after.require_valid().nodes) == {manifesto, right, other}
    assert after.files == {p: raw for p, raw in before.files.items() if p in after.files}


@pytest.mark.parametrize(
    "kind,status",
    [
        ("untracked", "??"),
        ("staged-added", "A "),
        ("unstaged", " M"),
        ("staged-modified", "M "),
        ("comment-only", " M"),
        ("renamed", "R "),
        ("ignored", "!!"),
        ("staged-mode", "M "),
    ],
)
def test_only_uncommitted_descendant_warns_even_when_staged_or_semantically_unchanged(
    workspace, kind, status
):
    root, manifesto = workspace
    before, left, right, full, shared, deep, code, other = branch(root, manifesto)
    commit(root)
    target = code if kind == "renamed" else shared
    if kind in {"untracked", "staged-added", "ignored"}:
        _, target = add_node(root, "requirement", [shared, other], "# Uncommitted child\n")
        if kind == "ignored":
            (root / ".gitignore").write_text("_specspec/\n", encoding="utf-8")
    path = load_snapshot(root).graph.nodes[target].path
    if kind in {"unstaged", "staged-modified"}:
        update_node(root, target, body="# Uncommitted changed child\n")
    elif kind == "comment-only":
        raw = (root / path).read_bytes()
        (root / path).write_bytes(raw.replace(b"type: requirement", b"type: requirement # pending"))
        assert (
            load_snapshot(root).graph.nodes[target].semantic()
            == before.graph.nodes[target].semantic()
        )
    elif kind == "renamed":
        target, path = replace_leaf_identity(root, before.graph.nodes[target])
    if kind in {"staged-added", "staged-modified", "renamed"}:
        git(root, "add", "-A", "_specspec")
    elif kind == "staged-mode":
        git(root, "config", "core.filemode", "false")
        git(root, "update-index", "--chmod=+x", path)
    before = load_snapshot(root)
    result, preview = invoke(root, left, "--dry-run")
    assert result.exit_code == 0, result.output
    assert preview["result"]["uncommitted"] == [{"id": target, "path": path, "status": status}]
    assert preview["diagnostics"][0]["node_id"] == target
    assert preview["diagnostics"][0]["severity"] == "warning"
    refused, response = invoke(root, left)
    assert refused.exit_code == 1, refused.output
    assert response["result"] == preview["result"]
    assert response["diagnostics"][-1]["code"] == "DELETE_CONFIRMATION"
    assert load_snapshot(root).files == before.files
    assert not (root / ".specspec-local/journal.json").exists()
    allowed, deleted = invoke(root, left, "--yes")
    assert allowed.exit_code == 0, allowed.output
    assert {d["node_id"] for d in deleted["diagnostics"]} == {target}
    assert "uncommitted" in allowed.stderr
    assert target not in load_snapshot(root).require_valid().nodes
    assert {manifesto, right, other} == set(load_snapshot(root).require_valid().nodes)


def test_new_or_changed_requested_root_warns_and_source_only_edits_do_not(workspace):
    root, manifesto = workspace
    _, left, right, full, shared, deep, code, other = branch(root, manifesto)
    (root / "code.py").write_text("original\n", encoding="utf-8")
    update_node(root, code, sources=[{"path": "code.py"}])
    commit(root)
    git(root, "add", "code.py")
    git(root, "commit", "-m", "Commit realization")
    (root / "code.py").write_text("changed\n", encoding="utf-8")
    assert not deletion_warnings(deletion_plan(load_snapshot(root), [left]))
    update_node(root, left, body="# Uncommitted root\n")
    plan = deletion_plan(load_snapshot(root), [left])
    assert {n["id"] for n in plan["uncommitted"]} == {left}
    # A staged different blob still warns when saved files are back at HEAD.
    git(root, "add", "_specspec")
    update_node(root, left, body="# Left\n")
    assert not semantic_diff(git_snapshot(root, "HEAD"), load_snapshot(root))["changes"]
    assert {n["id"] for n in deletion_plan(load_snapshot(root), [left])["uncommitted"]} == {left}


def test_no_git_and_unborn_head_warn_instead_of_claiming_committed_nodes(workspace):
    root, manifesto = workspace
    _, child = add_node(root, "requirement", [manifesto], "# New\n")
    before = load_snapshot(root)
    result, preview = invoke(root, child, "--dry-run")
    assert result.exit_code == 0
    assert preview["result"]["git_available"] is False
    assert preview["diagnostics"][0]["code"] == "DELETE_GIT_UNAVAILABLE"
    assert preview["result"]["uncommitted"][0]["status"] == "unknown"
    with pytest.raises(SpecError, match="Confirm"):
        delete_nodes(root, [child])
    assert load_snapshot(root).files == before.files
    git(root, "init")
    result, preview = invoke(root, child, "--dry-run")
    assert result.exit_code == 0
    assert preview["result"]["git_available"] is True
    assert preview["result"]["uncommitted"][0]["status"] == "??"


def test_warnings_are_delivered_before_the_first_unlink_even_with_json_yes(workspace, monkeypatch):
    root, manifesto = workspace
    _, child = add_node(root, "requirement", [manifesto], "# New\n")
    messages = []
    original_emit, original_unlink = cli_module.emit, Path.unlink

    def emit(result, diagnostics=None, **kwargs):
        messages.extend(diagnostics or [])
        return original_emit(result, diagnostics, **kwargs)

    def unlink(path, *args, **kwargs):
        if path.parent == root / "_specspec":
            assert any(d.node_id == child and d.severity == "warning" for d in messages)
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(cli_module, "emit", emit)
    monkeypatch.setattr(Path, "unlink", unlink)
    result, response = invoke(root, child, "--yes")
    assert result.exit_code == 0, result.output
    assert response["ok"] and response["diagnostics"]


@pytest.mark.parametrize("answer,deleted", [("n", False), ("y", True)])
def test_human_terminal_confirmation_can_cancel_or_confirm_the_whole_action(
    workspace, monkeypatch, answer, deleted
):
    root, manifesto = workspace
    before, left, right, full, shared, deep, code, other = branch(root, manifesto)
    commit(root)
    update_node(root, deep, body="# Pending deeper descendant\n")
    before = load_snapshot(root)
    monkeypatch.setattr(cli_module, "interactive_stdin", lambda: True)
    result = CliRunner().invoke(main, ["--root", str(root), "delete", left], input=answer + "\n")
    assert "uncommitted" in result.stderr
    assert "all 5 nodes, including shared descendants" in result.stdout
    if deleted:
        assert result.exit_code == 0, result.output
        assert set(load_snapshot(root).require_valid().nodes) == {manifesto, right, other}
    else:
        assert result.exit_code == 1 and "cancelled" in result.stderr
        assert load_snapshot(root).files == before.files
    assert not (root / ".specspec-local/journal.json").exists()


@pytest.mark.parametrize("change", ["descendant", "warning", "rename"])
def test_reviewed_scope_is_recomputed_and_refused_before_writes_if_it_changes(workspace, change):
    root, manifesto = workspace
    before, left, right, full, shared, deep, code, other = branch(root, manifesto)
    commit(root)
    plan = deletion_plan(before, [left])
    if change == "descendant":
        add_node(root, "requirement", [shared, other], "# New child\n")
    elif change == "warning":
        update_node(root, deep, body="# Now uncommitted\n")
    else:
        replace_leaf_identity(root, before.graph.nodes[code])
    before = load_snapshot(root)
    result, response = invoke(root, left, "--yes", "--reviewed-plan", "-", input=json.dumps(plan))
    assert result.exit_code == 1, result.output
    assert response["diagnostics"][0]["code"] == "DELETE_PLAN_CHANGED"
    assert load_snapshot(root).files == before.files
    assert not (root / ".specspec-local/journal.json").exists()


def test_unmerged_index_and_git_assessment_errors_are_warned_before_deletion(
    workspace, monkeypatch
):
    root, manifesto = workspace
    before, left, right, full, shared, deep, code, other = branch(root, manifesto)
    commit(root)
    path = before.graph.nodes[deep].path
    blob = git(root, "rev-parse", f"HEAD:{path}").decode("ascii").strip()
    data = f"0 {blob}\t{path}\n" + "".join(
        f"100644 {blob} {stage}\t{path}\n" for stage in [1, 2, 3]
    )
    subprocess.run(
        ["git", "-C", str(root), "update-index", "--index-info"], input=data.encode(), check=True
    )
    plan = deletion_plan(before, [left])
    assert plan["uncommitted"] == [{"id": deep, "path": path, "status": "UU"}]
    from specspec import deletion as module

    original = module.run_git

    def unavailable(root, *args):
        if "status" in args:
            raise SpecError([cli_module.Diagnostic("GIT", "Status assessment failed")], 2)
        return original(root, *args)

    monkeypatch.setattr(module, "run_git", unavailable)
    plan = deletion_plan(before, [left])
    assert not plan["git_available"] and len(plan["uncommitted"]) == 5
    assert all(d.code == "DELETE_GIT_UNAVAILABLE" for d in deletion_warnings(plan))
    assert load_snapshot(root).files == before.files


def test_detached_linked_worktree_assessment_uses_its_own_index(workspace, tmp_path):
    root, manifesto = workspace
    before, left, right, full, shared, deep, code, other = branch(root, manifesto)
    commit(root)
    linked = tmp_path / "linked"
    git(root, "worktree", "add", "--detach", str(linked), "HEAD")
    try:
        before = update_node(linked, deep, body="# Linked pending child\n")
        plan = deletion_plan(before, [left])
        assert {n["id"] for n in plan["uncommitted"]} == {deep}
        assert not deletion_plan(load_snapshot(root), [left])["uncommitted"]
    finally:
        git(root, "worktree", "remove", "--force", str(linked))


def test_noninteractive_text_refuses_uncommitted_deletion_even_if_stdin_says_yes(workspace):
    root, manifesto = workspace
    before, child = add_node(root, "requirement", [manifesto], "# New\n")
    result = CliRunner().invoke(main, ["--root", str(root), "delete", child], input="y\n")
    assert result.exit_code == 1 and "No files removed" in result.stderr
    assert load_snapshot(root).files == before.files


def test_unchanged_reviewed_plan_succeeds_but_invalid_plan_input_is_rejected(workspace):
    root, manifesto = workspace
    before, left, right, full, shared, deep, code, other = branch(root, manifesto)
    commit(root)
    plan = deletion_plan(before, [left])
    for text in ["[]", "{invalid", json.dumps({"git_available": 1})]:
        result, response = invoke(root, left, "--yes", "--reviewed-plan", "-", input=text)
        assert result.exit_code == 2 and response["diagnostics"][0]["code"] == "DELETE_PLAN"
        assert load_snapshot(root).files == before.files
    result, response = invoke(root, left, "--yes", "--reviewed-plan", "-", input=json.dumps(plan))
    assert result.exit_code == 0, result.output
    assert response["result"]["deleted_ids"] == plan["deleted_ids"]


def test_nested_literal_project_paths_are_scoped_and_plan_does_not_touch_index(tmp_path):
    git(tmp_path, "init")
    git(tmp_path, "config", "core.autocrlf", "false")
    root = tmp_path / "nested [literal] project"
    root.mkdir()
    before = initialize(root, "# Root\n")
    manifesto = before.nodes[0].id
    before, child = add_node(root, "requirement", [manifesto], "# Child\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-m", "Commit nested graph")
    index = (tmp_path / ".git/index").read_bytes()
    before = update_node(root, child, body="# Nested uncommitted\n")
    plan = deletion_plan(before, [child])
    assert plan["uncommitted"] == [
        {"id": child, "path": before.graph.nodes[child].path, "status": " M"}
    ]
    assert (tmp_path / ".git/index").read_bytes() == index


def test_long_chain_plan_is_iterative_and_invalid_requests_do_not_remove_files(workspace):
    root, manifesto = workspace
    nodes = [load_snapshot(root).nodes[0]]
    for _ in range(1300):
        nodes.append(new_node("requirement", [nodes[-1].id], "# Deep\n"))
    snapshot = snapshot_from_files(root, {n.path: serialize(n) for n in nodes})
    plan = deletion_plan(snapshot, [nodes[1].id, nodes[500].id])
    assert len(plan["deleted_ids"]) == len(set(plan["deleted_ids"])) == 1300
    for ids, message in [
        ([], "nonempty"),
        ([nodes[1].id] * 2, "distinct"),
        ([manifesto], "manifesto"),
        (["bWlzc2k="], "Unknown"),
    ]:
        with pytest.raises(SpecError, match=message):
            deletion_plan(snapshot, ids)


def test_external_change_during_confirmation_is_preserved_without_unfinished_deletion(workspace):
    root, manifesto = workspace
    before, left, right, full, shared, deep, code, other = branch(root, manifesto)
    commit(root)
    path = root / before.graph.nodes[deep].path

    def confirm(plan):
        path.write_bytes(path.read_bytes() + b"\nExternal text\n")
        return True

    with pytest.raises(SpecError, match="Files changed"):
        delete_nodes(root, [left], confirm=confirm)
    assert path.read_bytes().endswith(b"External text\n")
    assert set(load_snapshot(root).require_valid().nodes) == set(before.graph.nodes)
    assert not (root / ".specspec-local/journal.json").exists()
