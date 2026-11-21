"""The packaged agent guide, the instructions file that holds it and its exact-match placement."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from importlib.resources import files as package_files
from pathlib import Path

from .model import Diagnostic, SpecError

INSTRUCTIONS = "AGENTS.md"
# Files that can hold the guide, in the order in which a project without a guide chooses.
GUIDE_FILES = (INSTRUCTIONS, "CLAUDE.md", ".claude/CLAUDE.md")
# Claude Code reads these, and reads AGENTS.md only when none of them exists.
CLAUDE_FILES = ("CLAUDE.md", ".claude/CLAUDE.md", "CLAUDE.local.md")
INSTRUCTION_FILES = (INSTRUCTIONS, *CLAUDE_FILES)
MAX_INSTRUCTIONS_BYTES = 16 * 1024 * 1024
FENCE = re.compile(r"^\s*(```|~~~)")


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


def edited_guide_error(name: str = INSTRUCTIONS) -> SpecError:
    from . import __version__

    return SpecError(
        [
            Diagnostic(
                "GUIDE",
                f"{name} holds a specspec guide that matches no guide a release shipped, "
                "probably because it was edited by hand, so nothing was changed. Run "
                "`specspec guide --print` to get the guide of specspec "
                f"{__version__} and put it in place of the old guide section, keeping "
                "your own edits where you want them.",
                name,
            )
        ]
    )


def appended(original: bytes, text: bytes) -> bytes:
    """TEXT after ORIGINAL in the file's own line endings, after a blank line."""
    crlf = uses_crlf(original)
    newline = b"\r\n" if crlf else b"\n"
    separator = (
        b""
        if not original or original.endswith((b"\n\n", b"\r\n\r\n"))
        else newline
        if original.endswith((b"\n", b"\r"))
        else newline * 2
    )
    return original + separator + with_endings(text, crlf)


def place_guide(original: bytes | None) -> tuple[bytes, str]:
    """Instructions bytes that hold the current guide once, and what was done to get them.

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
    return appended(original, current), "appended"


@dataclass(frozen=True)
class InstructionFile:
    """An instructions file: its name in the project root and where its bytes live."""

    name: str
    path: Path  # the resolved file; for a symbolic link, the file it points to
    data: bytes | None  # None when the file is absent
    shown: str  # the resolved file's path relative to the project


def instruction_problem(message: str, name: str) -> SpecError:
    return SpecError([Diagnostic("INSTRUCTIONS", message, name)])


def locate(root: Path, name: str) -> InstructionFile:
    """Read the instructions file NAME, through a symbolic link to a file in the project."""
    project = root.resolve()
    link = root / name
    shape = f"{name} must be a regular file, a link to one inside the project, or absent."
    try:
        path = link.resolve()
    except (OSError, RuntimeError) as error:
        raise instruction_problem(f"{name} cannot be resolved ({error}). {shape}", name) from error
    if not path.is_relative_to(project):
        raise instruction_problem(f"{name} leads outside the project, to {path}. {shape}", name)
    if path.is_relative_to(project / ".specspec"):
        raise instruction_problem(f"{name} leads into .specspec. {shape}", name)
    shown = path.relative_to(project).as_posix()
    if not link.is_symlink() and not path.exists():
        return InstructionFile(name, path, None, shown)
    if not path.exists():
        raise instruction_problem(f"{name} links to a missing file. {shape}", name)
    if not path.is_file():
        raise instruction_problem(shape, name)
    with path.open("rb") as stream:
        data = stream.read(MAX_INSTRUCTIONS_BYTES + 1)
    if len(data) > MAX_INSTRUCTIONS_BYTES:
        raise instruction_problem(f"{name} exceeds the 16 MiB limit.", name)
    return InstructionFile(name, path, data, shown)


def guide_file(root: Path) -> InstructionFile:
    """The instructions file that holds the guide or receives it.

    That is the file among AGENTS.md, CLAUDE.md and .claude/CLAUDE.md that holds a guide
    heading, otherwise the first of them that exists, otherwise a new AGENTS.md. Names
    that lead to the same file count once, under the first of them.
    """
    present: dict[Path, InstructionFile] = {}
    for name in GUIDE_FILES:
        found = locate(root, name)
        if found.data is not None:
            present.setdefault(found.path, found)
    for found in present.values():
        if holds_heading(found.data or b""):
            return found
    return next(iter(present.values()), None) or locate(root, INSTRUCTIONS)


def import_line(name: str) -> bytes:
    """The import of the root AGENTS.md, written relative to the instructions file NAME."""
    return b"@../AGENTS.md" if "/" in name else b"@AGENTS.md"


def imports_guide(data: bytes, name: str) -> bool:
    """Whether DATA imports the root AGENTS.md outside code spans and fenced blocks."""
    forms = {"@../AGENTS.md"} if "/" in name else {"@AGENTS.md", "@./AGENTS.md"}
    fenced = False
    for line in data.decode("utf-8", errors="replace").splitlines():
        if FENCE.match(line):
            fenced = not fenced
        elif not fenced and forms & set(line.split()):
            return True
    return False


def claude_import(root: Path, guide: InstructionFile) -> tuple[InstructionFile, bytes] | None:
    """The Claude Code instructions file that has to import AGENTS.md, with its new bytes.

    Claude Code reads AGENTS.md only in a project without CLAUDE.md, .claude/CLAUDE.md
    and CLAUDE.local.md. When the guide is in AGENTS.md and one of these exists, the
    first that exists imports it, unless one of them already does or is AGENTS.md itself.
    """
    if guide.name != INSTRUCTIONS:
        return None
    claude = [found for name in CLAUDE_FILES if (found := locate(root, name)).data is not None]
    if not claude or any(
        found.path == guide.path or imports_guide(found.data or b"", found.name) for found in claude
    ):
        return None
    first = claude[0]
    return first, appended(first.data or b"", import_line(first.name) + b"\n")


def write_instructions(root: Path, found: InstructionFile, data: bytes) -> None:
    """Replace FOUND's bytes with DATA unless the file changed since it was read."""
    temporary = found.path.parent / f".{found.path.name}.specspec-{os.getpid()}"
    try:
        with temporary.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        now = locate(root, found.name)
        if now.path != found.path or now.data != found.data:
            raise SpecError(
                [Diagnostic("CONCURRENT", f"{found.name} changed while the guide was placed.")]
            )
        os.replace(temporary, found.path)
    finally:
        temporary.unlink(missing_ok=True)


@dataclass(frozen=True)
class GuidePlacement:
    """The file that holds the guide, what was done to it and the file that imports it."""

    shown: str
    action: str
    imported_by: str | None = None


def refresh_guide(root: Path) -> GuidePlacement:
    """Bring the project's instructions to the current guide, placed as init places it."""
    guide = guide_file(root)
    data, action = place_guide(guide.data)
    if action == "edited":
        raise edited_guide_error(guide.shown)
    importer = claude_import(root, guide)
    if action != "current":
        write_instructions(root, guide, data)
    if importer is not None:
        write_instructions(root, *importer)
    return GuidePlacement(guide.shown, action, importer[0].shown if importer else None)
