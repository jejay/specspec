"""Compact public commands, complete review patches and reconstructible protocol data."""

import json
import os
import subprocess
import sys

import pytest
from click.testing import CliRunner
from test_git import git, setup_repository

from specspec.application import compare
from specspec.cli import main
from specspec.model import API_VERSION, FORMAT_VERSION
from specspec.output import json_text
from specspec.wire import comparison, expand_comparison
from specspec.workspace import add_node, delete_nodes, load_snapshot, update_node


def call(root, *args, input=None):
    return CliRunner().invoke(main, ["--root", str(root), *args], input=input)


def api(root, **value):
    result = call(root, "api", input=json_text({"api_version": API_VERSION, "op": "read", **value}))
    assert result.exit_code == 0, result.output
    return json.loads(result.stdout)


@pytest.mark.parametrize("encoding", ["ascii", "cp1252"])
@pytest.mark.parametrize(
    "args", [[], ["diff"], ["query"], ["init"], ["add"], ["update"], ["delete"]]
)
def test_help_is_safe_through_legacy_windows_pipe_encodings(workspace, encoding, args):
    root, _ = workspace
    result = subprocess.run(
        [sys.executable, "-m", "specspec", "--root", str(root), *args, "--help"],
        env={**os.environ, "PYTHONIOENCODING": encoding, "PYTHONUTF8": "0"},
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr.decode(errors="replace")
    assert result.stdout.decode("ascii").startswith("Usage:")


def test_everyday_commands_advanced_help_and_no_parallel_legacy_surface(workspace):
    root, node_id = workspace
    assert {n for n, c in main.commands.items() if not c.hidden} == {
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
    assert set(main.commands["sources"].commands) == {"show", "capture", "reanchor"}
    assert set(main.commands["spotlight"].commands) == {"add", "show", "flush"}
    help_text = call(root, "--help").stdout
    assert "Everyday commands:" in help_text and "Advanced tools:" in help_text
    assert "api" not in help_text and "editor" not in help_text
    for args in [
        ("show",),
        ("show", "--help"),
        ("context", node_id),
        ("list",),
        ("export",),
        ("impact", node_id),
        ("validate",),
        ("hook", "check"),
        ("editor",),
        ("annotations",),
        ("apply",),
    ]:
        assert call(root, *args).exit_code == 2
    for args in [("init", "-m", "# Body"), ("add", "--parent", node_id, "-m", "# Body")]:
        assert call(root, *args, "--slug", "unused", input="# Body\n").exit_code == 2
    assert "--clear-parents" not in call(root, "update", "--help").stdout


def test_plain_outputs_are_readable_and_mutations_are_small(tmp_path):
    root = tmp_path
    result = call(root, "init", "-m", "# Manifesto 🐕\n", "--json")
    assert result.exit_code == 0, result.output
    first = json.loads(result.stdout)
    assert API_VERSION == 7 and FORMAT_VERSION == 7
    assert first["api_version"] == 7 and "snapshot" not in first["result"]
    parent = first["result"]["changed_ids"][0]
    result = call(root, "add", "--parent", parent, "-m", "# Useful heading\n", "--json")
    assert result.exit_code == 0, result.output
    receipt = json.loads(result.stdout)["result"]
    child = receipt["changed_ids"][0]
    assert receipt["nodes"][0]["path"] == f"_specspec/{child}.md"
    assert set(receipt["nodes"][0]) == {"id", "path"}
    assert len(result.stdout) < 1000 and '"body"' not in result.stdout
    listing = call(root, "query").stdout
    assert "manifesto" in listing and "Useful heading" in listing and not listing.startswith("{")
    record = call(root, "query", parent, "--max-distance", "0").stdout
    assert "manifesto" in record and "# Manifesto 🐕" in record
    assert call(root, "check").stdout.startswith("OK · 2 nodes")
    assert "\\ud83d" not in call(root, "query", "--json").stdout


def test_required_context_is_complete_without_optional_body_dump(workspace):
    root, parent = workspace
    _, selected = add_node(root, "requirement", [parent], "# Selected\n")
    _, sibling = add_node(root, "requirement", [parent], "# Sibling\nSECRET OPTIONAL BODY\n")
    args = ["query", selected, "--max-distance", "0", "--with-ancestors"]
    text = call(root, *args).stdout
    assert "# Selected" in text and "SECRET OPTIONAL BODY" not in text and sibling in text
    data = call(root, *args, "--json")
    result = json.loads(data.stdout)["result"]
    assert {n["id"] for n in result["target"]["nodes"]} == {parent, selected}
    assert result["selection"]["matched_ids"] == [selected]
    assert result["selection"]["ancestor_ids"] == [parent]
    assert result["selection"]["surrounding"]["omitted_ids"] == [sibling]
    exact = len(data.stdout.encode("utf8"))
    assert call(root, *args, "--json", "--max-bytes", str(exact)).exit_code == 0
    assert call(root, *args, "--json", "--max-bytes", str(exact - 1)).exit_code == 1


def test_human_controls_are_literal_but_machine_body_is_unchanged(workspace):
    root, parent = workspace
    update_node(root, parent, body="# Title\nESC: \x1b[2J\n")
    text = call(root, "query", parent, "--max-distance", "0").stdout
    assert "\x1b" not in text and "\\u001b[2J" in text
    node = json.loads(call(root, "query", parent, "--max-distance", "0", "--json").stdout)[
        "result"
    ]["target"]["nodes"][0]
    assert "\x1b[2J" in node["body"]


def test_full_diff_contains_raw_only_changes_edges_and_linked_source_summary(workspace):
    root, parent = workspace
    _, left = add_node(root, "requirement", [parent], "# Left\n")
    _, other = add_node(root, "requirement", [parent], "# Other\n")
    snapshot, child = add_node(root, "requirement", [left, other], "# Child\n\nold line\n")
    setup_repository(root)
    update_node(root, child, body="# Child\n\nnew line\n", parents=[left])
    parent_node = snapshot.graph.nodes[parent]
    file = root / parent_node.path
    file.write_bytes(
        file.read_bytes().replace(b"type: manifesto", b"type: manifesto # comment only")
    )
    result = call(root, "diff")
    assert result.exit_code == 0, result.output
    for needle in [
        "-old line",
        "+new line",
        "# comment only",
        "File-only change",
        "Relationship changes:",
        other,
        child,
    ]:
        assert needle in result.stdout
    compact = json.loads(call(root, "diff", "--json").stdout)["result"]
    assert "nodes" not in compact["base"] and "edges" not in compact["target"]
    assert all("patch" in f for f in compact["file_changes"])
    original, _ = compare(root, patches=True)
    assert expand_comparison(compact) == original
    summary = call(root, "diff", "--summary").stdout
    assert "File patch:" not in summary and "Nodes:" in summary


@pytest.mark.parametrize("after", [b"# Root\r\n", b"# Root", b"# Root\n\n"])
def test_full_diff_exposes_line_endings_and_final_newlines(workspace, after):
    root, parent = workspace
    update_node(root, parent, body="# Root\n")
    setup_repository(root)
    node = load_snapshot(root).graph.nodes[parent]
    path = root / node.path
    raw = path.read_bytes()
    header = raw[: raw.index(b"---\n", 4) + 4]
    path.write_bytes(header + after)
    result = call(root, "diff")
    assert result.exit_code == 0, result.output
    if after == b"# Root\n\n":
        assert "\n+\n" in result.stdout
    else:
        assert "Line endings/newline:" in result.stdout
    assert "File patch:" in result.stdout
    if not after.endswith(b"\n"):
        assert "No newline at end of file" in result.stdout


def test_shared_application_delta_keeps_ghosts_through_staging_until_commit(workspace):
    root, parent = workspace
    original, child = add_node(root, "requirement", [parent], "# Deleted historical body\n")
    setup_repository(root)
    delete_nodes(root, [child])
    for staged in (False, True):
        if staged:
            git(root, "add", "-u", "_specspec")
        response = api(root, base="HEAD", cache=True)
        result = response["result"]
        assert result["diff"]["target_ref"] == "workspace"
        assert "target" not in result["diff"] and "nodes" not in result["diff"]["base"]
        expanded = expand_comparison(result["diff"], result["snapshot"])
        assert child in {n["id"] for n in expanded["base"]["nodes"]}
        assert child not in {n["id"] for n in expanded["target"]["nodes"]}
        assert expanded["base"]["nodes"] == original.to_dict()["nodes"]
    git(root, "commit", "-m", "Remove experiment because its route is unused")
    assert api(root, base="HEAD")["result"]["diff"]["before"] == []
    assert child not in {n["id"] for n in api(root, base="HEAD")["result"]["snapshot"]["nodes"]}


def test_compact_projection_deduplicates_unchanged_revisions(workspace):
    root, parent = workspace
    for i in range(12):
        add_node(root, "requirement", [parent], f"# Requirement {i}\n" + "body " * 1000)
    setup_repository(root)
    original, _ = compare(root)
    compact = comparison(original)
    assert expand_comparison(compact) == original
    assert not compact["before"]
    assert len(json_text(compact)) < len(json_text(original)) * 0.6
    assert api(root, base="HEAD")["result"]["diff"]["before"] == []


def test_historical_application_read_ignores_invalid_saved_workspace_and_rejects_overlays(
    workspace,
):
    root, parent = workspace
    setup_repository(root)
    path = root / load_snapshot(root).graph.nodes[parent].path
    path.write_text("invalid", encoding="utf8")
    response = api(root, base="HEAD", target="HEAD")
    assert response["result"]["snapshot"]["valid"]
    bad = call(
        root,
        "api",
        input=json_text(
            {
                "api_version": 7,
                "op": "read",
                "base": "HEAD",
                "target": "HEAD",
                "documents": {"_specspec/x.md": "x"},
            }
        ),
    )
    assert bad.exit_code == 2 and not json.loads(bad.stdout)["ok"]


@pytest.mark.parametrize(
    "raw",
    [
        "{}",
        '{"api_version":5,"op":"read"}',
        '{"api_version":7,"op":"execute"}',
        '{"api_version":7,"op":"read","extra":true}',
    ],
)
def test_application_protocol_is_bounded_explicit_and_current_only(workspace, raw):
    root, _ = workspace
    result = call(root, "api", input=raw)
    assert result.exit_code == 2 and json.loads(result.stdout)["api_version"] == 7
