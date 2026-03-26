"""Tests for pbi_cli.utils.platform."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from pbi_cli.utils.platform import (
    _workspace_candidates,
    binary_name,
    detect_platform,
    discover_pbi_port,
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


# ---------------------------------------------------------------------------
# discover_pbi_port tests
# ---------------------------------------------------------------------------


def test_discover_pbi_port_no_pbi(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Returns None when Power BI Desktop workspace dir doesn't exist."""
    with (
        patch("pbi_cli.utils.platform.platform.system", return_value="Windows"),
        patch("pbi_cli.utils.platform.Path.home", return_value=tmp_path / "nohome"),
    ):
        monkeypatch.setenv("LOCALAPPDATA", "/nonexistent/path")
        assert discover_pbi_port() is None


def test_discover_pbi_port_non_windows() -> None:
    """Returns None on non-Windows platforms."""
    with patch("pbi_cli.utils.platform.platform.system", return_value="Darwin"):
        assert discover_pbi_port() is None


def test_discover_pbi_port_reads_port_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Reads port from msmdsrv.port.txt (MSI install path)."""
    ws_dir = tmp_path / "Microsoft" / "Power BI Desktop" / "AnalysisServicesWorkspaces"
    data_dir = ws_dir / "AnalysisServicesWorkspace_abc" / "Data"
    data_dir.mkdir(parents=True)
    (data_dir / "msmdsrv.port.txt").write_text("62547", encoding="utf-8")

    with (
        patch("pbi_cli.utils.platform.platform.system", return_value="Windows"),
        patch("pbi_cli.utils.platform.Path.home", return_value=tmp_path / "nohome"),
    ):
        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
        assert discover_pbi_port() == 62547


def test_discover_pbi_port_picks_newest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """When multiple workspaces exist, picks the most recently modified."""
    import time

    ws_dir = tmp_path / "Microsoft" / "Power BI Desktop" / "AnalysisServicesWorkspaces"

    d1 = ws_dir / "AnalysisServicesWorkspace_old" / "Data"
    d1.mkdir(parents=True)
    (d1 / "msmdsrv.port.txt").write_text("11111", encoding="utf-8")

    time.sleep(0.05)

    d2 = ws_dir / "AnalysisServicesWorkspace_new" / "Data"
    d2.mkdir(parents=True)
    (d2 / "msmdsrv.port.txt").write_text("22222", encoding="utf-8")

    with (
        patch("pbi_cli.utils.platform.platform.system", return_value="Windows"),
        patch("pbi_cli.utils.platform.Path.home", return_value=tmp_path / "nohome"),
    ):
        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
        assert discover_pbi_port() == 22222


def test_discover_pbi_port_corrupt_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Returns None when port file contains non-numeric content."""
    ws_dir = tmp_path / "Microsoft" / "Power BI Desktop" / "AnalysisServicesWorkspaces"
    data_dir = ws_dir / "AnalysisServicesWorkspace_bad" / "Data"
    data_dir.mkdir(parents=True)
    (data_dir / "msmdsrv.port.txt").write_text("not-a-number", encoding="utf-8")

    with (
        patch("pbi_cli.utils.platform.platform.system", return_value="Windows"),
        patch("pbi_cli.utils.platform.Path.home", return_value=tmp_path / "nohome"),
    ):
        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
        assert discover_pbi_port() is None


def test_discover_pbi_port_empty_workspace_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Returns None when workspace dir exists but has no port files."""
    ws_dir = tmp_path / "Microsoft" / "Power BI Desktop" / "AnalysisServicesWorkspaces"
    ws_dir.mkdir(parents=True)

    with (
        patch("pbi_cli.utils.platform.platform.system", return_value="Windows"),
        patch("pbi_cli.utils.platform.Path.home", return_value=tmp_path / "nohome"),
    ):
        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
        assert discover_pbi_port() is None


def test_discover_pbi_port_store_version(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Reads port from Microsoft Store installation path (UTF-16 LE)."""
    store_ws = tmp_path / "Microsoft" / "Power BI Desktop Store App" / "AnalysisServicesWorkspaces"
    data_dir = store_ws / "AnalysisServicesWorkspace_xyz" / "Data"
    data_dir.mkdir(parents=True)
    # Store version writes UTF-16 LE without BOM
    (data_dir / "msmdsrv.port.txt").write_bytes("57426".encode("utf-16-le"))

    with (
        patch("pbi_cli.utils.platform.platform.system", return_value="Windows"),
        patch("pbi_cli.utils.platform.Path.home", return_value=tmp_path),
    ):
        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "nolocal"))
        assert discover_pbi_port() == 57426


def test_discover_pbi_port_store_preferred_over_stale_msi(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When both MSI and Store paths exist, picks the newest port file."""
    import time

    # Older MSI workspace
    msi_ws = tmp_path / "local" / "Microsoft" / "Power BI Desktop" / "AnalysisServicesWorkspaces"
    msi_data = msi_ws / "AnalysisServicesWorkspace_old" / "Data"
    msi_data.mkdir(parents=True)
    (msi_data / "msmdsrv.port.txt").write_text("11111", encoding="utf-8")

    time.sleep(0.05)

    # Newer Store workspace
    home = tmp_path / "home"
    store_ws = home / "Microsoft" / "Power BI Desktop Store App" / "AnalysisServicesWorkspaces"
    store_data = store_ws / "AnalysisServicesWorkspace_new" / "Data"
    store_data.mkdir(parents=True)
    (store_data / "msmdsrv.port.txt").write_text("22222", encoding="utf-8")

    with (
        patch("pbi_cli.utils.platform.platform.system", return_value="Windows"),
        patch("pbi_cli.utils.platform.Path.home", return_value=home),
    ):
        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))
        assert discover_pbi_port() == 22222


def test_workspace_candidates_includes_both_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """_workspace_candidates returns both MSI and Store paths."""
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))
    home = tmp_path / "home"
    with patch("pbi_cli.utils.platform.Path.home", return_value=home):
        candidates = _workspace_candidates()
    assert len(candidates) == 2
    assert "Power BI Desktop" in str(candidates[0])
    assert "Power BI Desktop Store App" in str(candidates[1])
