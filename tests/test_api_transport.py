import io
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import pytest

from specspec import api_transport
from specspec.output import json_text
from specspec.workspace import update_node


def frames(*values):
    return io.BytesIO(b"".join((json_text(v) + "\n").encode() for v in values))


def test_stream_keeps_normal_envelopes_and_continues_after_rejected_requests(workspace):
    root, _ = workspace
    output = io.BytesIO()
    values = [
        {"api_version": 7, "op": "read"},
        {"api_version": 5, "op": "read"},
        {"api_version": 7, "op": "execute"},
        {"api_version": 7, "op": "annotations"},
    ]
    assert api_transport.serve(root, frames(*values), output) == 0
    results = [json.loads(line) for line in output.getvalue().splitlines()]
    assert [r["api_version"] for r in results] == [7] * 4
    assert [r["ok"] for r in results] == [True, False, False, True]
    assert results[-1]["result"] == {"shots": []}


def test_each_stream_frame_reads_current_text_and_validation(workspace):
    root, manifesto = workspace
    request = {"api_version": 7, "op": "read"}
    source = frames(request, request, request)
    read = source.readline
    calls = 0

    class Reader:
        def readline(self, budget):
            nonlocal calls
            calls += 1
            if calls == 2:
                update_node(root, manifesto, body="# Current 🦉\n")
            if calls == 3:
                path = next((root / "_specspec").glob("*.md"))
                path.write_text(
                    path.read_text(encoding="utf-8").replace("parents:", "broken:"),
                    encoding="utf-8",
                )
            return read(budget)

    output = io.BytesIO()
    assert api_transport.serve(root, Reader(), output) == 0
    first, second, third = [json.loads(line) for line in output.getvalue().splitlines()]
    assert first["ok"] and second["ok"]
    assert "Current 🦉" in json_text(second)
    assert third["result"]["snapshot"]["valid"] is False
    assert third["diagnostics"]


@pytest.mark.parametrize("raw", [b"{}", b"x" * 100 + b"\n"])
def test_framing_loss_ends_bounded_channel_without_guessing_a_request(raw, workspace, monkeypatch):
    monkeypatch.setattr(api_transport, "MAX_REQUEST_BYTES", 64)
    output = io.BytesIO()
    assert api_transport.serve(workspace[0], io.BytesIO(raw), output) == 2
    result = json.loads(output.getvalue())
    assert result["ok"] is False and result["diagnostics"][0]["code"] == "API"


def test_malformed_json_frame_is_an_error_and_next_valid_frame_still_runs(workspace):
    output = io.BytesIO()
    valid = frames({"api_version": 7, "op": "annotations"}).getvalue()
    assert api_transport.serve(workspace[0], io.BytesIO(b"not json\n" + valid), output) == 0
    first, second = [json.loads(line) for line in output.getvalue().splitlines()]
    assert first["ok"] is False and second["ok"] is True


def test_real_api_channel_flushes_before_eof_and_observes_next_request(workspace):
    root, manifesto = workspace
    process = subprocess.Popen(
        [sys.executable, "-m", "specspec", "--root", str(root), "api", "--stream"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    executor = ThreadPoolExecutor(max_workers=1)
    try:
        raw = (json_text({"api_version": 7, "op": "read"}) + "\n").encode()
        process.stdin.write(raw)
        process.stdin.flush()
        assert json.loads(executor.submit(process.stdout.readline).result(timeout=20))["ok"]
        update_node(root, manifesto, body="# Latest\n")
        process.stdin.write(raw)
        process.stdin.flush()
        assert "Latest" in json_text(
            json.loads(executor.submit(process.stdout.readline).result(timeout=20))
        )
        process.stdin.close()
        assert process.wait(timeout=20) == 0
        assert process.stderr.read() == b""
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=20)
        executor.shutdown()
