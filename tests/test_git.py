from __future__ import annotations

import shlex
import subprocess
import sys
from pathlib import Path

from click.testing import CliRunner

from specspec.cli import main
from specspec.git import git_snapshot, semantic_diff
from specspec.workspace import add_node, load_snapshot, update_node


def git(root: Path, *args: str):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    assert result.returncode == 0, result.stderr.decode(errors="replace")
    return result.stdout


def setup_repository(root):
    git(root, "init")
    git(root, "config", "user.name", "specspec tests")
    git(root, "config", "user.email", "tests@example.invalid")
    git(root, "config", "core.autocrlf", "false")
    git(root, "add", ".specspec")
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
    git(root, "add", ".specspec")
    assert not git_snapshot(root, staged=True).valid
    # A repaired worktree must not mask a corrupt staged version.
    path.write_bytes(valid_bytes)
    staged = git_snapshot(root, staged=True)
    assert any(d.code == "SCHEMA" for d in staged.diagnostics)


def test_index_and_revision_reject_noncanonical_paths_despite_working_repair(workspace):
    root, manifesto = workspace
    setup_repository(root)
    snapshot = load_snapshot(root)
    node = snapshot.graph.nodes[manifesto]
    wrong = root / ".specspec" / f"{manifesto}extra.md"
    (root / node.path).rename(wrong)
    git(root, "add", "-A", ".specspec")
    wrong.rename(root / node.path)
    assert load_snapshot(root).valid
    staged = git_snapshot(root, staged=True)
    assert not staged.valid
    assert any("Filename must equal" in d.message for d in staged.diagnostics)
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Invalid path fixture")
    assert not git_snapshot(root, "HEAD").valid
    assert git_snapshot(root, "HEAD~1").valid


def test_commit_diffs_removed_edges_and_changed_bodies(workspace):
    root, manifesto = workspace
    _, left = add_node(root, "requirement", [manifesto], "Left\n")
    _, right = add_node(root, "requirement", [manifesto], "Right\n")
    _, child = add_node(root, "requirement", [left, right], "Child\n")
    setup_repository(root)
    base = git_snapshot(root, "HEAD")
    update_node(root, child, parents=[right])
    result = semantic_diff(base, load_snapshot(root))
    assert [left, child] in result["removed_edges"]
    assert child in result["affected"]
    assert result["impact_complete"]
    node = load_snapshot(root).graph.nodes[left]
    update_node(root, left, body="# Changed heading\n")
    result = semantic_diff(base, load_snapshot(root))
    assert {"id": left, "kind": "changed", "fields": ["body"]} in result["changes"]
    assert load_snapshot(root).graph.nodes[left].path == node.path
    git(root, "add", ".specspec")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Changed graph")
    assert (
        semantic_diff(git_snapshot(root, "HEAD~1"), git_snapshot(root, "HEAD"))["changes"]
        == result["changes"]
    )


def test_ancestor_changes_include_old_and_new_descendants(workspace):
    root, manifesto = workspace
    _, parent = add_node(root, "requirement", [manifesto], "Parent\n")
    _, child = add_node(root, "requirement", [parent], "Child\n")
    setup_repository(root)
    base = git_snapshot(root, "HEAD")
    update_node(root, parent, body="Updated\n")
    update_node(root, child, parents=[manifesto])
    assert child in semantic_diff(base, load_snapshot(root))["affected"]


def test_empty_baseline(workspace):
    root, _ = workspace
    git(root, "init")
    git(root, "config", "user.name", "specspec tests")
    git(root, "config", "user.email", "tests@example.invalid")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "--allow-empty", "-m", "Before spec")
    base = git_snapshot(root, "HEAD", allow_empty=True)
    assert base.valid and not base.nodes
    assert semantic_diff(base, load_snapshot(root))["changes"][0]["kind"] == "added"


def test_resolved_head_skips_unborn_probes_and_reads_fresh_commits(workspace, monkeypatch):
    from specspec import git as backend

    root, manifesto = workspace
    setup_repository(root)
    calls, original = [], backend.run_git

    def traced(root, *args):
        calls.append(args)
        return original(root, *args)

    monkeypatch.setattr(backend, "run_git", traced)
    first = git_snapshot(root, "HEAD", allow_empty=True)
    assert first.valid and first.nodes
    assert not any(args[0] in {"symbolic-ref", "show-ref"} for args in calls)
    update_node(root, manifesto, body="# Changed HEAD\n")
    git(root, "add", ".specspec")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Move HEAD")
    second = git_snapshot(root, "HEAD", allow_empty=True)
    assert second.commit != first.commit and second.nodes[0].body == "# Changed HEAD\n"


def test_unresolved_head_is_empty_only_for_a_genuinely_unborn_branch(workspace):
    import pytest

    from specspec.model import SpecError

    root, _ = workspace
    git(root, "init")
    assert git_snapshot(root, "HEAD", allow_empty=True).nodes == []
    (root / ".git/HEAD").write_text("a" * 40 + "\n", encoding="ascii")
    with pytest.raises(SpecError):
        git_snapshot(root, "HEAD", allow_empty=True)
    with pytest.raises(SpecError):
        git_snapshot(root, "missing-revision", allow_empty=True)


def test_owner_configured_hook_calls_current_exact_index_check(workspace):
    root, _ = workspace
    setup_repository(root)
    git(root, "config", "core.hooksPath", ".hooks")
    path = root / ".hooks/pre-commit"
    path.parent.mkdir()
    python = shlex.quote(sys.executable.replace("\\", "/"))
    path.write_text(f"#!/bin/sh\nexec {python} -m specspec check --staged\n", encoding="utf8")
    path.chmod(path.stat().st_mode | 0o111)
    original = path.read_bytes()
    # Hook management is ordinary owner Git tooling, not a specspec installer.
    assert CliRunner().invoke(main, ["--root", str(root), "hook", "install"]).exit_code == 2
    assert path.read_bytes() == original
    git(root, "commit", "--allow-empty", "-m", "Hook passed")
    snapshot = load_snapshot(root)
    node = snapshot.nodes[0]
    (root / node.path).write_bytes(
        snapshot.files[node.path].replace(b"parents: []", b"parents: invalid")
    )
    git(root, "add", ".specspec")
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
    git(root, "add", "subproject/.specspec")
    assert git_snapshot(nested, staged=True).valid
