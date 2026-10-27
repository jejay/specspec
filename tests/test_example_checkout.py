"""Manual and automated examples share a non-destructive standalone checkout path."""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
from test_git import git

from specspec.git import git_snapshot

ROOT = Path(__file__).resolve().parents[1]
GANTT = ROOT / "example/gantt"
SCRIPT = GANTT / "history/checkout.py"


@pytest.fixture(scope="module")
def checkout():
    spec = importlib.util.spec_from_file_location("gantt_checkout", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_default_workspace_is_external_and_portable(checkout):
    assert checkout.default_destination() == Path.home() / "Projects/specspec-examples/gantt"


def test_explicit_checkout_keeps_independent_git_history_and_lf_index(checkout, tmp_path):
    root = checkout.clone_history(GANTT, tmp_path / "examples with spaces/gantt")
    assert Path(git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve() == root
    assert (
        Path(
            git(root, "rev-parse", "--path-format=absolute", "--git-common-dir").decode().strip()
        ).resolve()
        == root / ".git"
    )
    assert git(root, "rev-list", "--count", "--all").strip() == b"8"
    assert git(root, "config", "core.autocrlf").strip() == b"false"
    assert not git(root, "status", "--porcelain")
    assert git_snapshot(root, staged=True).valid
    for tag in ["stage/01-code", "stage/02-spec", "stage/02-code", "stage/03-spec"]:
        assert git_snapshot(root, tag).valid
    assert not (GANTT / ".git").exists()


@pytest.mark.parametrize(
    "destination", [ROOT, GANTT / "checkout", ROOT / ".specspec/local/example-workspace"]
)
def test_checkout_refuses_development_worktree(checkout, destination):
    existed = destination.exists()
    with pytest.raises(ValueError, match="outside"):
        checkout.clone_history(GANTT, destination)
    assert destination.exists() == existed


def test_checkout_preserves_existing_destination_even_if_empty(checkout, tmp_path):
    destination = tmp_path / "existing"
    destination.mkdir()
    with pytest.raises(ValueError, match="already exists"):
        checkout.clone_history(GANTT, destination)
    sentinel = destination / "unsaved-experiment.txt"
    sentinel.write_text("Do not reset my project.")
    with pytest.raises(ValueError, match="already exists"):
        checkout.clone_history(GANTT, destination)
    assert sentinel.read_text() == "Do not reset my project."
    assert not (destination / ".git").exists()


def test_checkout_resolves_symlinks_and_preserves_broken_links(checkout, tmp_path):
    link = tmp_path / "development-alias"
    try:
        link.symlink_to(ROOT, target_is_directory=True)
    except OSError:
        pytest.skip("Directory symlinks are unavailable in this test environment.")
    with pytest.raises(ValueError, match="outside"):
        checkout.clone_history(GANTT, link / "forbidden")
    broken = tmp_path / "broken"
    broken.symlink_to(tmp_path / "missing", target_is_directory=True)
    with pytest.raises(ValueError, match="already exists"):
        checkout.clone_history(GANTT, broken)
    assert broken.is_symlink() and not (tmp_path / "missing").exists()


def test_checkout_refuses_an_empty_destination_created_during_claim(
    checkout, tmp_path, monkeypatch
):
    destination = tmp_path / "racing-creator"
    mkdir = Path.mkdir

    def racing_mkdir(path, *args, **kwargs):
        if path == destination:
            mkdir(path)  # Another creator wins after the initial existence check.
        return mkdir(path, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", racing_mkdir)
    with pytest.raises(ValueError, match="already exists"):
        checkout.clone_history(GANTT, destination)
    assert destination.is_dir() and not list(destination.iterdir())


def test_checkout_cli_reports_existing_workspace_without_overwriting(tmp_path):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path)], capture_output=True, text=True
    )
    assert result.returncode == 1
    assert "Destination already exists" in result.stderr
    assert not (tmp_path / ".git").exists()
