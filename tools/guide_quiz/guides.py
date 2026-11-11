"""Guide versions by name.

Every name is a file under ``guides/``: dated states of the shipped guide and experimental
variants under ``guides/experiments/``. ``shipped`` stands for the package template, the
text that ``specspec init`` writes. A result must name a text that stays available, so
``shipped`` resolves to the kept file with the template's exact content.
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
    return list(files())


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def resolve(name: str) -> str:
    """The kept name behind ``shipped``; any other known name stays as it is."""
    kept = files()
    if name != SHIPPED:
        if name not in kept:
            raise ValueError(f"Unknown guide {name!r}. Known: {', '.join(kept)}")
        return name
    template = read(TEMPLATE)
    for stem, path in kept.items():
        if path.parent == FOLDER and read(path) == template:
            return stem
    raise ValueError(
        "The shipped guide has no kept copy. Copy src/specspec/templates/AGENTS.md to "
        "tools/guide_quiz/guides/ under a dated name, so that results name a text that stays."
    )


def text(name: str) -> str:
    """The guide text with LF line endings."""
    return read(files()[resolve(name)])


def size(name: str) -> int:
    return len(text(name).encode("utf-8"))
