"""Dilemmas: a situation, four options and one keyed answer.

``quizzes/dilemmas.json`` lists them. In each item the first option is the key; the
options are shuffled per repetition, in the same order for every model and guide, so
that results are compared on identical prompts. ``stated`` says whether the guide of
2026-11-10 states the rule: ``yes``, ``partly`` or ``no``.
"""

from __future__ import annotations

import json
import random
import re
from pathlib import Path

LETTERS = "ABCD"
FILE = Path(__file__).resolve().parent / "quizzes" / "dilemmas.json"
QUESTION = (
    "Which option fits this project's specspec graph best? Answer with the option's "
    "letter alone on the first line, then give your reason in at most two sentences."
)


def items() -> list[dict]:
    return json.loads(FILE.read_text(encoding="utf-8"))


def order(item: dict, repetition: int) -> list[int]:
    """The shuffled option indexes of one repetition; index 0 is the key."""
    indexes = list(range(len(item["options"])))
    random.Random(f"{item['id']}:{repetition}").shuffle(indexes)
    return indexes


def prompt(item: dict, repetition: int) -> str:
    lines = [item["stem"], "", "Options:"]
    for letter, index in zip(LETTERS, order(item, repetition), strict=True):
        lines.append(f"{letter}) {item['options'][index]}")
    return "\n".join([*lines, "", QUESTION])


def letter(text: str | None) -> str | None:
    """The letter on the first non-empty line of a reply."""
    for line in (text or "").splitlines():
        line = line.strip().strip("*`# ")
        if line:
            match = re.match(r"^(?:answer\s*[:\-]?\s*)?\(?([A-D])\)?(?:[\s).:,\-*]|$)", line, re.I)
            return match.group(1).upper() if match else None
    return None


def picked(item: dict, repetition: int, text: str | None) -> int | None:
    """The option index a reply chose, or None when it names no letter."""
    chosen = letter(text)
    return order(item, repetition)[LETTERS.index(chosen)] if chosen else None
