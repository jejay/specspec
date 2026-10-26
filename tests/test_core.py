from __future__ import annotations

import json
import random
from dataclasses import replace

import pytest
from click.testing import CliRunner

from specspec.cli import main
from specspec.format import parse_node, read_document, serialize
from specspec.graph import build_graph
from specspec.model import SpecError
from specspec.workspace import (
    add_node,
    delete_nodes,
    discover_root,
    load_snapshot,
    new_node,
    snapshot_from_files,
    update_node,
)


def test_flat_init(workspace):
    root, manifesto = workspace
    snapshot = load_snapshot(root)
    assert snapshot.valid
    assert snapshot.graph.order == [manifesto]
    assert all(path.is_file() and path.suffix == ".md" for path in (root / ".specspec").iterdir())
    assert not (root / ".specspec" / "specspec.yaml").exists()
    assert snapshot.nodes[0].format_version == 7
    assert "fingerprint" not in snapshot.to_dict()
    assert all("managed_hash" not in node.to_dict() for node in snapshot.nodes)
    assert all(b"managed_hash:" not in raw for raw in snapshot.files.values())


def test_diamond_and_implementation(workspace):
    root, manifesto = workspace
    _, left = add_node(root, "requirement", [manifesto], "Left\n")
    _, right = add_node(root, "requirement", [manifesto], "Right\n")
    snapshot, leaf = add_node(root, "requirement", [left, right], "Both\n")
    snapshot, implementation = add_node(root, "implementation", [leaf], "Realization\n")
    assert snapshot.graph.closure(implementation, ancestors=True) == {manifesto, left, right, leaf}
    assert snapshot.graph.closure(left) == {leaf, implementation}
    assert snapshot.graph.order.index(left) < snapshot.graph.order.index(leaf)


def test_exact_deletion_is_physical_and_retains_dangling_child_references(workspace):
    root, manifesto = workspace
    _, parent = add_node(root, "requirement", [manifesto], "Parent\n")
    snapshot, child = add_node(root, "requirement", [parent], "Child\n")
    assert all(
        "status" not in node.to_dict() and "retired" not in node.to_dict()
        for node in snapshot.nodes
    )
    for ids, match in [
        ([manifesto], "manifesto cannot be deleted"),
        ([], "nonempty"),
        ([child, child], "distinct"),
        (["bWlzc2k="], "Unknown node"),
    ]:
        with pytest.raises(SpecError, match=match):
            delete_nodes(root, ids)
        assert load_snapshot(root).files == snapshot.files
    remaining = delete_nodes(root, [parent], allow_uncommitted=True)
    assert not remaining.valid and set(remaining.graph.nodes) == {manifesto, child}
    assert not (root / snapshot.graph.nodes[parent].path).exists()
    assert (
        remaining.files[snapshot.graph.nodes[child].path]
        == snapshot.files[snapshot.graph.nodes[child].path]
    )


def test_cycles_and_forbidden_parent_types_leave_files_unchanged(workspace):
    root, manifesto = workspace
    _, parent = add_node(root, "requirement", [manifesto], "Parent\n")
    snapshot, child = add_node(root, "requirement", [parent], "Child\n")
    before = dict(snapshot.files)
    with pytest.raises(SpecError, match="Cycle"):
        update_node(root, parent, parents=[child], require_valid=True)
    assert load_snapshot(root).files == before
    with pytest.raises(SpecError, match="requirement parents"):
        add_node(root, "implementation", [manifesto], "No\n", require_valid=True)
    snapshot, implementation = add_node(root, "implementation", [child], "Code\n")
    with pytest.raises(SpecError, match="cannot have children"):
        add_node(root, "requirement", [implementation], "No\n", require_valid=True)


def test_manual_body_edits_are_valid_and_reads_do_not_rewrite_files(workspace):
    root, manifesto = workspace
    snapshot = load_snapshot(root)
    path = root / snapshot.nodes[0].path
    modified = path.read_bytes().replace(b"intentions", b"conclusions")
    path.write_bytes(modified)
    snapshot = load_snapshot(root)
    assert snapshot.valid
    assert path.read_bytes() == modified
    update_node(root, manifesto, body="Attempt\n")
    assert load_snapshot(root).graph.nodes[manifesto].body == "Attempt\n"


