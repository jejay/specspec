"""Rebuild the independent Gantt history with the current specspec command line.

Run from the specspec checkout:

    python example/gantt/history/rebuild.py
    python example/gantt/history/verify.py --history

Every recorded command in ``cli.jsonl`` is run again in a fresh repository outside the
checkout. The eight commits and their tags are made anew: an empty start, a planning commit
and a code commit for each of the three stages, and the audit. Runtime files of each stage
come from the bundle as it is; documents come from this folder. The new bundle, receipts,
ledger, graph and AGENTS.md then replace the tracked ones here. Nothing in the specspec
repository is staged or committed.

``--plan FILE`` replays another list of commands, for a history whose node texts or links
change: ``{"receipts": [{"argv", "keys", "id"}], "stages": [{"key", "label",
"deletion_reason", "spec_receipt", "implementation_receipt", "runtime_commit"}]}``. Without
it the plan is the tracked receipts and ledger.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from specspec.cli import main
from specspec.workspace import load_snapshot

SNAPSHOT = Path(__file__).resolve().parents[1]
GUIDE_HEADING = "# Working with a specspec graph"
# Files that the rebuild writes itself; everything else of a stage comes from the bundle.
MANAGED = {
    "AGENTS.md",
    "README.md",
    "STORY.md",
    "history/WALKTHROUGH.md",
    "history/checkout.py",
    "history/verify.py",
    "history/rebuild.py",
    "history/cli.jsonl",
    "history/revisions.json",
    "history/gantt.bundle",
}
STAGE_README = """# Gantt planning example, stage {stage}

