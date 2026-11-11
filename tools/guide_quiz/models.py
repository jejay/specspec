"""Ask a Claude model through the local Claude Code command line, with a fixed context.

Every call gets one system prompt, no tools and no project files. The command inherits
nothing from a surrounding Claude Code session: such a session exports its own reasoning
effort, which would otherwise apply to the quiz. The call runs in an empty folder with a
neutral name, because the command shows the model its working directory.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

FRAME = (
    "You are a coding agent working in a software project for its owner. "
    "The project's AGENTS.md follows; it is your instruction for working in this project.\n\n"
    "<AGENTS.md>\n{guide}\n</AGENTS.md>\n"
)

# Passed explicitly per model. Haiku 4.5 takes no effort level.
EFFORT = {
    "claude-haiku-5-5": "medium",
    "claude-sonnet-5-5": "high",
    "claude-opus-5-5": "high",
}
WAITS = (5, 20, 60, 120)


@dataclass
class Answer:
    """One reply, or the reason there is none."""

    text: str | None = None
    error: str | None = None
    cost: float = 0.0
    tokens: dict[str, int] = field(default_factory=dict)
    milliseconds: int | None = None
    served: list[str] = field(default_factory=list)


def frame(guide: str) -> str:
    """The system prompt that presents a guide version as the project's AGENTS.md."""
    return FRAME.format(guide=guide.rstrip("\n"))


def working_directory() -> Path:
    path = Path(tempfile.gettempdir()) / "frontdesk"
    path.mkdir(exist_ok=True)
    return path


def system_file(text: str) -> Path:
    """Keep each distinct system prompt in one file; the command reads it from there."""
    folder = Path(tempfile.gettempdir()) / "guide-quiz-prompts"
    folder.mkdir(exist_ok=True)
    path = folder / (hashlib.sha256(text.encode("utf-8")).hexdigest()[:20] + ".txt")
    if not path.exists():
        path.write_text(text, encoding="utf-8", newline="\n")
    return path


def environment() -> dict[str, str]:
    return {key: value for key, value in os.environ.items() if not key.upper().startswith("CLAUDE")}


def command(model: str, system_path: Path, effort: str | None) -> list[str]:
    executable = shutil.which("claude")
    if executable is None:
        raise RuntimeError("The claude command is not on PATH. Install Claude Code and sign in.")
    arguments = [
        executable,
        "-p",
        "--model",
        model,
        "--system-prompt-file",
        str(system_path),
        "--tools",
        "",
        "--safe-mode",
        "--strict-mcp-config",
        "--no-session-persistence",
        "--disable-slash-commands",
        "--output-format",
        "json",
    ]
    return arguments + ["--effort", effort] if effort else arguments


def read(output: str) -> Answer:
    """Turn the command's JSON result into an answer."""
    data = json.loads(output)
    if data.get("is_error") or not data.get("result"):
        status = data.get("api_error_status")
        return Answer(error=f"status {status}: {str(data.get('result'))[:200]}")
    usage = data.get("usage") or {}
    return Answer(
        text=data["result"],
        cost=data.get("total_cost_usd") or 0.0,
        tokens={
            "in": sum(
                usage.get(name, 0)
                for name in (
                    "input_tokens",
                    "cache_creation_input_tokens",
                    "cache_read_input_tokens",
                )
            ),
            "out": usage.get("output_tokens", 0),
            "thinking": (usage.get("output_tokens_details") or {}).get("thinking_tokens", 0),
        },
        milliseconds=data.get("duration_ms"),
        served=sorted(data.get("modelUsage") or {}),
    )


def ask(
    model: str,
    system: str,
    prompt: str,
    *,
    timeout: int = 1500,
    attempts: int = 4,
    run=subprocess.run,
    wait=time.sleep,
) -> Answer:
    """Send one prompt and return the reply; a failed call is repeated after a pause."""
    arguments = command(model, system_file(system), EFFORT.get(model))
    answer = Answer(error="not asked")
    for attempt in range(attempts):
        try:
            done = run(
                arguments,
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=working_directory(),
                env=environment(),
                timeout=timeout,
            )
            answer = read(done.stdout)
        except subprocess.TimeoutExpired:
            answer = Answer(error="timeout")
        except (ValueError, KeyError, OSError) as problem:
            answer = Answer(error=f"{type(problem).__name__}: {problem}"[:300])
        if answer.text is not None:
            return answer
        if attempt + 1 < attempts:
            wait(WAITS[min(attempt, len(WAITS) - 1)])
    return answer
