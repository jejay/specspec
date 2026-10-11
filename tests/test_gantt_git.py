"""Git regressions use the maintained Gantt history, never old root schemas."""

import importlib.util
from pathlib import Path

import pytest
from test_git import git

from specspec.git import git_snapshot, semantic_diff, source_change_impact
from specspec.workspace import add_node, load_snapshot, update_node

GANTT = Path(__file__).resolve().parents[1] / "example/gantt"


@pytest.fixture
def gantt_history(tmp_path):
    spec = importlib.util.spec_from_file_location("gantt_fixture", GANTT / "history/verify.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    root = module.clone_history(GANTT, tmp_path / "gantt")
    git(root, "config", "core.autocrlf", "false")
    git(root, "config", "user.name", "SpecSpec tests")
    git(root, "config", "user.email", "tests@example.invalid")
    return root


def test_gantt_index_reads_staged_corruption_not_repaired_worktree(gantt_history):
    root = gantt_history
    before = load_snapshot(root)
    node = next(n for n in before.nodes if n.type == "requirement" and not n.retired)
    file = root / node.path
    file.write_bytes(before.files[node.path].replace(b"parents:", b"unknown:"))
    assert not load_snapshot(root).valid and git_snapshot(root, staged=True).valid
    git(root, "add", "_specspec")
    file.write_bytes(before.files[node.path])
    assert load_snapshot(root).valid and not git_snapshot(root, staged=True).valid
    assert git_snapshot(root, "stage/03-code").valid


def test_gantt_full_identity_rename_parent_edges_and_impact(gantt_history):
    root = gantt_history
    original = load_snapshot(root)
    manifesto = next(n.id for n in original.nodes if n.type == "manifesto")
    parent = next(n.id for n in original.nodes if n.type == "requirement" and not n.retired)
    _, child = add_node(
        root, "requirement", [parent], "# Current-scheme regression\n", "regression"
    )
    git(root, "add", "_specspec")
    git(root, "commit", "-m", "Add current-schema regression branch")
    base = git_snapshot(root, "HEAD")
    changed = update_node(root, child, parents=[manifesto])
    node = changed.graph.nodes[child]
    renamed = root / f"_specspec/{child}renamed-regression.md"
    (root / node.path).rename(renamed)
    diff = semantic_diff(base, load_snapshot(root))
    assert diff["impact_complete"]
    assert [parent, child] in diff["removed_edges"]
    assert [manifesto, child] in diff["added_edges"]
    assert child in diff["affected"]
    assert next(c for c in diff["changes"] if c["id"] == child)["fields"] == ["parents", "path"]
    git(root, "add", "_specspec")
    assert git_snapshot(root, staged=True).valid
    git(root, "commit", "-m", "Reparent and rename without changing full identity")
    committed = git_snapshot(root, "HEAD")
    assert semantic_diff(base, committed)["changes"] == diff["changes"]
    (root / committed.graph.nodes[child].path).rename(root / f"_specspec/{child}summary-only.md")
    rename = semantic_diff(committed, load_snapshot(root))
    assert rename["changes"] == [{"id": child, "kind": "renamed", "fields": ["path"]}]
    assert not rename["affected"]


def test_gantt_worktree_linked_source_changes_reach_requirement_ancestors(gantt_history):
    root = gantt_history
    before = git_snapshot(root, "HEAD")
    path = root / "model.js"
    path.write_bytes(path.read_bytes() + b"\n// Disposable source-impact regression\n")
    current = load_snapshot(root)
    impact = source_change_impact(root, "HEAD", None, before, current)
    assert [s["path"] for s in impact["source_changes"]] == ["model.js"]
    implementations = {
        n.id for n in current.nodes if any(s["path"] == "model.js" for s in n.sources)
    }
    assert implementations <= set(impact["source_affected"])
    for node_id in implementations:
        assert current.graph.closure(node_id, ancestors=True) <= set(impact["source_affected"])
    assert semantic_diff(before, current)["changes"] == []
