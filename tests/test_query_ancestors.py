"""Ancestor completion is post-selection closure, not another bounded metric walk."""

import json
import os
import random
from collections import Counter
from dataclasses import replace

import pytest
from test_git import git
from test_query import call, entries, graph, identity, node
from test_query_select import METRICS, limits, shaped_graph
from test_query_select import query_project as query_project
from test_query_sources import BASE
from test_query_sources import project as project

from specspec.format import serialize
from specspec.graph import Graph
from specspec.query import read_query, render_query
from specspec.query_select import Limit, select_graph
from specspec.sources import SourceReader
from specspec.wire import comparison, expand_comparison
from specspec.workspace import add_node, load_snapshot, update_node


def closure_oracle(g, matches):
    """Fixed-point union over canonical declarations, independent of the graph walker."""
    result = set(matches)
    while True:
        enlarged = result | {p for i in result for p in g.nodes[i].parents}
        if enlarged == result:
            return result
        result = enlarged


def neighbors_oracle(g, matches, included):
    children = {n.id for n in g.nodes.values() if matches.intersection(n.parents)}
    parents = {p for i in matches for p in g.nodes[i].parents}
    siblings = {n.id for n in g.nodes.values() if parents.intersection(n.parents)}
    return {
        "child_ids": sorted(children - included),
        "sibling_ids": sorted(siblings - included),
        "omitted_ids": sorted((children | siblings) - included),
    }


@pytest.mark.parametrize("metric", METRICS)
@pytest.mark.parametrize("cutoff", ["0", "1", "2", "100", "0%", "50%", "100%"])
def test_completion_preserves_independent_matches_metrics_and_population(metric, cutoff):
    g = shaped_graph()
    original = [n.to_dict() for n in g.nodes.values()]
    root = identity(3)
    criteria = {metric: Limit.parse(cutoff, metric)}
    matches, selected = select_graph(g, root, criteria)
    view, completed = select_graph(g, root, criteria, with_ancestors=True)
    expected = closure_oracle(g, set(matches.nodes))
    assert set(view.nodes) == expected
    assert completed["matched_ids"] == selected["ids"]
    assert completed["ancestor_ids"] == sorted(expected - matches.nodes.keys())
    assert completed["ids"] == sorted(expected)
    assert completed["queries"] == selected["queries"]
    assert completed["population"] == selected["population"] == 4
    assert completed["edges"] == view.edges()
    assert completed["partial"] == (expected != g.nodes.keys())
    assert completed["surrounding"] == neighbors_oracle(g, set(matches.nodes), expected)
    assert all(set(n.parents) <= expected for n in view.nodes.values())
    assert [n.to_dict() for n in g.nodes.values()] == original


@pytest.mark.parametrize("mask", range(1, 8))
def test_completion_happens_after_each_criterion_and_their_union(mask):
    g = shaped_graph()
    chosen = dict(zip(METRICS, ("50%", "0", "50%"), strict=True))
    criteria = {
        m: Limit.parse(t, m) for index, (m, t) in enumerate(chosen.items()) if mask & (1 << index)
    }
    plain, original = select_graph(g, identity(3), criteria)
    view, completed = select_graph(g, identity(3), criteria, with_ancestors=True)
    assert completed["queries"] == original["queries"]
    assert set(completed["matched_ids"]) == set(plain.nodes)
    assert set(view.nodes) == closure_oracle(g, set(plain.nodes))
    assert set(completed["matched_ids"]).isdisjoint(completed["ancestor_ids"])


