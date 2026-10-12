"""Versioned engineering docs/input artifacts remain usable without remote assets."""

import re
import subprocess
from pathlib import Path
from xml.etree import ElementTree

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "path", ["README.md", "docs/architecture.md", "docs/own-spec.md", "branding/README.md"]
)
def test_engineering_entry_point_local_links_resolve(path):
    document = ROOT / path
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
        if target.startswith(("https://", "http://", "mailto:", "#")):
            continue
        target = target.split("#", 1)[0]
        assert (document.parent / target).exists(), (path, target)


def test_architecture_svg_is_accessible_self_contained_documentation():
    svg = ElementTree.parse(ROOT / "docs/architecture.svg").getroot()
    namespace = "{http://www.w3.org/2000/svg}"
    elements = list(svg.iter())
    ids = [element.attrib["id"] for element in elements if "id" in element.attrib]
    assert len(ids) == len(set(ids))
    assert svg.tag == namespace + "svg" and svg.attrib["role"] == "img"
    for labelled in svg.attrib["aria-labelledby"].split():
        assert any(element.attrib.get("id") == labelled and element.text for element in elements)
    for element in elements:
        assert element.tag.startswith(namespace)
        assert element.tag.removeprefix(namespace) not in {"script", "foreignObject", "image"}
        for key, value in element.attrib.items():
            assert not key.lower().startswith("on"), key
            if key.endswith("href"):
                assert value.startswith("#") and value[1:] in ids
    # The only URLs are local SVG marker references; system font fallbacks need no download.
    for reference in re.findall(
        r"url\(([^)]+)\)", (ROOT / "docs/architecture.svg").read_text(encoding="utf-8")
    ):
        assert reference.startswith("#") and reference[1:] in ids


def test_original_brand_inputs_are_preserved_and_svg_import_is_exact():
    original = ROOT / "Monochrome_Dachshund_Puppy_Emblem.svg"
    assert original.read_bytes() == (ROOT / "branding/dachshund.svg").read_bytes()
    assert (
        (ROOT / "Monochrome_Dachshund_Puppy_Emblem.png")
        .read_bytes()
        .startswith(b"\x89PNG\r\n\x1a\n")
    )
    attributes = subprocess.check_output(
        ["git", "check-attr", "text", "--", str(original), str(ROOT / "branding/dachshund.svg")],
        cwd=ROOT,
        text=True,
    ).splitlines()
    assert len(attributes) == 2 and all(line.endswith(": text: unset") for line in attributes)


def test_only_root_generated_settings_are_ignored_not_shared_launch_configuration():
    result = subprocess.run(
        [
            "git",
            "check-ignore",
            "--no-index",
            ".vscode/settings.json",
            ".vscode/launch.json",
            ".vscode/tasks.json",
            "specspec-dev.code-workspace",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert result.stdout.splitlines() == [".vscode/settings.json"]
