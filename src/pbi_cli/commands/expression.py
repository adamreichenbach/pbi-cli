"""Named expression and parameter commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import run_command
from pbi_cli.main import PbiContext, pass_context


@click.group()
def expression() -> None:
    """Manage named expressions and parameters."""


@expression.command(name="list")
@pass_context
def expression_list(ctx: PbiContext) -> None:
    """List all named expressions."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import expression_list as _expression_list

    session = get_session_for_command(ctx)
    run_command(ctx, _expression_list, model=session.model)


@expression.command()
@click.argument("name")
@pass_context
def get(ctx: PbiContext, name: str) -> None:
    """Get a named expression."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import expression_get

    session = get_session_for_command(ctx)
    run_command(ctx, expression_get, model=session.model, name=name)


@expression.command()
@click.argument("name")
@click.option("--expression", "-e", "expr", required=True, help="M expression.")
@click.option("--description", default=None, help="Expression description.")
@pass_context
def create(ctx: PbiContext, name: str, expr: str, description: str | None) -> None:
    """Create a named expression."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import expression_create

    session = get_session_for_command(ctx)
    run_command(
        ctx,
        expression_create,
        model=session.model,
        name=name,
        expression=expr,
        description=description,
    )


@expression.command()
@click.argument("name")
@pass_context
def delete(ctx: PbiContext, name: str) -> None:
    """Delete a named expression."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import expression_delete

    session = get_session_for_command(ctx)
    run_command(ctx, expression_delete, model=session.model, name=name)
