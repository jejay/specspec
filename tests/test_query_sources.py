"""Declared tracking contracts decide query cues; raw source facts stay separate."""

import json
import os
import subprocess
from collections import Counter

import pytest
from click.testing import CliRunner
from test_git import git, setup_repository

from specspec.cli import main
from specspec.model import SpecError
from specspec.query import read_query, render_query, source_line
from specspec.query_sources import CodeVersion
from specspec.sources import SourceReader
from specspec.workspace import add_node, update_node

BASE = "before\nalpha\nbeta\nafter\nend\n"


def commit(root, message):
    git(root, "add", "_specspec", "code.py")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", message)


@pytest.fixture
def project(workspace):
    root, manifesto = workspace
    _, requirement = add_node(root, "requirement", [manifesto], "Behavior\n", "behavior")
    _, implementation = add_node(root, "implementation", [requirement], "Mapping\n", "mapping")
    (root / "code.py").write_bytes(BASE.encode("utf8"))
    setup_repository(root)
    commit(root, "Code baseline")
    source = SourceReader(root, ref="HEAD").capture("code.py", [[2, 3]], "strict")
    update_node(root, implementation, sources=[source])
    git(root, "add", "_specspec")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Anchored mapping")
    return root, manifesto, requirement, implementation, source


def rows(project, **kwargs):
    root, _, _, implementation, _ = project
    query = read_query(root, **kwargs)
    return query, [r for r in query.result["source_resolutions"] if r["id"] == implementation]


@pytest.mark.parametrize(
    "code,mode,content,position,region,outcome",
    [
        (BASE, "strict", "same", "same", "same", "resolved"),
        ("prefix\n" + BASE, "strict", "same", "changed", "relocated", "resolved"),
        (BASE + "outside\n", "strict", "same", "same", "same", "resolved"),
        (
            BASE.replace("alpha\n", "alpha\ninserted\n"),
            "strict",
            "unavailable",
            "unavailable",
            "unavailable",
            "conflict",
        ),
        (
            BASE.replace("alpha\n", "alpha\ninserted\n"),
            "expanding",
            "changed",
            "changed",
            "modified",
            "modified",
        ),
        (
            BASE.replace("alpha", "replacement"),
            "expanding",
            "changed",
            "same",
            "modified",
            "modified",
        ),
        (BASE + BASE, "strict", "unavailable", "unavailable", "unavailable", "ambiguous"),
        (BASE.replace("\n", "\r\n"), "strict", "same", "same", "same", "resolved"),
    ],
)
def test_source_fact_matrix(project, code, mode, content, position, region, outcome):
    root, manifesto, requirement, implementation, source = project
    if mode != source["mode"]:
        source = {**source, "mode": mode}
        update_node(root, implementation, sources=[source])
        git(root, "add", "_specspec")
        git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Broad mapping")
    (root / "code.py").write_bytes(code.encode("utf8"))
    query, values = rows(project)
    assert query.result["changes"] == []  # Code changes do not manufacture node modifications.
    assert len(values) == 1 and values[0]["declaration"] == "="
    row = values[0]
    assert row["bytes"] == ("same" if code == BASE else "changed")
    assert (row["text"], row["position"], row["region"]) == (content, position, region)
    assert row["base"]["ranges"] == [[2, 3]]
    assert row["target"]["outcome"] == outcome
    assert set(query.result["source_affected"]) == (
        set() if code == BASE else {manifesto, requirement, implementation}
    )
    expected = (
        "changed" if outcome == "conflict" else "unavailable" if outcome == "ambiguous" else "same"
    )
    assert row["contract"] == expected
    assert set(query.result["source_contract_affected"]) == (
        {manifesto, requirement, implementation} if expected == "changed" else set()
    )
    assert query.result["source_contract_complete"] == (expected != "unavailable")
    assert set(query.result["affected"]) == set(query.result["source_contract_affected"])
    text = render_query(query)
    if expected == "same":
        assert "[" not in source_line(row)
    else:
        assert source_line(row).endswith(" [" + outcome + "]")
    assert ("[source-changed]" in text) == (expected == "changed")
    assert "region=" not in text and "bytes=" not in text
    assert "file changed" not in text and "region changed" not in text and "moved" not in text


