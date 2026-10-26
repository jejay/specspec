"""One ordinary editing vocabulary, preflighted into one recoverable candidate."""

import base64
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from specspec import cli, edit_cli
from specspec.workspace import add_node, initialize, load_snapshot, recover


def invoke(root, *args, input=None):
    return CliRunner().invoke(cli.main, ["--root", str(root), *args], input=input)


def call(root, *args, input=None):
    result = invoke(root, *args, "--json", input=input)
    assert result.stdout, (result.output, result.exception)
    return result, json.loads(result.stdout)


@pytest.mark.parametrize("command", ["add", "update", "delete"])
def test_editing_options_retain_click_shell_completion(command):
    result = CliRunner().invoke(
        cli.main,
        [],
        prog_name="specspec",
        env={
            "_SPECSPEC_COMPLETE": "bash_complete",
            "COMP_WORDS": f"specspec {command} --dry",
            "COMP_CWORD": "2",
        },
    )
    assert result.exit_code == 0 and "--dry-run" in result.stdout


def test_non_utf8_arguments_are_rejected_without_an_unhandled_exception(workspace):
    root, parent = workspace
    before = load_snapshot(root).files
    result = invoke(root, "add", "--parent", parent, "-m", "\ud800")
    assert result.exit_code == 2 and "valid UTF-8" in result.stderr
    assert load_snapshot(root).files == before


def test_delete_add_add_update_with_shared_aliases_is_one_transaction(workspace, monkeypatch):
    import specspec.workspace as workspace_module

    root, manifesto = workspace
    _, old = add_node(root, "requirement", [manifesto], "# Old\n")
    _, peer = add_node(root, "requirement", [manifesto], "# Peer\n")
    _, survivor = add_node(root, "requirement", [old, peer], "# Retained\r\n")
    journals, original = [], workspace_module.write_journal

    def journal(state, value):
        journals.append(value)
        return original(state, value)

    monkeypatch.setattr(workspace_module, "write_journal", journal)
    result, data = call(
        root,
        "delete",
        old,
        "--require-valid",
        "add",
        "--as",
        "goal",
        "--parent",
        manifesto,
        "-m",
        "# Replacement\r\n",
        "add",
        "--as",
        "detail",
        "--parent",
        "$goal",
        "-m",
        "# Detail\n",
        "update",
        survivor,
        "--parent",
        "$goal",
        "--parent",
        peer,
        "--yes",
    )
    assert result.exit_code == 0 and data["ok"], result.output
    receipt = data["result"]
    aliases, saved = receipt["aliases"], load_snapshot(root)
    assert receipt["applied"] and receipt["graph_valid"] and saved.valid
    assert set(aliases) == {"goal", "detail"}
    assert receipt["changed_ids"] == [old, aliases["goal"], aliases["detail"], survivor]
    assert receipt["deleted_ids"] == [old]
    assert receipt["deletion_plan"]["deleted_ids"] == [old]
    # The deletion-only assessment is distinct from the complete repaired candidate.
    assert not receipt["deletion_plan"]["graph_valid"]
    assert saved.graph.nodes[survivor].parents == [aliases["goal"], peer]
    assert saved.graph.nodes[survivor].body == "# Retained\r\n"
    assert saved.graph.nodes[aliases["detail"]].parents == [aliases["goal"]]
    assert all(b"$goal" not in raw for raw in saved.files.values())
    assert len(journals) == 1 and len(journals[0]["files"]) == 4
    assert not (root / f".specspec/{old}.md").exists()
    assert not (root / ".specspec-local/journal.json").exists()


@pytest.mark.parametrize("flag_position", ["early", "late"])
def test_invocation_flags_apply_to_every_step(workspace, flag_position):
    root, parent = workspace
    before = load_snapshot(root).files
    flags = ["--dry-run", "--require-valid", "--json"]
    args = ["add", "--as", "child", "--parent", "$goal", "-m", "# Child"]
    if flag_position == "early":
        args += flags
    args += ["add", "--as", "goal", "--parent", parent, "-m", "# Goal"]
    if flag_position == "late":
        args += flags
    result = invoke(root, *args)
    assert result.exit_code == 0, result.output
    receipt = json.loads(result.stdout)["result"]
    assert not receipt["applied"] and receipt["graph_valid"]
    assert set(receipt["aliases"]) == {"child", "goal"}
    assert load_snapshot(root).files == before


