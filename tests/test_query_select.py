"""Independent priority-frontier/path/closure oracles and scoped query integration."""

import json
import os
import random
import tracemalloc
from collections import Counter
from dataclasses import replace

import pytest
from test_git import git, setup_repository
from test_query import call, comparison, entries, graph, identity, node
from test_query_sources import BASE
from test_query_sources import project as project

from specspec.format import serialize
from specspec.graph import Graph
from specspec.model import SpecError
from specspec.query import comparison_graph, read_query, render_query
from specspec.query_select import METRICS, Limit, metric_values, select_graph
from specspec.sources import SourceReader
from specspec.wire import comparison as wire_comparison
from specspec.wire import expand_comparison
from specspec.workspace import add_node, load_snapshot, update_node


def shaped_graph():
    return graph(
        [
            node(0, kind="manifesto"),
            node(1, [0]),
            node(2, [0]),
            node(3, [1]),
            node(4, [3]),
            node(5, [2]),
            node(6, [4, 5]),
            node(7, [2]),
            node(8, [6], kind="implementation"),
        ]
    )


def oracles(g, root):
    depths = {}

    def walk(current, depth):
        depths.setdefault(current, []).append(depth)
        for child in g.children[current]:
            walk(child, depth + 1)

    walk(root, 0)
    counts = {}
    for current in depths:
        seen, pending = set(), [current]
        while pending:
            found = pending.pop()
            if found not in seen:
                seen.add(found)
                pending.extend(g.children[found])
        counts[current] = len(seen)
    return {
        "min-distance": {i: min(ds) for i, ds in depths.items()},
        "max-distance": {i: max(ds) for i, ds in depths.items()},
        "influence": counts,
    }


def frontier(g, root, values, metric, limit):
    pending, seen, result = {root}, set(), []
    quota = limit.count(len(values)) if limit.percent else None
    while pending and (quota is None or len(result) < quota):
        current = min(
            pending, key=lambda i: (-values[i] if metric == "influence" else values[i], i)
        )
        pending.remove(current)
        if not limit.percent and not (
            values[current] >= limit.value
            if metric == "influence"
            else values[current] <= limit.value
        ):
            break
        seen.add(current)
        result.append({"id": current, "value": values[current]})
        pending.update(g.children[current] - seen)
    return result


def limits(**values):
    return {
        key.replace("_", "-"): Limit.parse(value, key.replace("_", "-"))
        for key, value in values.items()
    }


@pytest.mark.parametrize("metric", METRICS)
@pytest.mark.parametrize(
    "text", ["0", "1", "2", "3", "100", "0%", "50%", "100%", "0.01%", "66.67%"]
)
def test_inclusive_thresholds_exact_quotas_and_reversed_influence_match_literal_frontier(
    metric, text
):
    g, root = shaped_graph(), identity(0)
    expected_values = oracles(g, root)
    limit = Limit.parse(text, metric)
    before = [n.to_dict() for n in g.nodes.values()]
    view, selection = select_graph(g, root, {metric: limit})
    expected = frontier(g, root, expected_values[metric], metric, limit)
    assert selection["queries"][0]["nodes"] == expected
    assert set(view.nodes) == {n["id"] for n in expected}
    assert selection["population"] == 9
    assert selection["edges"] == view.edges()
    assert [n.to_dict() for n in g.nodes.values()] == before


def test_root_relative_shortest_longest_and_self_inclusive_influence_are_independent():
    g = shaped_graph()
    values = metric_values(g, identity(0), set(g.nodes), set(METRICS))
    assert values == oracles(g, identity(0))
    assert values["min-distance"][identity(6)] == 3
    assert values["max-distance"][identity(6)] == 4
    assert values["influence"][identity(0)] == 9
    assert values["influence"][identity(1)] == 5
    assert values["influence"][identity(8)] == 1
    view, selection = select_graph(g, identity(3), limits(max_distance="1"))
    assert set(view.nodes) == {identity(3), identity(4)}
    assert selection["population"] == 4
    assert selection["queries"][0]["nodes"] == [
        {"id": identity(3), "value": 0},
        {"id": identity(4), "value": 1},
    ]
    assert view.nodes[identity(3)].parents == [identity(1)]
    assert view.parents[identity(3)] == set()


