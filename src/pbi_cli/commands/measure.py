"""Measure CRUD commands."""

from __future__ import annotations

import sys

import click

from pbi_cli.commands._helpers import run_command
from pbi_cli.main import PbiContext, pass_context


@click.group()
def measure() -> None:
    """Manage measures in a semantic model."""


@measure.command(name="list")
@click.option("--table", "-t", default=None, help="Filter by table name.")
@pass_context
def measure_list(ctx: PbiContext, table: str | None) -> None:
    """List all measures."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import measure_list as _measure_list

    session = get_session_for_command(ctx)
    run_command(ctx, _measure_list, model=session.model, table_name=table)


@measure.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table containing the measure.")
@pass_context
def get(ctx: PbiContext, name: str, table: str) -> None:
    """Get details of a specific measure."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import measure_get

    session = get_session_for_command(ctx)
    run_command(ctx, measure_get, model=session.model, table_name=table, measure_name=name)


@measure.command()
@click.argument("name")
@click.option("--expression", "-e", required=True, help="DAX expression (use - for stdin).")
@click.option("--table", "-t", required=True, help="Target table.")
@click.option("--format-string", default=None, help='Format string (e.g., "$#,##0").')
@click.option("--description", default=None, help="Measure description.")
@click.option("--folder", default=None, help="Display folder path.")
@click.option("--hidden", is_flag=True, default=False, help="Hide from client tools.")
@pass_context
def create(
    ctx: PbiContext,
    name: str,
    expression: str,
    table: str,
    format_string: str | None,
    description: str | None,
    folder: str | None,
    hidden: bool,
) -> None:
    """Create a new measure."""
    if expression == "-":
        expression = sys.stdin.read().strip()

    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import measure_create

    session = get_session_for_command(ctx)
    run_command(
        ctx,
        measure_create,
        model=session.model,
        table_name=table,
        name=name,
        expression=expression,
        format_string=format_string,
        description=description,
        display_folder=folder,
        is_hidden=hidden,
    )


@measure.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table containing the measure.")
@click.option("--expression", "-e", default=None, help="New DAX expression.")
@click.option("--format-string", default=None, help="New format string.")
@click.option("--description", default=None, help="New description.")
@click.option("--folder", default=None, help="New display folder.")
@pass_context
def update(
    ctx: PbiContext,
    name: str,
    table: str,
    expression: str | None,
    format_string: str | None,
    description: str | None,
    folder: str | None,
) -> None:
    """Update an existing measure."""
    if expression == "-":
        expression = sys.stdin.read().strip()

    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import measure_update

    session = get_session_for_command(ctx)
    run_command(
        ctx,
        measure_update,
        model=session.model,
        table_name=table,
        name=name,
        expression=expression,
        format_string=format_string,
        description=description,
        display_folder=folder,
    )


@measure.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table containing the measure.")
@pass_context
def delete(ctx: PbiContext, name: str, table: str) -> None:
    """Delete a measure."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import measure_delete

    session = get_session_for_command(ctx)
    run_command(ctx, measure_delete, model=session.model, table_name=table, name=name)


@measure.command()
@click.argument("old_name")
@click.argument("new_name")
@click.option("--table", "-t", required=True, help="Table containing the measure.")
@pass_context
def rename(ctx: PbiContext, old_name: str, new_name: str, table: str) -> None:
    """Rename a measure."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import measure_rename

    session = get_session_for_command(ctx)
    run_command(
        ctx,
        measure_rename,
        model=session.model,
        table_name=table,
        old_name=old_name,
        new_name=new_name,
    )


@measure.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Source table.")
@click.option("--to-table", required=True, help="Destination table.")
@pass_context
def move(ctx: PbiContext, name: str, table: str, to_table: str) -> None:
    """Move a measure to a different table."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import measure_move

    session = get_session_for_command(ctx)
    run_command(
        ctx,
        measure_move,
        model=session.model,
        table_name=table,
        name=name,
        dest_table_name=to_table,
    )
