"""The explicit CLI publisher keeps identity separate from project execution."""

import re
from pathlib import Path

from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/pipy_publish.yaml"


def test_pypi_publisher_matches_owner_configuration_and_is_explicit():
    workflow = YAML(typ="safe").load(WORKFLOW.read_text())
    assert set(workflow["on"]) == {"workflow_dispatch"}
    version = workflow["on"]["workflow_dispatch"]["inputs"]["version"]
    assert version["required"] is True and version["default"] == "0.0.1"
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["concurrency"]["cancel-in-progress"] is False
    assert set(workflow["jobs"]) == {"build", "publish"}
    for job in workflow["jobs"].values():
        assert job["if"] == "github.ref == 'refs/heads/main'"


def test_only_publisher_has_identity_and_does_not_execute_project_source():
    workflow = YAML(typ="safe").load(WORKFLOW.read_text())
    build = workflow["jobs"]["build"]
    assert "permissions" not in build
    publish = workflow["jobs"]["publish"]
    assert publish["needs"] == "build"
    assert publish["environment"]["name"] == "pypi"
    assert publish["environment"]["url"] == "https://pypi.org/project/specspec/"
    assert publish["permissions"] == {"id-token": "write"}
    assert all("run" not in step for step in publish["steps"])
    assert len(publish["steps"]) == 2
    assert publish["steps"][0]["uses"].startswith("actions/download-artifact@")
    action = publish["steps"][1]
    assert action["uses"].startswith("pypa/gh-action-pypi-publish@")
    assert action["with"] == {
        "packages-dir": "dist/",
        "attestations": True,
        "skip-existing": False,
    }
    assert "secrets." not in WORKFLOW.read_text()


def test_release_actions_are_pinned_and_artifacts_have_one_build_owner():
    workflow = YAML(typ="safe").load(WORKFLOW.read_text())
    for job in workflow["jobs"].values():
        for step in job["steps"]:
            if "uses" in step:
                assert re.fullmatch(r"[\w-]+/[\w-]+@[a-f0-9]{40}", step["uses"])
    steps = workflow["jobs"]["build"]["steps"]
    assert steps[0]["with"]["persist-credentials"] is False
    commands = "\n".join(step.get("run", "") for step in steps)
    for required in [
        '"twine==7.0.0"',
        "python -m tools.pypi_release version",
        "python -m pytest",
        "python -m build --outdir dist/pypi",
        "python -m tools.pypi_release verify",
        "python -m twine check --strict",
        "python -m tools.pypi_release smoke",
    ]:
        assert required in commands
    assert "${{ inputs.version }}" not in commands
    upload = steps[-1]
    assert upload["with"]["name"] == "cli-distributions"
    assert upload["with"]["path"].splitlines() == ["dist/pypi/*.whl", "dist/pypi/*.tar.gz"]
    assert workflow["jobs"]["publish"]["steps"][0]["with"]["name"] == "cli-distributions"


def test_current_guides_and_startup_screens_prefer_pypi_installation():
    for path in [
        "README.md",
        "AGENTS.md",
        "CONTRIBUTING.md",
        "docs/install.md",
        "docs/remote-workspaces.md",
        "vscode/README.md",
        "electron/README.md",
        "example/gantt/README.md",
        "example/gantt/AGENTS.md",
        "src/specspec/templates/AGENTS.md",
        "graph-ui-common/view.cjs",
        "vscode/src/extension.ts",
    ]:
        text = (ROOT / path).read_text(encoding="utf8")
        assert "uv tool install specspec" in text, path
    for path in ["graph-ui-common/view.cjs", "vscode/src/extension.ts"]:
        assert "uv tool install /path/to/specspec.whl" not in (ROOT / path).read_text(
            encoding="utf8"
        )
