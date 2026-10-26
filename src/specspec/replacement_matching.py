"""Source-mapped newline equivalence; Markdown structure is never flattened globally."""

from __future__ import annotations

from array import array
from bisect import bisect_left
from dataclasses import dataclass
from functools import lru_cache

from .model import Diagnostic, SpecError

MAX_MARKDOWN_LINES = 32768
MAX_MARKDOWN_TOKENS = 131072
MAX_MATCH_NESTING = 20
MAX_MATCH_CANDIDATES = 8192
MAX_MATCH_WORK = 64 * 1024 * 1024


def line_endings(text):
    return text.replace("\r\n", "\n").replace("\r", "\n")


@dataclass
class Budget:
    path: str | None = None
    tokens: int = 0
    candidates: int = 0
    work: int = 0
    depth: int = 0

    def fail(self):
        raise SpecError(
            [
                Diagnostic(
                    "REPLACE",
                    "Replacement matching exceeds its analysis budget; use whole-body input.",
                    self.path,
                )
            ],
            2,
        )

    def spend(self, amount):
        self.work += amount
        if self.work > MAX_MATCH_WORK:
            self.fail()

    def token(self):
        self.tokens += 1
        if self.tokens > MAX_MARKDOWN_TOKENS:
            self.fail()


@lru_cache(maxsize=1)
def markdown_parser():
    # Ordinary writes, help and API startup do not import the Markdown dependency.
    from markdown_it import MarkdownIt
    from markdown_it.parser_block import ParserBlock
    from markdown_it.parser_inline import ParserInline
    from markdown_it.rules_block.state_block import StateBlock
    from markdown_it.rules_inline import newline, text
    from markdown_it.rules_inline.state_inline import StateInline

    class BlockState(StateBlock):
        def push(self, *args):
            self.env["budget"].token()
            return super().push(*args)

    class BlockParser(ParserBlock):
        def tokenize(self, state, start, end):
            if state.level >= MAX_MATCH_NESTING:
                state.env["budget"].fail()
            return super().tokenize(state, start, end)

        def parse(self, src, md, env, tokens):
            state = BlockState(src, md, env, tokens)
            self.tokenize(state, state.line, state.lineMax)
            return state.tokens

    class InlineState(StateInline):
        def push(self, *args):
            self.env["budget"].token()
            return super().push(*args)

        def pushPending(self):
            self.env["budget"].token()
            return super().pushPending()

    class InlineParser(ParserInline):
        def skipToken(self, state):
            if state.level >= MAX_MATCH_NESTING:
                state.env["budget"].fail()
            return super().skipToken(state)

        def tokenize(self, state):
            if state.level >= MAX_MATCH_NESTING:
                state.env["budget"].fail()
            return super().tokenize(state)

        def parse(self, src, md, env, tokens):
            budget = env["budget"]
            budget.depth += 1
            if budget.depth > MAX_MATCH_NESTING:
                budget.fail()
            state = InlineState(src, md, env, tokens)
            root = env.get("root") is None
            if root:
                env["root"] = state
            try:
                self.tokenize(state)
                for rule in self.ruler2.getRules(""):
                    rule(state)
                return state.tokens
            finally:
                budget.depth -= 1
                if root:
                    env["root"] = None

    def prose_text(state, silent):
        start = state.pos
        result = text(state, silent)
        if result and not silent and state is state.env.get("root"):
            state.env["budget"].spend(state.pos - start)
            mask = state.env["mask"]
            for index in range(start, state.pos):
                if state.src[index] == " ":
                    mask[index] = 1
        return result

    def prose_newline(state, silent):
        start = state.pos
        result = newline(state, silent)
        if (
            result
            and not silent
            and state is state.env.get("root")
            and state.tokens[-1].type == "softbreak"
        ):
            state.env["mask"][start] = 1
            state.env["soft"].append(start)
        return result

    parser = MarkdownIt("commonmark")
    parser.block = BlockParser()
    parser.inline = InlineParser()
    parser.configure("commonmark").enable("table")
    parser.inline.ruler.at("text", prose_text)
    parser.inline.ruler.at("newline", prose_newline)
    return parser