@pytest.mark.parametrize("name", ["add", "update", "delete", "show", "query", "init", "api"])
@pytest.mark.parametrize("form", ["separate", "equals", "short-attached"])
def test_command_words_as_message_values_are_not_boundaries(workspace, name, form):
    root, parent = workspace
    message = (
        ["-m", name]
        if form == "separate"
        else ["--message=" + name]
        if form == "equals"
        else ["-m" + name]
    )
    result, data = call(
        root,
        "add",
        "--as",
        "show",
        "--parent",
        parent,
        *message,
        "add",
        "--parent",
        "$show",
        "-m",
        "--json",
        "--require-valid",
    )
    assert result.exit_code == 0, result.output
    saved = load_snapshot(root)
    assert saved.graph.nodes[data["result"]["aliases"]["show"]].body == name
    detail = data["result"]["changed_ids"][1]
    assert saved.graph.nodes[detail].body == "--json"


@pytest.mark.parametrize(
    "command", ["show", "query", "check", "diff", "init", "sources", "spotlight", "recover", "api"]
)
def test_non_editing_commands_are_rejected_before_input_reads(workspace, monkeypatch, command):
    root, id = workspace
    before = load_snapshot(root).files

    def forbidden(path):
        pytest.fail("A rejected mixed invocation must not read any body source.")

    monkeypatch.setattr(cli, "read_body", forbidden)
    result = invoke(root, "update", id, "--body", "-", command, "delete", id)
    assert result.exit_code == 2
    assert (
        "unexpected extra argument" if command == "show" else "Only add, update and delete"
    ) in result.stderr
    assert load_snapshot(root).files == before


@pytest.mark.parametrize(
    "suffix",
    [
        ["add", "--type", "not-a-type", "-m", "# X"],
        ["update"],
        ["add", "--unknown-option"],
        ["add", "-m", "# X", "unexpected-positional"],
    ],
)
def test_later_syntax_errors_do_not_read_or_commit_earlier_steps(workspace, monkeypatch, suffix):
    root, id = workspace
    before = load_snapshot(root).files
    monkeypatch.setattr(cli, "read_body", lambda path: pytest.fail("Preflight must finish first."))
    result = invoke(root, "update", id, "--body", "NEVER_OPEN.md", *suffix)
    assert result.exit_code == 2, result.output
    assert load_snapshot(root).files == before


def test_later_body_source_conflict_is_rejected_before_any_input_read(workspace, monkeypatch):
    root, id = workspace
    before = load_snapshot(root).files
    monkeypatch.setattr(cli, "read_body", lambda path: pytest.fail("Conflicts precede all reads."))
    result, data = call(
        root, "update", id, "--body", "-", "add", "--parent", id, "-m", "", "--body", "-"
    )
    assert result.exit_code == 2 and data["diagnostics"][0]["code"] == "ARGUMENT"
    assert load_snapshot(root).files == before


@pytest.mark.parametrize("alias", ["", "9bad", "$bad", "a" * 65])
def test_invalid_aliases_do_not_create_nodes(workspace, alias):
    root, id = workspace
    before = load_snapshot(root).files
    result, data = call(root, "add", "--as", alias, "--parent", id, "-m", "# X")
    assert result.exit_code == 2 and data["diagnostics"][0]["code"] == "BATCH"
    assert load_snapshot(root).files == before


def test_duplicate_and_unknown_aliases_and_new_node_reedits_are_rejected(workspace):
    root, id = workspace
    before = load_snapshot(root).files
    prefix = ["add", "--as", "new", "--parent", id, "-m", "# New"]
    for suffix in [
        ["add", "--as", "new", "--parent", id, "-m", "# Duplicate"],
        ["add", "--parent", "$unknown", "-m", "# Unknown"],
        ["update", "$new", "-m", "# Set these fields in add"],
        ["delete", "$new", "--yes"],
    ]:
        result, data = call(root, *prefix, *suffix)
        assert result.exit_code == 2 and data["diagnostics"][0]["code"] == "BATCH"
        assert load_snapshot(root).files == before


