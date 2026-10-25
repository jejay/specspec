"""Explicit edits, broken-justification evidence and safe repair of invalid workspaces."""

import json
from pathlib import Path

from click.testing import CliRunner
from test_git import git, setup_repository

from specspec.cli import main
from specspec.inspection import findings
from specspec.model import API_VERSION
from specspec.wire import expand_comparison
from specspec.workspace import add_node, delete_nodes, load_snapshot, recover, update_node


def call(root, *args, input=None):
    suffix = [] if args[0] == "api" else ["--json"]
    result = CliRunner().invoke(main, ["--root", str(root), *args, *suffix], input=input)
    return result, json.loads(result.stdout)


def branch(workspace):
    root, manifesto = workspace
    _, a = add_node(root, "requirement", [manifesto], "# Assumption A\n")
    _, b = add_node(root, "requirement", [manifesto], "# Assumption B\n")
    _, c = add_node(root, "requirement", [a, b], "# Joint conclusion C\n")
    _, d = add_node(root, "requirement", [c], "# Further conclusion D\n")
    _, e = add_node(root, "requirement", [a], "# Exclusive conclusion E\n")
    setup_repository(root)
    return root, manifesto, a, b, c, d, e


def test_parent_only_deletion_preserves_all_survivor_bytes_and_declarations(workspace):
    root, manifesto, a, b, c, d, e = branch(workspace)
    before = load_snapshot(root)
    result, preview = call(root, "delete", a, "--dry-run")
    assert result.exit_code == 0 and preview["ok"]
    plan = preview["result"]
    assert plan["deleted_ids"] == [a]
    assert set(plan["potentially_affected"]) == {c, d, e}
    assert {(r["parent"], r["child"]) for r in plan["broken_references"]} == {(a, c), (a, e)}
    assert not plan["graph_valid"] and plan["analysis_complete"]
    result, receipt = call(root, "delete", a)
    assert result.exit_code == 0 and receipt["ok"] and receipt["result"]["applied"]
    after = load_snapshot(root)
    assert not after.valid and after.complete
    assert after.files == {p: raw for p, raw in before.files.items() if p != f"_specspec/{a}.md"}
    assert next(n for n in after.nodes if n.id == c).parents == [a, b]
    assert set(after.graph.nodes) == {manifesto, b, c, d, e}
    assert not (root / ".specspec-local/journal.json").exists()
    assert call(root, "check")[0].exit_code == 1


def test_show_query_context_and_declared_diff_work_while_invalid(workspace):
    root, manifesto, a, b, c, d, e = branch(workspace)
    delete_nodes(root, [a])
    for args in [
        ("show", b),
        ("show", c, "--dependents"),
        ("show",),
        ("query",),
        ("query", c, "--max-distance", "0", "--with-ancestors"),
    ]:
        result, data = call(root, *args)
        assert result.exit_code == 0 and data["ok"], result.output
    result, delta = call(root, "diff", "--with-context")
    assert result.exit_code == 0 and delta["ok"]
    delta = expand_comparison(delta["result"])
    assert delta["changes"] == [{"id": a, "kind": "removed", "fields": []}]
    assert [a, c] not in delta["removed_edges"]  # C still declares A.
    assert [manifesto, a] in delta["removed_edges"]
    context = delta["context"]
    records = {r["id"]: r for r in context["records"]}
    assert records[a]["before"]["body"] == "# Assumption A\n"
    assert records[c]["unchanged"] and records[c]["surviving_parents"] == [b]
    assert any(w["path"] == [a, c, d] for w in context["cause_paths"])
    assert "owner intent" in context["interpretation"]
    assert {n["id"] for n in delta["target"]["nodes"]} == {manifesto, b, c, d, e}
    result, selection = call(root, "query", "--issues", "--with-ancestors")
    assert result.exit_code == 0
    assert {c, d, e} <= set(selection["result"]["selection"]["matched_ids"])
    result, scoped = call(root, "diff", "--with-context", "--node", c)
    assert result.exit_code == 0 and scoped["result"]["context"]["scope"] == [c]
    historical, data = call(root, "query", a, "--base", "HEAD", "--target", "HEAD")
    assert historical.exit_code == 0 and data["result"]["target"]["valid"]


