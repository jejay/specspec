"""Check the actual managed graph, CLI receipts, and (optionally) real Git stages.

Run with Python that has SpecSpec installed. Never edits nodes or the Git index.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from specspec.git import git_snapshot, repository_paths, run_git
from specspec.workspace import load_snapshot

ROOT = Path(__file__).resolve().parents[1]


def verify(root: Path = ROOT, *, history: bool = False) -> dict:
    current = load_snapshot(root)
    current.require_valid()
    assert not current.diagnostics, current.diagnostics
    assert sum(node.type == "manifesto" for node in current.nodes) == 1
    assert all("status" not in node.to_dict() for node in current.nodes)
    for node in current.nodes:
        if not node.retired and node.type == "implementation":
            assert node.sources, node.id
            assert all((root / source["path"]).is_file() for source in node.sources)

    receipts = [json.loads(line) for line in (root / "history/cli.jsonl").read_text().splitlines()]
    fingerprint = None
    for receipt in receipts:
        assert receipt["exit_code"] == 0 and receipt["api_version"] == 2
        assert not receipt["diagnostics"], receipt
        argv = receipt["argv"]
        assert argv[:2] == ["--root", "example/gantt"] and argv[-1] == "--json"
        if "--expect" in argv:
            assert argv[argv.index("--expect") + 1] == fingerprint, receipt
        if argv[2] in {"add", "update", "retire", "restore"}:
            assert "--expect" in argv, receipt
        if argv[2] == "init":
            assert fingerprint is None, "The existing graph was reinitialized."
        fingerprint = receipt["result"].get("fingerprint", fingerprint)
    assert fingerprint == current.fingerprint, "CLI receipts do not describe the current graph."

    revisions = json.loads((root / "history/revisions.json").read_text())
    assert len(revisions) == 3
    assert all(len(r["withdrawn_ids"]) * 2 >= r["live_before"] for r in revisions[1:])
    checked = []
    if history:
        _, spec_prefix = repository_paths(root)
        project_prefix = spec_prefix.removesuffix("_specspec")
        previous_implementation = None
        for record in revisions:
            spec_ref = record["spec_commit"]
            implementation_ref = record.get("implementation_commit")
            assert implementation_ref, (
                "Finish/stamp the implementation commit before history audit."
            )
            run_git(root, "merge-base", "--is-ancestor", record["predecessor_commit"], spec_ref)
            run_git(root, "merge-base", "--is-ancestor", spec_ref, implementation_ref)
            run_git(root, "merge-base", "--is-ancestor", implementation_ref, "HEAD")
            spec = git_snapshot(root, spec_ref)
            implementation = git_snapshot(root, implementation_ref)
            before = git_snapshot(root, record["predecessor_commit"], allow_empty=True)
            for snapshot in (spec, implementation):
                snapshot.require_valid()
                assert not snapshot.diagnostics
            assert before.valid and not before.diagnostics
            if before.nodes:
                before.require_valid()
            else:
                assert previous_implementation is None, (
                    "Only the first stage may start without a graph."
                )
            assert spec.fingerprint == record["spec_fingerprint"]
            assert implementation.fingerprint == record["implementation_fingerprint"]
            assert sum(not node.retired for node in spec.nodes) == record["spec_live_count"]
            assert not any(
                not node.retired and node.type == "implementation" for node in spec.nodes
            )
            old = {n.id: n for n in before.nodes}
            new = {n.id: n for n in spec.nodes}
            assert old.keys() <= new.keys(), "History was deleted instead of withdrawn."
            assert old.keys() <= {n.id for n in current.nodes}
            withdrawn = {n.id for n in spec.nodes if n.retired and not old[n.id].retired}
            assert withdrawn == set(record["withdrawn_ids"])
            assert sum(not n.retired for n in before.nodes) == record["live_before"]
            for node_id in withdrawn:
                # Withdrawal changes only the flag, not the old explanation or links.
                left, right = old[node_id].semantic(), new[node_id].semantic()
                left["retired"] = True
                assert left == right, node_id
            if previous_implementation:
                assert record["predecessor_commit"] == previous_implementation
            else:
                paths = run_git(
                    root, "ls-tree", "-r", "--name-only", spec_ref, "--", project_prefix
                )
                assert f"{project_prefix}model.js".encode() not in paths
                assert f"{project_prefix}app.js".encode() not in paths
            # Every implementation is actual runnable code, not only a prose plan.
            assert run_git(root, "show", f"{implementation_ref}:{project_prefix}model.js")
            assert run_git(root, "show", f"{implementation_ref}:{project_prefix}index.html")
            assert run_git(
                root, "show", f"{implementation_ref}:{project_prefix}test/model.test.cjs"
            )
            assert any(not n.retired and n.type == "implementation" for n in implementation.nodes)
            previous_implementation = implementation_ref
            checked.append(record["key"])
    return {
        "ok": True,
        "node_count": len(current.nodes),
        "live_count": sum(not n.retired for n in current.nodes),
        "withdrawn_count": sum(n.retired for n in current.nodes),
        "cli_operations": len(receipts),
        "verified_git_stages": checked,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--history", action="store_true", help="Require the full original Git history."
    )
    args = parser.parse_args()
    print(json.dumps(verify(history=args.history), indent=2))
