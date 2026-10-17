"""Metadata-only checkout-local spotlights; Git owns committed node contents."""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import subprocess
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path

from .git import git_snapshot, repository_paths, run_git, semantic_diff
from .git_objects import OBJECT_ID
from .model import ID_RE, MAX_FILE_BYTES, Diagnostic, SpecError
from .workspace import STATE_DIR, load_snapshot, snapshot_from_files, workspace_lock

SHOT_ID = re.compile(r"[0-9a-f]{32}\Z")
TEMP_FILE = re.compile(r"\.shot-[0-9a-f]{32}\.tmp\Z")
CHECKSUM = re.compile(r"[0-9a-f]{64}\Z")
MAX_SHOT_BYTES = 512 * 1024
MAX_LIST_BYTES = 4 * 1024 * 1024
MAX_SHOTS = 256
MAX_MEMBERS = 512


def fail(message):
    raise SpecError([Diagnostic("SPOTLIGHTS", message)])


def parse_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"Duplicate field: {key}")
            result[key] = value
        return result

    try:
        return json.loads(raw, object_pairs_hook=pairs)
    except (ValueError, UnicodeError, RecursionError) as error:
        fail(f"Invalid spotlight JSON: {error}")


def object_fields(value, fields):
    if not isinstance(value, dict) or set(value) != set(fields):
        fail(f"Expected exactly these fields: {', '.join(fields)}.")


def node_ids(value):
    if (
        not isinstance(value, list)
        or not 1 <= len(value) <= MAX_MEMBERS
        or any(not isinstance(i, str) or not ID_RE.fullmatch(i) for i in value)
        or len(value) != len(set(value))
    ):
        fail(f"Supply 1–{MAX_MEMBERS} unique full node IDs, including '='.")
    return value


