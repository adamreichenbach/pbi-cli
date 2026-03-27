"""Shared helpers for CLI commands to reduce boilerplate."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from pbi_cli.core.errors import TomError
from pbi_cli.core.output import format_result, print_error

if TYPE_CHECKING:
    from pbi_cli.main import PbiContext


def run_command(
    ctx: PbiContext,
    fn: Callable[..., Any],
    **kwargs: Any,
) -> Any:
    """Execute a backend function with standard error handling.

    Calls ``fn(**kwargs)`` and formats the output based on the
    ``--json`` flag. Returns the result or exits on error.
    """
    try:
        result = fn(**kwargs)
        format_result(result, ctx.json_output)
        return result
    except Exception as e:
        print_error(str(e))
        if not ctx.repl_mode:
            raise SystemExit(1)
        raise TomError(fn.__name__, str(e))


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
