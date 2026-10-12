"""The sole supported ID encoding, portable collisions and current-only schemas."""

import base64
import json
from dataclasses import replace

import pytest
from click.testing import CliRunner

from specspec import workspace as module
from specspec.cli import main
from specspec.editor import editor_request
from specspec.format import parse_node, read_document, serialize
from specspec.model import ID_RE, SpecError
from specspec.workspace import add_node, initialize, load_snapshot, new_node, set_retired


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(b"\x00" * 5, "AAAAAAA="), (b"\xff" * 5, "______8="), (b"fooba", "Zm9vYmE=")],
)
def test_canonical_five_byte_vectors_and_equals_filename(monkeypatch, raw, expected):
    def random_bytes(count):
        assert count == 5
        return raw

    monkeypatch.setattr(module.secrets, "token_bytes", random_bytes)
    node = new_node("manifesto", [], "# Root\n", "Friendly summary")
    assert node.id == expected and len(node.id) == 8
    assert node.path == f"_specspec/{expected}friendly-summary.md"
    assert base64.urlsafe_b64decode(node.id) == raw
    data, body = read_document(serialize(node), node.path)
    assert parse_node(data, body, node.path).id == expected


def test_every_last_octet_uses_zero_pad_bits(monkeypatch):
    for last in range(256):
        monkeypatch.setattr(
            module.secrets, "token_bytes", lambda _, last=last: bytes([0, 0, 0, 0, last])
        )
        node = new_node("manifesto", [], "# Root\n", "root")
        assert ID_RE.fullmatch(node.id)
        assert node.id[-2] in "AEIMQUYcgkosw048"
        assert base64.urlsafe_b64encode(base64.urlsafe_b64decode(node.id)).decode() == node.id


@pytest.mark.parametrize(
    "invalid",
    [
        "AAAAAAB=",
        "AAAAAAA",
        "AAAAAAA==",
        "AAAAAA/=",
        "AAAAAA+=",
        "AAAAAAE=\n",
        "00000000-0000-4000-8000-000000000000",
    ],
)
def test_invalid_ids_and_parent_ids_are_rejected(invalid):
    node = new_node("manifesto", [], "# Root\n", "root")
    with pytest.raises(SpecError, match="canonical padded Base64url"):
        serialize(replace(node, id=invalid, path=f"_specspec/{invalid}root.md"))
    with pytest.raises(SpecError, match="parents"):
        serialize(replace(node, parents=[invalid]))


def test_double_hyphen_is_not_a_second_filename_separator():
    node = new_node("manifesto", [], "# Root\n", "root")
    with pytest.raises(SpecError, match="slug"):
        serialize(replace(node, path=f"_specspec/{node.id}--root.md"))


def test_add_retries_live_retired_and_casefold_collisions_under_lock(workspace, monkeypatch):
    root, manifesto = workspace
    # Keep this deterministic independently of the randomly generated root.
    values = iter([b"fooba", b"other"])
    monkeypatch.setattr(module.secrets, "token_bytes", lambda _: next(values))
    _, live = add_node(root, "requirement", [manifesto], "Live\n", "live")
    _, retired = add_node(root, "requirement", [manifesto], "Withdrawn\n", "retired")
    set_retired(root, [retired], True)
    before = load_snapshot(root)
    alias = live[0].swapcase() + live[1:]
    assert ID_RE.fullmatch(alias), alias
    candidates = iter(
        [
            base64.urlsafe_b64decode(live),
            base64.urlsafe_b64decode(retired),
            base64.urlsafe_b64decode(alias),
            b"fresh",
        ]
    )
    calls = []

    def random_bytes(count):
        assert (root / ".specspec-local/lock").is_file()
        assert count == 5
        calls.append(count)
        return next(candidates)

    monkeypatch.setattr(module.secrets, "token_bytes", random_bytes)
    after, fresh = add_node(root, "requirement", [manifesto], "Fresh\n", "different-summary")
    assert fresh == "ZnJlc2g=" and len(calls) == 4
    assert all(after.files[p] == raw for p, raw in before.files.items())
    assert len(after.nodes) == len(before.nodes) + 1


def test_init_generates_inside_lock(tmp_path, monkeypatch):
    def random_bytes(count):
        assert count == 5 and (tmp_path / ".specspec-local/lock").exists()
        return b"fooba"

    monkeypatch.setattr(module.secrets, "token_bytes", random_bytes)
    assert initialize(tmp_path, "# Root\n").nodes[0].id == "Zm9vYmE="