def message(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 500:
        fail("Provide a spotlight message of 1–500 characters.")
    return value


def head_snapshot(root):
    try:
        return git_snapshot(root, "HEAD", allow_empty=True)
    except SpecError:
        # Non-Git projects still support local workspace messages. Invalid Git
        # snapshots are not silently turned into an empty baseline.
        try:
            repository_paths(root)
        except SpecError:
            return snapshot_from_files(root, {}, allow_empty=True)
        raise


def workspace_state(snapshot, head=None):
    """Sparse literal-byte drift hints, never stored hashes of clean Git nodes."""
    head = head if head is not None else head_snapshot(snapshot.root)
    if head.files or not head.valid:
        head.require_valid()
    old = head.graph.nodes if head.graph else {}
    new = snapshot.graph.nodes if snapshot.graph else {}
    # Git decides which saved files are uncommitted, including staged changes.
    # This avoids checksumming every clean CRLF checkout or clean-filter output.
    dirty_paths = set()
    if head.commit:
        dirty_paths = {
            p.decode("utf-8", errors="surrogateescape")
            for p in run_git(
                snapshot.root,
                "--literal-pathspecs",
                "diff",
                "--relative",
                "--name-only",
                "-z",
                "--no-renames",
                head.commit,
                "--",
                "_specspec",
            ).split(b"\0")
            if p
        }
    changes = {}
    for node_id in sorted(old.keys() | new.keys()):
        before = head.files[old[node_id].path] if node_id in old else None
        after = snapshot.files[new[node_id].path] if node_id in new else None
        if before == after:
            continue
        if before is not None and after is not None and new[node_id].path not in dirty_paths:
            # Trusted native overlays can differ from clean saved bytes too.
            try:
                with (snapshot.root / new[node_id].path).open("rb") as stream:
                    saved = stream.read(MAX_FILE_BYTES + 1)
            except FileNotFoundError:
                saved = None
            if after == saved:
                continue
        changes[node_id] = hashlib.sha256(after).hexdigest() if after is not None else None
    return {"head": head.commit, "changes": changes}


def workspace_warnings(captured, current):
    if captured is None:
        return []
    if current is None:
        return ["Workspace state is unavailable; highlighting available node IDs."]
    warnings = []
    if captured["head"] != current["head"]:
        warnings.append("Workspace HEAD moved since capture; highlighting available node IDs.")
    before, after = captured["changes"], current["changes"]
    changed = sorted(
        i
        for i in before.keys() | after.keys()
        if (i in before, before.get(i)) != (i in after, after.get(i))
    )
    if changed:
        warnings.append(
            f"Workspace nodes changed since capture ({len(changed)}): {', '.join(changed)}. "
            "Highlighting available node IDs."
        )
    return warnings


def directory(root):
    path = root / STATE_DIR / "annotations"
    for candidate in (root / STATE_DIR, path, path / "blobs"):
        if candidate.is_symlink() or (candidate.exists() and not candidate.is_dir()):
            fail(f"Spotlight storage must be real directories: {candidate}")
    return path


def shot_files(path, *, limited=True):
    if not path.exists():
        return []
    result = []
    for entry in path.iterdir():
        if entry.is_symlink():
            fail("Spotlight storage contains a forbidden symlink.")
        if entry.suffix == ".json":
            if not SHOT_ID.fullmatch(entry.stem) or not entry.is_file():
                fail(f"Unexpected shot file: {entry.name}")
            result.append(entry)
    if limited and len(result) > MAX_SHOTS:
        fail(f"Spotlight storage exceeds {MAX_SHOTS} spotlights; explicitly flush it.")
    return result


def commit_id(value):
    return isinstance(value, str) and OBJECT_ID.fullmatch(value)


def validate_shot(shot, shot_id):
    if (
        not isinstance(shot, dict)
        or type(shot.get("spotlight_version")) is not int
        or shot["spotlight_version"] != 2
    ):
        fail(
            "Unsupported local spotlight format. "
            "Review/clear old local data with spotlight flush --yes."
        )
    target = (
        shot.get("comparison", {}).get("target")
        if isinstance(shot.get("comparison"), dict)
        else None
    )
    fields = ["spotlight_version", "id", "created_at", "message", "comparison", "nodes"]
    object_fields(shot, fields + (["workspace"] if target == "workspace" else []))
    if shot["id"] != shot_id:
        fail("Shot filename and identity disagree.")
    try:
        date = datetime.fromisoformat(shot["created_at"])
        if date.tzinfo is None:
            raise ValueError()
    except (TypeError, ValueError):
        fail("Invalid spotlight capture time.")
    message(shot["message"])
    node_ids(shot["nodes"])
    comparison = shot["comparison"]
    object_fields(comparison, ["base", "target"])
    if comparison["base"] != "HEAD" and not commit_id(comparison["base"]):
        fail("Comparison base needs HEAD or an immutable commit ID.")
    if target != "workspace" and not commit_id(target):
        fail("Comparison target needs workspace or an immutable commit ID.")
    if target == "workspace":
        state = shot["workspace"]
        object_fields(state, ["head", "changes"])
        if state["head"] is not None and not commit_id(state["head"]):
            fail("Workspace HEAD needs an immutable commit ID or null.")
        if not isinstance(state["changes"], dict) or any(
            not isinstance(i, str)
            or not ID_RE.fullmatch(i)
            or (
                checksum is not None
                and (not isinstance(checksum, str) or not CHECKSUM.fullmatch(checksum))
            )
            for i, checksum in state["changes"].items()
        ):
            fail("Invalid sparse workspace checksums/deletion markers.")
    return shot


def load_shots(root):
    shots, total = [], 0
    for file in shot_files(directory(root)):
        try:
            size = file.stat().st_size
            total += size
            if size > MAX_SHOT_BYTES or total > MAX_LIST_BYTES:
                fail("Spotlight metadata exceeds its storage budget; explicitly flush it.")
            with file.open("rb") as stream:
                raw = stream.read(MAX_SHOT_BYTES + 1)
            if len(raw) > MAX_SHOT_BYTES:
                fail("Spotlight exceeds 512 KiB; retained for explicit repair or flush.")
        except FileNotFoundError:
            continue
        try:
            shots.append(validate_shot(parse_json(raw), file.stem))
        except SpecError as error:
            fail(f"Protected malformed shot {file.name}: {error.diagnostics[0].message}")
    return sorted(shots, key=lambda shot: (shot["created_at"], shot["id"]), reverse=True)


def ensure_ignored(root):
    """Protect local data without tracked .gitignore changes or installed hooks."""
    try:
        repository, _ = repository_paths(root)
    except SpecError:
        return
    relative = (root.resolve().relative_to(repository) / STATE_DIR).as_posix()
    if run_git(repository, "--literal-pathspecs", "ls-files", "-z", "--", relative):
        fail("Local state contains Git-tracked files; untrack it explicitly before submitting.")

    def ignored():
        try:
            result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(repository),
                    "check-ignore",
                    "--quiet",
                    "--",
                    relative + "/annotations/",
                ],
                capture_output=True,
                check=False,
                timeout=20,
            )
        except subprocess.TimeoutExpired:
            fail("Git exclusion verification timed out; no spotlight published.")
        if result.returncode not in (0, 1):
            fail("Cannot verify the Git exclusion for local spotlights.")
        return result.returncode == 0

    if ignored():
        return
    exclude = Path(
        run_git(repository, "rev-parse", "--path-format=absolute", "--git-path", "info/exclude")
        .decode()
        .strip()
    )
    if exclude.is_symlink():
        fail("Refusing to follow a substituted Git exclude file.")
    exclude.parent.mkdir(parents=True, exist_ok=True)
    escaped = "".join("\\" + c if c in "\\!#[]*? " else c for c in relative)
    with exclude.open("a", encoding="utf-8") as stream:
        stream.write(f"\n# SpecSpec checkout-local state\n/{escaped}/\n")
    if not ignored():
        fail("Local ignore rules override the spotlight exclusion; fix them before submitting.")


