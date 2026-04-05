"""ASCII banner displayed on bare `pbi` invocation."""

from __future__ import annotations

import os
import sys

# Power BI yellow — closest ANSI equivalent to #FFBE00
_YELLOW = "\033[93m"
_DIM = "\033[2m"
_RESET = "\033[0m"

_ART = r"""
 ██████╗ ██████╗ ██╗      ██████╗██╗     ██╗
 ██╔══██╗██╔══██╗██║     ██╔════╝██║     ██║
 ██████╔╝██████╔╝██║     ██║     ██║     ██║
 ██╔═══╝ ██╔══██╗██║     ██║     ██║     ██║
 ██║     ██████╔╝███████╗╚██████╗███████╗██║
 ╚═╝     ╚═════╝ ╚══════╝ ╚═════╝╚══════╝╚═╝
"""

_TAGLINE = "Power BI CLI  ·  Direct .NET interop  ·  Built for Claude Code"


def _color_supported() -> bool:
    """Return True if the terminal supports ANSI color codes."""
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return sys.stdout.isatty()


def _can_encode(text: str) -> bool:
    """Return True if stdout can encode the given text."""
    enc = getattr(sys.stdout, "encoding", "utf-8") or "utf-8"
    try:
        text.encode(enc)
        return True
    except (UnicodeEncodeError, LookupError):
        return False


def print_banner(version: str) -> None:
    """Print the PBI-CLI ASCII banner with version and quick-start hints."""
    use_color = _color_supported()
    use_art = _can_encode(_ART)

    if use_art:
        art = f"{_YELLOW}{_ART}{_RESET}" if use_color else _ART
    else:
        # Fallback for terminals without Unicode support (e.g. legacy cmd.exe)
        art = "\n  PBI-CLI\n"

    tagline = f"  {_DIM}{_TAGLINE}{_RESET}" if use_color else f"  {_TAGLINE}"
    ver_line = f"  {_DIM}v{version}{_RESET}" if use_color else f"  v{version}"

    print(art)
    print(tagline)
    print(ver_line)
    print()
    print("  Quick start:")
    print("    pipx install pbi-cli-tool   # already done")
    print("    pbi-cli skills install      # register Claude Code skills")
    print("    pbi connect                 # auto-detect Power BI Desktop")
    print()
    print("  Run 'pbi --help' for the full command list.")
    print()
