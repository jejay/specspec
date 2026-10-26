"""Literal passage edits share the existing candidate and transaction boundary."""

import base64
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from specspec import batch, body_replacements, cli
from specspec.body_replacements import input_bytes, replace_body
from specspec.model import MAX_FILE_BYTES, SpecError
from specspec.workspace import add_node, load_snapshot, recover, update_node


def call(root, *args):
    result = CliRunner().invoke(cli.main, ["--root", str(root), *args, "--json"])
    assert result.stdout, (result.output, result.exception)
    return result, json.loads(result.stdout)


@pytest.mark.parametrize("reverse", [False, True])
def test_pairs_refer_to_the_same_original_and_do_not_cascade(reverse):
    pairs = [("first", "second"), ("second", "third")]
    if reverse:
        pairs.reverse()
    assert replace_body("# first\n\nsecond\n", pairs) == "# second\n\nthird\n"
    assert replace_body("redblue", [("blue", "black"), ("red", "green")]) == "greenblack"


@pytest.mark.parametrize(
    "body,pairs,message",
    [
        ("# Literal", [("absent", "new")], "not found"),
        ("# Literal", [("literal", "new")], "not found"),
        ("# Café", [("Cafe\u0301", "new")], "not found"),
        ("# one\r\n\r\ntwo", [("one\ntwo", "new")], "not found"),
        ("# abc42", [(r"\d+", "new")], "not found"),
        ("# old old", [("old", "new")], "more than once"),
        ("# aaaa", [("aaa", "new")], "more than once"),
        ("# abc", [("abc", "x"), ("bc", "y")], "overlaps"),
        ("# abc", [("abc", "x"), ("abc", "y")], "overlaps"),
        ("# first", [("first", "second"), ("second", "third")], "not found"),
    ],
)
def test_uncertain_matches_are_rejected_without_guessing(body, pairs, message):
    with pytest.raises(SpecError) as caught:
        replace_body(body, pairs, path=".specspec/AAAAAAA=.md")
    error = caught.value
    assert error.exit_code == 1 and error.diagnostics[0].code == "REPLACE"
    assert message in error.diagnostics[0].message
    assert error.diagnostics[0].path == ".specspec/AAAAAAA=.md"


@pytest.mark.parametrize("pairs", [None, {}, [], [("", "x")], [("x",)], [("x", 1)], ["xy"]])
def test_replacement_input_has_an_explicit_bounded_shape(pairs):
    with pytest.raises(SpecError) as caught:
        input_bytes(pairs)
    assert caught.value.exit_code == 2 and caught.value.diagnostics[0].code == "REPLACE"


@pytest.mark.parametrize("ending", ["", "\n", "\r\n"])
def test_singleton_preserves_untouched_body_and_frontmatter(workspace, ending):
    root, parent = workspace
    body = '# Heading\r\n\r\nOld 🐕 passage.  \r\nKeep "quotes", \\ and $literal.' + ending
    _, id = add_node(root, "requirement", [parent], body)
    path = root / f".specspec/{id}.md"
    header, marker, raw_body = path.read_bytes().partition(b"\n---\n")
    header = header.replace(b"parents:", b"# Owner comment\nparents:")
    path.write_bytes(header + marker + raw_body)
    result, data = call(root, "update", id, "--replace", "Old 🐕 passage.", "New 🐕 reasoning.")
    assert result.exit_code == 0 and data["result"]["applied"], result.output
    assert data["api_version"] == 7
    saved = load_snapshot(root)
    assert saved.valid and saved.graph.nodes[id].parents == [parent]
    expected = body.replace("Old 🐕 passage.", "New 🐕 reasoning.")
    assert saved.graph.nodes[id].body == expected
    assert path.read_bytes() == header + marker + expected.encode("utf8")


def test_empty_new_deletes_text_equal_values_are_a_noop_and_empty_result_is_invalid(workspace):
    root, parent = workspace
    _, id = add_node(root, "requirement", [parent], "# Keep REMOVE\n")
    result, _ = call(root, "update", id, "--replace", " REMOVE", "")
    assert result.exit_code == 0 and load_snapshot(root).graph.nodes[id].body == "# Keep\n", (
        result.output
    )
    before = load_snapshot(root).files
    result, _ = call(root, "update", id, "--replace", "Keep", "Keep")
    assert result.exit_code == 0 and load_snapshot(root).files == before
    result, data = call(root, "update", id, "--replace", "# Keep\n", "")
    assert result.exit_code == 1 and any(d["code"] == "SCHEMA" for d in data["diagnostics"])
    assert load_snapshot(root).files == before


