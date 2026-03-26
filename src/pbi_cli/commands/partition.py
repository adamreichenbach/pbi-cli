"""Partition management commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import build_definition, run_tool
from pbi_cli.main import PbiContext, pass_context


@click.group()
def partition() -> None:
    """Manage table partitions."""


@partition.command(name="list")
@click.option("--table", "-t", required=True, help="Table name.")
@pass_context
def partition_list(ctx: PbiContext, table: str) -> None:
    """List partitions in a table."""
    run_tool(ctx, "partition_operations", {"operation": "List", "tableName": table})


@partition.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table name.")
@click.option("--expression", "-e", default=None, help="M/Power Query expression.")
@click.option("--mode", type=click.Choice(["Import", "DirectQuery", "Dual"]), default=None)
@pass_context
def create(
    ctx: PbiContext, name: str, table: str, expression: str | None, mode: str | None
) -> None:
    """Create a partition."""
    definition = build_definition(
        required={"name": name, "tableName": table},
        optional={"expression": expression, "mode": mode},
    )
    run_tool(ctx, "partition_operations", {"operation": "Create", "definitions": [definition]})


@partition.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table name.")
@pass_context
def delete(ctx: PbiContext, name: str, table: str) -> None:
    """Delete a partition."""
    run_tool(ctx, "partition_operations", {"operation": "Delete", "name": name, "tableName": table})


@partition.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table name.")
@pass_context
def refresh(ctx: PbiContext, name: str, table: str) -> None:
    """Refresh a partition."""
    run_tool(ctx, "partition_operations", {
        "operation": "Refresh",
        "name": name,
        "tableName": table,
    })