def test_incremental_updates_and_optional_final_validity_are_separate(workspace):
    root, manifesto, a, b, c, d, e = branch(workspace)
    delete_nodes(root, [a])
    before = load_snapshot(root).files
    preview = CliRunner().invoke(
        main, ["--root", str(root), "update", b, "-m", "# Proposed only\n", "--dry-run"]
    )
    assert preview.exit_code == 0 and "Proposed graph is INVALID" in preview.stdout
    assert load_snapshot(root).files == before
    refused, data = call(root, "update", c, "--parent", b, "--require-valid")
    assert refused.exit_code == 1 and not data["ok"]
    assert load_snapshot(root).files == before
    changed, data = call(root, "update", c, "--parent", b)
    assert changed.exit_code == 0 and data["ok"] and not data["result"]["graph_valid"]
    repaired, data = call(root, "update", e, "--parent", b, "--require-valid")
    assert repaired.exit_code == 0 and data["result"]["graph_valid"]
    assert call(root, "check")[0].exit_code == 0
    assert not (root / ".specspec-local/journal.json").exists()


def test_batch_candidate_is_coherent_bounded_explicit_and_aliases_are_ephemeral(
    workspace, tmp_path
):
    root, manifesto, a, b, c, d, e = branch(workspace)
    delete_nodes(root, [a])
    before = load_snapshot(root).files
    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    (plan_dir / "c.md").write_text("# B-derived C\n", encoding="utf8", newline="\n")
    args = [
        "update",
        c,
        "--parent",
        b,
        "--body",
        str(plan_dir / "c.md"),
        "update",
        e,
        "--parent",
        b,
        "add",
        "--as",
        "piece",
        "--parent",
        b,
        "-m",
        "# New independent part\n",
        "update",
        d,
        "--parent",
        "$piece",
    ]
    result, preview = call(root, *args, "--dry-run", "--require-valid")
    assert result.exit_code == 0 and not preview["result"]["applied"]
    assert load_snapshot(root).files == before
    result, data = call(root, *args, "--require-valid")
    assert result.exit_code == 0 and data["result"]["graph_valid"]
    alias = data["result"]["aliases"]["piece"]
    saved = load_snapshot(root)
    assert saved.valid and saved.graph.nodes[d].parents == [alias]
    assert saved.graph.nodes[c].body == "# B-derived C\n"
    assert all(b"$piece" not in raw for raw in saved.files.values())
    assert not (root / ".specspec-local/journal.json").exists()
    before = saved.files
    for args in [
        ["update", c, "-m", "one", "delete", c],
        ["update", c, "-m", "one", "update", c, "--parent", b],
    ]:
        result, _ = call(root, *args)
        assert result.exit_code == 2 and load_snapshot(root).files == before


def test_batch_deletion_consent_is_not_waived_by_invalid_editing(workspace):
    root, manifesto = workspace
    _, child = add_node(root, "requirement", [manifesto], "# New\n")
    args = ["delete", child, "update", manifesto, "-m", "# Still the product intention\n"]
    before = load_snapshot(root).files
    refused, data = call(root, *args)
    assert refused.exit_code == 1 and not data["ok"] and load_snapshot(root).files == before
    allowed, data = call(root, *args, "--yes")
    assert allowed.exit_code == 0 and data["result"]["deleted_ids"] == [child]
    assert "DELETE_GIT_UNAVAILABLE" in allowed.stderr


def test_cycles_are_finite_and_explicit_metrics_do_not_invent_longest_paths(workspace):
    root, manifesto, a, b, c, d, e = branch(workspace)
    update_node(root, a, parents=[c])
    result, data = call(root, "query")
    assert result.exit_code == 0 and data["ok"] and not data["result"]["target"]["valid"]
    result = CliRunner().invoke(main, ["--root", str(root), "query"])
    assert result.exit_code == 0 and result.stdout.count("# Joint conclusion C") == 1
    for args in [("--min-distance", "2"), ("--influence", "1")]:
        assert call(root, "query", c, *args)[0].exit_code == 0
    result, data = call(root, "query", c, "--max-distance", "2")
    assert result.exit_code == 1 and data["diagnostics"][0]["code"] == "METRIC"
    result, data = call(root, "query", d, "--max-distance", "0")
    assert result.exit_code == 0 and data["result"]["selection"]["ids"] == [d]