def test_generated_dags_completion_and_neighbor_metadata_match_declaration_oracles():
    rng = random.Random(9824)
    for _ in range(35):
        records = [node(0, kind="manifesto")]
        for index in range(1, 13):
            prior = graph(records)
            candidates = rng.sample(range(index), min(index, rng.randint(1, 4)))
            parents = [
                p
                for p in candidates
                if not any(
                    identity(p) in closure_oracle(prior, {identity(q)})
                    for q in candidates
                    if p != q
                )
            ]
            records.append(node(index, parents))
        g = graph(records)
        root = identity(rng.randrange(1, 10))
        criteria = limits(min_distance="50%", max_distance="0", influence="25%")
        matched, _ = select_graph(g, root, criteria)
        view, completed = select_graph(g, root, criteria, with_ancestors=True)
        assert set(view.nodes) == closure_oracle(g, set(matched.nodes))
        assert completed["surrounding"] == neighbors_oracle(g, set(matched.nodes), set(view.nodes))
        shuffled = graph([replace(n, parents=list(reversed(n.parents))) for n in reversed(records)])
        assert select_graph(shuffled, root, criteria, with_ancestors=True)[1] == completed


def test_root_without_criteria_still_reads_descendants_before_adding_ancestors():
    g = shaped_graph()
    view, selection = select_graph(g, identity(3), {}, with_ancestors=True)
    assert selection["matched_ids"] == sorted(identity(i) for i in (3, 4, 6, 8))
    assert selection["ancestor_ids"] == sorted(identity(i) for i in (0, 1, 2, 5))
    assert set(view.nodes) == set(g.nodes) - {identity(7)}
    assert identity(7) not in selection["surrounding"]["omitted_ids"], (
        "Added parents do not expand surrounding scope."
    )


def test_ancestors_can_outnumber_the_rooted_population_and_surroundings_are_only_near_matches():
    g = shaped_graph()
    _, selection = select_graph(g, identity(6), limits(max_distance="0"), with_ancestors=True)
    assert selection["matched_ids"] == [identity(6)] and selection["population"] == 2
    assert selection["ancestor_ids"] == sorted(identity(i) for i in range(6))
    assert selection["surrounding"] == {
        "child_ids": [identity(8)],
        "sibling_ids": [],
        "omitted_ids": [identity(8)],
    }
    assert identity(7) not in selection["surrounding"]["omitted_ids"]


def test_ancestor_completion_is_iterative_and_never_calls_per_node_closure(monkeypatch):
    ids = [f"A{i:05d}A=" for i in range(2500)]
    records = [
        replace(
            node(i, [] if not i else [i - 1], kind="manifesto" if not i else "requirement"),
            id=key,
            parents=[] if not i else [ids[i - 1]],
            path=f".specspec/{key}.md",
        )
        for i, key in enumerate(ids)
    ]
    g = Graph(
        {n.id: n for n in records},
        {key: set(n.parents) for key, n in zip(ids, records, strict=True)},
        {key: {ids[i + 1]} if i + 1 < len(ids) else set() for i, key in enumerate(ids)},
        ids,
    )
    monkeypatch.setattr(
        Graph, "closure", lambda *a, **k: pytest.fail("No per-node ancestry searches")
    )
    view, selection = select_graph(g, ids[-1], limits(max_distance="0"), with_ancestors=True)
    assert len(view.nodes) == len(ids)
    assert selection["matched_ids"] == [ids[-1]]
    assert len(selection["ancestor_ids"]) == len(ids) - 1


def test_sibling_collection_reads_each_shared_parent_child_set_once():
    g = graph([node(0, kind="manifesto"), *[node(i, [0]) for i in range(1, 401)]])
    reads = Counter()

    class Counted(dict):
        def __getitem__(self, key):
            reads[key] += 1
            return super().__getitem__(key)

    g.children = Counted(g.children)
    _, selection = select_graph(g, identity(0), limits(max_distance="50%"), with_ancestors=True)
    assert len(selection["matched_ids"]) == 201
    # Population, metric forward pass, matched-root children, distinct sibling parent,
    # and final induced view. Not another 200 sibling scans for the matched leaves.
    assert reads[identity(0)] == 5
    assert len(selection["surrounding"]["omitted_ids"]) == 200


