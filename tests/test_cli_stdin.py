"""Default stdin is a body transport, not automatic output or filename detection."""

import json

import pytest
from click.testing import CliRunner

from specspec import cli
from specspec.cli_help import HELP
from specspec.workspace import add_node, load_snapshot


def invoke(root, *args, input=None):
    result = CliRunner().invoke(cli.main, ["--root", str(root), *args, "--json"], input=input)
    return result, json.loads(result.stdout)


@pytest.mark.parametrize(
    "text", ["# Stdin 🐕\r\n\r\nKeep spaces.  ", "binding.md", "-", "literal $name \\n"]
)
def test_automatic_input_for_init_add_and_whole_body_update(tmp_path, text):
    expected = text.replace("\r\n", "\n") + ("" if text.endswith(("\n", "\r")) else "\n")
    result, data = invoke(tmp_path, "init", input=text.encode("utf8"))
    assert result.exit_code == 0, result.output
    parent = data["result"]["changed_ids"][0]
    result, data = invoke(tmp_path, "add", "--parent", parent, input=text.encode("utf8"))
    assert result.exit_code == 0, result.output
    node = data["result"]["changed_ids"][0]
    result, _ = invoke(tmp_path, "update", node, input=text.encode("utf8"))
    assert result.exit_code == 0, result.output
    assert all(n.body == expected for n in load_snapshot(tmp_path).nodes)


@pytest.mark.parametrize("mode", ["message", "replace", "interactive-metadata"])
def test_explicit_text_modes_and_interactive_metadata_do_not_read_stdin(
    workspace, monkeypatch, mode
):
    root, parent = workspace
    _, node = add_node(root, "requirement", [parent], "# Before\n")
    monkeypatch.setattr(cli, "read_body", lambda: pytest.fail("This mode must not consume stdin."))
    if mode == "message":
        args = ["-m", "# After"]
    elif mode == "replace":
        args = ["--replace", "Before", "After"]
    else:
        monkeypatch.setattr(cli, "interactive_stdin", lambda: True)
        args = ["--parent", parent]
    result, _ = invoke(root, "update", node, *args)
    assert result.exit_code == 0, result.output


def test_empty_metadata_stream_preserves_body_but_nonempty_input_replaces_it(workspace):
    root, parent = workspace
    _, node = add_node(root, "requirement", [parent], "# Before\n\n\n")
    result, _ = invoke(root, "update", node, "--parent", parent, input=b"")
    assert result.exit_code == 0
    assert load_snapshot(root).graph.nodes[node].body == "# Before\n\n\n"
    result, _ = invoke(root, "update", node, "--parent", parent, input=b"# After")
    assert result.exit_code == 0
    assert load_snapshot(root).graph.nodes[node].body == "# After\n"


def test_empty_metadata_only_chain_has_no_ambiguous_body(workspace):
    root, parent = workspace
    _, node = add_node(root, "requirement", [parent], "# Before\n")
    before = load_snapshot(root).files
    result, _ = invoke(
        root,
        "update",
        parent,
        "--parents-json",
        "[]",
        "update",
        node,
        "--parent",
        parent,
        input=b"",
    )
    assert result.exit_code == 0, result.output
    assert load_snapshot(root).files == before
    result, data = invoke(
        root,
        "update",
        parent,
        "--parents-json",
        "[]",
        "update",
        node,
        "--parent",
        parent,
        input=b"# Ambiguous",
    )
    assert result.exit_code == 2 and "ambiguous" in data["diagnostics"][0]["message"]
    assert load_snapshot(root).files == before


@pytest.mark.parametrize(
    "body",
    [b"\xffinvalid", b"x" * (1024 * 1024 + 1), b" \n"],
    ids=["invalid-utf8", "oversized", "blank"],
)
def test_invalid_or_oversized_stdin_fails_without_writes(workspace, body):
    root, parent = workspace
    before = load_snapshot(root).files
    result, data = invoke(root, "add", "--parent", parent, input=body)
    assert result.exit_code != 0 and not data["ok"]
    assert load_snapshot(root).files == before
    assert not (root / ".specspec/local/journal.json").exists()


def test_help_bodies_are_fifty_to_seventy_percent_of_the_previous_guides():
    baseline = {
        "root": 340,
        "init": 203,
        "query": 416,
        "add": 262,
        "update": 357,
        "delete": 241,
        "check": 216,
        "diff": 231,
        "recover": 133,
        "sources": 111,
        "sources show": 163,
        "sources capture": 197,
        "sources reanchor": 171,
        "spotlight": 123,
        "spotlight add": 167,
        "spotlight show": 110,
        "spotlight flush": 88,
        "api": 161,
    }
    for name, text in HELP.items():
        ratio = len(text.split()) / baseline[name]
        assert 0.5 <= ratio <= 0.7, (name, ratio)
        assert not any(flag in text for flag in ["--root", "--json", "--body", "API-7", "API 7"])


def test_private_startup_probe_is_project_and_stdin_independent(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Startup handshake must not read a project or request payload.")

    monkeypatch.setattr(cli, "root_path", forbidden)
    monkeypatch.setattr(cli, "application_request", forbidden)
    result = CliRunner().invoke(cli.main, ["api", "--probe"], input="NOT A REQUEST")
    assert result.exit_code == 0, result.output
    response = json.loads(result.stdout)
    assert response["ok"] and response["diagnostics"] == []
    assert set(response["result"]["features"]) == {
        "stdin-body",
        "project-init",
        "nested-local-state",
    }
    failed = CliRunner().invoke(cli.main, ["api", "--probe", "--stream"])
    assert failed.exit_code == 2 and not json.loads(failed.stdout)["ok"]


def test_normal_query_omits_internal_versions_but_raw_documents_keep_evidence(workspace):
    root, parent = workspace
    result = CliRunner().invoke(cli.main, ["--root", str(root), "query", "--human"])
    assert result.exit_code == 0
    assert "format_version" not in result.stdout and "Node format:" not in result.stdout
    raw = CliRunner().invoke(cli.main, ["--root", str(root), "query", parent, "--raw"])
    assert raw.exit_code == 0 and "format_version: 7" in raw.stdout
