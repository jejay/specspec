"""Raw answers and grades as JSON lines on the developer's machine.

Every process appends to a file of its own, so that runs in parallel never interleave
their lines. Readers take all files of a kind together.
"""

from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path

DEFAULT = Path(__file__).resolve().parent / "results"
KINDS = ("dilemmas", "tasks", "grades")


def folder() -> Path:
    """The results folder: ``GUIDE_QUIZ_RESULTS`` or ``results/`` beside the tool."""
    return Path(os.environ.get("GUIDE_QUIZ_RESULTS") or DEFAULT)


class Log:
    """Append records of one kind for the lifetime of this process."""

    def __init__(self, kind: str, directory: Path | None = None):
        if kind not in KINDS:
            raise ValueError(kind)
        directory = directory or folder()
        directory.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        self.path = directory / f"{kind}-{stamp}-{os.getpid()}.jsonl"
        self._lock = threading.Lock()

    def append(self, record: dict) -> None:
        line = json.dumps(record, ensure_ascii=False) + "\n"
        with self._lock, self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line)


def load(kind: str, directory: Path | None = None) -> list[dict]:
    """All records of a kind, oldest file first; a damaged line is skipped."""
    records = []
    for path in sorted((directory or folder()).glob(f"{kind}-*.jsonl")):
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except ValueError:
                continue
    return records
