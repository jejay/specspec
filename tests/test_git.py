from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from specspec.cli import main
from specspec.git import git_snapshot, semantic_diff
from specspec.git_process import CONFIG, pathspec_chunks
from specspec.workspace import add_node, initialize, load_snapshot, update_node


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


def test_pathspec_chunks_bound_command_lines_without_changing_membership():
    paths = [f"dir/{'x' * (i % 40)}-{i}.py" for i in range(500)]
    chunks = list(pathspec_chunks(paths, budget=1000))
    assert len(chunks) > 1 and [p for chunk in chunks for p in chunk] == paths
    assert all(sum(len(p) + 3 for p in chunk) <= 1000 for chunk in chunks)
    assert list(pathspec_chunks(["x" * 5000], budget=1000)) == [["x" * 5000]]
    assert list(pathspec_chunks([])) == []


def test_source_impact_chunks_thousands_of_referenced_paths(workspace):
    from specspec.application import compare
    from specspec.editor import editor_request

    root, manifesto = workspace
    _, requirement = add_node(root, "requirement", [manifesto], "Behavior\n")
    paths = [f"src/generated/module_{i:04d}_with_a_descriptive_name.py" for i in range(1400)]
    for start in range(0, len(paths), 256):
        references = [{"path": path} for path in paths[start : start + 256]]
        add_node(root, "implementation", [requirement], f"Code {start}\n", references)
    (root / "src/generated").mkdir(parents=True)
    for path in (paths[0], paths[-1]):
        (root / path).write_text("original\n", encoding="utf8")
    setup_repository(root)
    git(root, "add", "src")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Referenced code")
    (root / paths[0]).write_text("changed\n", encoding="utf8")
    (root / paths[700]).write_text("untracked realization\n", encoding="utf8")
    # One literal pathspec list would exceed Windows' 32,767-character command line.
    assert sum(len(path) + 1 for path in paths) > 32_767
    expected = sorted([paths[0], paths[700]])
    result, _ = compare(root)
    assert [change["path"] for change in result["source_changes"]] == expected
    response = CliRunner().invoke(main, ["--root", str(root), "diff", "--summary", "--json"])
    assert response.exit_code == 0, response.output
    changes = json.loads(response.stdout)["result"]["source_changes"]
    assert [change["path"] for change in changes] == expected
    read = editor_request(root, {}, "HEAD")
    assert read["note"] == "" and read["diff"]["source_changes"] == result["source_changes"]


def test_intent_to_add_placeholders_are_not_staged_nodes(workspace):
    root, manifesto = workspace
    setup_repository(root)
    _, planned = add_node(root, "requirement", [manifesto], "# Planned\n")
    path = f".specspec/{planned}.md"
    git(root, "add", "-N", path)
    staged = git_snapshot(root, staged=True)
    assert staged.valid and path not in staged.files and planned not in staged.graph.nodes
    result = CliRunner().invoke(main, ["--root", str(root), "check", "--staged", "--json"])
    assert result.exit_code == 0, result.output
    # A real empty blob in the index would be committed, so it stays diagnosed.
    (root / path).write_bytes(b"")
    git(root, "add", path)
    staged = git_snapshot(root, staged=True)
    assert [(d.code, d.path) for d in staged.diagnostics] == [("FORMAT", path)]


