"""Plain data structures and stable semantic fingerprints."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any

ID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NODE_TYPES = {"manifesto", "requirement", "implementation"}
STATUSES = {"proposed", "accepted", "retired"}
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


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )


@dataclass
class SpecNode:
    id: str
    type: str
    status: str
    parents: list[str]
    body: str
    path: str
    format_version: int | None = None
    sources: list[dict[str, str]] = field(default_factory=list)
    extensions: dict[str, Any] = field(default_factory=dict)
    managed_hash: str = ""

    def semantic(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": self.id,
            "type": self.type,
            "status": self.status,
            "parents": sorted(self.parents),
            "body": self.body.replace("\r\n", "\n"),
            "sources": sorted(self.sources, key=lambda s: (s["path"], s.get("symbol", ""))),
            "extensions": self.extensions,
        }
        if self.format_version is not None:
            data["format_version"] = self.format_version
        return data

    def digest(self) -> str:
        return hashlib.sha256(canonical_bytes(self.semantic())).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {**self.semantic(), "path": self.path, "managed_hash": self.managed_hash}

    def frontmatter(self, *, refresh_hash: bool = True) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "type": self.type,
            "status": self.status,
            "parents": self.parents,
        }
        if self.format_version is not None:
            result["format_version"] = self.format_version
        if self.sources:
            result["sources"] = self.sources
        if self.extensions:
            result["extensions"] = self.extensions
        result["managed_hash"] = self.digest() if refresh_hash else "0" * 64
        return result


def fingerprint(nodes: list[SpecNode]) -> str:
    projection = [node.semantic() for node in sorted(nodes, key=lambda n: n.id)]
    return hashlib.sha256(
        canonical_bytes({"canonical_version": 1, "nodes": projection})
    ).hexdigest()