def test_literal_backslash_n_whitespace_and_actual_newlines_are_distinct():
    assert replace_body("# old\r\n", [("old", r"new\ntext")]) == "# new\\ntext\r\n"
    assert replace_body("# old\r\n", [("old", "  new\ntext  ")]) == "#   new\ntext  \r\n"


def test_matching_cannot_touch_frontmatter_and_insertions_remain_body_text(workspace):
    root, parent = workspace
    _, id = add_node(root, "requirement", [parent], "# Marker\n")
    before = load_snapshot(root).files
    result, data = call(root, "update", id, "--replace", f"id: {id}", "id: AAAAAAA=")
    assert result.exit_code == 1 and data["diagnostics"][0]["code"] == "REPLACE"
    assert load_snapshot(root).files == before
    text = "# Changed\n---\nid: AAAAAAA=\nparents: []\n"
    result, _ = call(root, "update", id, "--replace", "# Marker\n", text)
    assert result.exit_code == 0
    node = load_snapshot(root).graph.nodes[id]
    assert node.id == id and node.parents == [parent] and node.body == text


@pytest.mark.parametrize("form", ["separate", "equals"])
@pytest.mark.parametrize(
    "old,new", [("add", "update"), ("show", "delete"), ("--json", "--dry-run")]
)
def test_both_option_values_remain_literal_in_chains(workspace, form, old, new):
    root, parent = workspace
    _, id = add_node(root, "requirement", [parent], old)
    replacement = ["--replace", old, new] if form == "separate" else ["--replace=" + old, new]
    result, data = call(
        root,
        "update",
        id,
        *replacement,
        "add",
        "--as",
        "detail",
        "--parent",
        id,
        "-m",
        "# Detail",
        "--require-valid",
    )
    assert result.exit_code == 0, result.output
    saved = load_snapshot(root)
    assert saved.graph.nodes[id].body == new
    assert saved.graph.nodes[data["result"]["aliases"]["detail"]].parents == [id]


@pytest.mark.parametrize("source", [["-m", ""], ["--body", "NEVER_OPEN.md"], ["--body", "-"]])
def test_conflicts_in_later_steps_are_rejected_before_body_reads(workspace, monkeypatch, source):
    root, parent = workspace
    before = load_snapshot(root).files
    monkeypatch.setattr(cli, "read_body", lambda p: pytest.fail("Finish source preflight first."))
    result, data = call(
        root,
        "add",
        "--parent",
        parent,
        "--body",
        "NEVER_OPEN.md",
        "update",
        parent,
        "--replace",
        "Project",
        "Product",
        *source,
    )
    assert result.exit_code == 2 and data["diagnostics"][0]["code"] == "ARGUMENT"
    assert load_snapshot(root).files == before


def test_empty_old_in_a_later_step_is_rejected_before_body_reads(workspace, monkeypatch):
    root, parent = workspace
    before = load_snapshot(root).files
    monkeypatch.setattr(cli, "read_body", lambda p: pytest.fail("Validate pairs before reading."))
    result, data = call(
        root,
        "add",
        "--parent",
        parent,
        "--body",
        "-",
        "update",
        parent,
        "--replace",
        "",
        "new",
    )
    assert result.exit_code == 2 and "nonempty" in data["diagnostics"][0]["message"]
    assert load_snapshot(root).files == before


@pytest.mark.parametrize("suffix", [["--replace", "old"], ["--replace", "old", "new", "query"]])
def test_incomplete_pairs_and_mixed_commands_do_not_read_or_write(workspace, monkeypatch, suffix):
    root, parent = workspace
    before = load_snapshot(root).files
    monkeypatch.setattr(cli, "read_body", lambda p: pytest.fail("Parse every step first."))
    result = CliRunner().invoke(
        cli.main,
        ["--root", str(root), "add", "--parent", parent, "--body", "-", "update", parent, *suffix],
    )
    assert result.exit_code == 2 and load_snapshot(root).files == before