def test_declaration_edit_does_not_masquerade_as_an_underlying_code_edit(project):
    root, _, _, implementation, source = project
    new = {**source, "ranges": [[2, 4]], "symbol": "Description\nnot an AST query"}
    update_node(root, implementation, sources=[new])
    query, values = rows(project)
    assert {r["declaration"] for r in values} == {"-", "+"}
    assert all(r["bytes"] == r["text"] == r["position"] == r["region"] == "same" for r in values)
    assert not query.result["source_changes"]
    assert query.result["changes"] == [
        {"id": implementation, "kind": "changed", "fields": ["sources"]}
    ]
    assert {json.dumps(r["reference"], sort_keys=True) for r in values} == {
        json.dumps(s, sort_keys=True) for s in (source, new)
    }


def test_new_declaration_compares_old_code_even_when_not_previously_declared(project):
    root, _, _, implementation, source = project
    update_node(root, implementation, sources=[source, source, {"path": "code.py"}])
    _, values = rows(project)
    assert Counter(r["declaration"] for r in values) == {"=": 1, "+": 2}
    assert sorted(r["target_source"] for r in values) == [1, 2, 3]
    assert [r["base_source"] for r in values if r["base_source"]] == [1]
    assert all(r["bytes"] == r["text"] == "same" for r in values)
    whole = next(r for r in values if "blob" not in r["reference"])
    assert whole["base"]["ranges"] == whole["target"]["ranges"] == [[1, 5]]


def test_selected_revisions_not_anchor_outcomes_determine_region_change(project):
    root, _, _, implementation, source = project
    update_node(root, implementation, sources=[{**source, "mode": "expanding"}])
    (root / "code.py").write_text(BASE.replace("alpha\n", "alpha\ninserted\n"), encoding="utf8")
    commit(root, "Already modified region")
    with (root / "code.py").open("a", encoding="utf8") as stream:
        stream.write("outside\n")
    query, values = rows(project)
    row = values[0]
    assert row["contract"] == "same" and not query.result["source_contract_affected"]
    assert "[" not in source_line(row)
    assert row["base"]["outcome"] == row["target"]["outcome"] == "modified"
    assert row["bytes"] == "changed" and row["region"] == "same"
    assert row["text"] == row["position"] == "same"


@pytest.mark.parametrize("prefix", ["", "prefix\n"])
def test_unique_rename_resolves_actual_paths_and_positions(project, prefix):
    root, _, _, _, _ = project
    git(root, "mv", "code.py", "renamed.py")
    (root / "renamed.py").write_bytes((prefix + BASE).encode("utf8"))
    query, values = rows(project)
    row = values[0]
    assert row["declaration"] == "=" and row["region"] == "relocated"
    assert row["base"]["path"] == "code.py" and row["base"]["ranges"] == [[2, 3]]
    assert row["target"]["path"] == "renamed.py"
    assert row["target"]["ranges"] == ([[3, 4]] if prefix else [[2, 3]])
    assert row["bytes"] == ("changed" if prefix else "same")
    assert query.result["source_changes"]
    assert row["contract"] == "same" and not query.result["source_contract_affected"]
    assert "[" not in source_line(row)


def test_intrafile_move_uses_existing_region_evidence(project):
    root, _, _, implementation, _ = project
    old = "start\nalpha\nbeta\nlong-x\nlong-y\nlong-z\nlast\n"
    (root / "code.py").write_text(old, encoding="utf8")
    commit(root, "Move baseline")
    source = SourceReader(root, ref="HEAD").capture("code.py", [[2, 3]], "strict")
    update_node(root, implementation, sources=[source])
    git(root, "add", "_specspec")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Move anchor")
    (root / "code.py").write_text(
        "start\nlong-x\nlong-y\nlong-z\nalpha\nbeta\nlast\n", encoding="utf8"
    )
    query, values = rows(project)
    assert values[0]["region"] == "relocated"
    assert values[0]["target"]["ranges"] == [[5, 6]]
    assert values[0]["contract"] == "same" and not query.result["source_contract_affected"]
    assert "[" not in source_line(values[0])


