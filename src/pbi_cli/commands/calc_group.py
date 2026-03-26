"""Calculation group commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import build_definition, run_tool
from pbi_cli.main import PbiContext, pass_context


@click.group(name="calc-group")
def calc_group() -> None:
    """Manage calculation groups."""


@calc_group.command(name="list")
@pass_context
def cg_list(ctx: PbiContext) -> None:
    """List all calculation groups."""
    run_tool(ctx, "calculation_group_operations", {"operation": "ListGroups"})


@calc_group.command()
@click.argument("name")
@click.option("--description", default=None, help="Group description.")
@click.option("--precedence", type=int, default=None, help="Calculation precedence.")
@pass_context
def create(ctx: PbiContext, name: str, description: str | None, precedence: int | None) -> None:
    """Create a calculation group."""
    definition = build_definition(
        required={"name": name},
        optional={"description": description, "calculationGroupPrecedence": precedence},
    )
    run_tool(
        ctx,
        "calculation_group_operations",
        {
            "operation": "CreateGroup",
            "definitions": [definition],
        },
    )


@calc_group.command()
@click.argument("name")
@pass_context
def delete(ctx: PbiContext, name: str) -> None:
    """Delete a calculation group."""
    run_tool(ctx, "calculation_group_operations", {"operation": "DeleteGroup", "name": name})


@calc_group.command(name="items")
@click.argument("group_name")
@pass_context
def list_items(ctx: PbiContext, group_name: str) -> None:
    """List calculation items in a group."""
    run_tool(
        ctx,
        "calculation_group_operations",
        {
            "operation": "ListItems",
            "calculationGroupName": group_name,
        },
    )


@calc_group.command(name="create-item")
@click.argument("item_name")
@click.option("--group", "-g", required=True, help="Calculation group name.")
@click.option("--expression", "-e", required=True, help="DAX expression.")
@click.option("--ordinal", type=int, default=None, help="Item ordinal.")
@pass_context
def create_item(
    ctx: PbiContext, item_name: str, group: str, expression: str, ordinal: int | None
) -> None:
    """Create a calculation item in a group."""
    definition = build_definition(
        required={"name": item_name, "expression": expression},
        optional={"ordinal": ordinal},
    )
    run_tool(
        ctx,
        "calculation_group_operations",
        {
            "operation": "CreateItem",
            "calculationGroupName": group,
            "definitions": [definition],
        },
    )
