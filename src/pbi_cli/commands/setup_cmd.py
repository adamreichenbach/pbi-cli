"""pbi setup: download and manage the Power BI MCP binary."""

from __future__ import annotations

import click

from pbi_cli.core.binary_manager import (
    check_for_updates,
    download_and_extract,
    get_binary_info,
)
from pbi_cli.core.output import print_error, print_info, print_json, print_key_value, print_success
from pbi_cli.main import PbiContext, pass_context


@click.command()
@click.option("--version", "target_version", default=None, help="Specific version to install.")
@click.option("--check", is_flag=True, default=False, help="Check for updates without installing.")
@click.option("--info", is_flag=True, default=False, help="Show info about the current binary.")
@pass_context
def setup(ctx: PbiContext, target_version: str | None, check: bool, info: bool) -> None:
    """Download and set up the Power BI MCP server binary.

    Run this once after installing pbi-cli to download the binary.
    """
    if info:
        _show_info(ctx.json_output)
        return

    if check:
        _check_updates(ctx.json_output)
        return

    _install(target_version, ctx.json_output)


def _show_info(json_output: bool) -> None:
    """Show binary info."""
    info = get_binary_info()
    if json_output:
        print_json(info)
    else:
        print_key_value("Power BI MCP Binary", info)


def _check_updates(json_output: bool) -> None:
    """Check for available updates."""
    try:
        installed, latest, update_available = check_for_updates()
        result = {
            "installed_version": installed,
            "latest_version": latest,
            "update_available": update_available,
        }
        if json_output:
            print_json(result)
        elif update_available:
            print_info(f"Update available: {installed} -> {latest}")
            print_info("Run 'pbi setup' to update.")
        else:
            print_success(f"Up to date: v{installed}")
    except Exception as e:
        print_error(f"Failed to check for updates: {e}")
        raise SystemExit(1)


def _install(version: str | None, json_output: bool) -> None:
    """Download and install the binary."""
    try:
        bin_path = download_and_extract(version)
        if json_output:
            print_json({"binary_path": str(bin_path), "status": "installed"})
    except Exception as e:
        print_error(f"Setup failed: {e}")
        raise SystemExit(1)
