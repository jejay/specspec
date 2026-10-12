import importlib.util
from pathlib import Path

import pytest

from specspec.workspace import initialize


@pytest.fixture
def workspace(tmp_path: Path):
    snapshot = initialize(tmp_path, "# Project\n\nPreserve the user's intentions.\n")
    return tmp_path, snapshot.nodes[0].id


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
    git(root, "config", "user.name", "SpecSpec tests")
    git(root, "config", "user.email", "tests@example.invalid")
    return root
