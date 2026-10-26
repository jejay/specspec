"""Bounded explicit multi-node authoring; no automatic repair or descendant selection."""

from __future__ import annotations

import re
from dataclasses import replace
from pathlib import PurePosixPath

from .body_replacements import MAX_REPLACEMENTS, input_bytes, replace_body
from .deletion import deletion_plan, deletion_warnings
from .inspection import findings, walks
from .model import MAX_FILE_BYTES, Diagnostic, SpecError
from .workspace import mutate, new_node, require_node, serialize

MAX_BATCH_BYTES = 16 * 1024 * 1024
MAX_EDITS = 1024


def fail(message):
    raise SpecError([Diagnostic("BATCH", message)], 2)


def count_body_bytes(body, total):
    """Charge each decoded input before retaining or reading another body."""
    if not isinstance(body, str):
        fail("body must be UTF-8 text.")
    size = len(body.encode("utf8"))
    if size > MAX_FILE_BYTES:
        fail("Body exceeds 1 MiB.")
    total += size
    if total > MAX_BATCH_BYTES:
        fail("Invocation bodies exceed 16 MiB in total.")
    return total


def input_budget(edits):
    """Bound supplied text, including both sides of every replacement, before I/O."""
    total, replacements = 0, 0
    for edit in edits:
        if "body" in edit:
            total = count_body_bytes(edit["body"], total)
        if "replacements" in edit:
            total += input_bytes(edit["replacements"])
            replacements += len(edit["replacements"])
            if replacements > MAX_REPLACEMENTS:
                fail("An editing invocation accepts at most 1024 replacement pairs.")
            if total > MAX_BATCH_BYTES:
                fail(
                    "Invocation bodies exceed 16 MiB in total, including OLD/NEW replacement text."
                )
    return total


def prepare(value):
    if (
        not isinstance(value, dict)
        or set(value) != {"edits"}
        or not isinstance(value["edits"], list)
        or not 1 <= len(value["edits"]) <= MAX_EDITS
    ):
        fail("Expected an object with 1-1024 explicit edits.")
    edits = []
    for original in value["edits"]:
        if not isinstance(original, dict):
            fail("Each edit must be an object.")
        edit = dict(original)
        op = edit.get("op")
        fields = {
            "add": {"op", "as", "type", "parents", "body", "sources"},
            "update": {"op", "id", "parents", "body", "replacements", "sources"},
            "delete": {"op", "ids"},
        }
        if not isinstance(op, str) or op not in fields or set(edit) - fields[op]:
            fail("Unknown batch operation or fields.")
        if "body" in edit and "replacements" in edit:
            fail("Use whole-body text or exact replacements, not both.")
        if op == "update" and not set(edit).intersection(
            {"body", "replacements", "parents", "sources"}
        ):
            fail("An update must name at least one replacement field.")
        if op == "add" and (
            not isinstance(edit.get("type", "requirement"), str)
            or edit.get("type", "requirement") not in {"requirement", "implementation"}
            or "body" not in edit
            or "parents" not in edit
        ):
            fail("add requires body, parents and a requirement/implementation type.")
        if "parents" in edit and (
            not isinstance(edit["parents"], list)
            or any(not isinstance(p, str) for p in edit["parents"])
        ):
            fail("parents must be an array of full IDs or batch aliases.")
        if "sources" in edit and not isinstance(edit["sources"], list):
            fail("sources must be an array.")
        edits.append(edit)
    input_budget(edits)
    return edits


def apply_edits(root, edits, *, require_valid=False, dry_run=False, confirm=None):
    receipt = {}

    def operation(before):
        aliases, created, used = {}, {}, set()
        reserved = (
            {n.id for n in before.nodes}
            | {PurePosixPath(p).stem for p in before.files}
            | {p for n in before.nodes for p in n.parents}
        )
        for index, edit in enumerate(edits):
            if edit["op"] == "add":
                alias = edit.get("as")
                if alias is not None and (
                    not isinstance(alias, str)
                    or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", alias)
                    or alias in aliases
                ):
                    fail("New-node aliases must be unique short identifiers.")
                node = new_node(
                    edit.get("type", "requirement"), [], edit["body"], reserved_ids=reserved
                )
                reserved.add(node.id)
                created[index] = node
                if alias is not None:
                    aliases[alias] = node.id

        def identity(value):
            if not isinstance(value, str):
                fail("Node identities must be strings.")
            if value.startswith("$"):
                if value[1:] not in aliases:
                    fail("Unknown batch alias: " + value)
                return aliases[value[1:]]
            return value

        def existing(value):
            node_id = identity(value)
            if value.startswith("$"):
                fail("Configure new nodes in their add step; aliases are parent references.")
            return require_node(before, node_id)

        changes, ids, deleted = {}, [], []
        for index, edit in enumerate(edits):
            if edit["op"] == "delete":
                values = edit.get("ids")
                if not isinstance(values, list) or not values:
                    fail("delete requires a nonempty ids array.")
                for value in values:
                    node = existing(value)
                    id = node.id
                    if node.type == "manifesto":
                        fail("The manifesto cannot be deleted.")
                    if id in used:
                        fail("Conflicting or duplicate edits for " + id)
                    used.add(id)
                    deleted.append(id)
                    ids.append(id)
                    changes[node.path] = None
                continue
            node = created[index] if edit["op"] == "add" else existing(edit.get("id"))
            if node.id in used:
                fail("Conflicting or duplicate edits for " + node.id)
            used.add(node.id)
            ids.append(node.id)
            parents = [identity(p) for p in edit.get("parents", node.parents)]
            if node.type == "manifesto" and parents:
                fail("The manifesto cannot be reparented.")
            candidate = replace(
                node,
                body=(
                    replace_body(node.body, edit["replacements"], path=node.path)
                    if "replacements" in edit
                    else edit.get("body", node.body)
                ),
                parents=parents,
                sources=edit.get("sources", node.sources),
            )
            changes[node.path] = serialize(candidate, before.files.get(node.path))
        plan = deletion_plan(before, deleted) if deleted else None
        if plan and not dry_run:
            if confirm is None and deletion_warnings(plan):
                raise SpecError(
                    [
                        *deletion_warnings(plan),
                        Diagnostic(
                            "DELETE_CONFIRMATION",
                            "Confirm selected uncommitted deletion before applying.",
                        ),
                    ]
                )
            if confirm is not None and not confirm(plan):
                raise SpecError(
                    [Diagnostic("DELETE_CANCELLED", "Batch cancelled; no files changed.")]
                )
        receipt.update(
            changed_ids=ids,
            deleted_ids=deleted,
            aliases=aliases,
            nodes=[{"id": id, "path": f"_specspec/{id}.md"} for id in ids],
            deletion_plan=plan,
            applied=not dry_run,
            affected=sorted(walks(before.graph, ids)),
        )
        return changes

    result = mutate(root, operation, require_valid=require_valid, dry_run=dry_run)
    receipt.update(findings(result))
    receipt["affected"] = sorted(
        set(receipt["changed_ids"])
        | set(receipt["affected"])
        | walks(result.graph, receipt["changed_ids"])
    )
    return result, receipt
