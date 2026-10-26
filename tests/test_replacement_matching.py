"""Default layout equivalence retains literal content and original source spans."""

import json
import os
import random
import subprocess
import sys

import pytest
from click.testing import CliRunner

from specspec import body_replacements, cli
from specspec import replacement_matching as matching
from specspec.body_replacements import replace_body
from specspec.model import SpecError
from specspec.workspace import add_node, load_snapshot


def call(root, *args):
    result = CliRunner().invoke(cli.main, ["--root", str(root), *args, "--json"])
    assert result.stdout, (result.output, result.exception)
    return result, json.loads(result.stdout)


@pytest.mark.parametrize("source_eol", ["\n", "\r\n", "\r"])
@pytest.mark.parametrize("old_eol", ["\n", "\r\n", "\r"])
def test_standard_line_endings_match_inside_code_without_reflow(source_eol, old_eol):
    body = "```text\n" + source_eol.join(["alpha", "beta"]) + "\n```"
    old = old_eol.join(["alpha", "beta"])
    assert replace_body(body, [(old, "NEW\r\ntext")]) == "```text\nNEW\r\ntext\n```"


@pytest.mark.parametrize(
    "body,old",
    [
        ("alpha\nbeta", "alpha beta"),
        ("alpha beta", "alpha\nbeta"),
        ("alpha\r\nbeta", "alpha beta"),
        ("alpha beta", "alpha\r\nbeta"),
        ("alpha beta\ngamma", "alpha\nbeta gamma"),
        ("**alpha\nbeta**", "alpha beta"),
        ("[alpha\nbeta](url)", "alpha beta"),
        ("- alpha beta", "alpha\nbeta"),
        ("- alpha\nbeta", "alpha beta"),
        ("> alpha\nbeta", "alpha beta"),
    ],
)
def test_only_the_selected_prose_span_is_replaced(body, old):
    matcher = matching.Matcher(body)
    spans = matcher.find(old)
    assert len(spans) == 1
    start, end = spans[0]
    new = "NEW\n  literal  "
    assert replace_body(body, [(old, new)]) == body[:start] + new + body[end:]


@pytest.mark.parametrize(
    "body,old",
    [
        ("alpha\n\nbeta", "alpha beta"),
        ("alpha beta", "alpha\n\nbeta"),
        ("alpha\n\n\nbeta", "alpha\n\nbeta"),
        ("# alpha\nbeta", "alpha beta"),
        ("alpha\nbeta\n===", "alpha beta"),
        ("alpha\n---\nbeta", "alpha --- beta"),
        ("alpha  \nbeta", "alpha beta"),
        ("alpha beta", "alpha  \nbeta"),
        ("alpha\\\nbeta", "alpha beta"),
        ("alpha beta", "alpha\\\nbeta"),
        ("alpha \nbeta", "alpha beta"),
        ("alpha\n beta", "alpha beta"),
        ("alpha\t beta", "alpha beta"),
        ("alpha  beta", "alpha beta"),
        ("- alpha\n- beta", "alpha - beta"),
        ("- alpha\n  beta", "alpha beta"),
        ("> alpha\n> beta", "alpha beta"),
        ("```\nalpha\nbeta\n```", "alpha beta"),
        ("~~~\nalpha beta\n~~~", "alpha\nbeta"),
        ("    alpha\n    beta", "alpha beta"),
        ("`alpha\nbeta`", "alpha beta"),
        ("`alpha beta`", "alpha\nbeta"),
        ('<span title="alpha beta">text</span>', "alpha\nbeta"),
        ("<pre>\nalpha\nbeta\n</pre>", "alpha beta"),
        ('[label](url "alpha beta")', "alpha\nbeta"),
        ("![alpha beta](url)", "alpha\nbeta"),
        ("alpha | beta\n---|---\none | two", "alpha | beta ---|---"),
        ("alpha | beta\n---|---\none | two", "one\n| two"),
        ("alpha&nbsp;beta", "alpha\nbeta"),
        ("alpha béta", "alpha be\u0301ta"),
        ("alpha beta", "Alpha beta"),
    ],
)
def test_structure_and_non_newline_whitespace_remain_significant(body, old):
    with pytest.raises(SpecError, match="not found"):
        replace_body(body, [(old, "NEW")])


@pytest.mark.parametrize(
    "body,old",
    [
        ("alpha beta\n\nalpha\nbeta", "alpha beta"),
        ("alpha\r\nbeta\n\nalpha\nbeta", "alpha\nbeta"),
        ("`alpha beta`\n\nalpha\nbeta", "alpha beta"),
        ("`alpha\nbeta`\n\nalpha beta", "alpha\nbeta"),
        ("alpha\nbeta\n\nalpha beta", "alpha\r\nbeta"),
    ],
)
def test_uniqueness_covers_all_admissible_layouts_without_preferring_exact(body, old):
    with pytest.raises(SpecError, match="more than once"):
        replace_body(body, [(old, "NEW")])