@dataclass
class Prose:
    text: str
    mask: bytearray
    soft: list[int]


def prose_view(source, budget):
    budget.spend(len(source))
    if source.count("\n") + 1 > MAX_MARKDOWN_LINES:
        budget.fail()
    parser = markdown_parser()
    tokens = []
    parser.block.parse(source.replace("\0", "\ufffd"), parser, {"budget": budget}, tokens)
    starts = [0, *(index + 1 for index, char in enumerate(source) if char == "\n")]
    starts.append(len(source))
    mask, soft = bytearray(len(source)), []
    for opening, inline in zip(tokens, tokens[1:], strict=False):
        if opening.type != "paragraph_open" or inline.type != "inline" or not inline.map:
            continue
        first, last = inline.map
        begin, end = starts[first], starts[last]
        offset = source.find(inline.content, begin, end)
        # A contiguous source correspondence must cover all mapped paragraph lines.
        # Container prefixes, removed indentation or NUL normalization can prevent it.
        if (
            not inline.content
            or offset < 0
            or "\n" in source[begin:offset]
            or source[offset + len(inline.content) : end].strip()
            or inline.content.count("\n") != last - first - 1
        ):
            continue
        env = {"budget": budget, "mask": bytearray(len(inline.content)), "soft": []}
        parser.inline.parse(inline.content, parser, env, [])
        mask[offset : offset + len(inline.content)] = env["mask"]
        soft.extend(offset + index for index in env["soft"])
    soft.sort()
    parts, cursor = [], 0
    for index in soft:
        parts.extend((source[cursor:index], " "))
        cursor = index + 1
    parts.append(source[cursor:])
    return Prose("".join(parts), mask, soft)


class Matcher:
    def __init__(self, body, *, path=None):
        self.text = line_endings(body)
        self.budget = Budget(path)
        self.prose = None
        self.offsets = None
        if "\r" in body:
            offsets = array("I")
            index = 0
            while index < len(body):
                offsets.append(index)
                index += 2 if body[index : index + 2] == "\r\n" else 1
            offsets.append(len(body))
            self.offsets = offsets

    def original(self, start, end):
        if self.offsets is None:
            return start, end
        return self.offsets[start], self.offsets[end]

    def find(self, old):
        pattern = line_endings(old)
        if len(pattern) > len(self.text):
            return []
        found = set()
        start = self.text.find(pattern)
        while start >= 0:
            found.add(self.original(start, start + len(pattern)))
            if len(found) == 2:
                return sorted(found)
            start = self.text.find(pattern, start + 1)
        # Both comparison views preserve normalized character counts: a full-body
        # exact match cannot acquire a distinct alternative span through wrapping.
        if found and len(pattern) == len(self.text):
            return sorted(found)
        if not (" " in pattern or "\n" in pattern):
            return sorted(found)
        if "\n" not in pattern and "\n" not in self.text:
            return sorted(found)
        if self.prose is None:
            self.prose = prose_view(self.text, self.budget)
        if not self.prose.soft and "\n" not in pattern:
            return sorted(found)
        wanted = prose_view(pattern, self.budget)
        if not wanted.soft and not self.prose.soft:
            return sorted(found)
        start = self.prose.text.find(wanted.text)
        while start >= 0:
            self.budget.candidates += 1
            if self.budget.candidates > MAX_MATCH_CANDIDATES:
                self.budget.fail()
            end = start + len(wanted.text)
            span = self.original(start, end)
            if span not in found and self.compatible(pattern, wanted, start, end):
                found.add(span)
                if len(found) == 2:
                    return sorted(found)
            start = self.prose.text.find(wanted.text, start + 1)
        return sorted(found)

    def compatible(self, pattern, wanted, start, end):
        for index in wanted.soft:
            self.budget.spend(1)
            if self.text[start + index] != "\n" and not self.prose.mask[start + index]:
                return False
        first = bisect_left(self.prose.soft, start)
        last = bisect_left(self.prose.soft, end)
        for cursor in range(first, last):
            self.budget.spend(1)
            index = self.prose.soft[cursor] - start
            if pattern[index] != "\n" and not wanted.mask[index]:
                return False
        return True
