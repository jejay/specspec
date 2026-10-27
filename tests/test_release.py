"""Artifact inspectors reject stale or incomplete packages without publishing."""

import io
import json
import os
import tarfile
import zipfile
from pathlib import Path

import pytest

from tools import pypi_release, release

VERSION = "0.0.1"


def put(root, path, content=b""):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content.encode() if isinstance(content, str) else content)
    return target


@pytest.fixture
def products(tmp_path):
    root = tmp_path
    put(root, "pyproject.toml", f'[project]\nname = "specspec"\nversion = "{VERSION}"\n')
    for path in [
        "package.json",
        "vscode/package.json",
        "electron/package.json",
        "graph-ui-common/package.json",
    ]:
        put(root, path, json.dumps({"version": VERSION}))
    lock = {"version": VERSION, "packages": {}}
    for path in ["", "vscode", "electron", "graph-ui-common"]:
        lock["packages"][path] = {"version": VERSION}
    put(root, "package-lock.json", json.dumps(lock))
    put(root, "src/specspec/__init__.py", f'__version__ = "{VERSION}"\n')
    put(root, "src/specspec/templates/AGENTS.md", "# Packaged current guide\n")
    put(root, "README.md", "# Package introduction\n")
    put(root, "branding/activity-icon.svg", "<svg/>")
    put(root, "branding/app-icon.png", "icon")
    dist = root / "dist"
    dist.mkdir()
    metadata = f"Metadata-Version: 2.4\nName: specspec\nVersion: {VERSION}\n\n"
    with zipfile.ZipFile(dist / f"specspec-{VERSION}-py3-none-any.whl", "w") as package:
        for name in ["__init__.py", "templates/AGENTS.md"]:
            package.write(root / "src/specspec" / name, f"specspec/{name}")
        package.writestr(f"specspec-{VERSION}.dist-info/METADATA", metadata)
        package.writestr(
            f"specspec-{VERSION}.dist-info/entry_points.txt",
            "[console_scripts]\nspecspec = specspec.cli:main\n",
        )
    with tarfile.open(dist / f"specspec-{VERSION}.tar.gz", "w:gz") as package:
        for name in ["__init__.py", "templates/AGENTS.md"]:
            package.add(
                root / "src/specspec" / name,
                arcname=f"specspec-{VERSION}/src/specspec/{name}",
            )
        package.add(root / "README.md", arcname=f"specspec-{VERSION}/README.md")
        item = tarfile.TarInfo(f"specspec-{VERSION}/PKG-INFO")
        item.size = len(metadata.encode())
        package.addfile(item, io.BytesIO(metadata.encode()))
    return root


def make_ui(root, platform):
    metadata = {
        "name": "specspec-vscode",
        "displayName": "specspec-vscode",
        "version": VERSION,
        "contributes": {
            "customEditors": [{"selector": [{"filenamePattern": "**/.specspec/???????=.md"}]}]
        },
    }
    with zipfile.ZipFile(root / f"dist/specspec-vscode-{VERSION}.vsix", "w") as package:
        for name in [
            "extension.vsixmanifest",
            "[Content_Types].xml",
            "extension/readme.md",
            "extension/LICENSE.txt",
            "extension/out/extension.js",
            "extension/out/common/host/session.cjs",
            "extension/out/common/host/startup.cjs",
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
    executable = put(
        directory, "specspec-desktop.exe" if platform == "win32" else "specspec-desktop", "binary"
    )
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
        "build/common/host/startup.cjs",
        "build/media/graph.js",
        "build/media/specspec.svg",
        "build/media/vendor/THIRD_PARTY_NOTICES.txt",
    ]:
        put(directory / "resources/app", name, "content")
    put(
        directory / "resources/app",
        "package.json",
        json.dumps(
            {"version": VERSION, "name": "specspec-desktop", "productName": "specspec-desktop"}
        ),
    )
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
    assert result["version"] == VERSION and len(result["artifacts"]) == 4
    assert all(len(a["sha256"]) == 64 and a["bytes"] > 0 for a in result["artifacts"].values())
    assert (root / "dist/SHA256SUMS").is_file()
    assert json.loads((root / "dist/release-manifest.json").read_text())["platform"] == platform
    assert not (root / ".git").exists() and not (root / ".specspec").exists()


def test_versions_must_agree(products):
    put(products, "vscode/package.json", '{"version":"9.9.9"}')
    with pytest.raises(ValueError, match="Version mismatch"):
        release.version(products)


@pytest.mark.parametrize("workspace", [None, "", "vscode", "electron", "graph-ui-common"])
def test_lockfile_versions_must_agree(products, workspace):
    lock = json.loads((products / "package-lock.json").read_text())
    target = lock if workspace is None else lock["packages"][workspace]
    target["version"] = "9.9.9"
    put(products, "package-lock.json", json.dumps(lock))
    with pytest.raises(ValueError, match="Version mismatch"):
        release.version(products)


@pytest.mark.parametrize("change", ["guide", "python"])
def test_wheel_must_contain_current_cli_and_guide(products, change):
    path = "templates/AGENTS.md" if change == "guide" else "__init__.py"
    put(products, f"src/specspec/{path}", f'__version__ = "{VERSION}"\n# changed source\n')
    with pytest.raises(ValueError, match="guide differs|stale CLI code"):
        release.check(products, "win32", "x64")


