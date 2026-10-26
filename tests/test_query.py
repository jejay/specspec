"""Compact annotated reads with independent unfolding and selected-parent oracles."""

import base64
import json
import os
import random
import re
import subprocess
import sys
from collections import Counter
from dataclasses import replace
from pathlib import Path

import pytest
from click.testing import CliRunner
from test_git import git, setup_repository

from specspec.cli import main
from specspec.format import serialize
from specspec.graph import build_graph
from specspec.model import FORMAT_VERSION, SpecNode
from specspec.node_text import logical_text
from specspec.output import safe_text
from specspec.query import (
    body_line,
    compare_snapshots,
    comparison_graph,
    last_occurrence_parents,
    read_query,
    render_query,
    tree_entries,
)
from specspec.wire import expand_comparison
from specspec.workspace import add_node, load_snapshot, snapshot_from_files, update_node


def identity(index):
    return base64.urlsafe_b64encode(index.to_bytes(5, "big")).decode("ascii")


def node(index, parents=(), *, body=None, kind="requirement"):
    return SpecNode(
        identity(index),
        kind,
        [identity(p) for p in parents],
        body if body is not None else f"Body {index}.\n",
        f".specspec/{identity(index)}.md",
        FORMAT_VERSION if kind == "manifesto" else None,
    )


def graph(nodes):
    result, diagnostics = build_graph(nodes)
    assert not diagnostics, diagnostics
    return result


def example():
    return graph(
        [
            node(0, kind="manifesto", body="Root.\n"),
            node(1, [0], body="Left first.\n\nLeft last.\n"),
            node(2, [1], body="Deep.\n"),
            node(3, [0], body="Right.\n"),
            node(4, [2, 3], body="Shared.\n"),
            node(5, [4], kind="implementation", body="Implementation.\n"),
        ]
    )


def snapshot(g=None):
    return snapshot_from_files(
        Path.cwd(), {n.path: serialize(n) for n in g.nodes.values()} if g else {}, allow_empty=True
    )


def comparison(g, old=None):
    current = snapshot(g)
    return compare_snapshots(snapshot(old) if old else current, current)


def call(root, *args):
    return CliRunner().invoke(main, ["--root", str(root), "query", *args])


def entries(text):
    pattern = re.compile(
        r"^((?:│ |  )*)(?:(├─|└─))?"
        r"(?:(?:manifesto|requirement|implementation) ([A-Za-z0-9_-]{7}=)"
        r"(?: @ [A-Za-z0-9_-]{7}=(?:, [A-Za-z0-9_-]{7}=)*)?"
        r"(?: \[(?:(?:added|modified|deleted)(?: source-changed)?"
        r"|source-changed(?: file-only)?|file-only)\])?"
        r"|↪ ([A-Za-z0-9_-]{7}=) ↓)$"
    )
    result, trail = [], []
    for line in text.split("\n"):
        match = pattern.fullmatch(line)
        if match:
            prefix, branch, full, reference = match.groups()
            depth = len(prefix) // 2 + bool(branch)
            parent = trail[depth - 1] if depth else None
            result.append((parent, full or reference, bool(reference)))
            if full:
                trail[depth:] = [full]
    return result


def unfolded_last_paths(g, included=None):
    included = set(g.nodes) if included is None else included
    paths = {}

    def unfold(node_id, path):
        paths[node_id] = path
        for child in sorted(c for c in g.children[node_id] if c in included):
            unfold(child, (*path, node_id))

    for root in sorted(i for i in included if not any(p in included for p in g.parents[i])):
        unfold(root, ())
    return paths


def test_last_occurrence_not_deepest_parent_and_compact_golden_read():
    g = example()
    assert last_occurrence_parents(g)[identity(4)] == identity(3)
    text = render_query(comparison(g))
    assert text == "\n".join(
        [
            "HEAD → workspace",
            f"manifesto {identity(0)}",
            "format_version: 7",
            "",
            "Root. ",
            f"├─requirement {identity(1)} @ {identity(0)}",
            "│ Left first. ¶ Left last. ",
            f"│ └─requirement {identity(2)} @ {identity(1)}",
            "│   Deep. ",
            f"│   └─↪ {identity(4)} ↓",
            f"└─requirement {identity(3)} @ {identity(0)}",
            "  Right. ",
            f"  └─requirement {identity(4)} @ {identity(2)}, {identity(3)}",
            "    Shared. ",
            f"    └─implementation {identity(5)} @ {identity(4)}",
            "      Implementation. ",
        ]
    )
    assert text.count("Shared.") == 1
    assert "@@" not in text and "[=]" not in text and "├─ R" not in text