def test_unreadable_file_is_not_mislabeled_as_deletion_and_unrelated_edits_work(workspace):
    root, manifesto, a, b, c, d, e = branch(workspace)
    file = root / f"_specspec/{a}.md"
    file.write_text("not frontmatter\n", encoding="utf8", newline="\n")
    assert not load_snapshot(root).complete
    assert findings(load_snapshot(root))["broken_references"][0]["reason"] == "unreadable"
    result, data = call(root, "show", a, "--raw")
    assert result.exit_code == 0 and data["result"]["text"] == "not frontmatter\n"
    assert call(root, "show", b)[0].exit_code == 0
    assert call(root, "update", b, "--body", "-", input="# Still editable\n")[0].exit_code == 0
    result, data = call(root, "diff", "--with-context")
    assert result.exit_code == 1 and data["result"]
    assert next(n for n in data["result"]["changes"] if n["id"] == a)["kind"] == "unavailable"
    assert file.read_text(encoding="utf8") == "not frontmatter\n"
    assert call(root, "show", "--raw", "--path", "../README.md")[0].exit_code == 2


def test_absent_history_and_committed_dangling_references_remain_honest(workspace):
    root, manifesto, a, b, c, d, e = branch(workspace)
    delete_nodes(root, [a])
    git(root, "add", "-u", "_specspec")
    assert call(root, "check", "--staged")[0].exit_code == 1
    git(
        root,
        "-c",
        "core.hooksPath=/dev/null",
        "commit",
        "-m",
        "Intentional invalid working fixture",
    )
    assert call(root, "query")[0].exit_code == 0
    result, data = call(root, "diff", "--with-context")
    assert result.exit_code == 0 and not data["result"]["changes"]
    assert a in data["result"]["context"]["unavailable_ids"]
    result, data = call(root, "diff", "HEAD~1", "--with-context")
    assert result.exit_code == 0 and any(
        r["id"] == a and r.get("before") for r in data["result"]["context"]["records"]
    )


def test_spotlights_can_describe_invalid_comparisons(workspace):
    root, manifesto, a, b, c, d, e = branch(workspace)
    delete_nodes(root, [a])
    result, data = call(root, "spotlight", "add", a, c, "Keep the B-derived part")
    assert result.exit_code == 0 and data["ok"]
    result, data = call(root, "spotlight", "show")
    assert result.exit_code == 0
    assert data["result"]["shots"][0]["message"] == "Keep the B-derived part"


def test_spotlight_drift_tracks_unreadable_file_bytes_instead_of_fabricating_deletion(workspace):
    root, manifesto, a, b, c, d, e = branch(workspace)
    path = root / f"_specspec/{c}.md"
    path.write_bytes(b"First unreadable current file\n")
    result, data = call(root, "spotlight", "add", c, "Explain this unfinished edit")
    assert result.exit_code == 0
    checksum = data["result"]["shots"][0]["workspace"]["changes"][c]
    assert isinstance(checksum, str) and len(checksum) == 64
    path.write_bytes(b"Second unreadable current file\n")
    result, data = call(root, "spotlight", "show")
    shot = data["result"]["shots"][0]
    assert result.exit_code == 0 and shot["members"][0]["kind"] == "unavailable"
    assert any("Workspace nodes changed" in w for w in shot["warnings"])


def test_unreadable_uncommitted_identity_can_receive_a_message_without_inventing_a_binding(
    workspace,
):
    root, manifesto = workspace
    (root / f"_specspec/{manifesto}.md").write_bytes(b"Unfinished raw document\n")
    result, data = call(root, "spotlight", "add", manifesto, "Please repair this document")
    assert result.exit_code == 0 and data["result"]["shots"][0]["nodes"] == [manifesto]
    result, data = call(root, "spotlight", "show")
    assert (
        result.exit_code == 0 and data["result"]["shots"][0]["members"][0]["kind"] == "unavailable"
    )


