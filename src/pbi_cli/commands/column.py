"""Column CRUD commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import run_command
from pbi_cli.main import PbiContext, pass_context


@click.group()
def column() -> None:
    """Manage columns in a semantic model."""


@column.command(name="list")
@click.option("--table", "-t", required=True, help="Table name.")
@pass_context
def column_list(ctx: PbiContext, table: str) -> None:
    """List all columns in a table."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import column_list as _column_list

    session = get_session_for_command(ctx)
    run_command(ctx, _column_list, model=session.model, table_name=table)


@column.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table name.")
@pass_context
def get(ctx: PbiContext, name: str, table: str) -> None:
    """Get details of a specific column."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import column_get

    session = get_session_for_command(ctx)
    run_command(ctx, column_get, model=session.model, table_name=table, column_name=name)


@column.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table name.")
@click.option(
    "--data-type", required=True, help="Data type (string, int64, double, datetime, etc.)."
)
@click.option("--source-column", default=None, help="Source column name (for Import mode).")
@click.option("--expression", default=None, help="DAX expression (for calculated columns).")
@click.option("--format-string", default=None, help="Format string.")
@click.option("--description", default=None, help="Column description.")
@click.option("--folder", default=None, help="Display folder.")
@click.option("--hidden", is_flag=True, default=False, help="Hide from client tools.")
@click.option("--is-key", is_flag=True, default=False, help="Mark as key column.")
@pass_context
def create(
    ctx: PbiContext,
    name: str,
    table: str,
    data_type: str,
    source_column: str | None,
    expression: str | None,
    format_string: str | None,
    description: str | None,
    folder: str | None,
    hidden: bool,
    is_key: bool,
) -> None:
    """Create a new column."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import column_create

    session = get_session_for_command(ctx)
    run_command(
        ctx,
        column_create,
        model=session.model,
        table_name=table,
        name=name,
        data_type=data_type,
        source_column=source_column,
        expression=expression,
        format_string=format_string,
        description=description,
        display_folder=folder,
        is_hidden=hidden,
        is_key=is_key,
    )


@column.command()
@click.argument("name")
@click.option("--table", "-t", required=True, help="Table name.")
@pass_context
def delete(ctx: PbiContext, name: str, table: str) -> None:
    """Delete a column."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import column_delete

    session = get_session_for_command(ctx)
    run_command(ctx, column_delete, model=session.model, table_name=table, column_name=name)


@column.command()
@click.argument("old_name")
@click.argument("new_name")
@click.option("--table", "-t", required=True, help="Table name.")
@pass_context
def rename(ctx: PbiContext, old_name: str, new_name: str, table: str) -> None:
    """Rename a column."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import column_rename

    session = get_session_for_command(ctx)
    run_command(
        ctx,
        column_rename,
        model=session.model,
        table_name=table,
        old_name=old_name,
        new_name=new_name,
    )