def test_unconditional_updates_round_trip_body_comments(workspace):
    root, manifesto = workspace
    snapshot = load_snapshot(root)
    path = root / snapshot.nodes[0].path
    raw = path.read_bytes().replace(b"type: manifesto", b"type: manifesto # keep this comment")
    path.write_bytes(raw)
    assert load_snapshot(root).nodes[0].semantic() == snapshot.nodes[0].semantic()
    changed = update_node(root, manifesto, body="# New\r\n\r\nKeep whitespace.  \r\n")
    assert b"# keep this comment" in path.read_bytes()
    assert path.read_bytes().endswith(b"# New\r\n\r\nKeep whitespace.  \r\n")
    assert load_snapshot(root).files == changed.files
    update_node(root, manifesto, body="Next edit\n")
    assert load_snapshot(root).nodes[0].body == "Next edit\n"


def test_noncanonical_filename_is_diagnosed_without_rewriting_it(workspace):
    root, _ = workspace
    snapshot = load_snapshot(root)
    node = snapshot.nodes[0]
    destination = root / ".specspec" / f"{node.id}extra.md"
    (root / node.path).rename(destination)
    invalid = load_snapshot(root)
    assert not invalid.valid
    assert any("Filename must equal" in d.message for d in invalid.diagnostics)
    assert destination.read_bytes() == snapshot.files[node.path]


@pytest.mark.parametrize("extra", ["nested", "specspec.yaml", "notes.txt"])
def test_forbidden_entries(workspace, extra):
    root, _ = workspace
    path = root / ".specspec" / extra
    if extra == "nested":
        path.mkdir()
    else:
        path.write_text("not a node")
    assert not load_snapshot(root).valid


def test_nearest_workspace_does_not_fall_back(workspace):
    root, _ = workspace
    nested = root / "nested"
    (nested / ".specspec").mkdir(parents=True)
    assert discover_root(nested) == nested
    assert not load_snapshot(nested).valid


@pytest.mark.parametrize(
    "mutation",
    [
        lambda raw: raw.replace(b"type: manifesto", b"type: manifesto\ntype: manifesto"),
        lambda raw: raw.replace(b"parents: []", b"parents: &alias []"),
        lambda raw: raw.replace(b"parents: []", b"parents: !!seq []"),
        lambda raw: raw.replace(b"format_version: 7", b"format_version: true"),
        lambda raw: raw.replace(b"format_version: 7", b"format_version: 999"),
        lambda raw: raw.replace(b"parents: []", b"parents: []\nmanaged_hash: obsolete"),
        lambda raw: raw.replace(b"type: manifesto", b"type: manifesto\nretired: 42"),
        lambda raw: raw.replace(b"type: manifesto", b"type: manifesto\nstatus: accepted"),
        lambda raw: raw.replace(b"parents: []", b"parents: []\nunknown: true"),
        lambda raw: b"\xff" + raw,
    ],
)
def test_malformed_frontmatter_is_diagnostic(workspace, mutation):
    root, _ = workspace
    snapshot = load_snapshot(root)
    path = snapshot.nodes[0].path
    broken = snapshot_from_files(root, {path: mutation(snapshot.files[path])})
    assert not broken.valid
    assert broken.diagnostics


def test_duplicate_ids_and_missing_parents(workspace):
    root, manifesto = workspace
    snapshot = load_snapshot(root)
    node = snapshot.nodes[0]
    duplicates = {**snapshot.files, f".specspec/{node.id}duplicate.md": snapshot.files[node.path]}
    assert not snapshot_from_files(root, duplicates).valid
    with pytest.raises(SpecError, match="Missing parent"):
        add_node(root, "requirement", ["bWlzc2k="], "Missing\n", require_valid=True)
    with pytest.raises(SpecError, match="duplicates"):
        add_node(root, "requirement", [manifesto, manifesto], "Duplicate\n")


def test_sources_paths_and_missing_warnings(workspace):
    root, manifesto = workspace
    _, requirement = add_node(root, "requirement", [manifesto], "Parent\n")
    snapshot, _ = add_node(
        root,
        "implementation",
        [requirement],
        "Code\n",
        sources=[{"path": "src/missing.py", "symbol": "run"}],
    )
    assert snapshot.valid
    assert any(d.code == "SOURCE_MISSING" and d.severity == "warning" for d in snapshot.diagnostics)
    for path in ["../outside.py", "C:/outside.py", "/outside.py", "src\\file.py"]:
        with pytest.raises(SpecError):
            add_node(root, "implementation", [requirement], "Bad\n", sources=[{"path": path}])


