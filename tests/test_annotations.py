"""Metadata-only comparison spotlights, sparse workspace drift and local lifetime."""

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


def payload(*ids, text="Nodes expressing this idea"):
    return {"message": text, "nodes": list(ids)}


def call(root, *args):
    return CliRunner().invoke(main, ["--root", str(root), "spotlight", *args])


def test_color_free_cli_add_show_statuses_and_atomic_rejection(workspace):
    root, parent = workspace
    setup_repository(root)
    _, child = add_node(root, "requirement", [parent], "# Child\n")
    result = call(root, "add", parent, child, "One", "shared", "message", "--json")
    assert result.exit_code == 0, result.output
    shot = json.loads(result.stdout)["result"]["shots"][0]
    assert shot["message"] == "One shared message"
    assert shot["nodes"] == [parent, child]
    assert shot["comparison"] == {"base": "HEAD", "target": "workspace"}
    assert [m["kind"] for m in shot["members"]] == ["unchanged", "added"]
    text = call(root, "show", shot["id"]).stdout
    assert f"= {parent}" in text and f"A {child}" in text
    assert "HEAD → workspace" in text
    before = annotations.load_shots(root)
    for args in [
        (parent,),
        (parent, " "),
        (parent, "x" * 501),
        (parent, parent, "Message"),
        ("red", parent, "Message"),
        ("bad-id", "Message"),
        (parent, "Zm9vYmE=", "Message"),
    ]:
        rejected = call(root, "add", *args, "--json")
        assert rejected.exit_code == 1, rejected.output
        assert annotations.load_shots(root) == before
    assert call(root, "show", "0" * 32, "--json").exit_code == 1
    assert call(root, "add", parent, "Message", "--ref", "HEAD").exit_code != 0
    assert set(main.commands["spotlight"].commands) == {"add", "show", "flush"}


@pytest.mark.parametrize("node_id", ["-_____8=", "--AAAQA="])
def test_dash_leading_ids_and_color_names_in_message(workspace, node_id):
    root, parent = workspace
    path = next((root / "_specspec").glob("*.md"))
    path.write_text(path.read_text().replace(parent, node_id))
    path.rename(path.with_name(path.name.replace(parent, node_id)))
    setup_repository(root)
    result = call(
        root,
        "add",
        node_id,
        "blue",
        "is",
        "ordinary",
        "text",
        "--base",
        "HEAD",
        "--target",
        "HEAD",
        "--json",
    )
    assert result.exit_code == 0, result.output
    shot = json.loads(result.stdout)["result"]["shots"][0]
    assert shot["message"] == "blue is ordinary text"
    assert shot["nodes"] == [node_id]
    assert "workspace" not in shot
    assert shot["comparison"] == {
        "base": git_snapshot(root, "HEAD").commit,
        "target": git_snapshot(root, "HEAD").commit,
    }


def test_only_dirty_nodes_get_checksums_no_node_copies_or_git_writes(workspace):
    root, parent = workspace
    _, changed = add_node(root, "requirement", [parent], "# Changed\n")
    _, removed = add_node(root, "requirement", [parent], "# Removed\n")
    setup_repository(root)
    index, refs = git(root, "ls-files", "--stage"), git(root, "show-ref")
    update_node(root, changed, body="# Workspace only\n")
    _, added = add_node(root, "requirement", [parent], "# Added\n")
    snapshot = load_snapshot(root)
    (root / snapshot.graph.nodes[removed].path).unlink()
    snapshot = load_snapshot(root)
    status = git(root, "status", "--porcelain", "--untracked-files=all")
    shot = annotations.submit(root, payload(parent, changed, removed, added))
    hashes = shot["workspace"]["changes"]
    assert parent not in hashes
    assert hashes == {
        changed: hashlib.sha256(snapshot.files[snapshot.graph.nodes[changed].path]).hexdigest(),
        added: hashlib.sha256(snapshot.files[snapshot.graph.nodes[added].path]).hexdigest(),
        removed: None,
    }
    assert shot["workspace"]["head"] == git_snapshot(root, "HEAD").commit
    assert not (root / ".specspec-local/annotations/blobs").exists()
    stored = root / ".specspec-local/annotations" / (shot["id"] + ".json")
    assert set(stored.parent.iterdir()) == {stored}
    assert "Workspace only" not in stored.read_text()
    assert "blob" not in stored.read_text() and "color" not in stored.read_text()
    assert load_snapshot(root).files == snapshot.files
    assert git(root, "status", "--porcelain", "--untracked-files=all") == status
    assert git(root, "ls-files", "--stage") == index and git(root, "show-ref") == refs
    git(root, "check-ignore", ".specspec-local/annotations/")
    assert not (root / ".gitignore").exists()


