"""Logical node newlines, independent of Git filters and physical safety guards."""


def logical_text(text: str) -> str:
    """Normalize newline encoding only; keep whitespace and EOF termination."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def logical_lines(text: str) -> list[str]:
    """Lines ended by LF, CRLF or CR only, as in logical node text.

    Form feeds, vertical tabs, NEL and Unicode line/paragraph separators remain
    line content: editors, grep and Git count no line break there.
    """
    lines = logical_text(text).split("\n")
    if lines[-1] == "":
        lines.pop()
    return lines


def logical_bytes(raw: bytes | None) -> bytes | None:
    """Compare UTF-8 nodes logically; unavailable/binary material stays literal."""
    if raw is None or b"\r" not in raw:
        return raw
    try:
        return logical_text(raw.decode("utf8")).encode("utf8")
    except UnicodeDecodeError:
        return raw


def document_eol(original: bytes | None) -> str:
    """The opening frontmatter delimiter supplies an existing document's style."""
    if original is not None and original.startswith(b"---\r"):
        return "\r\n" if original.startswith(b"---\r\n") else "\r"
    return "\n"


def stored_text(text: str, eol: str) -> str:
    return logical_text(text).replace("\n", eol)


def terminated_document(text: str, eol: str) -> str:
    """Add only a missing file terminator; never trim or add trailing blank lines."""
    return text if text.endswith(("\n", "\r")) else text + eol
