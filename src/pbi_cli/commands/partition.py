"""Partition management commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import run_command
from pbi_cli.main import PbiContext, pass_context


@click.group()
def partition() -> None:
    """Manage table partitions."""


@partition.command(name="list")
@click.option("--table", "-t", required=True, help="Table name.")
@pass_context
def partition_list(ctx: PbiContext, table: str) -> None:
    """List partitions in a table."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import partition_list as _partition_list

    session = get_session_for_command(ctx)
    run_command(ctx, _partition_list, model=session.model, table_name=table)


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
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import partition_create

    session = get_session_for_command(ctx)
    run_command(
        ctx,
        partition_create,
        model=session.model,
        table_name=table,
        name=name,
        expression=expression,
        mode=mode,
    )


@partition.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table name.")
@pass_context
def delete(ctx: PbiContext, name: str, table: str) -> None:
    """Delete a partition."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import partition_delete

    session = get_session_for_command(ctx)
    run_command(ctx, partition_delete, model=session.model, table_name=table, name=name)


@partition.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table name.")
@pass_context
def refresh(ctx: PbiContext, name: str, table: str) -> None:
    """Refresh a partition."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import partition_refresh

    session = get_session_for_command(ctx)
    run_command(ctx, partition_refresh, model=session.model, table_name=table, name=name)
