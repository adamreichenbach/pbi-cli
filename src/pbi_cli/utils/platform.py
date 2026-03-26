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


def find_vscode_extension_binary() -> Path | None:
    """Look for the binary in the VS Code extension install directory.

    This is the fallback resolution path when the user has the VS Code
    extension installed but hasn't run 'pbi setup'.
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
