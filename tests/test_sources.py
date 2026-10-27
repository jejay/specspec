"""Blob addressing, evolving regions, explicit capture and exact-index checks."""

import json
import subprocess

import pytest
from click.testing import CliRunner
from test_git import git

from specspec.cli import main
from specspec.git_objects import blob_id
from specspec.source_schema import validate_source
from specspec.sources import SourceReader, map_regions
from specspec.workspace import add_node, load_snapshot, update_node


def invoke(root, *args):
    result = CliRunner().invoke(main, ["--root", str(root), *args, "--json"])
    return result.exit_code, json.loads(result.output)


@pytest.fixture
def project(workspace):
    root, manifesto = workspace
    _, requirement = add_node(root, "requirement", [manifesto], "# Intent\n")
    _, implementation = add_node(root, "implementation", [requirement], "# Code\n")
    (root / "code.py").write_text("before\nalpha\nbeta\nafter\n", encoding="utf-8")
    git(root, "init")
    git(root, "config", "user.name", "Source tests")
    git(root, "config", "user.email", "sources@example.invalid")
    git(root, "config", "core.autocrlf", "false")
    git(root, "add", ".")
    git(root, "commit", "-m", "base")
    return root, implementation


@pytest.mark.parametrize("mode", ["strict", "expanding"])
@pytest.mark.parametrize(
    "new,expected",
    [
        (["prefix", "before", "alpha", "beta", "after"], [[3, 4]]),
        (["before", "boundary", "alpha", "beta", "after"], [[3, 4]]),
        (["before", "alpha", "beta", "boundary", "after"], [[2, 3]]),
    ],
)
def test_offsets_and_outer_insertions_do_not_retarget(mode, new, expected):
    r = map_regions(["before", "alpha", "beta", "after"], new, [[2, 3]], mode)
    assert r == {"outcome": "resolved", "ranges": expected, "changed": False}


def test_internal_additions_are_strict_conflicts_or_expanding_content():
    old, new = ["a", "b", "c", "d"], ["a", "b", "inserted", "c", "d"]
    assert map_regions(old, new, [[2, 3]], "strict") == {
        "outcome": "conflict",
        "ranges": [[2, 2], [4, 4]],
        "changed": True,
    }
    assert map_regions(old, new, [[2, 3]], "expanding") == {
        "outcome": "modified",
        "ranges": [[2, 4]],
        "changed": True,
    }


def test_separate_regions_do_not_absorb_gaps():
    for mode in ["strict", "expanding"]:
        r = map_regions(["a", "gap", "b"], ["a", "gap", "new gap", "b"], [[1, 1], [3, 3]], mode)
        assert r == {"outcome": "resolved", "ranges": [[1, 1], [4, 4]], "changed": False}


def test_replacements_deletion_and_cross_boundary_ambiguity():
    assert map_regions(["a", "b", "c"], ["a", "x", "y", "c"], [[2, 2]], "expanding")["ranges"] == [
        [2, 3]
    ]
    assert (
        map_regions(["a", "b", "c"], ["a", "x", "c"], [[2, 2]], "strict")["outcome"] == "conflict"
    )
    assert map_regions(["a", "b", "c"], ["a", "c"], [[2, 2]], "expanding")["outcome"] == "missing"
    assert map_regions(["a", "b", "c"], ["x"], [[2, 2]], "expanding")["outcome"] == "ambiguous"


def test_unique_moves_and_duplicate_ambiguity():
    assert map_regions(["a", "b", "c", "d"], ["a", "c", "d", "b"], [[2, 2]], "strict")[
        "ranges"
    ] == [[4, 4]]
    r = map_regions(["a", "same", "z"], ["x", "same", "x", "same", "x"], [[2, 2]], "expanding")
    assert r["outcome"] == "ambiguous"


@pytest.mark.parametrize(
    "changes",
    [
        {"blob": "abc"},
        {"mode": "specific"},
        {"mode": []},
        {"ranges": [[True, 2]]},
        {"ranges": [[0, 2]]},
        {"ranges": [[2, 1]]},
        {"ranges": [[2, 3], [3, 4]]},
        {"ranges": []},
        {"extra": 1},
        {"path": "../escape.py"},
    ],
)
def test_schema_rejects_invalid_anchors(changes):
    with pytest.raises(ValueError):
        validate_source(
            {"path": "code.py", "blob": "a" * 40, "mode": "strict", "ranges": [[1, 2]], **changes}
        )