@pytest.mark.parametrize("human", [False, True])
def test_cli_complete_multiparent_bindings_and_only_surrounding_ids(query_project, human):
    root = query_project
    args = [identity(6), "--max-distance", "0", "--with-ancestors", *(["--human"] if human else [])]
    result = call(root, *args)
    assert result.exit_code == 0, result.output
    assert "Subgraph: 1/2 matches + 6 ancestors;" in result.stdout
    assert "Surrounding IDs (bodies omitted): " + identity(8) in result.stdout
    assert "Body 7." not in result.stdout and "Body 8." not in result.stdout
    assert Counter(i for _, i, ref in entries(result.stdout) if not ref) == Counter(
        identity(i) for i in range(7)
    )
    value = json.loads(call(root, *args, "--json").stdout)["result"]
    assert (
        value
        == json.loads(
            call(root, identity(6), "--max-distance", "0", "--with-ancestors", "--json").stdout
        )["result"]
    )
    assert value["selection"]["boundary_parents"] == []
    assert value["selection"]["surrounding"]["child_ids"] == [identity(8)]
    expanded = expand_comparison(value)
    complete = read_query(root).result
    for side in ("base", "target"):
        assert expanded[side]["nodes"] == [
            n for n in complete[side]["nodes"] if n["id"] in value["selection"]["ids"]
        ]


def test_deleted_context_uses_selected_record_parents_and_explicit_history_uses_old_ancestry(
    query_project,
):
    root = query_project
    original = load_snapshot(root)
    for index in (4, 6, 8):
        (root / original.graph.nodes[identity(index)].path).unlink()
    update_node(root, identity(3), parents=[identity(2)], body="Current parent binding\n")
    q = read_query(root, node_id=identity(4), max_distance="0", with_ancestors=True)
    selection = q.result["selection"]
    assert selection["matched_ids"] == [identity(4)]
    assert selection["ancestor_ids"] == sorted(identity(i) for i in (0, 2, 3))
    assert selection["boundary_parents"] == [identity(1)], (
        "The original base parent remains a separate boundary fact."
    )
    text = render_query(q)
    assert "Current parent binding" in text and "Body 3." not in text
    assert f"{identity(4)}" in text and "[deleted]" in text
    old = read_query(
        root, "HEAD", "HEAD", node_id=identity(4), max_distance="0", with_ancestors=True
    )
    assert old.result["selection"]["ids"] == sorted(identity(i) for i in (0, 1, 3, 4))
    assert "Current parent binding" not in render_query(old) and "Body 3." in render_query(old)
    assert load_snapshot(root).graph.nodes[identity(3)].parents == [identity(2)]


def test_completion_uses_fresh_saved_ancestry_not_same_mtime_or_staged_graph(query_project):
    root = query_project
    first = read_query(root, node_id=identity(4), max_distance="0", with_ancestors=True)
    path = root / load_snapshot(root).graph.nodes[identity(3)].path
    raw, stat = path.read_bytes(), path.stat()
    update_node(root, identity(3), parents=[identity(2)])
    assert len(path.read_bytes()) == len(raw)
    os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    second = read_query(root, node_id=identity(4), max_distance="0", with_ancestors=True)
    assert identity(1) in first.result["selection"]["ancestor_ids"]
    assert identity(1) not in second.result["selection"]["ancestor_ids"]
    assert identity(2) in second.result["selection"]["ancestor_ids"]
    assert git(root, "show", ":" + path.relative_to(root).as_posix()) == raw


def test_unfiltered_completion_is_noop_even_with_distinct_manifesto_roots(query_project):
    root = query_project
    g = load_snapshot(root).graph
    old = g.nodes[identity(0)]
    new = replace(old, id=identity(99), path=f".specspec/{identity(99)}.md")
    (root / old.path).unlink()
    (root / new.path).write_bytes(serialize(new))
    for index in (1, 2):
        record = g.nodes[identity(index)]
        (root / record.path).write_bytes(serialize(replace(record, parents=[identity(99)])))
    plain = read_query(root)
    completed = read_query(root, with_ancestors=True)
    assert plain.result == completed.result and plain.display is completed.display is None
    assert identity(0) in {i for _, i, ref in entries(render_query(completed)) if not ref}


