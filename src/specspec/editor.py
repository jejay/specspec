"""Non-writing document overlays and edit plans for native text-editor hosts.

Unsaved text may be invalid. Return diagnostics, not a promise that saving a text
buffer is a journaled graph transaction. The managed writer remains separate.
"""

from __future__ import annotations

import io
import json
from pathlib import Path, PurePosixPath
from typing import Any

from .annotations import workspace_state
from .format import json_value, read_document, yaml_parser
from .git import git_snapshot, semantic_diff, source_change_impact
from .git_objects import OBJECT_ID
from .model import FORMAT_VERSION, ID_RE, MAX_FILE_BYTES, NODE_TYPES, Diagnostic, SpecError
from .node_text import document_eol, logical_text, stored_text
from .workspace import SPEC_DIR, read_files, runtime_diagnostics, snapshot_from_files

MAX_REQUEST_BYTES = 16 * 1024 * 1024


def fail(message: str, path: str | None = None) -> None:
    raise SpecError([Diagnostic("EDITOR", message, path)], 2)


def document_path(value: Any) -> str:
    if (
        not isinstance(value, str)
        or "\\" in value
        or len(PurePosixPath(value).parts) != 2
        or PurePosixPath(value).parent.as_posix() != SPEC_DIR
        or not value.endswith(".md")
        or value != PurePosixPath(value).as_posix()
    ):
        fail("Editor documents must be direct .specspec/*.md paths.")
    return value


def same_items(left: Any, right: Any) -> bool:
    """Parents/source references are unordered; don't rewrite untouched list comments."""
    if not isinstance(left, list) or not isinstance(right, list):
        return left == right
    try:
        return sorted(json.dumps(json_value(item), sort_keys=True) for item in left) == sorted(
            json.dumps(json_value(item), sort_keys=True) for item in right
        )
    except ValueError:
        return False


def document_files(root: Path, documents: Any) -> dict[str, bytes]:
    """Read actual canonical bytes with bounded native text overlays, without saves."""
    if not isinstance(documents, dict):
        fail("documents must map canonical paths to UTF-8 text.")
    files, diagnostics = read_files(root)
    diagnostics.extend(runtime_diagnostics(root))
    if diagnostics:
        raise SpecError(diagnostics)
    for path, text in documents.items():
        document_path(path)
        if not isinstance(text, str) or len(text.encode("utf-8")) > MAX_FILE_BYTES:
            fail("Document text exceeds the 1 MiB limit or is not a string.", path)
        if path in files:
            files[path] = text.encode("utf-8")
    return files


