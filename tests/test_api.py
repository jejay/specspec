import json

from click.testing import CliRunner

from specspec.cli import main
from specspec.workspace import load_snapshot


def test_stdin_is_utf8_and_preserves_binding_whitespace(tmp_path):
    body = "# Absicht 🐕\r\n\r\nText mit Umlauten: äöü.  \r\n"
    result = CliRunner().invoke(
        main,
        ["--root", str(tmp_path), "init", "--manifesto", "-", "--json"],
        input=body.encode("utf-8"),
    )
    assert result.exit_code == 0, result.output
    node = load_snapshot(tmp_path).nodes[0]
    assert node.body == body
    assert (tmp_path / node.path).read_bytes().endswith(body.encode("utf-8"))


def test_budget_covers_serialized_json_response(workspace):
    root, manifesto = workspace
    runner = CliRunner()
    args = ["--root", str(root), "context", manifesto, "--json"]
    result = runner.invoke(main, args)
    assert result.exit_code == 0
    exact_size = len(result.output.encode("utf-8"))
    limited = runner.invoke(main, [*args, "--max-bytes", str(exact_size)])
    assert limited.exit_code == 0
    assert len(limited.output.encode("utf-8")) <= exact_size
    too_small = runner.invoke(main, [*args, "--max-bytes", str(exact_size - 1)])
    assert too_small.exit_code == 1
    assert json.loads(too_small.output)["diagnostics"][0]["code"] == "BUDGET"


def test_source_paths_are_canonical_and_have_no_control_characters():
    from specspec.format import safe_source_path

    assert safe_source_path("src/handler.py")
    for value in ["./src/handler.py", "src//handler.py", "src/handler.py/", "src/\x00.py"]:
        assert not safe_source_path(value)
