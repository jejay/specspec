"""One hardened local Git subprocess contract for every specspec call site.

Calls never run repository-configured fsmonitor hooks or signature programs,
fetch missing objects, contact remotes, prompt, inherit request input or wait
without a deadline. Callers keep their own diagnostics and deliberate limits;
streaming object batches apply the same command and environment.
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Iterable, Iterator, Mapping
from pathlib import Path

CONFIG = ("-c", "core.fsmonitor=false", "-c", "log.showSignature=false")
TIMEOUT = 60
MAX_OUTPUT = 64 * 1024 * 1024
# Windows command lines hold 32,767 characters; keep literal pathspecs well below.
PATHSPEC_CHARS = 8 * 1024


class GitProcessError(Exception):
    """Git could not start, missed its deadline or exceeded its output budget."""


def git_environment(base: Mapping[str, str] | None = None) -> dict[str, str]:
    return {
        **(os.environ if base is None else base),
        "GIT_NO_LAZY_FETCH": "1",
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_ALLOW_PROTOCOL": "",
        "GIT_TERMINAL_PROMPT": "0",
    }


def git_command(root: Path | str, *args: str) -> list[str]:
    return ["git", "-C", str(root), *CONFIG, *args]


def run_git_process(
    root: Path | str,
    *args: str,
    input: bytes | None = None,
    timeout: float = TIMEOUT,
    max_output: int = MAX_OUTPUT,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[bytes]:
    """Run Git once; callers interpret its exit status and standard error."""
    streams = {"input": input} if input is not None else {"stdin": subprocess.DEVNULL}
    try:
        completed = subprocess.run(
            git_command(root, *args),
            capture_output=True,
            check=False,
            timeout=timeout,
            env=git_environment(env),
            **streams,
        )
    except subprocess.TimeoutExpired as error:
        raise GitProcessError(f"Git did not finish within {timeout} seconds.") from error
    except (OSError, subprocess.SubprocessError) as error:
        raise GitProcessError(str(error) or type(error).__name__) from error
    if len(completed.stdout) > max_output:
        raise GitProcessError(f"Git output exceeds its {max_output}-byte budget.")
    return completed


def pathspec_chunks(paths: Iterable[str], budget: int = PATHSPEC_CHARS) -> Iterator[list[str]]:
    """Split literal pathspecs into bounded command lines; their union is unchanged."""
    chunk: list[str] = []
    size = 0
    for path in paths:
        cost = len(path) + 3  # Separator plus possible quoting.
        if chunk and size + cost > budget:
            yield chunk
            chunk, size = [], 0
        chunk.append(path)
        size += cost
    if chunk:
        yield chunk
