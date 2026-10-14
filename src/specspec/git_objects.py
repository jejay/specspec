"""Bounded local Git object batches. Cache hints are verified Git blob bytes."""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
import threading
from pathlib import Path

from .model import MAX_FILE_BYTES, Diagnostic, SpecError

BATCH_COUNT = 256
BATCH_BYTES = 8 * 1024 * 1024
OBJECT_ID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")


def fail(message: str) -> None:
    raise SpecError([Diagnostic("GIT", message)], 2)


def batch_request(root: Path, option: str, ids: list[str], limit: int) -> bytes:
    """Kill on oversized output or timeout; never fetch missing local objects."""
    streams: dict[str, bytes] = {}
    errors: list[str] = []
    try:
        child = subprocess.Popen(
            ["git", "-C", str(root), "cat-file", option],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={
                **os.environ,
                "GIT_NO_LAZY_FETCH": "1",
                "GIT_OPTIONAL_LOCKS": "0",
                "GIT_ALLOW_PROTOCOL": "",
            },
        )
    except OSError as error:
        fail(str(error))

    def receive(name, stream, maximum):
        try:
            data = stream.read(maximum + 1)
            streams[name] = data
            if len(data) > maximum:
                errors.append("Git object response exceeds its batch budget.")
                child.kill()
        except OSError as error:
            errors.append(str(error))
        finally:
            stream.close()

    readers = [
        threading.Thread(target=receive, args=("out", child.stdout, limit), daemon=True),
        threading.Thread(target=receive, args=("err", child.stderr, 65536), daemon=True),
    ]

    def send():
        try:
            child.stdin.write(("\n".join(ids) + "\n").encode("ascii"))
            child.stdin.close()
        except OSError as error:
            errors.append(str(error))

    readers.append(threading.Thread(target=send, daemon=True))
    for reader in readers:
        reader.start()
    try:
        child.wait(timeout=20)
    except (OSError, subprocess.TimeoutExpired) as error:
        errors.append(str(error))
        child.kill()
        child.wait(timeout=5)
    finally:
        for reader in readers:
            reader.join(timeout=5)
    if errors or any(reader.is_alive() for reader in readers):
        fail("; ".join(errors) or "Git object stream did not finish.")
    if child.returncode:
        fail(streams.get("err", b"").decode("utf-8", errors="replace") or "Git object read failed.")
    return streams.get("out", b"")


def blob_id(raw: bytes, address: str) -> str:
    algorithm = "sha256" if len(address) == 64 else "sha1"
    return hashlib.new(algorithm, b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def read_blobs(
    root: Path, ids: list[str], hints: dict[str, bytes] | None = None
) -> tuple[dict[str, bytes], dict[str, str]]:
    """Return bounded eligible blobs and per-object availability/size errors."""
    pending = sorted(set(ids))
    if any(not OBJECT_ID.fullmatch(oid) for oid in pending):
        fail("Invalid Git object address.")
    blobs, failures = {}, {}
    hints = hints or {}
    for offset in range(0, len(pending), BATCH_COUNT):
        group = pending[offset : offset + BATCH_COUNT]
        metadata = batch_request(root, "--batch-check", group, len(group) * 160)
        rows = metadata.splitlines()
        if len(rows) != len(group):
            fail("Incomplete Git object metadata batch.")
        accepted = []
        for oid, row in zip(group, rows, strict=True):
            fields = row.split()
            if fields == [oid.encode(), b"missing"]:
                failures[oid] = "Git node object is unavailable locally."
                continue
            if (
                len(fields) != 3
                or fields[0] != oid.encode()
                or not fields[2].isdigit()
                or len(fields[2]) > 16
            ):
                fail("Malformed or mismatched Git object metadata.")
            size = int(fields[2])
            if fields[1] != b"blob":
                failures[oid] = "Git node object must be a blob."
            elif size > MAX_FILE_BYTES:
                failures[oid] = "Node exceeds the 1 MiB limit."
            elif oid in hints and len(hints[oid]) == size and blob_id(hints[oid], oid) == oid:
                blobs[oid] = hints[oid]
            else:
                accepted.append((oid, size))
        chunks, chunk, total = [], [], 0
        for entry in accepted:
            if chunk and total + entry[1] > BATCH_BYTES:
                chunks.append(chunk)
                chunk, total = [], 0
            chunk.append(entry)
            total += entry[1]
        if chunk:
            chunks.append(chunk)
        for chunk in chunks:
            raw = batch_request(
                root,
                "--batch",
                [oid for oid, _ in chunk],
                sum(s for _, s in chunk) + 160 * len(chunk),
            )
            cursor = 0
            for oid, size in chunk:
                end = raw.find(b"\n", cursor)
                if end < 0 or raw[cursor:end].split() != [
                    oid.encode(),
                    b"blob",
                    str(size).encode(),
                ]:
                    fail("Malformed or mismatched Git blob framing.")
                cursor = end + 1
                value = raw[cursor : cursor + size]
                cursor += size
                if len(value) != size or raw[cursor : cursor + 1] != b"\n":
                    fail("Truncated Git blob batch.")
                if blob_id(value, oid) != oid:
                    fail("Git blob bytes do not match their object address.")
                blobs[oid] = value
                cursor += 1
            if cursor != len(raw):
                fail("Unexpected trailing Git blob bytes.")
    return blobs, failures