def test_capture_preview_resolve_and_reanchor_preserve_index_and_history(project):
    root, node_id = project
    before = load_snapshot(root).files
    index = git(root, "ls-files", "--stage")
    code, data = invoke(
        root,
        "sources",
        "capture",
        node_id,
        "code.py",
        "--range",
        "2:3",
        "--mode",
        "expanding",
        "--dry-run",
    )
    assert code == 0 and not data["result"]["written"]
    assert load_snapshot(root).files == before and git(root, "ls-files", "--stage") == index
    source = data["result"]["reference"]
    assert source["blob"] == git(root, "rev-parse", "HEAD:code.py").decode().strip()
    assert (
        invoke(
            root, "sources", "capture", node_id, "code.py", "--range", "2:3", "--mode", "expanding"
        )[0]
        == 0
    )
    canonical = load_snapshot(root).files
    (root / "code.py").write_text("new\nbefore\nalpha\ninside\nbeta\nafter\n")
    code, result = invoke(root, "sources", "show", node_id)
    assert code == 0 and result["result"]["sources"][0]["ranges"] == [[3, 5]]
    assert load_snapshot(root).files == canonical
    # Index deliberately remains the old code; explicit staged reanchor uses it.
    assert invoke(root, "sources", "reanchor", node_id, "--source", "1", "--staged")[0] == 0
    assert git(root, "ls-files", "--stage") == index


def test_strict_check_rejects_internal_edit_but_explicit_reanchor_can_replace(project):
    root, node_id = project
    assert (
        invoke(
            root, "sources", "capture", node_id, "code.py", "--range", "2:3", "--mode", "strict"
        )[0]
        == 0
    )
    (root / "code.py").write_text("before\nalpha\nadded\nbeta\nafter\n")
    code, result = invoke(root, "check", node_id, "--sources")
    assert code == 1 and result["diagnostics"][0]["code"] == "SOURCE_LINK"
    git(root, "add", "code.py")
    assert invoke(root, "sources", "reanchor", node_id, "--source", "1", "--staged")[0] == 1
    assert (
        invoke(root, "sources", "reanchor", node_id, "--source", "1", "--staged", "--range", "2:4")[
            0
        ]
        == 0
    )


def test_same_commit_index_blob_capture_and_hook_reads_exact_index(project):
    root, node_id = project
    (root / "new.py").write_text("one\ntwo\nthree\n")
    git(root, "add", "new.py")
    assert (
        invoke(
            root,
            "sources",
            "capture",
            node_id,
            "new.py",
            "--staged",
            "--range",
            "1:3",
            "--mode",
            "strict",
        )[0]
        == 0
    )
    git(root, "add", ".specspec")
    index = git(root, "ls-files", "--stage")
    (root / "new.py").write_text("one\nchanged\nthree\n")
    assert invoke(root, "check", "--staged", "--sources")[0] == 0
    assert git(root, "ls-files", "--stage") == index
    git(root, "add", "new.py")
    assert invoke(root, "check", "--staged", "--sources")[0] == 1


def test_oversized_batch_object_does_not_starve_eligible_blobs(project, monkeypatch):
    root, _ = project
    small = b"ok\n"
    small_id = blob_id(small, "0" * 40)
    # Force the oversized object's address to sort first, exposing admission
    # accounting rather than accidentally accepting the small object first.
    for i in range(1000):
        large = f"large-{i}:".encode().ljust(64, b"x")
        if blob_id(large, "0" * 40) < small_id:
            break
    else:
        pytest.fail("Could not construct deterministic ordered object fixture")
    (root / "large.py").write_bytes(large)
    (root / "small.py").write_bytes(small)
    git(root, "add", "large.py", "small.py")
    git(root, "commit", "-m", "Sized source objects")
    reader = SourceReader(root, ref="HEAD")
    monkeypatch.setattr("specspec.sources.MAX_BYTES", 8)
    monkeypatch.setattr("specspec.sources.MAX_TOTAL_BYTES", 16)
    large_id = blob_id(large, "0" * 40)
    reader.batch({large_id, small_id})
    assert reader.blobs[small_id] == small
    assert "budget" in reader.blobs[large_id].lower()
    assert reader.data("small.py") == small


def test_source_batch_still_enforces_aggregate_eligible_content_budget(project, monkeypatch):
    root, _ = project
    payloads = [b"first-12-byte", b"second-12byt", b"third-12byte"]
    ids = {blob_id(raw, "0" * 40) for raw in payloads}
    for index, raw in enumerate(payloads):
        (root / f"batch-{index}.py").write_bytes(raw)
    git(root, "add", ".")
    git(root, "commit", "-m", "Aggregate source objects")
    reader = SourceReader(root, ref="HEAD")
    monkeypatch.setattr("specspec.sources.MAX_BYTES", 16)
    monkeypatch.setattr("specspec.sources.MAX_TOTAL_BYTES", 24)
    reader.batch(ids)
    assert set(reader.blobs) == ids
    assert 0 < sum(len(raw) for raw in reader.blobs.values() if isinstance(raw, bytes)) <= 24
    assert any(isinstance(value, str) and "budget" in value for value in reader.blobs.values())


def test_unretained_blob_and_wrong_object_type_are_explicit(project):
    root, node_id = project
    oid = (
        subprocess.check_output(
            ["git", "-C", str(root), "hash-object", "-w", "--stdin"], input=b"lost\nversion\n"
        )
        .decode()
        .strip()
    )
    ref = {"path": "code.py", "blob": oid, "mode": "expanding", "ranges": [[1, 2]]}
    reader = SourceReader(root)
    assert reader.resolve(ref, retention=True)["outcome"] == "unavailable"
    ref["blob"] = git(root, "rev-parse", "HEAD").decode().strip()
    assert reader.resolve(ref)["outcome"] == "unavailable"
    update_node(root, node_id, sources=[ref])
    assert load_snapshot(root).valid  # Resolution is not structural approval.


