"""Single-shot local persistence, exact blob references and host read boundaries."""

import json
import subprocess

import pytest
from click.testing import CliRunner
from test_git import git, setup_repository

from specspec import annotations
from specspec.application import request
from specspec.cli import main
from specspec.git import git_snapshot
from specspec.git_objects import blob_id
from specspec.model import SpecError
from specspec.workspace import add_node, load_snapshot, update_node


def payload(*ids, text="Nodes expressing this idea", color="purple"):
    return {"groups": [{"text": text, "color": color, "nodes": list(ids)}]}


def call(root, *args, input=None):
    return CliRunner().invoke(main, ["--root", str(root), "spotlight", *args], input=input)


def test_cli_add_multiple_colors_default_message_and_atomic_rejection(workspace):
    root, parent = workspace
    _, child = add_node(root, "requirement", [parent], "# Child\n", "child")
    result = call(root, "add", parent, "blue", child, "One", "shared", "message", "--json")
    assert result.exit_code == 0, result.output
    groups = json.loads(result.stdout)["result"]["shots"][0]["groups"]
    assert [g["text"] for g in groups] == ["One shared message"] * 2
    assert [g["color"] for g in groups] == [annotations.INKS["purple"], annotations.INKS["blue"]]
    assert [[n["id"] for n in g["nodes"]] for g in groups] == [[parent], [child]]
    before = annotations.load_shots(root)
    for args in [
        ("red", "blue", parent, "Message"),
        ("red", parent, "blue", "Message"),
        ("red", parent),
        ("red", parent, " "),
        ("red", parent, "x" * 501),
        (parent, "blue", parent, "Message"),
        ("orange", parent, "Message"),
        ("red", "bad-id", "Message"),
        ("red", parent, "blue", "Zm9vYmE=", "Message"),
    ]:
        rejected = call(root, "add", *args, "--json")
        assert rejected.exit_code == 1, rejected.output
        assert annotations.load_shots(root) == before


def test_cli_add_dash_leading_ids_all_named_colors_and_committed_capture(workspace):
    root, parent = workspace
    # A canonical ID may look like a short option. Exercise Click, not just parsing.
    path = next((root / "_specspec").glob("*.md"))
    path.write_text(path.read_text().replace(parent, "-_____8="))
    path.rename(path.with_name(path.name.replace(parent, "-_____8=")))
    setup_repository(root)
    for color in annotations.INKS:
        result = call(root, "add", color, "-_____8=", "Literal <img> 🐕", "--ref", "HEAD", "--json")
        assert result.exit_code == 0, result.output
        shot = json.loads(result.stdout)["result"]["shots"][0]
        assert shot["origin"]["kind"] == "commit"
        assert shot["groups"][0]["color"] == annotations.INKS[color]
        assert shot["groups"][0]["nodes"][0]["id"] == "-_____8="


def test_joint_shots_capture_exact_bytes_without_changing_nodes_and_remain_immutable(workspace):
    root, parent = workspace
    snapshot, child = add_node(root, "requirement", [parent], "# Child\n", "child")
    value = payload(parent, child)
    value["groups"].append({"text": "Shared member", "color": "#abcdef", "nodes": [child]})
    first = annotations.submit(root, value)
    file = root / ".specspec-local/annotations" / f"{first['id']}.json"
    original = file.read_bytes()
    assert load_snapshot(root).files == snapshot.files
    assert first["groups"][0]["color"] == annotations.INKS["purple"]
    assert first["groups"][1]["nodes"][0]["id"] == child
    for index, group in enumerate(first["groups"]):
        for number, member in enumerate(group["nodes"]):
            raw = snapshot.files[member["path"]]
            assert blob_id(raw, member["blob"]) == member["blob"]
            assert annotations.preview(root, first["id"], index, number)["text"].encode() == raw
    update_node(root, child, body="# Changed\n")
    second = annotations.submit(root, payload(child, text="Another answer"))
    assert file.read_bytes() == original
    assert [s["id"] for s in annotations.load_shots(root)] == [second["id"], first["id"]]
    assert first["groups"][0]["nodes"][1]["blob"] != second["groups"][0]["nodes"][0]["blob"]
    assert set(main.commands["spotlight"].commands) == {"add", "show", "flush"}
    assert "annotations" not in main.commands


