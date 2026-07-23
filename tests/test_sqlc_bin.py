import subprocess
import sys
from pathlib import Path

import pytest

sqlc_bin = pytest.importorskip("sqlc_bin", reason="sqlc-bin is not installed")

needs_binary = pytest.mark.skipif(
    not Path(sqlc_bin.sqlc_path()).exists(),
    reason="sqlc binary not bundled (source checkout; install a built wheel first)",
)


@needs_binary
def test_sqlc_version_runs():
    result = subprocess.run(
        [sqlc_bin.sqlc_path(), "version"], capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0
    assert result.stdout.strip().startswith("v")


@needs_binary
def test_python_m_entry_point():
    result = subprocess.run(
        [sys.executable, "-m", "sqlc_bin", "version"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    assert result.stdout.strip().startswith("v")