def test_empty_matches_need_no_metrics_ancestors_neighbors_or_source_reads(project, monkeypatch):
    import specspec.query_select as selection

    root, _, requirement, _, _ = project
    monkeypatch.setattr(
        selection, "metric_values", lambda *a, **k: pytest.fail("Zero quotas need no metrics")
    )
    monkeypatch.setattr(
        SourceReader, "__init__", lambda *a, **k: pytest.fail("Empty closure needs no code reader")
    )
    q = read_query(
        root, node_id=requirement, max_distance="0%", influence="0%", with_ancestors=True
    )
    assert (
        q.result["selection"]["matched_ids"]
        == q.result["selection"]["ancestor_ids"]
        == q.result["selection"]["ids"]
        == []
    )
    assert q.result["selection"]["surrounding"] == {
        "child_ids": [],
        "sibling_ids": [],
        "omitted_ids": [],
    }
    assert q.result["source_resolutions"] == [] and entries(render_query(q)) == []


def test_added_ancestors_keep_global_source_evidence_and_deduplicated_reader_work(
    project, monkeypatch
):
    root, manifesto, requirement, implementation, _ = project
    _, other = add_node(root, "requirement", [manifesto], "SECRET OTHER REQUIREMENT\n")
    _, other_impl = add_node(
        root,
        "implementation",
        [other],
        "SECRET OTHER IMPLEMENTATION\n",
        [{"path": "other.py"}],
    )
    (root / "other.py").write_bytes(b"Other source\n")
    git(root, "add", ".specspec", "other.py")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Independent source branch")
    (root / "code.py").write_bytes(BASE.replace("alpha\n", "alpha\ninserted\n").encode())
    reads, original = [], SourceReader.resolve

    def resolve(self, source):
        reads.append(source["path"])
        return original(self, source)

    monkeypatch.setattr(SourceReader, "resolve", resolve)
    q = read_query(root, node_id=requirement, max_distance="0", with_ancestors=True)
    assert q.result["selection"]["ancestor_ids"] == [manifesto]
    assert set(q.result["selection"]["source_evidence_ids"]) == {implementation, other_impl}
    assert Counter(reads) == Counter({"code.py": 2, "other.py": 2})
    assert set(q.result["source_contract_affected"]) == {manifesto, requirement}
    assert "SECRET OTHER" not in render_query(q)
    assert q.result["selection"]["surrounding"]["omitted_ids"] == sorted([implementation, other])


def test_completion_shares_one_projection_metric_closure_view_and_source_batch(
    query_project, monkeypatch
):
    import specspec.query as query_module
    import specspec.query_select as selection

    counts = Counter()
    for module, name in [
        (query_module, "snapshots"),
        (query_module, "comparison_graph"),
        (selection, "metric_values"),
        (selection, "induced"),
        (query_module, "source_comparisons"),
    ]:
        original = getattr(module, name)

        def count(*args, _original=original, _name=name, **kwargs):
            counts[_name] += 1
            return _original(*args, **kwargs)

        monkeypatch.setattr(module, name, count)
    original = selection.reachable

    def reachable(*args, **kwargs):
        if kwargs.get("ancestors"):
            counts["completion"] += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(selection, "reachable", reachable)
    q = read_query(
        query_project,
        node_id=identity(3),
        min_distance="0",
        max_distance="50%",
        influence="50%",
        with_ancestors=True,
    )
    assert counts == Counter(
        {
            name: 1
            for name in (
                "snapshots",
                "comparison_graph",
                "metric_values",
                "induced",
                "source_comparisons",
                "completion",
            )
        }
    )
    render_query(q)
    render_query(q, human=True)
    assert all(n == 1 for n in counts.values())


