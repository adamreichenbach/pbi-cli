"""Close and reopen Power BI Desktop to sync PBIR file changes.

Power BI Desktop does not auto-detect PBIR file changes on disk.
When pbi-cli writes to report JSON files while Desktop has the .pbip
open, Desktop's in-memory state is stale and will overwrite changes
on save.

This module solves the problem by:
  1. Finding the Desktop window that has the target .pbip open
  2. Extracting the exe path and .pbip path from the process command line
  3. Closing Desktop without saving (WM_CLOSE + dismiss save dialog)
  4. Waiting for the process to exit
  5. Relaunching Desktop with the same .pbip file

Requires pywin32.  Falls back to a manual instruction message if
pywin32 is not installed or Desktop is not running.
"""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import Any


def sync_desktop(pbip_hint: str | Path | None = None) -> dict[str, Any]:
    """Close and reopen Power BI Desktop so it loads current PBIR files.

    *pbip_hint* is an optional path to narrow the search to a specific
    .pbip file. If None, closes the first Desktop window found.

    Returns a dict with ``status``, ``method``, and ``message``.
    """
    try:
        import win32con  # type: ignore[import-untyped]  # noqa: F401
        import win32gui  # type: ignore[import-untyped]  # noqa: F401
    except ImportError:
        return {
            "status": "manual",
            "method": "instructions",
            "message": (
                "pywin32 is not installed. Install with: pip install pywin32\n"
                "Then pbi-cli can auto-reopen Desktop after report changes.\n"
                "For now, close Desktop (don't save) and reopen the .pbip file."
            ),
        }

    info = _find_desktop_process(pbip_hint)
    if info is None:
        return {
            "status": "skipped",
            "method": "pywin32",
            "message": "Power BI Desktop is not running. No sync needed.",
        }

    hwnd = info["hwnd"]
    pbip_path = info["pbip_path"]
    pid = info["pid"]

    # Close Desktop without saving
    close_result = _close_without_saving(hwnd, pid)
    if close_result is not None:
        return close_result

    # Reopen the .pbip file
    return _reopen_pbip(pbip_path)


def _find_desktop_process(
    pbip_hint: str | Path | None,
) -> dict[str, Any] | None:
    """Find the PBI Desktop window, its PID, and the .pbip file it has open."""
    import win32gui  # type: ignore[import-untyped]
    import win32process  # type: ignore[import-untyped]

    # Normalise the hint for matching
    hint_stem = None
    if pbip_hint is not None:
        hint_stem = Path(pbip_hint).stem.lower()

    matches: list[dict[str, Any]] = []

    def callback(hwnd: int, _: Any) -> bool:
        if not win32gui.IsWindowVisible(hwnd):
            return True
        title = win32gui.GetWindowText(hwnd)
        if not title:
            return True

        # PBI Desktop titles look like "HR_Analysis" or
        # "HR_Analysis - Power BI Desktop"
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        # Get process command line to find exe + pbip path
        cmd_info = _get_process_info(pid)
        if cmd_info is None:
            return True

        exe_path = cmd_info.get("exe", "")
        if "pbidesktop" not in exe_path.lower():
            return True

        pbip_path = cmd_info.get("pbip")
        if pbip_path is None:
            return True

        # If we have a hint, match against it
        if hint_stem is not None:
            if hint_stem not in Path(pbip_path).stem.lower():
                return True

        matches.append({
            "hwnd": hwnd,
            "pid": pid,
            "title": title,
            "exe_path": exe_path,
            "pbip_path": pbip_path,
        })
        return True

    try:
        win32gui.EnumWindows(callback, None)
    except Exception:
        pass

    return matches[0] if matches else None


def _get_process_info(pid: int) -> dict[str, str] | None:
    """Get exe path and .pbip file from a process command line via wmic."""
    try:
        out = subprocess.check_output(
            [
                "wmic", "process", "where", f"ProcessId={pid}",
                "get", "ExecutablePath,CommandLine", "/format:list",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
    except Exception:
        return None

    result: dict[str, str] = {}
    for line in out.strip().split("\n"):
        line = line.strip()
        if line.startswith("ExecutablePath="):
            result["exe"] = line[15:]
        elif line.startswith("CommandLine="):
            cmd = line[12:]
            # Extract .pbip path from command line
            for part in cmd.split('"'):
                part = part.strip()
                if part.lower().endswith(".pbip"):
                    result["pbip"] = part
                    break

    return result if "exe" in result else None


def _close_without_saving(hwnd: int, pid: int) -> dict[str, Any] | None:
    """Close Desktop via WM_CLOSE and dismiss the save dialog.

    Returns an error dict on failure, or None on success.
    """
    import win32con  # type: ignore[import-untyped]
    import win32gui  # type: ignore[import-untyped]

    # Send WM_CLOSE to trigger the save dialog
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    time.sleep(2)

    # Look for the save dialog window and dismiss it
    _dismiss_save_dialog()

    # Wait for process to exit (up to 15 seconds)
    for _ in range(30):
        if not _process_alive(pid):
            return None
        time.sleep(0.5)

    return {
        "status": "error",
        "method": "pywin32",
        "message": (
            "Power BI Desktop did not close within 15 seconds. "
            "Please close it manually, then reopen the .pbip file."
        ),
    }


def _reopen_pbip(pbip_path: str) -> dict[str, Any]:
    """Launch the .pbip file with the system default handler (PBI Desktop)."""
    try:
        # Use os.startfile on Windows -- opens with the registered handler
        os.startfile(pbip_path)  # type: ignore[attr-defined]
        return {
            "status": "success",
            "method": "pywin32",
            "message": f"Power BI Desktop reopening: {Path(pbip_path).name}",
            "file": pbip_path,
        }
    except Exception as e:
        return {
            "status": "error",
            "method": "pywin32",
            "message": f"Failed to reopen: {e}. Open manually: {pbip_path}",
        }


def _dismiss_save_dialog() -> None:
    """Find and dismiss the 'Do you want to save?' dialog.

    After WM_CLOSE, Power BI Desktop may show a save dialog titled
    'Microsoft Power BI Desktop'.  We activate it and send Tab+Enter
    to select 'Don't Save'.
    """
    import win32gui  # type: ignore[import-untyped]

    # Find the save dialog by scanning for its title
    dialog_titles = []

    def callback(hwnd: int, _: Any) -> bool:
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title == "Microsoft Power BI Desktop":
                dialog_titles.append(title)
        return True

    try:
        win32gui.EnumWindows(callback, None)
    except Exception:
        pass

    if not dialog_titles:
        # No save dialog -- Desktop may have closed without prompting
        return

    try:
        shell = _get_wscript_shell()
        activated = shell.AppActivate("Microsoft Power BI Desktop")
        if activated:
            time.sleep(0.3)
            shell.SendKeys("{TAB}{ENTER}")
    except Exception:
        pass


def _process_alive(pid: int) -> bool:
    """Check if a process is still running."""
    try:
        out = subprocess.check_output(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=3,
        )
        return str(pid) in out
    except Exception:
        return False


def _get_wscript_shell() -> Any:
    """Get a WScript.Shell COM object for SendKeys."""
    import win32com.client  # type: ignore[import-untyped]

    return win32com.client.Dispatch("WScript.Shell")