def test_one_original_span_seen_through_two_views_is_one_match():
    body = "# Heading\r\n\r\nalpha\r\nbeta\r\n"
    assert replace_body(body, [("alpha\nbeta", "NEW")]) == "# Heading\r\n\r\nNEW\r\n"


def test_mixed_unicode_and_line_endings_map_to_original_character_boundaries():
    body = "# 🐕\r\n\r\npré alpha\r\nbéta\rfin\n"
    assert replace_body(body, [("alpha béta", "NEW\n")]) == "# 🐕\r\n\r\npré NEW\n\rfin\n"


def test_equal_old_new_still_inserts_new_literally_after_tolerant_matching():
    assert replace_body("alpha\r\nbeta", [("alpha beta", "alpha beta")]) == "alpha beta"
    assert replace_body("alpha\r\nbeta", [("alpha\nbeta", "alpha\nbeta")]) == "alpha\nbeta"


def test_actual_consumed_bytes_not_argument_bytes_bound_the_result(monkeypatch):
    monkeypatch.setattr(body_replacements, "MAX_FILE_BYTES", 4)
    assert replace_body("é\r\nx", [("é\nx", "🐕")]) == "🐕"


def test_normalized_spans_still_use_original_overlap_and_non_cascading_rules():
    with pytest.raises(SpecError, match="overlaps"):
        replace_body("alpha\r\nbeta\ngamma", [("alpha beta", "x"), ("beta gamma", "y")])
    assert (
        replace_body(
            "alpha\r\nbetagamma\ndelta",
            [("gamma delta", "Y"), ("alpha beta", "X")],
        )
        == "XY"
    )
    assert (
        replace_body("alpha\nbeta\n\ngamma", [("alpha beta", "gamma"), ("gamma", "next")])
        == "gamma\n\nnext"
    )


def test_many_prose_reflows_preserve_all_unselected_source_bytes():
    rng = random.Random(419)
    words = ["alpha", "béta", "gamma🐕", "delta"]
    for _ in range(128):
        source = words[0]
        old = words[0]
        for word in words[1:]:
            source += rng.choice([" ", "\n", "\r\n", "\r"]) + word
            old += rng.choice([" ", "\n", "\r\n", "\r"]) + word
        prefix, suffix = "# Heading\r\n\r\n", "\r\n\r\nFooter.\n"
        assert (
            replace_body(prefix + source + suffix, [(old, "NEW\r\n  ")])
            == prefix + "NEW\r\n  " + suffix
        )


def test_analysis_limits_fail_explicitly_instead_of_using_an_incomplete_match_set(monkeypatch):
    with monkeypatch.context() as patch:
        patch.setattr(matching, "MAX_MARKDOWN_LINES", 1)
        with pytest.raises(SpecError, match="analysis budget"):
            replace_body("alpha\nbeta", [("alpha beta", "NEW")])
    with monkeypatch.context() as patch:
        patch.setattr(matching, "MAX_MARKDOWN_TOKENS", 1)
        with pytest.raises(SpecError, match="analysis budget"):
            replace_body("alpha\nbeta", [("alpha beta", "NEW")])
    with monkeypatch.context() as patch:
        patch.setattr(matching, "MAX_MATCH_NESTING", 1)
        with pytest.raises(SpecError, match="analysis budget"):
            replace_body("> > alpha\nbeta", [("alpha beta", "NEW")])
    with monkeypatch.context() as patch:
        patch.setattr(matching, "MAX_MATCH_CANDIDATES", 1)
        with pytest.raises(SpecError, match="analysis budget"):
            replace_body("`alpha beta`\n\nalpha\nbeta", [("alpha\nbeta", "NEW")])
    with monkeypatch.context() as patch:
        patch.setattr(matching, "MAX_MATCH_WORK", 1)
        with pytest.raises(SpecError, match="analysis budget"):
            replace_body("alpha\nbeta", [("alpha beta", "NEW")])
    # The cached parser retains no failed request's counters or source mapping.
    assert replace_body("alpha\nbeta", [("alpha beta", "NEW")]) == "NEW"


