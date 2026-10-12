"""Current source-reference shape; independent of Git and Markdown parsing."""

import re
from collections.abc import Mapping
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any

MAX_REFERENCES = 256
MAX_RANGES = 64


def safe_source_path(value: str) -> bool:
    posix, windows = PurePosixPath(value), PureWindowsPath(value)
    return (
        bool(value)
        and value == posix.as_posix()
        and not any(ord(c) < 32 or ord(c) == 127 for c in value)
        and "\\" not in value
        and not (posix.is_absolute() or windows.drive or ".." in posix.parts or value == ".")
    )


def validate_source(source: Any) -> None:
    if not isinstance(source, Mapping) or set(source) - {
        "path",
        "symbol",
        "blob",
        "mode",
        "ranges",
    }:
        raise ValueError(
            "Each source requires path, optional symbol and optional blob/mode/ranges."
        )
    if not isinstance(source.get("path"), str) or not safe_source_path(source["path"]):
        raise ValueError(
            "Source path must be canonical project-relative POSIX text without traversal."
        )
    if "symbol" in source and not isinstance(source["symbol"], str):
        raise ValueError("Source symbol must be text.")
    anchors = {"blob", "mode", "ranges"} & source.keys()
    if not anchors:
        return
    if anchors != {"blob", "mode", "ranges"}:
        raise ValueError("blob, mode and ranges must be supplied together.")
    if not isinstance(source["blob"], str) or not re.fullmatch(
        r"(?:[0-9a-f]{40}|[0-9a-f]{64})", source["blob"]
    ):
        raise ValueError("Source blob must be a full lowercase SHA-1 or SHA-256 Git object ID.")
    if not isinstance(source["mode"], str) or source["mode"] not in {"strict", "expanding"}:
        raise ValueError("Source mode must be strict or expanding.")
    ranges = source["ranges"]
    if not isinstance(ranges, list) or not 1 <= len(ranges) <= MAX_RANGES:
        raise ValueError(f"Source ranges requires 1..{MAX_RANGES} intervals.")
    previous = 0
    for interval in ranges:
        if (
            not isinstance(interval, list)
            or len(interval) != 2
            or any(type(n) is not int for n in interval)
            or not previous < interval[0] <= interval[1] <= 2_147_483_647
        ):
            raise ValueError(
                "Ranges must be sorted, nonoverlapping positive inclusive [start,end] pairs."
            )
        previous = interval[1]
