"""Validate and smoke-test the two Python distributions; publication belongs to CI."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import venv
import zipfile
from email import policy
from email.parser import BytesParser
from pathlib import Path

from tools.release import ROOT, safe_names, version


def expected_version(root: Path, expected: str) -> str:
    if not re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", expected):
        raise ValueError("Expected version must be a canonical X.Y.Z release.")
    actual = version(root)
    if actual != expected:
        raise ValueError(f"Expected release {expected}, found {actual}.")
    return actual


def metadata(raw: bytes, release: str):
    value = BytesParser(policy=policy.default).parsebytes(raw)
    if value.get_all("Name") != ["specspec"] or value.get_all("Version") != [release]:
        raise ValueError("Distribution metadata does not identify the expected specspec release.")


def verify(root: Path, directory: Path, expected: str) -> dict:
    release = expected_version(root, expected)
    names = {f"specspec-{release}-py3-none-any.whl", f"specspec-{release}.tar.gz"}
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("Distribution directory must be a real directory.")
    if {p.name for p in directory.iterdir()} != names:
        raise ValueError("Publish exactly one expected CLI wheel and source distribution.")
    if any(p.is_symlink() or not p.is_file() for p in directory.iterdir()):
        raise ValueError("Distributions must be regular files, not symlinks.")
    sources = {
        p.relative_to(root / "src").as_posix(): p.read_bytes()
        for p in (root / "src/specspec").rglob("*.py")
    }
    sources["specspec/templates/AGENTS.md"] = (
        root / "src/specspec/templates/AGENTS.md"
    ).read_bytes()
    wheel = directory / f"specspec-{release}-py3-none-any.whl"
    with zipfile.ZipFile(wheel) as package:
        members = package.namelist()
        safe_names(members)
        if len(members) != len(set(members)):
            raise ValueError("Wheel contains duplicate members.")
        info = f"specspec-{release}.dist-info"
        if any(name.split("/", 1)[0] not in {"specspec", info} for name in members):
            raise ValueError("Wheel contains non-CLI material.")
        if sum(item.file_size for item in package.infolist()) > 32 * 1024 * 1024:
            raise ValueError("Wheel exceeds the 32 MiB inspection limit.")
        metadata(package.read(f"{info}/METADATA"), release)
        entries = package.read(f"{info}/entry_points.txt").decode("utf8")
        if "specspec = specspec.cli:main" not in entries:
            raise ValueError("Wheel has no specspec console entry point.")
        for path, raw in sources.items():
            if package.read(path) != raw:
                raise ValueError(f"Wheel contains stale source/resource: {path}")
    with tarfile.open(directory / f"specspec-{release}.tar.gz") as package:
        members = package.getmembers()
        safe_names([item.name for item in members])
        if len(members) != len({item.name for item in members}):
            raise ValueError("Source distribution contains duplicate members.")
        prefix = f"specspec-{release}/"
        if any(
            (item.name != prefix[:-1] and not item.name.startswith(prefix))
            or not (item.isfile() or item.isdir())
            for item in members
        ):
            raise ValueError("Source distribution has an unsafe member/type.")
        if sum(item.size for item in members) > 32 * 1024 * 1024:
            raise ValueError("Source distribution exceeds the 32 MiB inspection limit.")

        def content(name):
            stream = package.extractfile(prefix + name)
            if stream is None:
                raise ValueError(f"Source distribution is missing {name}.")
            return stream.read()

        metadata(content("PKG-INFO"), release)
        for path, raw in sources.items():
            if content("src/" + path) != raw:
                raise ValueError(f"Source distribution contains stale source/resource: {path}")
        if content("README.md") != (root / "README.md").read_bytes():
            raise ValueError("Source distribution has a stale README.")
    return {
        "version": release,
        "artifacts": {
            name: {
                "sha256": hashlib.sha256((directory / name).read_bytes()).hexdigest(),
                "bytes": (directory / name).stat().st_size,
            }
            for name in sorted(names)
        },
    }


def smoke(root: Path, directory: Path, expected: str) -> dict:
    report = verify(root, directory, expected)
    container = Path(tempfile.mkdtemp(prefix="specspec-python-release-"))
    report["installed"] = []
    env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}}
    env.update(PYTHONNOUSERSITE="1", PYTHONIOENCODING="utf-8")

    def run(args, cwd, stdin=None):
        result = subprocess.run(
            [str(arg) for arg in args],
            cwd=cwd,
            env=env,
            input=stdin,
            capture_output=True,
            timeout=180,
        )
        if result.returncode:
            raise ValueError(
                f"Release smoke failed: {args[0]} {args[1:]}\n"
                + (result.stdout + result.stderr).decode("utf8", errors="replace")
            )
        return result.stdout.decode("utf8")

    try:
        for kind, filename in zip(("wheel", "sdist"), sorted(report["artifacts"]), strict=True):
            environment = container / kind
            venv.EnvBuilder(with_pip=True).create(environment)
            binary = environment / ("Scripts" if os.name == "nt" else "bin")
            python = binary / ("python.exe" if os.name == "nt" else "python")
            command = binary / ("specspec.exe" if os.name == "nt" else "specspec")
            run(
                [
                    python,
                    "-m",
                    "pip",
                    "--isolated",
                    "install",
                    "--index-url",
                    "https://pypi.org/simple",
                    directory.resolve() / filename,
                ],
                container,
            )
            project = container / f"{kind}-project"
            project.mkdir()
            origin = Path(
                run([python, "-c", "import specspec; print(specspec.__file__)"], project).strip()
            )
            if not origin.resolve().is_relative_to(environment.resolve()):
                raise ValueError("Smoke imported the checkout instead of the installed package.")
            if expected not in run([command, "--version"], project):
                raise ValueError("Installed CLI has the wrong version.")
            help_text = run([command, "--help"], project)
            if any(flag in help_text for flag in ("--root", "--json", "--body")):
                raise ValueError("Installed help exposes integration/removed body controls.")
            prefix = b"# Owner instructions\r\nPreserve these bytes."
            (project / "AGENTS.md").write_bytes(prefix)
            receipt = json.loads(run([command, "init", "-m", "# Release smoke", "--json"], project))
            identity = receipt["result"]["changed_ids"][0]
            guide = (project / "AGENTS.md").read_bytes()
            if not guide.startswith(prefix) or not guide.endswith(
                (root / "src/specspec/templates/AGENTS.md").read_bytes()
            ):
                raise ValueError("Installed init failed exact-prefix guide concatenation.")
            if not (project / ".git").exists():
                raise ValueError("Installed init did not establish Git.")
            body = "# Automatic stdin\n\nLiteral release smoke text.\n"
            run([command, "update", identity], project, body.encode())
            result = json.loads(
                run([command, "query", identity, "--max-distance", "0", "--json"], project)
            )
            node = result["result"]["target"]["nodes"][0]
            if node["body"] != body:
                raise ValueError("Installed CLI did not preserve the supplied stdin body.")
            run([command, "check", "--sources", "--warnings-as-errors"], project)
            report["installed"].append({"kind": kind, "artifact": filename, "origin": str(origin)})
    except BaseException:
        print(f"Release smoke evidence retained: {container}", file=sys.stderr)
        raise
    shutil.rmtree(container)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["version", "verify", "smoke"])
    parser.add_argument("--expected", required=True)
    parser.add_argument("--directory", type=Path, default=ROOT / "dist/pypi")
    args = parser.parse_args()
    try:
        if args.operation == "version":
            print(expected_version(ROOT, args.expected))
        else:
            operation = verify if args.operation == "verify" else smoke
            print(json.dumps(operation(ROOT, args.directory, args.expected), indent=2))
    except (ValueError, OSError, KeyError, zipfile.BadZipFile, tarfile.TarError) as error:
        raise SystemExit(str(error)) from error


if __name__ == "__main__":
    main()
