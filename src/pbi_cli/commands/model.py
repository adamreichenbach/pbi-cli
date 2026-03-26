"""Model-level operations."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import run_tool
from pbi_cli.main import PbiContext, pass_context


@click.group()
def model() -> None:
    """Manage the semantic model."""


@model.command()
@pass_context
def get(ctx: PbiContext) -> None:
    """Get model metadata."""
    run_tool(ctx, "model_operations", {"operation": "Get"})


@model.command()
@pass_context
def stats(ctx: PbiContext) -> None:
    """Get model statistics."""
    run_tool(ctx, "model_operations", {"operation": "GetStats"})


@model.command()
@click.option(
    "--type", "refresh_type",
    type=click.Choice(["Automatic", "Full", "Calculate", "DataOnly", "Defragment"]),
    default="Automatic", help="Refresh type.",
)
@pass_context
def refresh(ctx: PbiContext, refresh_type: str) -> None:
    """Refresh the model."""
    run_tool(ctx, "model_operations", {"operation": "Refresh", "refreshType": refresh_type})


@model.command()
@click.argument("new_name")
@pass_context
def rename(ctx: PbiContext, new_name: str) -> None:
    """Rename the model."""
    run_tool(ctx, "model_operations", {"operation": "Rename", "newName": new_name})


@model.command(name="export-tmdl")
@pass_context
def export_tmdl(ctx: PbiContext) -> None:
    """Export the model as TMDL."""
    run_tool(ctx, "model_operations", {"operation": "ExportTMDL"})