def test_missing_anchor_is_explicit_while_actual_file_bytes_are_still_known(project):
    root, _, _, implementation, source = project
    update_node(root, implementation, sources=[{**source, "blob": "a" * 40}])
    git(root, "add", "_specspec")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Unavailable mapping")
    query, values = rows(project)
    assert values[0]["bytes"] == "same" and values[0]["region"] == "unavailable"
    assert values[0]["base"]["outcome"] == values[0]["target"]["outcome"] == "unavailable"
    assert "[unavailable]" in render_query(query)
    assert "missing" in json.dumps(values[0]).lower()


def test_missing_whole_file_is_not_reported_as_unchanged(project):
    root, _, _, implementation, _ = project
    update_node(root, implementation, sources=[{"path": "missing.py"}])
    _, values = rows(project)
    row = next(r for r in values if r["reference"]["path"] == "missing.py")
    assert row["region"] == row["bytes"] == "unavailable"
    assert row["base"]["outcome"] == row["target"]["outcome"] == "missing"


@pytest.mark.parametrize(
    "raw", [b"binary\0data\n", b"version https://git-lfs.github.com/spec/v1\n", b"\xffinvalid"]
)
def test_non_line_targets_compare_bytes_without_inventing_line_coordinates(project, raw):
    root, _, _, implementation, _ = project
    (root / "code.py").write_bytes(raw)
    update_node(root, implementation, sources=[{"path": "code.py"}])
    commit(root, "Whole artifact")
    query, values = rows(project)
    row = values[0]
    assert row["bytes"] == "same" and row["region"] == "unavailable"
    assert not row["base"]["text_available"] and not row["target"]["text_available"]
    assert "read_message" in row["base"]
    assert row["contract"] == "same"
    assert "[" not in source_line(row)
    assert not query.result["source_contract_affected"]
    assert "unavailable" not in source_line(row)


def test_source_read_budget_remains_explicit_and_graph_read_succeeds(project, monkeypatch):
    root, _, _, implementation, _ = project
    update_node(root, implementation, sources=[{"path": "code.py"}])
    commit(root, "Whole source")
    monkeypatch.setattr("specspec.sources.MAX_BYTES", 8)
    query, values = rows(project)
    assert values[0]["region"] == values[0]["bytes"] == "unavailable"
    assert "lines unavailable" not in render_query(query)
    assert "budget" in json.dumps(values[0]).lower()
    assert values[0]["contract"] == "same"
    assert source_line(values[0]) == "sources: code.py"
    assert not query.result["source_contract_affected"]
    assert query.result["impact_complete"]


def test_exact_historical_code_not_dirty_workspace_code_is_compared(project):
    root, _, _, _, _ = project
    base = git(root, "rev-parse", "HEAD").decode().strip()
    (root / "code.py").write_text("prefix\n" + BASE, encoding="utf8")
    commit(root, "Shift lines")
    target = git(root, "rev-parse", "HEAD").decode().strip()
    (root / "code.py").write_text("Unrelated dirty source\n", encoding="utf8")
    query, values = rows(project, base=base, target=target)
    assert values[0]["region"] == "relocated"
    assert values[0]["target"]["ranges"] == [[3, 4]]
    assert query.result["base_commit"] == base and query.result["target_commit"] == target


def test_empty_and_non_git_base_sources_are_distinguished(workspace):
    root, parent = workspace
    _, requirement = add_node(root, "requirement", [parent], "Behavior\n", "req")
    (root / "code.py").write_text("one\n", encoding="utf8")
    add_node(root, "implementation", [requirement], "Code\n", "code", [{"path": "code.py"}])
    first = read_query(root).result["source_resolutions"][0]
    assert first["base"]["outcome"] == "unavailable" and first["bytes"] == "unavailable"
    git(root, "init")
    second = read_query(root).result["source_resolutions"][0]
    assert second["base"]["outcome"] == "missing" and second["bytes"] == "added"
    assert second["target"]["ranges"] == [[1, 1]]


