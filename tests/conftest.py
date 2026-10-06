from pathlib import Path

import pytest

from specspec.workspace import initialize


@pytest.fixture
def workspace(tmp_path: Path):
    snapshot = initialize(tmp_path, "# Project\n\nPreserve the user's intentions.\n")
    return tmp_path, snapshot.nodes[0].id
