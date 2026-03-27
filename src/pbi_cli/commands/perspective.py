"""Perspective management commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import run_command
from pbi_cli.main import PbiContext, pass_context


@click.group()
def perspective() -> None:
    """Manage model perspectives."""


@perspective.command(name="list")
@pass_context
def perspective_list(ctx: PbiContext) -> None:
    """List all perspectives."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import perspective_list as _perspective_list

    session = get_session_for_command(ctx)
    run_command(ctx, _perspective_list, model=session.model)


@perspective.command()
@click.argument("name")
@click.option("--description", default=None, help="Perspective description.")
@pass_context
def create(ctx: PbiContext, name: str, description: str | None) -> None:
    """Create a perspective."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import perspective_create

    session = get_session_for_command(ctx)
    run_command(ctx, perspective_create, model=session.model, name=name, description=description)


@perspective.command()
@click.argument("name")
@pass_context
def delete(ctx: PbiContext, name: str) -> None:
    """Delete a perspective."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import perspective_delete

    session = get_session_for_command(ctx)
    run_command(ctx, perspective_delete, model=session.model, name=name)
