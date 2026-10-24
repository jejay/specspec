"""Exact deletion, retained dependencies and pre-write warnings/consent."""

import json
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest
from click.testing import CliRunner
from test_git import git, setup_repository

from specspec import cli as cli_module
from specspec.cli import main
from specspec.deletion import deletion_plan, deletion_warnings
from specspec.model import Diagnostic, SpecError
from specspec.workspace import (
    add_node,
    delete_nodes,
    load_snapshot,
    new_node,
    serialize,
    snapshot_from_files,
    update_node,
)


def branch(root, manifesto):
    _, a = add_node(root, "requirement", [manifesto], "# A\n")
    _, b = add_node(root, "requirement", [manifesto], "# B\n")
    _, c = add_node(root, "requirement", [a, b], "# Shared C\n")
    snapshot, d = add_node(root, "requirement", [c], "# Deep D\n")
    setup_repository(root)
    return snapshot, a, b, c, d


def invoke(root, *args, **kwargs):
    result = CliRunner().invoke(main, ["--root", str(root), "delete", *args, "--json"], **kwargs)
    return result, json.loads(result.stdout)


def test_selected_ancestors_and_descendants_are_exact_not_implicitly_expanded(
    workspace, monkeypatch
):
    root, manifesto = workspace
    before, a, b, c, d = branch(root, manifesto)
    removed, original = [], Path.unlink

    def unlink(path, *args, **kwargs):
        if path.parent == root / "_specspec":
            removed.append(path.name)
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", unlink)
    after = delete_nodes(root, [a, c])
    assert set(removed) == {f"{a}.md", f"{c}.md"} and len(removed) == 2
    assert set(after.graph.nodes) == {manifesto, b, d} and not after.valid
    assert after.files == {p: raw for p, raw in before.files.items() if p in after.files}
    assert after.graph.nodes[d].parents == [c]


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
def test_selected_file_warnings_preserve_git_and_line_ending_semantics(workspace, kind, status):
    root, manifesto = workspace
    before, a, b, c, target = branch(root, manifesto)
    if kind in {"untracked", "staged-added", "ignored"}:
        _, target = add_node(root, "requirement", [c], "# Fresh\n")
        if kind == "ignored":
            (root / ".gitignore").write_text("_specspec/\n", encoding="utf8")
    path = load_snapshot(root).graph.nodes[target].path
    if kind in {"unstaged", "staged-modified"}:
        update_node(root, target, body="# Pending\n")
    elif kind == "comment-only":
        file = root / path
        file.write_bytes(
            file.read_bytes().replace(b"type: requirement", b"type: requirement # pending")
        )
    elif kind == "renamed":
        node = before.graph.nodes[target]
        replacement = new_node(node.type, node.parents, node.body)
        (root / replacement.path).write_bytes(serialize(replacement))
        (root / path).unlink()
        target, path = replacement.id, replacement.path
    if kind in {"staged-added", "staged-modified", "renamed"}:
        git(root, "add", "-A", "_specspec")
    elif kind == "staged-mode":
        git(root, "config", "core.filemode", "false")
        git(root, "update-index", "--chmod=+x", path)
    before = load_snapshot(root).files
    result, preview = invoke(root, target, "--dry-run")
    assert result.exit_code == 0
    assert preview["result"]["deleted_ids"] == [target]
    assert preview["result"]["uncommitted"] == [{"id": target, "path": path, "status": status}]
    refused, response = invoke(root, target)
    assert refused.exit_code == 1 and response["result"] == preview["result"]
    assert load_snapshot(root).files == before
    assert not (root / ".specspec-local/journal.json").exists()
    allowed, response = invoke(root, target, "--yes")
    assert allowed.exit_code == 0 and target not in load_snapshot(root).graph.nodes
    assert target in {d["node_id"] for d in response["diagnostics"] if d["severity"] == "warning"}
    assert "uncommitted" in allowed.stderr


def test_dirty_surviving_descendants_are_evidence_not_destructive_action_warnings(workspace):
    root, manifesto = workspace
    before, a, b, c, d = branch(root, manifesto)
    update_node(root, d, body="# Pending survivor\n")
    plan = deletion_plan(load_snapshot(root), [a])
    assert not plan["uncommitted"] and not deletion_warnings(plan)
    result, response = invoke(root, a)
    assert result.exit_code == 0 and response["ok"]
    assert load_snapshot(root).graph.nodes[d].body == "# Pending survivor\n"


def test_no_git_or_unborn_head_never_claims_selected_nodes_are_committed(workspace):
    root, manifesto = workspace
    _, child = add_node(root, "requirement", [manifesto], "# New\n")
    result, preview = invoke(root, child, "--dry-run")
    assert result.exit_code == 0 and not preview["result"]["git_available"]
    with pytest.raises(SpecError, match="Confirm"):
        delete_nodes(root, [child])
    git(root, "init")
    result, preview = invoke(root, child, "--dry-run")
    assert preview["result"]["git_available"]
    assert preview["result"]["uncommitted"][0]["status"] == "??"


@pytest.mark.parametrize("answer,deleted", [("n", False), ("y", True)])
def test_whole_action_human_consent_keeps_descendants(workspace, monkeypatch, answer, deleted):
    root, manifesto = workspace
    before, a, b, c, d = branch(root, manifesto)
    update_node(root, a, body="# Pending selected node\n")
    before = load_snapshot(root).files
    monkeypatch.setattr(cli_module, "interactive_stdin", lambda: True)
    result = CliRunner().invoke(main, ["--root", str(root), "delete", a], input=answer + "\n")
    assert "uncommitted" in result.stderr and "exactly 1 selected nodes" in result.stdout
    if deleted:
        assert result.exit_code == 0 and set(load_snapshot(root).graph.nodes) == {
            manifesto,
            b,
            c,
            d,
        }
    else:
        assert result.exit_code == 1 and load_snapshot(root).files == before
    assert not (root / ".specspec-local/journal.json").exists()


