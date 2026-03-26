"""Calendar table commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import build_definition, run_tool
from pbi_cli.main import PbiContext, pass_context


@click.group()
def calendar() -> None:
    """Manage calendar tables."""


@calendar.command(name="list")
@pass_context
def calendar_list(ctx: PbiContext) -> None:
    """List calendar tables."""
    run_tool(ctx, "calendar_operations", {"operation": "List"})


@calendar.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Target table name.")
@click.option("--description", default=None, help="Calendar description.")
@pass_context
def create(ctx: PbiContext, name: str, table: str, description: str | None) -> None:
    """Create a calendar table."""
    definition = build_definition(
        required={"name": name, "tableName": table},
        optional={"description": description},
    )
    run_tool(ctx, "calendar_operations", {"operation": "Create", "definitions": [definition]})


@calendar.command()
@click.argument("name")
@pass_context
def delete(ctx: PbiContext, name: str) -> None:
    """Delete a calendar."""
    run_tool(ctx, "calendar_operations", {"operation": "Delete", "name": name})
