"""Verify current CLI receipts and the independent, current-schema Gantt Git bundle.

The surrounding SpecSpec repository's obsolete graph history is not a test corpus.
No checkout/index changes are made in this repository; history uses a temporary clone.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from specspec.git import git_snapshot, run_git, semantic_diff, source_change_impact
from specspec.graph import build_graph
from specspec.model import API_VERSION, FORMAT_VERSION, ID_RE, SpecNode
from specspec.sources import check_results, resolve_nodes
from specspec.workspace import load_snapshot, slugify

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATHS = (
    "app.js",
    "model.js",
    "index.html",
    "styles.css",
    "package.json",
    "test/model.test.cjs",
    "test/browser.cjs",
    "history/personal-v1.json",
)


def clone_history(root: Path, destination: Path) -> Path:
    subprocess.run(
        [sys.executable, str(root / "history/checkout.py"), str(destination)],
        check=True,
        capture_output=True,
    )
    return destination.resolve()


def contents(snapshot):
    return {node.id: node.to_dict() for node in snapshot.nodes}


def assert_current_bindings(nodes) -> None:
    """Guard against embedding correction/run diaries in the active bindings."""
    markers = (
        "Origin:",
        "## Current deletion",
        "## Later ",
        "## Superseded ",
        "## Resolved follow-up",
        "At that checkpoint",
        "Earlier run counts",
        "Original test counts",
        "withdrawal flags",
    )
    for node in nodes:
        assert node.body.strip(), node.id
        assert not any(marker in node.body for marker in markers), node.id
        if node.type == "implementation":
            assert node.sources, node.id


def verify(root: Path = ROOT, *, history: bool = False) -> dict:
    current = load_snapshot(root)
    current.require_valid()
    assert not current.diagnostics, current.diagnostics
    assert all(ID_RE.fullmatch(node.id) for node in current.nodes)
    assert_current_bindings(current.nodes)
    for node in current.nodes:
        if node.type == "implementation":
            assert node.sources and all((root / s["path"]).is_file() for s in node.sources)

    receipts = [json.loads(line) for line in (root / "history/cli.jsonl").read_text().splitlines()]
    records: dict[str, SpecNode] = {}
    recorded_graphs = {}
    for ordinal, receipt in enumerate(receipts, 1):
        assert receipt["exit_code"] == 0 and receipt["api_version"] == API_VERSION
        assert not receipt["diagnostics"], receipt
        argv = receipt["argv"]
        assert argv[:2] == ["--root", "."] and argv[-1] == "--json"
        assert "--expect" not in argv and "fingerprint" not in receipt["result"]
        action, result = argv[2], receipt["result"]
        changed = result.get("changed_ids", [])
        if action in {"init", "add"}:
            assert len(changed) == 1
            node_id = changed[0]
            assert ID_RE.fullmatch(node_id)
            assert node_id.casefold() not in {key.casefold() for key in records}
            if action == "init":
                assert not records, "An existing graph was reinitialized."
            node_type = (
                "manifesto"
                if action == "init"
                else (argv[argv.index("--type") + 1] if "--type" in argv else "requirement")
            )
            summary = argv[argv.index("--slug") + 1] if "--slug" in argv else "project-manifesto"
            records[node_id] = SpecNode(
                node_id,
                node_type,
                [argv[i + 1] for i, arg in enumerate(argv) if arg == "--parent"],
                receipt["stdin"],
                f"_specspec/{node_id}{slugify(summary)}.md",
                FORMAT_VERSION if node_type == "manifesto" else None,
                json.loads(argv[argv.index("--sources") + 1]) if "--sources" in argv else [],
            )
        elif action == "update":
            node = records[argv[3]]
            if "--body" in argv:
                node.body = receipt["stdin"]
            if "--parent" in argv:
                node.parents = [argv[i + 1] for i, arg in enumerate(argv) if arg == "--parent"]
            if "--sources" in argv:
                node.sources = json.loads(argv[argv.index("--sources") + 1])
        elif action == "delete":
            requested = [arg for arg in argv[3:-1] if arg != "--yes"]
            prior_graph, errors = build_graph(list(records.values()))
            assert not errors
            expected = set(requested)
            for node_id in requested:
                expected.update(prior_graph.closure(node_id))
            assert set(changed) == expected
            for node_id in changed:
                del records[node_id]
        graph, diagnostics = build_graph(list(records.values()))
        assert not diagnostics, diagnostics
        if action == "context":
            selected = argv[3]
            assert result["selected"] == selected
            assert set(result["required_ids"]) == graph.closure(selected, ancestors=True) | {
                selected
            }
        elif action == "show" and "--dependents" in argv:
            assert result["id"] == argv[3]
            assert set(result["affected"]) == graph.closure(argv[3])
        elif action == "check":
            assert result["node_count"] == len(records)
        assert action in {
            "init",
            "add",
            "update",
            "delete",
            "context",
            "show",
            "check",
        }
        recorded_graphs[ordinal] = {key: node.to_dict() for key, node in records.items()}
    assert recorded_graphs[len(receipts)] == contents(current), (
        "Receipts differ from the working graph."
    )

    revisions = json.loads((root / "history/revisions.json").read_text())
    assert len(revisions) == 3
    assert all(len(r["deleted_ids"]) * 2 >= r["node_count_before"] for r in revisions[1:])
    checked = []
    if history:
        with tempfile.TemporaryDirectory(prefix="specspec-gantt-history-") as directory:
            fixture = clone_history(root, Path(directory) / "project")
            assert (
                Path(run_git(fixture, "rev-parse", "--show-toplevel").decode().strip()) == fixture
            )
            assert (
                Path(
                    run_git(fixture, "rev-parse", "--path-format=absolute", "--git-common-dir")
                    .decode()
                    .strip()
                )
                == fixture / ".git"
            )
            assert run_git(fixture, "config", "core.autocrlf").strip() == b"false"
            tags = run_git(fixture, "tag", "--list").decode().splitlines()
            assert set(tags) == {"stage/00-empty", "stage/04-audit"} | {
                f"stage/{record['key']}-{kind}" for record in revisions for kind in ("spec", "code")
            }
            assert run_git(fixture, "rev-parse", "HEAD") == run_git(
                fixture, "rev-parse", "stage/04-audit"
            )
            # Check ALL retained refs, not just main: no obsolete branch/tag may hide.
            commits = (
                run_git(fixture, "rev-list", "--topo-order", "--reverse", "--all")
                .decode()
                .splitlines()
            )
            assert len(commits) == 8, commits
            for index, ref in enumerate(commits):
                snapshot = git_snapshot(fixture, ref, allow_empty=index == 0)
                assert snapshot.valid and not snapshot.diagnostics
                if index:
                    snapshot.require_valid()
                    assert snapshot.format_version == FORMAT_VERSION
                    assert_current_bindings(snapshot.nodes)
                    assert not check_results(
                        resolve_nodes(
                            fixture,
                            snapshot.nodes,
                            ref=ref,
                            retention=True,
                        )
                    )
            assert git_snapshot(fixture, staged=True).valid
            assert contents(load_snapshot(fixture)) == contents(current)
            for path in RUNTIME_PATHS:
                assert run_git(fixture, "show", f"HEAD:{path}") == (root / path).read_bytes(), (
                    f"The tracked runtime/test snapshot differs from the bundle: {path}"
                )
            previous_implementation = None
            for record in revisions:
                predecessor, spec_ref, code_ref = (
                    record["predecessor_commit"],
                    record["spec_commit"],
                    record["implementation_commit"],
                )
                run_git(fixture, "merge-base", "--is-ancestor", predecessor, spec_ref)
                run_git(fixture, "merge-base", "--is-ancestor", spec_ref, code_ref)
                run_git(fixture, "merge-base", "--is-ancestor", code_ref, "HEAD")
                message = run_git(fixture, "log", "-1", "--format=%B", spec_ref).decode()
                assert message.startswith("Agent specspec changes: "), message
                before = git_snapshot(fixture, predecessor, allow_empty=True)
                spec, implementation = (
                    git_snapshot(fixture, spec_ref),
                    git_snapshot(fixture, code_ref),
                )
                assert contents(spec) == recorded_graphs[record["spec_receipt"]]
                assert contents(implementation) == recorded_graphs[record["implementation_receipt"]]
                assert len(spec.nodes) == record["spec_node_count"]
                assert not any(n.type == "implementation" for n in spec.nodes)
                old, new = {n.id: n for n in before.nodes}, {n.id: n for n in spec.nodes}
                deleted = old.keys() - new.keys()
                assert deleted == set(record["deleted_ids"])
                assert len(before.nodes) == record["node_count_before"]
                for node_id in old.keys() & new.keys():
                    assert old[node_id].semantic() == new[node_id].semantic(), node_id
                # Earlier explanations are preserved in prior commits, not HEAD flags.
                for node_id in deleted:
                    assert run_git(fixture, "show", f"{predecessor}:{old[node_id].path}")
                    assert old[node_id].path not in spec.files
                diff = semantic_diff(before, spec)
                assert diff["impact_complete"]
                assert deleted == {c["id"] for c in diff["changes"] if c["kind"] == "removed"}
                if deleted:
                    assert diff["removed_edges"]
                    message = run_git(fixture, "log", "-1", "--format=%B", spec_ref).decode()
                    assert "Delete" in message and "because" in message
                impact = source_change_impact(fixture, spec_ref, code_ref, spec, implementation)
                assert "model.js" in {s["path"] for s in impact["source_changes"]}
                assert impact["source_affected"]
                if previous_implementation:
                    assert predecessor == previous_implementation
                else:
                    paths = (
                        run_git(fixture, "ls-tree", "-r", "--name-only", spec_ref)
                        .decode()
                        .splitlines()
                    )
                    assert "model.js" not in paths and "app.js" not in paths
                for path in ["model.js", "index.html", "test/model.test.cjs"]:
                    assert run_git(fixture, "show", f"{code_ref}:{path}")
                # Run each real stage's model tests from an isolated export, not checkout.
                stage = Path(directory) / record["key"]
                stage.mkdir()
                for path in ["model.js", "test/model.test.cjs", "history/personal-v1.json"]:
                    available = run_git(fixture, "ls-tree", "--name-only", code_ref, "--", path)
                    if available:
                        target = stage / path
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(run_git(fixture, "show", f"{code_ref}:{path}"))
                test = subprocess.run(
                    ["node", "--test", str(stage / "test/model.test.cjs")], capture_output=True
                )
                assert test.returncode == 0, test.stdout.decode() + test.stderr.decode()
                assert any(n.type == "implementation" for n in implementation.nodes)
                previous_implementation = code_ref
                checked.append(record["key"])
    return {
        "ok": True,
        "node_count": len(current.nodes),
        "deleted_in_history": sum(len(r["deleted_ids"]) for r in revisions),
        "cli_operations": len(receipts),
        "verified_git_stages": checked,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--history", action="store_true", help="Clone and verify the compliant Git bundle."
    )
    args = parser.parse_args()
    print(json.dumps(verify(history=args.history), indent=2))
