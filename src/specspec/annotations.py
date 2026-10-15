"""Immutable checkout-local spotlights; never a canonical or Git object writer.

Storage paths/keys are independent of public naming; existing immutable shots stay intact.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import subprocess
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

from .format import read_document
from .git import git_snapshot, repository_paths, run_git
from .git_objects import OBJECT_ID, blob_id
from .model import ID_RE, MAX_FILE_BYTES, Diagnostic, SpecError
from .workspace import STATE_DIR, load_snapshot, workspace_lock

INKS = {
    "red": "#e65e66",
    "blue": "#5c9eff",
    "green": "#58ba7a",
    "purple": "#aa79df",
    "turquoise": "#35bdbe",
    "yellow": "#dfc24d",
}
SHOT_ID = re.compile(r"[0-9a-f]{32}\Z")
TEMP_FILE = re.compile(r"\.shot-[0-9a-f]{32}\.tmp\Z")
COLOR = re.compile(r"#[0-9a-fA-F]{6}\Z")
MAX_SHOT_BYTES = 512 * 1024
MAX_LIST_BYTES = 4 * 1024 * 1024
MAX_BLOB_BYTES = 64 * 1024 * 1024
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


def checked_color(value):
    if not isinstance(value, str) or (value not in INKS and not COLOR.fullmatch(value)):
        fail("Color must be red, blue, green, purple, turquoise, yellow or #RRGGBB.")
    return INKS.get(value, value.lower())


def groups(value, *, stored=False):
    if not isinstance(value, list) or not 1 <= len(value) <= 64:
        fail("Supply 1–64 complete label groups.")
    count = 0
    for group in value:
        object_fields(group, ["text", "color", "nodes"])
        if (
            not isinstance(group["text"], str)
            or not group["text"].strip()
            or len(group["text"]) > 500
        ):
            fail("Each label needs 1–500 characters of short text.")
        checked_color(group["color"])
        nodes = group["nodes"]
        if not isinstance(nodes, list) or not nodes:
            fail("Each label needs a nonempty node list.")
        count += len(nodes)
        if count > MAX_MEMBERS:
            fail(f"A shot can reference at most {MAX_MEMBERS} members.")
        ids = set()
        for member in nodes:
            if isinstance(member, str) and not stored:
                node_id = member
            else:
                fields = ["id", "blob", "path", "title"] if stored else ["id", "blob"]
                object_fields(member, fields)
                node_id = member["id"]
                if not isinstance(member["blob"], str) or not OBJECT_ID.fullmatch(member["blob"]):
                    fail("Use a full lowercase SHA-1 or SHA-256 Git blob ID.")
                if stored:
                    path = member["path"]
                    if (
                        not isinstance(path, str)
                        or "\\" in path
                        or len(PurePosixPath(path).parts) != 2
                        or PurePosixPath(path).parent.as_posix() != "_specspec"
                        or path != PurePosixPath(path).as_posix()
                        or not path.endswith(".md")
                        or not isinstance(member["title"], str)
                        or len(member["title"]) > 500
                    ):
                        fail("Invalid retained member description.")
            if not isinstance(node_id, str) or not ID_RE.fullmatch(node_id) or node_id in ids:
                fail("Node lists need unique full canonical node IDs, including '='.")
            ids.add(node_id)
    return value


def blob_ids(snapshot):
    """Derived addresses of actual bytes, not canonical fields or edit gates.

    Supply both Git object formats without another Git subprocess. Workspace hashes
    are over literal UTF-8 bytes, without clean filters or line-ending normalization.
    """
    return {
        node.id: [
            hashlib.new(algorithm, b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            for algorithm in ("sha1", "sha256")
        ]
        for node in snapshot.nodes
        if (raw := snapshot.files.get(node.path)) is not None
    }


def directory(root):
    state = root / STATE_DIR
    path = state / "annotations"
    for candidate in (state, path, path / "blobs"):
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


def blob_files(path):
    files = list(path.iterdir()) if path.exists() else []
    if any(
        p.is_symlink()
        or not p.is_file()
        or not (OBJECT_ID.fullmatch(p.name) or TEMP_FILE.fullmatch(p.name))
        for p in files
    ):
        fail("Retained spotlight blobs contain an unsafe entry; nothing removed.")
    return files


def validate_shot(shot, shot_id):
    object_fields(shot, ["annotation_version", "id", "created_at", "origin", "groups"])
    if type(shot["annotation_version"]) is not int or shot["annotation_version"] != 1:
        fail("Unsupported local spotlight format.")
    if shot["id"] != shot_id:
        fail("Shot filename and identity disagree.")
    try:
        date = datetime.fromisoformat(shot["created_at"])
        if date.tzinfo is None:
            raise ValueError()
    except (TypeError, ValueError):
        fail("Invalid shot capture time.")
    origin = shot["origin"]
    if (
        not isinstance(origin, dict)
        or not isinstance(origin.get("kind"), str)
        or origin["kind"] not in {"workspace", "commit", "highlights"}
    ):
        fail("Invalid shot capture context.")
    if origin["kind"] == "highlights":
        object_fields(origin, ["kind"])
        groups(shot["groups"], stored=True)
        return shot
    key = "head" if origin["kind"] == "workspace" else "commit"
    object_fields(origin, ["kind", key])
    commit = origin[key]
    if not (commit is None and key == "head") and (
        not isinstance(commit, str) or not OBJECT_ID.fullmatch(commit)
    ):
        fail("Capture provenance needs an immutable commit ID.")
    groups(shot["groups"], stored=True)
    return shot


def load_shots(root):
    path = directory(root)
    shots, total = [], 0
    for file in shot_files(path):
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
            continue  # Concurrent explicit flush; complete submissions publish atomically.
        try:
            shots.append(validate_shot(parse_json(raw), file.stem))
        except SpecError as error:
            fail(f"Protected malformed shot {file.name}: {error.diagnostics[0].message}")
    return sorted(shots, key=lambda shot: (shot["created_at"], shot["id"]), reverse=True)


def ensure_ignored(root):
    """Protect local data without changing tracked .gitignore or installing hooks."""
    try:
        repository, _ = repository_paths(root)
    except SpecError:
        return  # Non-Git graphs can still use local shots.
    relative = (root.resolve().relative_to(repository) / STATE_DIR).as_posix()
    tracked = run_git(repository, "--literal-pathspecs", "ls-files", "-z", "--", relative)
    if tracked:
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
            fail("Git exclusion verification timed out; no shot published.")
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
    # Escape Git-ignore metacharacters in project paths, including spaces at the end.
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


def submit(root, value, *, ref=None):
    object_fields(value, ["groups"])
    supplied = groups(value["groups"])
    if ref is not None and (not isinstance(ref, str) or not ref or len(ref) > 1024):
        fail("Invalid capture revision.")
    snapshot = git_snapshot(root, ref) if ref else load_snapshot(root)
    graph = snapshot.require_valid()
    addresses = blob_ids(snapshot)
    head = None
    if not ref:
        try:
            head = run_git(root, "rev-parse", "--verify", "HEAD^{commit}").decode().strip()
        except SpecError:
            pass
    sha256 = len(snapshot.commit or head or "") == 64
    if not ref and head is None:
        try:
            sha256 = run_git(root, "rev-parse", "--show-object-format").strip() == b"sha256"
        except SpecError:
            pass
    captured, retained = [], {}
    for group in supplied:
        members = []
        for requested in group["nodes"]:
            node_id = requested if isinstance(requested, str) else requested["id"]
            node = graph.nodes.get(node_id)
            if node is None:
                fail(f"Node {node_id} does not exist in the capture snapshot.")
            oid = addresses[node_id][int(sha256)]
            if isinstance(requested, dict) and requested["blob"] not in addresses[node_id]:
                fail(f"Node {node_id} differs from the supplied blob; nothing submitted.")
            if isinstance(requested, dict):
                oid = requested["blob"]
            raw = snapshot.files[node.path]
            retained[oid] = raw
            title = next(
                (line.lstrip("# ") for line in node.body.splitlines() if line.strip()), node_id
            )
            members.append({"id": node_id, "blob": oid, "path": node.path, "title": title[:500]})
        captured.append(
            {"text": group["text"], "color": checked_color(group["color"]), "nodes": members}
        )
    origin = (
        {"kind": "commit", "commit": snapshot.commit}
        if ref
        else {"kind": "workspace", "head": head}
    )
    return publish(root, captured, retained, origin)


def create_from_highlights(root, value, *, base=None, target=None, documents=None):
    """Capture exact, possibly mixed-version references; never silently retarget."""
    object_fields(value, ["groups"])
    supplied = groups(value["groups"])
    seen, texts = set(), set()
    for group in supplied:
        texts.add(group["text"])
        for member in group["nodes"]:
            if not isinstance(member, dict) or member["id"] in seen:
                fail("Highlights require exact references and one color per node.")
            seen.add(member["id"])
    if len(texts) != 1:
        fail("A new spotlight needs one shared message.")
    for ref in (base, target):
        if ref is not None and (not isinstance(ref, str) or not ref or len(ref) > 1024):
            fail("Invalid highlight capture revision.")
    if documents is not None and not isinstance(documents, dict):
        fail("documents must map canonical paths to UTF-8 text.")
    if target and documents:
        fail("Historical highlight capture does not consume native overlays.")
    retained_members = {
        (member["id"], member["blob"]): member
        for shot in load_shots(root)
        for group in shot["groups"]
        for member in group["nodes"]
    }
    requested = [member for group in supplied for member in group["nodes"]]
    missing = [m for m in requested if (m["id"], m["blob"]) not in retained_members]
    candidates = []
    if missing:
        from .editor import document_files
        from .workspace import snapshot_from_files

        current = (
            git_snapshot(root, target)
            if target
            else snapshot_from_files(root, document_files(root, documents or {}))
        )
        candidates.append(current)
    available = {}

    def collect(snapshot):
        snapshot.require_valid()
        addresses = blob_ids(snapshot)
        for node in snapshot.nodes:
            for oid in addresses.get(node.id, []):
                raw = snapshot.files[node.path]
                title = next(
                    (line.lstrip("# ") for line in node.body.splitlines() if line.strip()), node.id
                )
                available[node.id, oid] = (
                    {"id": node.id, "blob": oid, "path": node.path, "title": title[:500]},
                    raw,
                )

    for snapshot in candidates:
        collect(snapshot)
    if base and any((m["id"], m["blob"]) not in available for m in missing):
        collect(git_snapshot(root, base, allow_empty=True))
    captured, retained = [], {}
    for group in supplied:
        members = []
        for requested in group["nodes"]:
            key = requested["id"], requested["blob"]
            if key in retained_members:
                member = retained_members[key]
                raw = retained_bytes(root, member)
            elif key in available:
                member, raw = available[key]
            else:
                fail(
                    f"Highlighted node {requested['id']} is unavailable or changed; "
                    "nothing submitted."
                )
            members.append(dict(member))
            retained[member["blob"]] = raw
        captured.append(
            {"text": group["text"], "color": checked_color(group["color"]), "nodes": members}
        )
    return publish(root, captured, retained, {"kind": "highlights"})


def publish(root, captured, retained, origin):
    """Publish one complete shot under the same lock/budgets for CLI and UI."""
    with workspace_lock(root):
        path = directory(root)
        existing = load_shots(root)
        if len(existing) >= MAX_SHOTS:
            fail(f"Spotlight storage is full ({MAX_SHOTS} spotlights); explicitly flush it.")
        shot_id = secrets.token_hex(16)
        while (path / f"{shot_id}.json").exists():
            shot_id = secrets.token_hex(16)
        shot = {
            "annotation_version": 1,
            "id": shot_id,
            "created_at": datetime.now(UTC).isoformat(),
            "origin": origin,
            "groups": captured,
        }
        raw = json.dumps(shot, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if (
            len(raw) > MAX_SHOT_BYTES
            or len(raw) + sum(p.stat().st_size for p in shot_files(path)) > MAX_LIST_BYTES
        ):
            fail("Spotlight metadata storage is full; explicitly flush it.")
        blob_directory = path / "blobs"
        blobs = blob_files(blob_directory)
        needed = sum(
            len(data) for oid, data in retained.items() if not (blob_directory / oid).exists()
        )
        if sum(p.stat().st_size for p in blobs) + needed > MAX_BLOB_BYTES:
            fail("Retained spotlight content exceeds 64 MiB; explicitly flush it.")
        ensure_ignored(root)
        blob_directory.mkdir(parents=True, exist_ok=True)
        for oid, data in retained.items():
            destination = blob_directory / oid
            if destination.exists():
                if destination.read_bytes() != data:
                    fail(
                        "A retained spotlight blob has unexpected contents; no spotlight published."
                    )
            else:
                atomic_file(destination, data)
        atomic_file(path / f"{shot_id}.json", raw)
    return shot


def preview(root, shot_id, group, member):
    if not isinstance(shot_id, str) or not SHOT_ID.fullmatch(shot_id):
        fail("Invalid shot ID.")
    if type(group) is not int or type(member) is not int or min(group, member) < 0:
        fail("Select existing zero-based label/member indices.")
    shot = next((shot for shot in load_shots(root) if shot["id"] == shot_id), None)
    if (
        shot is None
        or group >= len(shot["groups"])
        or member >= len(shot["groups"][group]["nodes"])
    ):
        fail("The spotlight member no longer exists; it may have been flushed.")
    reference = shot["groups"][group]["nodes"][member]
    raw = retained_bytes(root, reference)
    return {"reference": reference, "origin": shot["origin"], "text": raw.decode("utf-8")}


def retained_bytes(root, reference):
    file = directory(root) / "blobs" / reference["blob"]
    if file.is_symlink() or not file.is_file() or file.stat().st_size > MAX_FILE_BYTES:
        fail("Captured spotlight content is unavailable or unsafe.")
    with file.open("rb") as stream:
        raw = stream.read(MAX_FILE_BYTES + 1)
    if len(raw) > MAX_FILE_BYTES or blob_id(raw, reference["blob"]) != reference["blob"]:
        fail("Captured spotlight content does not match its Git blob address.")
    data, _ = read_document(raw, reference["path"])
    if data.get("id") != reference["id"]:
        fail("Captured spotlight content has a different node identity.")
    return raw


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
        blobs = blob_files(path / "blobs")
        if files or blobs:
            ensure_ignored(root)
        for file in files:
            file.unlink(missing_ok=True)
        for file in blobs:
            file.unlink(missing_ok=True)
        # Incomplete, unpublished atomic writes can be discarded by explicit flush.
        for parent in (path, path / "blobs"):
            if parent.exists():
                for temporary in parent.glob(".shot-*.tmp"):
                    if (
                        TEMP_FILE.fullmatch(temporary.name)
                        and not temporary.is_symlink()
                        and temporary.is_file()
                    ):
                        temporary.unlink(missing_ok=True)
    return {"flushed": len(files)}


def listing(root, refs=()):
    shots = deepcopy(load_shots(root))
    if not shots:
        return {"shots": [], "contexts": []}
    contexts, versions = [], {}
    for ref in dict.fromkeys([None, "HEAD", *refs]):
        name = ref or "workspace"
        try:
            snapshot = git_snapshot(root, ref) if ref else load_snapshot(root)
            snapshot.require_valid()
            versions[name] = blob_ids(snapshot)
            contexts.append({"ref": name, "commit": snapshot.commit, "available": True})
        except SpecError as error:
            versions[name] = None
            contexts.append(
                {
                    "ref": name,
                    "available": False,
                    "message": "; ".join(d.message for d in error.diagnostics),
                }
            )
    for shot in shots:
        for group in shot["groups"]:
            for member in group["nodes"]:
                member["resolution"] = {
                    name: "unavailable"
                    if mapping is None
                    else "absent"
                    if member["id"] not in mapping
                    else "exact"
                    if member["blob"] in mapping[member["id"]]
                    else "changed"
                    for name, mapping in versions.items()
                }
    return {"shots": shots, "contexts": contexts}
