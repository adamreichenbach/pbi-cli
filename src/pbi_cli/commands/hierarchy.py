"""User hierarchy commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import run_command
from pbi_cli.main import PbiContext, pass_context


@click.group()
def hierarchy() -> None:
    """Manage user hierarchies."""


@hierarchy.command(name="list")
@click.option("--table", "-t", default=None, help="Filter by table.")
@pass_context
def hierarchy_list(ctx: PbiContext, table: str | None) -> None:
    """List hierarchies."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import hierarchy_list as _hierarchy_list

    session = get_session_for_command(ctx)
    run_command(ctx, _hierarchy_list, model=session.model, table_name=table)


@hierarchy.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table name.")
@pass_context
def get(ctx: PbiContext, name: str, table: str) -> None:
    """Get hierarchy details."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import hierarchy_get

    session = get_session_for_command(ctx)
    run_command(ctx, hierarchy_get, model=session.model, table_name=table, name=name)


@hierarchy.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table name.")
@click.option("--description", default=None, help="Hierarchy description.")
@pass_context
def create(ctx: PbiContext, name: str, table: str, description: str | None) -> None:
    """Create a hierarchy."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import hierarchy_create

    session = get_session_for_command(ctx)
    run_command(
        ctx,
        hierarchy_create,
        model=session.model,
        table_name=table,
        name=name,
        description=description,
    )


@hierarchy.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table name.")
@pass_context
def delete(ctx: PbiContext, name: str, table: str) -> None:
    """Delete a hierarchy."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import hierarchy_delete

    session = get_session_for_command(ctx)
    run_command(ctx, hierarchy_delete, model=session.model, table_name=table, name=name)
