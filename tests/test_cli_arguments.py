"""Argument-first authoring and explicitly separate integration bulk inputs."""

import json
import os
import subprocess
import sys

import pytest
from click.testing import CliRunner

from specspec import cli
from specspec.model import API_VERSION, FORMAT_VERSION
from specspec.workspace import load_snapshot


def call(root, *args, input=None):
    result = CliRunner().invoke(cli.main, ["--root", str(root), *args, "--json"], input=input)
    return result, json.loads(result.stdout)


@pytest.mark.parametrize(
    "body",
    [
        "node.md",
        "\u001b[2J",
        "-",
        "--message",
        r"Literal \n and $value `tick`",
        "# Literal 🐕\r\n\r\nQuotes: \" and apostrophe' and \\  \r\n",
    ],
)
def test_single_message_is_literal_for_init_add_and_update(tmp_path, monkeypatch, body):
    (tmp_path / "node.md").write_text("FILE CONTENT MUST NOT BECOME THE BODY", encoding="utf8")

    def forbidden(path):
        pytest.fail("Message arguments must not read a body file or stdin.")

    monkeypatch.setattr(cli, "read_body", forbidden)
    result, data = call(tmp_path, "init", "--message=" + body)
    assert result.exit_code == 0, result.output
    assert data["api_version"] == API_VERSION == 7
    root_id = data["result"]["changed_ids"][0]
    assert load_snapshot(tmp_path).graph.nodes[root_id].body == body
    result, data = call(tmp_path, "add", "--parent", root_id, "--message=" + body)
    assert result.exit_code == 0, result.output
    id = data["result"]["changed_ids"][0]
    result, _ = call(tmp_path, "update", id, "--message=" + body)
    assert result.exit_code == 0, result.output
    saved = load_snapshot(tmp_path)
    assert saved.format_version == FORMAT_VERSION == 7 and saved.valid
    assert saved.graph.nodes[id].body == body
    assert (tmp_path / saved.graph.nodes[id].path).read_bytes().endswith(body.encode("utf8"))


def test_repeated_messages_join_without_cleanup_and_omission_keeps_body(workspace):
    root, manifesto = workspace
    pieces = ["# Heading\r\n", "  paragraph with trailing spaces  ", "last\n\n"]
    args = ["add", "--parent", manifesto]
    for piece in pieces:
        args += ["-m", piece]
    result, data = call(root, *args)
    assert result.exit_code == 0, result.output
    id = data["result"]["changed_ids"][0]
    expected = "\n\n".join(pieces)
    assert load_snapshot(root).graph.nodes[id].body == expected
    assert call(root, "update", id, "--parent", manifesto)[0].exit_code == 0
    assert load_snapshot(root).graph.nodes[id].body == expected
    before = load_snapshot(root).files
    assert call(root, "update", id, "-m", "")[0].exit_code != 0
    assert load_snapshot(root).files == before


@pytest.mark.parametrize("command", ["init", "add", "update"])
def test_message_and_integration_source_are_exclusive_before_reads(workspace, monkeypatch, command):
    root, id = workspace
    before = load_snapshot(root).files

    def forbidden(path):
        pytest.fail("Conflicting inputs must be rejected before file/stdin reads.")

    monkeypatch.setattr(cli, "read_body", forbidden)
    args = [command, *([id] if command == "update" else []), "-m", "", "--body", "-"]
    result, data = call(root, *args)
    assert result.exit_code == 2 and data["diagnostics"][0]["code"] == "ARGUMENT"
    assert load_snapshot(root).files == before


@pytest.mark.parametrize("pieces", [("é" * 9,), ("x" * 8, "y" * 8)])
def test_message_budget_counts_utf8_and_inserted_separators(workspace, monkeypatch, pieces):
    root, id = workspace
    before = load_snapshot(root).files
    monkeypatch.setattr(cli, "MAX_FILE_BYTES", 16)
    args = ["add", "--parent", id]
    for part in pieces:
        args += ["-m", part]
    result, data = call(root, *args)
    assert result.exit_code == 2 and data["diagnostics"][0]["code"] == "FORMAT"
    assert load_snapshot(root).files == before