def test_source_reads_are_cached_across_nodes_but_declaration_rows_remain_separate(
    project, monkeypatch
):
    root, _, requirement, _, source = project
    add_node(root, "implementation", [requirement], "Another mapping\n", "other", [source])
    calls = Counter()
    original = SourceReader.read_data

    def counted(reader, path):
        calls[(reader.target, path)] += 1
        return original(reader, path)

    monkeypatch.setattr(SourceReader, "read_data", counted)
    query = read_query(root)
    assert len(query.result["source_resolutions"]) == 2
    assert len(calls) == 2 and all(n == 1 for n in calls.values())


@pytest.mark.parametrize("mode", ["strict", "expanding"])
def test_separate_regions_keep_gaps_out_of_the_compared_selection(project, mode):
    root, _, _, implementation, source = project
    update_node(
        root, implementation, sources=[{**source, "mode": mode, "ranges": [[2, 2], [4, 4]]}]
    )
    commit(root, "Separate regions")
    (root / "code.py").write_bytes(BASE.replace("beta\n", "beta\ngap addition\n").encode("utf8"))
    query, values = rows(project)
    assert values[0]["target"]["ranges"] == [[2, 2], [5, 5]]
    assert values[0]["text"] == "same" and values[0]["region"] == "relocated"
    assert values[0]["contract"] == "same" and not query.result["source_contract_affected"]
    assert "[" not in source_line(values[0])


def test_staging_alone_does_not_change_workspace_source_comparison(project):
    root, _, _, _, _ = project
    (root / "code.py").write_bytes(("prefix\n" + BASE).encode("utf8"))
    first = read_query(root)
    git(root, "add", "code.py")
    second = read_query(root)
    assert first.result["source_resolutions"] == second.result["source_resolutions"]
    assert first.result["source_changes"] == second.result["source_changes"]
    assert first.result["changes"] == second.result["changes"] == []


def test_query_source_symlink_escape_remains_unavailable(project):
    root, _, _, implementation, source = project
    escape = root / "escape.py"
    escape.write_bytes(b"permitted source\n")
    update_node(root, implementation, sources=[source, {"path": "escape.py"}])
    git(root, "add", "_specspec", "escape.py")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Safe historical source")
    outside = root.parent / (root.name + "-outside.py")
    outside.write_bytes(b"not a permitted source\n")
    escape.unlink()
    try:
        escape.symlink_to(outside)
    except OSError:
        pytest.skip("Symlinks are unavailable.")
    with pytest.raises(SpecError, match="outside"):
        read_query(root)  # Unsafe saved metadata still fails graph validation.
    _, values = rows(project, target="HEAD")
    row = next(r for r in values if r["reference"]["path"] == "escape.py")
    assert row["bytes"] == row["region"] == "unavailable"
    assert row["base"]["outcome"] == row["target"]["outcome"] == "unavailable"


def test_unchanged_source_display_is_one_plain_location_without_metadata_dump(project):
    root, _, _, _, source = project
    text = render_query(read_query(root))
    displayed = [
        line.lstrip("│ ") for line in text.split("\n") if line.lstrip("│ ").startswith("sources:")
    ]
    assert displayed == ["sources: code.py:2-3"]
    assert source["blob"] not in text
    assert '"ranges"' not in text and '"mode"' not in text and "b1/t1" not in text
    assert "[=]" not in text


@pytest.mark.parametrize("human", [False, True])
def test_source_display_keeps_duplicate_references_and_only_hints_metadata_edits(project, human):
    root, _, _, implementation, source = project
    update_node(
        root, implementation, sources=[source, {**source, "symbol": "Long\nnew description"}]
    )
    query = read_query(root)
    text = render_query(query, human=human)
    displayed = [line.lstrip("│ ") for line in text.split("\n") if "sources: " in line]
    expected = [source_line(row) for row in query.result["source_resolutions"]]
    assert displayed == (
        expected
        if human
        else ["sources: " + ", ".join(s.removeprefix("sources: ") for s in expected)]
    )
    assert len(displayed) == (2 if human else 1)
    assert sum("[ref+]" in line for line in displayed) == 1
    assert "Long" not in text and source["blob"] not in text
    assert all("changed" not in line for line in displayed)


