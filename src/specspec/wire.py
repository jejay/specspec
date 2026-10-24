"""API 7 projection; parsed bindings and file inventory retain independent availability."""

from copy import deepcopy


def snapshot(value):
    # Relationships are already present in each node's parents.
    return {key: val for key, val in value.items() if key != "edges"}


def comparison(value, *, target=True):
    current = {n["id"]: n for n in value["target"]["nodes"]}
    result = {key: val for key, val in value.items() if key not in {"base", "target"}}
    result["base"] = {
        key: val for key, val in value["base"].items() if key not in {"nodes", "edges"}
    }
    result["before"] = [n for n in value["base"]["nodes"] if current.get(n["id"]) != n]
    if target:
        result["target"] = snapshot(value["target"])
    return result


def loaded(value):
    result = {
        key: val for key, val in value.items() if key not in {"snapshot", "diff", "diagnostics"}
    }
    result["snapshot"] = snapshot(value["snapshot"])
    if value.get("diff"):
        result["diff"] = comparison(value["diff"], target=False)
    return result


def expand_comparison(value, current=None):
    """Independent Python round-trip oracle for protocol regression tests."""
    result = deepcopy(value)
    result["target"] = deepcopy(current or value["target"])
    target = {n["id"]: n for n in result["target"]["nodes"]}
    added = {
        c["id"]
        for c in result["changes"]
        if c["kind"] == "added" or c.get("base_available") is False
    }
    before = {n["id"]: n for n in result.pop("before")}
    base = {key: node for key, node in target.items() if key not in added}
    base.update(before)
    result["base"]["nodes"] = [base[key] for key in sorted(base)]
    for name in ["base", "target"]:
        result[name]["edges"] = sorted(
            [p, n["id"]] for n in result[name]["nodes"] for p in n["parents"]
        )
    return result
