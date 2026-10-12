"""Clone the maintained Gantt history outside the SpecSpec development worktree.

This is a fixture/workspace helper, not a production command or schema converter.
Existing destinations are never reused, reset or deleted.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]


def default_destination() -> Path:
    return Path.home() / "Projects/specspec-examples/gantt"


def clone_history(source: Path, destination: Path) -> Path:
    source = source.resolve()
    requested = destination.expanduser()
    destination = requested.resolve()
    development_root = Path(
        subprocess.run(
            ["git", "-C", str(source), "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    ).resolve()
    if destination == development_root or development_root in destination.parents:
        raise ValueError("Choose a destination outside the SpecSpec development worktree.")
    if requested.exists() or requested.is_symlink():
        raise ValueError(
            f"Destination already exists; preserve it and choose another: {destination}"
        )
    # Claim a new empty directory atomically: Git itself accepts existing empty
    # destinations, which would otherwise defeat the refusal if another creator
    # wins after the preceding check. Keep failed/partial clones for inspection.
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        destination.mkdir()
    except FileExistsError as error:
        raise ValueError(
            f"Destination already exists; preserve it and choose another: {destination}"
        ) from error
    subprocess.run(
        [
            "git",
            "clone",
            "--quiet",
            "--config",
            "core.autocrlf=false",
            "--branch",
            "main",
            str(source / "history/gantt.bundle"),
            str(destination),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "destination",
        nargs="?",
        type=Path,
        default=default_destination(),
        help="New external folder.",
    )
    args = parser.parse_args()
    try:
        destination = clone_history(SOURCE, args.destination)
    except ValueError as error:
        parser.exit(1, f"{error}\n")
    except subprocess.CalledProcessError as error:
        parser.exit(1, f"Git checkout failed: {error.stderr.strip()}\n")
    print(destination)


if __name__ == "__main__":
    main()
