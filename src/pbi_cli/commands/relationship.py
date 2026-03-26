"""Relationship management commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import build_definition, run_tool
from pbi_cli.main import PbiContext, pass_context


@click.group()
def relationship() -> None:
    """Manage relationships between tables."""


@relationship.command(name="list")
@pass_context
def relationship_list(ctx: PbiContext) -> None:
    """List all relationships."""
    run_tool(ctx, "relationship_operations", {"operation": "List"})


@relationship.command()
@click.argument("name")
@pass_context
def get(ctx: PbiContext, name: str) -> None:
    """Get details of a specific relationship."""
    run_tool(ctx, "relationship_operations", {"operation": "Get", "name": name})


@relationship.command()
@click.option("--name", "-n", default=None, help="Relationship name (auto-generated if omitted).")
@click.option("--from-table", required=True, help="Source (many-side) table.")
@click.option("--from-column", required=True, help="Source column.")
@click.option("--to-table", required=True, help="Target (one-side) table.")
@click.option("--to-column", required=True, help="Target column.")
@click.option(
    "--cross-filter",
    type=click.Choice(["OneDirection", "BothDirections", "Automatic"]),
    default="OneDirection",
    help="Cross-filtering behavior.",
)
@click.option("--active/--inactive", default=True, help="Whether the relationship is active.")
@pass_context
def create(
    ctx: PbiContext,
    name: str | None,
    from_table: str,
    from_column: str,
    to_table: str,
    to_column: str,
    cross_filter: str,
    active: bool,
) -> None:
    """Create a new relationship."""
    definition = build_definition(
        required={
            "fromTable": from_table,
            "fromColumn": from_column,
            "toTable": to_table,
            "toColumn": to_column,
        },
        optional={
            "name": name,
            "crossFilteringBehavior": cross_filter,
            "isActive": active,
        },
    )
    run_tool(ctx, "relationship_operations", {"operation": "Create", "definitions": [definition]})


@relationship.command()
@click.argument("name")
@pass_context
def delete(ctx: PbiContext, name: str) -> None:
    """Delete a relationship."""
    run_tool(ctx, "relationship_operations", {"operation": "Delete", "name": name})


@relationship.command()
@click.argument("name")
@pass_context
def activate(ctx: PbiContext, name: str) -> None:
    """Activate a relationship."""
    run_tool(ctx, "relationship_operations", {"operation": "Activate", "name": name})


@relationship.command()
@click.argument("name")
@pass_context
def deactivate(ctx: PbiContext, name: str) -> None:
    """Deactivate a relationship."""
    run_tool(ctx, "relationship_operations", {"operation": "Deactivate", "name": name})


@relationship.command()
@click.option("--table", "-t", required=True, help="Table to search for relationships.")
@pass_context
def find(ctx: PbiContext, table: str) -> None:
    """Find relationships involving a table."""
    run_tool(ctx, "relationship_operations", {"operation": "Find", "tableName": table})


@relationship.command(name="export-tmdl")
@click.argument("name")
@pass_context
def export_tmdl(ctx: PbiContext, name: str) -> None:
    """Export a relationship as TMDL."""
    run_tool(ctx, "relationship_operations", {"operation": "ExportTMDL", "name": name})