def test_workspace_drift_warns_without_losing_members_and_original_is_immutable(workspace):
    root, parent = workspace
    setup_repository(root)
    _, child = add_node(root, "requirement", [parent], "# Child\n")
    shot = annotations.submit(root, payload(parent, child))
    path = root / ".specspec-local/annotations" / (shot["id"] + ".json")
    raw = path.read_bytes()
    assert annotations.listing(root)["shots"][0]["warnings"] == []
    update_node(root, child, body="# Changed after capture\n")
    shown = annotations.listing(root)["shots"][0]
    assert shown["nodes"] == [parent, child]
    assert child in " ".join(shown["warnings"])
    assert shown["members"][1]["kind"] == "added"
    assert "WARNING:" in call(root, "show").stdout
    (root / load_snapshot(root).graph.nodes[child].path).unlink()
    shown = annotations.listing(root)["shots"][0]
    assert shown["members"][1]["kind"] == "absent"
    assert path.read_bytes() == raw
    git(root, "add", "_specspec")
    git(root, "commit", "--allow-empty", "-m", "Move HEAD")
    assert "HEAD moved" in " ".join(annotations.listing(root)["shots"][0]["warnings"])


def test_drift_tracks_unselected_changes_and_literal_comments_line_endings(workspace):
    root, parent = workspace
    _, child = add_node(root, "requirement", [parent], "# Child\n")
    setup_repository(root)
    shot = annotations.submit(root, payload(parent))
    node = load_snapshot(root).graph.nodes[child]
    path = root / node.path
    raw = path.read_bytes()
    for changed in (
        raw.replace(b"type: requirement", b"type: requirement # literal"),
        raw.replace(b"\n", b"\r\n"),
    ):
        path.write_bytes(changed)
        assert load_snapshot(root).graph.nodes[child].semantic() == node.semantic()
        shown = annotations.listing(root)["shots"][0]
        assert child in " ".join(shown["warnings"])
        assert shown["members"][0]["kind"] == "unchanged"
    path.write_bytes(raw)
    assert annotations.listing(root)["shots"][0]["warnings"] == []
    assert shot["workspace"]["changes"] == {}


def test_gantt_comparison_pins_branches_and_resolves_deleted_added_changed_unchanged(gantt_history):
    root = gantt_history
    base, target = git_snapshot(root, "stage/02-code"), git_snapshot(root, "stage/03-spec")
    common = next(n for n in target.nodes if n.id in base.graph.nodes)
    git(root, "checkout", "--detach", target.commit)
    update_node(root, common.id, body=common.body + "\nComparison regression.\n")
    git(root, "add", "_specspec")
    git(root, "commit", "-m", "Exercise a changed surviving node")
    target = git_snapshot(root, "HEAD")
    diff = annotations.semantic_diff(base, target)
    kinds = {c["id"]: c["kind"] for c in diff["changes"]}
    removed = next(i for i, kind in kinds.items() if kind == "removed")
    added = next(i for i, kind in kinds.items() if kind == "added")
    changed = next(i for i, kind in kinds.items() if kind == "changed")
    unchanged = next(n.id for n in target.nodes if n.id not in kinds)
    git(root, "branch", "spotlight-base", base.commit)
    git(root, "branch", "spotlight-target", target.commit)
    shot = annotations.submit(
        root,
        payload(removed, added, changed, unchanged),
        base="spotlight-base",
        target="spotlight-target",
    )
    assert shot["comparison"] == {"base": base.commit, "target": target.commit}
    assert "workspace" not in shot
    git(root, "branch", "-f", "spotlight-target", "HEAD")
    shown = annotations.listing(root)["shots"][0]
    assert [m["kind"] for m in shown["members"]] == ["removed", "added", "changed", "unchanged"]
    assert shown["warnings"] == []
    text = call(root, "show").stdout
    assert all(
        f"{mark} {i}" in text
        for mark, i in [("D", removed), ("A", added), ("M", changed), ("=", unchanged)]
    )
    assert annotations.load_shots(root) == [shot]