def test_help_focuses_on_arguments_and_missing_inputs_do_not_read_stdin(workspace):
    root, id = workspace
    for command in ["init", "add", "update", "apply"]:
        text = CliRunner().invoke(cli.main, [command, "--help"]).stdout
        assert "--body" not in text and "--plan " not in text and "stdin" not in text
        assert ("--edits-json" if command == "apply" else "--message") in text
    for args in [("init",), ("add", "--parent", id), ("apply",)]:
        result, data = call(root, *args)
        assert result.exit_code == 2 and data["diagnostics"][0]["code"] == "ARGUMENT"
    # Old positional payloads cannot be mistaken for literal text or JSON.
    for args in [("init", "manifesto.md"), ("init", "-"), ("apply", "plan.json"), ("apply", "-")]:
        result = CliRunner().invoke(cli.main, ["--root", str(root), *args])
        assert result.exit_code == 2


def test_inline_subgraph_forward_aliases_and_dry_run(workspace):
    root, parent = workspace
    before = load_snapshot(root).files
    plan = json.dumps(
        {
            "edits": [
                {"op": "add", "as": "detail", "parents": ["$goal"], "body": "node.md"},
                {"op": "add", "as": "goal", "parents": [parent], "body": "# Goal\n"},
            ]
        }
    )
    result, data = call(root, "apply", "--edits-json", plan, "--dry-run", "--require-valid")
    assert result.exit_code == 0 and not data["result"]["applied"]
    assert load_snapshot(root).files == before
    result, data = call(root, "apply", "--edits-json", plan, "--require-valid")
    assert result.exit_code == 0 and data["result"]["graph_valid"]
    aliases = data["result"]["aliases"]
    saved = load_snapshot(root)
    assert saved.graph.nodes[aliases["detail"]].parents == [aliases["goal"]]
    assert saved.graph.nodes[aliases["detail"]].body == "node.md"
    assert all(b"$goal" not in raw for raw in saved.files.values())


def test_inline_batches_reject_files_duplicate_keys_and_ambiguous_sources(workspace):
    root, id = workspace
    before = load_snapshot(root).files
    plans = [
        json.dumps({"edits": [{"op": "add", "parents": [id], "body_file": "DO_NOT_OPEN.md"}]}),
        '{"edits":[],"edits":[]}',
    ]
    for plan in plans:
        result, data = call(root, "apply", "--edits-json", plan)
        assert result.exit_code == 2 and data["diagnostics"][0]["code"] == "BATCH"
        assert load_snapshot(root).files == before
    result, data = call(root, "apply", "--edits-json", plans[0], "--plan", "-")
    assert result.exit_code == 2 and data["diagnostics"][0]["code"] == "ARGUMENT"
    assert load_snapshot(root).files == before


def test_integration_body_files_and_stdin_plan_remain_available(workspace, tmp_path, monkeypatch):
    root, id = workspace
    directory = tmp_path / "inputs"
    directory.mkdir()
    body = "# Integration body\r\n\r\nPreserved whitespace.  \r\n"
    (directory / "body.md").write_bytes(body.encode("utf8"))
    result, data = call(root, "add", "--parent", id, "--body", str(directory / "body.md"))
    assert result.exit_code == 0
    added = data["result"]["changed_ids"][0]
    assert load_snapshot(root).graph.nodes[added].body == body
    monkeypatch.chdir(directory)
    plan = json.dumps({"edits": [{"op": "update", "id": added, "body_file": "body.md"}]})
    result, _ = call(root, "apply", "--plan", "-", input=plan)
    assert result.exit_code == 0 and load_snapshot(root).graph.nodes[added].body == body


@pytest.mark.parametrize("encoding", ["ascii", "cp1252"])
def test_real_argv_unicode_quotes_and_eol_round_trip(tmp_path, encoding):
    body = '# Absicht 🐕\r\n\r\nUmlaute äöü; $name `literal` "quotes" and \\  \r\n'
    result = subprocess.run(
        [sys.executable, "-m", "specspec", "--root", str(tmp_path), "init", "-m", body, "--json"],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        env={**os.environ, "PYTHONIOENCODING": encoding, "PYTHONUTF8": "0"},
    )
    assert result.returncode == 0, result.stderr.decode("utf8", errors="replace")
    assert json.loads(result.stdout)["api_version"] == 7
    saved = load_snapshot(tmp_path)
    assert saved.nodes[0].body == body
    assert (tmp_path / saved.nodes[0].path).read_bytes().endswith(body.encode("utf8"))


def test_large_integration_stdin_does_not_move_into_argv(tmp_path):
    body = "# Bulk integration\n" + "x" * (128 * 1024)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "specspec",
            "--root",
            str(tmp_path),
            "init",
            "--body",
            "-",
            "--json",
        ],
        input=body.encode("utf8"),
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr.decode("utf8", errors="replace")
    assert load_snapshot(tmp_path).nodes[0].body == body