def test_human_golden_read_preserves_lines_and_uses_the_same_parent_commas():
    text = render_query(comparison(example()), human=True)
    assert text == "\n".join(
        [
            "HEAD → workspace",
            f"manifesto {identity(0)}",
            "format_version: 7",
            "",
            "Root.",
            "",
            f"├─requirement {identity(1)} @ {identity(0)}",
            "│ Left first.",
            "│ ",
            "│ Left last.",
            "│ ",
            f"│ └─requirement {identity(2)} @ {identity(1)}",
            "│   Deep.",
            "│   ",
            f"│   └─↪ {identity(4)} ↓",
            f"└─requirement {identity(3)} @ {identity(0)}",
            "  Right.",
            "  ",
            f"  └─requirement {identity(4)} @ {identity(2)}, {identity(3)}",
            "    Shared.",
            "    ",
            f"    └─implementation {identity(5)} @ {identity(4)}",
            "      Implementation.",
            "      ",
        ]
    )
    assert " ¶ " not in text
    assert entries(text) == entries(render_query(comparison(example())))


@pytest.mark.parametrize("human", [False, True])
def test_compact_nested_bars_and_every_sorted_direct_parent(human):
    g = graph(
        [
            node(0, kind="manifesto"),
            node(1, [0]),
            node(2, [1]),
            node(3, [1]),
            node(51, [0]),
            node(63, [0]),
            node(64, [51, 63, 3]),
            node(65, [2]),
        ]
    )
    text = render_query(comparison(g), human=human)
    assert "│ │ └─requirement" in text and "│  │" not in text
    full = next(line for line in text.split("\n") if f"requirement {identity(64)}" in line)
    assert full.endswith(f" @ {identity(3)}, {identity(63)}, {identity(51)}")
    assert " · " not in full
    assert last_occurrence_parents(g)[identity(64)] in full
    assert f"manifesto {identity(0)}\n" in text


def test_parent_order_and_input_order_do_not_choose_placement():
    g = example()
    reordered = graph(
        [replace(n, parents=list(reversed(n.parents))) for n in reversed(list(g.nodes.values()))]
    )
    assert render_query(comparison(g)) == render_query(comparison(reordered))


@pytest.mark.parametrize("human", [False, True])
def test_generated_dags_and_induced_forests_match_literal_unfolding(human):
    randomizer = random.Random(51)
    for _ in range(80):
        nodes = [node(0, kind="manifesto")]
        for index in range(1, randomizer.randrange(3, 12)):
            previous = graph(nodes)
            candidates = randomizer.sample(range(index), min(index, randomizer.randrange(1, 4)))
            parents = [
                p
                for p in candidates
                if not any(
                    identity(p) in previous.closure(identity(q), ancestors=True)
                    for q in candidates
                    if p != q
                )
            ]
            nodes.append(node(index, parents))
        g = graph(nodes)
        for included in (
            None,
            set(randomizer.sample(list(g.nodes), randomizer.randrange(len(nodes) + 1))),
        ):
            expected = unfolded_last_paths(g, included)
            assert last_occurrence_parents(g, included) == {
                i: path[-1] for i, path in expected.items() if path
            }
            walked = list(tree_entries(g, included))
            full = {i: p for p, (i, ref, _, _) in enumerate(walked) if not ref}
            assert set(full) == set(expected)
            for position, (child, reference, _, _) in enumerate(walked):
                if reference:
                    assert position < full[child]
            for child in expected:
                for parent in g.parents[child]:
                    if parent in expected:
                        assert full[parent] < full[child]
        occurrences = entries(render_query(comparison(g), human=human))
        assert len(occurrences) == len(g.edges()) + 1
        assert sorted([p, c] for p, c, _ in occurrences if p) == g.edges()


