"""Bounded API-7 frames; requests retain the ordinary application authority."""

import json

from .application import request
from .editor import MAX_REQUEST_BYTES
from .model import Diagnostic, SpecError
from .output import envelope, json_text


def decode_request(raw):
    try:
        if len(raw) > MAX_REQUEST_BYTES:
            raise ValueError("Request exceeds the 16 MiB limit.")
        return json.loads(raw)
    except (ValueError, UnicodeError) as error:
        raise SpecError([Diagnostic("API", f"Invalid application JSON: {error}")], 2) from error


def serve(root, reader, writer):
    """One bounded line in, one flushed ordinary envelope out; EOF closes the channel."""

    def send(result=None, diagnostics=(), ok=False):
        writer.write((json_text(envelope(result, diagnostics, ok)) + "\n").encode("utf-8"))
        writer.flush()

    while True:
        raw = reader.readline(MAX_REQUEST_BYTES + 2)
        if not raw:
            return 0
        if not raw.endswith(b"\n") or len(raw) > MAX_REQUEST_BYTES + 1:
            send(
                diagnostics=[Diagnostic("API", "Application frame needs a bounded complete line.")]
            )
            return 2  # Framing loss terminates; never guess the next request boundary.
        try:
            result, diagnostics = request(root, decode_request(raw[:-1]))
            send(result, diagnostics, True)
        except SpecError as error:
            send(diagnostics=error.diagnostics)
        except (OSError, UnicodeError) as error:
            send(diagnostics=[Diagnostic("IO", str(error))])