@pytest.mark.parametrize("human", [False, True])
def test_cli_source_lists_preserve_duplicates_ranges_quoted_paths_and_individual_issues(
    project, human
):
    root, _, _, implementation, source = project
    (root / "extra, source.py").write_bytes(b"new file\n")
    update_node(
        root,
        implementation,
        sources=[
            source,
            source,
            {**source, "ranges": [[2, 2], [4, 4]]},
            {"path": "extra, source.py"},
            {"path": "missing, source.py"},
            {**source, "blob": "b" * 40},
        ],
    )
    query, values = rows(project)
    expected = [source_line(row) for row in values]
    args = ["--root", str(root), "query", *(["--human"] if human else [])]
    result = CliRunner().invoke(main, args)
    assert result.exit_code == 0, result.output
    displayed = [line.lstrip("│ ") for line in result.stdout.split("\n") if "sources: " in line]
    assert displayed == (
        expected
        if human
        else ["sources: " + ", ".join(s.removeprefix("sources: ") for s in expected)]
    )
    assert len(displayed) == (6 if human else 1)
    text = "\n".join(displayed)
    assert '"extra, source.py":1 [ref+; file added]' in text
    assert '"missing, source.py" [ref+; missing]' in text
    assert "code.py:2,4 [ref+]" in text and "[ref+; unavailable]" in text
    assert sum(s.startswith("sources: code.py:2-3") for s in expected) == 2
    assert query.result["source_resolutions"] == read_query(root).result["source_resolutions"]
    if not human:
        assert text.count("sources: ") == 1


@pytest.mark.parametrize("human", [False, True])
@pytest.mark.parametrize("removed", ["reference", "node"])
def test_removed_and_deleted_sources_keep_base_locations_and_target_issues(project, human, removed):
    root, _, _, implementation, source = project
    update_node(root, implementation, sources=[source, source, {"path": "code.py"}])
    commit(root, "Multiple base source occurrences")
    if removed == "reference":
        update_node(root, implementation, sources=[])
    else:
        result = CliRunner().invoke(main, ["--root", str(root), "delete", implementation, "--yes"])
        assert result.exit_code == 0, result.output
    (root / "code.py").unlink()
    query, values = rows(project)
    expected = [source_line(row) for row in values]
    assert len(expected) == 3 and all("[ref-; target missing]" in item for item in expected)
    text = render_query(query, human=human)
    displayed = [line.lstrip("│ ") for line in text.split("\n") if "sources: " in line]
    assert displayed == (
        expected
        if human
        else ["sources: " + ", ".join(s.removeprefix("sources: ") for s in expected)]
    )
    assert sum("code.py:2-3" in item for item in expected) == 2
    assert any("code.py:1-5" in item for item in expected)
    if removed == "node":
        assert f"{implementation}mapping @" in text and "[deleted source-changed]" in text


def test_source_line_keeps_reference_changes_and_uncertainty_independent():
    good = {
        "path": "src/code.py",
        "ranges": [[4, 8]],
        "outcome": "resolved",
        "text_available": True,
        "mode": "strict",
    }
    row = {
        "declaration": "=",
        "base": good,
        "target": good,
        "contract": "same",
        "bytes": "same",
        "region": "same",
        "position": "same",
    }
    assert source_line(row) == "sources: src/code.py:4-8"
    assert source_line({**row, "declaration": "+"}).endswith(" [ref+]")
    assert source_line({**row, "bytes": "changed"}) == source_line(row)
    expanded = {**good, "mode": "expanding", "outcome": "modified"}
    assert source_line({**row, "target": expanded, "region": "modified"}) == source_line(row)
    renamed = {**good, "path": "src/renamed.py"}
    assert (
        source_line({**row, "target": renamed, "region": "relocated"})
        == "sources: src/renamed.py:4-8"
    )
    conflict = {**good, "outcome": "conflict", "text_available": False}
    assert (
        source_line({**row, "target": conflict, "contract": "changed"})
        == "sources: src/code.py [conflict]"
    )
    assert source_line({**row, "base": conflict, "contract": "changed"}).endswith(
        " [restored; base conflict]"
    )
    assert (
        source_line({**row, "base": conflict, "target": conflict})
        == "sources: src/code.py [conflict]"
    )
    assert (
        source_line({**row, "declaration": "-", "target": renamed})
        == "sources: src/code.py:4-8 [ref-]"
    )
    missing = {**good, "outcome": "missing", "text_available": False}
    assert source_line(
        {**row, "declaration": "-", "target": missing, "contract": "changed"}
    ).endswith(" [ref-; target missing]")
    file = {**good, "mode": "file", "outcome": "file", "text_available": False}
    assert source_line({**row, "base": file, "target": file}) == "sources: src/code.py"
    assert (
        source_line({**row, "base": missing, "target": file, "contract": "changed"})
        == "sources: src/code.py [file added]"
    )
    assert source_line({**row, "target": {**good, "ranges": []}}) == "sources: src/code.py:empty"
    assert source_line({**row, "target": {**good, "path": "src/a b.py"}}).startswith(
        'sources: "src/a b.py":4-8'
    )


