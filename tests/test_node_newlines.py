"""Logical node text works under independent Git policies without configuring them."""

import json

import pytest
from click.testing import CliRunner
from test_git import git, setup_repository

from specspec import cli
from specspec import workspace as workspace_module
from specspec.body_replacements import replace_body
from specspec.editor import editor_request
from specspec.git import git_snapshot, semantic_diff
from specspec.model import MAX_FILE_BYTES, SpecError
from specspec.node_text import document_eol, logical_bytes, logical_text
from specspec.workspace import add_node, load_snapshot, recover


def invoke(root, *args):
    return CliRunner().invoke(cli.main, ["--root", str(root), *args])


@pytest.mark.parametrize("eol", ["\n", "\r\n", "\r"])
@pytest.mark.parametrize("ending", ["", "\n", "\n\n"])
def test_existing_node_writes_and_native_plans_keep_the_document_style(workspace, eol, ending):
    root, parent = workspace
    before, target = add_node(root, "requirement", [parent], "# Old\n\nKeep  \n\tindent" + ending)
    path = root / f".specspec/{target}.md"
    raw = before.files[f".specspec/{target}.md"].replace(b"\n", eol.encode())
    path.write_bytes(raw)
    assert document_eol(raw) == eol
    body = "# New\n\nKeep  \n\tindent" + ending
    planned = editor_request(
        root,
        {
            "documents": {f".specspec/{target}.md": raw.decode()},
            "edit": {"id": target, "path": f".specspec/{target}.md", "body": body},
        },
    )
    assert planned["changes"][0]["before"].encode() == raw
    assert planned["changes"][0]["after"].encode() == raw.replace(b"Old", b"New")
    assert path.read_bytes() == raw
    result = invoke(root, "update", target, "--replace", "Old", "New")
    assert result.exit_code == 0, result.output
    assert path.read_bytes() == raw.replace(b"Old", b"New")
    result = invoke(root, "update", target, "-m", body)
    assert result.exit_code == 0 and result.stdout.startswith("Unchanged: " + target)
    assert path.read_bytes() == raw.replace(b"Old", b"New")


@pytest.mark.parametrize(
    "autocrlf,attribute",
    [
        ("false", None),
        ("true", None),
        ("input", None),
        ("false", "text eol=lf"),
        ("false", "text eol=crlf"),
        ("true", "-text"),
    ],
)
@pytest.mark.parametrize("eol", [b"\n", b"\r\n", b"\r"])
def test_git_policy_does_not_control_logical_diff_or_get_modified(
    workspace, autocrlf, attribute, eol
):
    root, parent = workspace
    setup_repository(root)
    git(root, "config", "core.autocrlf", autocrlf)
    attributes = root / ".gitattributes"
    if attribute:
        attributes.write_text(f"/.specspec/*.md {attribute}\n", encoding="utf8")
    path = root / f".specspec/{parent}.md"
    original = path.read_bytes()
    snapshots = {
        p: p.read_bytes() if p.exists() else None
        for p in [attributes, root / ".git/config", root / ".git/index"]
    }
    path.write_bytes(original.replace(b"\n", eol))
    for args in [("diff",), ("query", parent, "--max-distance", "0")]:
        result = invoke(root, *args)
        assert result.exit_code == 0, result.output
        assert "Line endings/newline:" not in result.stdout
        assert "File patch:" not in result.stdout and "file-only" not in result.stdout
    compared = semantic_diff(git_snapshot(root, "HEAD"), load_snapshot(root))
    assert compared["changes"] == [] and compared["file_changes"] == []
    raw = invoke(root, "query", parent, "--raw", "--json")
    assert json.loads(raw.stdout)["result"]["text"].encode() == path.read_bytes()
    body = load_snapshot(root).graph.nodes[parent].semantic()["body"]
    unchanged = invoke(root, "update", parent, "-m", body)
    assert unchanged.exit_code == 0 and unchanged.stdout.startswith("Unchanged: " + parent)
    assert path.read_bytes() == original.replace(b"\n", eol)
    for p, before in snapshots.items():
        assert (p.read_bytes() if p.exists() else None) == before, p


