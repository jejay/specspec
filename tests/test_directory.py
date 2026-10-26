"""The dot directory is literal and shared by discovery, raw/editor paths and Git."""

import json

import pytest
from click.testing import CliRunner

from specspec.cli import main
from specspec.editor import document_path
from specspec.model import SpecError
from specspec.workspace import discover_root, initialize


def test_nearest_dot_directory_wins_even_when_invalid(tmp_path):
    initialize(tmp_path, "# Outer\n")
    child = tmp_path / "nested"
    child.mkdir()
    (child / ".specspec").write_text("not a directory", encoding="utf8")
    assert discover_root(child) == child


def test_similar_or_old_directory_names_do_not_become_canonical(tmp_path):
    for name in ["_specspec", "xspecspec", "specspec", ".specspec-local"]:
        (tmp_path / name).mkdir()
    with pytest.raises(SpecError, match="No .specspec directory"):
        discover_root(tmp_path)
    snapshot = initialize(tmp_path, "# Product\n")
    assert snapshot.nodes[0].path.startswith(".specspec/")
    assert all((tmp_path / name).is_dir() for name in ["_specspec", "xspecspec", "specspec"])


@pytest.mark.parametrize(
    "path",
    [
        "xspecspec/AAAAAAA=.md",
        "_specspec/AAAAAAA=.md",
        ".specspec/nested/AAAAAAA=.md",
        ".specspec/../AGENTS.md",
        "./.specspec/AAAAAAA=.md",
        ".specspec\\AAAAAAA=.md",
    ],
)
def test_editor_and_raw_read_require_exact_canonical_paths(tmp_path, path):
    initialize(tmp_path, "# Product\n")
    with pytest.raises(SpecError):
        document_path(path)
    result = CliRunner().invoke(
        main, ["--root", str(tmp_path), "query", "--raw", "--path", path, "--json"]
    )
    assert result.exit_code == 2, result.output
    assert json.loads(result.output)["diagnostics"][0]["code"] == "PATH"
