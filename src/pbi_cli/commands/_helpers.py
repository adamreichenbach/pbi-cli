"""Shared helpers for CLI commands to reduce boilerplate."""

from __future__ import annotations

from typing import Any

from pbi_cli.core.errors import McpToolError
from pbi_cli.core.mcp_client import get_client
from pbi_cli.core.output import format_mcp_result, print_error
from pbi_cli.main import PbiContext


def resolve_connection_name(ctx: PbiContext) -> str | None:
    """Return the connection name from --connection flag or last-used store."""
    if ctx.connection:
        return ctx.connection
    from pbi_cli.core.connection_store import load_connections

    store = load_connections()
    return store.last_used or None


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
    conn_name = resolve_connection_name(ctx)
    if conn_name:
        request.setdefault("connectionName", conn_name)

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