def test_workspace_against_other_branch_uses_head_for_dirty_detection(workspace):
    root, parent = workspace
    setup_repository(root)
    first = git_snapshot(root, "HEAD").commit
    update_node(root, parent, body="# Committed update\n")
    git(root, "add", "_specspec")
    git(root, "commit", "-m", "New intention")
    shot = annotations.submit(root, payload(parent), base=first, target="workspace")
    assert shot["comparison"] == {"base": first, "target": "workspace"}
    assert shot["workspace"]["changes"] == {}
    assert annotations.listing(root)["shots"][0]["members"][0]["kind"] == "changed"


def test_clean_crlf_checkout_is_not_hashed_but_native_overlay_and_dirty_files_are(workspace):
    root, parent = workspace
    setup_repository(root)
    git(root, "config", "core.autocrlf", "true")
    snapshot = load_snapshot(root)
    node = snapshot.graph.nodes[parent]
    raw = snapshot.files[node.path]
    (root / node.path).write_bytes(raw.replace(b"\n", b"\r\n"))
    assert not git(root, "diff", "--name-only", "HEAD")
    shot = annotations.submit(root, payload(parent))
    assert shot["workspace"]["changes"] == {}
    native = raw.decode().replace("# Project", "# Native unsaved")
    created, _ = request(
        root,
        {
            "api_version": 7,
            "op": "annotation-create",
            "message": "Native",
            "nodes": [parent],
            "documents": {node.path: native},
        },
    )
    assert created["shots"][0]["workspace"]["changes"] == {
        parent: hashlib.sha256(native.encode()).hexdigest()
    }
    (root / node.path).write_bytes(raw.replace(b"# Project", b"# Dirty saved"))
    assert parent in annotations.submit(root, payload(parent))["workspace"]["changes"]


def test_heading_changes_keep_spotlight_identity_and_canonical_path(workspace):
    root, parent = workspace
    setup_repository(root)
    node = load_snapshot(root).graph.nodes[parent]
    update_node(root, parent, body="# Different heading\n")
    shot = annotations.submit(root, payload(parent))
    assert parent in shot["workspace"]["changes"]
    member = annotations.listing(root)["shots"][0]["members"][0]
    assert member["kind"] == "changed"
    assert load_snapshot(root).graph.nodes[parent].path == node.path
    assert f"M {parent}" in call(root, "show").stdout


def test_non_git_unborn_and_sha256_workspaces(workspace):
    root, parent = workspace
    shot = annotations.submit(root, payload(parent))
    assert shot["workspace"]["head"] is None
    assert parent in shot["workspace"]["changes"]
    assert annotations.listing(root)["shots"][0]["members"][0]["kind"] == "added"
    git(root, "init", "--object-format=sha256")
    unborn = annotations.submit(root, payload(parent))
    assert unborn["workspace"] == shot["workspace"]
    setup_repository(root)
    committed = annotations.submit(root, payload(parent), base="HEAD", target="HEAD")
    assert len(committed["comparison"]["target"]) == 64
    assert "workspace" not in committed


@pytest.mark.parametrize(
    "value",
    [
        {},
        {"message": "x", "nodes": []},
        payload("bad"),
        payload("Zm9vYmE=", "Zm9vYmE="),
        payload("Zm9vYmE=", text=" "),
        payload("Zm9vYmE=", text="x" * 501),
        {"message": "x", "nodes": [{"id": "Zm9vYmE=", "blob": "a" * 40}]},
    ],
)
def test_inputs_are_bounded_explicit_and_literal(workspace, value):
    root, _ = workspace
    with pytest.raises(SpecError):
        annotations.submit(root, value)
    assert annotations.load_shots(root) == []


