import importlib.util
from pathlib import Path

import pytest

from specspec.workspace import initialize


@pytest.fixture
def workspace(tmp_path: Path):
    snapshot = initialize(tmp_path, "# Project\n\nPreserve the user's intentions.\n")
    return tmp_path, snapshot.nodes[0].id


@pytest.fixture
def without_git(workspace):
    """Exercise deliberately non-Git states after init's required repository setup."""
    import shutil

    root, _ = workspace
    shutil.rmtree(root / ".git")
    assert not (root / ".git").exists()


@pytest.fixture(scope="session")
def gantt_verifier():
    source = Path(__file__).resolve().parents[1] / "example/gantt/history/verify.py"
    spec = importlib.util.spec_from_file_location("gantt_history_verify", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def gantt_history(tmp_path, gantt_verifier):
    from test_git import git

    source = Path(__file__).resolve().parents[1] / "example/gantt"
    root = gantt_verifier.clone_history(source, tmp_path / "gantt")
    git(root, "config", "user.name", "specspec tests")
    git(root, "config", "user.email", "tests@example.invalid")
    return root