@pytest.mark.parametrize("failure", ["missing", "ambiguous", "overlap"])
def test_a_failed_replacement_cancels_the_complete_chain_before_journaling(workspace, failure):
    root, parent = workspace
    update_node(root, parent, body="# abc and old old\n")
    _, id = add_node(root, "requirement", [parent], "# Remove me\n")
    args = {
        "missing": ["--replace", "missing", "new"],
        "ambiguous": ["--replace", "old", "new"],
        "overlap": ["--replace", "abc", "x", "--replace", "bc", "y"],
    }[failure]
    before = load_snapshot(root).files
    result, data = call(
        root,
        "delete",
        id,
        "--yes",
        "add",
        "--parent",
        parent,
        "-m",
        "# Cancelled",
        "update",
        parent,
        *args,
    )
    assert result.exit_code == 1 and not data["ok"]
    message = {"missing": "not found", "ambiguous": "more than once", "overlap": "overlaps"}[
        failure
    ]
    assert message in data["diagnostics"][0]["message"]
    assert load_snapshot(root).files == before
    assert not (root / ".specspec-local/journal.json").exists()


def test_replacement_repair_aliases_and_exact_deletion_share_one_transaction(
    workspace, monkeypatch
):
    import specspec.workspace as workspace_module

    root, parent = workspace
    _, old = add_node(root, "requirement", [parent], "# Old goal")
    _, survivor = add_node(root, "requirement", [old], "# Old reasoning\n\nKeep this.\n")
    journals, original = [], workspace_module.write_journal

    def journal(state, value):
        journals.append(value)
        return original(state, value)

    monkeypatch.setattr(workspace_module, "write_journal", journal)
    result, data = call(
        root,
        "delete",
        old,
        "--yes",
        "add",
        "--as",
        "goal",
        "--parent",
        parent,
        "-m",
        "# New goal",
        "update",
        survivor,
        "--replace",
        "Old reasoning",
        "New reasoning",
        "--parent",
        "$goal",
        "--require-valid",
    )
    assert result.exit_code == 0 and data["result"]["graph_valid"], result.output
    saved, receipt = load_snapshot(root), data["result"]
    assert old not in saved.graph.nodes and receipt["deleted_ids"] == [old]
    assert saved.graph.nodes[survivor].parents == [receipt["aliases"]["goal"]]
    assert saved.graph.nodes[survivor].body == "# New reasoning\n\nKeep this.\n"
    assert len(journals) == 1 and len(journals[0]["files"]) == 3


def test_preview_and_optional_whole_graph_validation_are_preserved(workspace):
    root, parent = workspace
    _, id = add_node(root, "requirement", ["AAAAAAA="], "# Old\n")
    before = load_snapshot(root).files
    result, data = call(root, "update", id, "--replace", "Old", "New", "--dry-run")
    assert result.exit_code == 0 and not data["result"]["applied"]
    assert not data["result"]["graph_valid"] and load_snapshot(root).files == before
    result, data = call(root, "update", id, "--replace", "Old", "New", "--require-valid")
    assert result.exit_code == 1 and not data["ok"] and load_snapshot(root).files == before
    result, data = call(root, "update", id, "--replace", "Old", "New")
    assert result.exit_code == 0 and data["result"]["applied"] and not data["result"]["graph_valid"]
    assert load_snapshot(root).graph.nodes[id].body == "# New\n"


def test_replacements_can_change_parents_and_sources_with_their_existing_owners(workspace):
    root, parent = workspace
    _, first = add_node(root, "requirement", [parent], "# First")
    _, second = add_node(root, "requirement", [parent], "# Second")
    (root / "main.py").write_text("pass\n", encoding="utf8")
    sources = [{"path": "main.py", "symbol": "literal old"}]
    _, id = add_node(root, "implementation", [first], "# Old", sources)
    result, _ = call(root, "update", id, "--replace", "Old", "New", "--parent", second)
    assert result.exit_code == 0
    node = load_snapshot(root).graph.nodes[id]
    assert node.body == "# New" and node.parents == [second] and node.sources == sources
    replacement_sources = [{"path": "main.py", "symbol": "literal new"}]
    result, _ = call(
        root,
        "update",
        id,
        "--replace",
        "New",
        "Newest",
        "--sources",
        json.dumps(replacement_sources),
    )
    assert (
        result.exit_code == 0 and load_snapshot(root).graph.nodes[id].sources == replacement_sources
    )


