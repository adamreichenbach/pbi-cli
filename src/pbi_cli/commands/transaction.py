"""Transaction management commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import run_command
from pbi_cli.main import PbiContext, pass_context


@click.group()
def transaction() -> None:
    """Manage explicit transactions."""


@transaction.command()
@pass_context
def begin(ctx: PbiContext) -> None:
    """Begin a new transaction."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import transaction_begin

    session = get_session_for_command(ctx)
    run_command(ctx, transaction_begin, server=session.server)


@transaction.command()
@click.argument("transaction_id", default="")
@pass_context
def commit(ctx: PbiContext, transaction_id: str) -> None:
    """Commit the active or specified transaction."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import transaction_commit

    session = get_session_for_command(ctx)
    run_command(ctx, transaction_commit, server=session.server, transaction_id=transaction_id)


@transaction.command()
@click.argument("transaction_id", default="")
@pass_context
def rollback(ctx: PbiContext, transaction_id: str) -> None:
    """Rollback the active or specified transaction."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import transaction_rollback

    session = get_session_for_command(ctx)
    run_command(ctx, transaction_rollback, server=session.server, transaction_id=transaction_id)
