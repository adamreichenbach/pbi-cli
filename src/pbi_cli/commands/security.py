"""Security role management commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import build_definition, run_tool
from pbi_cli.main import PbiContext, pass_context


@click.group(name="security-role")
def security_role() -> None:
    """Manage security roles (RLS)."""


@security_role.command(name="list")
@pass_context
def role_list(ctx: PbiContext) -> None:
    """List all security roles."""
    run_tool(ctx, "security_role_operations", {"operation": "List"})


@security_role.command()
@click.argument("name")
@pass_context
def get(ctx: PbiContext, name: str) -> None:
    """Get details of a security role."""
    run_tool(ctx, "security_role_operations", {"operation": "Get", "name": name})


@security_role.command()
@click.argument("name")
@click.option("--description", default=None, help="Role description.")
@pass_context
def create(ctx: PbiContext, name: str, description: str | None) -> None:
    """Create a new security role."""
    definition = build_definition(
        required={"name": name},
        optional={"description": description},
    )
    run_tool(ctx, "security_role_operations", {"operation": "Create", "definitions": [definition]})


@security_role.command()
@click.argument("name")
@pass_context
def delete(ctx: PbiContext, name: str) -> None:
    """Delete a security role."""
    run_tool(ctx, "security_role_operations", {"operation": "Delete", "name": name})


@security_role.command(name="export-tmdl")
@click.argument("name")
@pass_context
def export_tmdl(ctx: PbiContext, name: str) -> None:
    """Export a security role as TMDL."""
    run_tool(ctx, "security_role_operations", {"operation": "ExportTMDL", "name": name})