@pytest.mark.parametrize("change", ["descendant", "selected-warning", "selected-rename"])
def test_reviewed_consequences_are_rechecked_under_lock(workspace, change):
    root, manifesto = workspace
    before, a, b, c, d = branch(root, manifesto)
    plan = deletion_plan(before, [a])
    if change == "descendant":
        add_node(root, "requirement", [c], "# More downstream\n")
    elif change == "selected-warning":
        update_node(root, a, body="# Pending\n")
    else:
        node = before.graph.nodes[a]
        replacement = replace(node, id=new_node(node.type, node.parents, node.body).id)
        replacement.path = f"_specspec/{replacement.id}.md"
        (root / replacement.path).write_bytes(serialize(replacement))
        (root / node.path).unlink()
    current = load_snapshot(root).files
    result, response = invoke(root, a, "--yes", "--reviewed-plan", "-", input=json.dumps(plan))
    assert result.exit_code == 1 and load_snapshot(root).files == current
    assert response["diagnostics"][0]["code"] in {"DELETE_PLAN_CHANGED", "NODE"}
    assert not (root / ".specspec-local/journal.json").exists()


def test_unmerged_and_unavailable_git_assessment_warn_for_selected_files(workspace, monkeypatch):
    root, manifesto = workspace
    before, a, b, c, d = branch(root, manifesto)
    path = before.graph.nodes[a].path
    blob = git(root, "rev-parse", f"HEAD:{path}").decode().strip()
    data = f"0 {blob}\t{path}\n" + "".join(
        f"100644 {blob} {stage}\t{path}\n" for stage in [1, 2, 3]
    )
    subprocess.run(
        ["git", "-C", str(root), "update-index", "--index-info"], input=data.encode(), check=True
    )
    plan = deletion_plan(before, [a])
    assert plan["uncommitted"] == [{"id": a, "path": path, "status": "UU"}]
    from specspec import deletion as module

    original = module.run_git

    def unavailable(root, *args):
        if "status" in args:
            raise SpecError([Diagnostic("GIT", "Status failed")], 2)
        return original(root, *args)

    monkeypatch.setattr(module, "run_git", unavailable)
    plan = deletion_plan(before, [a])
    assert not plan["git_available"] and len(plan["uncommitted"]) == 1
    assert all(d["id"] == a for d in plan["uncommitted"])


def test_linked_worktree_and_literal_nested_paths_use_their_own_index(workspace, tmp_path):
    root, manifesto = workspace
    before, a, b, c, d = branch(root, manifesto)
    linked = tmp_path / "linked [literal]"
    git(root, "worktree", "add", "--detach", str(linked), "HEAD")
    try:
        current = update_node(linked, a, body="# Linked selected change\n")
        index = git(linked, "ls-files", "--stage")
        assert {n["id"] for n in deletion_plan(current, [a])["uncommitted"]} == {a}
        assert not deletion_plan(load_snapshot(root), [a])["uncommitted"]
        assert git(linked, "ls-files", "--stage") == index
    finally:
        git(root, "worktree", "remove", "--force", str(linked))


def test_warning_delivery_precedes_unlink_and_external_changes_are_preserved(
    workspace, monkeypatch
):
    root, manifesto = workspace
    before, child = add_node(root, "requirement", [manifesto], "# New\n")
    messages, original_emit, original_unlink = [], cli_module.emit, Path.unlink

    def emit(result, diagnostics=None, **kwargs):
        messages.extend(diagnostics or [])
        return original_emit(result, diagnostics, **kwargs)

    def unlink(path, *args, **kwargs):
        if path.parent == root / "_specspec":
            assert any(d.severity == "warning" and d.node_id == child for d in messages)
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(cli_module, "emit", emit)
    monkeypatch.setattr(Path, "unlink", unlink)
    assert invoke(root, child, "--yes")[0].exit_code == 0
    _, child = add_node(root, "requirement", [manifesto], "# Another\n")
    path = root / f"_specspec/{child}.md"

    def confirm(plan):
        path.write_bytes(path.read_bytes() + b"\nExternal text\n")
        return True

    with pytest.raises(SpecError, match="Files changed"):
        delete_nodes(root, [child], confirm=confirm)
    assert path.read_bytes().endswith(b"External text\n")
    assert not (root / ".specspec-local/journal.json").exists()


def test_long_chain_exact_scope_and_invalid_requests_are_non_writing(workspace):
    root, manifesto = workspace
    nodes = [load_snapshot(root).nodes[0]]
    for _ in range(1300):
        nodes.append(new_node("requirement", [nodes[-1].id], "# Deep\n"))
    snapshot = snapshot_from_files(root, {n.path: serialize(n) for n in nodes})
    plan = deletion_plan(snapshot, [nodes[1].id, nodes[500].id])
    assert set(plan["deleted_ids"]) == {nodes[1].id, nodes[500].id}
    assert len(plan["potentially_affected"]) == 1298
    for ids, message in [
        ([], "nonempty"),
        ([nodes[1].id] * 2, "distinct"),
        ([manifesto], "manifesto"),
        (["bWlzc2k="], "Unknown"),
    ]:
        with pytest.raises(SpecError, match=message):
            deletion_plan(snapshot, ids)