def test_portable_archive_rejects_development_files(products):
    directory = make_ui(products, "win32")
    put(directory / "resources/app", "test/probe.cjs", "not runtime")
    with pytest.raises(ValueError, match="unintended runtime files"):
        release.archive(products, "win32", "x64")


def test_vsix_rejects_development_material(products):
    make_ui(products, "win32")
    with zipfile.ZipFile(products / f"dist/specspec-vscode-{VERSION}.vsix", "a") as package:
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
    assert release.version(root) == VERSION
    import tomllib

    assert tomllib.loads((root / "pyproject.toml").read_text())["project"]["name"] == "specspec"
    vscode = json.loads((root / "vscode/package.json").read_text())
    assert vscode["name"] == vscode["displayName"] == "specspec-vscode"
    desktop = json.loads((root / "electron/package.json").read_text())
    assert desktop["name"] == desktop["productName"] == "specspec-desktop"
    assert (root / "src/specspec/templates/AGENTS.md").is_file()
    metadata = json.loads((root / "package.json").read_text())
    assert metadata["private"] is True
    assert metadata["workspaces"] == ["graph-ui-common", "vscode", "electron"]
    lock = json.loads((root / "package-lock.json").read_text())
    assert lock["packages"][""]["workspaces"] == metadata["workspaces"]
    for workspace in metadata["workspaces"]:
        assert not (root / workspace / "package-lock.json").exists()


def test_python_publication_verifies_exact_two_artifacts(products):
    report = pypi_release.verify(products, products / "dist", VERSION)
    assert report["version"] == VERSION and len(report["artifacts"]) == 2
    assert all(len(item["sha256"]) == 64 for item in report["artifacts"].values())
    assert not (products / ".git").exists()


@pytest.mark.parametrize("expected", ["9.9.9", "v0.0.1", "00.0.1", "0.0.1\n", "0.0.1; false"])
def test_publication_rejects_wrong_or_noncanonical_expected_version(products, expected):
    with pytest.raises(ValueError, match="Expected"):
        pypi_release.verify(products, products / "dist", expected)


@pytest.mark.parametrize("name", ["old.whl", "ui.vsix", "desktop.tar.gz", "SHA256SUMS"])
def test_publication_directory_contains_no_other_files(products, name):
    put(products, "dist/" + name, "unintended upload")
    with pytest.raises(ValueError, match="exactly one expected"):
        pypi_release.verify(products, products / "dist", VERSION)


@pytest.mark.parametrize("path", ["src/specspec/__init__.py", "src/specspec/templates/AGENTS.md"])
def test_publication_rejects_stale_wheel_source_and_guide(products, path):
    target = products / path
    target.write_bytes(target.read_bytes() + b"\n# changed\n")
    with pytest.raises(ValueError, match="stale source/resource"):
        pypi_release.verify(products, products / "dist", VERSION)


def test_publication_rejects_stale_sdist_readme(products):
    put(products, "README.md", "# Updated introduction\n")
    with pytest.raises(ValueError, match="stale README"):
        pypi_release.verify(products, products / "dist", VERSION)


@pytest.mark.parametrize(
    "headers",
    [
        b"Name: other\nVersion: 0.0.1\n\n",
        b"Name: specspec\nVersion: 9.9.9\n\n",
        b"Name: specspec\nName: other\nVersion: 0.0.1\n\n",
    ],
)
def test_distribution_identity_is_not_inferred_only_from_filename(headers):
    with pytest.raises(ValueError, match="Distribution metadata"):
        pypi_release.metadata(headers, VERSION)


@pytest.mark.parametrize("name", ["../escape", "ui/runtime.js", "node_modules/other.js"])
def test_publication_rejects_non_cli_or_unsafe_wheel_members(products, name):
    with zipfile.ZipFile(products / f"dist/specspec-{VERSION}-py3-none-any.whl", "a") as package:
        package.writestr(name, "unintended")
    with pytest.raises(ValueError, match="Unsafe package member|non-CLI"):
        pypi_release.verify(products, products / "dist", VERSION)


def test_publication_rejects_duplicate_wheel_entries(products):
    with zipfile.ZipFile(products / f"dist/specspec-{VERSION}-py3-none-any.whl", "a") as package:
        with pytest.warns(UserWarning, match="Duplicate"):
            package.writestr("specspec/__init__.py", "other")
    with pytest.raises(ValueError, match="duplicate members"):
        pypi_release.verify(products, products / "dist", VERSION)


def test_publication_rejects_sdist_links_without_extracting_them(products):
    path = products / f"dist/specspec-{VERSION}.tar.gz"
    with tarfile.open(path) as package:
        members = [(item, package.extractfile(item).read()) for item in package.getmembers()]
    with tarfile.open(path, "w:gz") as package:
        for item, raw in members:
            package.addfile(item, io.BytesIO(raw))
        link = tarfile.TarInfo(f"specspec-{VERSION}/escape")
        link.type = tarfile.SYMTYPE
        link.linkname = "../../outside"
        package.addfile(link)
    with pytest.raises(ValueError, match="unsafe member/type"):
        pypi_release.verify(products, products / "dist", VERSION)
    assert not (products.parent / "outside").exists()
