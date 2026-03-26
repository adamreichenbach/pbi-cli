"""Tests for pbi_cli.utils.platform."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from pbi_cli.utils.platform import (
    binary_name,
    detect_platform,
    ensure_executable,
    find_vscode_extension_binary,
)


def test_detect_platform_windows() -> None:
    with (
        patch("pbi_cli.utils.platform.platform.system", return_value="Windows"),
        patch("pbi_cli.utils.platform.platform.machine", return_value="AMD64"),
    ):
        assert detect_platform() == "win32-x64"


def test_detect_platform_macos_arm() -> None:
    with (
        patch("pbi_cli.utils.platform.platform.system", return_value="Darwin"),
        patch("pbi_cli.utils.platform.platform.machine", return_value="arm64"),
    ):
        assert detect_platform() == "darwin-arm64"


def test_detect_platform_linux_x64() -> None:
    with (
        patch("pbi_cli.utils.platform.platform.system", return_value="Linux"),
        patch("pbi_cli.utils.platform.platform.machine", return_value="x86_64"),
    ):
        assert detect_platform() == "linux-x64"


def test_detect_platform_unsupported() -> None:
    with (
        patch("pbi_cli.utils.platform.platform.system", return_value="FreeBSD"),
        patch("pbi_cli.utils.platform.platform.machine", return_value="sparc"),
    ):
        with pytest.raises(ValueError, match="Unsupported platform"):
            detect_platform()


def test_binary_name_windows() -> None:
    with patch("pbi_cli.utils.platform.platform.system", return_value="Windows"):
        assert binary_name() == "powerbi-modeling-mcp.exe"


def test_binary_name_unix() -> None:
    with patch("pbi_cli.utils.platform.platform.system", return_value="Linux"):
        assert binary_name() == "powerbi-modeling-mcp"


def test_binary_name_unsupported() -> None:
    with patch("pbi_cli.utils.platform.platform.system", return_value="FreeBSD"):
        with pytest.raises(ValueError, match="Unsupported OS"):
            binary_name()


def test_ensure_executable_noop_on_windows(tmp_path: Path) -> None:
    f = tmp_path / "test.exe"
    f.write_text("fake", encoding="utf-8")
    with patch("pbi_cli.utils.platform.platform.system", return_value="Windows"):
        ensure_executable(f)  # should be a no-op


def test_find_vscode_extension_binary_no_dir(tmp_path: Path) -> None:
    with patch("pbi_cli.utils.platform.Path.home", return_value=tmp_path):
        result = find_vscode_extension_binary()
        assert result is None


def test_find_vscode_extension_binary_no_match(tmp_path: Path) -> None:
    ext_dir = tmp_path / ".vscode" / "extensions"
    ext_dir.mkdir(parents=True)
    with patch("pbi_cli.utils.platform.Path.home", return_value=tmp_path):
        result = find_vscode_extension_binary()
        assert result is None


def test_find_vscode_extension_binary_found(tmp_path: Path) -> None:
    ext_name = "analysis-services.powerbi-modeling-mcp-0.4.0"
    server_dir = tmp_path / ".vscode" / "extensions" / ext_name / "server"
    server_dir.mkdir(parents=True)
    fake_bin = server_dir / "powerbi-modeling-mcp.exe"
    fake_bin.write_text("fake", encoding="utf-8")

    with (
        patch("pbi_cli.utils.platform.Path.home", return_value=tmp_path),
        patch("pbi_cli.utils.platform.binary_name", return_value="powerbi-modeling-mcp.exe"),
    ):
        result = find_vscode_extension_binary()
        assert result is not None
        assert result.name == "powerbi-modeling-mcp.exe"