def test_fresh_matching_happens_under_the_writer_lock_and_keeps_unrelated_changes(
    workspace, monkeypatch
):
    root, parent = workspace
    _, id = add_node(root, "requirement", [parent], "# Old\n")
    original_mutate, original_replace = batch.mutate, batch.replace_body

    def before_lock(root, operation, **options):
        update_node(root, id, body="# Old\n\nConcurrent unrelated text.\n")
        return original_mutate(root, operation, **options)

    def under_lock(body, pairs, **options):
        assert (root / ".specspec-local/lock").is_file()
        assert "Concurrent unrelated text." in body
        return original_replace(body, pairs, **options)

    monkeypatch.setattr(batch, "mutate", before_lock)
    monkeypatch.setattr(batch, "replace_body", under_lock)
    result, _ = call(root, "update", id, "--replace", "Old", "New")
    assert result.exit_code == 0
    assert load_snapshot(root).graph.nodes[id].body == "# New\n\nConcurrent unrelated text.\n"


def test_replacement_input_and_result_limits_count_utf8_bytes(monkeypatch):
    monkeypatch.setattr(body_replacements, "MAX_FILE_BYTES", 4)
    assert input_bytes([("é", "🐕")]) == 6
    assert replace_body("é", [("é", "🐕")]) == "🐕"
    with pytest.raises(SpecError, match="exceeds 1 MiB"):
        input_bytes([("old", "ééé")])
    with pytest.raises(SpecError, match="result exceeds"):
        replace_body("# é", [("é", "🐕")])
    monkeypatch.setattr(body_replacements, "MAX_REPLACEMENTS", 1)
    with pytest.raises(SpecError, match="1-1024"):
        input_bytes([("a", "b"), ("c", "d")])


def test_total_pair_count_and_combined_text_budget_precede_input_reads(workspace, monkeypatch):
    root, parent = workspace
    _, second = add_node(root, "requirement", [parent], "# Second")
    before = load_snapshot(root).files
    monkeypatch.setattr(cli, "read_body", lambda p: pytest.fail("Bound inputs before body reads."))
    monkeypatch.setattr(batch, "MAX_REPLACEMENTS", 1)
    args = [
        "update",
        parent,
        "--replace",
        "Project",
        "Product",
        "update",
        second,
        "--replace",
        "Second",
        "Other",
        "add",
        "--parent",
        parent,
        "--body",
        "-",
    ]
    result, data = call(root, *args)
    assert result.exit_code == 2 and "1024 replacement pairs" in data["diagnostics"][0]["message"]
    monkeypatch.setattr(batch, "MAX_REPLACEMENTS", 1024)
    monkeypatch.setattr(batch, "MAX_BATCH_BYTES", 15)
    result, data = call(root, *args)
    assert result.exit_code == 2 and "16 MiB" in data["diagnostics"][0]["message"]
    assert load_snapshot(root).files == before


def test_old_new_material_reduces_the_remaining_body_file_budget(workspace, monkeypatch, tmp_path):
    root, parent = workspace
    before = load_snapshot(root).files
    monkeypatch.setattr(batch, "MAX_BATCH_BYTES", 15)
    path = tmp_path / "body.md"
    path.write_bytes(b"12345678")
    reads, original = [], cli.read_body

    def read(path):
        reads.append(path)
        assert len(reads) == 1, "Do not open further bodies after the combined limit."
        return original(path)

    monkeypatch.setattr(cli, "read_body", read)
    result, data = call(
        root,
        "update",
        parent,
        "--replace",
        "old!",
        "new!",
        "add",
        "--parent",
        parent,
        "--body",
        str(path),
        "add",
        "--parent",
        parent,
        "--body",
        str(path),
    )
    assert result.exit_code == 2 and "16 MiB" in data["diagnostics"][0]["message"]
    assert len(reads) == 1 and load_snapshot(root).files == before


@pytest.mark.parametrize("growth,code", [(950, "FORMAT"), (1001, "REPLACE")])
def test_large_replacement_result_rejects_the_whole_candidate(workspace, growth, code):
    root, parent = workspace
    _, id = add_node(root, "requirement", [parent], "# " + "x" * (MAX_FILE_BYTES - 1000))
    before = load_snapshot(root).files
    result, data = call(root, "update", id, "--replace", "#", "#" + "z" * growth)
    assert result.exit_code == 1 and data["diagnostics"][0]["code"] == code
    assert load_snapshot(root).files == before


def test_private_prepared_edits_reject_mixed_or_non_update_replacement_fields():
    for edit in [
        {"op": "update", "id": "AAAAAAA=", "body": "# Body", "replacements": [["old", "new"]]},
        {"op": "add", "parents": ["AAAAAAA="], "body": "# Body", "replacements": [["old", "new"]]},
        {"op": "delete", "ids": ["AAAAAAA="], "replacements": [["old", "new"]]},
    ]:
        with pytest.raises(SpecError):
            batch.prepare({"edits": [edit]})