def test_case_only_duplicate_graph_ids_are_invalid(workspace):
    root, manifesto = workspace
    node = new_node("requirement", [manifesto], "Child\n", "one")
    node.id = "Zm9vYmE="
    node.path = f"_specspec/{node.id}one.md"
    alias_id = node.id[0].swapcase() + node.id[1:]
    alias = replace(node, id=alias_id, path=f"_specspec/{alias_id}two.md")
    files = {**load_snapshot(root).files, node.path: serialize(node), alias.path: serialize(alias)}
    snapshot = module.snapshot_from_files(root, files)
    assert not snapshot.valid
    assert any(d.code == "DUPLICATE" and "case-only" in d.message for d in snapshot.diagnostics)


@pytest.mark.parametrize("retired", ["true", 1, None, [], {}])
def test_withdrawal_flag_is_strictly_boolean(workspace, retired):
    root, _ = workspace
    with pytest.raises(SpecError, match="boolean"):
        serialize(replace(load_snapshot(root).nodes[0], retired=retired))


@pytest.mark.parametrize("version", [1, 2, 3, 5, True])
def test_only_current_schema_is_readable_and_never_converted(workspace, version):
    root, _ = workspace
    before = load_snapshot(root)
    node = before.nodes[0]
    raw = before.files[node.path].replace(
        b"format_version: 4", f"format_version: {str(version).lower()}".encode()
    )
    (root / node.path).write_bytes(raw)
    assert not load_snapshot(root).valid
    assert (root / node.path).read_bytes() == raw
    result = CliRunner().invoke(main, ["--root", str(root), "migrate", "--json"])
    assert result.exit_code == 2


def test_full_id_round_trips_cli_editor_context_and_mermaid(workspace):
    root, manifesto = workspace
    snapshot, child = add_node(root, "requirement", [manifesto], "# Child\n", "child")
    runner = CliRunner()
    for command in ["show", "context", "impact"]:
        result = runner.invoke(main, ["--root", str(root), command, child, "--json"])
        assert result.exit_code == 0, result.output
        assert child in result.output
    result = runner.invoke(main, ["--root", str(root), "export", "--format", "mermaid"])
    assert result.exit_code == 0
    assert f"n_{manifesto.encode().hex()} --> n_{child.encode().hex()}" in result.output
    node = snapshot.graph.nodes[child]
    result = editor_request(
        root, {"edit": {"path": node.path, "id": child, "body": "# Native edit\n"}}
    )
    assert result["snapshot"]["valid"]
    assert next(n for n in result["snapshot"]["nodes"] if n["id"] == child)["parents"] == [
        manifesto
    ]
    assert load_snapshot(root).files == snapshot.files
    retired = set_retired(root, [child], True)
    assert retired.graph.nodes[child].id.endswith("=")
    payload = json.loads(
        runner.invoke(main, ["--root", str(root), "list", "--retired", "--json"]).output
    )
    assert payload["result"]["nodes"][0]["id"] == child


@pytest.mark.parametrize("node_id", ["-_____8=", "--____8="])
def test_ids_beginning_with_hyphens_are_full_cli_arguments(workspace, monkeypatch, node_id):
    root, manifesto = workspace
    raw = base64.urlsafe_b64decode(node_id)
    assert base64.urlsafe_b64encode(raw).decode() == node_id
    monkeypatch.setattr(module.secrets, "token_bytes", lambda _: raw)
    runner = CliRunner()
    prefix = ["--root", str(root)]
    added = runner.invoke(
        main,
        [*prefix, "add", "--parent", manifesto, "--slug", "hyphens", "--body", "-", "--json"],
        input="# Hyphen identity\n",
    )
    assert added.exit_code == 0, added.output
    assert json.loads(added.output)["result"]["changed_ids"] == [node_id]
    for command in ["show", "context", "impact", "retire", "restore"]:
        result = runner.invoke(main, [*prefix, command, node_id, "--json"])
        assert result.exit_code == 0, result.output
    result = runner.invoke(
        main, [*prefix, "update", node_id, "--body", "-", "--json"], input="# Updated\n"
    )
    assert result.exit_code == 0, result.output
    assert load_snapshot(root).graph.nodes[node_id].body == "# Updated\n"


def test_obsolete_fields_are_not_normalized(workspace):
    root, _ = workspace
    node = load_snapshot(root).nodes[0]
    for field in ["managed_hash: ignored", "status: accepted"]:
        raw = serialize(node).replace(b"type: manifesto", f"type: manifesto\n{field}".encode())
        data, body = read_document(raw, node.path)
        with pytest.raises(SpecError, match="Unknown fields"):
            parse_node(data, body, node.path)
