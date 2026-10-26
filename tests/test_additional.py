from dataclasses import replace

import pytest
from click.testing import CliRunner
from test_git import git, setup_repository

from specspec.cli import main
from specspec.format import serialize
from specspec.git import git_snapshot, source_change_impact
from specspec.model import SpecError
from specspec.workspace import add_node, encode, load_snapshot, recover, update_node, write_journal


def test_changed_source_maps_to_implementation_and_ancestors(workspace):
    root, manifesto = workspace
    _, requirement = add_node(root, "requirement", [manifesto], "Behavior\n")
    source = root / "source.py"
    source.write_text("print('before')\n")
    _, implementation = add_node(
        root,
        "implementation",
        [requirement],
        "Mapping\n",
        sources=[{"path": "source.py"}],
    )
    setup_repository(root)
    git(root, "add", "source.py")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-m", "Source")
    base = git_snapshot(root, "HEAD")
    source.write_text("print('after')\n")
    result = source_change_impact(root, "HEAD", None, base, load_snapshot(root))
    assert result["source_changes"] == [
        {"path": "source.py", "implementation_ids": [implementation]}
    ]
    assert set(result["source_affected"]) == {manifesto, requirement, implementation}


def test_new_untracked_sources_are_reported(workspace):
    root, manifesto = workspace
    _, requirement = add_node(root, "requirement", [manifesto], "Behavior\n")
    setup_repository(root)
    base = git_snapshot(root, "HEAD")
    (root / "new.py").write_text("print('new')\n")
    target, implementation = add_node(
        root, "implementation", [requirement], "Mapping\n", sources=[{"path": "new.py"}]
    )
    result = source_change_impact(root, "HEAD", None, base, target)
    assert result["source_changes"] == [{"path": "new.py", "implementation_ids": [implementation]}]


def test_generated_documents_validate_before_hashing_bad_library_inputs(workspace):
    root, _ = workspace
    node = load_snapshot(root).nodes[0]
    with pytest.raises(SpecError):
        serialize(replace(node, parents=[{}, "invalid"]))
    with pytest.raises(SpecError):
        serialize(replace(node, type="implementation", format_version=None, sources=[{}]))


def test_query_errors_retain_structured_incomplete_evidence(workspace):
    import json

    root, _ = workspace
    (root / ".specspec" / "bad.txt").write_text("bad")
    result = CliRunner().invoke(main, ["--root", str(root), "query", "--json"])
    assert result.exit_code == 1
    assert not json.loads(result.output)["ok"]


def test_orphan_staging_requires_recovery(workspace):
    root, manifesto = workspace
    (root / ".specspec-local" / "stage-0").write_bytes(b"unfinished")
    assert not load_snapshot(root).valid
    with pytest.raises(SpecError, match="recover"):
        update_node(root, manifesto, body="Another edit\n")
    recover(root)
    assert load_snapshot(root).valid


def test_init_recovery_refuses_extra_files_before_modifying_anything(workspace):
    root, _ = workspace
    snapshot = load_snapshot(root)
    node = snapshot.nodes[0]
    write_journal(
        root / ".specspec-local",
        {
            "kind": "init",
            "files": {
                node.path: {"old": None, "new": encode(snapshot.files[node.path])},
            },
        },
    )
    extra = root / ".specspec" / "unexpected.txt"
    extra.write_text("intervening edit")
    with pytest.raises(SpecError, match="recovery changed nothing"):
        recover(root)
    assert (root / node.path).read_bytes() == snapshot.files[node.path]
    assert extra.read_text() == "intervening edit"