def test_renames_and_branches_use_selected_code_not_worktree(project):
    root, node_id = project
    reader = SourceReader(root, ref="HEAD")
    source = reader.capture("code.py", [[2, 3]], "strict")
    git(root, "mv", "code.py", "renamed.py")
    (root / "renamed.py").write_text("prefix\nbefore\nalpha\nbeta\nafter\n")
    git(root, "add", ".")
    git(root, "commit", "-m", "rename and prefix")
    result = SourceReader(root, ref="HEAD").resolve(source)
    assert result["path"] == "renamed.py" and result["ranges"] == [[3, 4]]
    assert SourceReader(root, ref="HEAD~1").resolve(source)["path"] == "code.py"
    # Copies without a unique original path must not invent file identity.
    git(root, "rm", "renamed.py")
    for p in ["copy-a.py", "copy-b.py"]:
        (root / p).write_text("before\nalpha\nbeta\nafter\n")
    git(root, "add", ".")
    assert SourceReader(root, staged=True).resolve(source)["outcome"] == "ambiguous"


def test_deleting_original_copy_does_not_retarget_another_survivor():
    r = map_regions(
        ["pre", "x", "middle", "x", "tail"], ["pre", "middle", "x", "tail"], [[2, 2]], "strict"
    )
    assert r["outcome"] == "ambiguous"


def test_non_git_file_links_and_symlink_escapes(tmp_path):
    (tmp_path / "local.py").write_text("safe\n")
    reader = SourceReader(tmp_path)
    assert reader.resolve({"path": "local.py"})["outcome"] == "file"
    assert (
        reader.resolve(
            {"path": "local.py", "blob": "a" * 40, "mode": "strict", "ranges": [[1, 1]]}
        )["outcome"]
        == "unavailable"
    )
    outside = tmp_path.parent / (tmp_path.name + "-outside.py")
    outside.write_text("outside\n")
    try:
        (tmp_path / "escape.py").symlink_to(outside)
    except OSError:
        pytest.skip("Symlinks are unavailable.")
    assert reader.resolve({"path": "escape.py"})["outcome"] == "unavailable"


def test_branch_merge_and_missing_shallow_objects(project, tmp_path):
    root, _ = project
    source = SourceReader(root, ref="HEAD").capture("code.py", [[2, 3]], "strict")
    original_branch = git(root, "branch", "--show-current").decode().strip()
    git(root, "checkout", "-b", "topic")
    (root / "code.py").write_text("prefix\nbefore\nalpha\nbeta\nafter\n")
    git(root, "add", ".")
    git(root, "commit", "-m", "topic prefix")
    assert SourceReader(root, ref=original_branch).resolve(source)["ranges"] == [[2, 3]]
    assert SourceReader(root, ref="topic").resolve(source)["ranges"] == [[3, 4]]
    git(root, "checkout", original_branch)
    git(root, "merge", "--no-ff", "topic", "-m", "merge topic")
    assert SourceReader(root, ref="HEAD").resolve(source)["ranges"] == [[3, 4]]
    shallow = tmp_path / "shallow"
    subprocess.run(
        ["git", "clone", "--quiet", "--depth", "1", root.as_uri(), str(shallow)], check=True
    )
    assert SourceReader(shallow, ref="HEAD").resolve(source)["outcome"] == "unavailable"


def test_view_is_literal_and_nonwriting(project):
    root, node_id = project
    source = SourceReader(root, ref="HEAD").capture("code.py", [[2, 3]], "strict")
    before = load_snapshot(root).files
    response = CliRunner().invoke(
        main,
        ["--root", str(root), "api"],
        input=json.dumps({"api_version": 7, "op": "source-view", "reference": source}),
    )
    result = json.loads(response.output)
    assert response.exit_code == 0 and result["result"]["chunks"][0]["selected"] == [2, 3]
    assert load_snapshot(root).files == before


def test_sha256_repository_and_binary_target(workspace, without_git):
    root, manifesto = workspace
    init = subprocess.run(
        ["git", "-C", str(root), "init", "--object-format=sha256"], capture_output=True
    )
    if init.returncode:
        pytest.skip("This Git build lacks SHA-256 repositories.")
    (root / "code.py").write_text("one\ntwo\n")
    git(root, "add", ".")
    source = SourceReader(root, staged=True).capture("code.py", [[1, 2]], "strict")
    assert len(source["blob"]) == 64
    (root / "binary").write_bytes(b"a\0b")
    git(root, "add", "binary")
    with pytest.raises(ValueError, match="UTF-8"):
        SourceReader(root, staged=True).capture("binary", [[1, 1]], "expanding")
