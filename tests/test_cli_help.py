"""Helpful local command guides and one specification inspection vocabulary."""

import base64
import json
import os
import subprocess
import sys

import click
import pytest
from click.testing import CliRunner
from test_git import git, setup_repository

from specspec import cli
from specspec.workspace import add_node, load_snapshot

PATHS = [
    [],
    ["init"],
    ["query"],
    ["add"],
    ["update"],
    ["delete"],
    ["check"],
    ["diff"],
    ["recover"],
    ["sources"],
    ["sources", "show"],
    ["sources", "capture"],
    ["sources", "reanchor"],
    ["spotlight"],
    ["spotlight", "add"],
    ["spotlight", "show"],
    ["spotlight", "flush"],
    ["api"],
]


def call(root, *args):
    result = CliRunner().invoke(cli.main, ["--root", str(root), *args, "--json"])
    assert result.stdout, (result.output, result.exception)
    return result, json.loads(result.stdout)


@pytest.mark.parametrize("path", PATHS)
def test_every_help_is_substantial_specific_and_project_independent(monkeypatch, path):
    def forbidden(*args, **kwargs):
        pytest.fail("Help must not discover/read a project, payload or application request.")

    monkeypatch.setattr(cli, "root_path", forbidden)
    monkeypatch.setattr(cli, "read_body", forbidden)
    monkeypatch.setattr(cli, "application_request", forbidden)
    result = CliRunner().invoke(cli.main, [*path, "--help"], input="MUST NOT BE READ")
    assert result.exit_code == 0, result.output
    text = result.stdout
    assert text.startswith("Usage:") and "Options:" in text
    assert len(text.split()) >= 100, (path, text)
    assert "specspec " in text and any(
        word in text.lower() for word in ["example", "workflow", "one-shot"]
    )
    assert text.isascii() and "\b" not in text
    assert not any(ord(c) < 32 and c not in "\n\r\t" for c in text)


@pytest.mark.parametrize("encoding", ["ascii", "cp1252"])
@pytest.mark.parametrize("path", PATHS)
def test_all_help_survives_real_legacy_encoded_pipes_without_a_project(path, encoding, tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "specspec",
            "--root",
            str(tmp_path / "not-a-project"),
            *path,
            "--help",
        ],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        env={**os.environ, "PYTHONIOENCODING": encoding, "PYTHONUTF8": "0"},
    )
    assert result.returncode == 0, result.stderr.decode("utf8", errors="replace")
    assert result.stdout.decode("ascii").startswith("Usage:")


def test_root_lists_seven_commands_without_summary_ellipses_and_query_examples():
    text = CliRunner().invoke(cli.main, ["--help"]).stdout
    assert {name for name in cli.main.commands if not cli.main.commands[name].hidden} == {
        "init",
        "query",
        "add",
        "update",
        "delete",
        "check",
        "diff",
        "sources",
        "spotlight",
        "recover",
    }
    commands = text.split("Everyday commands:", 1)[1]
    assert not any(line.rstrip().endswith("...") for line in commands.splitlines())
    assert "--max-distance 0 --with-ancestors" in text
    assert "including the final '='" in " ".join(text.split())
    assert "do not" in text.lower() or "nothing stages" in text.lower()
    assert "show" not in cli.main.commands and "api" not in commands


def test_help_explains_the_actual_choices_not_only_option_names():
    runner = CliRunner()
    query = " ".join(runner.invoke(cli.main, ["query", "--help"]).stdout.split())
    for phrase in [
        "UNION",
        "not intersection",
        "rounded up",
        "shortest",
        "longest",
        "including themselves",
        "--raw",
        "--staged",
    ]:
        assert phrase in query, phrase
    update = " ".join(runner.invoke(cli.main, ["update", "--help"]).stdout.split())
    for phrase in [
        "WHOLE body",
        "SAME original body",
        "REPLACES",
        "does not append",
        "NEW is always literal",
        "--body FILE|-",
    ]:
        assert phrase in update, phrase
    capture = " ".join(runner.invoke(cli.main, ["sources", "capture", "--help"]).stdout.split())
    for phrase in [
        "inclusive",
        "1-based",
        "strict",
        "expanding",
        "CURRENT",
        "Code defaults",
        "Git staging",
    ]:
        assert phrase in capture, phrase
    assert (
        "--warnings-as-errors"
        in runner.invoke(cli.main, ["check", "--help"]).stdout.split("Options:")[1]
    )