A small planning app that is specified with specspec before each round of code. The
graph of this stage is in `.specspec/`, and `AGENTS.md` holds the guide that
`specspec init` wrote. A commit titled `Agent specspec changes:` plans a stage, and the
commit after it builds that stage. `history/WALKTHROUGH.md` explains how to compare the
stages, and `STORY.md` tells the product briefs behind them as a fictional dialogue.
"""


def tracked_plan() -> dict:
    """The plan that repeats the tracked history as it is."""
    lines = (SNAPSHOT / "history/cli.jsonl").read_text(encoding="utf-8").splitlines()
    receipts = []
    for receipt in map(json.loads, lines):
        entry = {"argv": receipt["argv"], "keys": sorted(receipt["result"])}
        if receipt["argv"][2] in ("init", "add"):
            entry["id"] = receipt["result"]["changed_ids"][0]
        receipts.append(entry)
    ledger = json.loads((SNAPSHOT / "history/revisions.json").read_text(encoding="utf-8"))
    stages = [
        {
            "key": row["key"],
            "label": row["label"],
            "deletion_reason": row["deletion_reason"],
            "spec_receipt": row["spec_receipt"],
            "implementation_receipt": row["implementation_receipt"],
            "runtime_commit": f"stage/{row['key']}-code",
        }
        for row in ledger
    ]
    return {"receipts": receipts, "stages": stages}


class Rebuild:
    def __init__(self, plan: dict, container: Path):
        self.plan = plan
        self.old = container / "present"
        self.new = container / "rebuilt"
        self.runner = CliRunner()
        self.receipts: list[dict] = []
        self.ledger = [
            {
                "key": stage["key"],
                "label": stage["label"],
                "node_count_before": 0,
                "spec_node_count": 0,
                "deletion_reason": stage["deletion_reason"],
                "deleted_ids": [],
            }
            for stage in plan["stages"]
        ]
        bundle = SNAPSHOT / "history/gantt.bundle"
        subprocess.run(
            ["git", "clone", "--quiet", "--config", "core.autocrlf=false", str(bundle), self.old],
            check=True,
        )
        self.new.mkdir()

    def git(self, *arguments: str, root: Path | None = None) -> str:
        done = subprocess.run(
            ["git", "-C", str(root or self.new), *arguments], capture_output=True, check=True
        )
        return done.stdout.decode("utf-8").strip()

    def blob(self, ref: str, path: str) -> bytes:
        """A file of the present bundle, byte for byte."""
        done = subprocess.run(
            ["git", "-C", str(self.old), "show", f"{ref}:{path}"], capture_output=True, check=True
        )
        return done.stdout

    def cli(self, arguments: list[str], identity: str | None = None) -> dict:
        """Run one command in the rebuilt repository; a new node gets the planned ID."""
        previous = Path.cwd()
        os.chdir(self.new)
        try:
            if identity:
                fixed = base64.urlsafe_b64decode(identity)
                with patch("specspec.workspace.secrets.token_bytes", return_value=fixed):
                    result = self.runner.invoke(main, arguments)
            else:
                result = self.runner.invoke(main, arguments)
        finally:
            os.chdir(previous)
        assert result.exit_code == 0, (arguments, result.output, result.exception)
        response = json.loads(result.stdout)
        assert response["ok"] and not response["diagnostics"], response
        if identity:
            assert response["result"]["changed_ids"] == [identity], response["result"]
        return response

    def write(self, path: str, data: bytes | str) -> None:
        target = self.new / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, str):
            data = data.encode("utf-8")
        target.write_bytes(data.replace(b"\r\n", b"\n"))

    def documents(self, stage: int, ref: str | None) -> None:
        """Documents of a stage: from this folder, helper scripts from the bundle's commit."""
        for path in ("STORY.md", "history/WALKTHROUGH.md"):
            self.write(path, (SNAPSHOT / path).read_bytes())
        for path in ("history/checkout.py", "history/verify.py"):
            self.write(path, self.blob(ref, path) if ref else (SNAPSHOT / path).read_bytes())
        if ref:
            self.write("README.md", STAGE_README.format(stage=self.plan["stages"][stage]["key"]))
        else:
            self.write("README.md", (SNAPSHOT / "README.md").read_bytes())
        self.write("history/revisions.json", json.dumps(self.ledger, indent=2) + "\n")
        lines = "".join(json.dumps(receipt, ensure_ascii=True) + "\n" for receipt in self.receipts)
        self.write("history/cli.jsonl", lines)

    def runtime(self, stage: int) -> None:
        """Bring in the app and its tests as the bundle has them for this stage."""
        ref = self.plan["stages"][stage]["runtime_commit"]
        for path in self.git("ls-tree", "-r", "--name-only", ref, root=self.old).splitlines():
            if not path.startswith(".specspec/") and path not in MANAGED:
                self.write(path, self.blob(ref, path))
        self.git("add", "-A")

    def commit(self, message: str, tag: str) -> str:
        self.cli(["--root", ".", "check", "--warnings-as-errors", "--json"])
        self.git("add", "-A")
        self.cli(
            ["--root", ".", "check", "--staged", "--sources", "--warnings-as-errors", "--json"]
        )
        self.git("commit", "--quiet", "-m", message)
        self.git("tag", tag)
        return self.git("rev-parse", "HEAD")

    def run(self) -> None:
        stages = self.plan["stages"]
        marks = {}
        for index, stage in enumerate(stages):
            marks[stage["spec_receipt"]] = (index, "spec")
            marks[stage["implementation_receipt"]] = (index, "implementation")
        self.git("init", "--quiet", "--initial-branch=main")
        self.git("config", "core.autocrlf", "false")
        self.git("config", "user.name", "specspec example fixture")
        self.git("config", "user.email", "fixture@specspec.invalid")
        self.git("commit", "--quiet", "--allow-empty", "-m", "gantt: start the independent example")
        self.git("tag", "stage/00-empty")
        predecessor = self.git("rev-parse", "HEAD")
        section = (SNAPSHOT / "AGENTS.md").read_text(encoding="utf-8").replace("\r\n", "\n")
        section = section.split(GUIDE_HEADING)[0].rstrip() + "\n"
        installed: set[int] = set()
        for ordinal, entry in enumerate(self.plan["receipts"], 1):
            stage = next(
                (i for i, s in enumerate(stages) if ordinal <= s["implementation_receipt"]),
                len(stages) - 1,
            )
            arguments, action = entry["argv"], entry["argv"][2]
            if action == "init":
                self.write("AGENTS.md", section)  # init appends the shipped guide to it
            building = action == "add" and "implementation" in arguments
            if building and stage not in installed:
                self.runtime(stage)
                installed.add(stage)
            if ordinal == stages[stage]["spec_receipt"] - self.spec_length(stage) + 1:
                self.ledger[stage]["node_count_before"] = self.node_count()
            response = self.cli(arguments, entry.get("id"))
            result = {key: response["result"][key] for key in entry["keys"]}
            if action == "delete":
                self.ledger[stage]["deleted_ids"] = result["requested_ids"]
            self.receipts.append(
                {
                    "argv": arguments,
                    "stdin": None,
                    "exit_code": 0,
                    "api_version": response["api_version"],
                    "result": result,
                    "diagnostics": response["diagnostics"],
                }
            )
            if ordinal in marks:
                index, kind = marks[ordinal]
                row, tag = self.ledger[index], f"stage/{stages[index]['key']}-"
                row[f"{kind}_receipt"] = ordinal
                if kind == "spec":
                    row["predecessor_commit"] = predecessor
                    row["spec_node_count"] = self.node_count()
                    message = f"Agent specspec changes: plan {row['label']}"
                    if row["deleted_ids"]:
                        message += "\n\n" + row["deletion_reason"]
                else:
                    message = f"gantt: implement {row['label']}"
                self.documents(index, stages[index]["runtime_commit"])
                row[f"{kind}_commit"] = self.commit(
                    message, tag + ("spec" if kind == "spec" else "code")
                )
                if kind == "implementation":
                    predecessor = row["implementation_commit"]
                print(ordinal, tag + kind, row[f"{kind}_commit"], flush=True)
        self.documents(len(stages) - 1, None)
        self.commit(
            "Agent specspec changes: audit the recorded stages, receipts and verifier",
            "stage/04-audit",
        )
        assert self.git("rev-list", "--count", "--all") == "8"

    def spec_length(self, stage: int) -> int:
        """How many receipts belong to a stage's planning commit."""
        stages = self.plan["stages"]
        start = stages[stage - 1]["implementation_receipt"] if stage else 0
        return stages[stage]["spec_receipt"] - start

    def node_count(self) -> int:
        if not (self.new / ".specspec").is_dir():
            return 0
        return len(load_snapshot(self.new).nodes)

    def install(self) -> None:
        """Replace the tracked bundle, receipts, ledger, graph and guide with the rebuilt ones."""
        bundle = self.new.parent / "gantt.bundle"
        self.git("bundle", "create", str(bundle), "--all")
        shutil.copyfile(bundle, SNAPSHOT / "history/gantt.bundle")
        for path in ("history/cli.jsonl", "history/revisions.json", "AGENTS.md"):
            shutil.copyfile(self.new / path, SNAPSHOT / path)
        graph = SNAPSHOT / ".specspec"
        rebuilt = {path.name: path for path in (self.new / ".specspec").glob("*.md")}
        for path in graph.glob("*.md"):
            if path.name not in rebuilt:
                path.unlink()
        for name, path in rebuilt.items():
            shutil.copyfile(path, graph / name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--plan", type=Path, help="a JSON plan to replay instead of the tracked one"
    )
    parser.add_argument("--keep", type=Path, help="an empty folder in which the work stays")
    options = parser.parse_args()
    chosen = (
        json.loads(options.plan.read_text(encoding="utf-8")) if options.plan else tracked_plan()
    )
    folder = options.keep or Path(tempfile.mkdtemp(prefix="specspec-gantt-rebuild-"))
    folder.mkdir(parents=True, exist_ok=True)
    assert not any(folder.iterdir()), f"{folder} is not empty"
    rebuild = Rebuild(chosen, folder)
    rebuild.run()
    rebuild.install()
    print(
        f"Rebuilt {len(rebuild.receipts)} receipts in {rebuild.new}; now run verify.py --history."
    )
