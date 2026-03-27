"""DAX query commands: execute, validate, clear-cache."""

from __future__ import annotations

import sys

import click

from pbi_cli.commands._helpers import run_command
from pbi_cli.core.output import print_error
from pbi_cli.main import PbiContext, pass_context


@click.group()
def dax() -> None:
    """Execute and validate DAX queries."""


@dax.command()
@click.argument("query", default="")
@click.option(
    "--file", "-f", "query_file", type=click.Path(exists=True), help="Read query from file."
)
@click.option("--max-rows", type=int, default=None, help="Maximum rows to return.")
@click.option("--timeout", type=int, default=200, help="Query timeout in seconds.")
@pass_context
def execute(
    ctx: PbiContext,
    query: str,
    query_file: str | None,
    max_rows: int | None,
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

    from pbi_cli.core.adomd_backend import execute_dax
    from pbi_cli.core.session import get_session_for_command

    session = get_session_for_command(ctx)
    run_command(
        ctx,
        execute_dax,
        adomd_connection=session.adomd_connection,
        query=resolved_query,
        max_rows=max_rows,
        timeout=timeout,
    )


@dax.command()
@click.argument("query", default="")
@click.option(
    "--file", "-f", "query_file", type=click.Path(exists=True), help="Read query from file."
)
@click.option("--timeout", type=int, default=10, help="Validation timeout in seconds.")
@pass_context
def validate(ctx: PbiContext, query: str, query_file: str | None, timeout: int) -> None:
    """Validate a DAX query without executing it."""
    resolved_query = _resolve_query(query, query_file)
    if not resolved_query:
        print_error("No query provided.")
        raise SystemExit(1)

    from pbi_cli.core.adomd_backend import validate_dax
    from pbi_cli.core.session import get_session_for_command

    session = get_session_for_command(ctx)
    run_command(
        ctx,
        validate_dax,
        adomd_connection=session.adomd_connection,
        query=resolved_query,
        timeout=timeout,
    )


@dax.command(name="clear-cache")
@pass_context
def clear_cache_cmd(ctx: PbiContext) -> None:
    """Clear the DAX query cache."""
    from pbi_cli.core.adomd_backend import clear_cache
    from pbi_cli.core.session import get_session_for_command

    session = get_session_for_command(ctx)
    db_id = str(session.database.ID) if session.database else ""
    run_command(ctx, clear_cache, adomd_connection=session.adomd_connection, database_id=db_id)


def _resolve_query(query: str, query_file: str | None) -> str:
    """Resolve the DAX query from argument, file, or stdin."""
    if query == "-":
        return sys.stdin.read().strip()
    if query_file:
        with open(query_file, encoding="utf-8") as f:
            return f.read().strip()
    return query.strip()