def test_percentage_example_selects_62_of_124_including_root_and_splits_id_ties():
    g = graph([node(0, kind="manifesto"), *[node(i, [0]) for i in range(1, 124)]])
    _, selection = select_graph(g, identity(0), limits(max_distance="50%"))
    assert len(selection["ids"]) == 62
    expected = [identity(0), *sorted(set(g.nodes) - {identity(0)})[:61]]
    assert [n["id"] for n in selection["queries"][0]["nodes"]] == expected
    assert Limit.parse("66.66666666666666666667%", "max-distance").count(3) == 3
    assert Limit.parse("66.66666666666666666666%", "max-distance").count(3) == 2


@pytest.mark.parametrize("mask", range(1, 8))
def test_all_criterion_combinations_union_independent_subqueries(mask):
    g, root = shaped_graph(), identity(0)
    requested = dict(zip(METRICS, ("0", "50%", "50%"), strict=True))
    chosen = {
        m: Limit.parse(text, m)
        for index, (m, text) in enumerate(requested.items())
        if mask & (1 << index)
    }
    view, selection = select_graph(g, root, chosen)
    separate = [select_graph(g, root, {m: cutoff})[1] for m, cutoff in chosen.items()]
    assert set(view.nodes) == set().union(*(set(s["ids"]) for s in separate))
    assert selection["queries"] == [s["queries"][0] for s in separate]
    if mask == 6:
        assert len(view.nodes) == 6  # Two five-node quotas, with distinct boundary choices.


def test_generated_shortcut_free_dags_and_reordered_inputs_match_frontier_and_path_oracles():
    randomizer = random.Random(781)
    for _ in range(40):
        records = [node(0, kind="manifesto")]
        for index in range(1, 12):
            previous = graph(records)
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
            records.append(node(index, parents))
        g = graph(records)
        reordered = graph(
            [replace(n, parents=list(reversed(n.parents))) for n in reversed(records)]
        )
        root = identity(randomizer.randrange(4))
        values = oracles(g, root)
        population = set(values["influence"])
        assert metric_values(g, root, population, set(METRICS)) == values
        chosen = limits(min_distance="50%", max_distance="2", influence="66.67%")
        _, selection = select_graph(g, root, chosen)
        assert selection == select_graph(reordered, root, chosen)[1]
        expected = [frontier(g, root, values[m], m, cutoff) for m, cutoff in chosen.items()]
        assert [q["nodes"] for q in selection["queries"]] == expected
        assert set(selection["ids"]) == {n["id"] for query in expected for n in query}


def test_distance_bounds_share_one_forward_pass_and_influence_one_reverse_pass(monkeypatch):
    g = shaped_graph()
    reads = Counter()

    class Counted:
        def __init__(self, key, children):
            self.key, self.children = key, children

        def __iter__(self):
            reads[self.key] += 1
            return iter(self.children)

    g.children = {i: Counted(i, children) for i, children in g.children.items()}
    monkeypatch.setattr(
        Graph, "closure", lambda *a, **k: pytest.fail("No per-node closure in metric batch")
    )
    values = metric_values(g, identity(0), set(g.nodes), set(METRICS))
    assert values["influence"][identity(0)] == 9
    assert reads == Counter({i: 2 for i in g.nodes})


@pytest.mark.parametrize("shape", ["chain", "fan"])
def test_large_influence_batches_are_iterative_and_release_live_bitsets(shape):
    ids = [f"A{i:05d}A=" for i in range(20000)]
    records = [replace(node(0, kind="manifesto"), id=ids[0])]
    parents, children = {ids[0]: set()}, {i: set() for i in ids}
    for index, current in enumerate(ids[1:], 1):
        parent = ids[index - 1] if shape == "chain" else ids[0]
        records.append(replace(node(index), id=current, parents=[parent]))
        parents[current] = {parent}
        children[parent].add(current)
    g = Graph({n.id: n for n in records}, parents, children, ids)
    tracemalloc.start()
    try:
        values = metric_values(g, ids[0], set(ids), {"influence"})["influence"]
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert values[ids[0]] == len(ids) and values[ids[-1]] == 1
    assert values[ids[1]] == (len(ids) - 1 if shape == "chain" else 1)
    assert peak < 16 * 1024 * 1024, f"Retained closure rows consume {peak} bytes"


@pytest.mark.parametrize(
    "text",
    [
        "",
        "-1",
        "+1",
        "1.5",
        "NaN",
        "inf",
        "101%",
        "-1%",
        "%",
        "1e1%",
        "1/2%",
        " 50%",
        "５０%",
        "9" * 65,
    ],
)
def test_invalid_criteria_are_invocation_errors(text):
    with pytest.raises(SpecError) as error:
        Limit.parse(text, "max-distance")
    assert error.value.exit_code == 2


