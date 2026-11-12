"""specspec guide brings AGENTS.md to the installed guide by exact match, nothing else."""

from click.testing import CliRunner

from specspec import __version__
from specspec.cli import main
from specspec.guide import current_guide, earlier_guides, place_guide, with_endings


def run(root, *args):
    return CliRunner().invoke(main, ["--root", str(root), "guide", *args])


def test_an_earlier_release_guide_is_replaced_and_every_other_byte_stays(workspace):
    root, _ = workspace
    # Checkouts may hold either line ending; the owner's text around it decides here.
    earlier = with_endings(earlier_guides()["0.0.1"], False)
    owner_before, owner_after = b"# Our rules\n\nUse tabs.\n\n", b"\n## Local notes\nKeep.\n"
    (root / "AGENTS.md").write_bytes(owner_before + earlier + owner_after)
    result = run(root)
    assert result.exit_code == 0, result.output
    assert "guide of an earlier release replaced" in result.stdout and __version__ in result.stdout
    assert (root / "AGENTS.md").read_bytes() == (
        owner_before + with_endings(current_guide(), False) + owner_after
    )
    again = run(root)
    assert again.exit_code == 0 and "guide already current" in again.stdout


def test_crlf_files_keep_their_line_endings(workspace):
    root, _ = workspace
    earlier = with_endings(earlier_guides()["0.0.1"], True)
    (root / "AGENTS.md").write_bytes(b"Owner\r\n\r\n" + earlier)
    assert run(root).exit_code == 0
    assert (root / "AGENTS.md").read_bytes() == b"Owner\r\n\r\n" + with_endings(
        current_guide(), True
    )


def test_a_hand_edited_guide_is_left_alone_with_an_explanation(workspace):
    root, _ = workspace
    edited = with_endings(current_guide(), False).replace(b"Routine", b"Our routine", 1)
    (root / "AGENTS.md").write_bytes(edited)
    result = run(root)
    assert result.exit_code == 1
    assert "edited by hand" in result.stderr and "specspec guide --print" in result.stderr
    assert (root / "AGENTS.md").read_bytes() == edited


def test_files_without_a_guide_get_one_and_print_changes_nothing(workspace):
    root, _ = workspace
    (root / "AGENTS.md").unlink()
    created = run(root)
    assert created.exit_code == 0 and "created" in created.stdout
    assert (root / "AGENTS.md").read_bytes() == current_guide()
    (root / "AGENTS.md").write_bytes(b"Owner only")
    appended = run(root)
    assert appended.exit_code == 0 and "guide appended" in appended.stdout
    assert (root / "AGENTS.md").read_bytes() == b"Owner only\n\n" + with_endings(
        current_guide(), False
    )
    printed = CliRunner().invoke(main, ["guide", "--print"])
    assert printed.exit_code == 0 and printed.stdout_bytes == current_guide()


def test_every_carried_guide_differs_from_the_current_one_and_is_recognized():
    current = with_endings(current_guide(), False)
    for version, guide in earlier_guides().items():
        guide = with_endings(guide, False)
        assert guide != current, version
        data, action = place_guide(b"Prefix\n\n" + guide)
        assert action == "replaced" and data == b"Prefix\n\n" + current, version
