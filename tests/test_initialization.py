"""Initialization owns its exact node/guide bytes, not Git history or external edits."""

import json
import subprocess
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


def test_init_creates_git_and_packaged_guide_with_reserved_local_state(tmp_path):
    snapshot = initialize(tmp_path, "Test")
    assert snapshot.created_instructions is True
    assert (tmp_path / "AGENTS.md").read_bytes() == guide_bytes()
    assert (tmp_path / ".git").is_dir()
    assert snapshot.valid and len(snapshot.nodes) == 1
    assert snapshot.nodes[0].body == "Test\n"
    assert set(snapshot.files) == {f".specspec/{snapshot.nodes[0].id}.md"}
    assert {p.name for p in (tmp_path / ".specspec").iterdir()} == {
        "local",
        snapshot.nodes[0].id + ".md",
    }
    assert not (tmp_path / ".specspec/local/journal.json").exists()
    assert not list((tmp_path / ".specspec/local").glob("stage-*"))
    assert subprocess.check_output(["git", "-C", str(tmp_path), "ls-files"]) == b""
    assert (
        subprocess.run(
            ["git", "-C", str(tmp_path), "rev-parse", "--verify", "HEAD"], capture_output=True
        ).returncode
        != 0
    )
    (tmp_path / ".specspec/local/cache.json").write_text("{}")
    assert (
        subprocess.run(
            ["git", "-C", str(tmp_path), "check-ignore", "--quiet", ".specspec/local/cache.json"]
        ).returncode
        == 0
    )


@pytest.mark.parametrize(
    "body", [b"Owner instructions\r\n\x00\xff", b"", b"Owner\n", b"Owner\n\n\n"]
)
def test_existing_instructions_are_an_exact_prefix_followed_by_template(tmp_path, body):
    path = tmp_path / "AGENTS.md"
    path.write_bytes(body)
    snapshot = initialize(tmp_path, "# Product\n")
    separator = (
        b""
        if not body or body.endswith(b"\n\n")
        else b"\n"
        if body.endswith((b"\n", b"\r"))
        else b"\n\n"
    )
    assert snapshot.created_instructions is False
    assert path.read_bytes() == body + separator + guide_bytes()


def test_an_instruction_directory_is_rejected_before_git_or_graph_creation(tmp_path):
    (tmp_path / "AGENTS.md").mkdir()
    with pytest.raises(SpecError, match="regular file"):
        initialize(tmp_path, "# Product\n")
    assert (tmp_path / "AGENTS.md").is_dir()
    assert not (tmp_path / ".specspec").exists() and not (tmp_path / ".git").exists()


@pytest.mark.parametrize("dangling", [False, True])
def test_instruction_symlinks_are_rejected_without_following_them(tmp_path, dangling):
    target = tmp_path / "owner.md"
    if not dangling:
        target.write_bytes(b"Owner text\xff\r\n")
    path = tmp_path / "AGENTS.md"
    try:
        path.symlink_to(target)
    except OSError:
        pytest.skip("Symlinks are unavailable on this host.")
    with pytest.raises(SpecError, match="regular file"):
        initialize(tmp_path, "# Product\n")
    assert path.is_symlink() and target.exists() is not dangling
    assert not (tmp_path / ".specspec").exists() and not (tmp_path / ".git").exists()
    if not dangling:
        assert target.read_bytes() == b"Owner text\xff\r\n"


@pytest.mark.parametrize(
    "body", ["", " \n", "x" * (1024 * 1024)], ids=["empty", "whitespace", "oversized"]
)
def test_invalid_initial_graph_has_no_git_graph_or_guide_side_effects(tmp_path, body):
    with pytest.raises(SpecError):
        initialize(tmp_path, body)
    assert not any((tmp_path / name).exists() for name in [".specspec", "AGENTS.md", ".git"])


@pytest.mark.parametrize("failure", ["missing", "failed", "timeout"])
def test_git_is_a_required_successful_initialization_prerequisite(tmp_path, monkeypatch, failure):
    def run(*args, **kwargs):
        if failure == "missing":
            raise FileNotFoundError("git")
        if failure == "timeout":
            raise subprocess.TimeoutExpired("git", 30)
        return subprocess.CompletedProcess(args, 1, b"", b"Cannot initialize repository")

    monkeypatch.setattr(module.subprocess, "run", run)
    with pytest.raises(SpecError, match="Git is required|Cannot initialize"):
        initialize(tmp_path, "Test")
    assert not any((tmp_path / name).exists() for name in [".specspec", "AGENTS.md", ".git"])


def test_a_second_init_leaves_graph_guide_and_git_configuration_unchanged(tmp_path):
    first = initialize(tmp_path, "# Product\n")
    (tmp_path / "AGENTS.md").write_bytes(b"My edited instructions\r\n")
    config = (tmp_path / ".git/config").read_bytes()
    with pytest.raises(SpecError, match="overwrite"):
        initialize(tmp_path, "# Another product\n")
    assert load_snapshot(tmp_path).files == first.files
    assert (tmp_path / "AGENTS.md").read_bytes() == b"My edited instructions\r\n"
    assert (tmp_path / ".git/config").read_bytes() == config


