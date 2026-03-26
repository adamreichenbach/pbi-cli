"""Perspective management commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import build_definition, run_tool
from pbi_cli.main import PbiContext, pass_context


@click.group()
def perspective() -> None:
    """Manage model perspectives."""


@perspective.command(name="list")
@pass_context
def perspective_list(ctx: PbiContext) -> None:
    """List all perspectives."""
    run_tool(ctx, "perspective_operations", {"operation": "List"})


@perspective.command()
@click.argument("name")
@click.option("--description", default=None, help="Perspective description.")
@pass_context
def create(ctx: PbiContext, name: str, description: str | None) -> None:
    """Create a perspective."""
    definition = build_definition(required={"name": name}, optional={"description": description})
    run_tool(ctx, "perspective_operations", {"operation": "Create", "definitions": [definition]})


@perspective.command()
@click.argument("name")
@pass_context
def delete(ctx: PbiContext, name: str) -> None:
    """Delete a perspective."""
    run_tool(ctx, "perspective_operations", {"operation": "Delete", "name": name})
