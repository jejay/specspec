"""Compatibility and guarded conversion of original tool-managed v1 blobs."""

import json
from dataclasses import replace
from pathlib import Path

import pytest
from click.testing import CliRunner
from test_git import git, setup_repository

from specspec import workspace as module
from specspec.cli import main
from specspec.format import read_document, serialize, yaml_parser
from specspec.git import git_snapshot, semantic_diff
from specspec.model import SpecError
from specspec.workspace import add_node, load_snapshot, migrate, recover, set_retired, update_node

FIXTURES = Path(__file__).parent / "fixtures" / "v1"


@pytest.fixture
def legacy_workspace(tmp_path):
    directory = tmp_path / "_specspec"
    directory.mkdir()
    for file in FIXTURES.glob("*.md"):
        raw = file.read_bytes()
        # Comments and CRLF do not alter the original v1 semantic hash.
        raw = raw.replace(b"type: manifesto", b"type: manifesto # preserve this comment")
        raw = raw.replace(b"\n", b"\r\n")
        (directory / file.name).write_bytes(raw)
    snapshot = load_snapshot(tmp_path)
    assert snapshot.valid, snapshot.diagnostics
    return tmp_path, snapshot


def test_legacy_reader_ignores_hashes_without_exposing_approval(legacy_workspace):
    root, before = legacy_workspace
    assert before.format_version == 1
    assert all("managed_hash" not in node.to_dict() for node in before.nodes)
    assert all(
        "status" not in node.to_dict() and "legacy_status" not in node.to_dict()
        for node in before.nodes
    )
    assert sum(node.retired for node in before.nodes) == 1
    result = CliRunner().invoke(main, ["--root", str(root), "export", "--format", "json"])
    assert result.exit_code == 0
    assert json.loads(result.output)["api_version"] == 3
    assert load_snapshot(root).files == before.files


def test_migration_preserves_identity_relationships_body_and_comments(legacy_workspace):
    root, before = legacy_workspace
    after = migrate(root)
    assert after.valid and after.format_version == 3
    assert set(after.files) == set(before.files)
    for node in after.nodes:
        old = before.graph.nodes[node.id]
        assert node.body == old.body
        assert node.parents == old.parents
        assert node.path == old.path
        assert node.sources == old.sources
        assert node.extensions == old.extensions
        assert node.retired == old.retired
        header = read_document(after.files[node.path], node.path)[0]
        assert "status" not in header and "managed_hash" not in header
        if node.type == "manifesto":
            assert b"# preserve this comment" in after.files[node.path]
    assert migrate(root).files == after.files
    diff = semantic_diff(before, after)
    assert diff["added_edges"] == diff["removed_edges"] == []
    # Dropped approval labels are not invented per-node semantic changes.
    assert [item["fields"] for item in diff["changes"]] == [["format_version"]]


def test_migration_preserves_optional_sources_and_extensions(legacy_workspace):
    import io

    root, before = legacy_workspace
    old = next(
        node
        for node in before.nodes
        if node.type == "requirement" and not node.retired and not before.graph.children[node.id]
    )
    data, body = read_document(before.files[old.path], old.path)
    data["type"] = "implementation"
    data["sources"] = [{"path": "source.py", "symbol": "example"}]
    data["extensions"] = {"example:context": {"nested": [1, True, "text"]}}
    (root / "source.py").write_text("# example\n", encoding="utf-8")
    # Manual changes to a disposable legacy fixture need no digest update.
    data["managed_hash"] = "ignored stale marker"
    stream = io.StringIO()
    yaml_parser().dump(data, stream)
    (root / old.path).write_bytes(("---\n" + stream.getvalue() + "---\n" + body).encode("utf-8"))
    before = load_snapshot(root)
    assert before.valid
    after = migrate(root)
    assert after.graph.nodes[old.id].sources == data["sources"]
    assert after.graph.nodes[old.id].extensions == data["extensions"]
    assert after.graph.nodes[old.id].body == body


def test_legacy_writes_require_explicit_migration(legacy_workspace):
    root, before = legacy_workspace
    node = next(node for node in before.nodes if node.type == "manifesto")
    operations = [
        lambda: add_node(root, "requirement", [node.id], "New\n", "new"),
        lambda: update_node(root, node.id, body="Edit\n"),
        lambda: set_retired(root, [node.id], True),
    ]
    for operation in operations:
        with pytest.raises(SpecError, match="migrate"):
            operation()
        assert load_snapshot(root).files == before.files


