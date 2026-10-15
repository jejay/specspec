"""Owner-to-agent messages reuse immutable shots and exact node versions."""

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


def reference(snapshot, node_id, algorithm=0):
    return {"id": node_id, "blob": annotations.blob_ids(snapshot)[node_id][algorithm]}


def payload(*members, color="red", text="Please reconsider these nodes"):
    return {"groups": [{"text": text, "color": color, "nodes": list(members)}]}


def create(root, value, **options):
    return request(root, {"api_version": 6, "op": "annotation-create", **value, **options})[0][
        "shots"
    ][0]


def test_ui_creation_is_readable_by_agent_cli_and_preserves_canonical_and_git_bytes(workspace):
    root, parent = workspace
    snapshot, child = add_node(root, "requirement", [parent], "# Child\n", "child")
    setup_repository(root)
    index, refs = git(root, "ls-files", "--stage"), git(root, "show-ref")
    value = payload(reference(snapshot, parent), text='Please explain <img onerror="bad()"> 🐕')
    value["groups"].append(
        {"text": value["groups"][0]["text"], "color": "blue", "nodes": [reference(snapshot, child)]}
    )
    result = CliRunner().invoke(
        main,
        ["--root", str(root), "api"],
        input=json.dumps({"api_version": 6, "op": "annotation-create", **value}),
    )
    assert result.exit_code == 0, result.output
    shot = json.loads(result.stdout)["result"]["shots"][0]
    assert shot["origin"] == {"kind": "highlights"}
    assert [g["color"] for g in shot["groups"]] == [
        annotations.INKS["red"],
        annotations.INKS["blue"],
    ]
    assert load_snapshot(root).files == snapshot.files
    assert git(root, "ls-files", "--stage") == index
    assert git(root, "show-ref") == refs
    shown = CliRunner().invoke(main, ["--root", str(root), "spotlight", "show", "--json"])
    assert shown.exit_code == 0, shown.output
    record = json.loads(shown.stdout)["result"]["shots"][0]
    assert record["id"] == shot["id"]
    assert record["groups"][0]["text"] == value["groups"][0]["text"]
    assert record["groups"][0]["nodes"][0]["resolution"]["workspace"] == "exact"
    assert (
        "owner highlights"
        in CliRunner().invoke(main, ["--root", str(root), "spotlight", "show"]).stdout
    )


def test_creation_captures_native_unsaved_overlay_and_sha256_reference_without_saving(workspace):
    root, parent = workspace
    saved = load_snapshot(root)
    node = saved.graph.nodes[parent]
    text = saved.files[node.path].decode().replace("# Project", "# Native unsaved")
    loaded, _ = request(root, {"api_version": 6, "op": "read", "documents": {node.path: text}})
    member = {"id": parent, "blob": loaded["node_blobs"][parent][1]}
    shot = create(root, payload(member), documents={node.path: text})
    assert shot["groups"][0]["nodes"][0]["blob"] == member["blob"]
    assert annotations.preview(root, shot["id"], 0, 0)["text"] == text
    assert load_snapshot(root).files == saved.files
    assert (
        annotations.listing(root)["shots"][0]["groups"][0]["nodes"][0]["resolution"]["workspace"]
        == "changed"
    )


def test_reedited_highlights_reuse_retained_bytes_even_when_workspace_is_invalid(workspace):
    root, parent = workspace
    original = annotations.submit(
        root, {"groups": [{"text": "Agent answer", "color": "purple", "nodes": [parent]}]}
    )
    member = original["groups"][0]["nodes"][0]
    file = root / ".specspec-local/annotations" / (original["id"] + ".json")
    record_bytes = file.read_bytes()
    node_bytes = annotations.preview(root, original["id"], 0, 0)["text"]
    (root / member["path"]).write_bytes(b"Owner's unfinished invalid document")
    shot = create(root, payload({"id": parent, "blob": member["blob"]}, color="turquoise"))
    assert file.read_bytes() == record_bytes
    assert shot["id"] != original["id"] and shot["groups"][0]["text"] != "Agent answer"
    assert annotations.preview(root, shot["id"], 0, 0)["text"] == node_bytes
    assert (root / member["path"]).read_bytes() == b"Owner's unfinished invalid document"


