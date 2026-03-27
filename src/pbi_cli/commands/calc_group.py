"""Calculation group commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import run_command
from pbi_cli.main import PbiContext, pass_context


@click.group(name="calc-group")
def calc_group() -> None:
    """Manage calculation groups."""


@calc_group.command(name="list")
@pass_context
def cg_list(ctx: PbiContext) -> None:
    """List all calculation groups."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import calc_group_list

    session = get_session_for_command(ctx)
    run_command(ctx, calc_group_list, model=session.model)


@calc_group.command()
@click.argument("name")
@click.option("--description", default=None, help="Group description.")
@click.option("--precedence", type=int, default=None, help="Calculation precedence.")
@pass_context
def create(ctx: PbiContext, name: str, description: str | None, precedence: int | None) -> None:
    """Create a calculation group."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import calc_group_create

    session = get_session_for_command(ctx)
    run_command(
        ctx,
        calc_group_create,
        model=session.model,
        name=name,
        description=description,
        precedence=precedence,
    )


@calc_group.command()
@click.argument("name")
@pass_context
def delete(ctx: PbiContext, name: str) -> None:
    """Delete a calculation group."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import calc_group_delete

    session = get_session_for_command(ctx)
    run_command(ctx, calc_group_delete, model=session.model, name=name)


@calc_group.command(name="items")
@click.argument("group_name")
@pass_context
def list_items(ctx: PbiContext, group_name: str) -> None:
    """List calculation items in a group."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import calc_item_list

    session = get_session_for_command(ctx)
    run_command(ctx, calc_item_list, model=session.model, group_name=group_name)


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
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import calc_item_create

    session = get_session_for_command(ctx)
    run_command(
        ctx,
        calc_item_create,
        model=session.model,
        group_name=group,
        name=item_name,
        expression=expression,
        ordinal=ordinal,
    )
