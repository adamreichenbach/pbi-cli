"""Platform and architecture detection for binary resolution."""

from __future__ import annotations

import platform
import stat
from pathlib import Path

# Maps (system, machine) to VS Marketplace target platform identifier.
PLATFORM_MAP: dict[tuple[str, str], str] = {
    ("Windows", "AMD64"): "win32-x64",
    ("Windows", "x86_64"): "win32-x64",
    ("Windows", "ARM64"): "win32-arm64",
    ("Darwin", "arm64"): "darwin-arm64",
    ("Linux", "x86_64"): "linux-x64",
    ("Linux", "aarch64"): "linux-arm64",
}

# Binary name per OS.
BINARY_NAMES: dict[str, str] = {
    "Windows": "powerbi-modeling-mcp.exe",
    "Darwin": "powerbi-modeling-mcp",
    "Linux": "powerbi-modeling-mcp",
}


def detect_platform() -> str:
    """Return the VS Marketplace target platform string for this machine.

    Raises ValueError if the platform is unsupported.
    """
    system = platform.system()
    machine = platform.machine()
    key = (system, machine)
    target = PLATFORM_MAP.get(key)
    if target is None:
        raise ValueError(
            f"Unsupported platform: {system}/{machine}. "
            f"Supported: {', '.join(f'{s}/{m}' for s, m in PLATFORM_MAP)}"
        )
    return target


def binary_name() -> str:
    """Return the expected binary filename for this OS."""
    system = platform.system()
    name = BINARY_NAMES.get(system)
    if name is None:
        raise ValueError(f"Unsupported OS: {system}")
    return name


def ensure_executable(path: Path) -> None:
    """Set executable permission on non-Windows systems."""
    if platform.system() != "Windows":
        current = path.stat().st_mode
        path.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


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
            Path(local_app_data)
            / "Microsoft"
            / "Power BI Desktop"
            / "AnalysisServicesWorkspaces"
        )

    user_profile = Path.home()
    dirs.append(
        user_profile
        / "Microsoft"
        / "Power BI Desktop Store App"
        / "AnalysisServicesWorkspaces"
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
        port_files.extend(
            workspaces_dir.glob("*/Data/msmdsrv.port.txt")
        )

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


def find_vscode_extension_binary() -> Path | None:
    """Look for the binary in the VS Code extension install directory.

    This is the fallback resolution path when the user has the VS Code
    extension installed but hasn't run 'pbi connect' or 'pbi setup'.
    """
    vscode_ext_dir = Path.home() / ".vscode" / "extensions"
    if not vscode_ext_dir.exists():
        return None

    matches = sorted(
        vscode_ext_dir.glob("analysis-services.powerbi-modeling-mcp-*/server"),
        reverse=True,
    )
    if not matches:
        return None

    server_dir = matches[0]
    bin_path = server_dir / binary_name()
    if bin_path.exists():
        return bin_path
    return None
