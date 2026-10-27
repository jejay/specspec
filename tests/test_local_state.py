"""The reserved local subtree is runtime data, never canonical node membership."""

import shutil

import pytest
from test_git import git, setup_repository

from specspec.git import git_snapshot
from specspec.model import SpecError
from specspec.workspace import STATE_DIR, initialize, load_snapshot, recover


def test_current_index_and_history_ignore_the_reserved_subtree(workspace):
    root, _ = workspace
    assert STATE_DIR == ".specspec/local"
    before = load_snapshot(root)
    path = root / STATE_DIR / "cache" / "AAAAAAA=.md"
    path.parent.mkdir()
    path.write_bytes(b"\xffnot a node\x00")
    assert load_snapshot(root).files == before.files
    assert load_snapshot(root).valid
    setup_repository(root)
    git(root, "add", "--force", ".specspec/local/cache/AAAAAAA=.md")
    indexed = git_snapshot(root, staged=True)
    assert indexed.valid and indexed.files == before.files
    git(root, "commit", "-m", "Deliberately tracked noncanonical test data")
    historical = git_snapshot(root, "HEAD")
    assert historical.valid and historical.files == before.files


def test_other_nested_directories_remain_invalid(workspace):
    root, _ = workspace
    (root / ".specspec/other").mkdir()
    assert any(d.code == "ENTRY" for d in load_snapshot(root).diagnostics)


@pytest.mark.parametrize("boundary", [".specspec", ".specspec/local"])
def test_runtime_parent_and_local_symlinks_are_never_followed(workspace, tmp_path, boundary):
    root, _ = workspace
    target = tmp_path / "external"
    target.mkdir()
    (target / "keep").write_bytes(b"Owner bytes")
    path = root / boundary
    saved = path.with_name(path.name + "-saved")
    path.rename(saved)
    try:
        path.symlink_to(target, target_is_directory=True)
    except OSError:
        saved.rename(path)
        pytest.skip("Symlinks are unavailable on this host.")
    assert not load_snapshot(root).valid
    with pytest.raises(SpecError):
        recover(root)
    assert (target / "keep").read_bytes() == b"Owner bytes"
    assert not (target / "lock").exists()


def test_legacy_sibling_is_not_a_runtime_fallback(workspace):
    root, _ = workspace
    legacy = root / ".specspec-local"
    legacy.mkdir()
    (legacy / "journal.json").write_text("Owner experiment")
    assert load_snapshot(root).valid
    recover(root)
    assert (legacy / "journal.json").read_text() == "Owner experiment"


def test_local_only_state_can_be_initialized_after_clean_recovery(tmp_path):
    local = tmp_path / STATE_DIR
    local.mkdir(parents=True)
    (local / "diagnostics.txt").write_text("Keep this experiment")
    assert initialize(tmp_path, "Test").valid
    assert (local / "diagnostics.txt").read_text() == "Keep this experiment"


def test_reserved_local_file_is_rejected_and_preserved(tmp_path):
    directory = tmp_path / ".specspec"
    directory.mkdir()
    (directory / "local").write_bytes(b"Owner bytes")
    with pytest.raises(SpecError):
        initialize(tmp_path, "Test")
    assert (directory / "local").read_bytes() == b"Owner bytes"


def test_state_move_does_not_create_an_old_sibling(workspace):
    root, _ = workspace
    assert (root / STATE_DIR).is_dir()
    assert not (root / ".specspec-local").exists()
    shutil.rmtree(root / ".git")
    # Existing readable graphs can remain inspectable when Git was deliberately removed.
    assert load_snapshot(root).valid
