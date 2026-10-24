"""UI messages capture comparison references and dirty summaries without saving."""

import hashlib
import json

import pytest
from click.testing import CliRunner
from test_git import git, setup_repository

from specspec import annotations
from specspec.application import request
from specspec.cli import main
from specspec.git import git_snapshot
from specspec.model import SpecError
from specspec.workspace import add_node, load_snapshot, update_node


def create(root, nodes, message="Please reconsider these nodes", **options):
    return request(
        root,
        {
            "api_version": 7,
            "op": "annotation-create",
            "message": message,
            "nodes": nodes,
            **options,
        },
    )[0]["shots"][0]


def test_ui_creation_is_readable_by_cli_without_canonical_index_or_ref_changes(workspace):
    root, parent = workspace
    snapshot, child = add_node(root, "requirement", [parent], "# Child\n")
    setup_repository(root)
    index, refs = git(root, "ls-files", "--stage"), git(root, "show-ref")
    message = 'Please explain <img onerror="bad()"> 🐕'
    shot = create(root, [parent, child], message)
    shown = CliRunner().invoke(main, ["--root", str(root), "spotlight", "show", "--json"])
    assert shown.exit_code == 0, shown.output
    record = json.loads(shown.stdout)["result"]["shots"][0]
    assert record["id"] == shot["id"] and record["message"] == message
    assert record["nodes"] == [parent, child]
    assert record["workspace"]["changes"] == {}
    assert all(m["kind"] == "unchanged" for m in record["members"])
    assert load_snapshot(root).files == snapshot.files
    assert git(root, "ls-files", "--stage") == index and git(root, "show-ref") == refs


def test_native_unsaved_overlay_has_only_a_checksum_not_retained_text(workspace):
    root, parent = workspace
    setup_repository(root)
    saved = load_snapshot(root)
    node = saved.graph.nodes[parent]
    text = saved.files[node.path].decode().replace("# Project", "# Native unsaved 🐕")
    loaded, _ = request(
        root, {"api_version": 7, "op": "read", "base": "HEAD", "documents": {node.path: text}}
    )
    checksum = hashlib.sha256(text.encode()).hexdigest()
    assert loaded["workspace_state"]["changes"] == {parent: checksum}
    assert "node_blobs" not in loaded and "base_node_blobs" not in loaded
    shot = create(root, [parent], documents={node.path: text})
    assert shot["workspace"] == loaded["workspace_state"]
    assert "Native unsaved" not in json.dumps(shot)
    assert load_snapshot(root).files == saved.files
    assert "Workspace nodes changed" in " ".join(annotations.listing(root)["shots"][0]["warnings"])
    assert not (root / ".specspec-local/annotations/blobs").exists()


def test_historical_backchannel_selects_target_and_deleted_base_nodes(gantt_history):
    root = gantt_history
    base, target = git_snapshot(root, "stage/02-code"), git_snapshot(root, "stage/03-spec")
    removed = next(n.id for n in base.nodes if n.id not in target.graph.nodes)
    added = next(n.id for n in target.nodes if n.id not in base.graph.nodes)
    before = load_snapshot(root).files
    shot = create(root, [removed, added], base="stage/02-code", target="stage/03-spec")
    assert shot["comparison"] == {"base": base.commit, "target": target.commit}
    assert shot["nodes"] == [removed, added] and "workspace" not in shot
    assert load_snapshot(root).files == before
    with pytest.raises(SpecError, match="Historical"):
        create(root, [added], target="stage/03-spec", documents={"_specspec/forged.md": "text"})
    loaded, _ = request(
        root, {"api_version": 7, "op": "read", "base": base.commit, "target": target.commit}
    )
    assert "node_blobs" not in loaded and "workspace_state" not in loaded


def test_identity_capture_uses_current_version_and_rejects_unknown_ids_atomically(workspace):
    root, parent = workspace
    snapshot, child = add_node(root, "requirement", [parent], "# Child\n")
    update_node(root, child, body="# Current version\n")
    shot = create(root, [parent, child])
    current = load_snapshot(root)
    assert (
        shot["workspace"]["changes"][child]
        == hashlib.sha256(current.files[current.graph.nodes[child].path]).hexdigest()
    )
    assert load_snapshot(root).files != snapshot.files
    with pytest.raises(SpecError, match="either side"):
        create(root, [parent, "Zm9vYmE="])
    assert annotations.load_shots(root) == [shot]


@pytest.mark.parametrize(
    "case", ["duplicate", "object", "blank", "long", "documents", "unknown-field"]
)
def test_creation_rejects_invalid_payloads_without_partial_publication(workspace, case):
    root, parent = workspace
    value = {
        "api_version": 7,
        "op": "annotation-create",
        "message": "Please review",
        "nodes": [parent],
    }
    if case == "duplicate":
        value["nodes"] *= 2
    elif case == "object":
        value["nodes"] = [{"id": parent, "blob": "a" * 40}]
    elif case == "blank":
        value["message"] = " "
    elif case == "long":
        value["message"] = "x" * 501
    elif case == "documents":
        value["documents"] = []
    else:
        value["groups"] = []
    with pytest.raises(SpecError):
        request(root, value)
    assert annotations.load_shots(root) == []


def test_local_list_read_is_independent_of_graph_validity_and_preview_is_removed(workspace):
    root, parent = workspace
    shot = create(root, [parent])
    node = load_snapshot(root).graph.nodes[parent]
    (root / node.path).write_bytes(b"Unfinished invalid document")
    result, _ = request(root, {"api_version": 7, "op": "annotations"})
    assert result == {"shots": [shot]}
    assert annotations.listing(root)["shots"][0]["members"][0]["kind"] == "unavailable"
    with pytest.raises(SpecError, match="Unknown application operation"):
        request(root, {"api_version": 7, "op": "annotation-view", "shot": shot["id"]})
