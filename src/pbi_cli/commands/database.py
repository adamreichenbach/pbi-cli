"""Database-level operations: list, TMDL import/export, TMSL export."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import run_command
from pbi_cli.main import PbiContext, pass_context


@click.group()
def database() -> None:
    """Manage semantic models (databases) at the top level."""


@database.command(name="list")
@pass_context
def database_list(ctx: PbiContext) -> None:
    """List all databases on the connected server."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import database_list as _database_list

    session = get_session_for_command(ctx)
    run_command(ctx, _database_list, server=session.server)


@database.command(name="import-tmdl")
@click.argument("folder_path", type=click.Path(exists=True))
@pass_context
def import_tmdl(ctx: PbiContext, folder_path: str) -> None:
    """Import a model from a TMDL folder."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import import_tmdl as _import_tmdl

    session = get_session_for_command(ctx)
    run_command(ctx, _import_tmdl, server=session.server, folder_path=folder_path)


@database.command(name="export-tmdl")
@click.argument("folder_path", type=click.Path())
@pass_context
def export_tmdl(ctx: PbiContext, folder_path: str) -> None:
    """Export the model to a TMDL folder."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import export_tmdl as _export_tmdl

    session = get_session_for_command(ctx)
    run_command(ctx, _export_tmdl, database=session.database, folder_path=folder_path)


@database.command(name="export-tmsl")
@pass_context
def export_tmsl(ctx: PbiContext) -> None:
    """Export the model as TMSL."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import export_tmsl as _export_tmsl

    session = get_session_for_command(ctx)
    run_command(ctx, _export_tmsl, database=session.database)