def test_recovery_restores_invalid_original_and_preserves_external_intervention(
    workspace, monkeypatch
):
    root, manifesto, a, b, c, d, e = branch(workspace)
    delete_nodes(root, [a])
    before = load_snapshot(root).files
    import specspec.workspace as module

    original = module.os.replace
    count = 0

    def interrupt(source, target):
        nonlocal count
        if Path(target).parent == root / "_specspec":
            count += 1
            if count == 2:
                raise OSError("Interrupted invalid repair")
        return original(source, target)

    monkeypatch.setattr(module.os, "replace", interrupt)
    result, _ = call(
        root, "update", c, "--parent", b, "update", e, "--parent", b, "--require-valid"
    )
    assert result.exit_code == 2 and (root / ".specspec-local/journal.json").exists()
    monkeypatch.setattr(module.os, "replace", original)
    recovered = recover(root)
    assert not recovered["graph_valid"] and load_snapshot(root).files == before
    assert not (root / ".specspec-local/journal.json").exists()


def test_mutation_safety_does_not_depend_on_graph_validity(workspace, monkeypatch):
    import pytest

    from specspec.model import SpecError
    from specspec.workspace import mutate

    root, manifesto, a, b, c, d, e = branch(workspace)
    delete_nodes(root, [a])
    before = load_snapshot(root).files
    for path, raw in [
        ("../outside.md", b"bad"),
        ("_specspec/nested/no.md", b"bad"),
        (f"_specspec/{b}.md", b"bad"),
    ]:
        with pytest.raises(SpecError):
            mutate(root, lambda snapshot, path=path, raw=raw: {path: raw})
        assert load_snapshot(root).files == before
        assert not (root / ".specspec-local/journal.json").exists()
    with pytest.raises(SpecError, match="manifesto"):
        mutate(root, lambda snapshot: {f"_specspec/{manifesto}.md": None})
    from specspec.batch import prepare

    bad = {"edits": [{"op": "add", "type": [], "body": "# X", "parents": [b]}]}
    with pytest.raises(SpecError, match="requirement/implementation"):
        prepare(bad)
    import base64
    import secrets

    import specspec.workspace as module

    fresh = secrets.token_bytes(5)
    while base64.urlsafe_b64encode(fresh).decode().casefold() in {
        n.id.casefold() for n in load_snapshot(root).nodes
    } | {a.casefold()}:
        fresh = secrets.token_bytes(5)
    tokens = iter([base64.urlsafe_b64decode(a), fresh])
    monkeypatch.setattr(module.secrets, "token_bytes", lambda n: next(tokens))
    after, id = add_node(root, "requirement", [b], "# Independent new conclusion\n")
    assert id != a and not after.valid
    assert any(r["parent"] == a for r in findings(after)["broken_references"])


def test_context_and_canonical_hunks_share_one_current_snapshot(workspace, monkeypatch):
    import specspec.application as application

    root, manifesto, a, b, c, d, e = branch(workspace)
    delete_nodes(root, [a])
    calls, original = [], application.load_snapshot

    def counted(root):
        calls.append(root)
        return original(root)

    monkeypatch.setattr(application, "load_snapshot", counted)
    assert call(root, "diff", "--with-context")[0].exit_code == 0
    assert calls == [root]


def test_non_git_context_retains_evidence_without_inventing_owner_changes(workspace):
    root, manifesto = workspace
    _, child = add_node(root, "requirement", [manifesto], "# Current conclusion\n")
    result, data = call(root, "diff", "--with-context")
    assert result.exit_code == 1 and not data["ok"] and data["result"]
    assert data["result"]["target"]["valid"]
    assert not data["result"]["context"]["comparison_available"]
    assert not data["result"]["context"]["complete"]
    assert {n["id"] for n in data["result"]["context"]["records"]} == {manifesto, child}
    assert all(c["kind"] == "unavailable" for c in data["result"]["changes"])
    assert any(d["code"] == "GIT_CONTEXT" for d in data["diagnostics"])


def test_api6_is_rejected_and_context_budget_is_exact(workspace):
    root, manifesto, a, b, c, d, e = branch(workspace)
    assert API_VERSION == 7
    result, data = call(root, "api", input='{"api_version":6,"op":"read"}')
    assert result.exit_code == 2 and not data["ok"]
    delete_nodes(root, [a])
    result, data = call(root, "diff", "--with-context")
    exact = len(result.stdout.encode("utf8"))
    assert call(root, "diff", "--with-context", "--max-bytes", str(exact))[0].exit_code == 0
    result, data = call(root, "diff", "--with-context", "--max-bytes", str(exact - 1))
    assert result.exit_code == 1 and data["result"] is None