@pytest.mark.parametrize(
    "body",
    [
        "*a* " * 256 + "unique phrase\nwrapped",
        "|" + "a|" * 128 + "\n|" + "--|" * 128 + "\n",
        "![" * 24 + "alpha beta" + "](url)" * 24 + "\nwrapped",
    ],
)
def test_pathological_markdown_is_bounded_before_token_growth(body, monkeypatch):
    monkeypatch.setattr(matching, "MAX_MARKDOWN_TOKENS", 32)
    with pytest.raises(SpecError, match="analysis budget"):
        replace_body(body, [("alpha beta", "NEW")])


def test_provably_unique_full_body_and_literal_word_matches_need_no_markdown_budget(monkeypatch):
    monkeypatch.setattr(matching, "MAX_MARKDOWN_TOKENS", 0)
    body = "# Heading\r\n\r\nalpha beta\r\n"
    assert replace_body(body, [(body.replace("\r\n", "\n"), "NEW")]) == "NEW"
    assert replace_body(body, [("alpha", "changed")]) == body.replace("alpha", "changed")


def test_budget_rejection_cancels_other_chained_edits_without_writes(workspace, monkeypatch):
    root, parent = workspace
    _, id = add_node(root, "requirement", [parent], "alpha\nbeta")
    before = load_snapshot(root).files
    monkeypatch.setattr(matching, "MAX_MARKDOWN_TOKENS", 1)
    result, data = call(
        root,
        "add",
        "--parent",
        parent,
        "-m",
        "# Cancelled",
        "update",
        id,
        "--replace",
        "alpha beta",
        "NEW",
    )
    assert result.exit_code == 2 and not data["ok"]
    assert data["diagnostics"][0]["code"] == "REPLACE"
    assert data["diagnostics"][0]["path"] == f"_specspec/{id}.md"
    assert load_snapshot(root).files == before
    assert not (root / ".specspec-local/journal.json").exists()


def test_ambiguity_after_normalization_cancels_deletions_and_creation(workspace):
    root, parent = workspace
    _, id = add_node(root, "requirement", [parent], "alpha beta\n\nalpha\nbeta")
    _, removed = add_node(root, "requirement", [parent], "# Retain me")
    before = load_snapshot(root).files
    result, data = call(
        root,
        "delete",
        removed,
        "--yes",
        "add",
        "--parent",
        parent,
        "-m",
        "# Cancelled",
        "update",
        id,
        "--replace",
        "alpha beta",
        "NEW",
    )
    assert result.exit_code == 1 and "more than once" in data["diagnostics"][0]["message"]
    assert load_snapshot(root).files == before
    assert not (root / ".specspec-local/journal.json").exists()


def test_tolerant_matching_reuses_alias_chains_and_preserves_literal_new(workspace):
    root, parent = workspace
    _, id = add_node(root, "requirement", [parent], "# Heading\r\n\r\nalpha\r\nbeta\r\n")
    before = load_snapshot(root).files
    args = [
        "add",
        "--as",
        "goal",
        "--parent",
        parent,
        "-m",
        "# Goal",
        "update",
        id,
        "--parent",
        "$goal",
        "--replace",
        "alpha beta",
        "NEW\n  ",
        "--require-valid",
    ]
    preview, data = call(root, *args, "--dry-run")
    assert preview.exit_code == 0 and not data["result"]["applied"]
    assert load_snapshot(root).files == before
    result, data = call(root, *args)
    assert result.exit_code == 0 and data["result"]["graph_valid"]
    node = load_snapshot(root).graph.nodes[id]
    assert node.parents == [data["result"]["aliases"]["goal"]]
    assert node.body == "# Heading\r\n\r\nNEW\n  \r\n"


def test_markdown_dependency_is_lazy_for_ordinary_imports_and_word_replacements():
    code = """
import sys
from specspec import cli
from specspec.body_replacements import replace_body
assert 'markdown_it' not in sys.modules
assert replace_body('# Old', [('Old', 'New')]) == '# New'
assert 'markdown_it' not in sys.modules
assert replace_body('Old\\npassage', [('Old passage', 'New')]) == 'New'
assert 'markdown_it' in sys.modules
"""
    result = subprocess.run([sys.executable, "-c", code], capture_output=True)
    assert result.returncode == 0, result.stderr.decode("utf8", errors="replace")


@pytest.mark.parametrize("encoding", ["ascii", "cp1252"])
def test_real_windows_argv_matches_wrapped_unicode_and_keeps_new_literal(workspace, encoding):
    root, parent = workspace
    _, id = add_node(root, "requirement", [parent], "# Heading\r\n\r\nOld 🐕\r\npassage.\r\n")
    new = 'New 🐕\n"literal" $value.  '
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
            "Old 🐕 passage.",
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
    assert load_snapshot(root).graph.nodes[id].body == "# Heading\r\n\r\n" + new + "\r\n"
