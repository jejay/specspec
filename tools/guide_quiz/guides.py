"""Guide versions by name.

``shipped`` is the package template, the text that ``specspec init`` writes. Every other
name is a file under ``guides/``: dated states of the shipped guide that earlier results
refer to, and experimental variants under ``guides/experiments/``.
"""

from __future__ import annotations

from pathlib import Path

FOLDER = Path(__file__).resolve().parent / "guides"
TEMPLATE = Path(__file__).resolve().parents[2] / "src/specspec/templates/AGENTS.md"
SHIPPED = "shipped"


def files() -> dict[str, Path]:
    """Every kept version by its file stem."""
    found: dict[str, Path] = {}
    for path in sorted(FOLDER.rglob("*.md")):
        if path.stem in found or path.stem == SHIPPED:
            raise ValueError(f"Guide name is used twice: {path.stem}")
        found[path.stem] = path
    return found


def names() -> list[str]:
    return [SHIPPED, *files()]


def text(name: str) -> str:
    """The guide text with LF line endings."""
    path = TEMPLATE if name == SHIPPED else files().get(name)
    if path is None:
        raise ValueError(f"Unknown guide {name!r}. Known: {', '.join(names())}")
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def size(name: str) -> int:
    return len(text(name).encode("utf-8"))
