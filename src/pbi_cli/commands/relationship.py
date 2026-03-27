"""Relationship management commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import run_command
from pbi_cli.main import PbiContext, pass_context


@click.group()
def relationship() -> None:
    """Manage relationships between tables."""


@relationship.command(name="list")
@pass_context
def relationship_list(ctx: PbiContext) -> None:
    """List all relationships."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import relationship_list as _rel_list

    session = get_session_for_command(ctx)
    run_command(ctx, _rel_list, model=session.model)


@relationship.command()
@click.argument("name")
@pass_context
def get(ctx: PbiContext, name: str) -> None:
    """Get details of a specific relationship."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import relationship_get

    session = get_session_for_command(ctx)
    run_command(ctx, relationship_get, model=session.model, name=name)


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
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import relationship_create

    session = get_session_for_command(ctx)
    run_command(
        ctx,
        relationship_create,
        model=session.model,
        from_table=from_table,
        from_column=from_column,
        to_table=to_table,
        to_column=to_column,
        name=name,
        cross_filter=cross_filter,
        is_active=active,
    )


@relationship.command()
@click.argument("name")
@pass_context
def delete(ctx: PbiContext, name: str) -> None:
    """Delete a relationship."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import relationship_delete

    session = get_session_for_command(ctx)
    run_command(ctx, relationship_delete, model=session.model, name=name)


@relationship.command()
@click.argument("name")
@pass_context
def activate(ctx: PbiContext, name: str) -> None:
    """Activate a relationship."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import relationship_set_active

    session = get_session_for_command(ctx)
    run_command(ctx, relationship_set_active, model=session.model, name=name, active=True)


@relationship.command()
@click.argument("name")
@pass_context
def deactivate(ctx: PbiContext, name: str) -> None:
    """Deactivate a relationship."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import relationship_set_active

    session = get_session_for_command(ctx)
    run_command(ctx, relationship_set_active, model=session.model, name=name, active=False)


@relationship.command()
@click.option("--table", "-t", required=True, help="Table to search for relationships.")
@pass_context
def find(ctx: PbiContext, table: str) -> None:
    """Find relationships involving a table."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import relationship_find

    session = get_session_for_command(ctx)
    run_command(ctx, relationship_find, model=session.model, table_name=table)
