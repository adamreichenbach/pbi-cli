"""Measure CRUD commands."""

from __future__ import annotations

import sys

import click

from pbi_cli.commands._helpers import build_definition, run_tool
from pbi_cli.main import PbiContext, pass_context


@click.group()
def measure() -> None:
    """Manage measures in a semantic model."""


@measure.command(name="list")
@click.option("--table", "-t", default=None, help="Filter by table name.")
@pass_context
def measure_list(ctx: PbiContext, table: str | None) -> None:
    """List all measures."""
    request: dict[str, object] = {"operation": "List"}
    if table:
        request["tableName"] = table
    run_tool(ctx, "measure_operations", request)


@measure.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table containing the measure.")
@pass_context
def get(ctx: PbiContext, name: str, table: str) -> None:
    """Get details of a specific measure."""
    run_tool(ctx, "measure_operations", {
        "operation": "Get",
        "name": name,
        "tableName": table,
    })


@measure.command()
@click.argument("name")
@click.option("--expression", "-e", required=True, help="DAX expression (use - for stdin).")
@click.option("--table", "-t", required=True, help="Target table.")
@click.option("--format-string", default=None, help='Format string (e.g., "$#,##0").')
@click.option("--description", default=None, help="Measure description.")
@click.option("--folder", default=None, help="Display folder path.")
@click.option("--hidden", is_flag=True, default=False, help="Hide from client tools.")
@pass_context
def create(
    ctx: PbiContext,
    name: str,
    expression: str,
    table: str,
    format_string: str | None,
    description: str | None,
    folder: str | None,
    hidden: bool,
) -> None:
    """Create a new measure."""
    if expression == "-":
        expression = sys.stdin.read().strip()

    definition = build_definition(
        required={"name": name, "expression": expression, "tableName": table},
        optional={
            "formatString": format_string,
            "description": description,
            "displayFolder": folder,
            "isHidden": hidden if hidden else None,
        },
    )
    run_tool(ctx, "measure_operations", {
        "operation": "Create",
        "definitions": [definition],
    })


@measure.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table containing the measure.")
@click.option("--expression", "-e", default=None, help="New DAX expression.")
@click.option("--format-string", default=None, help="New format string.")
@click.option("--description", default=None, help="New description.")
@click.option("--folder", default=None, help="New display folder.")
@pass_context
def update(
    ctx: PbiContext,
    name: str,
    table: str,
    expression: str | None,
    format_string: str | None,
    description: str | None,
    folder: str | None,
) -> None:
    """Update an existing measure."""
    if expression == "-":
        expression = sys.stdin.read().strip()

    definition = build_definition(
        required={"name": name, "tableName": table},
        optional={
            "expression": expression,
            "formatString": format_string,
            "description": description,
            "displayFolder": folder,
        },
    )
    run_tool(ctx, "measure_operations", {
        "operation": "Update",
        "definitions": [definition],
    })


@measure.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table containing the measure.")
@pass_context
def delete(ctx: PbiContext, name: str, table: str) -> None:
    """Delete a measure."""
    run_tool(ctx, "measure_operations", {
        "operation": "Delete",
        "name": name,
        "tableName": table,
    })


@measure.command()
@click.argument("old_name")
@click.argument("new_name")
@click.option("--table", "-t", required=True, help="Table containing the measure.")
@pass_context
def rename(ctx: PbiContext, old_name: str, new_name: str, table: str) -> None:
    """Rename a measure."""
    run_tool(ctx, "measure_operations", {
        "operation": "Rename",
        "name": old_name,
        "newName": new_name,
        "tableName": table,
    })


@measure.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Source table.")
@click.option("--to-table", required=True, help="Destination table.")
@pass_context
def move(ctx: PbiContext, name: str, table: str, to_table: str) -> None:
    """Move a measure to a different table."""
    run_tool(ctx, "measure_operations", {
        "operation": "Move",
        "name": name,
        "tableName": table,
        "destinationTableName": to_table,
    })


@measure.command(name="export-tmdl")
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table containing the measure.")
@pass_context
def export_tmdl(ctx: PbiContext, name: str, table: str) -> None:
    """Export a measure as TMDL."""
    run_tool(ctx, "measure_operations", {
        "operation": "ExportTMDL",
        "name": name,
        "tableName": table,
    })
