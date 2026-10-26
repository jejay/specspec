"""Compact invocation outcomes, independent of Git status and JSON transport."""

import base64
import json
import re
from contextlib import contextmanager
from dataclasses import replace

import pytest
from click.testing import CliRunner
from test_git import git, setup_repository

from specspec import cli
from specspec import workspace as workspace_module
from specspec.output import action_lines, render_receipt
from specspec.workspace import add_node, initialize, load_snapshot, serialize, update_node

ACTIONS = re.compile(r"^(Added|Modified|Deleted|Unchanged|Would add|Would modify|Would delete):")
FINDINGS = {
    "graph_valid",
    "analysis_complete",
    "broken_references",
    "issue_ids",
    "potentially_affected",
    "unreadable_paths",
}
SINGLE_RECEIPT = {"changed_ids", "nodes", "affected", "applied"} | FINDINGS
BATCH_RECEIPT = SINGLE_RECEIPT | {"deleted_ids", "aliases", "deletion_plan"}


def invoke(root, *args, input=None):
    return CliRunner().invoke(cli.main, ["--root", str(root), *args], input=input)


def summaries(result):
    return [line for line in result.stdout.splitlines() if ACTIONS.match(line)]


def assert_compact(result):
    assert result.exit_code == 0, result.output
    assert all(line == line.lstrip() and "\t" not in line for line in result.stdout.splitlines())
    assert ".specspec/" not in result.stdout and ".md" not in "\n".join(summaries(result))
    assert not any(
        line.startswith(("Changed:", "Planned:", "Initialized:"))
        for line in result.stdout.splitlines()
    )


def available_ids(root, count, monkeypatch):
    used = {node.id.casefold() for node in load_snapshot(root).nodes}
    values = []
    number = 0
    while len(values) < count:
        raw = number.to_bytes(5, "big")
        number += 1
        if base64.urlsafe_b64encode(raw).decode().casefold() not in used:
            values.append(raw)
    tokens = iter(values)
    monkeypatch.setattr(workspace_module.secrets, "token_bytes", lambda size: next(tokens))
    return [base64.urlsafe_b64encode(raw).decode() for raw in values]


@pytest.mark.parametrize("existing_guide", [False, True])
def test_init_adds_the_first_node_once_without_a_storage_path(tmp_path, existing_guide):
    if existing_guide:
        (tmp_path / "AGENTS.md").write_text("Owner instructions", encoding="utf8")
    result = invoke(tmp_path, "init", "-m", "Here we go")
    node = load_snapshot(tmp_path).nodes[0]
    assert_compact(result)
    assert summaries(result) == [f"Added: {node.id}"]
    assert result.stdout.count(node.id) == 1
    status = "existing entry preserved" if existing_guide else "created"
    assert f"Agent instructions: AGENTS.md ({status})" in result.stdout
    assert "Affected: 1 nodes" in result.stdout


@pytest.mark.parametrize("dry_run", [False, True])
@pytest.mark.parametrize("node_type", ["requirement", "implementation"])
def test_add_receipt_identifies_the_action_not_the_file(workspace, dry_run, node_type):
    root, manifesto = workspace
    _, parent = add_node(root, "requirement", [manifesto], "# Parent\n")
    before = load_snapshot(root).files
    args = ["add", "--parent", parent, "--type", node_type, "-m", "# New 🐕"]
    result = invoke(root, *args, *(["--dry-run"] if dry_run else []))
    assert_compact(result)
    (line,) = summaries(result)
    label = "Would add" if dry_run else "Added"
    assert line.startswith(label + ": ") and len(line.removeprefix(label + ": ")) == 8
    node_id = line.removeprefix(label + ": ")
    assert result.stdout.count(node_id) == 1
    after = load_snapshot(root)
    if dry_run:
        assert after.files == before and node_id not in after.graph.nodes
    else:
        assert after.graph.nodes[node_id].type == node_type


