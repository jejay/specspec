from pathlib import Path

import pytest

from specspec import workspace as module
from specspec.model import SpecError
from specspec.workspace import add_node, change_status, load_snapshot, recover, serialize


def test_real_partial_batch_failure_is_recoverable(workspace, monkeypatch):
    root, manifesto = workspace
    _, parent = add_node(root, "requirement", [manifesto], "Parent\n", "parent")
    before, child = add_node(root, "requirement", [parent], "Child\n", "child")
    original = module.os.replace
    replacements = 0

    def interrupted(source, target):
        nonlocal replacements
        if Path(target).parent == root / "_specspec":
            replacements += 1
            if replacements == 2:
                raise OSError("Simulated process interruption")
        return original(source, target)

    monkeypatch.setattr(module.os, "replace", interrupted)
    with pytest.raises(OSError, match="Simulated"):
        change_status(root, [parent, child], "accepted")
    assert not load_snapshot(root).valid
    assert (root / ".specspec-local" / "journal.json").exists()
    assert all(entry.suffix == ".md" for entry in (root / "_specspec").iterdir())
    monkeypatch.setattr(module.os, "replace", original)
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