def test_context_errors_remain_advisory_on_show_and_do_not_mutate_store(workspace):
    root, parent = workspace
    setup_repository(root)
    shot = annotations.submit(root, payload(parent), target="HEAD")
    file = root / ".specspec-local/annotations" / (shot["id"] + ".json")
    shot["comparison"]["target"] = "0" * 40
    file.write_text(json.dumps(shot), encoding="utf-8")
    shown = annotations.listing(root)["shots"][0]
    assert shown["members"][0]["kind"] == "unavailable"
    assert "Comparison unavailable" in " ".join(shown["warnings"])
    assert call(root, "show", "--json").exit_code == 0
    assert annotations.load_shots(root) == [shot]


def test_tracked_local_state_is_refused(workspace):
    root, parent = workspace
    setup_repository(root)
    tracked = root / ".specspec-local/owner.txt"
    tracked.write_text("Owner data", encoding="utf-8")
    git(root, "add", "-f", ".specspec-local/owner.txt")
    with pytest.raises(SpecError, match="Git-tracked"):
        annotations.submit(root, payload(parent))
    assert annotations.load_shots(root) == []


def test_reviewed_flush_races_consent_and_obsolete_copy_cleanup(workspace):
    root, parent = workspace
    first = annotations.submit(root, payload(parent))
    second = annotations.submit(root, payload(parent))
    path = root / ".specspec-local/annotations"
    (path / "blobs").mkdir()
    (path / "blobs" / ("a" * 40)).write_bytes(b"obsolete node copy")
    (path / (".shot-" + "b" * 32 + ".tmp")).write_bytes(b"unpublished")
    notes = root / ".specspec-local/notes.txt"
    notes.write_text("Keep")
    with pytest.raises(SpecError, match="list changed"):
        annotations.flush(root, expected=[first["id"]])
    assert call(root, "flush", "--json").exit_code == 1
    assert len(annotations.load_shots(root)) == 2
    result, _ = request(
        root, {"api_version": 7, "op": "annotation-flush", "expected": [first["id"], second["id"]]}
    )
    assert result == {"flushed": 2} and annotations.load_shots(root) == []
    assert not list(path.iterdir()) and notes.read_text() == "Keep"
    assert load_snapshot(root).valid
    assert call(root, "flush", "--yes", "--json").exit_code == 0
    with pytest.raises(SpecError, match="reviewed"):
        request(root, {"api_version": 7, "op": "annotation-flush"})


def test_old_or_malformed_local_records_are_protected_and_explicitly_flushable(workspace):
    root, parent = workspace
    shot = annotations.submit(root, payload(parent))
    file = root / ".specspec-local/annotations" / (shot["id"] + ".json")
    for raw in (b'{"annotation_version":1}', b"{broken"):
        file.write_bytes(raw)
        with pytest.raises(SpecError, match="Protected malformed"):
            annotations.load_shots(root)
        with pytest.raises(SpecError):
            annotations.submit(root, payload(parent))
        assert file.read_bytes() == raw
    annotations.flush(root)
    assert not file.exists()


def test_metadata_limits_refuse_eviction_or_partial_publication(workspace, monkeypatch):
    root, parent = workspace
    shot = annotations.submit(root, payload(parent))
    monkeypatch.setattr(annotations, "MAX_SHOTS", 1)
    with pytest.raises(SpecError, match="full"):
        annotations.submit(root, payload(parent))
    assert annotations.load_shots(root) == [shot]
    monkeypatch.setattr(annotations, "MAX_SHOTS", 256)
    monkeypatch.setattr(annotations, "MAX_LIST_BYTES", 1)
    with pytest.raises(SpecError):
        annotations.submit(root, payload(parent))
    assert annotations.flush(root) == {"flushed": 1}


def test_unsafe_obsolete_entries_are_not_deleted(workspace):
    root, parent = workspace
    annotations.submit(root, payload(parent))
    path = root / ".specspec-local/annotations/blobs"
    path.mkdir()
    unsafe = path / "owner-notes.txt"
    unsafe.write_text("Keep")
    with pytest.raises(SpecError, match="unsafe entry"):
        annotations.flush(root)
    assert unsafe.read_text() == "Keep"