def test_spotlights_public_name_reads_existing_immutable_local_data_unchanged(workspace):
    root, parent = workspace
    shot = annotations.submit(root, payload(parent))
    path = root / ".specspec-local/annotations" / (shot["id"] + ".json")
    original = path.read_bytes()
    result = call(root, "show", "--json")
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["result"]["shots"][0]["id"] == shot["id"]
    text = call(root, "show").stdout
    assert "local spotlight(s)" in text and "annotation" not in text.lower()
    assert path.read_bytes() == original


def test_single_shot_validates_the_whole_payload_before_publication(workspace):
    root, parent = workspace
    value = payload(parent)
    value["groups"].append({"text": "Invalid second group", "color": "red", "nodes": ["Zm9vYmE="]})
    with pytest.raises(SpecError, match="does not exist"):
        annotations.submit(root, value)
    assert annotations.load_shots(root) == []
    value = payload({"id": parent, "blob": "a" * 40})
    with pytest.raises(SpecError, match="differs from the supplied blob"):
        annotations.submit(root, value)
    assert annotations.load_shots(root) == []
    address = annotations.blob_ids(load_snapshot(root))[parent][0]
    guarded = annotations.submit(root, payload({"id": parent, "blob": address}))
    assert guarded["groups"][0]["nodes"][0]["blob"] == address


@pytest.mark.parametrize(
    "value",
    [
        {},
        {"groups": [], "update": True},
        payload("bad"),
        payload("Zm9vYmE=", color="url(javascript:bad)"),
        payload("Zm9vYmE=", text=" "),
        payload("Zm9vYmE=", "Zm9vYmE="),
        payload({"id": "Zm9vYmE=", "blob": "../escape"}),
        payload("Zm9vYmE=", text="x" * 501),
    ],
)
def test_annotation_inputs_are_bounded_explicit_and_literal(workspace, value):
    root, _ = workspace
    with pytest.raises(SpecError):
        annotations.submit(root, value)
    assert not list((root / ".specspec-local").glob("annotations/*.json"))


def test_cli_add_show_flush_json_and_explicit_noninteractive_consent(workspace):
    root, parent = workspace
    result = call(root, "add", "purple", parent, "literal <img> 🐕", "--json")
    assert result.exit_code == 0, result.output
    envelope = json.loads(result.stdout)
    assert envelope["api_version"] == 6 and envelope["ok"]
    shot_id = envelope["result"]["shots"][0]["id"]
    listing = call(root, "show")
    assert listing.exit_code == 0 and "literal <img> 🐕" in listing.stdout
    assert "workspace: exact" in listing.stdout and "HEAD: unavailable" in listing.stdout
    assert call(root, "flush", "--json").exit_code == 1
    assert annotations.load_shots(root)[0]["id"] == shot_id
    assert call(root, "flush", "--yes", "--json").exit_code == 0
    assert annotations.load_shots(root) == []
    assert call(root, "update", shot_id).exit_code == 2
    assert call(root, "submit", "-").exit_code == 2
    assert CliRunner().invoke(main, ["spotlights", "show"]).exit_code == 2


