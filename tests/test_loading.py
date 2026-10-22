import copy

import pytest
from test_git import git, setup_repository

from specspec import git_objects
from specspec.editor import editor_request
from specspec.format import read_document
from specspec.git import git_snapshot
from specspec.model import SpecError
from specspec.workspace import add_node, load_snapshot, update_node


def test_git_batches_and_verified_cache_hints_preserve_exact_results(workspace, monkeypatch):
    root, manifesto = workspace
    for i in range(12):
        add_node(root, "requirement", [manifesto], f"# Child {i}\n")
    setup_repository(root)
    calls = []
    request = git_objects.batch_request

    def traced(*args):
        calls.append(args[1])
        return request(*args)

    monkeypatch.setattr(git_objects, "batch_request", traced)
    first = editor_request(root, {"cache": True}, "HEAD")
    assert calls == ["--batch-check", "--batch"]
    calls.clear()
    cached = first["base_cache"]
    second = editor_request(root, {"base_cache": cached}, "HEAD")
    expected = {k: v for k, v in first.items() if k != "base_cache"}
    assert second == expected
    assert calls == ["--batch-check"]
    # Forged data is a hint, never an authoritative historical graph.
    forged = copy.deepcopy(cached)
    path = next(iter(forged["files"]))
    forged["files"][path] += "Forged history\n"
    calls.clear()
    assert editor_request(root, {"base_cache": forged}, "HEAD") == expected
    assert calls == ["--batch-check", "--batch"]
    update_node(root, manifesto, body="# New HEAD\n")
    git(root, "add", "_specspec")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Change HEAD")
    assert editor_request(root, {"base_cache": cached}, "HEAD") == editor_request(root, {}, "HEAD")


def test_batches_chunk_without_changing_staged_or_nested_graphs(workspace, monkeypatch):
    root, manifesto = workspace
    add_node(root, "requirement", [manifesto], "# Child\n")
    setup_repository(root)
    expected = git_snapshot(root, "HEAD").to_dict()
    monkeypatch.setattr(git_objects, "BATCH_COUNT", 1)
    monkeypatch.setattr(git_objects, "BATCH_BYTES", 1)
    assert git_snapshot(root, staged=True).to_dict() == expected
    assert git_snapshot(root, "HEAD").to_dict() == expected


def test_cache_cannot_hide_a_missing_git_blob(workspace):
    root, _ = workspace
    setup_repository(root)
    first = editor_request(root, {"cache": True}, "HEAD")
    node = load_snapshot(root).nodes[0]
    oid = git(root, "rev-parse", f"HEAD:{node.path}").decode().strip()
    object_path = root / ".git/objects" / oid[:2] / oid[2:]
    object_path.chmod(0o600)
    object_path.unlink()
    result = editor_request(root, {"base_cache": first["base_cache"]}, "HEAD")
    assert "unavailable" in result["note"] and "diff" not in result


@pytest.mark.parametrize(
    "bad",
    [
        {},
        {"commit": "not-a-commit", "files": {}},
        {"commit": "a" * 40, "files": {"../bad.md": "bad"}},
        {"commit": "a" * 40, "files": {"_specspec/x.md": 1}},
    ],
)
def test_invalid_cache_inputs_are_bounded_editor_errors(workspace, bad):
    with pytest.raises(SpecError):
        editor_request(workspace[0], {"base_cache": bad}, "HEAD")


def test_frontmatter_memo_isolated_copies_body_bytes_and_current_diagnostics(workspace):
    root, _ = workspace
    path, raw = next(iter(load_snapshot(root).files.items()))
    first, body = read_document(raw, path)
    first["parents"].append("bad")
    second, again = read_document(raw, path)
    assert not second["parents"] and again == body
    original = raw[: len(raw) - len(body.encode())]
    third, edited = read_document(original + b"# New body\r\n", path)
    assert third == second and edited == "# New body\r\n"


@pytest.mark.parametrize("mode", ["missing", "wrong-id", "short", "trailing", "non-blob"])
def test_batch_protocol_rejects_unavailable_or_malformed_objects(monkeypatch, tmp_path, mode):
    raw = b"hello\n"
    oid = git_objects.blob_id(raw, "0" * 40)

    def fake(root, option, ids, limit):
        if option == "--batch-check":
            if mode == "missing":
                return f"{oid} missing\n".encode()
            return f"{oid} {'tree' if mode == 'non-blob' else 'blob'} {len(raw)}\n".encode()
        header = f"{'0' * 40 if mode == 'wrong-id' else oid} blob {len(raw)}\n".encode()
        value = header + raw + b"\n"
        return value[:-2] if mode == "short" else value + b"extra" if mode == "trailing" else value

    monkeypatch.setattr(git_objects, "batch_request", fake)
    if mode in {"missing", "non-blob"}:
        blobs, failures = git_objects.read_blobs(tmp_path, [oid])
        assert not blobs and oid in failures
    else:
        with pytest.raises(SpecError):
            git_objects.read_blobs(tmp_path, [oid])
