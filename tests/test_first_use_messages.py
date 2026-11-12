"""Situations a first user or agent meets get a message that says what to do next."""

import json
import subprocess

import pytest
from click.testing import CliRunner

from specspec import cli, git_process
from specspec.cli import main
from specspec.workspace import add_node, load_snapshot, recover


def invoke(root, *args, **kwargs):
    return CliRunner().invoke(main, ["--root", str(root), *args], **kwargs)


def test_a_terminal_on_stdin_gets_a_hint_instead_of_a_wait(workspace, monkeypatch):
    root, manifesto = workspace
    monkeypatch.setattr(cli, "stdin_terminal", lambda: True)
    before = load_snapshot(root).files
    for args in (["add", "--parent", manifesto], ["update", manifesto]):
        result = invoke(root, *args)
        assert result.exit_code == 2 and "No node text given" in result.stderr, args
        assert "-m" in result.stderr
    metadata_only = invoke(root, "update", manifesto, "--parent", manifesto)
    assert "No node text given" not in metadata_only.stderr
    assert load_snapshot(root).files == before


def test_empty_stdin_for_add_and_init_names_the_ways_to_give_text(workspace, tmp_path_factory):
    root, manifesto = workspace
    result = invoke(root, "add", "--parent", manifesto, input="")
    assert result.exit_code == 2 and "No node text given" in result.stderr
    assert ".specspec/" not in result.stderr
    fresh = tmp_path_factory.mktemp("fresh")
    result = CliRunner().invoke(main, ["--root", str(fresh), "init"], input="  \n")
    assert result.exit_code == 2 and "No node text given" in result.stderr
    assert not (fresh / ".specspec").exists()


def test_a_byte_order_mark_is_dropped_and_other_encodings_are_named(workspace):
    root, manifesto = workspace
    result = invoke(
        root, "add", "--parent", manifesto, "--json", input="﻿# Title\n\nBody\n".encode()
    )
    assert result.exit_code == 0, result.output
    node = json.loads(result.stdout)["result"]["changed_ids"][0]
    assert load_snapshot(root).graph.nodes[node].body == "# Title\n\nBody\n"
    latin = invoke(root, "add", "--parent", manifesto, input=b"# Caf\xe9\n")
    assert latin.exit_code == 2 and "not UTF-8" in latin.stderr and "0xe9" in latin.stderr


def test_parents_that_do_not_exist_are_rejected_before_writes(workspace):
    root, manifesto = workspace
    before = load_snapshot(root).files
    missing = invoke(root, "add", "--parent", "AAAAAAA=", "-m", "# Orphan")
    assert missing.exit_code == 1
    assert "Parent AAAAAAA= does not exist" in missing.stderr
    assert "nothing was written" in missing.stderr
    malformed = invoke(root, "add", "--parent", "x", "-m", "# Orphan")
    assert malformed.exit_code == 2 and "'x' is not a node ID" in malformed.stderr
    reparent = invoke(root, "add", "--parent", manifesto, "--parent", "AAAAAAA=", "-m", "# Two")
    assert reparent.exit_code == 1 and "AAAAAAA=" in reparent.stderr
    assert load_snapshot(root).files == before


def test_parents_a_node_already_declares_stay_editable(workspace):
    root, manifesto = workspace
    _, parent = add_node(root, "requirement", [manifesto], "# Parent\n")
    _, child = add_node(root, "requirement", [parent], "# Child\n")
    assert invoke(root, "delete", parent, "--yes").exit_code == 0
    result = invoke(root, "update", child, "-m", "# Child, repaired later")
    assert result.exit_code == 0, result.output
    assert load_snapshot(root).graph is not None


def test_an_unanswered_deletion_question_names_yes(workspace, monkeypatch):
    root, manifesto = workspace
    _, node = add_node(root, "requirement", [manifesto], "# Draft\n")
    monkeypatch.setattr(cli, "interactive_terminal", lambda: True)
    result = invoke(root, "delete", node, input="")
    assert result.exit_code == 1 and "--yes" in result.stderr
    assert "Aborted" not in result.output
    assert node in load_snapshot(root).graph.nodes