def test_exponential_paths_only_scan_child_adjacencies_twice():
    nodes, parents = [node(0, kind="manifesto")], [0]
    for level in range(65):
        children = [2 * level + 1, 2 * level + 2]
        nodes.extend(node(child, parents) for child in children)
        parents = children
    g = graph(nodes)
    reads = Counter()

    class CountedChildren:
        def __init__(self, node_id, values):
            self.node_id, self.values = node_id, values

        def __iter__(self):
            reads[self.node_id] += 1
            return iter(self.values)

    g.children = {i: CountedChildren(i, values) for i, values in g.children.items()}
    assert len(list(tree_entries(g))) == 1 + sum(len(n.parents) for n in nodes)
    assert reads == Counter({i: 2 for i in g.nodes})


def test_deep_chain_is_iterative():
    g = graph([node(0, kind="manifesto"), *[node(i, [i - 1]) for i in range(1, 1250)]])
    assert len(last_occurrence_parents(g)) == 1249
    assert len(list(tree_entries(g))) == 1250


def test_union_cycles_and_reparenting_keep_deleted_nodes_in_the_overlay_once():
    base = graph(
        [node(0, kind="manifesto"), node(1, [0]), node(2, [1]), node(3, [1, 4]), node(4, [0])]
    )
    target = graph([node(0, kind="manifesto"), node(2, [0]), node(1, [2])])
    result = comparison(target, base)
    text = render_query(result)
    assert "Deleted (base):" not in text
    occurrences = entries(text)
    assert Counter(i for _, i, ref in occurrences if not ref) == Counter(set(base.nodes))
    expected = [[p, n.id] for n in target.nodes.values() for p in n.parents]
    expected += [
        [p, n.id] for n in base.nodes.values() if n.id not in target.nodes for p in n.parents
    ]
    assert sorted([p, c] for p, c, _ in occurrences if p) == sorted(expected)
    assert any(p == identity(0) and c == identity(4) for p, c, _ in occurrences)
    assert any(p == identity(1) and c == identity(3) and ref for p, c, ref in occurrences)
    assert any(p == identity(4) and c == identity(3) and not ref for p, c, ref in occurrences)
    assert result.result["added_edges"] == [[identity(0), identity(2)], [identity(2), identity(1)]]
    assert [identity(1), identity(2)] in result.result["removed_edges"]
    assert f"requirement {identity(3)} @ {identity(1)}, {identity(4)} [deleted]" in text
    assert "@@" not in text and "frontmatter" not in text


def selected_unfolding(base, target):
    # Independent oracle: choose parent lists, then repeatedly scan them for
    # children. Do not reuse the production adjacency construction or walk.
    parents = {
        i: (target.nodes.get(i) or base.nodes[i]).parents
        for i in base.nodes.keys() | target.nodes.keys()
    }
    paths = {}

    def unfold(node_id, path):
        paths[node_id] = path
        for child in sorted(i for i, incoming in parents.items() if node_id in incoming):
            unfold(child, (*path, node_id))

    for root in sorted(i for i, incoming in parents.items() if not incoming):
        unfold(root, ())
    return parents, paths


@pytest.mark.parametrize("human", [False, True])
def test_generated_comparisons_match_independent_selected_parent_and_unfolding_oracles(human):
    randomizer = random.Random(175)

    def generate(order):
        nodes = [node(0, kind="manifesto")]
        for index in order:
            previous = graph(nodes)
            candidates = randomizer.sample(nodes, min(len(nodes), randomizer.randrange(1, 4)))
            parents = [
                n
                for n in candidates
                if not any(
                    n.id in previous.closure(other.id, ancestors=True)
                    for other in candidates
                    if other.id != n.id
                )
            ]
            n = node(index)
            n.parents = [p.id for p in parents]
            nodes.append(n)
        return graph(nodes)

    for _ in range(60):
        base = generate(randomizer.sample(range(1, 9), 8))
        target = generate(randomizer.sample(range(1, 11), randomizer.randrange(3, 9)))
        expected, paths = selected_unfolding(base, target)
        comparison_value = comparison(target, base)
        projection = comparison_graph(comparison_value.base, comparison_value.target)
        edges = sorted([p, c] for c, parents in expected.items() for p in parents)
        assert projection.edges() == edges and not projection.cycle()
        positions = {i: n for n, i in enumerate(projection.order)}
        assert all(positions[p] < positions[c] for p, c in edges)
        assert last_occurrence_parents(projection) == {i: p[-1] for i, p in paths.items() if p}
        occurrences = entries(render_query(comparison_value, human=human))
        assert sorted([p, c] for p, c, _ in occurrences if p) == edges
        assert Counter(i for _, i, ref in occurrences if not ref) == Counter(expected.keys())
        full = {i: n for n, (_, i, ref) in enumerate(occurrences) if not ref}
        assert all(n < full[i] for n, (_, i, ref) in enumerate(occurrences) if ref)