@pytest.mark.parametrize("dry_run", [False, True])
@pytest.mark.parametrize("changed", [False, True])
@pytest.mark.parametrize("field", ["body", "parents", "sources", "replacement"])
def test_update_classifies_actual_candidate_bytes(workspace, dry_run, changed, field):
    root, manifesto = workspace
    _, parent = add_node(root, "requirement", [manifesto], "# Parent\n")
    _, peer = add_node(root, "requirement", [manifesto], "# Peer\n")
    node_type = "implementation" if field == "sources" else "requirement"
    before, target = add_node(root, node_type, [parent], "# Original\n")
    node = before.graph.nodes[target]
    if field == "body":
        args = ["-m", "# Updated 🐕\n" if changed else node.body]
    elif field == "parents":
        args = ["--parent", peer if changed else parent]
    elif field == "sources":
        (root / "implementation.py").write_text("# Code\n", encoding="utf8")
        args = ["--sources", json.dumps([{"path": "implementation.py"}] if changed else [])]
    else:
        args = ["--replace", "Original", "Updated" if changed else "Original"]
    result = invoke(root, "update", target, *args, *(["--dry-run"] if dry_run else []))
    assert_compact(result)
    label = ("Would modify" if dry_run else "Modified") if changed else "Unchanged"
    assert summaries(result) == [f"{label}: {target}"]
    assert result.stdout.count(target) == 1
    saved = load_snapshot(root)
    if dry_run or not changed:
        assert saved.files == before.files
    else:
        assert saved.files[node.path] != before.files[node.path]


def test_newline_encoding_does_not_make_a_noop_modified(workspace):
    root, manifesto = workspace
    before, target = add_node(root, "requirement", [manifesto], "# Same\n")
    path = root / f".specspec/{target}.md"
    raw = before.files[f".specspec/{target}.md"].replace(b"\n", b"\r\n")
    path.write_bytes(raw)
    result = invoke(root, "update", target, "-m", "# Same\n")
    assert_compact(result)
    assert summaries(result) == [f"Unchanged: {target}"]
    assert path.read_bytes() == raw


@pytest.mark.parametrize("dry_run", [False, True])
def test_mixed_invocation_groups_each_action_without_padding(workspace, monkeypatch, dry_run):
    root, manifesto = workspace
    ids = [add_node(root, "requirement", [manifesto], f"# Node {n}\n")[1] for n in range(5)]
    deleted_one, deleted_two, modified_one, modified_two, unchanged = ids
    before = load_snapshot(root)
    added_one, added_two = available_ids(root, 2, monkeypatch)
    result = invoke(
        root,
        "delete",
        deleted_two,
        "update",
        modified_two,
        "-m",
        "# Updated second\n",
        "add",
        "--parent",
        manifesto,
        "-m",
        "# New first\n",
        "update",
        unchanged,
        "-m",
        before.graph.nodes[unchanged].body,
        "delete",
        deleted_one,
        "add",
        "--parent",
        manifesto,
        "-m",
        "# New second\n",
        "update",
        modified_one,
        "-m",
        "# Updated first\n",
        "--yes",
        "--require-valid",
        *(["--dry-run"] if dry_run else []),
    )
    assert_compact(result)
    labels = (
        ["Would add", "Would modify", "Would delete"]
        if dry_run
        else ["Added", "Modified", "Deleted"]
    )
    assert summaries(result) == [
        f"{labels[0]}: {added_one}, {added_two}",
        f"{labels[1]}: {modified_two}, {modified_one}",
        f"{labels[2]}: {deleted_two}, {deleted_one}",
        f"Unchanged: {unchanged}",
    ]
    assert all(result.stdout.count(id) == 1 for id in [*ids, added_one, added_two])
    if dry_run:
        assert load_snapshot(root).files == before.files
    else:
        assert set(load_snapshot(root).graph.nodes) == (
            set(before.graph.nodes) - {deleted_one, deleted_two}
        ) | {added_one, added_two}


@pytest.mark.parametrize("dry_run", [False, True])
def test_alias_mappings_remain_explicit_on_one_unpadded_line(workspace, monkeypatch, dry_run):
    root, parent = workspace
    first, second = available_ids(root, 2, monkeypatch)
    result = invoke(
        root,
        "add",
        "--as",
        "z",
        "--parent",
        parent,
        "-m",
        "# Z",
        "add",
        "--as",
        "a",
        "--parent",
        "$z",
        "-m",
        "# A",
        *(["--dry-run"] if dry_run else []),
    )
    assert_compact(result)
    assert summaries(result) == [f"{'Would add' if dry_run else 'Added'}: {first}, {second}"]
    assert f"Aliases: $a -> {second}, $z -> {first}" in result.stdout.splitlines()


