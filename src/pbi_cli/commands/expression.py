"""Named expression and parameter commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import build_definition, run_tool
from pbi_cli.main import PbiContext, pass_context


@click.group()
def expression() -> None:
    """Manage named expressions and parameters."""


@expression.command(name="list")
@pass_context
def expression_list(ctx: PbiContext) -> None:
    """List all named expressions."""
    run_tool(ctx, "named_expression_operations", {"operation": "List"})


@expression.command()
@click.argument("name")
@pass_context
def get(ctx: PbiContext, name: str) -> None:
    """Get a named expression."""
    run_tool(ctx, "named_expression_operations", {"operation": "Get", "name": name})


@expression.command()
@click.argument("name")
@click.option("--expression", "-e", required=True, help="M expression.")
@click.option("--description", default=None, help="Expression description.")
@pass_context
def create(ctx: PbiContext, name: str, expression: str, description: str | None) -> None:
    """Create a named expression."""
    definition = build_definition(
        required={"name": name, "expression": expression},
        optional={"description": description},
    )
    run_tool(ctx, "named_expression_operations", {"operation": "Create", "definitions": [definition]})


@expression.command()
@click.argument("name")
@pass_context
def delete(ctx: PbiContext, name: str) -> None:
    """Delete a named expression."""
    run_tool(ctx, "named_expression_operations", {"operation": "Delete", "name": name})


@expression.command(name="create-param")
@click.argument("name")
@click.option("--expression", "-e", required=True, help="Default value expression.")
@click.option("--description", default=None, help="Parameter description.")
@pass_context
def create_param(ctx: PbiContext, name: str, expression: str, description: str | None) -> None:
    """Create a model parameter."""
    definition = build_definition(
        required={"name": name, "expression": expression},
        optional={"description": description},
    )
    run_tool(ctx, "named_expression_operations", {"operation": "CreateParameter", "definitions": [definition]})
