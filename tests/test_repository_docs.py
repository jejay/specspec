"""Repository documents, README figures and the self-specification stay consistent."""

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree

import pytest

ROOT = Path(__file__).resolve().parents[1]

# The graph is the design record; these are the entry points, guides and procedures.
DOCUMENTS = [
    "README.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "vscode/README.md",
    "src/specspec/templates/AGENTS.md",
    "example/gantt/README.md",
    "example/gantt/AGENTS.md",
    "example/gantt/history/WALKTHROUGH.md",
]
FIGURES = sorted((ROOT / "docs/images").glob("*.svg"))
COMMAND_WORDS = {
    "specspec",
    "query",
    "check",
    "diff",
    "add",
    "update",
    "delete",
    "init",
    "recover",
    "sources",
    "spotlight",
    "npm",
    "uv",
    "pipx",
    "git",
    "python",
    "e.g",
    "i.e",
    "vs",
}


@pytest.mark.parametrize("path", DOCUMENTS)
def test_document_local_links_resolve(path):
    document = ROOT / path
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
        if target.startswith(("https://", "http://", "mailto:", "#")):
            continue
        target = target.split("#", 1)[0]
        assert (document.parent / target).exists(), (path, target)


def test_documents_use_id_only_node_path_examples():
    paths = [ROOT / name for name in DOCUMENTS] + list((ROOT / "example/gantt").rglob("*.md"))
    for path in paths:
        if ".specspec" in path.parts:
            continue
        text = path.read_text(encoding="utf8")
        assert "--slug" not in text, path
        assert not re.search(r"[A-Za-z0-9_-]{7}=[A-Za-z0-9_-]+\.md", text), path
        assert "???????=*.md" not in text, path
        assert "<slug>" not in text, path
        assert not re.search(r"filename[- ]only|filename summary|summary-only", text, re.I), path


def test_repository_agents_md_is_a_repository_section_plus_the_shipped_guide():
    guide = (ROOT / "src/specspec/templates/AGENTS.md").read_bytes().replace(b"\r\n", b"\n")
    agents = (ROOT / "AGENTS.md").read_bytes().replace(b"\r\n", b"\n")
    assert agents.endswith(guide)
    assert len(agents) > len(guide)


def node_text(path):
    body = path.read_text(encoding="utf-8").split("\n---", 1)[1]
    body = re.sub(r"```.*?```", " ", body, flags=re.S)
    return re.sub(r"`[^`]*`", " CODE ", body)


@pytest.mark.parametrize("path", sorted((ROOT / ".specspec").glob("*.md")), ids=lambda p: p.stem)
def test_own_graph_text_has_no_doubled_words_or_lowercase_sentence_starts(path):
    text = node_text(path)
    for match in re.finditer(r"\b([A-Za-z]+)(?:[ \t]+|[ \t]*\r?\n[ \t]*)\1\b", text, re.I):
        assert match.group(1).lower() in {"that", "had"}, match.group(0)
    flat = " ".join(text.split())
    for match in re.finditer(r"(?:^|[.!?]\s+)([a-z][^\s,;:()]*)", flat):
        word = match.group(1)
        assert word in COMMAND_WORDS or re.search(r"[_\-./=]", word), flat[match.start(1) :][:60]


@pytest.mark.parametrize("path", [p.relative_to(ROOT).as_posix() for p in FIGURES])
def test_readme_figures_are_accessible_self_contained_svgs(path):
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
    for reference in re.findall(r"url\(([^)]+)\)", (ROOT / path).read_text(encoding="utf-8")):
        assert reference.startswith("#") and reference[1:] in ids


def test_readme_shows_every_figure_in_light_and_dark():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    names = {path.stem.rsplit("-", 1)[0] for path in FIGURES}
    assert names
    for name in names:
        for theme in ("light", "dark"):
            assert (ROOT / f"docs/images/{name}-{theme}.svg").is_file()
            assert f"docs/images/{name}-{theme}.svg" in readme


def test_readme_figures_match_their_generator(tmp_path):
    pytest.importorskip("fontTools")
    script = ROOT / "tools/readme_figures.py"
    spec = importlib.util.spec_from_file_location("readme_figures", script)
    figures = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(figures)
    mono = next((path for path in figures.MONO_CANDIDATES if path.exists()), None)
    if not figures.MANROPE.exists() or mono is None:
        pytest.skip("the brand kit's Manrope or a DejaVu Sans Mono font is not available")
    subprocess.run(
        [sys.executable, str(ROOT / "tools/readme_figures.py"), "--out", str(tmp_path)],
        check=True,
        capture_output=True,
    )
    for path in FIGURES:
        expected = path.read_bytes().replace(b"\r\n", b"\n")
        assert (tmp_path / path.name).read_bytes() == expected, path.name


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
