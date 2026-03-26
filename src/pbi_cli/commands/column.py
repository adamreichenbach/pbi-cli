"""Column CRUD commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import build_definition, run_tool
from pbi_cli.main import PbiContext, pass_context


@click.group()
def column() -> None:
    """Manage columns in a semantic model."""


@column.command(name="list")
@click.option("--table", "-t", required=True, help="Table name.")
@pass_context
def column_list(ctx: PbiContext, table: str) -> None:
    """List all columns in a table."""
    run_tool(ctx, "column_operations", {"operation": "List", "tableName": table})


@column.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table name.")
@pass_context
def get(ctx: PbiContext, name: str, table: str) -> None:
    """Get details of a specific column."""
    run_tool(ctx, "column_operations", {"operation": "Get", "name": name, "tableName": table})


@column.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table name.")
@click.option(
    "--data-type", required=True, help="Data type (string, int64, double, datetime, etc.)."
)
@click.option("--source-column", default=None, help="Source column name (for Import mode).")
@click.option("--expression", default=None, help="DAX expression (for calculated columns).")
@click.option("--format-string", default=None, help="Format string.")
@click.option("--description", default=None, help="Column description.")
@click.option("--folder", default=None, help="Display folder.")
@click.option("--hidden", is_flag=True, default=False, help="Hide from client tools.")
@click.option("--is-key", is_flag=True, default=False, help="Mark as key column.")
@pass_context
def create(
    ctx: PbiContext,
    name: str,
    table: str,
    data_type: str,
    source_column: str | None,
    expression: str | None,
    format_string: str | None,
    description: str | None,
    folder: str | None,
    hidden: bool,
    is_key: bool,
) -> None:
    """Create a new column."""
    definition = build_definition(
        required={"name": name, "tableName": table, "dataType": data_type},
        optional={
            "sourceColumn": source_column,
            "expression": expression,
            "formatString": format_string,
            "description": description,
            "displayFolder": folder,
            "isHidden": hidden if hidden else None,
            "isKey": is_key if is_key else None,
        },
    )
    run_tool(ctx, "column_operations", {"operation": "Create", "definitions": [definition]})


@column.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table name.")
@pass_context
def delete(ctx: PbiContext, name: str, table: str) -> None:
    """Delete a column."""
    run_tool(ctx, "column_operations", {"operation": "Delete", "name": name, "tableName": table})


@column.command()
@click.argument("old_name")
@click.argument("new_name")
@click.option("--table", "-t", required=True, help="Table name.")
@pass_context
def rename(ctx: PbiContext, old_name: str, new_name: str, table: str) -> None:
    """Rename a column."""
    run_tool(ctx, "column_operations", {
        "operation": "Rename",
        "name": old_name,
        "newName": new_name,
        "tableName": table,
    })


@column.command(name="export-tmdl")
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table name.")
@pass_context
def export_tmdl(ctx: PbiContext, name: str, table: str) -> None:
    """Export a column as TMDL."""
    run_tool(ctx, "column_operations", {
        "operation": "ExportTMDL",
        "name": name,
        "tableName": table,
    })