def test_overlay_keeps_new_display_shortcuts_without_revalidating_or_mutating_canonical_graphs():
    base = graph([node(0, kind="manifesto"), node(1, [0]), node(2, [0]), node(3, [1, 2])])
    target = graph([node(0, kind="manifesto"), node(1, [0]), node(2, [1])])
    result = comparison(target, base)
    projection = comparison_graph(result.base, result.target)
    _, diagnostics = build_graph(list(projection.nodes.values()))
    assert any(d.code == "REDUNDANT_PARENT" for d in diagnostics)
    assert [identity(1), identity(3)] in projection.edges()
    assert [identity(2), identity(3)] in projection.edges()
    assert f"@ {identity(1)}, {identity(2)} [deleted]" in render_query(result)
    assert (
        result.base.graph.edges() == base.edges() and result.target.graph.edges() == target.edges()
    )


def test_deleted_children_remain_visible_under_a_parent_whose_current_type_is_implementation():
    base = graph([node(0, kind="manifesto"), node(1, [0]), node(2, [1]), node(3, [0])])
    target = graph([node(0, kind="manifesto"), node(1, [3], kind="implementation"), node(3, [0])])
    result = comparison(target, base)
    text = render_query(result)
    assert (identity(1), identity(2), False) in entries(text)
    assert f"implementation {identity(1)} @ {identity(3)} [modified]" in text
    assert f"requirement {identity(2)} @ {identity(1)} [deleted]" in text


def test_deleted_node_does_not_reintroduce_its_old_parent_link_to_a_surviving_child():
    base = graph([node(0, kind="manifesto"), node(1, [0]), node(2, [1]), node(3, [2])])
    target = graph([node(0, kind="manifesto"), node(3, [0]), node(1, [3])])
    result = comparison(target, base)
    drawn = [[p, c] for p, c, _ in entries(render_query(result)) if p]
    assert [identity(1), identity(2)] in drawn
    assert [identity(2), identity(3)] not in drawn
    assert [identity(2), identity(3)] in result.result["removed_edges"]


def test_comparison_with_distinct_manifestos_keeps_both_roots_without_a_deleted_section():
    base = graph([node(0, kind="manifesto"), node(1, [0])])
    target = graph([node(2, kind="manifesto"), node(3, [2])])
    text = render_query(comparison(target, base))
    assert "Deleted (base):" not in text
    assert entries(text) == [
        (None, identity(0), False),
        (identity(0), identity(1), False),
        (None, identity(2), False),
        (identity(2), identity(3), False),
    ]
    assert f"manifesto {identity(0)} [deleted]" in text
    assert f"manifesto {identity(2)} [added]" in text
    assert "\nBody 0. \n" in text and "\nBody 2. \n" in text


def test_deep_overlay_remains_iterative():
    # Sequential Base64 encodings have case-only aliases at this size. Use
    # distinct canonical digit-heavy IDs so this exercises validated snapshots.
    nodes = [
        replace(
            node(i, kind="requirement" if i else "manifesto"),
            id=f"A{i:05d}A=",
            parents=[f"A{i - 1:05d}A="] if i else [],
            path=f".specspec/A{i:05d}A=.md",
        )
        for i in range(1250)
    ]
    base = graph(nodes)
    target = graph(nodes[:600])
    result = comparison(target, base)
    projection = comparison_graph(result.base, result.target)
    assert len(list(tree_entries(projection))) == 1250
    assert last_occurrence_parents(projection)["A01249A="] == "A01248A="


