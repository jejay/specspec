"""Artifact inspectors reject stale or incomplete local packages without Git writes."""

import json
import os
import tarfile
import zipfile
from pathlib import Path

import pytest

from tools import release


def put(root, path, content=b""):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content.encode() if isinstance(content, str) else content)
    return target


@pytest.fixture
def products(tmp_path):
    root = tmp_path
    put(root, "pyproject.toml", '[project]\nversion = "0.1.0"\n')
    for path in [
        "package.json",
        "vscode/package.json",
        "electron/package.json",
        "graph-ui-common/package.json",
    ]:
        put(root, path, '{"version":"0.1.0"}')
    put(root, "src/specspec/__init__.py", '__version__ = "0.1.0"\n')
    put(root, "src/specspec/templates/AGENTS.md", "# Packaged current guide\n")
    put(root, "branding/activity-icon.svg", "<svg/>")
    put(root, "branding/app-icon.png", "icon")
    dist = root / "dist"
    dist.mkdir()
    with zipfile.ZipFile(dist / "specspec-0.1.0-py3-none-any.whl", "w") as package:
        for name in ["__init__.py", "templates/AGENTS.md"]:
            package.write(root / "src/specspec" / name, f"specspec/{name}")
        package.writestr(
            "specspec-0.1.0.dist-info/entry_points.txt",
            "[console_scripts]\nspecspec = specspec.cli:main\n",
        )
    with tarfile.open(dist / "specspec-0.1.0.tar.gz", "w:gz") as package:
        package.add(
            root / "src/specspec/templates/AGENTS.md",
            arcname="specspec-0.1.0/src/specspec/templates/AGENTS.md",
        )
    return root


def make_ui(root, platform):
    metadata = {
        "version": "0.1.0",
        "contributes": {
            "customEditors": [{"selector": [{"filenamePattern": "**/.specspec/???????=.md"}]}]
        },
    }
    with zipfile.ZipFile(root / "dist/specspec-vscode-0.1.0.vsix", "w") as package:
        for name in [
            "extension.vsixmanifest",
            "[Content_Types].xml",
            "extension/readme.md",
            "extension/LICENSE.txt",
            "extension/out/extension.js",
            "extension/out/common/host/session.cjs",
            "extension/media/graph.js",
        ]:
            package.writestr(name, "content")
        package.writestr("extension/package.json", json.dumps(metadata))
        package.writestr("extension/media/specspec.svg", "<svg/>")
        package.writestr("extension/media/app-icon.png", "icon")
        package.writestr(
            "extension/media/vendor/THIRD_PARTY_NOTICES.txt", "@codemirror/view\nd3-shape"
        )
    directory, _ = release.desktop_paths(root, platform, "x64")
    executable = put(directory, "SpecSpec.exe" if platform == "win32" else "SpecSpec", "binary")
    executable.chmod(0o755)
    put(directory, "LICENSES.chromium.html", "Chromium licenses")
    for name in [
        "main.cjs",
        "preload.cjs",
        "security.cjs",
        "store.cjs",
        "launch.cjs",
        "build/LICENSE",
        "build/app-icon.png",
        "build/common/host/session.cjs",
        "build/media/graph.js",
        "build/media/specspec.svg",
        "build/media/vendor/THIRD_PARTY_NOTICES.txt",
    ]:
        put(directory / "resources/app", name, "content")
    put(directory / "resources/app", "package.json", '{"version":"0.1.0"}')
    release.archive(root, platform, "x64")
    return directory


@pytest.mark.parametrize(
    "platform",
    [
        "win32",
        pytest.param(
            "linux",
            marks=pytest.mark.skipif(
                os.name == "nt", reason="POSIX executable modes need a POSIX filesystem."
            ),
        ),
    ],
)
def test_local_artifacts_get_hashes_and_preserve_target_archive_semantics(products, platform):
    root = products
    make_ui(root, platform)
    result = release.check(root, platform, "x64")
    assert result["version"] == "0.1.0" and len(result["artifacts"]) == 4
    assert all(len(a["sha256"]) == 64 and a["bytes"] > 0 for a in result["artifacts"].values())
    assert (root / "dist/SHA256SUMS").is_file()
    assert json.loads((root / "dist/release-manifest.json").read_text())["platform"] == platform
    assert not (root / ".git").exists() and not (root / ".specspec").exists()


def test_versions_must_agree(products):
    put(products, "vscode/package.json", '{"version":"0.2.0"}')
    with pytest.raises(ValueError, match="Version mismatch"):
        release.version(products)


@pytest.mark.parametrize("change", ["guide", "python"])
def test_wheel_must_contain_current_cli_and_guide(products, change):
    path = "templates/AGENTS.md" if change == "guide" else "__init__.py"
    put(products, f"src/specspec/{path}", '__version__ = "0.1.0"\n# changed source\n')
    with pytest.raises(ValueError, match="guide differs|stale CLI code"):
        release.check(products, "win32", "x64")


def test_portable_archive_rejects_development_files(products):
    directory = make_ui(products, "win32")
    put(directory / "resources/app", "test/probe.cjs", "not runtime")
    with pytest.raises(ValueError, match="unintended runtime files"):
        release.archive(products, "win32", "x64")


def test_vsix_rejects_development_material(products):
    make_ui(products, "win32")
    with zipfile.ZipFile(products / "dist/specspec-vscode-0.1.0.vsix", "a") as package:
        package.writestr("extension/node_modules/private/file", "no")
    with pytest.raises(ValueError, match="development-only"):
        release.check(products, "win32", "x64")


@pytest.mark.parametrize(
    "name", ["../escape", "/absolute", "x/../../escape", "a\\b", "C:/absolute", "a/./b", "a//b"]
)
def test_package_paths_cannot_escape(name):
    with pytest.raises(ValueError, match="Unsafe package member"):
        release.safe_names([name])


def test_real_monorepo_versions_and_packaged_resource_are_aligned():
    root = Path(__file__).resolve().parents[1]
    assert release.version(root) == "0.1.0"
    assert (root / "src/specspec/templates/AGENTS.md").is_file()
    metadata = json.loads((root / "package.json").read_text())
    assert metadata["private"] is True
    assert metadata["workspaces"] == ["graph-ui-common", "vscode", "electron"]
    lock = json.loads((root / "package-lock.json").read_text())
    assert lock["packages"][""]["workspaces"] == metadata["workspaces"]
    for workspace in metadata["workspaces"]:
        assert not (root / workspace / "package-lock.json").exists()
