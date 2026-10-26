"""Logical node newlines, independent of Git filters and physical safety guards."""


def logical_text(text: str) -> str:
    """Normalize newline encoding only; keep whitespace and EOF termination."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


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
