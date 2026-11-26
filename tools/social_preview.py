"""Draw the repository's GitHub social preview as branding/social-preview.svg and .png.

The card has GitHub's recommended size of 1280 x 640. Its text is outlined from the
brand's Manrope font with the helpers of tools/readme_figures.py, and the logo is
branding/specspec-logo-dark.svg, so the SVG needs no fonts. With resvg on PATH the
script also renders the PNG, which is uploaded under Settings > General > Social
preview. Run it with any Python that has fontTools:

    python tools/social_preview.py

The pictogram uses the graph editor's node shapes without text: a circular manifesto,
rounded requirement cards and square implementation nodes, colored by their depth
from why to how. One implementation node is drawn with all its ancestors on heavier
lines, so the card shows the chain of intentions behind one piece of work.
"""

from __future__ import annotations

import argparse
import html
import math
import re
import shutil
import subprocess
from pathlib import Path

from fontTools.pens.transformPen import TransformPen
from readme_figures import MANROPE, RelativePathPen, face, mix, num

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 1280, 640
BG, INK, MUTED, FAINT, EDGE = "#18202B", "#ECF1FA", "#B8C4D4", "#7D8A9C", "#435369"
STOPS = [
    (0, "#AE89E2"),
    (0.24, "#7BA4EF"),
    (0.45, "#5ECBD2"),
    (0.64, "#98C86F"),
    (0.83, "#E5BA58"),
    (1, "#F28F82"),
]
SLANT = math.tan(math.radians(10))  # Manrope has no italic; Why is slanted instead.
LEFT = 84
BASELINE = 568  # the footer and the why/how labels

# GitHub's mark-github Octicon (16 x 16, MIT License).
GITHUB_MARK = (
    "M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01"
    "-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36"
    "-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2"
    "-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95"
    "-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53"
    ".34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995"
    " 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"
)

# The pictogram: kind, depth and row of each node. Node d has two parents, and the
# ancestors of f1 run as a diamond from the manifesto to d and straight on to f1.
NODES = {
    "root": ("manifesto", 0, 2.4),
    "a": ("requirement", 1, 1.2),
    "b": ("requirement", 1, 3.6),
    "c": ("requirement", 2, 0),
    "d": ("requirement", 2, 1.8),
    "e": ("requirement", 2, 4.2),
    "c1": ("implementation", 3, 0),
    "f": ("requirement", 3, 1.8),
    "g": ("requirement", 3, 3.4),
    "e1": ("implementation", 3, 4.8),
    "f1": ("implementation", 4, 1.8),
    "g1": ("implementation", 4, 3.4),
}
EDGES = [
    ("root", "a"),
    ("root", "b"),
    ("a", "c"),
    ("a", "d"),
    ("b", "d"),
    ("b", "e"),
    ("c", "c1"),
    ("d", "f"),
    ("e", "g"),
    ("e", "e1"),
    ("f", "f1"),
    ("g", "g1"),
]
FOCUS = "f1"
# Clean spectrum stops per kind and depth instead of in-between mixtures.
COLOR_AT = {
    ("manifesto", 0): 0,
    ("requirement", 1): 0.24,
    ("requirement", 2): 0.45,
    ("requirement", 3): 0.64,
    ("implementation", 3): 0.83,
    ("implementation", 4): 1,
}
GRAPH = dict(x0=820, x1=1170, y0=132, y1=468, node=40, ring=9, edge=2.75, chain=6.5)


def spectrum_at(t: float) -> str:
    for (o1, c1), (o2, c2) in zip(STOPS, STOPS[1:], strict=False):
        if t <= o2:
            return mix(c1, c2, (t - o1) / (o2 - o1))
    return STOPS[-1][1]


def gradient(gid: str, x1: float, x2: float) -> str:
    stops = "".join(f'<stop offset="{num(o)}" stop-color="{c}"/>' for o, c in STOPS)
    return (
        f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{num(x1)}" y1="0" '
        f'x2="{num(x2)}" y2="0">{stops}</linearGradient>'
    )


def text(
    weight: float,
    value: str,
    x: float,
    baseline: float,
    size: float,
    fill: str,
    slant: float = 0.0,
    anchor: str = "start",
) -> tuple[str, float]:
    """Outlined Manrope text; a slant leans the glyphs to the right around the baseline."""
    font = face(str(MANROPE), weight)
    width = font.width(value, size)
    x -= width if anchor == "end" else 0
    scale = size / font.upm
    pen = RelativePathPen(font.glyphs)
    for name, offset in font._advances(value, size):
        if name is not None:
            transform = (scale, 0, scale * slant, -scale, x + offset, baseline)
            font.glyphs[name].draw(TransformPen(pen, transform))
    return f'<path fill="{fill}" d="{"".join(pen.commands)}"/>', width


def logo(left: float, top: float, height: float) -> str:
    """The dark logo, placed by its visible artwork (x 66-872, y 33-231 of 960 x 256)."""
    scale = height / 198
    source = (ROOT / "branding" / "specspec-logo-dark.svg").read_text(encoding="utf8")
    body = re.sub(r"<(title|desc)[^>]*>.*?</\1>\s*", "", source, flags=re.S)
    return re.sub(
        r"<svg[^>]*>",
        f'<svg x="{num(left - 66 * scale)}" y="{num(top - 33 * scale)}" '
        f'width="{num(960 * scale)}" height="{num(256 * scale)}" viewBox="0 0 960 256">',
        body.strip(),
        count=1,
    )


