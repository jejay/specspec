"""The packaged agent guide and its exact-match placement in a project's AGENTS.md."""

from __future__ import annotations

import os
from importlib.resources import files as package_files
from pathlib import Path

from .model import Diagnostic, SpecError

INSTRUCTIONS = "AGENTS.md"
MAX_INSTRUCTIONS_BYTES = 16 * 1024 * 1024


def current_guide() -> bytes:
    """The guide this release ships, with LF line endings."""
    return package_files("specspec").joinpath("templates/AGENTS.md").read_bytes()


def earlier_guides() -> dict[str, bytes]:
    """The guide of every earlier release, keyed by that release's version."""
    folder = package_files("specspec").joinpath("templates/earlier")
    return {
        entry.name.removesuffix(".md"): entry.read_bytes()
        for entry in sorted(folder.iterdir(), key=lambda item: item.name)
        if entry.name.endswith(".md")
    }


def with_endings(text: bytes, crlf: bool) -> bytes:
    lf = text.replace(b"\r\n", b"\n")
    return lf.replace(b"\n", b"\r\n") if crlf else lf


def uses_crlf(data: bytes) -> bool:
    end = data.find(b"\n")
    return end > 0 and data[end - 1 : end] == b"\r"


def headings() -> set[str]:
    """The first lines of all shipped guides, which mark a guide even after hand edits."""
    return {
        guide.split(b"\n", 1)[0].rstrip(b"\r").decode("utf-8").strip().casefold()
        for guide in (current_guide(), *earlier_guides().values())
    }


def holds_heading(data: bytes) -> bool:
    marks = headings()
    return any(
        line.strip().casefold() in marks
        for line in data.decode("utf-8", errors="replace").splitlines()
    )


def edited_guide_error() -> SpecError:
    from . import __version__

    return SpecError(
        [
            Diagnostic(
                "GUIDE",
                "AGENTS.md holds a specspec guide that matches no guide a release shipped, "
                "probably because it was edited by hand, so nothing was changed. Run "
                "`specspec guide --print` to get the guide of specspec "
                f"{__version__} and put it in place of the old guide section, keeping "
                "your own edits where you want them.",
                INSTRUCTIONS,
            )
        ]
    )


def place_guide(original: bytes | None) -> tuple[bytes, str]:
    """AGENTS.md bytes that hold the current guide once, and what was done to get them.

    The current guide, or the guide of an earlier release, is found by exact match in
    LF or CRLF line endings; an earlier guide is replaced in place in the same line
    endings and every other byte stays. A file without any guide gets the guide
    appended in its own line endings. Actions: created, current, replaced, appended,
    or edited when a guide heading has no exact shipped text (nothing changes).
    """
    current = current_guide()
    if original is None:
        return current, "created"
    for crlf in (False, True):
        if with_endings(current, crlf) in original:
            return original, "current"
    for guide in earlier_guides().values():
        for crlf in (False, True):
            found = with_endings(guide, crlf)
            if found in original:
                return original.replace(found, with_endings(current, crlf), 1), "replaced"
    if holds_heading(original):
        return original, "edited"
    crlf = uses_crlf(original)
    newline = b"\r\n" if crlf else b"\n"
    separator = (
        b""
        if not original or original.endswith((b"\n\n", b"\r\n\r\n"))
        else newline
        if original.endswith((b"\n", b"\r"))
        else newline * 2
    )
    return original + separator + with_endings(current, crlf), "appended"


def read_instructions(path: Path) -> bytes | None:
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise SpecError([Diagnostic("INSTRUCTIONS", "AGENTS.md must be a regular file or absent.")])
    if not path.exists():
        return None
    with path.open("rb") as stream:
        data = stream.read(MAX_INSTRUCTIONS_BYTES + 1)
    if len(data) > MAX_INSTRUCTIONS_BYTES:
        raise SpecError([Diagnostic("INSTRUCTIONS", "AGENTS.md exceeds the 16 MiB limit.")])
    return data


def refresh_guide(root: Path) -> str:
    """Bring root/AGENTS.md to the current guide; the action names what happened."""
    path = root / INSTRUCTIONS
    original = read_instructions(path)
    data, action = place_guide(original)
    if action == "edited":
        raise edited_guide_error()
    if action == "current":
        return action
    temporary = root / f".{INSTRUCTIONS}.specspec-{os.getpid()}"
    try:
        with temporary.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if read_instructions(path) != original:
            raise SpecError(
                [Diagnostic("CONCURRENT", "AGENTS.md changed while the guide was placed.")]
            )
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    return action
