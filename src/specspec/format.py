"""Strict frontmatter parsing, with round-trip YAML updates."""

from __future__ import annotations

import io
import math
from collections.abc import Mapping
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError
from ruamel.yaml.tokens import AliasToken, AnchorToken, TagToken

from .model import (
    HASH_RE,
    ID_RE,
    MAX_FILE_BYTES,
    NODE_TYPES,
    SLUG_RE,
    STATUSES,
    Diagnostic,
    SpecError,
    SpecNode,
)

FIELDS = {
    "id",
    "type",
    "status",
    "parents",
    "format_version",
    "sources",
    "extensions",
    "managed_hash",
}


def yaml_parser() -> YAML:
    parser = YAML(typ="rt")
    parser.allow_duplicate_keys = False
    parser.preserve_quotes = True
    parser.width = 100
    return parser


def split_document(raw: bytes, path: str) -> tuple[str, str]:
    def fail(message: str) -> None:
        raise SpecError([Diagnostic("FORMAT", message, path)])

    if len(raw) > MAX_FILE_BYTES:
        fail("Node exceeds the 1 MiB limit; split it into smaller nodes.")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        fail("Node must be UTF-8 without a byte-order mark.")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        fail("Node must begin with a YAML frontmatter delimiter (---).")
    for index, line in enumerate(lines[1:], 1):
        if line.rstrip("\r\n") == "---":
            return "".join(lines[1:index]), "".join(lines[index + 1 :])
    fail("Missing closing YAML frontmatter delimiter (---).")
    raise AssertionError("unreachable")


def read_document(raw: bytes, path: str) -> tuple[Mapping[str, Any], str]:
    header, body = split_document(raw, path)
    parser = yaml_parser()
    try:
        for token in parser.scan(header):
            if isinstance(token, (AliasToken, AnchorToken, TagToken)):
                raise SpecError(
                    [Diagnostic("YAML", "Tags, anchors and aliases are not allowed.", path)]
                )
        data = parser.load(header)
    except YAMLError as error:
        mark = getattr(error, "problem_mark", None)
        raise SpecError(
            [
                Diagnostic(
                    "YAML",
                    f"Invalid YAML: {getattr(error, 'problem', str(error))}",
                    path,
                    line=mark.line + 2 if mark else None,
                )
            ]
        ) from error
    if not isinstance(data, Mapping):
        raise SpecError([Diagnostic("SCHEMA", "Frontmatter must be a mapping.", path)])
    return data, body


def json_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("Non-finite numbers are not JSON metadata.")
        return value
    if isinstance(value, list):
        return [json_value(item) for item in value]
    if isinstance(value, Mapping) and all(isinstance(key, str) for key in value):
        return {key: json_value(item) for key, item in value.items()}
    raise ValueError("Metadata must contain only JSON-compatible values and string keys.")


def safe_source_path(value: str) -> bool:
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    return (
        bool(value)
        and value == posix.as_posix()
        and not any(ord(character) < 32 or ord(character) == 127 for character in value)
        and "\\" not in value
        and not (posix.is_absolute() or windows.drive or ".." in posix.parts or value in {".", ""})
    )


def parse_node(data: Mapping[str, Any], body: str, path: str) -> SpecNode:
    errors: list[Diagnostic] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(Diagnostic("SCHEMA", message, path))

    check(all(isinstance(key, str) for key in data), "Frontmatter keys must be strings.")
    check(not (set(data) - FIELDS), f"Unknown fields: {sorted(str(k) for k in set(data) - FIELDS)}")
    node_id = data.get("id")
    check(
        isinstance(node_id, str) and bool(ID_RE.fullmatch(node_id)),
        "id must be a lowercase UUIDv4.",
    )
    node_type = data.get("type")
    check(isinstance(node_type, str) and node_type in NODE_TYPES, "Invalid node type.")
    status = data.get("status")
    check(isinstance(status, str) and status in STATUSES, "Invalid lifecycle status.")
    parents = data.get("parents")
    valid_parents = isinstance(parents, list) and all(
        isinstance(parent, str) and ID_RE.fullmatch(parent) for parent in parents
    )
    check(valid_parents, "parents must be an array of lowercase UUIDv4 IDs.")
    if valid_parents:
        check(len(set(parents)) == len(parents), "parents must not contain duplicates.")
    version = data.get("format_version")
    if node_type == "manifesto":
        check(
            isinstance(version, int) and not isinstance(version, bool) and version == 1,
            "Manifesto requires format_version: 1.",
        )
    else:
        check("format_version" not in data, "format_version belongs on the manifesto only.")
    managed_hash = data.get("managed_hash")
    check(
        isinstance(managed_hash, str) and bool(HASH_RE.fullmatch(managed_hash)),
        "managed_hash must be a SHA-256 hex digest; use the tool to create or edit nodes.",
    )
    check(isinstance(body, str) and bool(body.strip()), "Node body must be non-empty text.")
    sources = data.get("sources", [])
    check(isinstance(sources, list), "sources must be an array.")
    if "sources" in data:
        check(node_type == "implementation", "sources is allowed only on implementation nodes.")
    normalized_sources: list[dict[str, str]] = []
    if isinstance(sources, list):
        for source in sources:
            if not isinstance(source, Mapping):
                check(False, "Each source must be a mapping.")
                continue
            source_path = source.get("path")
            check(set(source) <= {"path", "symbol"}, "Unknown source reference field.")
            check(
                isinstance(source_path, str) and safe_source_path(source_path),
                "Source paths must be project-relative POSIX paths without traversal.",
            )
            check(
                "symbol" not in source or isinstance(source["symbol"], str),
                "Source symbol must be a string.",
            )
            normalized_sources.append(dict(source))
    extensions = data.get("extensions", {})
    try:
        check(isinstance(extensions, Mapping), "extensions must be a mapping.")
        extensions = json_value(extensions)
        if isinstance(extensions, dict):
            check(
                all("." in key or ":" in key for key in extensions),
                "Extension keys must be namespaced (for example org.example:note).",
            )
    except ValueError as error:
        check(False, str(error))
    filename = PurePosixPath(path).name
    if isinstance(node_id, str):
        prefix = f"{node_id}--"
        check(
            filename.startswith(prefix) and filename.endswith(".md"), "Filename must match its id."
        )
        if filename.startswith(prefix) and filename.endswith(".md"):
            check(
                bool(SLUG_RE.fullmatch(filename[len(prefix) : -3])),
                "Filename slug is not portable.",
            )
    if errors:
        raise SpecError(errors)
    return SpecNode(
        node_id,
        node_type,
        status,
        list(parents),
        body,
        path,
        version,
        normalized_sources,
        extensions,
        managed_hash,
    )


def serialize(node: SpecNode, original: bytes | None = None) -> bytes:
    data = read_document(original, node.path)[0] if original is not None else {}
    # Keep round-trip comments on untouched fields and omit empty optional fields.
    # Validate caller-supplied data before hashing/sorting it (library callers
    # can pass malformed inputs just as CLI callers can).
    desired = parse_node(node.frontmatter(refresh_hash=False), node.body, node.path).frontmatter()
    for key in list(data):
        if key not in desired:
            del data[key]
    for key, value in desired.items():
        if key not in data or data[key] != value:
            data[key] = value
    stream = io.StringIO()
    yaml_parser().dump(data, stream)
    result = ("---\n" + stream.getvalue() + "---\n" + node.body).encode("utf-8")
    # Apply the same schema/size limits to generated documents before writing.
    header, body = read_document(result, node.path)
    parse_node(header, body, node.path)
    return result