@pytest.mark.parametrize("human", [False, True])
@pytest.mark.parametrize(
    "body,expected",
    [
        ("No heading", "No heading"),
        ("soft\nline\nbreaks", "soft line breaks"),
        ("first\n\nlast\n", "first ¶ last "),
        ("first\n\n\n\nlast", "first ¶ last"),
        ("one\r\ntwo\r\n\r\nthree", "one two ¶ three"),
        ("# Head\r\n\r\n  nested\ttext  \r\n", "# Head ¶   nested\ttext   "),
        ("literal \\u202e\n", "literal \\u202e "),
        ("a\rb\u2028c\u2029\n", "a b\u2028c\u2029 "),
        ("\nleading\n\n\n", " leading ¶ "),
        ("first\n \nlast", "first   last"),
        ("- one\n- two\n", "- one - two "),
        ("```py\na()\n\nb()\n```\n", "```py a() ¶ b() ``` "),
    ],
)
def test_body_presentation_flattens_only_the_default_and_preserves_human_lines(
    body, expected, human
):
    g = graph([node(0, kind="manifesto", body=body)])
    query = comparison(g)
    original_body = query.target.graph.nodes[identity(0)].body
    text = render_query(query, human=human)
    assert body_line(body) == expected and "\n" not in expected
    body_rows = logical_text(body).split("\n") if human else [expected]
    assert text.split("\n") == [
        "HEAD → workspace",
        f"manifesto {identity(0)}",
        "format_version: 7",
        "",
        *body_rows,
    ]
    assert query.target.graph.nodes[identity(0)].body == original_body
    assert "body @@" not in text and "No newline at end of file" not in text


def test_full_word_hints_need_no_legend_and_keep_independent_source_and_literal_cues():
    g = example()
    query = comparison(g)
    query.result["source_contract_affected"] = [identity(0)]
    query.result["file_changes"] = [{"path": g.nodes[identity(0)].path, "kind": "changed"}]
    text = render_query(query)
    assert text.split("\n")[:2] == [
        "HEAD → workspace",
        f"manifesto {identity(0)} [source-changed file-only]",
    ]
    assert "=parents" not in text and "=manifesto" not in text and "=below" not in text
    assert body_line("") == ""


@pytest.mark.parametrize("human", [False, True])
def test_modified_node_shows_only_current_body_with_a_hint(human):
    old = graph([node(0, kind="manifesto", body="Old wording\n")])
    new = graph([node(0, kind="manifesto", body="# Current wording\n\n  nested\n")])
    text = render_query(comparison(new, old), human=human)
    assert f"manifesto {identity(0)} [modified]" in text
    assert "Old wording" not in text
    expected = "\n# Current wording\n\n  nested\n" if human else "\n# Current wording ¶   nested "
    assert expected in text
    assert "[modified file-only]" not in text and "@@" not in text


@pytest.mark.parametrize("human", [False, True])
def test_deleted_node_keeps_base_body_but_survivors_keep_target_text(human):
    old = graph(
        [
            node(0, kind="manifesto", body="Old root\n"),
            node(1, [0], body="Deleted first\n\nDeleted last\nwrapped\n"),
        ]
    )
    new = graph([node(0, kind="manifesto", body="Current root\n")])
    text = render_query(comparison(new, old), human=human)
    assert "Old root" not in text and "Current root" in text
    assert f"requirement {identity(1)} @ {identity(0)} [deleted]" in text
    expected = (
        "  Deleted first\n  \n  Deleted last\n  wrapped\n  "
        if human
        else "  Deleted first ¶ Deleted last wrapped "
    )
    assert text.endswith(expected)


def test_current_extensions_are_complete_without_old_metadata_or_raw_frontmatter():
    old_node = node(0, kind="manifesto", body="Binding without a heading\n")
    old_node.extensions = {"org.example:note": "Old extension"}
    new_node = replace(old_node, extensions={"org.example:note": [None, True, {"text": "全体"}]})
    text = render_query(comparison(graph([new_node]), graph([old_node])))
    assert 'extensions: {"org.example:note":[null,true,{"text":"全体"}]}' in text
    assert "\nBinding without a heading " in text
    assert "Old extension" not in text and "---" not in text


