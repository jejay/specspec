"""Shared application reads; native plans and managed writes retain their owners."""

from __future__ import annotations

from .annotations import blob_ids, create_from_highlights, flush, load_shots, preview
from .editor import editor_request
from .git import git_snapshot, semantic_diff, source_change_impact
from .model import API_VERSION, Diagnostic, SpecError
from .output import file_patches
from .workspace import load_snapshot


def compare(root, base="HEAD", target=None, *, patches=False, versions=False):
    old = git_snapshot(root, base, allow_empty=True)
    new = git_snapshot(root, target) if target else load_snapshot(root)
    result = semantic_diff(old, new)
    if old.valid and new.valid:
        result.update(source_change_impact(root, old.commit or base, target, old, new))
        result["affected"] = sorted(set(result["affected"]) | set(result["source_affected"]))
    else:
        result.update(source_changes=[], source_affected=[])
    result.update(
        base_ref=base,
        target_ref=target or "workspace",
        base_commit=old.commit,
        target_commit=new.commit,
    )
    if patches:
        result["file_changes"] = file_patches(old, new)
    if versions:
        result["node_blobs"] = blob_ids(new)
        result["base_node_blobs"] = blob_ids(old)
    return result, old.diagnostics + new.diagnostics


def request(root, value):
    if (
        not isinstance(value, dict)
        or type(value.get("api_version")) is not int
        or value["api_version"] != API_VERSION
    ):
        raise SpecError(
            [Diagnostic("API", f"Application requests require api_version {API_VERSION}.")], 2
        )
    op = value.get("op")
    fields = {
        "read": {"base", "target", "documents", "cache", "base_cache"},
        "plan": {"documents", "edit"},
        "source-view": {"reference", "ref", "staged"},
        "source-capture": {"id", "path", "ranges", "mode", "staged", "ref"},
        "annotations": set(),
        "annotation-create": {"groups", "base", "target", "documents"},
        "annotation-view": {"shot", "group", "member"},
        "annotation-flush": {"expected"},
    }
    if (
        not isinstance(op, str)
        or op not in fields
        or set(value) - {"op", "api_version"} - fields[op]
    ):
        raise SpecError([Diagnostic("API", "Unknown application operation or fields.")], 2)
    if op == "annotations":
        return {"shots": load_shots(root)}, []
    if op == "annotation-create":
        shot = create_from_highlights(
            root,
            {"groups": value.get("groups")},
            base=value.get("base"),
            target=value.get("target"),
            documents=value.get("documents"),
        )
        return {"shots": [shot]}, []
    if op == "annotation-view":
        return preview(root, value.get("shot"), value.get("group"), value.get("member")), []
    if op == "annotation-flush":
        if not isinstance(value.get("expected"), list):
            raise SpecError([Diagnostic("API", "Flush requires the reviewed shot ID list.")], 2)
        return flush(root, expected=value["expected"]), []
    if op in {"read", "plan"}:
        from .wire import loaded

        base, target = value.get("base"), value.get("target")
        for ref in (base, target):
            if ref is not None and (not isinstance(ref, str) or not ref or len(ref) > 1024):
                raise SpecError([Diagnostic("API", "Invalid revision.")], 2)
        if op == "plan" and not isinstance(value.get("edit"), dict):
            raise SpecError([Diagnostic("API", "Document planning requires an edit object.")], 2)
        if target is not None:
            if value.get("documents") or value.get("base_cache") or value.get("cache"):
                raise SpecError(
                    [
                        Diagnostic(
                            "API",
                            "Historical comparisons do not consume workspace overlays or hints.",
                        )
                    ],
                    2,
                )
            result, diagnostics = compare(root, base or "HEAD", target, versions=True)
            if not result["impact_complete"]:
                raise SpecError(diagnostics)
            versions = {key: result.pop(key) for key in ("node_blobs", "base_node_blobs")}
            return loaded(
                {
                    "snapshot": result["target"],
                    "diff": result,
                    "note": "",
                    "changes": [],
                    **versions,
                }
            ), diagnostics
        payload = {
            key: val
            for key, val in value.items()
            if key in {"documents", "edit", "cache", "base_cache"}
        }
        result = editor_request(root, payload, base)
        return loaded(result), [Diagnostic(**d) for d in result["diagnostics"]]
    from .source_commands import capture_source, preview_source

    if op == "source-view":
        return preview_source(
            root, value.get("reference"), ref=value.get("ref"), staged=value.get("staged", False)
        ), []
    return capture_source(
        root,
        value.get("id"),
        value.get("path"),
        value.get("ranges"),
        value.get("mode"),
        ref=value.get("ref"),
        staged=value.get("staged", False),
        dry_run=True,
    ), []