def test_agents_never_count_as_an_interactive_terminal(monkeypatch):
    class Stream:
        def __init__(self, tty):
            self.tty = tty

        def isatty(self):
            return self.tty

    monkeypatch.setattr(cli.sys, "stdin", Stream(True))
    monkeypatch.setattr(cli.sys, "stdout", Stream(False))
    assert not cli.interactive_terminal()
    monkeypatch.setattr(cli.sys, "stdout", Stream(True))
    assert cli.interactive_terminal()


def test_reads_and_writes_wait_for_a_running_writer_and_name_a_stale_lock(workspace):
    root, manifesto = workspace
    lock = root / ".specspec/local/lock"
    lock.write_text("12345")
    for args in (
        ["query", manifesto, "--max-distance", "0", "--with-ancestors"],
        ["query", "--max-distance", "2"],
        ["add", "--parent", manifesto, "-m", "# Blocked"],
    ):
        result = invoke(root, *args)
        assert result.exit_code != 0, args
        assert "Another specspec command is writing" in result.stderr, args
        assert "recover --force-lock" in result.stderr, args
    lock.unlink()
    assert invoke(root, "query", "--max-distance", "2").exit_code == 0


def test_a_lock_released_while_waiting_lets_the_command_proceed(workspace, monkeypatch):
    from specspec import workspace as module

    root, manifesto = workspace
    lock = root / ".specspec/local/lock"
    lock.write_text("12345")
    sleep = module.time.sleep

    def release(seconds):
        lock.unlink(missing_ok=True)
        sleep(seconds)

    monkeypatch.setattr(module.time, "sleep", release)
    result = invoke(root, "add", "--parent", manifesto, "-m", "# After the other writer")
    assert result.exit_code == 0, result.output


@pytest.mark.parametrize("journal", [b"", b'{"kind":"edit","fil'])
def test_an_unreadable_journal_is_removed_and_reported(workspace, journal):
    root, manifesto = workspace
    state = root / ".specspec/local"
    (state / "journal.json").write_bytes(journal)
    (state / "stage-0").write_bytes(b"partial")
    blocked = invoke(root, "add", "--parent", manifesto, "-m", "# Blocked")
    assert blocked.exit_code == 1 and "recover" in blocked.stderr
    result = recover(root)
    assert result["restored"] == []
    assert "no node was changed" in result["diagnostics"][0]["message"]
    assert not (state / "journal.json").exists() and not (state / "stage-0").exists()
    assert invoke(root, "add", "--parent", manifesto, "-m", "# Unblocked").exit_code == 0


def test_missing_git_says_how_to_install_it(tmp_path, monkeypatch):
    def absent(*args, **kwargs):
        raise FileNotFoundError(2, "The system cannot find the file specified")

    monkeypatch.setattr(git_process.subprocess, "run", absent)
    result = CliRunner().invoke(main, ["--root", str(tmp_path), "init", "-m", "# Product"])
    assert result.exit_code == 2
    assert "Git was not found" in result.stderr and "git-scm.com" in result.stderr
    assert not (tmp_path / ".specspec").exists()


def test_an_unknown_revision_is_named(workspace):
    root, _ = workspace
    result = invoke(root, "diff", "no-such-branch")
    assert result.exit_code == 2
    assert "Unknown revision 'no-such-branch'" in result.stderr


def test_a_conflicting_strict_source_link_says_how_to_reanchor(workspace):
    root, manifesto = workspace
    subprocess.run(["git", "-C", str(root), "config", "core.autocrlf", "false"], check=True)
    (root / "code.py").write_bytes(b"one\ntwo\nthree\n")
    subprocess.run(["git", "-C", str(root), "add", "code.py"], check=True)
    _, requirement = add_node(root, "requirement", [manifesto], "# Count\n")
    _, implementation = add_node(root, "implementation", [requirement], "# Code\n")
    capture = invoke(
        root,
        "sources",
        "capture",
        implementation,
        "code.py",
        "--range",
        "1:2",
        "--mode",
        "strict",
        "--staged",
    )
    assert capture.exit_code == 0, capture.output
    (root / "code.py").write_bytes(b"one\nTWO\nthree\n")
    result = invoke(root, "check", "--sources")
    assert result.exit_code == 1
    assert "Source 1: conflict. The linked lines changed" in result.stderr
    assert "specspec sources reanchor" in result.stderr and "--source 1 --staged" in result.stderr
