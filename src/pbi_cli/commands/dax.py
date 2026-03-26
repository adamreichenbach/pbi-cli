"""DAX query commands: execute, validate, clear-cache."""

from __future__ import annotations

import sys

import click

from pbi_cli.core.mcp_client import get_client
from pbi_cli.core.output import format_mcp_result, print_error
from pbi_cli.main import PbiContext, pass_context


@click.group()
def dax() -> None:
    """Execute and validate DAX queries."""


@dax.command()
@click.argument("query", default="")
@click.option("--file", "-f", "query_file", type=click.Path(exists=True), help="Read query from file.")
@click.option("--max-rows", type=int, default=None, help="Maximum rows to return.")
@click.option("--metrics", is_flag=True, default=False, help="Include execution metrics.")
@click.option("--metrics-only", is_flag=True, default=False, help="Return metrics without row data.")
@click.option("--timeout", type=int, default=200, help="Query timeout in seconds.")
@pass_context
def execute(
    ctx: PbiContext,
    query: str,
    query_file: str | None,
    max_rows: int | None,
    metrics: bool,
    metrics_only: bool,
    timeout: int,
) -> None:
    """Execute a DAX query.

    Pass the query as an argument, via --file, or pipe it from stdin:

        pbi dax execute "EVALUATE Sales"

        pbi dax execute --file query.dax

        cat query.dax | pbi dax execute -
    """
    resolved_query = _resolve_query(query, query_file)
    if not resolved_query:
        print_error("No query provided. Pass as argument, --file, or stdin.")
        raise SystemExit(1)

    request: dict = {
        "operation": "Execute",
        "query": resolved_query,
        "timeoutSeconds": timeout,
        "getExecutionMetrics": metrics or metrics_only,
        "executionMetricsOnly": metrics_only,
    }
    if ctx.connection:
        request["connectionName"] = ctx.connection
    if max_rows is not None:
        request["maxRows"] = max_rows

    client = get_client()
    try:
        result = client.call_tool("dax_query_operations", request)
        format_mcp_result(result, ctx.json_output)
    except Exception as e:
        print_error(f"DAX execution failed: {e}")
        raise SystemExit(1)
    finally:
        client.stop()


@dax.command()
@click.argument("query", default="")
@click.option("--file", "-f", "query_file", type=click.Path(exists=True), help="Read query from file.")
@click.option("--timeout", type=int, default=10, help="Validation timeout in seconds.")
@pass_context
def validate(ctx: PbiContext, query: str, query_file: str | None, timeout: int) -> None:
    """Validate a DAX query without executing it."""
    resolved_query = _resolve_query(query, query_file)
    if not resolved_query:
        print_error("No query provided.")
        raise SystemExit(1)

    request: dict = {
        "operation": "Validate",
        "query": resolved_query,
        "timeoutSeconds": timeout,
    }
    if ctx.connection:
        request["connectionName"] = ctx.connection

    client = get_client()
    try:
        result = client.call_tool("dax_query_operations", request)
        format_mcp_result(result, ctx.json_output)
    except Exception as e:
        print_error(f"DAX validation failed: {e}")
        raise SystemExit(1)
    finally:
        client.stop()


@dax.command(name="clear-cache")
@pass_context
def clear_cache(ctx: PbiContext) -> None:
    """Clear the DAX query cache."""
    request: dict = {"operation": "ClearCache"}
    if ctx.connection:
        request["connectionName"] = ctx.connection

    client = get_client()
    try:
        result = client.call_tool("dax_query_operations", request)
        format_mcp_result(result, ctx.json_output)
    except Exception as e:
        print_error(f"Cache clear failed: {e}")
        raise SystemExit(1)
    finally:
        client.stop()


def _resolve_query(query: str, query_file: str | None) -> str:
    """Resolve the DAX query from argument, file, or stdin."""
    if query == "-":
        return sys.stdin.read().strip()
    if query_file:
        with open(query_file, encoding="utf-8") as f:
            return f.read().strip()
    return query.strip()
