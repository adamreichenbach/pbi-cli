"""Table CRUD commands."""

from __future__ import annotations

import sys

import click

from pbi_cli.commands._helpers import build_definition, run_tool
from pbi_cli.main import PbiContext, pass_context


@click.group()
def table() -> None:
    """Manage tables in a semantic model."""


@table.command(name="list")
@pass_context
def table_list(ctx: PbiContext) -> None:
    """List all tables."""
    run_tool(ctx, "table_operations", {"operation": "List"})


@table.command()
@click.argument("name")
@pass_context
def get(ctx: PbiContext, name: str) -> None:
    """Get details of a specific table."""
    run_tool(ctx, "table_operations", {"operation": "Get", "name": name})


@table.command()
@click.argument("name")
@click.option(
    "--mode", type=click.Choice(["Import", "DirectQuery", "Dual"]),
    default="Import", help="Table mode.",
)
@click.option("--m-expression", default=None, help="M/Power Query expression (use - for stdin).")
@click.option("--dax-expression", default=None, help="DAX expression for calculated tables.")
@click.option("--sql-query", default=None, help="SQL query for DirectQuery.")
@click.option("--description", default=None, help="Table description.")
@click.option("--hidden", is_flag=True, default=False, help="Hide from client tools.")
@pass_context
def create(
    ctx: PbiContext,
    name: str,
    mode: str,
    m_expression: str | None,
    dax_expression: str | None,
    sql_query: str | None,
    description: str | None,
    hidden: bool,
) -> None:
    """Create a new table."""
    if m_expression == "-":
        m_expression = sys.stdin.read().strip()
    if dax_expression == "-":
        dax_expression = sys.stdin.read().strip()

    definition = build_definition(
        required={"name": name},
        optional={
            "mode": mode,
            "mExpression": m_expression,
            "daxExpression": dax_expression,
            "sqlQuery": sql_query,
            "description": description,
            "isHidden": hidden if hidden else None,
        },
    )
    run_tool(ctx, "table_operations", {
        "operation": "Create",
        "definitions": [definition],
    })


@table.command()
@click.argument("name")
@pass_context
def delete(ctx: PbiContext, name: str) -> None:
    """Delete a table."""
    run_tool(ctx, "table_operations", {"operation": "Delete", "name": name})


@table.command()
@click.argument("name")
@click.option(
    "--type", "refresh_type",
    type=click.Choice(["Full", "Automatic", "Calculate", "DataOnly"]),
    default="Automatic", help="Refresh type.",
)
@pass_context
def refresh(ctx: PbiContext, name: str, refresh_type: str) -> None:
    """Refresh a table."""
    run_tool(ctx, "table_operations", {
        "operation": "Refresh",
        "name": name,
        "refreshType": refresh_type,
    })


@table.command()
@click.argument("name")
@pass_context
def schema(ctx: PbiContext, name: str) -> None:
    """Get the schema of a table."""
    run_tool(ctx, "table_operations", {"operation": "GetSchema", "name": name})


@table.command(name="export-tmdl")
@click.argument("name")
@pass_context
def export_tmdl(ctx: PbiContext, name: str) -> None:
    """Export a table as TMDL."""
    run_tool(ctx, "table_operations", {"operation": "ExportTMDL", "name": name})


@table.command()
@click.argument("old_name")
@click.argument("new_name")
@pass_context
def rename(ctx: PbiContext, old_name: str, new_name: str) -> None:
    """Rename a table."""
    run_tool(ctx, "table_operations", {
        "operation": "Rename",
        "name": old_name,
        "newName": new_name,
    })


@table.command(name="mark-date")
@click.argument("name")
@click.option("--date-column", required=True, help="Date column to use.")
@pass_context
def mark_date_table(ctx: PbiContext, name: str, date_column: str) -> None:
    """Mark a table as a date table."""
    run_tool(ctx, "table_operations", {
        "operation": "MarkAsDateTable",
        "name": name,
        "dateColumn": date_column,
    })