def test_local_git_exclusion_no_index_or_object_writes_and_workspace_retention(workspace):
    root, parent = workspace
    setup_repository(root)
    before_index = git(root, "ls-files", "--stage")
    before_refs = git(root, "show-ref")
    update_node(root, parent, body="# Workspace only\n")
    before_status = git(root, "status", "--porcelain", "--untracked-files=all")
    shot = annotations.submit(root, payload(parent))
    assert git(root, "status", "--porcelain", "--untracked-files=all") == before_status
    assert git(root, "ls-files", "--stage") == before_index
    assert git(root, "show-ref") == before_refs
    member = shot["groups"][0]["nodes"][0]
    exists = subprocess.run(
        ["git", "-C", str(root), "cat-file", "-e", member["blob"]], capture_output=True
    )
    assert exists.returncode != 0, "Workspace capture must not write orphan Git objects."
    (root / load_snapshot(root).nodes[0].path).write_text("invalid", encoding="utf-8")
    # Captured contents remain readable without loading the now-invalid graph or Git.
    preview = annotations.preview(root, shot["id"], 0, 0)
    assert "# Workspace only" in preview["text"]
    assert annotations.listing(root)["shots"][0]["groups"][0]["nodes"][0]["resolution"] == {
        "workspace": "unavailable",
        "HEAD": "changed",
    }
    git(root, "check-ignore", ".specspec-local/annotations/")
    assert not (root / ".gitignore").exists()


def test_tracked_local_state_is_refused(workspace):
    root, parent = workspace
    setup_repository(root)
    tracked = root / ".specspec-local/owner.txt"
    tracked.write_text("Owner data", encoding="utf-8")
    git(root, "add", "-f", ".specspec-local/owner.txt")
    with pytest.raises(SpecError, match="Git-tracked"):
        annotations.submit(root, payload(parent))
    assert annotations.load_shots(root) == []
    assert tracked.read_text() == "Owner data"


def test_annotation_history_uses_independent_current_schema_gantt(gantt_history):
    root = gantt_history
    original = git_snapshot(root, "HEAD")
    node = next(n for n in original.nodes if n.type == "implementation")
    before = git(root, "rev-parse", "HEAD").decode().strip()
    shot = annotations.submit(root, payload(node.id), ref="HEAD")
    member = shot["groups"][0]["nodes"][0]
    assert shot["origin"] == {"kind": "commit", "commit": before}
    assert member["blob"] == blob_id(original.files[node.path], member["blob"])
    # A filename-only rename preserves the exact content reference.
    current = load_snapshot(root).graph.nodes[node.id]
    renamed = root / "_specspec" / f"{node.id}annotation-rename.md"
    (root / current.path).rename(renamed)
    assert (
        annotations.listing(root)["shots"][0]["groups"][0]["nodes"][0]["resolution"]["workspace"]
        == "exact"
    )
    update_node(root, node.id, body=node.body + "\nAdditional implementation evidence.\n")
    git(root, "add", "_specspec")
    git(
        root,
        "-c",
        "core.hooksPath=/dev/null",
        "commit",
        "-m",
        "Exercise annotation version resolution",
    )
    result = annotations.listing(root, [before, "HEAD"])
    resolution = result["shots"][0]["groups"][0]["nodes"][0]["resolution"]
    assert resolution == {"workspace": "changed", "HEAD": "changed", before: "exact"}
    git(root, "checkout", "--detach", before)
    assert annotations.load_shots(root)[0] == shot
    assert (
        annotations.listing(root)["shots"][0]["groups"][0]["nodes"][0]["resolution"]["HEAD"]
        == "exact"
    )
    assert annotations.preview(root, shot["id"], 0, 0)["text"].encode() == original.files[node.path]