def test_help_keeps_option_spellings_intact_when_wrapping_prose():
    text = CliRunner().invoke(cli.main, ["query", "--help"], terminal_width=52).stdout
    assert "--max-\ndistance" not in text and "--max-\n  distance" not in text
    assert "specspec query NODE_ID --max-distance 0 --with-ancestors --human" in text


def test_show_is_removed_not_a_hidden_alias_and_does_not_read_project(monkeypatch):
    monkeypatch.setattr(
        cli, "root_path", lambda p: pytest.fail("Removed command must not read files.")
    )
    for args in [["show"], ["show", "--help"], ["show", "AAAAAAA=", "--raw", "--json"]]:
        result = CliRunner().invoke(cli.main, args)
        assert result.exit_code == 2 and "No such command 'show'" in result.stderr
    assert isinstance(cli.main.commands["sources"], click.Group)
    assert "show" in cli.main.commands["sources"].commands
    assert "show" in cli.main.commands["spotlight"].commands


@pytest.mark.parametrize(
    "raw", [b"not frontmatter\r\n", b"---\nunfinished: [\n", b"\xffinvalid\x00"]
)
def test_query_raw_retains_literal_malformed_bytes_by_id_and_path(workspace, raw):
    root, parent = workspace
    _, id = add_node(root, "requirement", [parent], "# Before")
    path = f"_specspec/{id}.md"
    (root / path).write_bytes(raw)
    before = load_snapshot(root).files
    for selector in [[id], ["--path", path]]:
        result, data = call(root, "query", *selector, "--raw")
        assert result.exit_code == 0 and data["ok"], result.output
        value = data["result"]
        assert value["path"] == path
        if raw.startswith(b"\xff"):
            assert base64.b64decode(value["bytes_base64"]) == raw
        else:
            assert value["text"].encode("utf8") == raw
    assert load_snapshot(root).files == before


def test_query_raw_reads_current_index_and_history_without_checkout(workspace):
    root, parent = workspace
    _, id = add_node(root, "requirement", [parent], "# Old\r\n")
    path = root / f"_specspec/{id}.md"
    setup_repository(root)
    old = path.read_bytes()
    path.write_bytes(old.replace(b"Old", b"Index"))
    git(root, "add", "_specspec")
    indexed = path.read_bytes()
    path.write_bytes(indexed.replace(b"Index", b"Saved"))
    index, refs = git(root, "ls-files", "--stage"), git(root, "show-ref")
    for args, expected in [
        ([], path.read_bytes()),
        (["--staged"], indexed),
        (["--target", "HEAD"], old),
    ]:
        result, data = call(root, "query", id, "--raw", *args)
        assert result.exit_code == 0 and data["result"]["text"].encode("utf8") == expected
    assert git(root, "ls-files", "--stage") == index and git(root, "show-ref") == refs


@pytest.mark.parametrize(
    "flags",
    [
        ["--path", "_specspec/AAAAAAA=.md"],
        ["--staged"],
        ["--raw", "--base", "HEAD"],
        ["--raw", "--human"],
        ["--raw", "--with-ancestors"],
        ["--raw", "--issues"],
        ["--raw", "--min-distance", "1"],
        ["--raw", "--max-distance", "0"],
        ["--raw", "--influence", "1"],
        ["--raw", "--target", "HEAD", "--staged"],
    ],
)
def test_raw_conflicts_fail_before_reading_graph_inputs(workspace, monkeypatch, flags):
    root, parent = workspace
    monkeypatch.setattr(
        cli, "target_graph", lambda *a: pytest.fail("Reject ambiguous raw selectors first.")
    )
    result, data = call(root, "query", parent, *flags)
    assert result.exit_code == 2 and data["diagnostics"][0]["code"] == "ARGUMENT"
