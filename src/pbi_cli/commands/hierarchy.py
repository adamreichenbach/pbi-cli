"""User hierarchy commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import build_definition, run_tool
from pbi_cli.main import PbiContext, pass_context


@click.group()
def hierarchy() -> None:
    """Manage user hierarchies."""


@hierarchy.command(name="list")
@click.option("--table", "-t", default=None, help="Filter by table.")
@pass_context
def hierarchy_list(ctx: PbiContext, table: str | None) -> None:
    """List hierarchies."""
    request: dict[str, object] = {"operation": "List"}
    if table:
        request["tableName"] = table
    run_tool(ctx, "user_hierarchy_operations", request)


@hierarchy.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table name.")
@pass_context
def get(ctx: PbiContext, name: str, table: str) -> None:
    """Get hierarchy details."""
    run_tool(ctx, "user_hierarchy_operations", {
        "operation": "Get",
        "name": name,
        "tableName": table,
    })


@hierarchy.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table name.")
@click.option("--description", default=None, help="Hierarchy description.")
@pass_context
def create(ctx: PbiContext, name: str, table: str, description: str | None) -> None:
    """Create a hierarchy."""
    definition = build_definition(
        required={"name": name, "tableName": table},
        optional={"description": description},
    )
    run_tool(ctx, "user_hierarchy_operations", {"operation": "Create", "definitions": [definition]})


@hierarchy.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table name.")
@pass_context
def delete(ctx: PbiContext, name: str, table: str) -> None:
    """Delete a hierarchy."""
    run_tool(ctx, "user_hierarchy_operations", {
        "operation": "Delete",
        "name": name,
        "tableName": table,
    })
