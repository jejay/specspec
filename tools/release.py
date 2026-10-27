"""Archive and inspect local artifacts. Never publish, tag, stage or commit.

Uses only the Python standard library; run after the root package scripts.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tarfile
import tomllib
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]


def version(root: Path) -> str:
    python = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf8"))["project"]
    expected = python["version"]
    for name in [
        "package.json",
        "vscode/package.json",
        "electron/package.json",
        "graph-ui-common/package.json",
    ]:
        metadata = json.loads((root / name).read_text(encoding="utf8"))
        if metadata["version"] != expected:
            raise ValueError(f"Version mismatch: {name}")
    if f'__version__ = "{expected}"' not in (root / "src/specspec/__init__.py").read_text(
        encoding="utf8"
    ):
        raise ValueError("Python runtime version differs from package metadata.")
    lock = json.loads((root / "package-lock.json").read_text(encoding="utf8"))
    if lock["version"] != expected:
        raise ValueError("Version mismatch: package-lock.json")
    for workspace in ["", "graph-ui-common", "vscode", "electron"]:
        if lock["packages"][workspace]["version"] != expected:
            raise ValueError(f"Version mismatch: package-lock.json workspace {workspace!r}")
    return expected


def target() -> tuple[str, str]:
    value = json.loads(
        subprocess.check_output(
            ["node", "-p", "JSON.stringify([process.platform,process.arch])"], text=True
        )
    )
    if value[0] not in {"win32", "linux"}:
        raise ValueError("Portable Electron release targets are Windows and Linux.")
    return tuple(value)


def desktop_paths(root: Path, platform: str, arch: str) -> tuple[Path, Path]:
    suffix = ".zip" if platform == "win32" else ".tar.gz"
    return (
        root / "dist/desktop" / f"specspec-desktop-{platform}-{arch}",
        root / "dist" / f"specspec-desktop-{version(root)}-{platform}-{arch}{suffix}",
    )


def runtime_check(directory: Path, platform: str):
    executable = directory / ("specspec-desktop.exe" if platform == "win32" else "specspec-desktop")
    if not executable.is_file():
        raise ValueError(f"Missing portable executable: {executable}")
    application = directory / "resources/app"
    allowed = {
        "package.json",
        "main.cjs",
        "preload.cjs",
        "security.cjs",
        "store.cjs",
        "launch.cjs",
        "build",
    }
    if {p.name for p in application.iterdir()} != allowed:
        raise ValueError("Portable application contains missing or unintended runtime files.")
    for name in [
        "build/LICENSE",
        "build/app-icon.png",
        "build/common/host/session.cjs",
        "build/common/host/startup.cjs",
        "build/media/graph.js",
        "build/media/specspec.svg",
        "build/media/vendor/THIRD_PARTY_NOTICES.txt",
    ]:
        if not (application / name).is_file():
            raise ValueError(f"Portable application is missing {name}")
    if not (directory / "LICENSES.chromium.html").is_file():
        raise ValueError("Missing Chromium license notices.")
    for path in directory.rglob("*"):
        if path.is_symlink() and not path.resolve().is_relative_to(directory.resolve()):
            raise ValueError(f"Archive symlink escapes package: {path}")


def archive(root: Path, platform: str, arch: str) -> Path:
    directory, output = desktop_paths(root, platform, arch)
    runtime_check(directory, platform)
    if platform == "win32":
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as package:
            for path in sorted(directory.rglob("*")):
                if path.is_file():
                    package.write(path, path.relative_to(directory.parent).as_posix())
    else:
        # tar retains executable modes and symlinks; uploading a raw folder does not.
        with tarfile.open(output, "w:gz") as package:
            package.add(directory, arcname=directory.name)
    print(f"Portable archive: {output}")
    return output


def safe_names(names):
    for name in names:
        path = PurePosixPath(name)
        if (
            not path.parts
            or path.is_absolute()
            or ".." in path.parts
            or ":" in path.parts[0]
            or "\\" in name
            or "\x00" in name
            or path.as_posix() != name.rstrip("/")
        ):
            raise ValueError(f"Unsafe package member: {name}")


def check(root: Path, platform: str, arch: str) -> dict:
    release = version(root)
    dist = root / "dist"
    wheel = dist / f"specspec-{release}-py3-none-any.whl"
    sdist = dist / f"specspec-{release}.tar.gz"
    vsix = dist / f"specspec-vscode-{release}.vsix"
    directory, portable = desktop_paths(root, platform, arch)
    guide = (root / "src/specspec/templates/AGENTS.md").read_bytes()
    with zipfile.ZipFile(wheel) as package:
        safe_names(package.namelist())
        if package.read("specspec/templates/AGENTS.md") != guide:
            raise ValueError("Wheel initialization guide differs from the current template.")
        for source in (root / "src/specspec").rglob("*.py"):
            if package.read(source.relative_to(root / "src").as_posix()) != source.read_bytes():
                raise ValueError(f"Wheel contains stale CLI code: {source}")
        entries = package.read(f"specspec-{release}.dist-info/entry_points.txt").decode("utf8")
        if "specspec = specspec.cli:main" not in entries:
            raise ValueError("Wheel has no specspec console entry point.")
        if any("node_modules" in name or ".specspec/" in name for name in package.namelist()):
            raise ValueError("CLI wheel contains project/UI material.")
    with tarfile.open(sdist) as package:
        safe_names(package.getnames())
        resource = package.extractfile(f"specspec-{release}/src/specspec/templates/AGENTS.md")
        if resource is None or resource.read() != guide:
            raise ValueError("Source distribution is missing the current initialization guide.")
    with zipfile.ZipFile(vsix) as package:
        names = package.namelist()
        safe_names(names)
        required = {
            "extension.vsixmanifest",
            "[Content_Types].xml",
            "extension/package.json",
            "extension/readme.md",
            "extension/LICENSE.txt",
            "extension/out/extension.js",
            "extension/out/common/host/session.cjs",
            "extension/out/common/host/startup.cjs",
            "extension/media/graph.js",
            "extension/media/specspec.svg",
            "extension/media/app-icon.png",
            "extension/media/vendor/THIRD_PARTY_NOTICES.txt",
        }
        if missing := required - set(names):
            raise ValueError(f"VSIX is missing runtime files: {sorted(missing)}")
        if any(
            any(
                part in {"node_modules", "src", "test", "test-host", ".specspec"}
                for part in PurePosixPath(name).parts
            )
            for name in names
        ):
            raise ValueError("VSIX contains development-only material.")
        metadata = json.loads(package.read("extension/package.json"))
        if (
            metadata.get("name") != "specspec-vscode"
            or metadata.get("displayName") != "specspec-vscode"
        ):
            raise ValueError("VSIX product naming differs from the current release.")
        if metadata["version"] != release or metadata["contributes"]["customEditors"][0][
            "selector"
        ] != [{"filenamePattern": "**/.specspec/???????=.md"}]:
            raise ValueError("VSIX version/path contract differs from the current release.")
        for filename, source in [
            ("extension/media/specspec.svg", "branding/activity-icon.svg"),
            ("extension/media/app-icon.png", "branding/app-icon.png"),
        ]:
            if package.read(filename) != (root / source).read_bytes():
                raise ValueError(f"VSIX identity asset differs: {filename}")
        notices = package.read("extension/media/vendor/THIRD_PARTY_NOTICES.txt").decode("utf8")
        if "@codemirror/view" not in notices or "d3-shape" not in notices:
            raise ValueError("VSIX dependency license notices are incomplete.")
    runtime_check(directory, platform)
    application = directory / "resources/app"
    metadata = json.loads((application / "package.json").read_text(encoding="utf8"))
    if metadata["version"] != release:
        raise ValueError("Desktop version differs from the current release.")
    if (
        metadata.get("name") != "specspec-desktop"
        or metadata.get("productName") != "specspec-desktop"
    ):
        raise ValueError("Desktop product naming differs from the current release.")
    if platform == "win32":
        with zipfile.ZipFile(portable) as package:
            safe_names(package.namelist())
            if (
                package.read(f"{directory.name}/resources/app/main.cjs")
                != (application / "main.cjs").read_bytes()
            ):
                raise ValueError("Portable archive has stale runtime code.")
    else:
        with tarfile.open(portable) as package:
            safe_names(package.getnames())
            member = package.getmember(f"{directory.name}/specspec-desktop")
            if not member.mode & 0o111:
                raise ValueError("Linux portable archive lost executable permissions.")
    artifacts = {}
    for path in [wheel, sdist, vsix, portable]:
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        artifacts[path.name] = {"sha256": digest, "bytes": path.stat().st_size}
    report = {"version": release, "platform": platform, "arch": arch, "artifacts": artifacts}
    (dist / "release-manifest.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf8"
    )
    (dist / "SHA256SUMS").write_text(
        "".join(f"{value['sha256']}  {name}\n" for name, value in artifacts.items()),
        encoding="utf8",
    )
    print(json.dumps(report, indent=2))
    return report


def main():
    if sys.argv[1:] not in (["archive"], ["check"]):
        raise SystemExit("Usage: python tools/release.py archive|check")
    platform, arch = target()
    (archive if sys.argv[1] == "archive" else check)(ROOT, platform, arch)


if __name__ == "__main__":
    main()