@pytest.mark.parametrize("mode", ["strict", "expanding"])
@pytest.mark.parametrize("boundary", ["start", "end"])
def test_outer_boundary_insertions_are_permitted_without_source_badges(project, mode, boundary):
    root, _, _, implementation, source = project
    if mode != "strict":
        update_node(root, implementation, sources=[{**source, "mode": mode}])
        commit(root, "Boundary contract")
    code = (
        BASE.replace("alpha\n", "edge\nalpha\n")
        if boundary == "start"
        else BASE.replace("beta\n", "beta\nedge\n")
    )
    (root / "code.py").write_text(code, encoding="utf8")
    query, values = rows(project)
    assert values[0]["target"]["outcome"] == "resolved"
    assert values[0]["contract"] == "same" and "[" not in source_line(values[0])
    assert not query.result["source_contract_affected"] and "[source-changed]" not in render_query(
        query
    )


@pytest.mark.parametrize(
    "raw",
    [
        b"all new contents\n",
        b"binary\0contents",
        b"\xffinvalid",
        b"version https://git-lfs.github.com/spec/v1\n",
    ],
)
def test_whole_file_content_changes_are_permitted_even_without_line_targets(project, raw):
    root, _, _, implementation, _ = project
    update_node(root, implementation, sources=[{"path": "code.py"}])
    commit(root, "Path-only contract")
    (root / "code.py").write_bytes(raw)
    query, values = rows(project)
    assert values[0]["bytes"] == "changed" and values[0]["contract"] == "same"
    assert query.result["source_changes"]  # Retained raw evidence, not a query badge.
    assert not query.result["source_contract_affected"] and not query.result["affected"]
    assert "[" not in source_line(values[0]) and "[source-changed]" not in render_query(query)


def test_expanding_partial_deletion_is_permitted_but_total_loss_is_a_change(project):
    root, _, _, implementation, source = project
    update_node(root, implementation, sources=[{**source, "mode": "expanding"}])
    commit(root, "Expanding contract")
    (root / "code.py").write_text(BASE.replace("alpha\n", ""), encoding="utf8")
    query, values = rows(project)
    assert values[0]["target"]["outcome"] == "modified"
    assert values[0]["contract"] == "same" and not query.result["source_contract_affected"]
    assert "[" not in source_line(values[0])
    (root / "code.py").write_text(BASE.replace("alpha\nbeta\n", ""), encoding="utf8")
    query, values = rows(project)
    assert values[0]["target"]["outcome"] == "missing"
    assert (
        values[0]["contract"] == "changed"
        and implementation in query.result["source_contract_affected"]
    )
    assert source_line(values[0]).endswith(" [missing]")


def test_expanding_cross_boundary_replacement_remains_uncertain_not_a_fake_change(project):
    root, _, _, implementation, source = project
    update_node(root, implementation, sources=[{**source, "mode": "expanding"}])
    commit(root, "Expanding boundary contract")
    (root / "code.py").write_text("new block\nbeta\nafter\nend\n", encoding="utf8")
    query, values = rows(project)
    assert values[0]["target"]["outcome"] == "ambiguous"
    assert values[0]["contract"] == "unavailable"
    assert (
        not query.result["source_contract_complete"]
        and not query.result["source_contract_affected"]
    )
    assert source_line(values[0]).endswith(" [ambiguous]")


