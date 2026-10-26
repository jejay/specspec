"""API-7 logical records and raw physical documents deliberately have different jobs."""

import json

from click.testing import CliRunner

from specspec.cli import main
from specspec.workspace import add_node


def test_logical_json_and_raw_reads_keep_their_roles_when_writes_adapt_newlines(workspace):
    root, manifesto = workspace
    _, node = add_node(root, "requirement", [manifesto], "# Body\n\nalpha\r\nbeta\n")
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--root",
            str(root),
            "update",
            node,
            "--replace",
            "alpha beta",
            "literal\r\nNEW 😀",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    physical = "# Body\n\nliteral\nNEW 😀\n"
    assert (root / f".specspec/{node}.md").read_bytes().endswith(physical.encode("utf8"))
    result = runner.invoke(
        main, ["--root", str(root), "query", node, "--max-distance", "0", "--json"]
    )
    assert result.exit_code == 0, result.output
    body = json.loads(result.output)["result"]["target"]["nodes"][0]["body"]
    assert body == physical.replace("\r\n", "\n")
    result = runner.invoke(main, ["--root", str(root), "query", node, "--raw", "--json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["result"]["text"].endswith(physical)