def test_query_does_not_compute_patch_payloads(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("query must leave patch construction to diff")

    monkeypatch.setattr("specspec.output.file_patches", forbidden)
    g = example()
    changed = graph([replace(n, body=n.body + "Extra\n") for n in g.nodes.values()])
    result = comparison(changed, g)
    assert result.result["file_changes"]
    assert all(set(row) == {"path", "kind"} for row in result.result["file_changes"])
    assert "@@" not in render_query(result)


def test_comment_only_eol_changes_have_literal_not_fake_semantic_status(workspace):
    root, parent = workspace
    setup_repository(root)
    n = load_snapshot(root).graph.nodes[parent]
    path = root / n.path
    path.write_bytes(path.read_bytes().replace(b"type: manifesto", b"type: manifesto # comment"))
    result = read_query(root)
    assert result.result["changes"] == []
    text = render_query(result)
    assert "[file-only]" in text and "frontmatter" not in text and "# comment" not in text
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    result = read_query(root)
    assert result.result["changes"] == []
    assert "[file-only]" in render_query(result)


def test_cr_only_encoding_change_is_quiet_without_rewriting_the_file(workspace):
    root, parent = workspace
    setup_repository(root)
    n = load_snapshot(root).graph.nodes[parent]
    path = root / n.path
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r"))
    result = read_query(root)
    text = render_query(result)
    assert "@@" not in text and "[file-only]" not in text
    assert "[modified]" not in text and "\\u000d" not in safe_text(text)
    assert b"\r" in path.read_bytes() and b"\n" not in path.read_bytes()


@pytest.mark.parametrize("human", [False, True])
def test_cli_comparison_json_round_trip_and_read_only_git_state(workspace, human):
    root, parent = workspace
    setup_repository(root)
    _, child = add_node(root, "requirement", [parent], "No heading\n\nComplete last line.\n")
    before = load_snapshot(root)
    index, refs = git(root, "ls-files", "--stage"), git(root, "show-ref")
    objects = git(root, "count-objects", "-v")
    args = ["--human"] if human else []
    result = call(root, *args)
    assert result.exit_code == 0 and f"{child} @ {parent} [added]" in result.stdout
    expected_body = (
        "\n  No heading\n  \n  Complete last line.\n"
        if human
        else "\n  No heading ¶ Complete last line. \n"
    )
    assert expected_body in result.stdout
    structured = call(root, *args, "--json")
    assert structured.exit_code == 0, structured.output
    value = json.loads(structured.stdout)
    assert value["api_version"] == 7 and value["ok"]
    assert value == json.loads(call(root, "--json").stdout)
    expanded = expand_comparison(value["result"])
    assert expanded["base"]["nodes"] == read_query(root).base.to_dict()["nodes"]
    assert expanded["target"]["nodes"] == before.to_dict()["nodes"]
    assert load_snapshot(root).files == before.files
    assert git(root, "ls-files", "--stage") == index and git(root, "show-ref") == refs
    assert git(root, "count-objects", "-v") == objects
    assert not (root / ".specspec-local/lock").exists()
    assert not (root / ".specspec-local/journal.json").exists()


def test_diff_provides_exact_patches_while_query_keeps_change_summaries(workspace, tmp_path):
    root, parent = workspace
    setup_repository(root)
    old = read_query(root).base
    n = old.graph.nodes[parent]
    update_node(root, parent, body="# Text\r\n\n  \tspace  \r\nUnicode\u2028and CR\rfinal")
    query = read_query(root)
    assert all("patch" not in row for row in query.result["file_changes"])
    diff = CliRunner().invoke(main, ["--root", str(root), "diff", "--json"])
    assert diff.exit_code == 0, diff.output
    patches = json.loads(diff.stdout)["result"]["file_changes"]
    destination = tmp_path / "apply"
    for path, raw in old.files.items():
        p = destination / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(raw)
    patch = "".join(f["patch"] for f in patches).encode("utf8")
    applied = subprocess.run(
        ["git", "-C", str(destination), "apply", "--whitespace=nowarn", "-"],
        input=patch,
        capture_output=True,
    )
    assert applied.returncode == 0, applied.stderr
    assert (destination / n.path).read_bytes() == query.target.files[n.path]


@pytest.mark.parametrize("human", [False, True])
def test_cli_large_multiline_body_and_visible_controls(workspace, human):
    root, parent = workspace
    body = "# Once only\n\n" + "full line\n" * 7000 + "Last line\t  \x1b[2J\u202e\n"
    update_node(root, parent, body=body)
    result = call(root, *(["--human"] if human else []))
    assert result.exit_code == 0, result.output
    if human:
        assert result.stdout.count("full line\n") == 7000
        assert "# Once only\n\nfull line\n" in result.stdout
    else:
        assert result.stdout.count("full line ") == 7000 and "full line\n" not in result.stdout
        bodies = [line for line in result.stdout.split("\n") if "# Once only" in line]
        assert len(bodies) == 1 and bodies[0].startswith("# Once only ¶ full line ")
    assert "Last line\t  \\u001b[2J\\u202e" in result.stdout
    assert "\x1b" not in result.stdout and "\u202e" not in result.stdout
    record = json.loads(call(root, "--json").stdout)["result"]["target"]["nodes"][0]
    assert record["body"] == body


@pytest.mark.parametrize(
    "args", [["ID="], ["--where", "anything"], ["--ref", "HEAD"], ["--one-line-body"]]
)
def test_removed_or_unimplemented_arguments_reject(workspace, args):
    assert call(workspace[0], *args).exit_code == 2


def test_cli_retains_available_context_when_a_document_is_unreadable(workspace):
    root, parent = workspace
    setup_repository(root)
    path = root / load_snapshot(root).graph.nodes[parent].path
    path.write_bytes(b"invalid")
    result = call(root)
    assert (
        result.exit_code == 1
        and "Target graph INVALID" in result.stdout
        and "FORMAT" in result.stderr
    )
    assert "unavailable" in result.stdout
    assert not json.loads(call(root, "--json").stdout)["ok"]
    assert call(root, "--base", "nonexistent").exit_code == 2
    assert call(root, "--base", "").exit_code == 2


def test_non_git_unborn_head_and_head_without_spec_are_explicit(workspace):
    root, _ = workspace
    result = json.loads(call(root, "--json").stdout)["result"]
    assert result["base_commit"] is None and "No Git" in result["notes"][0]
    git(root, "init")
    assert call(root).exit_code == 0
    git(
        root,
        "-c",
        "user.name=T",
        "-c",
        "user.email=t@example.invalid",
        "-c",
        "core.hooksPath=/dev/null",
        "commit",
        "--allow-empty",
        "-m",
        "Empty",
    )
    result = json.loads(call(root, "--json").stdout)["result"]
    assert result["base_commit"] and all(c["kind"] == "added" for c in result["changes"])


def test_maintained_gantt_revisions_workspace_and_comparison_match_shared_semantics(gantt_history):
    root = gantt_history
    for base, target in [
        ("stage/01-spec", "stage/02-code"),
        ("stage/02-code", "stage/03-spec"),
        ("HEAD", "workspace"),
    ]:
        query = read_query(root, base, target)
        result = call(root, "--base", base, "--target", target, "--json")
        assert result.exit_code == 0, result.output
        assert json.loads(result.stdout)["result"]["changes"] == query.result["changes"]
        for human in (False, True):
            text = render_query(query, human=human)
            assert Counter(i for _, i, ref in entries(text) if not ref) == Counter(
                {n.id for n in [*query.base.nodes, *query.target.nodes]}
            )
    commits = git(root, "rev-list", "--all").decode().splitlines()
    assert len(commits) == 8
    for commit in commits:
        query = read_query(root, commit, "workspace")
        assert query.result["base_commit"] == commit
        assert entries(render_query(query))


def test_cli_fresh_head_and_workspace_default_can_be_overridden(workspace):
    root, parent = workspace
    setup_repository(root)
    initial = git(root, "rev-parse", "HEAD").decode().strip()
    update_node(root, parent, body="Committed text\n")
    git(root, "add", ".specspec")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Second")
    current = git(root, "rev-parse", "HEAD").decode().strip()
    update_node(root, parent, body="Saved text\n")
    assert read_query(root).result["base_commit"] == current
    pinned = read_query(root, initial, current)
    assert pinned.result["target_commit"] == current
    assert pinned.target.graph.nodes[parent].body == "Committed text\n"


@pytest.mark.parametrize("encoding", ["ascii", "cp1252"])
def test_unicode_query_and_ascii_help_survive_legacy_pipes(workspace, encoding):
    root, parent = workspace
    update_node(root, parent, body="Unicode 🐕 body.\n")
    environment = {**os.environ, "PYTHONIOENCODING": encoding, "PYTHONUTF8": "0"}
    result = subprocess.run(
        [sys.executable, "-m", "specspec", "--root", str(root), "query"],
        env=environment,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    assert "Unicode 🐕 body." in result.stdout.decode("utf8")
    help_result = subprocess.run(
        [sys.executable, "-m", "specspec", "query", "--help"], env=environment, capture_output=True
    )
    assert help_result.returncode == 0
    text = help_result.stdout.decode("ascii")
    assert "--base" in text and "--target" in text and "--human" in text
    assert "--one-line-body" not in text