def test_whole_candidate_validity_rejects_every_change_without_a_journal(workspace):
    root, parent = workspace
    _, node = add_node(root, "requirement", [parent], "# Original\n")
    before = load_snapshot(root).files
    result, data = call(
        root,
        "add",
        "--as",
        "detail",
        "--parent",
        node,
        "-m",
        "# Descendant",
        "update",
        node,
        "--parent",
        "$detail",
        "--require-valid",
    )
    assert result.exit_code == 1 and not data["ok"]
    assert any(d["code"] == "CYCLE" for d in data["diagnostics"])
    assert load_snapshot(root).files == before
    assert not (root / ".specspec-local/journal.json").exists()
    # Without the optional boundary the same explicit cyclic candidate can be saved.
    result, data = call(
        root,
        "add",
        "--as",
        "detail",
        "--parent",
        node,
        "-m",
        "# Descendant",
        "update",
        node,
        "--parent",
        "$detail",
    )
    assert result.exit_code == 0 and data["result"]["applied"]
    assert not data["result"]["graph_valid"]


def test_multi_id_delete_stops_at_next_step_and_accepts_hyphen_ids(workspace, monkeypatch):
    import specspec.workspace as workspace_module

    root, parent = workspace
    ids = ["-AAAAAA=", "--AAAAA="]
    tokens = iter(base64.urlsafe_b64decode(id) for id in ids)
    monkeypatch.setattr(workspace_module.secrets, "token_bytes", lambda n: next(tokens))
    for id in ids:
        assert add_node(root, "requirement", [parent], "# Remove")[1] == id
    result, data = call(root, "delete", "--yes", "--", *ids, "update", parent, "-m", "# Intention")
    assert result.exit_code == 0, result.output
    assert set(data["result"]["deleted_ids"]) == set(ids)
    assert set(load_snapshot(root).graph.nodes) == {parent}


def test_selected_deletions_ask_once_for_the_whole_chain(workspace, monkeypatch):
    root, parent = workspace
    children = [add_node(root, "requirement", [parent], "# Remove")[1] for _ in range(2)]
    confirmations = []
    monkeypatch.setattr(cli, "interactive_stdin", lambda: True)
    monkeypatch.setattr(
        cli.click, "confirm", lambda message, **kw: confirmations.append(message) or True
    )
    result = invoke(root, "delete", children[0], "delete", children[1])
    assert result.exit_code == 0, result.output
    assert len(confirmations) == 1 and "2 selected files" in confirmations[0]
    assert set(load_snapshot(root).graph.nodes) == {parent}


def test_reviewed_plans_stay_single_delete_only_and_are_not_read_in_chains(workspace, monkeypatch):
    root, parent = workspace
    _, child = add_node(root, "requirement", [parent], "# Remove")
    before = load_snapshot(root).files
    monkeypatch.setattr(
        cli, "read_deletion_plan", lambda p: pytest.fail("Do not read reviewed plan.")
    )
    result, data = call(
        root, "delete", child, "--reviewed-plan", "-", "update", parent, "-m", "# Root"
    )
    assert result.exit_code == 2 and data["diagnostics"][0]["code"] == "ARGUMENT"
    assert load_snapshot(root).files == before


def test_hidden_body_files_and_one_stdin_body_can_join_a_chain(workspace, tmp_path):
    root, parent = workspace
    body = "# Literal\r\n\r\nUnicode 🐕 and trailing spaces.  \r\n"
    path = tmp_path / "body.md"
    path.write_bytes(body.encode("utf8"))
    result, data = call(
        root,
        "add",
        "--as",
        "file",
        "--parent",
        parent,
        "--body",
        str(path),
        "add",
        "--parent",
        "$file",
        "--body",
        "-",
        "--require-valid",
        input=body.encode("utf8"),
    )
    assert result.exit_code == 0, result.output
    saved = load_snapshot(root)
    assert all(saved.graph.nodes[id].body == body for id in data["result"]["changed_ids"])
    before = saved.files
    result, data = call(
        root,
        "update",
        parent,
        "--body",
        "-",
        "update",
        data["result"]["changed_ids"][0],
        "--body",
        "-",
    )
    assert result.exit_code == 2 and "one stdin body" in data["diagnostics"][0]["message"]
    assert load_snapshot(root).files == before


