"""Contract-aware source changes with independent raw comparison facts.

Each exact declaration is resolved against both code versions, independently of
membership. Permitted strict/expanding/path-only edits stay quiet; raw byte/text/
location differences and mapping uncertainty remain available for detailed review.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from .model import SpecError
from .query_select import reachable
from .sources import BAD_OUTCOMES, SourceReader, text_lines
from .workspace import Snapshot


def reference_key(source: dict) -> str:
    return json.dumps(source, sort_keys=True)


@dataclass
class Reading:
    public: dict
    raw: bytes | None = None
    selected: list[list[str]] | None = None


class CodeVersion:
    def __init__(self, root: Path, snapshot: Snapshot, *, base=False, git_available=True):
        self.target = snapshot.commit or ("empty" if base else "workspace")
        self.empty = base and not snapshot.commit and git_available
        self.reader = None
        self.error = "No committed source version is available."
        self.cache: dict[str, Reading] = {}
        if not base or snapshot.commit:
            try:
                self.reader = SourceReader(root, ref=snapshot.commit)
            except (SpecError, ValueError, OSError) as error:
                self.error = str(error)

    def batch(self, sources: list[dict]):
        if self.reader is None:
            return
        ids = {s["blob"] for s in sources if "blob" in s}
        if self.reader.ref or self.reader.staged:
            # Populate the existing invocation-local blob cache in bulk, not via
            # one cat-file pair on each first path read. Never use index entries
            # as a substitute for saved workspace bytes.
            for source in sources:
                entry = self.reader.entries.get(self.reader.prefix + source["path"])
                if entry and entry[0] in {"100644", "100755"}:
                    ids.add(entry[1])
        try:
            self.reader.batch(ids)
        except (SpecError, ValueError, OSError) as error:
            for oid in ids - self.reader.blobs.keys():
                self.reader.blobs[oid] = str(error)

    def read(self, source: dict) -> Reading:
        key = reference_key(source)
        if key in self.cache:
            return self.cache[key]
        if self.reader is None:
            value = Reading(
                {
                    "path": source["path"],
                    "target": self.target,
                    "mode": source.get("mode", "file"),
                    "ranges": [],
                    "outcome": "missing" if self.empty else "unavailable",
                    "message": "The base source tree is empty." if self.empty else self.error,
                    "text_available": False,
                }
            )
        else:
            resolution = dict(self.reader.resolve(source))
            resolution["target"] = self.target
            value = Reading({**resolution, "text_available": False})
            try:
                # Even a strict region conflict can have known file bytes. Never
                # mistake its surviving fragments for a complete selected region.
                value.raw = self.reader.data(resolution["path"])
                value.public["byte_count"] = len(value.raw)
                lines = text_lines(value.raw)
                if resolution["outcome"] not in BAD_OUTCOMES:
                    ranges = (
                        ([[1, len(lines)]] if lines else [])
                        if resolution["outcome"] == "file"
                        else resolution["ranges"]
                    )
                    value.public.update(ranges=ranges, text_available=True)
                    value.selected = [lines[start - 1 : end] for start, end in ranges]
            except (SpecError, ValueError, UnicodeError, OSError) as error:
                value.public["read_message"] = str(error)
        self.cache[key] = value
        return value


def byte_change(before: Reading, after: Reading) -> str:
    if before.raw is not None and after.raw is not None:
        return "same" if before.raw == after.raw else "changed"
    if before.public["outcome"] == "missing" and after.raw is not None:
        return "added"
    if after.public["outcome"] == "missing" and before.raw is not None:
        return "removed"
    return "unavailable"


def contract_state(value: dict) -> str:
    """Validity of the declared reference, not equality of its file contents."""
    outcome = value["outcome"]
    if outcome in {"conflict", "missing"} or value["mode"] == "strict" and outcome == "modified":
        return "broken"
    if outcome in BAD_OUTCOMES:
        return "unavailable"
    if value["mode"] == "file" and outcome == "file":
        return "valid"  # Lines/bytes are optional for a path-only reference.
    if value["text_available"] and (
        outcome == "resolved" or value["mode"] == "expanding" and outcome == "modified"
    ):
        return "valid"
    return "unavailable"


def contract_change(before: Reading, after: Reading) -> str:
    """Compare contract validity while keeping permitted edits quiet."""
    a, b = contract_state(before.public), contract_state(after.public)
    if a == b == "valid":
        return "same"
    if before.public["outcome"] == after.public["outcome"] == "missing":
        return "same"
    signature = ("mode", "outcome", "ranges", "text_available")
    if (
        before.raw is not None
        and before.raw == after.raw
        and all(before.public[key] == after.public[key] for key in signature)
    ):
        # A pre-existing broken/unavailable mapping is still shown as such, but
        # identical file bytes/resolution facts establish no revision difference.
        return "same"
    if "unavailable" not in {a, b} and a != b:
        return "changed"
    return "unavailable"


def source_contract_impact(base: Snapshot, target: Snapshot, rows: list[dict]) -> dict:
    changed = {r["id"] for r in rows if r["contract"] == "changed"}
    affected = set(changed)
    for snapshot in (base, target):
        if snapshot.graph:
            affected.update(reachable(snapshot.graph, changed, ancestors=True))
    return {
        "source_contract_affected": sorted(affected),
        "source_contract_complete": all(r["contract"] != "unavailable" for r in rows),
    }


def source_comparisons(
    root: Path, base: Snapshot, target: Snapshot, *, git_available=True, node_ids=None
) -> list[dict]:
    old = {n.id: n for n in base.nodes if node_ids is None or n.id in node_ids}
    new = {n.id: n for n in target.nodes if node_ids is None or n.id in node_ids}
    references = [s for n in [*old.values(), *new.values()] for s in n.sources]
    if not references:
        return []
    before = CodeVersion(root, base, base=True, git_available=git_available)
    after = (
        before
        if target.commit and target.commit == base.commit
        else CodeVersion(root, target, git_available=git_available)
    )
    before.batch(references)
    if after is not before:
        after.batch(references)
    rows = []
    for node_id in sorted(old.keys() | new.keys()):
        declared = []
        for nodes in (old, new):
            values = defaultdict(list)
            for number, source in enumerate(
                nodes[node_id].semantic()["sources"] if node_id in nodes else [], 1
            ):
                values[reference_key(source)].append(number)
            declared.append(values)
        a, b = declared
        for key in sorted(a.keys() | b.keys()):
            source = json.loads(key)
            left, right = before.read(source), after.read(source)
            trustworthy = left.selected is not None and right.selected is not None
            content = (
                ("same" if left.selected == right.selected else "changed")
                if trustworthy
                else "unavailable"
            )
            location = (
                (
                    "same"
                    if (left.public["path"], left.public["ranges"])
                    == (right.public["path"], right.public["ranges"])
                    else "changed"
                )
                if trustworthy
                else "unavailable"
            )
            # Multiplicity is preserved; identical duplicate records are not
            # silently merged. Unequal declarations are removals/additions, not
            # heuristic pairings by path or symbol.
            for index in range(max(len(a[key]), len(b[key]))):
                base_number = a[key][index] if index < len(a[key]) else None
                target_number = b[key][index] if index < len(b[key]) else None
                rows.append(
                    {
                        "id": node_id,
                        "base_source": base_number,
                        "target_source": target_number,
                        "declaration": "="
                        if base_number and target_number
                        else "+"
                        if target_number
                        else "-",
                        "reference": source,
                        "base": left.public,
                        "target": right.public,
                        "contract": contract_change(left, right),
                        "bytes": byte_change(left, right),
                        "text": content,
                        "position": location,
                        "region": (
                            "unavailable"
                            if not trustworthy
                            else "modified"
                            if content == "changed"
                            else "relocated"
                            if location == "changed"
                            else "same"
                        ),
                    }
                )
    return rows
