"""Security role management commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import run_command
from pbi_cli.main import PbiContext, pass_context


@click.group(name="security-role")
def security_role() -> None:
    """Manage security roles (RLS)."""


@security_role.command(name="list")
@pass_context
def role_list(ctx: PbiContext) -> None:
    """List all security roles."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import role_list as _role_list

    session = get_session_for_command(ctx)
    run_command(ctx, _role_list, model=session.model)


@security_role.command()
@click.argument("name")
@pass_context
def get(ctx: PbiContext, name: str) -> None:
    """Get details of a security role."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import role_get

    session = get_session_for_command(ctx)
    run_command(ctx, role_get, model=session.model, name=name)


@security_role.command()
@click.argument("name")
@click.option("--description", default=None, help="Role description.")
@pass_context
def create(ctx: PbiContext, name: str, description: str | None) -> None:
    """Create a new security role."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import role_create

    session = get_session_for_command(ctx)
    run_command(ctx, role_create, model=session.model, name=name, description=description)


@security_role.command()
@click.argument("name")
@pass_context
def delete(ctx: PbiContext, name: str) -> None:
    """Delete a security role."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import role_delete

    session = get_session_for_command(ctx)
    run_command(ctx, role_delete, model=session.model, name=name)
