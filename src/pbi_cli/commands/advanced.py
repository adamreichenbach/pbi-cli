"""Less common operations: culture, translation."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import run_command
from pbi_cli.main import PbiContext, pass_context


@click.group()
def advanced() -> None:
    """Advanced operations: cultures, translations."""


# --- Culture ---


@advanced.group()
def culture() -> None:
    """Manage model cultures (locales)."""


@culture.command(name="list")
@pass_context
def culture_list(ctx: PbiContext) -> None:
    """List cultures."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import culture_list as _culture_list

    session = get_session_for_command(ctx)
    run_command(ctx, _culture_list, model=session.model)


@culture.command()
@click.argument("name")
@pass_context
def culture_create(ctx: PbiContext, name: str) -> None:
    """Create a culture."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import culture_create as _culture_create

    session = get_session_for_command(ctx)
    run_command(ctx, _culture_create, model=session.model, name=name)


@culture.command(name="delete")
@click.argument("name")
@pass_context
def culture_delete(ctx: PbiContext, name: str) -> None:
    """Delete a culture."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import culture_delete as _culture_delete

    session = get_session_for_command(ctx)
    run_command(ctx, _culture_delete, model=session.model, name=name)