@pytest.fixture
def query_project(tmp_path):
    g = shaped_graph()
    for record in g.nodes.values():
        path = tmp_path / record.path
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(serialize(record))
    setup_repository(tmp_path)
    return tmp_path


@pytest.mark.parametrize("human", [False, True])
def test_cli_scopes_bindings_and_reconstructs_selected_revisions_with_full_boundary_parents(
    query_project, human
):
    root = query_project
    update_node(root, identity(4), body="Current\n\n  indented\n")
    args = [identity(3), "--max-distance", "1", *(["--human"] if human else [])]
    result = call(root, *args)
    assert result.exit_code == 0, result.output
    assert "Subgraph: 2/4 nodes" in result.stdout
    assert Counter(i for _, i, ref in entries(result.stdout) if not ref) == Counter(
        {identity(3), identity(4)}
    )
    assert f"requirement {identity(3)}node-3 @ {identity(1)}\nBody 3." in result.stdout
    expected = "  Current\n  \n    indented\n" if human else "  Current ¶   indented "
    assert expected in result.stdout
    value = json.loads(call(root, *args, "--json").stdout)["result"]
    assert (
        value
        == json.loads(call(root, identity(3), "--max-distance", "1", "--json").stdout)["result"]
    )
    assert value["selection"]["boundary_parents"] == [identity(1)]
    assert {n["id"] for n in value["target"]["nodes"]} == {identity(3), identity(4)}
    expanded = expand_comparison(value)
    full = read_query(root).result
    for side in ("base", "target"):
        assert expanded[side]["nodes"] == [
            n for n in full[side]["nodes"] if n["id"] in {identity(3), identity(4)}
        ]
        assert expanded[side]["valid"]  # Original graph validity, not canonicality of this view.
    assert value["changes"] == [{"id": identity(4), "kind": "changed", "fields": ["body"]}]
    assert all(c["path"].endswith(f"{identity(4)}node-4.md") for c in value["file_changes"])


def test_deleted_records_reparenting_and_explicit_deleted_root_use_selected_edges(query_project):
    root = query_project
    for index in (4, 6, 8):
        (root / load_snapshot(root).graph.nodes[identity(index)].path).unlink()
    update_node(root, identity(3), parents=[identity(2)])
    query = read_query(root, node_id=identity(3), max_distance="2")
    assert query.result["selection"]["ids"] == sorted(identity(i) for i in (3, 4, 6))
    assert "[deleted]" in render_query(query)
    deleted = read_query(root, node_id=identity(4))
    assert deleted.result["selection"]["ids"] == sorted(identity(i) for i in (4, 6, 8))
    assert deleted.result["target"]["nodes"] == []
    restored = expand_comparison(wire_comparison(deleted.result))
    assert [n["id"] for n in restored["base"]["nodes"]] == sorted(identity(i) for i in (4, 6, 8))


def test_default_metric_root_is_target_manifesto_and_old_roots_remain_explicit(query_project):
    root = query_project
    g = load_snapshot(root).graph
    old = g.nodes[identity(0)]
    new = replace(old, id=identity(99), path=f"_specspec/{identity(99)}new-root.md")
    (root / old.path).unlink()
    (root / new.path).write_bytes(serialize(new))
    for index in (1, 2):
        record = g.nodes[identity(index)]
        (root / record.path).write_bytes(serialize(replace(record, parents=[identity(99)])))
    full = read_query(root)
    assert identity(0) in {i for _, i, reference in entries(render_query(full)) if not reference}
    scoped = read_query(root, max_distance="100%")
    assert scoped.result["selection"]["root"] == identity(99)
    assert identity(0) not in scoped.result["selection"]["ids"]
    previous = read_query(root, node_id=identity(0))
    assert previous.result["selection"]["ids"] == [identity(0)]


def test_batch_ranking_handles_shortcuts_and_full_revision_union_cycles():
    base = graph(
        [node(0, kind="manifesto"), node(1, [0]), node(2, [1]), node(3, [1, 4]), node(4, [0])]
    )
    target = graph([node(0, kind="manifesto"), node(2, [0]), node(1, [2])])
    query = comparison(target, base)
    g = comparison_graph(query.base, query.target)
    _, selection = select_graph(g, identity(0), limits(max_distance="100%", influence="100%"))
    expected = oracles(g, identity(0))
    for subquery in selection["queries"]:
        assert subquery["nodes"] == frontier(
            g,
            identity(0),
            expected[subquery["metric"]],
            subquery["metric"],
            Limit.parse("100%", subquery["metric"]),
        )