def graph() -> list[str]:
    g = GRAPH
    depth = max(d for _, d, _ in NODES.values())
    rows = max(r for _, _, r in NODES.values())
    pos = {
        key: (
            g["x0"] + (g["x1"] - g["x0"]) * d / depth,
            g["y0"] + (g["y1"] - g["y0"]) * r / rows,
        )
        for key, (_, d, r) in NODES.items()
    }
    half, ring = g["node"] / 2, g["node"] / 2 + 4
    chain = {FOCUS}
    for _ in NODES:
        chain |= {p for p, q in EDGES if q in chain}
    parts = []
    for heavy in (False, True):
        for p, q in EDGES:
            if (p in chain and q in chain) != heavy:
                continue
            (px, py), (tx, ty) = pos[p], pos[q]
            tx -= half
            if NODES[p][0] == "manifesto":
                angle = math.atan2(ty - py, tx - px) * 0.9
                sx, sy = px + ring * math.cos(angle), py + ring * math.sin(angle)
            else:
                sx, sy = px + half, py
            dx = (tx - sx) * 0.55
            parts.append(
                f'<path d="M{num(sx)} {num(sy)}C{num(sx + dx)} {num(sy)} {num(tx - dx)} '
                f'{num(ty)} {num(tx)} {num(ty)}" fill="none" '
                f'stroke="{"url(#chain)" if heavy else EDGE}" '
                f'stroke-width="{num(g["chain"] if heavy else g["edge"])}" '
                'stroke-linecap="round"/>'
            )
    size = g["node"]
    for key, (kind, d, _) in NODES.items():
        x, y = pos[key]
        color = spectrum_at(COLOR_AT[(kind, d)])
        if kind == "manifesto":
            parts.append(
                f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(ring - g["ring"] / 2)}" '
                f'fill="{BG}" stroke="{color}" stroke-width="{num(g["ring"])}"/>'
            )
            continue
        parts.append(
            f'<rect x="{num(x - half)}" y="{num(y - half)}" width="{num(size)}" '
            f'height="{num(size)}" rx="{num(size * 0.24 if kind == "requirement" else 0)}" '
            f'fill="{color}"/>'
        )
        if kind == "requirement":  # two lines of text, as on the logo's cards
            for dy, length in ((-0.16, 0.44), (0.08, 0.31)):
                parts.append(
                    f'<rect x="{num(x - half + size * 0.27)}" y="{num(y + dy * size)}" '
                    f'width="{num(size * length)}" height="{num(size * 0.1)}" fill="{BG}"/>'
                )
    return parts


def card() -> str:
    parts = [logo(LEFT, 68, 88)]
    lead, width = text(700, "The Missing ", LEFT, 318, 64, INK)
    why, _ = text(700, "Why", LEFT + width, 318, 64, STOPS[0][1], SLANT)
    rest, _ = text(700, "in Your Specification", LEFT, 394.8, 64, INK)
    parts += [lead, why, rest]
    parts += graph()

    # The spectrum under the graph runs from why to how.
    x0, x1 = GRAPH["x0"] - 30, GRAPH["x1"] + 22
    parts.append(
        f'<rect x="{num(x0)}" y="{BASELINE - 43}" width="{num(x1 - x0)}" height="6" rx="3" '
        'fill="url(#axis)"/>'
    )
    parts.append(text(650, "why", x0, BASELINE, 24, STOPS[0][1], SLANT)[0])
    parts.append(text(650, "how", x1, BASELINE, 24, STOPS[-1][1], SLANT, "end")[0])

    # The repository on GitHub and its license.
    mark = 30
    parts.append(
        f'<path fill="{INK}" transform="translate({LEFT} {num(BASELINE - mark * 0.82)}) '
        f'scale({num(mark / 16)})" d="{GITHUB_MARK}"/>'
    )
    repo, width = text(650, "jejay/specspec", LEFT + mark + 14, BASELINE, 24, INK)
    pill_x = LEFT + mark + 14 + width + 28
    label, label_width = text(650, "MIT License", pill_x + 16, BASELINE, 24, MUTED)
    parts += [
        repo,
        f'<rect x="{num(pill_x)}" y="{num(BASELINE - 24.5)}" width="{num(label_width + 32)}" '
        f'height="34.8" rx="17.4" fill="none" stroke="{FAINT}" stroke-width="2"/>',
        label,
    ]

    title = "specspec: The Missing Why in Your Specification"
    desc = (
        "The specspec logo above the headline The Missing Why in Your Specification, with "
        "Why in italics. Beside it, a small graph without text runs from a circle on the "
        "left, labeled why, through rounded cards to squares on the right, labeled how; "
        "heavier lines trace one square back through its cards to the circle. At the "
        "bottom: the GitHub mark, jejay/specspec and MIT License."
    )
    defs = gradient("chain", GRAPH["x0"] - 24, GRAPH["x1"] + 20) + gradient("axis", x0, x1)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">\n'
        f'<title id="title">{html.escape(title)}</title>\n'
        f'<desc id="desc">{html.escape(desc)}</desc>\n'
        "<!-- Generated by tools/social_preview.py; edit the script, not this file. -->\n"
        f"<defs>{defs}</defs>\n"
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{BG}"/>\n' + "\n".join(parts) + "\n</svg>\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=ROOT / "branding")
    args = parser.parse_args()
    if not MANROPE.exists():
        parser.error(f"Manrope not found at {MANROPE}")
    args.out.mkdir(parents=True, exist_ok=True)
    svg = args.out / "social-preview.svg"
    svg.write_text(card(), encoding="utf-8", newline="\n")
    print(svg)
    resvg = shutil.which("resvg")
    if resvg is None:
        print("resvg is not on PATH; render the PNG with: resvg --skip-system-fonts SVG PNG")
        return
    png = svg.with_suffix(".png")
    subprocess.run([resvg, "--skip-system-fonts", str(svg), str(png)], check=True)
    print(png)


if __name__ == "__main__":
    main()