def editor_request(root: Path, request: Any, base: str | None = None) -> dict[str, Any]:
    """Overlay existing files and optionally plan one document change, without IO writes."""
    if not isinstance(request, dict) or set(request) - {"documents", "edit", "base_cache", "cache"}:
        fail("Expected documents, optional edit and bounded cache hints.")
    cache = request.get("base_cache")
    if "cache" in request and type(request["cache"]) is not bool:
        fail("cache must be a boolean.")
    if cache is not None:
        if (
            not isinstance(cache, dict)
            or set(cache) != {"commit", "files"}
            or not isinstance(cache["commit"], str)
            or not OBJECT_ID.fullmatch(cache["commit"])
            or not isinstance(cache["files"], dict)
        ):
            fail("Invalid baseline cache hint.")
        total = 0
        for path, text in cache["files"].items():
            document_path(path)
            if not isinstance(text, str) or len(text.encode("utf-8")) > MAX_FILE_BYTES:
                fail("Invalid cached node bytes.")
            total += len(text.encode("utf-8"))
        if total > 2 * MAX_FILE_BYTES:
            fail("Baseline cache exceeds its 2 MiB budget.")
    documents = request.get("documents", {})
    files = document_files(root, documents)
    changes = []
    edit = request.get("edit")
    if edit is not None:
        if not isinstance(edit, dict) or set(edit) - {
            "path",
            "id",
            "body",
            "parents",
            "sources",
        }:
            fail("Unknown editor fields.")
        path = document_path(edit.get("path"))
        if path not in files:
            fail("The document no longer exists; it will not be recreated.", path)
        data, body = read_document(files[path], path)
        original_body, metadata_changed = body, False
        if not isinstance(edit.get("id"), str) or edit["id"] != data.get("id"):
            fail("The edit must keep the bound document identity.", path)
        versions = []
        for name, raw in files.items():
            try:
                header, _ = read_document(raw, name)
            except SpecError:
                continue
            if header.get("type") == "manifesto":
                versions.append(header.get("format_version"))
        if len(versions) != 1 or type(versions[0]) is not int or versions[0] != FORMAT_VERSION:
            fail(
                f"Editing requires a current format-{FORMAT_VERSION} manifesto. "
                "Repair its Markdown.",
                path,
            )
        if "body" in edit:
            if not isinstance(edit["body"], str):
                fail("body must be text.", path)
            body = edit["body"]
        if "parents" in edit:
            if not isinstance(edit["parents"], list) or not all(
                isinstance(parent, str) for parent in edit["parents"]
            ):
                fail("parents must be an array of IDs.", path)
            if not same_items(data.get("parents"), edit["parents"]):
                data["parents"] = edit["parents"]
                metadata_changed = True
        if "sources" in edit:
            if not isinstance(edit["sources"], str):
                fail("sources requires JSON text.", path)
            try:
                sources = json.loads(edit["sources"])
            except ValueError:
                # Preserve intermediate JSON typing in the native dirty document.
                # It is intentionally invalid schema until the user completes it.
                sources = edit["sources"]
            if data.get("type") != "implementation":
                if sources != []:
                    fail("Non-empty sources requires an implementation node.", path)
                # Shared forms send a neutral [] field; don't add sources to other
                # node types or silently remove an invalid external sources field.
            elif not same_items(data.get("sources", []), sources):
                data["sources"] = sources
                metadata_changed = True
        before = files[path].decode("utf-8")
        eol = document_eol(files[path])
        body = stored_text(body, eol)
        if metadata_changed:
            stream = io.StringIO()
            yaml_parser().dump(data, stream)
            after = f"---{eol}{stored_text(stream.getvalue(), eol)}---{eol}{body}"
        else:
            # Ordinary typing leaves the entire frontmatter byte-for-byte intact.
            after = before[: len(before) - len(original_body)] + body
        if len(after.encode("utf-8")) > MAX_FILE_BYTES:
            fail("Planned document exceeds the 1 MiB limit.", path)
        files[path] = after.encode("utf-8")
        changes.append({"path": path, "before": before, "after": after})
    snapshot = snapshot_from_files(root, files, check_sources=True)
    # Repairable native form data is separate from parsed canonical membership.
    # Empty bodies/intermediate source JSON must not freeze the existing native form.
    repair_forms = []
    parsed_paths = {n.path for n in snapshot.nodes}
    if snapshot.format_version == FORMAT_VERSION:
        for path in sorted(
            (set(documents) | {c["path"] for c in changes}) & files.keys() - parsed_paths
        ):
            try:
                data, body = read_document(files[path], path)
                id, kind, parents = data.get("id"), data.get("type"), data.get("parents")
                if (
                    not isinstance(id, str)
                    or not ID_RE.fullmatch(id)
                    or path != f"{SPEC_DIR}/{id}.md"
                    or not isinstance(kind, str)
                    or kind not in NODE_TYPES
                ):
                    continue
                if not isinstance(parents, list) or any(
                    not isinstance(p, str) or not ID_RE.fullmatch(p) for p in parents
                ):
                    continue
                sources = json_value(data.get("sources", []))
                if not isinstance(sources, (list, str)):
                    continue
                repair_forms.append(
                    {
                        "id": id,
                        "path": path,
                        "type": kind,
                        "parents": list(parents),
                        "body": logical_text(body),
                        "sources": sources if isinstance(sources, list) else [],
                        "sources_text": sources
                        if isinstance(sources, str)
                        else json.dumps(sources, ensure_ascii=False, indent=2),
                        "repairForm": True,
                    }
                )
            except (SpecError, ValueError):
                continue
    result: dict[str, Any] = {
        "repair_forms": repair_forms,
        "snapshot": snapshot.to_dict(),
        "diagnostics": [item.to_dict() for item in snapshot.diagnostics],
        "changes": changes,
        "note": "",
    }
    head = None
    if base and snapshot.format_version == FORMAT_VERSION:
        try:
            old = git_snapshot(root, base, allow_empty=True, cache=cache)
            if base == "HEAD":
                head = old
            if not old.complete and old.graph is None:
                raise SpecError(old.diagnostics)
            comparison = semantic_diff(old, snapshot)
            comparison.update(source_change_impact(root, old.commit or base, None, old, snapshot))
            comparison["affected"] = sorted(
                set(comparison["affected"]) | set(comparison["source_affected"])
            )
            comparison.update(
                {
                    "base_ref": base,
                    "target_ref": "workspace + open documents" if documents else "workspace",
                    "base_commit": old.commit,
                    "target_commit": None,
                }
            )
            result["diff"] = comparison
            if (
                request.get("cache")
                and old.commit
                and sum(map(len, old.files.values())) <= 2 * MAX_FILE_BYTES
            ):
                result["base_cache"] = {
                    "commit": old.commit,
                    "files": {path: raw.decode("utf-8") for path, raw in old.files.items()},
                }
        except SpecError as error:
            result["note"] = "Diff unavailable: " + "; ".join(
                item.message for item in error.diagnostics
            )
    if snapshot.format_version == FORMAT_VERSION and base:
        try:
            result["workspace_state"] = workspace_state(snapshot, head)
        except SpecError:
            result["workspace_state"] = None
    return result
