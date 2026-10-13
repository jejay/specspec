"""Git regressions use the maintained Gantt history, never old root schemas."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner
from test_git import git

from specspec.cli import main
from specspec.git import git_snapshot, semantic_diff, source_change_impact
from specspec.workspace import add_node, load_snapshot, update_node

ROOT = Path(__file__).resolve().parents[1]


def test_gantt_index_reads_staged_corruption_not_repaired_worktree(gantt_history):
    root = gantt_history
    before = load_snapshot(root)
    node = next(n for n in before.nodes if n.type == "requirement")
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
    parent = next(n.id for n in original.nodes if n.type == "requirement")
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


@pytest.mark.parametrize(
    ("base", "target", "deleted"),
    [
        ("stage/01-code", "stage/02-spec", 13),
        ("stage/02-code", "stage/03-spec", 9),
    ],
)
def test_historical_redirects_load_through_the_ui_diff_protocol(
    gantt_history, base, target, deleted
):
    root = gantt_history
    original_index = git(root, "ls-files", "--stage")
    original_worktree = load_snapshot(root).files
    result = CliRunner().invoke(
        main, ["--root", str(root), "diff", "--base", base, "--target", target, "--json"]
    )
    assert result.exit_code == 0, result.output
    envelope = json.loads(result.output)
    assert envelope["ok"] and not envelope["diagnostics"]
    diff = envelope["result"]
    assert diff["base"]["valid"] and diff["target"]["valid"] and diff["impact_complete"]
    assert sum(change["kind"] == "removed" for change in diff["changes"]) == deleted
    assert diff["removed_edges"]
    assert all("retired" not in n for side in ["base", "target"] for n in diff[side]["nodes"])
    assert diff["added_edges"] and diff["affected"]
    assert git(root, "ls-files", "--stage") == original_index
    assert load_snapshot(root).files == original_worktree


def test_host_fixture_preserves_real_history_and_adds_only_disposable_git_cues():
    script = r"""
const { execFileSync } = require('node:child_process');
const { fixture } = require('./graph-ui-common/test-host/fixture.cjs');
const project = fixture(process.argv[1], process.argv[2]);
try {
  const git = (...args) => execFileSync('git', ['-C', project.root, ...args],
    {encoding:'utf8'}).trim();
  console.log(JSON.stringify({
    root: project.root, top: git('rev-parse','--show-toplevel'),
    commits: git('rev-list','--count','--all'),
    modified: project.modified, added: project.added, removed: project.removed,
    diff: project.cli(['diff','--base','HEAD','--json']),
    history: project.cli(['diff','--base','stage/02-code','--target','stage/03-spec','--json']),
  }));
} finally { project.cleanup(); }
"""
    completed = subprocess.run(
        ["node", "-e", script, str(ROOT / "example/gantt"), sys.executable],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    assert Path(result["top"]).resolve() == Path(result["root"]).resolve()
    assert ROOT not in Path(result["root"]).resolve().parents
    assert result["commits"] == "8"
    assert result["history"]["impact_complete"]
    assert {c["id"]: c["kind"] for c in result["diff"]["changes"]} == {
        result["modified"]: "changed",
        result["added"]: "added",
        result["removed"]: "removed",
    }
    assert not Path(result["root"]).exists()