def test_bounded_argv_steps_and_aggregate_file_bodies(workspace, monkeypatch, tmp_path):
    import specspec.batch as batch

    root, parent = workspace
    before = load_snapshot(root).files
    args = ["add", "--parent", parent, "-m", "12345678"] * 2
    monkeypatch.setattr(edit_cli, "MAX_EDITS", 1)
    assert invoke(root, *args).exit_code == 2
    monkeypatch.setattr(edit_cli, "MAX_EDITS", 1024)
    monkeypatch.setattr(edit_cli, "MAX_BATCH_BYTES", 16)
    assert invoke(root, *args).exit_code == 2
    monkeypatch.setattr(edit_cli, "MAX_BATCH_BYTES", 16 * 1024 * 1024)
    monkeypatch.setattr(batch, "MAX_BATCH_BYTES", 15)
    path = tmp_path / "body.md"
    path.write_bytes(b"12345678")
    reads, original = [], cli.read_body

    def bounded_read(path):
        reads.append(path)
        assert len(reads) <= 2, "Stop loading once the aggregate budget is exceeded."
        return original(path)

    monkeypatch.setattr(cli, "read_body", bounded_read)
    args = ["add", "--parent", parent, "--body", str(path)] * 3
    result, data = call(root, *args)
    assert result.exit_code == 2 and "16 MiB" in data["diagnostics"][0]["message"]
    assert len(reads) == 2
    assert load_snapshot(root).files == before


def test_literal_bodies_charge_the_budget_before_body_file_reads(workspace, monkeypatch):
    import specspec.batch as batch

    root, parent = workspace
    before = load_snapshot(root).files
    monkeypatch.setattr(batch, "MAX_BATCH_BYTES", 15)
    monkeypatch.setattr(
        cli, "read_body", lambda path: pytest.fail("Inline bodies already exhaust budget.")
    )
    result, data = call(
        root,
        "add",
        "--parent",
        parent,
        "-m",
        "12345678",
        "add",
        "--parent",
        parent,
        "-m",
        "12345678",
        "add",
        "--parent",
        parent,
        "--body",
        "NEVER_OPEN.md",
    )
    assert result.exit_code == 2 and data["diagnostics"][0]["code"] == "BATCH"
    assert load_snapshot(root).files == before


@pytest.mark.parametrize("flag,code", [("--sources", "SOURCES"), ("--parents-json", "PARENTS")])
def test_malformed_integration_arrays_fail_preflight_without_reading_bodies(
    workspace, monkeypatch, flag, code
):
    root, parent = workspace
    before = load_snapshot(root).files
    monkeypatch.setattr(cli, "read_body", lambda path: pytest.fail("Finish field preflight first."))
    encoded = "[" * 2048 + "0" + "]" * 2048
    args = ["add", "-m", "# Node", flag, encoded]
    if flag == "--sources":
        args += ["--parent", parent]
    result, data = call(root, "update", parent, "--body", "-", *args)
    assert result.exit_code in {1, 2} and data["diagnostics"][0]["code"] == code
    assert load_snapshot(root).files == before


def test_source_fields_and_literal_alias_text_stay_associated_with_their_step(workspace):
    root, parent = workspace
    (root / "source.py").write_text("pass\n", encoding="utf8")
    sources = [{"path": "source.py", "symbol": "$goal remains descriptive"}]
    result, data = call(
        root,
        "add",
        "--as",
        "goal",
        "--parent",
        parent,
        "-m",
        "# Keep $goal literal",
        "add",
        "--as",
        "impl",
        "--type",
        "implementation",
        "--parent",
        "$goal",
        "--sources",
        json.dumps(sources),
        "-m",
        "# Implementation",
        "--require-valid",
    )
    assert result.exit_code == 0, result.output
    saved, aliases = load_snapshot(root), data["result"]["aliases"]
    assert saved.graph.nodes[aliases["impl"]].sources == sources
    assert saved.graph.nodes[aliases["goal"]].sources == []
    assert saved.graph.nodes[aliases["goal"]].body == "# Keep $goal literal"


def test_readable_receipt_includes_the_actual_alias_mapping(workspace):
    root, parent = workspace
    result = invoke(
        root,
        "add",
        "--as",
        "goal",
        "--parent",
        parent,
        "-m",
        "# Goal",
        "add",
        "--parent",
        "$goal",
        "-m",
        "# Detail",
    )
    assert result.exit_code == 0 and result.stdout.count("Added:") == 1
    goal = next(n for n in load_snapshot(root).nodes if n.body == "# Goal")
    assert f"Aliases: $goal -> {goal.id}" in result.stdout