def test_minimum_distance_selection_keeps_shared_children_without_adding_distant_parents():
    g = graph(
        [
            node(0, kind="manifesto"),
            node(1, [0]),
            node(2, [0]),
            node(3, [1]),
            node(4, [3]),
            node(9, [4]),
            node(10, [9]),
            node(5, [2]),
            node(6, [5, 10]),
        ]
    )
    view, selection = select_graph(g, identity(0), limits(min_distance="3"))
    assert identity(6) in view.nodes and identity(10) not in view.nodes
    assert view.nodes[identity(6)].parents == [identity(5), identity(10)]
    assert view.parents[identity(6)] == {identity(5)}
    assert identity(10) not in selection["ids"]


def test_cli_accepts_hyphen_leading_full_ids_and_keeps_every_boundary_parent(query_project):
    root = query_project
    snapshot = load_snapshot(root)
    old = snapshot.graph.nodes[identity(8)]
    (root / old.path).unlink()
    new = replace(old, id="-AAAAAA=", path="_specspec/-AAAAAA=hyphen.md")
    (root / new.path).write_bytes(serialize(new))
    result = call(root, "-AAAAAA=", "--max-distance", "0", "--json")
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["result"]["selection"]["ids"] == ["-AAAAAA="]
    result = call(root, identity(6), "--max-distance", "0")
    assert f"requirement {identity(6)}node-6 @ {identity(4)}, {identity(5)}" in result.stdout
    value = json.loads(call(root, identity(6), "--max-distance", "0", "--json").stdout)["result"]
    assert value["selection"]["boundary_parents"] == [identity(4), identity(5)]


def test_filtered_reads_use_fresh_saved_graph_bytes_not_mtime_or_the_index(query_project):
    root = query_project
    first = read_query(root, max_distance="1")
    assert set(first.result["selection"]["ids"]) == {identity(i) for i in (0, 1, 2)}
    path = root / load_snapshot(root).graph.nodes[identity(7)].path
    before, stat = path.read_bytes(), path.stat()
    update_node(root, identity(7), parents=[identity(0)])
    assert len(path.read_bytes()) == len(before) and path.read_bytes() != before
    os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    second = read_query(root, max_distance="1")
    assert set(second.result["selection"]["ids"]) == {identity(i) for i in (0, 1, 2, 7)}
    assert git(root, "show", ":" + path.relative_to(root).as_posix()) == before
    assert path.read_bytes() != before


def test_scoped_reads_do_not_modify_files_refs_index_or_object_store(query_project):
    root = query_project
    files = {p: p.read_bytes() for p in (root / "_specspec").iterdir()}
    before = [
        git(root, *args)
        for args in (
            ("status", "--porcelain=v1", "-z"),
            ("show-ref",),
            ("ls-files", "--stage", "-z"),
            ("count-objects", "-v"),
        )
    ]
    for args in (
        ["--max-distance", "50%"],
        [identity(3), "--influence", "1", "--human"],
        ["--min-distance", "0", "--max-distance", "50%", "--influence", "50%", "--json"],
    ):
        result = call(root, *args)
        assert result.exit_code == 0, result.output
    after = [
        git(root, *args)
        for args in (
            ("status", "--porcelain=v1", "-z"),
            ("show-ref",),
            ("ls-files", "--stage", "-z"),
            ("count-objects", "-v"),
        )
    ]
    assert after == before
    assert all(path.read_bytes() == data for path, data in files.items())


def test_unknown_roots_bad_limits_and_invalid_unselected_nodes_fail_before_tree(query_project):
    root = query_project
    assert call(root, identity(99)).exit_code == 2
    assert call(root, "--max-distance", "101%").exit_code == 2
    path = root / load_snapshot(root).graph.nodes[identity(8)].path
    path.write_bytes(b"invalid")
    result = call(root, identity(7))
    assert result.exit_code == 1 and result.stdout == ""


def test_zero_percent_skips_metric_and_source_work_and_root_alone_skips_metrics(
    project, monkeypatch
):
    import specspec.query_select as selection

    root, _, requirement, _, _ = project
    monkeypatch.setattr(
        selection, "metric_values", lambda *a, **k: pytest.fail("No unused metric batch")
    )
    monkeypatch.setattr(
        SourceReader,
        "__init__",
        lambda *a, **k: pytest.fail("No source readers for an empty selection"),
    )
    query = read_query(root, max_distance="0%", influence="0%")
    assert query.result["selection"]["ids"] == [] and query.result["source_resolutions"] == []
    assert query.result["target"]["nodes"] == []
    assert entries(render_query(query)) == []
    monkeypatch.undo()
    monkeypatch.setattr(
        selection, "metric_values", lambda *a, **k: pytest.fail("Root alone needs no metrics")
    )
    assert len(read_query(root, node_id=requirement).result["selection"]["ids"]) == 2


