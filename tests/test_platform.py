"""Tests for pbi_cli.utils.platform."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from pbi_cli.utils.platform import (
    _workspace_candidates,
    discover_pbi_port,
)


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