@pytest.mark.parametrize("body", ["one\r\ntwo", "one\rtwo", "one\r\n\n  \tlast\r\n\r\n"])
def test_new_nodes_use_lf_without_changing_content_or_final_newline(workspace, body):
    root, parent = workspace
    snapshot, target = add_node(root, "requirement", [parent], body)
    raw = snapshot.files[f".specspec/{target}.md"]
    assert b"\r" not in raw and raw.endswith(logical_text(body).encode())
    assert snapshot.graph.nodes[target].body == logical_text(body)


@pytest.mark.parametrize(
    "after", [b"# Body\n\n", b"# Body", b"# Body  \n", b" # Body\n", b"# BODY\n"]
)
def test_blank_lines_eof_spaces_indentation_and_words_stay_meaningful(workspace, after):
    root, parent = workspace
    _, target = add_node(root, "requirement", [parent], "# Body\n")
    setup_repository(root)
    path = root / f".specspec/{target}.md"
    path.write_bytes(path.read_bytes().removesuffix(b"# Body\n") + after)
    result = invoke(root, "diff")
    assert result.exit_code == 0 and "File patch:" in result.stdout
    assert "Line endings/newline:" not in result.stdout
    if not after.endswith(b"\n"):
        assert "No newline at end of file" in result.stdout
    assert semantic_diff(git_snapshot(root, "HEAD"), load_snapshot(root))["changes"]


def test_encoding_adaptation_does_not_create_a_modified_receipt(workspace):
    root, parent = workspace
    snapshot, target = add_node(root, "requirement", [parent], "# Body\n")
    path = root / f".specspec/{target}.md"
    mixed = snapshot.files[f".specspec/{target}.md"].removesuffix(b"# Body\n") + b"# Body\r\n"
    path.write_bytes(mixed)
    result = invoke(root, "update", target, "-m", "# Body\n")
    assert result.exit_code == 0 and result.stdout.startswith("Unchanged: " + target)
    assert path.read_bytes() != mixed and logical_bytes(path.read_bytes()) == logical_bytes(mixed)


def test_journal_and_recovery_guards_still_compare_exact_bytes(workspace, monkeypatch):
    root, parent = workspace
    snapshot, target = add_node(root, "requirement", [parent], "# Old\n")
    path = root / f".specspec/{target}.md"
    raw = snapshot.files[f".specspec/{target}.md"]
    journal = workspace_module.write_journal

    def race(state, value):
        journal(state, value)
        path.write_bytes(raw.replace(b"\n", b"\r\n"))

    monkeypatch.setattr(workspace_module, "write_journal", race)
    result = invoke(root, "update", target, "-m", "# New\n")
    assert result.exit_code == 1 and "CONCURRENT" in result.stderr
    assert not result.stdout
    with pytest.raises(SpecError, match="External edit"):
        recover(root)
    assert path.read_bytes() == raw.replace(b"\n", b"\r\n")
    path.write_bytes(raw)
    recover(root)
    assert path.read_bytes() == raw


def test_actual_target_newline_bytes_control_replacement_result_bounds():
    body = "# old" + "x" * 400000
    new = "y\r\n" * 250000
    result = replace_body(body, [("old", new)], eol="\n")
    assert result == "# " + logical_text(new) + "x" * 400000
    assert len(result.encode()) < MAX_FILE_BYTES
    with pytest.raises(SpecError, match="1 MiB"):
        replace_body("# old", [("old", "x\n" * (MAX_FILE_BYTES // 2))], eol="\r\n")


def test_unavailable_binary_and_absent_documents_are_not_folded_together():
    assert logical_bytes(None) is None
    assert logical_bytes(b"") == b""
    assert logical_bytes(b"\xff\r\n") == b"\xff\r\n"
    assert logical_bytes(b"a\r\nb\r") == b"a\nb\n"
