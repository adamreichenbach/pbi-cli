"""Tests for pbi_cli.core.binary_manager."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from pbi_cli.core.binary_manager import (
    _binary_source,
    _find_managed_binary,
    get_binary_info,
    resolve_binary,
)


def test_resolve_binary_env_var(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_bin = tmp_path / "powerbi-modeling-mcp.exe"
    fake_bin.write_text("fake", encoding="utf-8")
    monkeypatch.setenv("PBI_MCP_BINARY", str(fake_bin))

    result = resolve_binary()
    assert result == fake_bin


def test_resolve_binary_env_var_missing_file(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PBI_MCP_BINARY", "/nonexistent/path")
    with pytest.raises(FileNotFoundError, match="non-existent"):
        resolve_binary()


def test_resolve_binary_not_found(
    tmp_config: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("PBI_MCP_BINARY", raising=False)
    with patch("pbi_cli.core.binary_manager.find_vscode_extension_binary", return_value=None):
        with pytest.raises(FileNotFoundError, match="not found"):
            resolve_binary()


def test_find_managed_binary(tmp_config: Path) -> None:
    bin_dir = tmp_config / "bin" / "0.4.0"
    bin_dir.mkdir(parents=True)
    fake_bin = bin_dir / "powerbi-modeling-mcp.exe"
    fake_bin.write_text("fake", encoding="utf-8")

    with patch("pbi_cli.core.binary_manager.PBI_CLI_HOME", tmp_config), \
         patch("pbi_cli.core.binary_manager.binary_name", return_value="powerbi-modeling-mcp.exe"):
        result = _find_managed_binary()
        assert result is not None
        assert result.name == "powerbi-modeling-mcp.exe"


def test_find_managed_binary_empty_dir(tmp_config: Path) -> None:
    bin_dir = tmp_config / "bin"
    bin_dir.mkdir(parents=True)

    with patch("pbi_cli.core.binary_manager.PBI_CLI_HOME", tmp_config):
        result = _find_managed_binary()
        assert result is None


def test_binary_source_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PBI_MCP_BINARY", "/some/path")
    result = _binary_source(Path("/some/path"))
    assert "environment variable" in result


def test_binary_source_managed() -> None:
    with patch.dict(os.environ, {}, clear=False):
        if "PBI_MCP_BINARY" in os.environ:
            del os.environ["PBI_MCP_BINARY"]
        result = _binary_source(Path("/home/user/.pbi-cli/bin/0.4.0/binary"))
        assert "managed" in result


def test_binary_source_vscode() -> None:
    with patch.dict(os.environ, {}, clear=False):
        if "PBI_MCP_BINARY" in os.environ:
            del os.environ["PBI_MCP_BINARY"]
        result = _binary_source(Path("/home/user/.vscode/extensions/ext/server/binary"))
        assert "VS Code" in result


def test_get_binary_info_not_found(tmp_config: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PBI_MCP_BINARY", raising=False)
    with patch("pbi_cli.core.binary_manager.find_vscode_extension_binary", return_value=None):
        info = get_binary_info()
        assert info["binary_path"] == "not found"
        assert info["version"] == "none"