def test_symlink_rejection(workspace, tmp_path):
    root, _ = workspace
    target = root / "outside.md"
    target.write_text("outside")
    link = root / ".specspec" / "link.md"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("Symlink creation is unavailable in this environment.")
    assert not load_snapshot(root).valid


def test_cli_end_to_end_and_budget(tmp_path):
    runner = CliRunner()
    prefix = ["--root", str(tmp_path)]
    result = runner.invoke(main, [*prefix, "init", "-m", "# Purpose\n", "--json"])
    assert result.exit_code == 0, result.output
    manifesto = json.loads(result.output)["result"]["changed_ids"][0]
    result = runner.invoke(
        main,
        [*prefix, "add", "--parent", manifesto, "--body", "-", "--json"],
        input="# Child\n",
    )
    assert result.exit_code == 0, result.output
    node_id = json.loads(result.output)["result"]["changed_ids"][0]
    assert runner.invoke(main, [*prefix, "accept", node_id, "--json"]).exit_code == 2
    assert json.loads(result.output)["api_version"] == 7
    assert (
        runner.invoke(
            main,
            [*prefix, "update", node_id, "--body", "-", "--expect", "anything"],
            input="Text\n",
        ).exit_code
        == 2
    )
    args = [*prefix, "query", node_id, "--max-distance", "0", "--with-ancestors", "--json"]
    result = runner.invoke(main, args)
    assert len(json.loads(result.output)["result"]["target"]["nodes"]) == 2
    result = runner.invoke(main, [*args, "--max-bytes", "10"])
    assert result.exit_code == 1
    assert json.loads(result.output)["diagnostics"][0]["code"] == "BUDGET"
    assert runner.invoke(main, [*prefix, "export", "--format", "mermaid"]).exit_code == 2
    assert "Child" in runner.invoke(main, [*prefix, "query"]).output
    assert runner.invoke(main, [*prefix, "update", node_id, "--json"]).exit_code == 2


def test_generated_dags_and_injected_cycle():
    randomizer = random.Random(42)
    for count in [2, 10, 60]:
        nodes = [new_node("manifesto", [], "Root\n")]
        for index in range(1, count):
            parents = randomizer.sample(
                [n.id for n in nodes], k=min(index, randomizer.randint(1, 4))
            )
            existing, errors = build_graph(nodes)
            assert not errors
            parents = [
                p
                for p in parents
                if not any(p in existing.closure(q, ancestors=True) for q in parents if p != q)
            ]
            nodes.append(new_node("requirement", parents, "Body\n"))
        graph, errors = build_graph(nodes)
        assert not errors
        assert graph.order.index(nodes[0].id) == 0
        for node in nodes:
            expected = set(node.parents)
            pending = list(node.parents)
            while pending:
                parent = pending.pop()
                unseen = set(graph.nodes[parent].parents) - expected
                expected.update(unseen)
                pending.extend(unseen)
            assert graph.closure(node.id, ancestors=True) == expected
        nodes[0] = replace(nodes[0], parents=[nodes[-1].id])
        graph, errors = build_graph(nodes)
        assert any(error.code == "CYCLE" for error in errors)
        assert graph.cycle()[0] == graph.cycle()[-1]


def test_long_chain_has_no_recursion_limit():
    nodes = [new_node("manifesto", [], "Root\n")]
    for _ in range(1200):
        nodes.append(new_node("requirement", [nodes[-1].id], "Body\n"))
    graph, errors = build_graph(nodes)
    assert not errors
    assert len(graph.closure(nodes[-1].id, ancestors=True)) == 1200
    nodes[1] = replace(nodes[1], parents=[nodes[-1].id])
    graph, errors = build_graph(nodes)
    assert any(error.code == "CYCLE" for error in errors)
    assert len(graph.cycle()) == 1201


def test_serialization_and_parent_order_semantics(workspace):
    root, manifesto = workspace
    _, one = add_node(root, "requirement", [manifesto], "One\n")
    _, two = add_node(root, "requirement", [manifesto], "Two\n")
    snapshot, child = add_node(root, "requirement", [one, two], "Child\n")
    node = snapshot.graph.nodes[child]
    reordered = replace(node, parents=list(reversed(node.parents)))
    assert node.semantic() == reordered.semantic()
    raw = serialize(node)
    metadata, body = read_document(raw, node.path)
    parsed = parse_node(metadata, body, node.path)
    assert "managed_hash" not in metadata
    assert parsed.semantic() == node.semantic()
