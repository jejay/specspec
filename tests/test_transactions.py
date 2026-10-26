from pathlib import Path

import pytest

from specspec import workspace as module
from specspec.model import SpecError
from specspec.workspace import add_node, delete_nodes, load_snapshot, recover, serialize


def test_real_partial_batch_failure_is_recoverable(workspace, monkeypatch):
    root, manifesto = workspace
    _, parent = add_node(root, "requirement", [manifesto], "Parent\n")
    before, child = add_node(root, "requirement", [parent], "Child\n")
    original = Path.unlink
    deletions = 0

    def interrupted(target, *args, **kwargs):
        nonlocal deletions
        if target.parent == root / ".specspec":
            deletions += 1
            if deletions == 2:
                raise OSError("Simulated process interruption")
        return original(target, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", interrupted)
    with pytest.raises(OSError, match="Simulated"):
        delete_nodes(root, [parent, child], allow_uncommitted=True)
    assert not load_snapshot(root).valid
    assert (root / ".specspec-local" / "journal.json").exists()
    assert all(entry.suffix == ".md" for entry in (root / ".specspec").iterdir())
    assert len(list((root / ".specspec").iterdir())) == 2
    monkeypatch.setattr(Path, "unlink", original)
    recover(root)
    assert load_snapshot(root).files == before.files


def test_concurrent_external_edit_is_preserved(workspace):
    root, manifesto = workspace
    before = load_snapshot(root)
    node = before.graph.nodes[manifesto]
    from dataclasses import replace

    external = serialize(replace(node, body="External edit\n"))

    def operation(snapshot):
        (root / node.path).write_bytes(external)
        return {node.path: serialize(replace(node, body="Tool proposal\n"))}

    with pytest.raises(SpecError, match="Files changed"):
        module.mutate(root, operation)
    assert (root / node.path).read_bytes() == external
    assert load_snapshot(root).valid


def test_other_writers_are_blocked_by_workspace_lock(workspace):
    root, _ = workspace
    with module.workspace_lock(root):
        assert not load_snapshot(root).valid
        with pytest.raises(SpecError, match="locked"):
            with module.workspace_lock(root):
                pytest.fail("A concurrent writer acquired the lock.")
    assert load_snapshot(root).valid
