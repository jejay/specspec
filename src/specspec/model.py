"""Plain data structures and normalized semantic records."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

# Five octets encode to seven Base64url symbols and one '='. The last
# symbol has four significant bits and two zero pad bits (RFC 4648).
ID_RE = re.compile(r"^[A-Za-z0-9_-]{6}[AEIMQUYcgkosw048]=$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NODE_TYPES = {"manifesto", "requirement", "implementation"}
FORMAT_VERSION = 6
API_VERSION = 6
MAX_FILE_BYTES = 1024 * 1024


@dataclass(frozen=True)
class Diagnostic:
    code: str
    message: str
    path: str | None = None
    node_id: str | None = None
    severity: str = "error"
    line: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {key: value for key, value in vars(self).items() if value is not None}


class SpecError(Exception):
    def __init__(self, diagnostics: list[Diagnostic], exit_code: int = 1):
        self.diagnostics = diagnostics
        self.exit_code = exit_code
        super().__init__("; ".join(d.message for d in diagnostics))


@dataclass
class SpecNode:
    id: str
    type: str
    parents: list[str]
    body: str
    path: str
    format_version: int | None = None
    sources: list[dict[str, Any]] = field(default_factory=list)
    extensions: dict[str, Any] = field(default_factory=dict)

    def semantic(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": self.id,
            "type": self.type,
            "parents": sorted(self.parents),
            "body": self.body.replace("\r\n", "\n"),
            "sources": sorted(self.sources, key=lambda s: json.dumps(s, sort_keys=True)),
            "extensions": self.extensions,
        }
        if self.format_version is not None:
            data["format_version"] = self.format_version
        return data

    def to_dict(self) -> dict[str, Any]:
        return {**self.semantic(), "path": self.path}

    def frontmatter(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "type": self.type,
            "parents": self.parents,
        }
        if self.format_version is not None:
            result["format_version"] = self.format_version
        if self.sources:
            result["sources"] = self.sources
        if self.extensions:
            result["extensions"] = self.extensions
        return result
