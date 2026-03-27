"""Platform detection and Power BI Desktop port discovery."""

from __future__ import annotations

import platform
from pathlib import Path


def _workspace_candidates() -> list[Path]:
    """Return candidate AnalysisServicesWorkspaces directories.

    Power BI Desktop (MSI) uses:
      %LOCALAPPDATA%/Microsoft/Power BI Desktop/AnalysisServicesWorkspaces/

    Power BI Desktop (Microsoft Store) uses:
      %USERPROFILE%/Microsoft/Power BI Desktop Store App/AnalysisServicesWorkspaces/
    """
    import os

    dirs: list[Path] = []

    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        dirs.append(
            Path(local_app_data) / "Microsoft" / "Power BI Desktop" / "AnalysisServicesWorkspaces"
        )

    user_profile = Path.home()
    dirs.append(
        user_profile / "Microsoft" / "Power BI Desktop Store App" / "AnalysisServicesWorkspaces"
    )

    return dirs


def discover_pbi_port() -> int | None:
    """Find the port of a running Power BI Desktop instance.

    Checks both MSI and Microsoft Store installation paths.
    Returns the port number, or None if Power BI Desktop is not running.
    """
    if platform.system() != "Windows":
        return None

    port_files: list[Path] = []
    for workspaces_dir in _workspace_candidates():
        if not workspaces_dir.exists():
            continue
        port_files.extend(workspaces_dir.glob("*/Data/msmdsrv.port.txt"))

    if not port_files:
        return None

    # Pick the most recently modified (latest instance)
    port_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    try:
        raw = port_files[0].read_bytes()
        # Power BI writes UTF-16 LE (no BOM): b'5\x007\x004\x002\x006\x00'
        # Try UTF-16-LE first, fall back to UTF-8 for compatibility.
        try:
            port_text = raw.decode("utf-16-le").strip("\x00").strip()
        except UnicodeDecodeError:
            port_text = raw.decode("utf-8").strip()
        return int(port_text)
    except (ValueError, OSError):
        return None
