"""Model-level operations."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import run_command
from pbi_cli.core.session import get_session_for_command
from pbi_cli.core.tom_backend import model_get, model_get_stats
from pbi_cli.main import PbiContext, pass_context


@click.group()
def model() -> None:
    """Manage the semantic model."""


@model.command()
@pass_context
def get(ctx: PbiContext) -> None:
    """Get model metadata."""
    session = get_session_for_command(ctx)
    run_command(ctx, model_get, model=session.model, database=session.database)


@model.command()
@pass_context
def stats(ctx: PbiContext) -> None:
    """Get model statistics."""
    session = get_session_for_command(ctx)
    run_command(ctx, model_get_stats, model=session.model)
