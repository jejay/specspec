"""Initialization ships usable instructions without acquiring existing project files."""

import json
from importlib.resources import files
from pathlib import Path

import pytest
from click.testing import CliRunner

from specspec import workspace as module
from specspec.cli import main
from specspec.model import SpecError
from specspec.workspace import initialize, load_snapshot, recover, write_journal


def guide_bytes():
    return files("specspec").joinpath("templates/AGENTS.md").read_bytes()


def test_init_creates_packaged_guide_outside_the_canonical_graph(tmp_path):
    snapshot = initialize(tmp_path, "# A product\n")
    assert snapshot.created_instructions is True
    assert (tmp_path / "AGENTS.md").read_bytes() == guide_bytes()
    assert snapshot.valid and len(snapshot.nodes) == 1
    assert set(snapshot.files) == {f".specspec/{snapshot.nodes[0].id}.md"}
    assert len(list((tmp_path / ".specspec").iterdir())) == 1
    assert not (tmp_path / ".specspec-local/journal.json").exists()
    assert not list((tmp_path / ".specspec-local").glob("stage-*"))


@pytest.mark.parametrize("body", [b"Owner instructions\r\n\x00\xff", b""])
def test_existing_instructions_are_preserved_byte_for_byte(tmp_path, body):
    path = tmp_path / "AGENTS.md"
    path.write_bytes(body)
    snapshot = initialize(tmp_path, "# Product\n")
    assert snapshot.created_instructions is False
    assert path.read_bytes() == body


def test_an_existing_instruction_directory_is_preserved(tmp_path):
    (tmp_path / "AGENTS.md").mkdir()
    snapshot = initialize(tmp_path, "# Product\n")
    assert snapshot.created_instructions is False
    assert (tmp_path / "AGENTS.md").is_dir()


@pytest.mark.parametrize("dangling", [False, True])
def test_existing_instruction_symlinks_are_not_read_or_replaced(tmp_path, dangling):
    target = tmp_path / "owner.md"
    if not dangling:
        target.write_bytes(b"Owner text\xff\r\n")
    path = tmp_path / "AGENTS.md"
    try:
        path.symlink_to(target)
    except OSError:
        pytest.skip("Symlinks are unavailable on this host.")
    snapshot = initialize(tmp_path, "# Product\n")
    assert snapshot.created_instructions is False
    assert path.is_symlink()
    assert target.exists() is not dangling
    if not dangling:
        assert target.read_bytes() == b"Owner text\xff\r\n"


@pytest.mark.parametrize(
    "body", ["", " \n", "x" * (1024 * 1024)], ids=["empty", "whitespace", "oversized"]
)
def test_invalid_initial_graph_creates_neither_graph_nor_guide(tmp_path, body):
    with pytest.raises(SpecError):
        initialize(tmp_path, body)
    assert not (tmp_path / ".specspec").exists()
    assert not (tmp_path / "AGENTS.md").exists()
    assert not (tmp_path / ".specspec-local/journal.json").exists()


def test_a_second_init_leaves_existing_graph_and_modified_guide_unchanged(tmp_path):
    first = initialize(tmp_path, "# Product\n")
    (tmp_path / "AGENTS.md").write_bytes(b"My edited instructions\r\n")
    with pytest.raises(SpecError, match="overwrite"):
        initialize(tmp_path, "# Another product\n")
    assert load_snapshot(tmp_path).files == first.files
    assert (tmp_path / "AGENTS.md").read_bytes() == b"My edited instructions\r\n"


@pytest.mark.parametrize("interruption", ["before-guide", "after-guide"])
def test_recovery_rolls_back_known_graph_and_new_instructions(tmp_path, monkeypatch, interruption):
    def interrupted(*args, **kwargs):
        raise OSError("Simulated initialization interruption")

    with monkeypatch.context() as patch:
        patch.setattr(
            module.os if interruption == "before-guide" else module,
            "link" if interruption == "before-guide" else "cleanup",
            interrupted,
        )
        with pytest.raises(OSError, match="interruption"):
            initialize(tmp_path, "# Product\n")
    before = load_snapshot(tmp_path)
    assert not before.valid and (tmp_path / ".specspec-local/journal.json").exists()
    result = recover(tmp_path)
    assert set(result["restored"]) == {*before.files, "AGENTS.md"}
    assert not (tmp_path / ".specspec").exists()
    assert not (tmp_path / "AGENTS.md").exists()
    assert not (tmp_path / ".specspec-local/journal.json").exists()