def test_cancelling_deletion_cancels_unrelated_adds_too(workspace, monkeypatch):
    root, parent = workspace
    _, child = add_node(root, "requirement", [parent], "# Keep")
    before = load_snapshot(root).files
    monkeypatch.setattr(cli, "interactive_stdin", lambda: True)
    monkeypatch.setattr(cli.click, "confirm", lambda *args, **kwargs: False)
    result = invoke(root, "add", "--parent", parent, "-m", "# Cancel me", "delete", child)
    assert result.exit_code == 1 and "cancelled" in result.stderr
    assert load_snapshot(root).files == before


def test_singleton_add_alias_and_add_update_previews(workspace):
    root, parent = workspace
    before = load_snapshot(root).files
    result, data = call(
        root, "add", "--as", "only", "--parent", parent, "-m", "# Only", "--dry-run"
    )
    assert result.exit_code == 0 and not data["result"]["applied"]
    assert set(data["result"]["aliases"]) == {"only"} and load_snapshot(root).files == before
    result, data = call(root, "add", "--as", "only", "--parent", parent, "-m", "# Only")
    assert result.exit_code == 0 and data["result"]["applied"]
    id = data["result"]["aliases"]["only"]
    before = load_snapshot(root).files
    result, data = call(root, "update", id, "-m", "# Proposed", "--dry-run")
    assert result.exit_code == 0 and not data["result"]["applied"]
    assert load_snapshot(root).files == before


def test_recovery_rolls_back_mixed_creation_deletion_and_update(tmp_path, monkeypatch):
    import specspec.workspace as workspace_module

    ids = ["AAAAAAA=", "AAAAAAE=", "AAAAAAM=", "AAAAAAI="]
    tokens = iter(base64.urlsafe_b64decode(id) for id in ids)
    monkeypatch.setattr(workspace_module.secrets, "token_bytes", lambda n: next(tokens))
    initialize(tmp_path, "# Intention")
    _, removed = add_node(tmp_path, "requirement", [ids[0]], "# Removed")
    _, changed = add_node(tmp_path, "requirement", [ids[0]], "# Original")
    before = load_snapshot(tmp_path).files
    original, writes = workspace_module.os.replace, []

    def interrupt(source, target):
        if Path(target).parent == tmp_path / ".specspec":
            writes.append(Path(target).name)
            if len(writes) == 2:
                raise OSError("Interrupted mixed edit chain")
        return original(source, target)

    monkeypatch.setattr(workspace_module.os, "replace", interrupt)
    result, _ = call(
        tmp_path,
        "delete",
        removed,
        "--yes",
        "add",
        "--as",
        "new",
        "--parent",
        ids[0],
        "-m",
        "# New",
        "update",
        changed,
        "-m",
        "# Replacement",
        "--require-valid",
    )
    assert result.exit_code == 2 and (tmp_path / ".specspec-local/journal.json").exists()
    assert not (tmp_path / f".specspec/{removed}.md").exists()
    assert (tmp_path / f".specspec/{ids[-1]}.md").exists()
    monkeypatch.setattr(workspace_module.os, "replace", original)
    assert recover(tmp_path)["graph_valid"]
    assert load_snapshot(tmp_path).files == before


@pytest.mark.parametrize("encoding", ["ascii", "cp1252"])
def test_real_argv_chain_preserves_unicode_crlf_and_aliases(workspace, encoding):
    root, parent = workspace
    body = '# Unicode 🐕\r\n\r\n"quotes", backslash \\, $literal and `tick`.  \r\n'
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "specspec",
            "--root",
            str(root),
            "add",
            "--as",
            "goal",
            "--parent",
            parent,
            "-m",
            body,
            "add",
            "--parent",
            "$goal",
            "-m",
            "update",
            "--require-valid",
            "--json",
        ],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        env={**os.environ, "PYTHONIOENCODING": encoding, "PYTHONUTF8": "0"},
    )
    assert result.returncode == 0, result.stderr.decode("utf8", errors="replace")
    data = json.loads(result.stdout)["result"]
    saved = load_snapshot(root)
    assert saved.graph.nodes[data["aliases"]["goal"]].body == body
    assert saved.graph.nodes[data["changed_ids"][1]].parents == [data["aliases"]["goal"]]