def atomic_file(path, raw):
    temporary = path.with_name(f".shot-{secrets.token_hex(16)}.tmp")
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(raw)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def snapshots(root, base, target, documents=None):
    old = head_snapshot(root) if base == "HEAD" else git_snapshot(root, base, allow_empty=True)
    if target == "workspace":
        if documents is None:
            new = load_snapshot(root)
        else:
            from .editor import document_files

            new = snapshot_from_files(root, document_files(root, documents))
    else:
        if documents:
            fail("Historical spotlight capture does not consume native overlays.")
        new = git_snapshot(root, target)
    if old.files or not old.valid:
        old.require_valid()
    new.require_valid()
    return old, new


def submit(root, value, *, base=None, target=None, documents=None):
    object_fields(value, ["message", "nodes"])
    message(value["message"])
    ids = node_ids(value["nodes"])
    for ref in (base, target):
        if ref is not None and (not isinstance(ref, str) or not ref or len(ref) > 1024):
            fail("Invalid spotlight revision.")
    if documents is not None and not isinstance(documents, dict):
        fail("documents must map canonical paths to UTF-8 text.")
    target = target or "workspace"
    old, new = snapshots(root, base or "HEAD", target, documents)
    available = {n.id for n in old.nodes} | {n.id for n in new.nodes}
    for node_id in ids:
        if node_id not in available:
            fail(f"Node {node_id} does not exist in either side of the comparison.")
    comparison = {
        "base": old.commit
        if (base is not None or target != "workspace") and old.commit
        else "HEAD",
        "target": new.commit if target != "workspace" else "workspace",
    }
    extra = (
        {"workspace": workspace_state(new, old if base in (None, "HEAD") else None)}
        if target == "workspace"
        else {}
    )
    return publish(
        root, {"message": value["message"], "comparison": comparison, "nodes": ids, **extra}
    )


