"""Draw the README figures in docs/images as light and dark SVGs.

The figures are self-contained: text is outlined from the brand's Manrope font
(and a monospace font for file references), so GitHub and PyPI show the same
lettering without loading fonts. Run with any Python that has fontTools:

    python tools/readme_figures.py
    python tools/readme_figures.py --manrope PATH/Manrope[wght].ttf --mono PATH/DejaVuSansMono.ttf

By default Manrope comes from the sibling specspec-branding workspace's final
brand kit. Colors follow the selected Spectrum flow identity; node shapes follow
the graph editor (circle manifesto, rounded requirement, square implementation).
"""

from __future__ import annotations

import argparse
import html
import math
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from fontTools.pens.basePen import BasePen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]
MANROPE = ROOT.parent / "specspec-branding" / "final" / "fonts" / "Manrope[wght].ttf"
MONO_CANDIDATES = [
    Path("C:/Windows/Fonts/DejaVuSansMono.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
    Path("/usr/share/fonts/TTF/DejaVuSansMono.ttf"),
    Path("/Library/Fonts/DejaVuSansMono.ttf"),
]

THEMES = {
    "light": dict(
        bg="#F3F5F5",
        ink="#29354D",
        muted="#596575",
        faint="#8A95A5",
        node="#FFFFFF",
        line="#C3CCD7",
        shade="#E2E7EE",
        shade_line="#AEB8C5",
        stops=[
            (0, "#8C4FC2"),
            (0.24, "#3C78D6"),
            (0.45, "#18A6AC"),
            (0.64, "#6BAA3D"),
            (0.83, "#D59624"),
            (1, "#D9564E"),
        ],
        added="#1E8A66",
        deleted="#C2474A",
    ),
    "dark": dict(
        bg="#18202B",
        ink="#ECF1FA",
        muted="#B8C4D4",
        faint="#7D8A9C",
        node="#263142",
        line="#465568",
        shade="#1F2836",
        shade_line="#5A6A80",
        stops=[
            (0, "#AE89E2"),
            (0.24, "#7BA4EF"),
            (0.45, "#5ECBD2"),
            (0.64, "#98C86F"),
            (0.83, "#E5BA58"),
            (1, "#F28F82"),
        ],
        added="#5CCB9F",
        deleted="#EE8A8A",
    ),
}


# outlined text ----------------------------------------------------------------


def num(value: float) -> str:
    text = f"{value:.1f}".rstrip("0").rstrip(".")
    return "0" if text in {"-0", ""} else text


def short(value: float) -> str:
    text = num(value)
    if text.startswith("0."):
        return text[1:]
    if text.startswith("-0."):
        return "-" + text[2:]
    return text


class RelativePathPen(BasePen):
    """Compact path data: relative commands on a 0.1 px grid without rounding drift."""

    def __init__(self, glyphs=None):
        super().__init__(glyphs)
        self.commands: list[str] = []
        self.current = (0.0, 0.0)
        self.start = (0.0, 0.0)

    def _relative(self, point):
        x, y = round(point[0], 1), round(point[1], 1)
        return (x, y), (x - self.current[0], y - self.current[1])

    def _emit(self, command, *deltas):
        self.commands.append(command + " ".join(map(short, deltas)).replace(" -", "-"))

    def _moveTo(self, pt):
        end, delta = self._relative(pt)
        self._emit("m", *delta)
        self.current = self.start = end

    def _lineTo(self, pt):
        end, delta = self._relative(pt)
        self._emit("l", *delta)
        self.current = end

    def _qCurveToOne(self, pt1, pt2):
        _, control = self._relative(pt1)
        end, delta = self._relative(pt2)
        self._emit("q", *control, *delta)
        self.current = end

    def _curveToOne(self, pt1, pt2, pt3):
        _, first = self._relative(pt1)
        _, second = self._relative(pt2)
        end, delta = self._relative(pt3)
        self._emit("c", *first, *second, *delta)
        self.current = end

    def _closePath(self):
        self.commands.append("z")
        self.current = self.start


class Face:
    """One font instance with advance widths and GPOS pair kerning."""

    def __init__(self, path: Path, weight: float | None = None):
        font = TTFont(path)
        if weight is not None and "fvar" in font:
            font = instantiateVariableFont(font, {"wght": weight})
        self.glyphs = font.getGlyphSet()
        self.cmap = font.getBestCmap()
        self.upm = font["head"].unitsPerEm
        self.pairs: dict[tuple[str, str], int] = {}
        self.classes: list[tuple[set[str], dict, dict, list]] = []
        if "GPOS" in font:
            self._read_kerning(font["GPOS"].table)

    def _read_kerning(self, table) -> None:
        indices = [
            index
            for record in table.FeatureList.FeatureRecord
            if record.FeatureTag == "kern"
            for index in record.Feature.LookupListIndex
        ]
        for index in dict.fromkeys(indices):
            lookup = table.LookupList.Lookup[index]
            for sub in lookup.SubTable:
                if lookup.LookupType == 9:
                    if sub.ExtensionLookupType != 2:
                        continue
                    sub = sub.ExtSubTable
                elif lookup.LookupType != 2:
                    continue
                if sub.Format == 1:
                    for first, pair_set in zip(sub.Coverage.glyphs, sub.PairSet, strict=True):
                        for record in pair_set.PairValueRecord:
                            value = getattr(record.Value1, "XAdvance", 0) if record.Value1 else 0
                            self.pairs.setdefault((first, record.SecondGlyph), value)
                elif sub.Format == 2:
                    self.classes.append(
                        (
                            set(sub.Coverage.glyphs),
                            sub.ClassDef1.classDefs if sub.ClassDef1 else {},
                            sub.ClassDef2.classDefs if sub.ClassDef2 else {},
                            sub.Class1Record,
                        )
                    )

    def glyph(self, char: str) -> str:
        name = self.cmap.get(ord(char))
        if name is None:
            raise ValueError(f"missing glyph for {char!r}")
        return name

    def kern(self, left: str, right: str) -> int:
        if (left, right) in self.pairs:
            return self.pairs[(left, right)]
        for coverage, first, second, records in self.classes:
            if left in coverage:
                value = records[first.get(left, 0)].Class2Record[second.get(right, 0)].Value1
                return getattr(value, "XAdvance", 0) if value else 0
        return 0

    def _advances(self, text: str, size: float):
        scale = size / self.upm
        x, previous = 0.0, None
        for char in text:
            name = self.glyph(char)
            if previous is not None:
                x += self.kern(previous, name) * scale
            yield name, x
            x += self.glyphs[name].width * scale
            previous = name
        yield None, x

    def width(self, text: str, size: float) -> float:
        return list(self._advances(text, size))[-1][1]

    def path(self, text: str, x: float, baseline: float, size: float) -> str:
        scale = size / self.upm
        pen = RelativePathPen(self.glyphs)
        for name, offset in self._advances(text, size):
            if name is not None:
                transform = (scale, 0, 0, -scale, x + offset, baseline)
                self.glyphs[name].draw(TransformPen(pen, transform))
        return "".join(pen.commands)

    def _greedy(self, text: str, size: float, width: float) -> list[str]:
        lines: list[str] = []
        current = ""
        for word in text.split():
            candidate = f"{current} {word}".strip()
            if current and self.width(candidate, size) > width:
                lines.append(current)
                current = word
            else:
                current = candidate
        return lines + [current] if current else lines

    def wrap(self, text: str, size: float, width: float) -> list[str]:
        """Keep the greedy line count, but balance the lines."""
        lines = self._greedy(text, size, width)
        low, high, best = 0.0, width, lines
        while len(lines) > 1 and high - low > 0.5:
            middle = (low + high) / 2
            candidate = self._greedy(text, size, middle)
            if len(candidate) <= len(lines) and all(
                self.width(line, size) <= middle for line in candidate
            ):
                best, high = candidate, middle
            else:
                low = middle
        return best


@lru_cache(maxsize=8)
def face(path: str, weight: float | None = None) -> Face:
    return Face(Path(path), weight)


# drawing ------------------------------------------------------------------------


def mix(a: str, b: str, t: float) -> str:
    ca = [int(a[i : i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i : i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ca, cb, strict=True))


@dataclass
class Canvas:
    width: int
    height: int
    theme: dict
    title: str
    desc: str
    fonts: dict
    x0: float = 32
    x1: float = 934
    parts: list[str] = field(default_factory=list)

    def spectrum_at(self, x: float) -> str:
        """The brand spectrum color at horizontal position x."""
        stops = self.theme["stops"]
        t = min(1.0, max(0.0, (x - self.x0) / (self.x1 - self.x0)))
        for (o1, c1), (o2, c2) in zip(stops, stops[1:], strict=False):
            if t <= o2:
                return mix(c1, c2, (t - o1) / (o2 - o1))
        return stops[-1][1]

    def add(self, svg: str) -> None:
        self.parts.append(svg)

    def text(self, value, x, y, size, fill, weight="body", anchor="start") -> float:
        font = self.fonts[weight]
        width = font.width(value, size)
        x -= {"start": 0, "middle": width / 2, "end": width}[anchor]
        self.add(f'<path fill="{fill}" d="{font.path(value, x, y, size)}"/>')
        return width

    def wrap(self, value: str, size: float, width: float) -> list[str]:
        return self.fonts["title"].wrap(value, size, width)

    def svg(self) -> str:
        stops = "".join(
            f'<stop offset="{num(o)}" stop-color="{c}"/>' for o, c in self.theme["stops"]
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" '
            f'height="{self.height}" viewBox="0 0 {self.width} {self.height}" role="img" '
            f'aria-labelledby="title desc">\n'
            f'<title id="title">{html.escape(self.title)}</title>\n'
            f'<desc id="desc">{html.escape(self.desc)}</desc>\n'
            "<!-- Generated by tools/readme_figures.py; edit the script, not this file. -->\n"
            f'<defs><linearGradient id="spectrum" gradientUnits="userSpaceOnUse" '
            f'x1="{num(self.x0)}" y1="0" x2="{num(self.x1)}" y2="0">{stops}'
            "</linearGradient></defs>\n"
            f'<rect width="{self.width}" height="{self.height}" rx="18" '
            f'fill="{self.theme["bg"]}"/>\n' + "\n".join(self.parts) + "\n</svg>\n"
        )


TITLE = 16
LEADING = 20.5
LABEL = 12
PAD = 16


@dataclass
class Node:
    kind: str  # manifesto | requirement | implementation
    title: str
    x: float
    y: float  # vertical centre
    w: float = 0
    source: str = ""
    r: float = 0
    ghost: bool = False
    badge: str = ""  # A or D, as the graph editor marks Git changes
    size: float = TITLE
    rows: list[str] = field(default_factory=list)
    h: float = 0

    @property
    def top(self) -> float:
        return self.y - self.h / 2


def fit(c: Canvas, node: Node) -> Node:
    if node.kind != "manifesto":
        reserve = 26 if node.badge else 0
        node.rows = c.wrap(node.title, node.size, node.w - 2 * PAD - reserve)
        node.h = 63 + (len(node.rows) - 1) * LEADING
    return node


def draw(c: Canvas, node: Node) -> None:
    t = c.theme
    ink = t["faint"] if node.ghost else t["ink"]
    muted = t["faint"] if node.ghost else t["muted"]
    if node.kind == "manifesto":
        c.add(
            f'<circle cx="{num(node.x)}" cy="{num(node.y)}" r="{num(node.r - 3)}" '
            f'fill="{t["node"]}" stroke="{c.spectrum_at(node.x - node.r)}" stroke-width="6"/>'
        )
        leading = node.size * 1.3
        rows = c.wrap(node.title, node.size, node.r * 1.62)
        top = node.y - (len(rows) - 1) * leading / 2 - 4
        for index, row in enumerate(rows):
            c.text(row, node.x, top + index * leading, node.size, ink, "title", "middle")
        below = top + (len(rows) - 1) * leading + 23
        c.text("manifesto", node.x, below, LABEL, muted, "body", "middle")
        return
    stroke = t["line"] if node.ghost else c.spectrum_at(node.x + node.w / 2)
    dash = ' stroke-dasharray="6 5"' if node.ghost else ""
    c.add(
        f'<rect x="{num(node.x)}" y="{num(node.top)}" width="{num(node.w)}" '
        f'height="{num(node.h)}" rx="{14 if node.kind == "requirement" else 0}" '
        f'fill="{t["bg"] if node.ghost else t["node"]}" stroke="{stroke}" '
        f'stroke-width="1.6"{dash}/>'
    )
    baseline = node.top + 27
    for index, row in enumerate(node.rows):
        c.text(row, node.x + PAD, baseline + index * LEADING, node.size, ink, "title")
    below = baseline + (len(node.rows) - 1) * LEADING + 8
    if node.source:
        c.text(node.source, node.x + PAD, below + 13.5, 12, muted, "mono")
    else:
        c.text(node.kind, node.x + PAD, below + 12.5, LABEL, muted)
    if node.badge:
        color = t["added"] if node.badge == "A" else t["deleted"]
        bx, by = node.x + node.w - 18, node.top + 18
        c.add(
            f'<circle cx="{num(bx)}" cy="{num(by)}" r="9.5" fill="none" '
            f'stroke="{color}" stroke-width="1.7"/>'
        )
        c.text(node.badge, bx, by + 4.3, 12, color, "bold", "middle")


def link(c: Canvas, a: Node, b: Node, ghost: bool = False) -> None:
    t = c.theme
    tx, ty = (b.x - b.r if b.kind == "manifesto" else b.x) - 8, b.y
    if a.kind == "manifesto":
        angle = max(-0.8, min(0.8, math.atan2(ty - a.y, tx - a.x)))
        sx, sy = a.x + a.r * math.cos(angle), a.y + a.r * math.sin(angle)
    else:
        sx, sy = a.x + a.w, a.y
    dx = max(16.0, (tx - sx) * 0.55)
    curve = (
        f"M{num(sx)} {num(sy)}C{num(sx + dx)} {num(sy)} {num(tx - dx)} {num(ty)} "
        f"{num(tx)} {num(ty)}"
    )
    dash = ' stroke-dasharray="6 5"' if ghost else ""
    c.add(
        f'<path d="{curve}" fill="none" stroke="{t["line"] if ghost else "url(#spectrum)"}" '
        f'stroke-width="2.4" stroke-linecap="round"{dash}/>'
    )
    c.add(
        f'<path d="M{num(tx - 1)} {num(ty - 5.5)}L{num(tx + 8)} {num(ty)}'
        f'L{num(tx - 1)} {num(ty + 5.5)}Z" '
        f'fill="{t["line"] if ghost else c.spectrum_at(tx)}"/>'
    )


def rounded_polygon(points: list[tuple[float, float]], radius: float) -> str:
    out = []
    for i, (cx, cy) in enumerate(points):
        px, py = points[i - 1]
        nx, ny = points[(i + 1) % len(points)]
        din, dout = math.hypot(cx - px, cy - py), math.hypot(nx - cx, ny - cy)
        r = min(radius, din / 2, dout / 2)
        ax, ay = cx - (cx - px) / din * r, cy - (cy - py) / din * r
        bx, by = cx + (nx - cx) / dout * r, cy + (ny - cy) / dout * r
        out.append(f"{'L' if out else 'M'}{num(ax)} {num(ay)}")
        out.append(f"Q{num(cx)} {num(cy)} {num(bx)} {num(by)}")
    return "".join(out) + "Z"


# the example planning graph ----------------------------------------------------

COLUMNS = dict(manifesto=(114, 84), intention=(240, 204), choice=(490, 222), code=(758, 176))
ROWS = (78, 209, 340)


def planner(c: Canvas):
    mx, mr = COLUMNS["manifesto"]
    ix, iw = COLUMNS["intention"]
    cx, cw = COLUMNS["choice"]
    xx, xw = COLUMNS["code"]
    r1, r2, r3 = ROWS
    root = Node("manifesto", "Help a small team agree on a plan", mx, (r1 + r3) / 2, r=mr, size=15)
    n = {
        "timing": Node("requirement", "Make timing easy to read", ix, (r1 + r2) / 2 - 3, iw),
        "share": Node("requirement", "Let anyone propose changes", ix, (r2 + r3) / 2 + 3, iw),
        "timeline": Node("requirement", "Show tasks on a weekday timeline", cx, r1, cw),
        "moved": Node("requirement", "Highlight what moved since the last version", cx, r2, cw),
        "json": Node("requirement", "Keep the plan as a JSON file in the repository", cx, r3, cw),
        "draw": Node("implementation", "Draw the timeline", xx, r1, xw, "timeline.ts:12-80"),
        "mark": Node("implementation", "Mark moved dates", xx, r2, xw, "changes.ts:5-41"),
        "check": Node("implementation", "Validate plan files", xx, r3, xw, "plan.schema.json"),
    }
    for node in n.values():
        fit(c, node)
    links = [
        (root, n["timing"]),
        (root, n["share"]),
        (n["timing"], n["timeline"]),
        (n["timing"], n["moved"]),
        (n["share"], n["moved"]),
        (n["share"], n["json"]),
        (n["timeline"], n["draw"]),
        (n["moved"], n["mark"]),
        (n["json"], n["check"]),
    ]
    return root, n, links


def draw_planner(c: Canvas, root, nodes, links) -> None:
    for a, b in links:
        link(c, a, b)
    draw(c, root)
    for node in nodes.values():
        draw(c, node)


# figures --------------------------------------------------------------------------


def spectrum(theme: dict, fonts: dict) -> str:
    c = Canvas(
        960,
        472,
        theme,
        fonts=fonts,
        title="The specification spectrum",
        desc="A specspec graph for a small planning app. A circular manifesto states the goal: "
        "help a small team agree on a plan. Two requirements state what the team wants: make "
        "timing easy to read, and let anyone propose changes. Three requirements to their "
        "right are choices that serve them; the middle one, highlight what moved since the "
        "last version, serves both. Three square implementation nodes explain the code and "
        "link to source lines. A color band underneath runs from intention on the left to "
        "conclusion on the right.",
    )
    draw_planner(c, *planner(c))
    y = 416
    c.add(f'<rect x="32" y="{y}" width="902" height="6" rx="3" fill="url(#spectrum)"/>')
    w = c.text("intention", 32, y + 34, 15, theme["ink"], "title")
    c.text("what you want and why", 32 + w + 9, y + 34, 15, theme["muted"])
    tail = c.text("how it gets done", 934, y + 34, 15, theme["muted"], anchor="end")
    c.text("conclusion", 934 - tail - 9, y + 34, 15, theme["ink"], "title", "end")
    return c.svg()


def revise(theme: dict, fonts: dict) -> str:
    c = Canvas(
        960,
        330,
        theme,
        fonts=fonts,
        title="Replacing a conclusion",
        desc="The intention make timing easy to read stays unchanged. Its earlier conclusion, "
        "show tasks on a weekday timeline, and the implementation node below it are drawn "
        "dashed and marked D for deleted. A new conclusion, list milestones by date, and its "
        "implementation are marked A for added. Git keeps the deleted branch in its history.",
    )
    root = Node("manifesto", "Help a small team agree on a plan", 96, 160, r=64, size=12.5)
    timing = fit(c, Node("requirement", "Make timing easy to read", 214, 160, 202))
    old = fit(
        c,
        Node(
            "requirement", "Show tasks on a weekday timeline", 474, 84, 220, ghost=True, badge="D"
        ),
    )
    old_code = fit(
        c,
        Node(
            "implementation",
            "Draw the timeline",
            752,
            84,
            182,
            "timeline.ts:12-80",
            ghost=True,
            badge="D",
        ),
    )
    new = fit(c, Node("requirement", "List milestones by date", 474, 236, 220, badge="A"))
    new_code = fit(
        c,
        Node(
            "implementation",
            "Draw the milestone list",
            752,
            236,
            182,
            "milestones.ts:3-36",
            badge="A",
        ),
    )
    link(c, root, timing)
    link(c, timing, old, ghost=True)
    link(c, old, old_code, ghost=True)
    link(c, timing, new)
    link(c, new, new_code)
    for node in (root, timing, old, old_code, new, new_code):
        draw(c, node)
    centre = timing.x + timing.w / 2
    c.text("unchanged", centre, timing.top + timing.h + 24, 12.5, theme["muted"], anchor="middle")
    x, y = 474, 304
    x += c.text("D", x, y, 12.5, theme["deleted"], "bold") + 6
    x += c.text("deleted, kept in Git history", x, y, 12.5, theme["muted"]) + 22
    x += c.text("A", x, y, 12.5, theme["added"], "bold") + 6
    c.text("added", x, y, 12.5, theme["muted"])
    return c.svg()


def direct(theme: dict, fonts: dict) -> str:
    c = Canvas(
        960,
        478,
        theme,
        fonts=fonts,
        title="How far you direct",
        desc="The same planning graph with a shaded area for the decisions the owner made. In "
        "the top branch the owner decided down to the code. In the middle branch the owner "
        "chose the approach and the agent wrote the code. In the bottom branch the owner "
        "stated only the intention; the agent chose the JSON file and wrote the validation. "
        "Everything outside the shaded area was concluded by the agent and can be reviewed "
        "and replaced.",
    )
    root, nodes, links = planner(c)
    ix, iw = COLUMNS["intention"]
    cx, cw = COLUMNS["choice"]
    xx, xw = COLUMNS["code"]
    between_12 = (ROWS[0] + ROWS[1]) / 2 + 2
    between_23 = (ROWS[1] + ROWS[2]) / 2 + 2
    after_intention = (ix + iw + cx) / 2
    after_choice = (cx + cw + xx) / 2
    right = xx + xw + 14
    area = [
        (16, 18),
        (right, 18),
        (right, between_12),
        (after_choice, between_12),
        (after_choice, between_23),
        (after_intention, between_23),
        (after_intention, 404),
        (16, 404),
    ]
    c.add(
        f'<path d="{rounded_polygon(area, 14)}" fill="{theme["shade"]}" '
        f'stroke="{theme["shade_line"]}" stroke-width="1.4" stroke-dasharray="7 6"/>'
    )
    draw_planner(c, root, nodes, links)
    y = 448
    c.add(
        f'<rect x="34" y="{y - 13}" width="22" height="16" rx="5" fill="{theme["shade"]}" '
        f'stroke="{theme["shade_line"]}" stroke-width="1.2" stroke-dasharray="4 3"/>'
    )
    x = 66 + c.text("you decided", 66, y, 14, theme["ink"], "title") + 28
    c.add(
        f'<rect x="{num(x)}" y="{y - 13}" width="22" height="16" rx="5" fill="{theme["bg"]}" '
        f'stroke="{theme["shade_line"]}" stroke-width="1.2"/>'
    )
    c.text("your agent concluded", x + 32, y, 14, theme["ink"], "title")
    return c.svg()


FIGURES = {"spectrum": spectrum, "revise": revise, "direct": direct}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manrope", type=Path, default=MANROPE)
    parser.add_argument("--mono", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=ROOT / "docs" / "images")
    args = parser.parse_args()
    mono = args.mono or next((path for path in MONO_CANDIDATES if path.exists()), None)
    if not args.manrope.exists() or mono is None:
        parser.error("pass --manrope and --mono font files")
    fonts = {
        "title": face(str(args.manrope), 650),
        "body": face(str(args.manrope), 500),
        "bold": face(str(args.manrope), 700),
        "mono": face(str(mono)),
    }
    args.out.mkdir(parents=True, exist_ok=True)
    for name, build in FIGURES.items():
        for theme_name, theme in THEMES.items():
            target = args.out / f"{name}-{theme_name}.svg"
            target.write_text(build(theme, fonts), encoding="utf-8", newline="\n")
            print(target.relative_to(ROOT) if target.is_relative_to(ROOT) else target)


if __name__ == "__main__":
    main()