@pytest.mark.parametrize("human", [False, True])
@pytest.mark.parametrize("as_json", [False, True])
def test_budget_measures_complete_chosen_encoding_envelope_controls_and_final_newline(
    workspace, human, as_json
):
    root, manifesto = workspace
    update_node(
        root,
        manifesto,
        body="# Full ancestor 🐕\r\n\r\nUnicode äöü, tabs\tand ESC \x1b[2J\r\n"
        + "Full binding.\n" * 100,
    )
    _, child = add_node(root, "requirement", [manifesto], "Selected\n")
    args = [
        child,
        "--max-distance",
        "0",
        "--with-ancestors",
        *(["--human"] if human else []),
        *(["--json"] if as_json else []),
    ]
    first = call(root, *args)
    assert first.exit_code == 0, first.output
    exact = len(first.stdout.encode("utf8"))
    fitting = call(root, *args, "--max-bytes", str(exact))
    assert fitting.exit_code == 0 and fitting.stdout == first.stdout
    refused = call(root, *args, "--max-bytes", str(exact - 1))
    assert refused.exit_code == 1
    if as_json:
        error = json.loads(refused.stdout)
        assert not error["ok"] and error["result"] is None
        assert error["diagnostics"][0]["code"] == "BUDGET"
        assert str(exact) in error["diagnostics"][0]["message"]
        assert json.loads(first.stdout)["result"]["target"]["nodes"][0]["body"]
    else:
        assert refused.stdout == "" and "BUDGET" in refused.stderr
        assert "\\u001b[2J" in first.stdout and "\x1b" not in first.stdout


@pytest.mark.parametrize("as_json", [False, True])
def test_query_formats_once_even_with_exact_budget(workspace, monkeypatch, as_json):
    import specspec.cli as cli

    root, manifesto = workspace
    counts = Counter()
    for name in ("render_query", "json_text"):
        original = getattr(cli, name)

        def count(*args, _name=name, _original=original, **kwargs):
            counts[_name] += 1
            return _original(*args, **kwargs)

        monkeypatch.setattr(cli, name, count)
    result = call(
        root,
        manifesto,
        "--max-distance",
        "0",
        "--with-ancestors",
        "--max-bytes",
        "1000000",
        *(["--json"] if as_json else []),
    )
    assert result.exit_code == 0, result.output
    assert counts == Counter({"json_text" if as_json else "render_query": 1})


def test_cli_ancestor_queries_are_read_only_and_do_not_install_old_command_alias(query_project):
    from specspec.cli import main

    root = query_project
    files = load_snapshot(root).files
    commands = [
        ("status", "--porcelain=v1", "-z"),
        ("ls-files", "--stage", "-z"),
        ("show-ref",),
        ("count-objects", "-v"),
    ]
    before = [git(root, *args) for args in commands]
    for extra in ([], ["--human"], ["--json"], ["--human", "--json"]):
        result = call(root, identity(6), "--max-distance", "0", "--with-ancestors", *extra)
        assert result.exit_code == 0, result.output
    assert [git(root, *args) for args in commands] == before
    assert load_snapshot(root).files == files
    assert "context" not in main.commands


@pytest.mark.parametrize("human", [False, True])
def test_all_retained_gantt_revisions_have_complete_target_ancestor_reads(gantt_history, human):
    from specspec.git import git_snapshot

    commits = git(gantt_history, "rev-list", "--all").decode().splitlines()
    assert len(commits) == 8
    for commit in commits:
        snapshot = git_snapshot(gantt_history, commit, allow_empty=True)
        if not snapshot.nodes:
            continue
        selected = max(
            snapshot.nodes, key=lambda n: (len(snapshot.graph.closure(n.id, ancestors=True)), n.id)
        ).id
        q = read_query(
            gantt_history, commit, commit, node_id=selected, max_distance="0", with_ancestors=True
        )
        expected = snapshot.graph.closure(selected, ancestors=True) | {selected}
        assert set(q.result["selection"]["ids"]) == expected
        assert q.result["selection"]["matched_ids"] == [selected]
        assert not q.result["selection"]["boundary_parents"]
        assert Counter(
            i for _, i, ref in entries(render_query(q, human=human)) if not ref
        ) == Counter(expected)
        expanded = expand_comparison(comparison(q.result))
        assert {n["id"] for n in expanded["base"]["nodes"]} == expected