@pytest.mark.parametrize("preview", [False, True])
def test_standalone_deletion_groups_ids_and_retains_structural_context(workspace, preview):
    root, parent = workspace
    _, one = add_node(root, "requirement", [parent], "# One\n")
    _, two = add_node(root, "requirement", [parent], "# Two\n")
    before, survivor = add_node(root, "requirement", [one], "# Survivor\n")
    result = invoke(root, "delete", two, one, "--dry-run" if preview else "--yes")
    assert_compact(result)
    label = "Would delete" if preview else "Deleted"
    assert summaries(result) == [f"{label}: " + ", ".join(sorted([one, two]))]
    assert "INVALID" in result.stdout and survivor in result.stdout
    assert "warning:" in result.stderr
    if preview:
        assert "Descendants and their parent declarations remain." in result.stdout
        assert load_snapshot(root).files == before.files
    else:
        assert load_snapshot(root).graph.nodes[survivor].parents == [one]
        assert (
            load_snapshot(root).files[f".specspec/{survivor}.md"]
            == before.files[f".specspec/{survivor}.md"]
        )


def test_declined_noninteractive_deletion_only_reports_a_proposal(workspace):
    root, parent = workspace
    before, target = add_node(root, "requirement", [parent], "# Keep\n")
    result = invoke(root, "delete", target)
    assert result.exit_code == 1
    assert summaries(result) == [f"Would delete: {target}"]
    assert "DELETE_CONFIRMATION" in result.stderr
    assert load_snapshot(root).files == before.files


def test_rejected_candidate_does_not_print_completed_or_proposed_actions(workspace):
    root, parent = workspace
    before = load_snapshot(root).files
    for args in [
        ["add", "-m", "# Detached", "--require-valid"],
        ["update", parent, "--parent", parent, "--require-valid"],
        ["delete", parent, "--yes"],
    ]:
        result = invoke(root, *args)
        assert result.exit_code == 1 and not summaries(result), result.output
        assert load_snapshot(root).files == before


def test_receipts_describe_this_invocation_not_git_head(workspace):
    root, parent = workspace
    setup_repository(root)
    _, target = add_node(root, "requirement", [parent], "# Original\n")
    git(root, "add", ".specspec")
    assert git(root, "status", "--short").startswith(b"A ")
    result = invoke(root, "update", target, "-m", "# Updated\n")
    assert summaries(result) == [f"Modified: {target}"]
    result = invoke(root, "update", target, "-m", "# Updated\n")
    assert summaries(result) == [f"Unchanged: {target}"]
    assert git(root, "status", "--short").startswith(b"AM")


def test_outcome_uses_the_fresh_locked_original(workspace, monkeypatch):
    root, parent = workspace
    before, target = add_node(root, "requirement", [parent], "# Earlier\n")
    node = before.graph.nodes[target]
    latest = serialize(replace(node, body="# Latest\n"), before.files[node.path])
    original_lock = workspace_module.workspace_lock

    @contextmanager
    def lock_with_newer_saved_bytes(project, **kwargs):
        with original_lock(project, **kwargs) as state:
            (root / node.path).write_bytes(latest)
            yield state

    monkeypatch.setattr(workspace_module, "workspace_lock", lock_with_newer_saved_bytes)
    result = invoke(root, "update", target, "-m", "# Latest\n")
    assert summaries(result) == [f"Unchanged: {target}"]
    assert (root / node.path).read_bytes() == latest


def test_formatting_does_not_reread_files_after_the_transaction(workspace, monkeypatch):
    root, parent = workspace
    before, target = add_node(root, "requirement", [parent], "# Original\n")
    original_output = cli.mutation_output
    path = f".specspec/{target}.md"

    def output_after_external_change(snapshot, ids, as_json):
        (root / path).write_bytes(before.files[path])
        return original_output(snapshot, ids, as_json)

    monkeypatch.setattr(cli, "mutation_output", output_after_external_change)
    result = invoke(root, "update", target, "-m", "# Updated\n")
    assert summaries(result) == [f"Modified: {target}"]
    assert (root / path).read_bytes() == before.files[path]