def test_historical_creation_combines_target_and_base_ghost_bytes_in_current_schema_gantt(
    gantt_history,
):
    root = gantt_history
    base, target = git_snapshot(root, "stage/02-code"), git_snapshot(root, "stage/03-spec")
    base_only = next(n for n in base.nodes if n.id not in target.graph.nodes)
    target_only = next(n for n in target.nodes if n.id not in base.graph.nodes)
    value = payload(reference(base, base_only.id))
    value["groups"].append(
        {
            "text": value["groups"][0]["text"],
            "color": "yellow",
            "nodes": [reference(target, target_only.id)],
        }
    )
    before = load_snapshot(root).files
    shot = create(root, value, base="stage/02-code", target="stage/03-spec")
    assert (
        annotations.preview(root, shot["id"], 0, 0)["text"].encode() == base.files[base_only.path]
    )
    assert (
        annotations.preview(root, shot["id"], 1, 0)["text"].encode()
        == target.files[target_only.path]
    )
    assert load_snapshot(root).files == before
    assert shot["origin"] == {"kind": "highlights"}
    with pytest.raises(SpecError, match="Historical"):
        create(root, value, target="stage/03-spec", documents={"_specspec/forbidden.md": "text"})


def test_creation_rejects_changed_or_unavailable_highlights_atomically(workspace):
    root, parent = workspace
    snapshot, child = add_node(root, "requirement", [parent], "# Child\n", "child")
    old = reference(snapshot, child)
    update_node(root, child, body="# Changed while composing\n")
    saved = load_snapshot(root).files
    with pytest.raises(SpecError, match="unavailable or changed"):
        create(root, payload(reference(snapshot, parent), old))
    assert annotations.load_shots(root) == []
    assert load_snapshot(root).files == saved
    with pytest.raises(SpecError, match="unavailable or changed"):
        create(root, payload({"id": parent, "blob": "0" * 40}))


@pytest.mark.parametrize(
    "case", ["ids-only", "duplicate", "messages", "path", "blank", "long", "documents"]
)
def test_creation_rejects_invalid_messages_members_and_untrusted_fields(workspace, case):
    root, parent = workspace
    member = reference(load_snapshot(root), parent)
    value, options = payload(member), {}
    if case == "ids-only":
        value = payload(parent)
    elif case == "duplicate":
        value["groups"].append({**value["groups"][0], "color": "blue"})
    elif case == "messages":
        _, child = add_node(root, "requirement", [parent], "# Child\n", "child")
        value["groups"].append(
            {
                "text": "Different message",
                "color": "blue",
                "nodes": [reference(load_snapshot(root), child)],
            }
        )
    elif case == "path":
        member["path"] = "../owner.txt"
    elif case == "blank":
        value["groups"][0]["text"] = " "
    elif case == "long":
        value["groups"][0]["text"] = "x" * 501
    else:
        options["documents"] = []
    with pytest.raises(SpecError):
        create(root, value, **options)
    assert annotations.load_shots(root) == []


def test_corruption_and_store_limits_also_guard_ui_publication(workspace, monkeypatch):
    root, parent = workspace
    snapshot = load_snapshot(root)
    shot = create(root, payload(reference(snapshot, parent)))
    monkeypatch.setattr(annotations, "MAX_SHOTS", 1)
    with pytest.raises(SpecError, match="full"):
        create(root, payload(reference(snapshot, parent)))
    monkeypatch.setattr(annotations, "MAX_SHOTS", 256)
    member = shot["groups"][0]["nodes"][0]
    (root / ".specspec-local/annotations/blobs" / member["blob"]).write_bytes(b"Corrupt")
    with pytest.raises(SpecError, match="does not match"):
        create(root, payload(reference(snapshot, parent)))
    assert annotations.load_shots(root) == [shot]
