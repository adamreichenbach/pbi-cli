"""Binary manager: download, extract, and resolve the Power BI MCP server binary.

The binary is a .NET executable distributed as part of a VS Code extension (VSIX).
This module handles downloading the VSIX from the VS Marketplace, extracting the
server binary, and resolving the binary path for the MCP client.
"""

from __future__ import annotations

import os
import shutil
import tempfile
import zipfile
from pathlib import Path

import httpx

from pbi_cli.core.config import PBI_CLI_HOME, ensure_home_dir, load_config, save_config
from pbi_cli.core.output import print_info, print_success
from pbi_cli.utils.platform import (
    binary_name,
    detect_platform,
    ensure_executable,
    find_vscode_extension_binary,
)

EXTENSION_ID = "analysis-services.powerbi-modeling-mcp"
PUBLISHER = "analysis-services"
EXTENSION_NAME = "powerbi-modeling-mcp"

MARKETPLACE_API = "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery"
VSIX_URL_TEMPLATE = (
    "https://marketplace.visualstudio.com/_apis/public/gallery/publishers/"
    "{publisher}/vsextensions/{extension}/{version}/vspackage"
    "?targetPlatform={platform}"
)


def resolve_binary() -> Path:
    """Resolve the MCP server binary path using the priority chain.

    Priority:
    1. PBI_MCP_BINARY environment variable
    2. ~/.pbi-cli/bin/{version}/ (managed by pbi setup)
    3. VS Code extension fallback

    Raises FileNotFoundError if no binary is found.
    """
    env_path = os.environ.get("PBI_MCP_BINARY")
    if env_path:
        p = Path(env_path)
        if p.exists():
            return p
        raise FileNotFoundError(f"PBI_MCP_BINARY points to non-existent path: {env_path}")

    config = load_config()
    if config.binary_path:
        p = Path(config.binary_path)
        if p.exists():
            return p

    managed = _find_managed_binary()
    if managed:
        return managed

    vscode_bin = find_vscode_extension_binary()
    if vscode_bin:
        print_info(f"Using VS Code extension binary: {vscode_bin}")
        return vscode_bin

    raise FileNotFoundError(
        "Power BI MCP binary not found. Run 'pbi setup' to download it, "
        "or set PBI_MCP_BINARY environment variable."
    )


def _find_managed_binary() -> Path | None:
    """Look for a binary in ~/.pbi-cli/bin/."""
    bin_dir = PBI_CLI_HOME / "bin"
    if not bin_dir.exists():
        return None
    versions = sorted(bin_dir.iterdir(), reverse=True)
    for version_dir in versions:
        candidate = version_dir / binary_name()
        if candidate.exists():
            return candidate
    return None


def query_latest_version() -> str:
    """Query the VS Marketplace for the latest extension version.

    Returns the version string (e.g., '0.4.0').
    """
    payload = {
        "filters": [
            {
                "criteria": [
                    {"filterType": 7, "value": EXTENSION_ID},
                ],
                "pageNumber": 1,
                "pageSize": 1,
            }
        ],
        "flags": 914,
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json;api-version=6.1-preview.1",
    }

    with httpx.Client(timeout=30.0) as client:
        resp = client.post(MARKETPLACE_API, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    results = data.get("results", [])
    if not results:
        raise RuntimeError("No results from VS Marketplace query")

    extensions = results[0].get("extensions", [])
    if not extensions:
        raise RuntimeError(f"Extension {EXTENSION_ID} not found on VS Marketplace")

    versions = extensions[0].get("versions", [])
    if not versions:
        raise RuntimeError(f"No versions found for {EXTENSION_ID}")

    return str(versions[0]["version"])


def download_and_extract(version: str | None = None) -> Path:
    """Download the VSIX and extract the server binary.

    Args:
        version: Specific version to download. If None, queries latest.

    Returns:
        Path to the extracted binary.
    """
    if version is None:
        print_info("Querying VS Marketplace for latest version...")
        version = query_latest_version()

    target_platform = detect_platform()
    print_info(f"Downloading pbi-mcp v{version} for {target_platform}...")

    url = VSIX_URL_TEMPLATE.format(
        publisher=PUBLISHER,
        extension=EXTENSION_NAME,
        version=version,
        platform=target_platform,
    )

    dest_dir = ensure_home_dir() / "bin" / version
    dest_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        vsix_path = Path(tmp) / "extension.vsix"

        with httpx.Client(timeout=120.0, follow_redirects=True) as client:
            with client.stream("GET", url) as resp:
                resp.raise_for_status()
                total = int(resp.headers.get("content-length", 0))
                downloaded = 0
                with open(vsix_path, "wb") as f:
                    for chunk in resp.iter_bytes(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            pct = downloaded * 100 // total
                            print(f"\r  Downloading... {pct}%", end="", flush=True)
                print()

        print_info("Extracting server binary...")
        with zipfile.ZipFile(vsix_path, "r") as zf:
            server_prefix = "extension/server/"
            server_files = [n for n in zf.namelist() if n.startswith(server_prefix)]
            if not server_files:
                raise RuntimeError("No server/ directory found in VSIX package")

            for file_name in server_files:
                rel_path = file_name[len(server_prefix) :]
                if not rel_path:
                    continue
                target_path = dest_dir / rel_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(file_name) as src, open(target_path, "wb") as dst:
                    shutil.copyfileobj(src, dst)

    bin_path = dest_dir / binary_name()
    if not bin_path.exists():
        raise RuntimeError(f"Binary not found after extraction: {bin_path}")

    ensure_executable(bin_path)

    config = load_config().with_updates(
        binary_version=version,
        binary_path=str(bin_path),
    )
    save_config(config)

    print_success(f"Installed pbi-mcp v{version} at {dest_dir}")
    return bin_path


def check_for_updates() -> tuple[str, str, bool]:
    """Compare installed version with latest available.

    Returns (installed_version, latest_version, update_available).
    """
    config = load_config()
    installed = config.binary_version or "none"
    latest = query_latest_version()
    return installed, latest, installed != latest


def get_binary_info() -> dict[str, str]:
    """Return info about the currently resolved binary."""
    try:
        path = resolve_binary()
        config = load_config()
        return {
            "binary_path": str(path),
            "version": config.binary_version or "unknown",
            "platform": detect_platform(),
            "source": _binary_source(path),
        }
    except FileNotFoundError:
        return {
            "binary_path": "not found",
            "version": "none",
            "platform": detect_platform(),
            "source": "none",
        }


def _binary_source(path: Path) -> str:
    """Determine the source of a resolved binary path."""
    path_str = str(path)
    if "PBI_MCP_BINARY" in os.environ:
        return "environment variable (PBI_MCP_BINARY)"
    if ".pbi-cli" in path_str:
        return "managed (pbi setup)"
    if ".vscode" in path_str:
        return "VS Code extension (fallback)"
    return "unknown"