def test_outcome_metadata_is_transient_and_not_in_snapshot_serialization(tmp_path):
    initial = initialize(tmp_path, "# Product\n")
    parent = initial.nodes[0].id
    assert initial.mutation_actions == {"added": [parent]}
    added, target = add_node(tmp_path, "requirement", [parent], "# Child\n")
    assert added.mutation_actions == {"added": [target]}
    same = update_node(tmp_path, target, body="# Child\n")
    assert same.mutation_actions == {"unchanged": [target]}
    changed = update_node(tmp_path, target, body="# Updated\n")
    assert changed.mutation_actions == {"modified": [target]}
    assert load_snapshot(tmp_path).mutation_actions is None
    for snapshot in [initial, added, same, changed]:
        assert "mutation_actions" not in snapshot.to_dict()
        assert not any(b"mutation_actions" in raw for raw in snapshot.files.values())


@pytest.mark.parametrize(
    "operation", ["init", "add", "update", "noop", "replace", "delete", "preview", "chain"]
)
def test_json_receipt_keys_and_id_path_records_are_unchanged(tmp_path, operation):
    if operation == "init":
        args = ["init", "-m", "# Product"]
        expected = SINGLE_RECEIPT | {"agent_instructions"}
    else:
        initial = initialize(tmp_path, "# Product\n")
        parent = initial.nodes[0].id
        _, target = add_node(tmp_path, "requirement", [parent], "# Child\n")
        expected = SINGLE_RECEIPT
        args = {
            "add": ["add", "--parent", parent, "-m", "# Added"],
            "update": ["update", target, "-m", "# Updated"],
            "noop": ["update", target, "-m", "# Child\n"],
            "replace": ["update", target, "--replace", "Child", "Updated"],
            "delete": ["delete", target, "--yes"],
            "preview": ["update", target, "-m", "# Preview", "--dry-run"],
            "chain": [
                "update",
                target,
                "-m",
                "# Child\n",
                "add",
                "--as",
                "new",
                "--parent",
                parent,
                "-m",
                "# Added",
            ],
        }[operation]
        if operation in {"replace", "preview", "chain"}:
            expected = BATCH_RECEIPT
        if operation == "delete":
            expected |= {"requested_ids", "deleted_ids", "uncommitted", "git_available", "git_note"}
    result = invoke(tmp_path, *args, "--json")
    assert result.exit_code == 0, result.output
    envelope = json.loads(result.stdout)
    assert set(envelope) == {"api_version", "ok", "result", "diagnostics"}
    assert envelope["api_version"] == 7 and envelope["ok"]
    receipt = envelope["result"]
    assert set(receipt) == expected
    assert receipt["changed_ids"] == [node["id"] for node in receipt["nodes"]]
    assert all(
        node == {"id": node["id"], "path": f".specspec/{node['id']}.md"}
        for node in receipt["nodes"]
    )
    assert receipt["applied"] == (operation != "preview")
    assert "mutation_actions" not in result.stdout


def test_renderer_keeps_completeness_and_alias_context_without_padding():
    result = {
        "affected": ["AAAAAAA="],
        "applied": False,
        "analysis_complete": False,
        "graph_valid": False,
        "aliases": {"goal": "AAAAAAA="},
        "broken_references": [{"parent": "AAAAAAE=", "child": "AAAAAAA=", "reason": "missing"}],
    }
    output = render_receipt(result, {"added": ["AAAAAAA="]}, dry_run=True)
    assert output.splitlines()[0] == "Would add: AAAAAAA="
    assert "Aliases: $goal -> AAAAAAA=" in output
    assert "Proposed graph is INVALID" in output
    assert "Analysis incomplete" in output
    assert "Unresolved: AAAAAAE= -> AAAAAAA= (missing)" in output
    assert all(line == line.lstrip() for line in output.splitlines())
    assert action_lines({}, dry_run=False) == []