def test_migration_accepts_manual_changes_and_ignores_obsolete_hashes(legacy_workspace):
    root, before = legacy_workspace
    node = next(node for node in before.nodes if node.type == "manifesto")
    raw = before.files[node.path].replace(b"practical", b"different")
    (root / node.path).write_bytes(raw)
    assert load_snapshot(root).valid
    assert load_snapshot(root).files[node.path] == raw
    migrated = migrate(root)
    assert "different" in migrated.graph.nodes[node.id].body
    assert b"managed_hash:" not in migrated.files[node.path]
    assert not (root / ".specspec-local" / "journal.json").exists()


def test_interrupted_migration_recovers_the_complete_original_schema(legacy_workspace, monkeypatch):
    root, before = legacy_workspace
    original = module.os.replace
    replacements = 0

    def interrupted(source, target):
        nonlocal replacements
        if Path(target).parent == root / "_specspec":
            replacements += 1
            if replacements == 2:
                raise OSError("Interrupted schema migration")
        return original(source, target)

    monkeypatch.setattr(module.os, "replace", interrupted)
    with pytest.raises(OSError, match="Interrupted"):
        migrate(root)
    assert (root / ".specspec-local" / "journal.json").exists()
    assert not load_snapshot(root).valid
    monkeypatch.setattr(module.os, "replace", original)
    recover(root)
    assert load_snapshot(root).files == before.files
    assert load_snapshot(root).format_version == 1
    assert migrate(root).valid


def test_staged_and_historical_v1_v3_snapshots_remain_readable(legacy_workspace):
    root, before = legacy_workspace
    setup_repository(root)
    assert git_snapshot(root, staged=True).format_version == 1
    after = migrate(root)
    # Unstaged conversion must not change staged validation.
    assert git_snapshot(root, staged=True).format_version == 1
    git(root, "add", "_specspec")
    assert git_snapshot(root, staged=True).valid
    assert git_snapshot(root, staged=True).format_version == 3
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Approval-free schema")
    old = git_snapshot(root, "HEAD~1")
    new = git_snapshot(root, "HEAD")
    assert old.valid and new.valid
    assert old.format_version == 1 and new.format_version == 3
    assert new.files == after.files
    assert all("status" not in node.to_dict() for node in old.nodes + new.nodes)
    result = CliRunner().invoke(
        main, ["--root", str(root), "diff", "--base", "HEAD~1", "--target", "HEAD", "--json"]
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["result"]["impact_complete"]


def test_cli_migration_and_withdrawal_filters_have_no_approval_commands(legacy_workspace):
    root, before = legacy_workspace
    runner = CliRunner()
    prefix = ["--root", str(root)]
    result = runner.invoke(main, [*prefix, "migrate", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["api_version"] == 3
    assert len(payload["result"]["changed_ids"]) == len(before.nodes)
    assert runner.invoke(main, [*prefix, "accept", "any-id"]).exit_code == 2
    assert runner.invoke(main, [*prefix, "list", "--status", "proposed"]).exit_code == 2
    live = json.loads(runner.invoke(main, [*prefix, "list", "--live", "--json"]).output)["result"]
    retired = json.loads(runner.invoke(main, [*prefix, "list", "--retired", "--json"]).output)[
        "result"
    ]
    assert all(not node["retired"] for node in live["nodes"])
    assert all(node["retired"] for node in retired["nodes"])
    assert len(live["nodes"]) + len(retired["nodes"]) == len(before.nodes)
    assert runner.invoke(main, [*prefix, "list", "--live", "--retired"]).exit_code == 2
    id = retired["nodes"][0]["id"]
    assert runner.invoke(main, [*prefix, "restore", id, "--json"]).exit_code == 0
    assert not load_snapshot(root).graph.nodes[id].retired
    again = runner.invoke(main, [*prefix, "migrate", "--json"])
    assert json.loads(again.output)["result"]["changed_ids"] == []


def test_context_includes_live_siblings_without_an_approval_filter(legacy_workspace):
    root, before = legacy_workspace
    migrate(root)
    parent = next(node for node in before.nodes if node.type == "requirement" and not node.retired)
    result = CliRunner().invoke(main, ["--root", str(root), "context", parent.id, "--json"])
    context = json.loads(result.output)["result"]
    assert "proposal_ids" not in context
    expected = set().union(*(before.graph.children[id] for id in parent.parents))
    expected -= set(context["required_ids"])
    expected = {id for id in expected if not before.graph.nodes[id].retired}
    assert set(context["sibling_ids"]) == expected
    assert all("status" not in node for node in context["nodes"])


@pytest.mark.parametrize("retired", ["true", 1, None, [], {}])
def test_withdrawal_flag_is_strictly_boolean(workspace, retired):
    root, _ = workspace
    node = load_snapshot(root).nodes[0]
    with pytest.raises(SpecError, match="boolean"):
        serialize(replace(node, retired=retired))
