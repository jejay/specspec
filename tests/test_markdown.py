"""Manual Markdown changes remain ordinary validated inputs, without provenance gates."""

import json

from click.testing import CliRunner

from specspec.cli import main
from specspec.git import semantic_diff
from specspec.workspace import add_node, load_snapshot, update_node


def test_manual_parent_body_and_deletion_changes_are_readable(workspace):
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
    update_node(root, leaf, body="Tool edit after manual edits\n")
    path.unlink()
    deleted = load_snapshot(root)
    assert deleted.valid and leaf not in deleted.graph.nodes
    assert (
        next(c for c in semantic_diff(after, deleted)["changes"] if c["id"] == leaf)["kind"]
        == "removed"
    )


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
        assert envelope["api_version"] == 5
        assert "fingerprint" not in envelope["result"]
        assert "managed_hash" not in result.output
