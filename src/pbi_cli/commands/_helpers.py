"""Shared helpers for CLI commands to reduce boilerplate."""

from __future__ import annotations

from typing import Any

from pbi_cli.core.errors import McpToolError
from pbi_cli.core.mcp_client import PbiMcpClient, get_client
from pbi_cli.core.output import format_mcp_result, print_error
from pbi_cli.main import PbiContext


def resolve_connection_name(ctx: PbiContext) -> str | None:
    """Return the connection name from --connection flag or last-used store."""
    if ctx.connection:
        return ctx.connection
    from pbi_cli.core.connection_store import load_connections

    store = load_connections()
    return store.last_used or None


def _auto_reconnect(client: PbiMcpClient, ctx: PbiContext) -> str | None:
    """Re-establish the saved connection on a fresh MCP server process.

    Each non-REPL command starts a new MCP server, so the connection
    must be re-established before running any tool that needs one.
    Returns the connection name, or None if no saved connection exists.
    """
    from pbi_cli.core.connection_store import (
        get_active_connection,
        load_connections,
    )

    store = load_connections()
    conn = get_active_connection(store, override=ctx.connection)
    if conn is None:
        return None

    # Build the appropriate Connect request
    if conn.workspace_name:
        request: dict[str, object] = {
            "operation": "ConnectFabric",
            "workspaceName": conn.workspace_name,
            "semanticModelName": conn.semantic_model_name,
            "tenantName": conn.tenant_name,
        }
    else:
        request = {
            "operation": "Connect",
            "dataSource": conn.data_source,
        }
        if conn.initial_catalog:
            request["initialCatalog"] = conn.initial_catalog
        if conn.connection_string:
            request["connectionString"] = conn.connection_string

    result = client.call_tool("connection_operations", request)

    # Use server-assigned connection name (e.g. "PBIDesktop-demo-57947")
    # instead of our locally saved name (e.g. "localhost-57947")
    server_name = None
    if isinstance(result, dict):
        server_name = result.get("connectionName") or result.get("ConnectionName")
    return server_name or conn.name


def run_tool(
    ctx: PbiContext,
    tool_name: str,
    request: dict[str, Any],
) -> Any:
    """Execute an MCP tool call with standard error handling.

    In non-REPL mode, automatically re-establishes the saved connection
    before running the tool (each invocation starts a fresh MCP server).
    Formats output based on --json flag. Returns the result or exits on error.
    """
    client = get_client(repl_mode=ctx.repl_mode)
    try:
        # In non-REPL mode, re-establish connection on the fresh server
        if not ctx.repl_mode:
            conn_name = _auto_reconnect(client, ctx)
        else:
            conn_name = resolve_connection_name(ctx)

        if conn_name:
            request.setdefault("connectionName", conn_name)

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
