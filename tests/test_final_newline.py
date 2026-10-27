"""Tool writes terminate node files; manual reads and trailing blank lines stay exact."""

import json

import pytest
from click.testing import CliRunner

from specspec.cli import main
from specspec.editor import editor_request
from specspec.model import MAX_FILE_BYTES, SpecError
from specspec.node_text import stored_text, terminated_document
from specspec.workspace import add_node, load_snapshot, update_node


def invoke(root, *args, input=None):
    return CliRunner().invoke(main, ["--root", str(root), *args], input=input)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("node", "node\n"),
        ("node\n", "node\n"),
        ("node\n\n\n", "node\n\n\n"),
        ("node\n  ", "node\n  \n"),
        ("---\n---\n", "---\n---\n"),
    ],
)
def test_terminator_only_adds_the_single_missing_boundary(text, expected):
    assert terminated_document(text, "\n") == expected


@pytest.mark.parametrize(
    "body",
    ["Here we go", "Here we go\n", "Here we go\n\n\n", "Here we go\n  ", "Here we go\r\n\r\n"],
)
@pytest.mark.parametrize("bulk", [False, True])
def test_init_always_terminates_without_trimming_body_whitespace(tmp_path, body, bulk):
    result = invoke(
        tmp_path,
        "init",
        *(["--body", "-"] if bulk else ["-m", body]),
        input=body.encode() if bulk else None,
    )
    assert result.exit_code == 0, result.output
    node = load_snapshot(tmp_path).nodes[0]
    expected = terminated_document(stored_text(body, "\n"), "\n")
    assert node.body == expected
    assert (tmp_path / node.path).read_bytes().endswith(expected.encode())


@pytest.mark.parametrize("eol", ["\n", "\r\n", "\r"])
@pytest.mark.parametrize("ending", ["", "\n", "\n\n\n", "\n  "])
def test_managed_updates_and_native_plans_append_only_a_missing_terminator(workspace, eol, ending):
    root, parent = workspace
    snapshot, target = add_node(root, "requirement", [parent], "# Old\n")
    node = snapshot.graph.nodes[target]
    path = root / node.path
    header = snapshot.files[node.path].removesuffix(b"# Old\n").replace(b"\n", eol.encode())
    original = header + b"# Old"
    path.write_bytes(original)
    body = "# New\n\nKeep trailing spaces  " + ending
    expected = header + terminated_document(stored_text(body, eol), eol).encode()
    plan = editor_request(
        root, {"documents": {}, "edit": {"id": target, "path": node.path, "body": body}}
    )
    assert plan["changes"][0] == {
        "path": node.path,
        "before": original.decode(),
        "after": expected.decode(),
    }
    assert path.read_bytes() == original
    updated = invoke(root, "update", target, "-m", body)
    assert updated.exit_code == 0, updated.output
    assert path.read_bytes() == expected
    before = path.read_bytes()
    result = invoke(root, "update", target, "--parent", parent)
    assert result.exit_code == 0 and result.stdout.startswith("Unchanged: " + target)
    assert path.read_bytes() == before


def test_replacements_and_composed_adds_receive_file_terminators(workspace):
    root, parent = workspace
    snapshot, target = add_node(root, "requirement", [parent], "# Old\n")
    path = root / snapshot.graph.nodes[target].path
    path.write_bytes(path.read_bytes().removesuffix(b"\n"))
    result = invoke(
        root,
        "update",
        target,
        "--replace",
        "Old",
        "New",
        "add",
        "--parent",
        parent,
        "-m",
        "# Added",
        "--json",
    )
    assert result.exit_code == 0, result.output
    added = json.loads(result.stdout)["result"]["changed_ids"][1]
    saved = load_snapshot(root)
    assert saved.graph.nodes[target].body == "# New\n"
    assert saved.graph.nodes[added].body == "# Added\n"
    assert all(raw.endswith(b"\n") for raw in saved.files.values())


def test_empty_native_repair_body_stays_empty_while_the_document_is_terminated(workspace):
    root, parent = workspace
    snapshot = load_snapshot(root)
    path = snapshot.graph.nodes[parent].path
    plan = editor_request(root, {"documents": {}, "edit": {"id": parent, "path": path, "body": ""}})
    assert plan["changes"][0]["after"].endswith("---\n")
    assert plan["repair_forms"][0]["body"] == ""
    assert load_snapshot(root).files == snapshot.files


def test_unterminated_manual_files_remain_valid_and_raw_reads_do_not_rewrite_them(workspace):
    root, parent = workspace
    node = load_snapshot(root).graph.nodes[parent]
    path = root / node.path
    original = path.read_bytes().removesuffix(b"\n")
    path.write_bytes(original)
    assert load_snapshot(root).valid
    for args in [("query", parent, "--raw", "--json"), ("check",)]:
        result = invoke(root, *args)
        assert result.exit_code == 0, result.output
        assert path.read_bytes() == original
    result = invoke(root, "query", parent, "--raw", "--json")
    assert json.loads(result.stdout)["result"]["text"].encode() == original
    result = invoke(root, "update", parent, "--parents-json", "[]")
    assert result.exit_code == 0 and result.stdout.startswith("Modified: " + parent)
    assert path.read_bytes() == original + b"\n"


def test_implicit_final_newline_counts_against_the_serialized_node_limit(workspace):
    root, parent = workspace
    node = load_snapshot(root).graph.nodes[parent]
    path = root / node.path
    header = path.read_bytes().removesuffix(node.body.encode())
    body = "x" * (MAX_FILE_BYTES - len(header))
    original = header + body.encode()
    path.write_bytes(original)
    assert load_snapshot(root).valid and len(original) == MAX_FILE_BYTES
    with pytest.raises(SpecError, match="1 MiB"):
        update_node(root, parent, body=body)
    with pytest.raises(SpecError, match="1 MiB"):
        editor_request(
            root, {"documents": {}, "edit": {"id": parent, "path": node.path, "body": body}}
        )
    assert path.read_bytes() == original