@pytest.mark.parametrize("mode", ["strict", "expanding", "file"])
def test_missing_links_change_once_and_restoration_is_reported(project, mode):
    root, manifesto, requirement, implementation, source = project
    source = {"path": "code.py"} if mode == "file" else {**source, "mode": mode}
    if mode != "strict":
        update_node(root, implementation, sources=[source])
        commit(root, "Selected contract")
    (root / "code.py").unlink()
    query, values = rows(project)
    assert values[0]["contract"] == "changed"
    assert set(query.result["source_contract_affected"]) == {manifesto, requirement, implementation}
    assert source_line(values[0]).endswith(" [missing]")
    commit(root, "Missing source")
    query, values = rows(project)
    assert values[0]["contract"] == "same" and not query.result["source_contract_affected"]
    assert source_line(values[0]).endswith(" [missing]")  # Existing issue remains visible.
    (root / "code.py").write_bytes(BASE.encode())
    query, values = rows(project)
    assert (
        values[0]["contract"] == "changed"
        and implementation in query.result["source_contract_affected"]
    )
    assert source_line(values[0]).endswith(" [file added]" if mode == "file" else " [restored]")


def test_preexisting_strict_conflict_is_not_a_new_change_and_can_be_restored(project):
    root, _, _, implementation, _ = project
    (root / "code.py").write_text(BASE.replace("alpha", "edited"), encoding="utf8")
    commit(root, "Existing conflict")
    query, values = rows(project)
    assert values[0]["base"]["outcome"] == values[0]["target"]["outcome"] == "conflict"
    assert values[0]["contract"] == "same" and not query.result["source_contract_affected"]
    assert source_line(values[0]).endswith(" [conflict]")
    (root / "code.py").write_text(BASE, encoding="utf8")
    query, values = rows(project)
    assert (
        values[0]["contract"] == "changed"
        and implementation in query.result["source_contract_affected"]
    )
    assert source_line(values[0]).endswith(" [restored; base conflict]")


def test_unknown_anchors_do_not_turn_ordinary_byte_changes_into_known_contract_changes(project):
    root, _, _, implementation, source = project
    update_node(root, implementation, sources=[{**source, "blob": "b" * 40}])
    commit(root, "Unavailable anchor")
    (root / "code.py").write_text("prefix\n" + BASE, encoding="utf8")
    query, values = rows(project)
    assert values[0]["bytes"] == "changed" and values[0]["contract"] == "unavailable"
    assert (
        not query.result["source_contract_complete"]
        and not query.result["source_contract_affected"]
    )
    assert source_line(values[0]).endswith(" [unavailable]")


def test_two_reference_classes_on_one_file_have_independent_semantics(project):
    root, _, _, implementation, source = project
    update_node(
        root, implementation, sources=[source, {**source, "mode": "expanding"}, {"path": "code.py"}]
    )
    commit(root, "Three reference classes")
    (root / "code.py").write_text(BASE.replace("alpha", "edited"), encoding="utf8")
    query, values = rows(project)
    by_mode = {r["target"]["mode"]: r for r in values}
    assert by_mode["strict"]["contract"] == "changed"
    assert by_mode["expanding"]["contract"] == by_mode["file"]["contract"] == "same"
    assert "[" not in source_line(by_mode["expanding"]) and "[" not in source_line(by_mode["file"])
    assert implementation in query.result["source_contract_affected"]


def test_contract_change_ancestors_use_both_original_graphs(project):
    root, manifesto, old_requirement, implementation, _ = project
    _, new_requirement = add_node(
        root, "requirement", [manifesto], "New behavior\n", "new-behavior"
    )
    update_node(root, implementation, parents=[new_requirement])
    (root / "code.py").write_text(BASE.replace("alpha", "edited"), encoding="utf8")
    query, values = rows(project)
    assert values[0]["contract"] == "changed"
    assert set(query.result["source_contract_affected"]) == {
        manifesto,
        old_requirement,
        new_requirement,
        implementation,
    }
    text = render_query(query)
    assert "[modified source-changed]" in text and "[added source-changed]" in text


