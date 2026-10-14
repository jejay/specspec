import json

import pytest
from click.testing import CliRunner

from specspec.cli import main
from specspec.editor import editor_request
from specspec.model import SpecError
from specspec.workspace import add_node, load_snapshot


def request(root, payload, *args):
    value = {"api_version": 6, "op": "plan" if "edit" in payload else "read", **payload}
    if args:
        value["base"] = args[1]
    result = CliRunner().invoke(main, ["--root", str(root), "api"], input=json.dumps(value))
    assert result.exit_code == 0, result.output
    response = json.loads(result.output)
    return {**response["result"], "diagnostics": response["diagnostics"]}


def test_overlay_and_plan_preserve_disk_comments_extensions_and_crlf(workspace):
    root, manifesto = workspace
    snapshot, node_id = add_node(root, "requirement", [manifesto], "# Original\n", "node")
    node = next(node for node in snapshot.nodes if node.id == node_id)
    path = root / node.path
    original = (
        path.read_text(encoding="utf-8")
        .replace("type: requirement", "type: requirement  # keep this comment")
        .replace("---\n# Original", "extensions:\n  org.example:flag: true\n---\n# Original")
    )
    original = original.replace("\n", "\r\n")
    path.write_bytes(original.encode("utf-8"))
    before = {p.name: p.read_bytes() for p in (root / "_specspec").iterdir()}
    overlay = original.replace("# Original", "# Unsaved 🐕")
    result = request(root, {"documents": {node.path: overlay}})
    assert next(n for n in result["snapshot"]["nodes"] if n["id"] == node_id)["body"] == (
        "# Unsaved 🐕\n"
    )
    planned = request(
        root,
        {
            "documents": {node.path: overlay},
            "edit": {"path": node.path, "id": node_id, "body": "# Planned 🐕\r\n"},
        },
    )
    change = planned["changes"][0]
    assert change["before"] == overlay
    assert "# keep this comment" in change["after"]
    assert "org.example:flag: true" in change["after"]
    assert change["after"].startswith("---\r\n")
    assert change["after"].endswith("# Planned 🐕\r\n")
    assert planned["snapshot"]["valid"]
    assert {p.name: p.read_bytes() for p in (root / "_specspec").iterdir()} == before


def test_body_typing_does_not_reorder_or_reformat_untouched_frontmatter(workspace):
    root, manifesto = workspace
    _, parent = add_node(root, "requirement", [manifesto], "# Parent", "parent")
    snapshot, node_id = add_node(root, "implementation", [parent], "# Impl", "impl")
    node = next(n for n in snapshot.nodes if n.id == node_id)
    raw = (root / node.path).read_text(encoding="utf-8")
    raw = raw.replace(f"- {parent}", f"- {parent}  # parent list comment")
    raw = raw.replace(
        "---\n# Impl", "sources:\n- path: z.py  # reference comment\n- path: a.py\n---\n# Impl"
    )
    planned = request(
        root,
        {
            "documents": {node.path: raw},
            "edit": {
                "path": node.path,
                "id": node_id,
                "body": "# Typed",
                "parents": [parent],
                "sources": '[{"path":"a.py"},{"path":"z.py"}]',
            },
        },
    )
    assert planned["changes"][0]["after"] == raw.removesuffix("# Impl") + "# Typed"
    noop = request(
        root,
        {
            "documents": {node.path: raw},
            "edit": {
                "path": node.path,
                "id": node_id,
                "body": "# Impl",
                "parents": [parent],
                "sources": '[{"path":"a.py"},{"path":"z.py"}]',
            },
        },
    )
    assert noop["changes"][0]["after"] == raw


def test_invalid_native_buffers_have_diagnostics_and_can_be_repaired(workspace):
    root, manifesto = workspace
    _, requirement = add_node(root, "requirement", [manifesto], "# Requirement", "requirement")
    snapshot, node_id = add_node(root, "implementation", [requirement], "# Impl\n", "impl")
    node = next(n for n in snapshot.nodes if n.id == node_id)
    invalid = request(root, {"edit": {"path": node.path, "id": node_id, "sources": "[{"}})
    assert not invalid["snapshot"]["valid"]
    assert invalid["diagnostics"]
    assert "[{" in invalid["changes"][0]["after"]
    fixed = request(
        root,
        {
            "documents": {node.path: invalid["changes"][0]["after"]},
            "edit": {"path": node.path, "id": node_id, "sources": "[]"},
        },
    )
    assert fixed["snapshot"]["valid"]
    assert load_snapshot(root).valid
    root_node = next(n for n in snapshot.nodes if n.id == manifesto)
    blank = request(root, {"edit": {"path": root_node.path, "id": manifesto, "body": ""}})
    assert not blank["snapshot"]["valid"]
    fixed_root = request(
        root,
        {
            "documents": {root_node.path: blank["changes"][0]["after"]},
            "edit": {"path": root_node.path, "id": manifesto, "body": "# Repaired\n"},
        },
    )
    assert fixed_root["snapshot"]["valid"]