def test_application_node_addresses_follow_native_overlays_and_comparison_bytes(workspace):
    root, parent = workspace
    setup_repository(root)
    original = load_snapshot(root)
    node = original.graph.nodes[parent]
    changed = original.files[node.path].decode().replace("# Project", "# Native unsaved")
    loaded, _ = request(
        root, {"api_version": 6, "op": "read", "base": "HEAD", "documents": {node.path: changed}}
    )
    old = annotations.blob_ids(original)[parent]
    assert old == loaded["base_node_blobs"][parent]
    assert not set(old) & set(loaded["node_blobs"][parent])
    assert loaded["node_blobs"][parent][0] == blob_id(changed.encode(), "a" * 40)
    # No canonical fields or node format change; addresses belong to application metadata.
    assert "blob" not in loaded["snapshot"]["nodes"][0]
    historical, _ = request(
        root, {"api_version": 6, "op": "read", "base": "HEAD", "target": "HEAD"}
    )
    assert historical["node_blobs"][parent] == old
    assert historical["base_node_blobs"][parent] == old
    assert load_snapshot(root).files == original.files


def test_flush_checks_the_reviewed_shot_list_and_preserves_other_local_state(workspace):
    root, parent = workspace
    first = annotations.submit(root, payload(parent))
    second = annotations.submit(root, payload(parent, text="Arrived during confirmation"))
    notes = root / ".specspec-local/owner-notes.txt"
    notes.write_text("Keep", encoding="utf-8")
    with pytest.raises(SpecError, match="list changed"):
        annotations.flush(root, expected=[first["id"]])
    assert len(annotations.load_shots(root)) == 2
    result, _ = request(
        root, {"api_version": 6, "op": "annotation-flush", "expected": [first["id"], second["id"]]}
    )
    assert result == {"flushed": 2}
    assert notes.read_text() == "Keep"
    assert load_snapshot(root).valid
    assert not list((root / ".specspec-local/annotations/blobs").iterdir())
    assert annotations.load_shots(root) == []
    with pytest.raises(SpecError):
        annotations.preview(root, first["id"], 0, 0)
    for value in (
        {"api_version": 6, "op": "annotation-flush"},
        {"api_version": 6, "op": "annotation-flush", "expected": None},
    ):
        with pytest.raises(SpecError, match="reviewed"):
            request(root, value)


def test_malformed_and_corrupted_annotation_data_is_protected_until_explicit_flush(workspace):
    root, parent = workspace
    shot = annotations.submit(root, payload(parent))
    file = root / ".specspec-local/annotations" / f"{shot['id']}.json"
    raw = file.read_bytes()
    blob = file.parent / "blobs" / shot["groups"][0]["nodes"][0]["blob"]
    blob.write_bytes(b"corrupted")
    with pytest.raises(SpecError, match="does not match"):
        annotations.preview(root, shot["id"], 0, 0)
    file.write_bytes(b"{broken")
    with pytest.raises(SpecError, match="Protected malformed"):
        annotations.load_shots(root)
    with pytest.raises(SpecError):
        annotations.submit(root, payload(parent))
    assert file.read_bytes() == b"{broken" and load_snapshot(root).valid
    assert raw != file.read_bytes()
    annotations.flush(root)
    assert not file.exists()


def test_annotation_limits_refuse_eviction_or_partial_publication(workspace, monkeypatch):
    root, parent = workspace
    shot = annotations.submit(root, payload(parent))
    monkeypatch.setattr(annotations, "MAX_SHOTS", 1)
    with pytest.raises(SpecError, match="full"):
        annotations.submit(root, payload(parent))
    assert annotations.load_shots(root) == [shot]
    monkeypatch.setattr(annotations, "MAX_SHOTS", 256)
    monkeypatch.setattr(annotations, "MAX_BLOB_BYTES", 1)
    with pytest.raises(SpecError, match="64 MiB"):
        annotations.submit(root, payload(parent))
    assert annotations.load_shots(root) == [shot]


