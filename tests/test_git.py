from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from specspec.git import git_snapshot, install_hook, semantic_diff
from specspec.model import SpecError
from specspec.workspace import add_node, load_snapshot, update_node


def git(root: Path, *args: str):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    assert result.returncode == 0, result.stderr.decode(errors="replace")
    return result.stdout


def setup_repository(root):
    git(root, "init")
    git(root, "config", "user.name", "SpecSpec tests")
    git(root, "config", "user.email", "tests@example.invalid")
    git(root, "config", "core.autocrlf", "false")
    git(root, "add", "_specspec")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Initial graph")


def test_index_validation_checks_partial_staging(workspace):
    root, manifesto = workspace
    setup_repository(root)
    node = load_snapshot(root).graph.nodes[manifesto]
    path = root / node.path
    valid_bytes = path.read_bytes()
    path.write_bytes(valid_bytes.replace(b"parents: []", b"parents: invalid"))
    # Unstaged corruption must not break validation of the already valid index.
    assert git_snapshot(root, staged=True).valid
    git(root, "add", "_specspec")
    assert not git_snapshot(root, staged=True).valid
    # A repaired worktree must not mask a corrupt staged version.
    path.write_bytes(valid_bytes)
    staged = git_snapshot(root, staged=True)
    assert any(d.code == "SCHEMA" for d in staged.diagnostics)


def test_commit_diffs_removed_edges_and_renames(workspace):
    root, manifesto = workspace
    _, left = add_node(root, "requirement", [manifesto], "Left\n", "left")
    _, right = add_node(root, "requirement", [manifesto], "Right\n", "right")
    _, child = add_node(root, "requirement", [left, right], "Child\n", "child")
    setup_repository(root)
    base = git_snapshot(root, "HEAD")
    update_node(root, child, parents=[right])
    result = semantic_diff(base, load_snapshot(root))
    assert [left, child] in result["removed_edges"]
    assert child in result["affected"]
    assert result["impact_complete"]
    node = load_snapshot(root).graph.nodes[left]
    (root / node.path).rename(root / "_specspec" / f"{left}--renamed.md")
    result = semantic_diff(base, load_snapshot(root))
    assert {"id": left, "kind": "renamed", "fields": ["path"]} in result["changes"]
    git(root, "add", "_specspec")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Changed graph")
    assert (
        semantic_diff(git_snapshot(root, "HEAD~1"), git_snapshot(root, "HEAD"))["changes"]
        == result["changes"]
    )


def test_ancestor_changes_include_old_and_new_descendants(workspace):
    root, manifesto = workspace
    _, parent = add_node(root, "requirement", [manifesto], "Parent\n", "parent")
    _, child = add_node(root, "requirement", [parent], "Child\n", "child")
    setup_repository(root)
    base = git_snapshot(root, "HEAD")
    update_node(root, parent, body="Updated\n")
    update_node(root, child, parents=[manifesto])
    assert child in semantic_diff(base, load_snapshot(root))["affected"]


def test_empty_baseline(workspace):
    root, _ = workspace
    git(root, "init")
    git(root, "config", "user.name", "SpecSpec tests")
    git(root, "config", "user.email", "tests@example.invalid")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "--allow-empty", "-m", "Before spec")
    base = git_snapshot(root, "HEAD", allow_empty=True)
    assert base.valid and not base.nodes
    assert semantic_diff(base, load_snapshot(root))["changes"][0]["kind"] == "added"


def test_hook_installer_preserves_hooks_and_respects_config(workspace):
    root, _ = workspace
    setup_repository(root)
    git(root, "config", "core.hooksPath", ".hooks")
    path = install_hook(root)
    assert path == root / ".hooks" / "pre-commit"
    original = path.read_bytes()
    with pytest.raises(SpecError, match="Existing hook preserved"):
        install_hook(root)
    assert path.read_bytes() == original
    assert "hook check" in path.read_text()
    # Run the actual installed script through Git, not only the helper function.
    git(root, "commit", "--allow-empty", "-m", "Hook passed")
    snapshot = load_snapshot(root)
    node = snapshot.nodes[0]
    (root / node.path).write_bytes(
        snapshot.files[node.path].replace(b"parents: []", b"parents: invalid")
    )
    git(root, "add", "_specspec")
    result = subprocess.run(
        ["git", "-C", str(root), "commit", "-m", "Should fail"], capture_output=True
    )
    assert result.returncode != 0
    assert b"SCHEMA" in result.stderr + result.stdout


def test_nested_project_paths(workspace):
    root, _ = workspace
    setup_repository(root)
    from specspec.workspace import initialize

    nested = root / "subproject"
    nested.mkdir()
    initialize(nested, "Nested\n")
    git(root, "add", "subproject/_specspec")
    assert git_snapshot(nested, staged=True).valid
