"""Trigger Power BI Desktop to reload the current report.

Implements a fallback chain:
  1. pywin32 (if installed): find window, send keyboard shortcut
  2. PowerShell: use Add-Type + SendKeys via subprocess
  3. Manual: print instructions for the user

Power BI Desktop's Developer Mode auto-detects file changes in TMDL but
not in PBIR. This module bridges the gap by programmatically triggering
a reload from the CLI.
"""

from __future__ import annotations

import subprocess
import sys
from typing import Any


def reload_desktop() -> dict[str, Any]:
    """Attempt to reload the current report in Power BI Desktop.

    Tries methods in order of reliability. Returns a dict with
    ``status``, ``method``, and ``message``.
    """
    # Method 1: pywin32
    result = _try_pywin32()
    if result is not None:
        return result

    # Method 2: PowerShell
    result = _try_powershell()
    if result is not None:
        return result

    # Method 3: manual instructions
    return {
        "status": "manual",
        "method": "instructions",
        "message": (
            "Could not auto-reload Power BI Desktop. "
            "Please press Ctrl+Shift+F5 in Power BI Desktop to refresh, "
            "or close and reopen the report file."
        ),
    }


def _try_pywin32() -> dict[str, Any] | None:
    """Try to use pywin32 to send a reload shortcut to PBI Desktop."""
    try:
        import win32api
        import win32con
        import win32gui
    except ImportError:
        return None

    hwnd = _find_pbi_window_pywin32()
    if hwnd == 0:
        return {
            "status": "error",
            "method": "pywin32",
            "message": "Power BI Desktop window not found. Is it running?",
        }

    try:
        # Bring window to foreground
        win32gui.SetForegroundWindow(hwnd)

        # Send Ctrl+Shift+F5 (common refresh shortcut)
        VK_CONTROL = 0x11
        VK_SHIFT = 0x10
        VK_F5 = 0x74

        win32api.keybd_event(VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(VK_SHIFT, 0, 0, 0)
        win32api.keybd_event(VK_F5, 0, 0, 0)
        win32api.keybd_event(VK_F5, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

        return {
            "status": "success",
            "method": "pywin32",
            "message": "Sent Ctrl+Shift+F5 to Power BI Desktop.",
        }
    except Exception as e:
        return {
            "status": "error",
            "method": "pywin32",
            "message": f"Failed to send keystrokes: {e}",
        }


def _find_pbi_window_pywin32() -> int:
    """Find Power BI Desktop's main window handle via pywin32."""
    import win32gui

    result = 0

    def callback(hwnd: int, _: Any) -> bool:
        nonlocal result
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "Power BI Desktop" in title:
                result = hwnd
                return False  # Stop enumeration
        return True

    try:
        win32gui.EnumWindows(callback, None)
    except Exception:
        pass

    return result


def _try_powershell() -> dict[str, Any] | None:
    """Try to use PowerShell to activate PBI Desktop and send keystrokes."""
    if sys.platform != "win32":
        return None

    ps_script = """
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName Microsoft.VisualBasic

$pbi = Get-Process -Name "PBIDesktop" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $pbi) {
    $pbi = Get-Process -Name "PBIDesktopStore" -ErrorAction SilentlyContinue | Select-Object -First 1
}

if (-not $pbi) {
    Write-Output "NOT_FOUND"
    exit 0
}

# Activate the window
[Microsoft.VisualBasic.Interaction]::AppActivate($pbi.Id)
Start-Sleep -Milliseconds 500

# Send Ctrl+Shift+F5
[System.Windows.Forms.SendKeys]::SendWait("^+{F5}")
Write-Output "OK"
"""

    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = proc.stdout.strip()

        if output == "NOT_FOUND":
            return {
                "status": "error",
                "method": "powershell",
                "message": "Power BI Desktop process not found. Is it running?",
            }
        if output == "OK":
            return {
                "status": "success",
                "method": "powershell",
                "message": "Sent Ctrl+Shift+F5 to Power BI Desktop via PowerShell.",
            }

        return {
            "status": "error",
            "method": "powershell",
            "message": f"Unexpected output: {output}",
        }
    except FileNotFoundError:
        return None  # PowerShell not available
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "method": "powershell",
            "message": "PowerShell command timed out.",
        }
    except Exception as e:
        return {
            "status": "error",
            "method": "powershell",
            "message": f"PowerShell error: {e}",
        }
