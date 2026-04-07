"""Shared helpers for CLI commands to reduce boilerplate."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

import click

from pbi_cli.core.errors import TomError
from pbi_cli.core.output import format_result, print_error

if TYPE_CHECKING:
    from pbi_cli.main import PbiContext

# Statuses that indicate a write operation (triggers Desktop sync)
_WRITE_STATUSES = frozenset(
    {
        "created",
        "deleted",
        "updated",
        "applied",
        "added",
        "cleared",
        "bound",
        "removed",
        "set",
    }
)


def run_command(
    ctx: PbiContext,
    fn: Callable[..., Any],
    **kwargs: Any,
) -> Any:
    """Execute a backend function with standard error handling.

    Calls ``fn(**kwargs)`` and formats the output based on the
    ``--json`` flag.

    If the current Click context has a ``report_path`` key (set by
    report-layer command groups), write operations automatically
    trigger a safe Desktop sync: save Desktop's work, re-apply our
    PBIR changes, and reopen.
    """
    try:
        result = fn(**kwargs)
        format_result(result, ctx.json_output)
    except Exception as e:
        print_error(str(e))
        if not ctx.repl_mode:
            raise SystemExit(1)
        raise TomError(fn.__name__, str(e))

    # Auto-sync Desktop for report-layer write operations
    if _is_report_write(result):
        definition_path = kwargs.get("definition_path")
        _try_desktop_sync(definition_path)

    return result


def _is_report_write(result: Any) -> bool:
    """Check if the result indicates a report-layer write that should trigger sync."""
    if not isinstance(result, dict):
        return False
    status = result.get("status", "")
    if status not in _WRITE_STATUSES:
        return False

    # Only sync if we're inside a report-layer command group
    click_ctx = click.get_current_context(silent=True)
    if click_ctx is None:
        return False

    # Walk up to the group to find report_path; also check for --no-sync flag
    parent = click_ctx.parent
    while parent is not None:
        obj = parent.obj
        if isinstance(obj, dict) and "report_path" in obj:
            if obj.get("no_sync", False):
                return False
            return True
        parent = parent.parent
    return False


def _try_desktop_sync(definition_path: Any = None) -> None:
    """Attempt Desktop sync, silently ignore failures."""
    try:
        from pbi_cli.utils.desktop_sync import sync_desktop

        # Find report_path hint from the Click context chain
        report_path = None
        click_ctx = click.get_current_context(silent=True)
        parent = click_ctx.parent if click_ctx else None
        while parent is not None:
            obj = parent.obj
            if isinstance(obj, dict) and "report_path" in obj:
                report_path = obj["report_path"]
                break
            parent = parent.parent

        # Convert definition_path to string for sync
        defn_str = str(definition_path) if definition_path is not None else None

        result = sync_desktop(report_path, definition_path=defn_str)
        status = result.get("status", "")
        msg = result.get("message", "")
        if status == "success":
            print_error(f"  Desktop: {msg}")
        elif status == "manual":
            print_error(f"  {msg}")
    except Exception:
        pass  # sync is best-effort, never block the command


def build_definition(
    required: dict[str, Any],
    optional: dict[str, Any],
) -> dict[str, Any]:
    """Build a definition dict, including only non-None optional values."""
    definition = dict(required)
    for key, value in optional.items():
        if value is not None:
            definition[key] = value
    return definition