def test_source_planning_uses_current_text_type_not_the_initial_tab_type(workspace):
    root, manifesto = workspace
    _, parent = add_node(root, "requirement", [manifesto], "# Parent", "parent")
    snapshot, child = add_node(root, "requirement", [parent], "# Child", "child")
    node = next(n for n in snapshot.nodes if n.id == child)
    raw = (root / node.path).read_text(encoding="utf-8")
    (root / "impl.py").write_text("# linked source\n", encoding="utf-8")
    result = request(
        root,
        {
            "documents": {node.path: raw.replace("type: requirement", "type: implementation")},
            "edit": {
                "path": node.path,
                "id": child,
                "body": "# Changed type",
                "sources": '[{"path":"impl.py"}]',
            },
        },
    )
    changed = next(n for n in result["snapshot"]["nodes"] if n["id"] == child)
    assert changed["type"] == "implementation"
    assert changed["sources"] == [{"path": "impl.py"}]
    neutral = request(root, {"edit": {"path": node.path, "id": child, "sources": "[]"}})
    assert "sources:" not in neutral["changes"][0]["after"]
    with pytest.raises(SpecError, match="implementation"):
        editor_request(
            root, {"edit": {"path": node.path, "id": child, "sources": '[{"path":"impl.py"}]'}}
        )


def test_cycle_diagnostics_use_the_full_overlay_and_retirement_edits_are_rejected(workspace):
    root, manifesto = workspace
    snapshot, first = add_node(root, "requirement", [manifesto], "# First", "first")
    snapshot, second = add_node(root, "requirement", [first], "# Second", "second")
    node = next(n for n in snapshot.nodes if n.id == first)
    cycle = request(root, {"edit": {"path": node.path, "id": first, "parents": [second]}})
    assert not cycle["snapshot"]["valid"]
    assert any(d["code"] == "CYCLE" for d in cycle["diagnostics"])
    with pytest.raises(SpecError, match="Unknown editor fields"):
        editor_request(root, {"edit": {"path": node.path, "id": first, "retired": True}})
    assert "retired" not in load_snapshot(root).require_valid().nodes[first].to_dict()


def test_editor_rejects_unsafe_paths_identity_changes_and_deleted_files(workspace):
    root, manifesto = workspace
    node = load_snapshot(root).nodes[0]
    for path in [
        "../README.md",
        "_specspec/../README.md",
        "_specspec/nested/a.md",
        "_specspec\\a.md",
    ]:
        with pytest.raises(SpecError, match="direct"):
            editor_request(root, {"documents": {path: "text"}})
    with pytest.raises(SpecError, match="identity"):
        editor_request(root, {"edit": {"path": node.path, "id": "not-the-node", "body": "# X"}})
    with pytest.raises(SpecError, match="Unknown editor"):
        editor_request(root, {"edit": {"path": node.path, "id": manifesto, "type": "requirement"}})
    (root / node.path).unlink()
    missing = editor_request(root, {"documents": {node.path: "text"}})
    assert not missing["snapshot"]["valid"]  # Deleting the manifesto remains invalid.
    assert not (root / node.path).exists()
    with pytest.raises(SpecError, match="not be recreated"):
        editor_request(root, {"edit": {"path": node.path, "id": manifesto, "body": "text"}})


def test_invalid_raw_text_is_not_repaired_and_runtime_lock_is_not_overlaid(workspace):
    root, _ = workspace
    node = load_snapshot(root).nodes[0]
    before = (root / node.path).read_bytes()
    result = request(root, {"documents": {node.path: "bad raw Markdown"}})
    assert not result["snapshot"]["valid"]
    assert (root / node.path).read_bytes() == before
    (root / ".specspec-local").mkdir(exist_ok=True)
    (root / ".specspec-local/lock").write_text("123")
    with pytest.raises(SpecError, match="progress"):
        editor_request(root, {"documents": {node.path: before.decode()}})


def test_git_comparison_includes_unsaved_changes_without_writing(workspace):
    import subprocess

    root, manifesto = workspace
    for args in [
        ["init"],
        ["add", "."],
        ["-c", "user.name=Test", "-c", "user.email=t@x", "commit", "-m", "base"],
    ]:
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)
    node = load_snapshot(root).nodes[0]
    raw = (root / node.path).read_text(encoding="utf-8")
    result = request(root, {"documents": {node.path: raw + "\nUnsaved."}}, "--base", "HEAD")
    assert result["diff"]["changes"][0]["id"] == manifesto
    assert result["diff"]["changes"][0]["kind"] == "changed"
    assert result["diff"]["target_ref"] == "workspace + open documents"
    assert not subprocess.check_output(["git", "-C", str(root), "diff"])


def test_editor_has_bounded_structured_input_errors(workspace):
    root, _ = workspace
    for raw in ["{", "[]", '{"documents": []}', '{"documents": {"_specspec/a.md": 42}}']:
        result = CliRunner().invoke(main, ["--root", str(root), "api"], input=raw)
        assert result.exit_code == 2
        assert json.loads(result.output)["ok"] is False
    node = load_snapshot(root).nodes[0]
    with pytest.raises(SpecError, match="1 MiB"):
        editor_request(root, {"documents": {node.path: "x" * (1024 * 1024 + 1)}})