def publish(root, value):
    with workspace_lock(root):
        path = directory(root)
        existing = load_shots(root)
        if len(existing) >= MAX_SHOTS:
            fail(f"Spotlight storage is full ({MAX_SHOTS} spotlights); explicitly flush it.")
        shot_id = secrets.token_hex(16)
        while (path / f"{shot_id}.json").exists():
            shot_id = secrets.token_hex(16)
        shot = {
            "spotlight_version": 2,
            "id": shot_id,
            "created_at": datetime.now(UTC).isoformat(),
            **deepcopy(value),
        }
        validate_shot(shot, shot_id)
        raw = json.dumps(shot, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if (
            len(raw) > MAX_SHOT_BYTES
            or len(raw) + sum(p.stat().st_size for p in shot_files(path)) > MAX_LIST_BYTES
        ):
            fail("Spotlight metadata storage is full; explicitly flush it.")
        ensure_ignored(root)
        path.mkdir(parents=True, exist_ok=True)
        atomic_file(path / f"{shot_id}.json", raw)
    return shot


def flush(root, *, expected=None):
    if expected is not None and (
        not isinstance(expected, list)
        or any(not isinstance(i, str) or not SHOT_ID.fullmatch(i) for i in expected)
        or len(expected) != len(set(expected))
    ):
        fail("Invalid reviewed spotlight list.")
    with workspace_lock(root):
        path = directory(root)
        files = shot_files(path, limited=False)
        if expected is not None and set(expected) != {file.stem for file in files}:
            fail("The spotlight list changed; review it and confirm flush again.")
        # Cleanup only: the current mechanism never reads or creates node copies.
        legacy = list((path / "blobs").iterdir()) if (path / "blobs").exists() else []
        if any(
            p.is_symlink()
            or not p.is_file()
            or not (OBJECT_ID.fullmatch(p.name) or TEMP_FILE.fullmatch(p.name))
            for p in legacy
        ):
            fail("Obsolete spotlight blobs contain an unsafe entry; nothing removed.")
        if files or legacy:
            ensure_ignored(root)
        for file in files + legacy:
            file.unlink(missing_ok=True)
        if path.exists():
            for temporary in path.glob(".shot-*.tmp"):
                if (
                    TEMP_FILE.fullmatch(temporary.name)
                    and not temporary.is_symlink()
                    and temporary.is_file()
                ):
                    temporary.unlink(missing_ok=True)
        if (path / "blobs").exists():
            (path / "blobs").rmdir()
    return {"flushed": len(files)}


def listing(root, shot_id=None):
    shots = deepcopy(load_shots(root))
    if shot_id is not None:
        shots = [s for s in shots if s["id"] == shot_id]
        if not shots:
            fail("No local spotlight has that ID.")
    cache = {}
    for shot in shots:
        context = shot["comparison"]
        key = context["base"], context["target"]
        if key not in cache:
            try:
                old, new = snapshots(root, *key)
                changes = {c["id"]: c["kind"] for c in semantic_diff(old, new)["changes"]}
                state = (
                    workspace_state(new, old if key[0] == "HEAD" else None)
                    if key[1] == "workspace"
                    else None
                )
                cache[key] = old, new, changes, state, None
            except SpecError as error:
                cache[key] = None, None, {}, None, "; ".join(d.message for d in error.diagnostics)
        old, new, changes, state, error = cache[key]
        shot["warnings"] = workspace_warnings(shot.get("workspace"), state)
        if error:
            shot["warnings"].append("Comparison unavailable: " + error)
        members = []
        for node_id in shot["nodes"]:
            node = (
                (
                    new.graph.nodes.get(node_id)
                    or (old.graph.nodes.get(node_id) if old.graph else None)
                )
                if new
                else None
            )
            kind = (
                "unavailable" if error else changes.get(node_id, "unchanged") if node else "absent"
            )
            title = (
                next(
                    (line.lstrip("# ") for line in node.body.splitlines() if line.strip()), node_id
                )
                if node
                else None
            )
            members.append(
                {"id": node_id, "kind": kind, "title": title, "path": node.path if node else None}
            )
        shot["members"] = members
    return {"shots": shots}
