import json
import random
import shlex
import subprocess
import sys
from dataclasses import replace

import pytest
from click.testing import CliRunner
from test_git import git, setup_repository

from specspec.cli import main
from specspec.editor import editor_request
from specspec.format import serialize
from specspec.git import git_snapshot
from specspec.graph import build_graph
from specspec.model import SpecError
from specspec.workspace import add_node, load_snapshot, mutate, new_node, update_node


def nodes_for_chain():
    root = new_node("manifesto", [], "# Root\n")
    first = new_node("requirement", [root.id], "# First\n")
    second = new_node("requirement", [first.id], "# Second\n")
    return root, first, second


@pytest.mark.parametrize("kind", ["requirement", "implementation"])
def test_redundant_parent_has_a_real_deterministic_alternative_path(kind):
    root, first, second = nodes_for_chain()
    leaf = new_node(kind, [first.id, second.id], "# Leaf\n")
    expected = f"alternative path: {first.id} -> {second.id} -> {leaf.id}."
    for nodes in (
        [root, first, second, leaf],
        [replace(leaf, parents=list(reversed(leaf.parents))), second, first, root],
    ):
        graph, diagnostics = build_graph(nodes)
        assert len(diagnostics) == 1
        diagnostic = diagnostics[0]
        assert diagnostic.code == "REDUNDANT_PARENT"
        assert diagnostic.path == leaf.path and diagnostic.node_id == leaf.id
        assert expected in diagnostic.message
        assert graph.parents[leaf.id] == {first.id, second.id}, "Validation never normalizes."


def test_manifesto_shortcut_and_multiple_nested_shortcuts_are_reported():
    root, first, second = nodes_for_chain()
    leaf = new_node("requirement", [root.id, first.id, second.id], "# Leaf\n")
    graph, diagnostics = build_graph([root, first, second, leaf])
    assert len(diagnostics) == 2
    for d in diagnostics:
        assert d.code == "REDUNDANT_PARENT"
        text = d.message.split("alternative path: ")[1].split(". ")[0]
        path = text.split(" -> ")
        assert len(path) >= 3 and path[-1] == leaf.id
        assert path[0] in {root.id, first.id}
        assert all(
            child in graph.children[parent] for parent, child in zip(path, path[1:], strict=False)
        )


def test_unequal_depth_incomparable_parents_are_valid():
    root, first, second = nodes_for_chain()
    other = new_node("requirement", [root.id], "# Other\n")
    leaf = new_node("implementation", [second.id, other.id], "# Leaf\n")
    graph, diagnostics = build_graph([root, first, second, other, leaf])
    assert not diagnostics
    assert graph.closure(leaf.id, ancestors=True) == {root.id, first.id, second.id, other.id}


def test_generated_dags_match_an_independent_closure_oracle():
    randomizer = random.Random(91)
    for _ in range(20):
        nodes = [new_node("manifesto", [], "# Root\n")]
        for index in range(1, 65):
            parents = randomizer.sample([n.id for n in nodes], min(index, randomizer.randint(1, 5)))
            nodes.append(new_node("requirement", parents, "# Body\n"))
        graph, diagnostics = build_graph(nodes)
        expected = {
            (p, n.id)
            for n in nodes
            for p in n.parents
            if any(p in graph.closure(q, ancestors=True) for q in n.parents if p != q)
        }
        assert all(d.code == "REDUNDANT_PARENT" for d in diagnostics)
        actual = {
            (d.message.split(" -> ")[0].removeprefix("Direct edge "), d.node_id)
            for d in diagnostics
        }
        assert actual == expected
        reduced, errors = build_graph(
            [replace(n, parents=[p for p in n.parents if (p, n.id) not in expected]) for n in nodes]
        )
        assert not errors
        assert all(
            graph.closure(n.id, ancestors=True) == reduced.closure(n.id, ancestors=True)
            for n in nodes
        )


def test_deep_shortcut_detection_is_iterative():
    root, first, second = nodes_for_chain()
    nodes = [root, first, second]
    for _ in range(1500):
        nodes.append(new_node("requirement", [nodes[-1].id], "# Body\n"))
    leaf = new_node("implementation", [first.id, nodes[-1].id], "# Leaf\n")
    _, diagnostics = build_graph([*nodes, leaf])
    assert len(diagnostics) == 1 and diagnostics[0].code == "REDUNDANT_PARENT"
    assert f"{first.id} -> {second.id}" in diagnostics[0].message
    assert f"{nodes[-1].id} -> {leaf.id}" in diagnostics[0].message


