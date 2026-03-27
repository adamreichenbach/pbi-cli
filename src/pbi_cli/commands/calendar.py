"""Calendar table commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import run_command
from pbi_cli.main import PbiContext, pass_context


@click.group()
def calendar() -> None:
    """Manage calendar tables."""


@calendar.command(name="list")
@pass_context
def calendar_list(ctx: PbiContext) -> None:
    """List calendar/date tables (tables with DataCategory = Time)."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import _safe_str

    session = get_session_for_command(ctx)
    # Filter to tables marked as date/calendar tables
    # Check DataCategory on the actual TOM objects
    results = []
    for table in session.model.Tables:
        cat = _safe_str(table.DataCategory)
        if cat.lower() in ("time", "date"):
            results.append({
                "name": str(table.Name),
                "dataCategory": cat,
                "columns": table.Columns.Count,
            })
    from pbi_cli.core.output import format_result

    format_result(results, ctx.json_output)


@calendar.command(name="mark")
@click.argument("name")
@click.option("--date-column", required=True, help="Date column to use as key.")
@pass_context
def mark(ctx: PbiContext, name: str, date_column: str) -> None:
    """Mark a table as a calendar/date table."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import table_mark_as_date

    session = get_session_for_command(ctx)
    run_command(
        ctx,
        table_mark_as_date,
        model=session.model,
        table_name=name,
        date_column=date_column,
    )
