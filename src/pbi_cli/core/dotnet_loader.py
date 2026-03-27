"""CLR bootstrap: load pythonnet and Microsoft Analysis Services DLLs.

Uses .NET Framework (net45) DLLs bundled in ``pbi_cli/dlls/``.
Lazy-loaded on first access so import cost is zero until needed.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_initialized = False


def _dll_dir() -> Path:
    """Return the path to the bundled DLL directory."""
    return Path(__file__).resolve().parent.parent / "dlls"


def _ensure_initialized() -> None:
    """Initialize the CLR runtime and load Analysis Services assemblies.

    Idempotent: safe to call multiple times.
    """
    global _initialized
    if _initialized:
        return

    try:
        import pythonnet
        from clr_loader import get_netfx
    except ImportError as e:
        raise ImportError(
            "pythonnet is required for direct Power BI connection.\n"
            "Install it with: pip install pythonnet"
        ) from e

    rt = get_netfx()
    pythonnet.set_runtime(rt)

    import clr  # noqa: E402 (must import after set_runtime)

    dll_path = _dll_dir()
    if not dll_path.exists():
        raise FileNotFoundError(
            f"Bundled DLL directory not found: {dll_path}\n"
            "Reinstall pbi-cli-tool: pipx install pbi-cli-tool --force"
        )

    sys.path.insert(0, str(dll_path))

    clr.AddReference("Microsoft.AnalysisServices.Tabular")
    clr.AddReference("Microsoft.AnalysisServices.AdomdClient")

    _initialized = True


def get_server_class() -> Any:
    """Return the ``Microsoft.AnalysisServices.Tabular.Server`` class."""
    _ensure_initialized()
    from Microsoft.AnalysisServices.Tabular import Server  # type: ignore[import-untyped]

    return Server


def get_adomd_connection_class() -> Any:
    """Return the ``AdomdConnection`` class."""
    _ensure_initialized()
    from Microsoft.AnalysisServices.AdomdClient import (
        AdomdConnection,  # type: ignore[import-untyped]
    )

    return AdomdConnection


def get_adomd_command_class() -> Any:
    """Return the ``AdomdCommand`` class."""
    _ensure_initialized()
    from Microsoft.AnalysisServices.AdomdClient import AdomdCommand  # type: ignore[import-untyped]

    return AdomdCommand


def get_tmdl_serializer() -> Any:
    """Return the ``TmdlSerializer`` class."""
    _ensure_initialized()
    from Microsoft.AnalysisServices.Tabular import TmdlSerializer  # type: ignore[import-untyped]

    return TmdlSerializer


def get_tom_classes(*names: str) -> tuple[Any, ...]:
    """Return one or more classes from ``Microsoft.AnalysisServices.Tabular``.

    Example::

        Measure, Table = get_tom_classes("Measure", "Table")
    """
    _ensure_initialized()
    import Microsoft.AnalysisServices.Tabular as TOM  # type: ignore[import-untyped]

    results: list[Any] = []
    for name in names:
        cls = getattr(TOM, name, None)
        if cls is None:
            raise AttributeError(
                f"Class '{name}' not found in Microsoft.AnalysisServices.Tabular"
            )
        results.append(cls)
    return tuple(results)
