"""Database-level operations: list, TMDL import/export, Fabric deploy."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import run_tool
from pbi_cli.main import PbiContext, pass_context


@click.group()
def database() -> None:
    """Manage semantic models (databases) at the top level."""


@database.command(name="list")
@pass_context
def database_list(ctx: PbiContext) -> None:
    """List all databases on the connected server."""
    run_tool(ctx, "database_operations", {"operation": "List"})


@database.command(name="import-tmdl")
@click.argument("folder_path", type=click.Path(exists=True))
@pass_context
def import_tmdl(ctx: PbiContext, folder_path: str) -> None:
    """Import a model from a TMDL folder."""
    run_tool(
        ctx,
        "database_operations",
        {
            "operation": "ImportFromTmdlFolder",
            "tmdlFolderPath": folder_path,
        },
    )


@database.command(name="export-tmdl")
@click.argument("folder_path", type=click.Path())
@pass_context
def export_tmdl(ctx: PbiContext, folder_path: str) -> None:
    """Export the model to a TMDL folder."""
    run_tool(
        ctx,
        "database_operations",
        {
            "operation": "ExportToTmdlFolder",
            "tmdlFolderPath": folder_path,
        },
    )


@database.command(name="export-tmsl")
@pass_context
def export_tmsl(ctx: PbiContext) -> None:
    """Export the model as TMSL."""
    run_tool(ctx, "database_operations", {"operation": "ExportTMSL"})


@database.command()
@click.option("--workspace", "-w", required=True, help="Target Fabric workspace name.")
@click.option("--new-name", default=None, help="New database name in target workspace.")
@click.option("--tenant", default=None, help="Tenant name for B2B scenarios.")
@pass_context
def deploy(ctx: PbiContext, workspace: str, new_name: str | None, tenant: str | None) -> None:
    """Deploy the model to a Fabric workspace."""
    deploy_request: dict[str, object] = {"targetWorkspaceName": workspace}
    if new_name:
        deploy_request["newDatabaseName"] = new_name
    if tenant:
        deploy_request["targetTenantName"] = tenant

    run_tool(
        ctx,
        "database_operations",
        {
            "operation": "DeployToFabric",
            "deployToFabricRequest": deploy_request,
        },
    )