@pytest.mark.parametrize("reparent", [False, True])
def test_excluded_descendant_evidence_preserves_selected_badges_and_skips_unrelated_sources(
    project, monkeypatch, reparent
):
    root, manifesto, requirement, implementation, _ = project
    _, other = add_node(root, "requirement", [manifesto], "Other\n", "other")
    add_node(
        root,
        "implementation",
        [other],
        "Other source\n",
        "other-source",
        [{"path": "unrelated.py"}],
    )
    git(root, "add", "_specspec")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Independent source branch")
    if reparent:
        update_node(root, implementation, parents=[other])
    (root / "code.py").write_bytes(BASE.replace("alpha\n", "alpha\ninserted\n").encode())
    resolved, original = [], SourceReader.resolve

    def resolve(self, source):
        resolved.append(source["path"])
        return original(self, source)

    monkeypatch.setattr(SourceReader, "resolve", resolve)
    query = read_query(root, node_id=requirement, max_distance="0")
    assert set(resolved) == {"code.py"} and len(resolved) == 2
    assert query.result["selection"]["ids"] == [requirement]
    assert query.result["selection"]["source_evidence_ids"] == [implementation]
    assert {r["id"] for r in query.result["source_resolutions"]} == {implementation}
    assert query.result["source_contract_affected"] == [requirement]
    assert "[source-changed]" in render_query(query)
    assert "sources: " not in render_query(query)  # Evidence owner, not the ancestor, declares it.


def test_all_criteria_share_one_snapshot_projection_metric_and_source_batch(project, monkeypatch):
    import specspec.query as query_module
    import specspec.query_select as selection

    root, _, requirement, _, _ = project
    calls = Counter()
    for module, name in [
        (query_module, "snapshots"),
        (query_module, "comparison_graph"),
        (selection, "metric_values"),
        (query_module, "source_comparisons"),
        (query_module, "source_change_impact"),
        (selection.Limit, "count"),
    ]:
        original = getattr(module, name)

        def counted(*args, _name=name, _original=original, **kwargs):
            calls[_name] += 1
            return _original(*args, **kwargs)

        monkeypatch.setattr(module, name, counted)
    query = read_query(
        root, node_id=requirement, min_distance="0", max_distance="50%", influence="2"
    )
    assert calls == Counter(
        {
            name: 1
            for name in (
                "snapshots",
                "comparison_graph",
                "metric_values",
                "source_comparisons",
                "source_change_impact",
                "count",
            )
        }
    )
    render_query(query)
    render_query(query, human=True)
    assert all(value == 1 for value in calls.values()), "Rendering reuses the selected projection."


def test_benchmark_profiles_the_same_selection_as_its_fresh_cli_processes(query_project, tmp_path):
    from tools.benchmark_query import benchmark

    report = benchmark(
        query_project,
        1,
        tmp_path / "benchmark.json",
        node_id=identity(3),
        min_distance="0",
        max_distance="50%",
        influence="50%",
        with_ancestors=True,
    )
    assert report["query"] == {
        "node_id": identity(3),
        "min_distance": "0",
        "max_distance": "50%",
        "influence": "50%",
        "with_ancestors": True,
    }
    assert report["selection"]["matched_ids"] == [identity(3), identity(4)]
    assert report["selection"]["ancestor_ids"] == [identity(0), identity(1)]
    assert report["selection"]["population"] == 4
    assert len(report["selection"]["queries"]) == 3
    assert report["profile"]["git_processes"]
    assert all(len(value["seconds"]) == 1 for value in report["cli"].values())
    assert (tmp_path / "benchmark.prof").is_file()


def test_current_schema_gantt_retained_revisions_support_every_metric_and_union(gantt_history):
    root = gantt_history
    commits = git(root, "rev-list", "--all").decode().splitlines()
    assert len(commits) == 8
    for commit in commits:
        query = read_query(
            root, commit, "workspace", min_distance="25%", max_distance="2", influence="50%"
        )
        selection = query.result["selection"]
        assert set(selection["ids"]) == {n["id"] for q in selection["queries"] for n in q["nodes"]}
        assert selection["population"] == len(
            {n.id for n in [*query.base.nodes, *query.target.nodes]}
        )
        assert Counter(i for _, i, ref in entries(render_query(query)) if not ref) == Counter(
            selection["ids"]
        )