def test_preview_never_accepts_renderer_paths_or_unsafe_indices(workspace):
    root, parent = workspace
    shot = annotations.submit(root, payload(parent))
    for shot_id, group, member in [
        ("../owner", 0, 0),
        (shot["id"], -1, 0),
        (shot["id"], True, 0),
        (shot["id"], 0, 99),
    ]:
        with pytest.raises(SpecError):
            annotations.preview(root, shot_id, group, member)
    result, _ = request(root, {"api_version": 6, "op": "annotations"})
    assert result == {"shots": [shot]}
    assert (
        "text"
        in request(
            root,
            {
                "api_version": 6,
                "op": "annotation-view",
                "shot": shot["id"],
                "group": 0,
                "member": 0,
            },
        )[0]
    )
    with pytest.raises(SpecError):
        request(root, {"api_version": 6, "op": "annotation-view", "path": "../owner"})


def test_sha256_git_object_format_is_retained_without_canonical_changes(workspace):
    root, parent = workspace
    git(root, "init", "--object-format=sha256")
    shot = annotations.submit(root, payload(parent))
    member = shot["groups"][0]["nodes"][0]
    assert len(member["blob"]) == 64
    assert annotations.preview(root, shot["id"], 0, 0)["reference"] == member
    assert member["blob"] in annotations.blob_ids(load_snapshot(root))[parent]


def test_interrupted_unpublished_files_and_over_limit_metadata_remain_flushable(
    workspace, monkeypatch
):
    root, parent = workspace
    shot = annotations.submit(root, payload(parent))
    path = root / ".specspec-local/annotations"
    (path / "blobs" / (".shot-" + "a" * 32 + ".tmp")).write_bytes(b"unpublished blob")
    (path / (".shot-" + "b" * 32 + ".tmp")).write_bytes(b"unpublished metadata")
    # Recognized interruption leftovers do not invalidate complete immutable shots.
    assert annotations.load_shots(root) == [shot]
    second = annotations.submit(root, payload(parent))
    monkeypatch.setattr(annotations, "MAX_SHOTS", 1)
    with pytest.raises(SpecError, match="explicitly flush"):
        annotations.load_shots(root)
    assert annotations.flush(root) == {"flushed": 2}
    assert not list((path / "blobs").iterdir())
    assert not list(path.glob("*.json")) and not list(path.glob("*.tmp"))
    assert second["id"] != shot["id"]


def test_literal_comment_and_line_endings_change_addresses_not_node_identity(workspace):
    root, parent = workspace
    original = load_snapshot(root)
    node = original.graph.nodes[parent]
    shot = annotations.submit(root, payload(parent))
    file = root / node.path
    file.write_bytes(
        original.files[node.path].replace(b"type: manifesto", b"type: manifesto # exact bytes")
    )
    comment = load_snapshot(root)
    assert comment.graph.nodes[parent].semantic() == node.semantic()
    assert annotations.blob_ids(comment)[parent] != annotations.blob_ids(original)[parent]
    file.write_bytes(original.files[node.path].replace(b"\n", b"\r\n"))
    crlf = load_snapshot(root)
    assert crlf.graph.nodes[parent].semantic() == node.semantic()
    assert annotations.blob_ids(crlf)[parent] != annotations.blob_ids(original)[parent]
    assert (
        annotations.listing(root)["shots"][0]["groups"][0]["nodes"][0]["resolution"]["workspace"]
        == "changed"
    )
    assert annotations.preview(root, shot["id"], 0, 0)["text"].encode() == original.files[node.path]


def test_malformed_origin_is_a_protected_diagnostic_and_unsafe_store_entries_are_refused(workspace):
    root, parent = workspace
    shot = annotations.submit(root, payload(parent))
    path = root / ".specspec-local/annotations"
    shot["origin"]["kind"] = []
    file = path / (shot["id"] + ".json")
    file.write_text(json.dumps(shot), encoding="utf-8")
    result = call(root, "show", "--json")
    assert result.exit_code == 1 and "Protected malformed shot" in result.stdout
    annotations.flush(root)
    unsafe = path / "blobs/owner-notes.txt"
    unsafe.write_text("Keep", encoding="utf-8")
    with pytest.raises(SpecError, match="unsafe entry"):
        annotations.flush(root)
    assert unsafe.read_text() == "Keep"