@pytest.mark.parametrize("interruption", ["before-node", "before-guide", "after-guide"])
@pytest.mark.parametrize("existing", [False, True])
def test_recovery_rolls_back_partial_publication_and_exact_guide_original(
    tmp_path, monkeypatch, interruption, existing
):
    original = b"Owner instructions\r\n\xff" if existing else None
    if existing:
        (tmp_path / "AGENTS.md").write_bytes(original)
    link, replace = module.os.link, module.os.replace

    def publish(source, target):
        if interruption == "before-node" or (
            interruption == "before-guide" and Path(target).name == "AGENTS.md"
        ):
            raise OSError("Simulated publication interruption")
        return link(source, target)

    def amend(source, target):
        if interruption == "before-guide" and Path(target).name == "AGENTS.md":
            raise OSError("Simulated publication interruption")
        return replace(source, target)

    with monkeypatch.context() as patch:
        patch.setattr(module.os, "link", publish)
        patch.setattr(module.os, "replace", amend)
        if interruption == "after-guide":
            patch.setattr(
                module,
                "cleanup",
                lambda _: (_ for _ in ()).throw(OSError("Simulated interruption")),
            )
        with pytest.raises(OSError, match="interruption"):
            initialize(tmp_path, "# Product\n")
    journal = json.loads((tmp_path / ".specspec/local/journal.json").read_text())
    result = recover(tmp_path)
    assert set(result["restored"]) == set(journal["files"])
    assert not list((tmp_path / ".specspec").glob("*.md"))
    assert (tmp_path / ".git").is_dir()
    assert not (tmp_path / ".specspec/local/journal.json").exists()
    assert (
        (tmp_path / "AGENTS.md").read_bytes() == original
        if existing
        else not (tmp_path / "AGENTS.md").exists()
    )
    assert initialize(tmp_path, "# Retry\n").valid


def test_recovery_validates_all_files_before_touching_an_externally_changed_guide(
    tmp_path, monkeypatch
):
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
    assert (tmp_path / ".specspec/local/journal.json").exists()


@pytest.mark.parametrize("existing", [False, True])
def test_concurrent_instruction_changes_are_not_overwritten(tmp_path, monkeypatch, existing):
    if existing:
        (tmp_path / "AGENTS.md").write_bytes(b"Before")
    write = module.write_journal

    def race(state, journal):
        write(state, journal)
        (tmp_path / "AGENTS.md").write_bytes(b"Concurrent owner instructions\r\n")

    monkeypatch.setattr(module, "write_journal", race)
    with pytest.raises(SpecError, match="Instructions changed"):
        initialize(tmp_path, "# Product\n")
    before = load_snapshot(tmp_path).files
    with pytest.raises(SpecError, match="External edit"):
        recover(tmp_path)
    assert (tmp_path / "AGENTS.md").read_bytes() == b"Concurrent owner instructions\r\n"
    assert load_snapshot(tmp_path).files == before


@pytest.mark.parametrize("kind", ["edit", "init"])
@pytest.mark.parametrize(
    "path",
    [
        "../AGENTS.md",
        "./AGENTS.md",
        "AGENTS.md/x",
        ".specspec/../AGENTS.md",
        ".specspec/local/cache.md",
    ],
)
def test_instruction_exception_never_allows_other_journal_paths(tmp_path, kind, path):
    state = tmp_path / ".specspec/local"
    state.mkdir(parents=True)
    write_journal(state, {"kind": kind, "files": {path: {"old": None, "new": ""}}})
    with pytest.raises(SpecError, match="Unsafe journal path"):
        recover(tmp_path)


def test_edit_journals_cannot_write_root_instructions(tmp_path):
    state = tmp_path / ".specspec/local"
    state.mkdir(parents=True)
    write_journal(state, {"kind": "edit", "files": {"AGENTS.md": {"old": None, "new": ""}}})
    with pytest.raises(SpecError, match="Unsafe journal path"):
        recover(tmp_path)


@pytest.mark.parametrize("existing", [False, True])
def test_cli_reports_instruction_creation_or_amendment(tmp_path, existing):
    if existing:
        (tmp_path / "AGENTS.md").write_bytes(b"Owner")
    result = CliRunner().invoke(main, ["--root", str(tmp_path), "init", "-m", "Test", "--json"])
    assert result.exit_code == 0, result.output
    value = json.loads(result.stdout)["result"]
    assert value["agent_instructions"] == {"path": "AGENTS.md", "created": not existing}
    assert len(value["changed_ids"]) == 1
    assert (tmp_path / "AGENTS.md").read_bytes().endswith(guide_bytes())


@pytest.mark.parametrize("existing", [False, True])
def test_readable_receipt_mentions_create_or_append(tmp_path, existing):
    if existing:
        (tmp_path / "AGENTS.md").write_bytes(b"Owner")
    result = CliRunner().invoke(main, ["--root", str(tmp_path), "init", "-m", "Test"])
    assert result.exit_code == 0, result.output
    assert (
        f"Agent instructions: AGENTS.md ({'template appended' if existing else 'created'})"
        in result.stdout
    )


def test_packaged_guide_matches_current_behavior():
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
    for obsolete in [
        "_specspec",
        "all descendants",
        "Filename summaries",
        "--body",
        "API 7",
        "format 7",
    ]:
        assert obsolete not in text
