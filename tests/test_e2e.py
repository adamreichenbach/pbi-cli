"""End-to-end tests requiring the real Power BI MCP binary.

These tests are skipped in CI unless a binary is available.
Run with: pytest -m e2e
"""

from __future__ import annotations

import subprocess
import sys

import pytest


pytestmark = pytest.mark.e2e


def _pbi(*args: str) -> subprocess.CompletedProcess[str]:
    """Run a pbi command via subprocess."""
    return subprocess.run(
        [sys.executable, "-m", "pbi_cli", *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


@pytest.fixture(autouse=True)
def _skip_if_no_binary() -> None:
    """Skip all e2e tests if the binary is not available."""
    result = _pbi("--json", "setup", "--info")
    if "not found" in result.stdout:
        pytest.skip("Power BI MCP binary not available")


def test_version() -> None:
    result = _pbi("--version")
    assert result.returncode == 0
    assert "pbi-cli" in result.stdout


def test_help() -> None:
    result = _pbi("--help")
    assert result.returncode == 0
    assert "pbi-cli" in result.stdout


def test_setup_info() -> None:
    result = _pbi("--json", "setup", "--info")
    assert result.returncode == 0
