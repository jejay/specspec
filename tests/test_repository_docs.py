"""Versioned engineering docs/input artifacts remain usable without remote assets."""

import hashlib
import json
import re
import subprocess
from pathlib import Path
from xml.etree import ElementTree

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "path",
    [
        "README.md",
        "AGENTS.md",
        "INTENTION_SPEC.md",
        "CONCLUSION_SPEC.md",
        "branding/README.md",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        "vscode/README.md",
        "electron/README.md",
        "src/specspec/templates/AGENTS.md",
    ]
    + [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / "docs").rglob("*.md"))]
    + [
        "example/gantt/README.md",
        "example/gantt/AGENTS.md",
        "example/gantt/history/WALKTHROUGH.md",
    ],
)
def test_engineering_entry_point_local_links_resolve(path):
    document = ROOT / path
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
        if target.startswith(("https://", "http://", "mailto:", "#")):
            continue
        target = target.split("#", 1)[0]
        assert (document.parent / target).exists(), (path, target)


def test_current_documentation_uses_id_only_node_path_examples():
    paths = [
        ROOT / name
        for name in ["README.md", "AGENTS.md", "INTENTION_SPEC.md", "CONCLUSION_SPEC.md"]
    ]
    paths += list((ROOT / "docs").rglob("*.md")) + list((ROOT / "docs").glob("*.svg"))
    paths += list((ROOT / "example/gantt").rglob("*.md"))
    for path in paths:
        if ".specspec" in path.parts:
            continue
        text = path.read_text(encoding="utf8")
        assert "--slug" not in text, path
        assert not re.search(r"[A-Za-z0-9_-]{7}=[A-Za-z0-9_-]+\.md", text), path
        assert "???????=*.md" not in text, path
        assert "<slug>" not in text, path
        assert not re.search(r"filename[- ]only|filename summary|summary-only", text, re.I), path


@pytest.mark.parametrize("path", ["docs/architecture.svg", "docs/architecture-interfaces.svg"])
def test_architecture_svg_is_accessible_self_contained_documentation(path):
    svg = ElementTree.parse(ROOT / path).getroot()
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
    for reference in re.findall(r"url\(([^)]+)\)", (ROOT / path).read_text(encoding="utf-8")):
        assert reference.startswith("#") and reference[1:] in ids


def test_architecture_svg_exposes_actor_interfaces_and_distinct_save_workflows():
    svg = ElementTree.parse(ROOT / "docs/architecture.svg").getroot()
    groups = {
        element.attrib["id"]: element
        for element in svg.iter("{http://www.w3.org/2000/svg}g")
        if "id" in element.attrib
    }
    # Check the overview's reading structure, not coordinates, paint or exact prose.
    for group_id in (
        "owner-entry",
        "agent-entry",
        "conversation",
        "visual-workspace",
        "cli-interface",
        "python-authority",
        "project-data",
        "refresh-loop",
        "managed-save",
        "native-save",
        "review-loop",
    ):
        assert group_id in groups, group_id
        assert groups[group_id].attrib.get("aria-label", "").strip(), group_id
        assert "".join(groups[group_id].itertext()).strip(), group_id
    assert groups["managed-save"] is not groups["native-save"]


def test_interface_zoom_names_the_contracts_and_shows_a_current_json_envelope():
    from specspec.model import API_VERSION

    svg = ElementTree.parse(ROOT / "docs/architecture-interfaces.svg").getroot()
    elements = {element.attrib["id"]: element for element in svg.iter() if "id" in element.attrib}
    for group_id in (
        "renderer-port",
        "host-coordination",
        "message-contract",
        "subprocess-contract",
        "cli-facade",
        "python-library",
        "library-contract",
        "agent-cli",
        "python-embedding",
        "validity-contract",
        "render-handshake",
        "native-edit-trace",
        "command-routing",
    ):
        assert elements[group_id].attrib.get("aria-label", "").strip(), group_id
    envelope = json.loads("".join(elements["json-envelope"].itertext()))
    assert envelope == {
        "api_version": API_VERSION,
        "ok": True,
        "result": {},
        "diagnostics": [],
    }


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


def test_selected_identity_imports_and_built_host_assets_match():
    manifest = json.loads((ROOT / "branding/identity.sha256.json").read_text(encoding="utf8"))
    assert manifest["activity-icon.svg"]["source"] == "final/icons/specspec-icon-24.svg"
    assert manifest["app-icon.png"]["source"] == "final/png/specspec-app-icon-512.png"
    for name, record in manifest.items():
        data = (ROOT / "branding" / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == record["sha256"]
        outputs = (
            [
                ("vscode/media", "specspec.svg" if name.endswith(".svg") else name),
                (
                    "electron/build/media" if name.endswith(".svg") else "electron/build",
                    "specspec.svg" if name.endswith(".svg") else name,
                ),
            ]
            if name in {"activity-icon.svg", "app-icon.png"}
            else []
        )
        for output, target in outputs:
            built = ROOT / output / target
            if built.exists():
                assert built.read_bytes() == data, built
    attributes = subprocess.check_output(
        ["git", "check-attr", "text", "--", "branding/activity-icon.svg"],
        cwd=ROOT,
        text=True,
    )
    assert attributes.strip().endswith(": text: unset")
    svg = ElementTree.parse(ROOT / "branding/activity-icon.svg").getroot()
    assert svg.attrib["viewBox"] == "0 0 24 24"
    assert "currentColor" in (ROOT / "branding/activity-icon.svg").read_text(encoding="utf8")
    png = (ROOT / "branding/app-icon.png").read_bytes()
    assert png.startswith(b"\x89PNG\r\n\x1a\n")
    assert int.from_bytes(png[16:20], "big") == 512
    assert int.from_bytes(png[20:24], "big") == 512


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