def test_repository_fsmonitor_hook_never_runs_during_specspec_reads(tmp_path):
    from specspec.annotations import submit
    from specspec.editor import editor_request

    root = tmp_path / "project"
    root.mkdir()
    manifesto = initialize(root, "# Project\n").nodes[0].id
    _, requirement = add_node(root, "requirement", [manifesto], "Behavior\n")
    add_node(root, "implementation", [requirement], "Code\n", [{"path": "code.py"}])
    (root / "code.py").write_text("one\n", encoding="utf8")
    setup_repository(root)
    git(root, "add", "code.py")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Code")
    marker = tmp_path / "fsmonitor-ran"
    hook = tmp_path / "fsmonitor-hook"
    hook.write_bytes(f"#!/bin/sh\necho ran >> '{marker.as_posix()}'\nexit 1\n".encode())
    hook.chmod(0o755)
    git(root, "config", "core.fsmonitor", hook.as_posix())
    (root / "code.py").write_text("two\n", encoding="utf8")
    for args in [
        ["diff", "--json"],
        ["query", "--json"],
        ["check", "--staged", "--sources", "--json"],
        ["delete", requirement, "--dry-run", "--json"],
    ]:
        CliRunner().invoke(main, ["--root", str(root), *args])
    editor_request(root, {"cache": True}, "HEAD")
    submit(root, {"message": "Review", "nodes": [manifesto]})
    assert not marker.exists()
    # The hook stays configured: ordinary worktree Git commands still execute it.
    subprocess.run(["git", "-C", str(root), "diff", "--name-only", "HEAD"], capture_output=True)
    if not marker.exists():
        pytest.skip("This Git build does not execute fsmonitor hooks.")


def test_every_git_subprocess_uses_the_hardened_invocation(tmp_path, monkeypatch):
    from specspec.annotations import submit
    from specspec.editor import editor_request
    from specspec.sources import SourceReader

    processes, deadlines, active = [], [], [False]
    popen, run = subprocess.Popen, subprocess.run

    def traced_popen(command, *args, **kwargs):
        if active[0] and command[0] == "git":
            processes.append((list(command), kwargs.get("env") or {}))
        return popen(command, *args, **kwargs)

    def traced_run(command, *args, **kwargs):
        if active[0] and command[0] == "git":
            deadlines.append(kwargs.get("timeout"))
        return run(command, *args, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", traced_popen)
    monkeypatch.setattr(subprocess, "run", traced_run)
    root = tmp_path / "project"
    root.mkdir()
    active[0] = True
    manifesto = initialize(root, "# Project\n").nodes[0].id
    editor_request(root, {}, "HEAD")  # Unborn HEAD probes.
    active[0] = False
    _, requirement = add_node(root, "requirement", [manifesto], "Behavior\n")
    _, implementation = add_node(root, "implementation", [requirement], "Code\n")
    (root / "code.py").write_text("one\ntwo\nthree\n", encoding="utf8")
    setup_repository(root)
    git(root, "add", "code.py")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Code")
    active[0] = True
    source = SourceReader(root, ref="HEAD").capture("code.py", [[2, 2]], "strict")
    active[0] = False
    update_node(root, implementation, sources=[source, {"path": "code.py"}])
    (root / "code.py").write_text("zero\none\ntwo\nthree\n", encoding="utf8")
    active[0] = True
    for args in [
        ["diff", "--json"],
        ["query", "--json"],
        ["check", "--sources", "--json"],
        ["check", "--staged", "--sources", "--json"],
        ["sources", "show", "--ref", "HEAD", "--json"],
        ["delete", requirement, "--dry-run", "--json"],
    ]:
        CliRunner().invoke(main, ["--root", str(root), *args])
    editor_request(root, {"cache": True}, "HEAD")
    submit(root, {"message": "Review", "nodes": [manifesto]})
    active[0] = False
    commands = {arg for command, _ in processes for arg in command[3 + len(CONFIG) :][:2]}
    assert {
        "init",
        "rev-parse",
        "symbolic-ref",
        "show-ref",
        "ls-files",
        "ls-tree",
        "diff",
        "status",
        "cat-file",
        "check-ignore",
    } <= commands
    for command, env in processes:
        assert command[3 : 3 + len(CONFIG)] == list(CONFIG), command
        assert env.get("GIT_OPTIONAL_LOCKS") == "0" and env.get("GIT_NO_LAZY_FETCH") == "1"
        assert env.get("GIT_ALLOW_PROTOCOL") == "" and env.get("GIT_TERMINAL_PROMPT") == "0"
    assert deadlines and all(deadlines)