def test_recovery_never_acquires_preexisting_instructions(tmp_path, monkeypatch):
    path = tmp_path / "AGENTS.md"
    path.write_bytes(b"Owner instructions\r\n")
    with monkeypatch.context() as patch:
        patch.setattr(module, "cleanup", lambda _: (_ for _ in ()).throw(OSError("Interrupted")))
        with pytest.raises(OSError):
            initialize(tmp_path, "# Product\n")
    result = recover(tmp_path)
    assert "AGENTS.md" not in result["restored"]
    assert path.read_bytes() == b"Owner instructions\r\n"
    assert not (tmp_path / ".specspec").exists()


def test_recovery_validates_all_files_before_touching_a_changed_guide(tmp_path, monkeypatch):
    with monkeypatch.context() as patch:
        patch.setattr(module, "cleanup", lambda _: (_ for _ in ()).throw(OSError("Interrupted")))
        with pytest.raises(OSError):
            initialize(tmp_path, "# Product\n")
    before = load_snapshot(tmp_path).files
    (tmp_path / "AGENTS.md").write_bytes(b"Owner edit after interruption\r\n")
    with pytest.raises(SpecError, match="External edit to AGENTS.md"):
        recover(tmp_path)
    assert load_snapshot(tmp_path).files == before
    assert (tmp_path / "AGENTS.md").read_bytes() == b"Owner edit after interruption\r\n"
    assert (tmp_path / ".specspec-local/journal.json").exists()


def test_an_instruction_file_appearing_before_publication_is_not_overwritten(tmp_path, monkeypatch):
    link = module.os.link

    def race(source, target):
        Path(target).write_bytes(b"Concurrent owner instructions\r\n")
        return link(source, target)

    with monkeypatch.context() as patch:
        patch.setattr(module.os, "link", race)
        with pytest.raises(FileExistsError):
            initialize(tmp_path, "# Product\n")
    before = load_snapshot(tmp_path).files
    assert (tmp_path / "AGENTS.md").read_bytes() == b"Concurrent owner instructions\r\n"
    with pytest.raises(SpecError, match="External edit"):
        recover(tmp_path)
    assert load_snapshot(tmp_path).files == before


@pytest.mark.parametrize("kind", ["edit", "init"])
@pytest.mark.parametrize(
    "path", ["../AGENTS.md", "./AGENTS.md", "AGENTS.md/x", ".specspec/../AGENTS.md"]
)
def test_instruction_exception_never_allows_other_root_journal_paths(tmp_path, kind, path):
    state = tmp_path / ".specspec-local"
    state.mkdir()
    write_journal(state, {"kind": kind, "files": {path: {"old": None, "new": ""}}})
    with pytest.raises(SpecError, match="Unsafe journal path"):
        recover(tmp_path)


def test_edit_journals_cannot_write_root_instructions(tmp_path):
    state = tmp_path / ".specspec-local"
    state.mkdir()
    write_journal(state, {"kind": "edit", "files": {"AGENTS.md": {"old": None, "new": ""}}})
    with pytest.raises(SpecError, match="Unsafe journal path"):
        recover(tmp_path)


@pytest.mark.parametrize("existing", [False, True])
def test_cli_reports_instruction_creation_or_preservation(tmp_path, existing):
    if existing:
        (tmp_path / "AGENTS.md").write_text("Owner", encoding="utf8")
    result = CliRunner().invoke(
        main, ["--root", str(tmp_path), "init", "-m", "# Product", "--json"]
    )
    assert result.exit_code == 0, result.output
    value = json.loads(result.output)["result"]
    assert value["agent_instructions"] == {"path": "AGENTS.md", "created": not existing}
    assert len(value["changed_ids"]) == 1


def test_readable_receipt_mentions_the_guide(tmp_path):
    result = CliRunner().invoke(main, ["--root", str(tmp_path), "init", "-m", "# Product"])
    assert result.exit_code == 0, result.output
    assert "Agent instructions: AGENTS.md (created)" in result.output


def test_packaged_guide_matches_current_behavior_not_obsolete_draft_assumptions():
    text = guide_bytes().decode("utf8")
    for phrase in [
        ".specspec/",
        "<id>.md",
        "Tandem planning",
        "Agent planning",
        "Implementation",
        "--with-ancestors",
        "check --staged --sources --warnings-as-errors",
        "exactly selected files",
        "soft wrapping",
        "NEW is literal",
        "--replace",
        "without erasing its outcome",
        "Do not silently stage",
    ]:
        assert phrase in text
    assert "_specspec" not in text
    assert "all descendants" not in text
    assert "Filename summaries" not in text
