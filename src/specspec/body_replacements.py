"""Disjoint original-body replacements with source-mapped newline tolerance."""

from itertools import pairwise

from .model import MAX_FILE_BYTES, Diagnostic, SpecError
from .node_text import stored_text
from .replacement_matching import Matcher

MAX_REPLACEMENTS = 1024


def fail(message, *, path=None, exit_code=2):
    raise SpecError([Diagnostic("REPLACE", message, path)], exit_code)


def input_bytes(pairs):
    """Validate explicit literal pairs and count both sides of their input."""
    if not isinstance(pairs, (list, tuple)) or not 1 <= len(pairs) <= MAX_REPLACEMENTS:
        fail("Supply 1-1024 exact OLD/NEW replacement pairs.")
    total = 0
    for index, pair in enumerate(pairs, 1):
        if (
            not isinstance(pair, (list, tuple))
            or len(pair) != 2
            or any(not isinstance(text, str) for text in pair)
        ):
            fail(f"Replacement {index} must contain OLD and NEW text.")
        if not pair[0]:
            fail(f"Replacement {index} OLD text must be nonempty.")
        for text in pair:
            size = len(text.encode("utf8"))
            if size > MAX_FILE_BYTES:
                fail(f"Replacement {index} text exceeds 1 MiB.")
            total += size
    return total


def replace_body(body, pairs, *, path=None, eol=None):
    """Resolve every span on the original before constructing the bounded result."""
    input_bytes(pairs)
    spans = []
    size = len(body.encode("utf8"))
    matcher = Matcher(body, path=path)
    for index, (old, new) in enumerate(pairs, 1):
        matches = matcher.find(old)
        if not matches:
            fail(
                f"Replacement {index} OLD text was not found in the current body; reread it.",
                path=path,
                exit_code=1,
            )
        if len(matches) > 1:
            fail(
                f"Replacement {index} OLD text occurs more than once; supply unique context.",
                path=path,
                exit_code=1,
            )
        start, end = matches[0]
        spans.append((start, end, index, new))
        size += len(new.encode("utf8")) - len(body[start:end].encode("utf8"))
    spans.sort(key=lambda span: span[0])
    for earlier, later in pairwise(spans):
        if later[0] < earlier[1]:
            fail(
                f"Replacement {later[2]} overlaps replacement {earlier[2]}; use disjoint context.",
                path=path,
                exit_code=1,
            )
    # Newline adaptation can shrink CRLF by at most half. Bound construction
    # before joining, then assess actual target-style bytes before serialization.
    if size > MAX_FILE_BYTES * (2 if eol is not None else 1):
        fail("Replacement result exceeds the 1 MiB node limit.", path=path, exit_code=1)
    parts, cursor = [], 0
    for start, end, _, new in spans:
        parts.extend((body[cursor:start], new))
        cursor = end
    parts.append(body[cursor:])
    result = "".join(parts)
    if eol is not None:
        result = stored_text(result, eol)
    if len(result.encode("utf8")) > MAX_FILE_BYTES:
        fail("Replacement result exceeds the 1 MiB node limit.", path=path, exit_code=1)
    return result
