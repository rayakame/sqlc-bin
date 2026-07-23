"""Launcher for the sqlc binary bundled with this package."""

from __future__ import annotations

import os
import subprocess
import sys

__all__ = ["main", "sqlc_path"]


def sqlc_path() -> str:
    """Absolute path to the bundled sqlc executable."""
    name = "sqlc.exe" if os.name == "nt" else "sqlc"
    return os.path.join(os.path.dirname(__file__), "bin", name)


def main() -> int:
    binary = sqlc_path()
    if not os.path.exists(binary):
        print(
            "sqlc-bin: bundled sqlc binary not found; "
            "this usually means the package was installed from a source checkout "
            "instead of a built wheel",
            file=sys.stderr,
        )
        return 1
    argv = [binary, *sys.argv[1:]]
    if os.name == "nt":
        return subprocess.call(argv)
    os.execv(binary, argv)
