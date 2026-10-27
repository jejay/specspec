import pytest

from specspec.model import SpecError
from specspec.workspace import (
    encode,
    load_snapshot,
    recover,
    update_node,
    write_journal,
)


def test_interrupted_edit_can_restore_original(workspace):
    root, manifesto = workspace
    before = load_snapshot(root)
    updated = update_node(root, manifesto, body="New content\n")
    path = before.nodes[0].path
    write_journal(
        root / ".specspec/local",
        {
            "kind": "edit",
            "files": {
                path: {"old": encode(before.files[path]), "new": encode(updated.files[path])},
            },
        },
    )
    assert not load_snapshot(root).valid
    with pytest.raises(SpecError, match="recover"):
        update_node(root, manifesto, body="Another\n")
    assert recover(root)["restored"] == [path]
    assert load_snapshot(root).files == before.files
    assert all(p.suffix == ".md" for p in (root / ".specspec").iterdir() if p.name != "local")


def test_recovery_refuses_external_changes(workspace):
    root, _ = workspace
    snapshot = load_snapshot(root)
    node = snapshot.nodes[0]
    state = root / ".specspec/local"
    write_journal(
        state,
        {
            "kind": "edit",
            "files": {
                node.path: {"old": encode(snapshot.files[node.path]), "new": encode(b"other")},
            },
        },
    )
    target = root / node.path
    target.write_bytes(b"external edit")
    with pytest.raises(SpecError, match="External edit"):
        recover(root)
    assert target.read_bytes() == b"external edit"
    assert (state / "journal.json").exists()


def test_unsafe_journal_path_is_rejected(workspace):
    root, _ = workspace
    state = root / ".specspec/local"
    write_journal(
        state,
        {
            "kind": "edit",
            "files": {
                "../outside.txt": {"old": None, "new": encode(b"data")},
            },
        },
    )
    with pytest.raises(SpecError, match="Unsafe journal path"):
        recover(root)


def test_stale_lock_requires_explicit_acknowledgment(workspace):
    root, _ = workspace
    lock = root / ".specspec/local" / "lock"
    lock.write_text("unknown writer")
    assert not load_snapshot(root).valid
    with pytest.raises(SpecError, match="--force-lock"):
        recover(root)
    recover(root, force_lock=True)
    assert load_snapshot(root).valid


def test_recover_init_removes_only_known_node(workspace):
    root, _ = workspace
    snapshot = load_snapshot(root)
    node = snapshot.nodes[0]
    write_journal(
        root / ".specspec/local",
        {
            "kind": "init",
            "files": {
                node.path: {"old": None, "new": encode(snapshot.files[node.path])},
            },
        },
    )
    recover(root)
    assert not list((root / ".specspec").glob("*.md"))
    assert (root / ".specspec/local").is_dir()
    assert not (root / ".specspec/local" / "journal.json").exists()
