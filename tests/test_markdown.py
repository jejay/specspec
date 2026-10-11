"""Manual Markdown changes remain ordinary validated inputs, without provenance gates."""

import json
from dataclasses import replace

from click.testing import CliRunner

from specspec.cli import main
from specspec.format import read_document, serialize
from specspec.git import git_snapshot, semantic_diff
from specspec.workspace import add_node, load_snapshot, migrate, update_node


def test_manual_parent_body_and_withdrawal_changes_are_readable(workspace):
    root, manifesto = workspace
    _, left = add_node(root, "requirement", [manifesto], "Left\n", "left")
    _, right = add_node(root, "requirement", [manifesto], "Right\n", "right")
    before, leaf = add_node(root, "requirement", [left], "Child\n", "child")
    node = before.graph.nodes[leaf]
    path = root / node.path
    raw = path.read_bytes().replace(left.encode(), right.encode()) + b"\nManually added text.\n"
    path.write_bytes(raw)
    after = load_snapshot(root)
    assert after.valid and after.graph.nodes[leaf].parents == [right]
    assert after.graph.nodes[leaf].body.endswith("Manually added text.\n")
    assert path.read_bytes() == raw
    diff = semantic_diff(before, after)
    assert [left, leaf] in diff["removed_edges"] and [right, leaf] in diff["added_edges"]
    path.write_bytes(raw.replace(b"type: requirement", b"type: requirement\nretired: true"))
    assert load_snapshot(root).graph.nodes[leaf].retired
    update_node(root, leaf, body="Tool edit after manual edits\n")
    assert load_snapshot(root).graph.nodes[leaf].retired


def test_v2_stale_or_missing_hashes_are_ignored_and_migration_removes_them(workspace):
    root, manifesto = workspace
    _, child = add_node(root, "requirement", [manifesto], "Child\n", "child")
    current = load_snapshot(root)
    for node in current.nodes:
        raw = current.files[node.path]
        if node.id == manifesto:
            raw = raw.replace(b"format_version: 3", b"format_version: 2 # keep comment")
            raw = raw.replace(b"type: manifesto", b"type: manifesto\nmanaged_hash: obsolete")
        else:
            raw += b"\nManual legacy edit without a marker.\n"
        (root / node.path).write_bytes(raw)
    before = load_snapshot(root)
    assert before.valid and before.format_version == 2
    assert before.graph.nodes[child].body.endswith("Manual legacy edit without a marker.\n")
    after = migrate(root)
    assert after.valid and after.format_version == 3
    assert set(after.files) == set(before.files)
    for node in after.nodes:
        assert node.body == before.graph.nodes[node.id].body
        assert "managed_hash" not in read_document(after.files[node.path], node.path)[0]
    assert b"# keep comment" in after.files[after.graph.nodes[manifesto].path]
    assert migrate(root).files == after.files


def test_cli_outputs_have_no_content_hashes(workspace):
    root, manifesto = workspace
    runner = CliRunner()
    for args in [
        ["list"],
        ["show", manifesto],
        ["impact", manifesto],
        ["context", manifesto],
        ["validate"],
        ["export", "--format", "json"],
    ]:
        result = runner.invoke(
            main,
            ["--root", str(root), *args, "--json"]
            if args[0] != "export"
            else ["--root", str(root), *args],
        )
        assert result.exit_code == 0, result.output
        envelope = json.loads(result.output)
        assert envelope["api_version"] == 3
        assert "fingerprint" not in envelope["result"]
        assert "managed_hash" not in result.output


def test_manually_edited_v2_git_blobs_remain_readable(workspace):
    from test_git import git, setup_repository

    root, _ = workspace
    before = load_snapshot(root)
    node = before.nodes[0]
    raw = serialize(replace(node, body="# Manual historical text\n"))
    raw = raw.replace(b"format_version: 3", b"format_version: 2\nmanaged_hash: stale")
    (root / node.path).write_bytes(raw)
    setup_repository(root)
    assert git_snapshot(root, "HEAD").valid
    assert git_snapshot(root, staged=True).valid
    migrate(root)
    git(root, "add", "_specspec")
    assert git_snapshot(root, staged=True).format_version == 3
    result = semantic_diff(git_snapshot(root, "HEAD"), load_snapshot(root))
    assert result["impact_complete"]
    assert result["changes"][0]["fields"] == ["format_version"]