def test_interruption_recovery_restores_patched_and_new_files(workspace, monkeypatch):
    import specspec.workspace as workspace_module

    root, parent = workspace
    _, first = add_node(root, "requirement", [parent], "# First")
    _, second = add_node(root, "requirement", [parent], "# Second")
    before = load_snapshot(root).files
    original, writes = workspace_module.os.replace, []

    def interrupt(source, target):
        if Path(target).parent == root / ".specspec":
            writes.append(Path(target).name)
            if len(writes) == 2:
                raise OSError("Interrupted exact replacements")
        return original(source, target)

    monkeypatch.setattr(workspace_module.os, "replace", interrupt)
    result, _ = call(
        root,
        "update",
        first,
        "--replace",
        "First",
        "Changed first",
        "update",
        second,
        "--replace",
        "Second",
        "Changed second",
        "add",
        "--parent",
        parent,
        "-m",
        "# New",
    )
    assert result.exit_code == 2 and (root / ".specspec-local/journal.json").exists()
    monkeypatch.setattr(workspace_module.os, "replace", original)
    assert recover(root)["graph_valid"] and load_snapshot(root).files == before


def test_external_edits_after_matching_are_protected_by_original_byte_checks(
    workspace, monkeypatch
):
    import specspec.workspace as workspace_module

    root, parent = workspace
    _, id = add_node(root, "requirement", [parent], "# Old")
    path = root / f".specspec/{id}.md"
    external = path.read_bytes().replace(b"# Old", b"# External")
    original = workspace_module.write_journal

    def concurrent(state, value):
        original(state, value)
        path.write_bytes(external)

    monkeypatch.setattr(workspace_module, "write_journal", concurrent)
    result, data = call(root, "update", id, "--replace", "Old", "New")
    assert result.exit_code == 1 and data["diagnostics"][0]["code"] == "CONCURRENT"
    assert path.read_bytes() == external and (root / ".specspec-local/journal.json").exists()
    with pytest.raises(SpecError):
        recover(root)
    assert path.read_bytes() == external


@pytest.mark.parametrize("id", ["-amuwNs=", "-mAAAAA=", "-mmAAA0="])
def test_canonical_ids_cannot_become_message_options_and_option_values_stay_literal(
    workspace, monkeypatch, id
):
    import specspec.workspace as workspace_module

    root, parent = workspace
    with monkeypatch.context() as patch:
        patch.setattr(
            workspace_module.secrets, "token_bytes", lambda n: base64.urlsafe_b64decode(id)
        )
        assert add_node(root, "requirement", [parent], "Old passage")[1] == id
    result, data = call(
        root,
        "update",
        id,
        "--replace",
        "Old passage",
        id,
        "add",
        "--parent",
        id,
        "-m",
        id,
        "--require-valid",
    )
    assert result.exit_code == 0 and data["result"]["graph_valid"], result.output
    saved = load_snapshot(root)
    assert all(saved.graph.nodes[changed].body == id for changed in data["result"]["changed_ids"])
    result, _ = call(root, "update", "-m", "# Updated", id)
    assert result.exit_code == 0 and load_snapshot(root).graph.nodes[id].body == "# Updated"


def test_help_exposes_replacements_only_on_update():
    runner = CliRunner()
    assert "--replace OLD NEW" in runner.invoke(cli.main, ["update", "--help"]).stdout
    for command in ["init", "add", "delete"]:
        assert "--replace" not in runner.invoke(cli.main, [command, "--help"]).stdout


@pytest.mark.parametrize("encoding", ["ascii", "cp1252"])
def test_real_process_preserves_unicode_multiline_replacement_arguments(workspace, encoding):
    root, parent = workspace
    old = 'Old 🐕\r\n"quoted" $value and \\.'
    new = "New 🐕\r\n`literal` and spaces.  "
    _, id = add_node(root, "requirement", [parent], "# Body\r\n" + old)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "specspec",
            "--root",
            str(root),
            "update",
            id,
            "--replace",
            old,
            new,
            "--require-valid",
            "--json",
        ],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        env={**os.environ, "PYTHONIOENCODING": encoding, "PYTHONUTF8": "0"},
    )
    assert result.returncode == 0, result.stderr.decode("utf8", errors="replace")
    assert json.loads(result.stdout)["api_version"] == 7
    assert load_snapshot(root).graph.nodes[id].body == "# Body\r\n" + new