def test_committed_source_blobs_are_batched_with_lazy_equivalent_facts(project, monkeypatch):
    root, _, _, implementation, source = project
    paths = [f"piece-{i}.py" for i in range(24)]
    for i, path in enumerate(paths):
        (root / path).write_text(f"unique piece {i}\n", encoding="utf8")
    update_node(
        root,
        implementation,
        sources=[source, source, {"path": "code.py"}, *[{"path": p} for p in paths]],
    )
    git(root, "add", ".")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Many linked files")
    (root / paths[0]).write_text("saved edit\n", encoding="utf8")
    (root / "code.py").write_text("prefix\n" + BASE, encoding="utf8")
    processes = Counter()
    original = subprocess.run

    def counted(command, *args, **kwargs):
        if "cat-file" in command:
            processes[command[-1]] += 1
        return original(command, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", counted)
    optimized = read_query(root)
    assert processes == {"--batch-check": 2, "--batch": 2}
    assert len(optimized.result["source_resolutions"]) == 27
    assert not optimized.result["source_contract_affected"]

    def anchors_only(version, references):
        if version.reader is not None:
            version.reader.batch({s["blob"] for s in references if "blob" in s})

    monkeypatch.setattr(CodeVersion, "batch", anchors_only)
    processes.clear()
    lazy = read_query(root)
    assert processes["--batch-check"] > 24 and processes["--batch"] > 24
    assert lazy.result == optimized.result
    for human in (False, True):
        assert render_query(lazy, human=human) == render_query(optimized, human=human)


def test_identical_selected_commits_reuse_one_invocation_local_code_reader(project, monkeypatch):
    root, _, _, _, _ = project
    calls = []
    original = SourceReader.__init__

    def counted(reader, *args, **kwargs):
        calls.append(kwargs.get("ref"))
        original(reader, *args, **kwargs)

    monkeypatch.setattr(SourceReader, "__init__", counted)
    query = read_query(root, "HEAD", "HEAD")
    assert calls == [query.result["base_commit"]]
    assert query.result["base_commit"] == query.result["target_commit"]
    assert all(r["contract"] == r["bytes"] == "same" for r in query.result["source_resolutions"])


def test_per_call_cache_reloads_same_size_same_mtime_saved_edits(project):
    root, _, _, _, _ = project
    before, values = rows(project)
    assert values[0]["contract"] == "same"
    path = root / "code.py"
    stamp = path.stat()
    path.write_bytes(BASE.replace("alpha", "ALPHA").encode())
    os.utime(path, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    assert path.stat().st_size == stamp.st_size
    after, values = rows(project)
    assert values[0]["contract"] == "changed"
    assert values[0]["target"]["outcome"] == "conflict"
    assert before.result["source_contract_affected"] != after.result["source_contract_affected"]


def test_workspace_prefetch_does_not_request_unrelated_index_blobs(project, monkeypatch):
    root, _, _, _, source = project
    path = root / "code.py"
    path.write_bytes(b"Different staged version\n")
    git(root, "add", "code.py")
    index_oid = git(root, "rev-parse", ":code.py").decode().strip()
    path.write_bytes(("prefix\n" + BASE).encode())
    requested = []
    original = SourceReader.batch

    def counted(reader, ids):
        if reader.ref is None:
            requested.extend(ids)
        return original(reader, ids)

    monkeypatch.setattr(SourceReader, "batch", counted)
    query, values = rows(project)
    assert index_oid not in requested and source["blob"] in requested
    assert values[0]["target"]["ranges"] == [[3, 4]]
    assert values[0]["contract"] == "same" and not query.result["source_contract_affected"]


def test_source_json_retains_complete_declarations_and_derived_readings(project):
    root, _, _, implementation, source = project
    result = CliRunner().invoke(main, ["--root", str(root), "query", "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)["result"]
    node = next(n for n in data["target"]["nodes"] if n["id"] == implementation)
    assert node["sources"] == [source]
    row = data["source_resolutions"][0]
    assert row["reference"] == source and row["base_source"] == row["target_source"] == 1
    assert row["base"]["ranges"] == row["target"]["ranges"] == [[2, 3]]