@pytest.mark.parametrize("broken", ["missing", "cycle", "type"])
def test_basic_graph_errors_precede_shortcut_checks(broken):
    root, first, second = nodes_for_chain()
    leaf = new_node("requirement", [root.id, first.id, second.id], "# Leaf\n")
    if broken == "missing":
        first = replace(first, parents=["bWlzc2k="])
    elif broken == "cycle":
        first = replace(first, parents=[second.id])
    else:
        first = replace(first, type="implementation")
    _, diagnostics = build_graph([root, first, second, leaf])
    assert diagnostics and not any(d.code == "REDUNDANT_PARENT" for d in diagnostics)


def test_managed_add_rejects_shortcuts_before_writing(workspace):
    root, manifesto = workspace
    before, parent = add_node(root, "requirement", [manifesto], "# Parent\n")
    with pytest.raises(SpecError, match="alternative path"):
        add_node(root, "requirement", [manifesto, parent], "# Child\n", require_valid=True)
    assert load_snapshot(root).files == before.files
    assert not (root / ".specspec/local/journal.json").exists()


def independent_parents(workspace):
    root, manifesto = workspace
    _, first = add_node(root, "requirement", [manifesto], "# First\n")
    _, second = add_node(root, "requirement", [manifesto], "# Second\n")
    before, leaf = add_node(root, "implementation", [first, second], "# Leaf\n")
    return root, before, first, second, leaf


def test_update_checks_other_nodes_and_coherent_batch_can_resolve_them(workspace):
    root, before, first, second, leaf = independent_parents(workspace)
    with pytest.raises(SpecError) as error:
        update_node(root, second, parents=[first], require_valid=True)
    assert error.value.diagnostics[0].node_id == leaf
    assert error.value.diagnostics[0].code == "REDUNDANT_PARENT"
    assert load_snapshot(root).files == before.files

    # The existing journaled writer can apply a deliberately supplied whole change.
    def operation(snapshot):
        return {
            snapshot.graph.nodes[i].path: serialize(replace(snapshot.graph.nodes[i], parents=ps))
            for i, ps in [(second, [first]), (leaf, [second])]
        }

    after = mutate(root, operation)
    assert after.valid
    assert after.graph.closure(leaf, ancestors=True) == before.graph.closure(leaf, ancestors=True)


def test_native_invalid_shortcuts_remain_diagnosable_and_repairable(workspace):
    root, before, first, second, leaf = independent_parents(workspace)
    node = before.graph.nodes[second]
    planned = editor_request(root, {"edit": {"path": node.path, "id": second, "parents": [first]}})
    assert not planned["snapshot"]["valid"]
    assert any(
        d["code"] == "REDUNDANT_PARENT" and d["node_id"] == leaf for d in planned["diagnostics"]
    )
    repaired = editor_request(
        root,
        {
            "documents": {node.path: planned["changes"][0]["after"]},
            "edit": {"path": before.graph.nodes[leaf].path, "id": leaf, "parents": [second]},
        },
    )
    assert repaired["snapshot"]["valid"]
    assert load_snapshot(root).files == before.files


def test_exact_index_owner_hook_and_revision_checks_share_the_rule(workspace):
    root, before, first, second, leaf = independent_parents(workspace)
    setup_repository(root)
    node = before.graph.nodes[second]
    bad = serialize(replace(node, parents=[first]))
    (root / node.path).write_bytes(bad)
    runner = CliRunner()
    prefix = ["--root", str(root), "check"]
    assert runner.invoke(main, [*prefix, "--staged", "--json"]).exit_code == 0
    git(root, "add", ".specspec")
    (root / node.path).write_bytes(before.files[node.path])
    assert runner.invoke(main, [*prefix, "--json"]).exit_code == 0
    checked = runner.invoke(main, [*prefix, "--staged", "--json"])
    assert checked.exit_code == 1
    assert json.loads(checked.stdout)["diagnostics"][0]["code"] == "REDUNDANT_PARENT"
    assert git_snapshot(root, "HEAD").valid
    # Only this disposable repository receives an explicit owner-configured hook.
    git(root, "config", "core.hooksPath", ".hooks")
    hook = root / ".hooks/pre-commit"
    hook.parent.mkdir()
    python = shlex.quote(sys.executable.replace("\\", "/"))
    hook.write_text(f"#!/bin/sh\nexec {python} -m specspec check --staged\n", encoding="utf-8")
    hook.chmod(hook.stat().st_mode | 0o111)
    result = subprocess.run(
        ["git", "-C", str(root), "commit", "-m", "Must reject shortcut"], capture_output=True
    )
    assert result.returncode != 0
    assert b"REDUNDANT_PARENT" in result.stdout + result.stderr
    git(
        root,
        "-c",
        "core.hooksPath=/dev/null",
        "commit",
        "-m",
        "Deliberate invalid historical fixture",
    )
    historical = runner.invoke(main, [*prefix, "--ref", "HEAD", "--json"])
    assert historical.exit_code == 1 and "REDUNDANT_PARENT" in historical.stdout
    assert load_snapshot(root).valid and not git_snapshot(root, "HEAD").valid
