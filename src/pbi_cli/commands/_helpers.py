"""Shared helpers for CLI commands to reduce boilerplate."""

from __future__ import annotations

from typing import Any

from pbi_cli.core.errors import McpToolError
from pbi_cli.core.mcp_client import get_client
from pbi_cli.core.output import format_mcp_result, print_error
from pbi_cli.main import PbiContext


def run_tool(
    ctx: PbiContext,
    tool_name: str,
    request: dict[str, Any],
) -> Any:
    """Execute an MCP tool call with standard error handling.

    Adds connectionName from context if available. Formats output based
    on --json flag. Returns the result or exits on error.

    In REPL mode the shared client is reused and never stopped.
    """
    if ctx.connection:
        request.setdefault("connectionName", ctx.connection)

    client = get_client(repl_mode=ctx.repl_mode)
    try:
        result = client.call_tool(tool_name, request)
        format_mcp_result(result, ctx.json_output)
        return result
    except Exception as e:
        print_error(str(e))
        raise McpToolError(tool_name, str(e))
    finally:
        if not ctx.repl_mode:
            client.stop()


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
