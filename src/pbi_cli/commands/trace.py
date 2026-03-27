"""Diagnostic trace commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import run_command
from pbi_cli.main import PbiContext, pass_context


@click.group()
def trace() -> None:
    """Manage diagnostic traces."""


@trace.command()
@pass_context
def start(ctx: PbiContext) -> None:
    """Start a diagnostic trace."""
    from pbi_cli.core.session import get_session_for_command
    from pbi_cli.core.tom_backend import trace_start

    session = get_session_for_command(ctx)
    run_command(ctx, trace_start, server=session.server)


@trace.command()
@pass_context
def stop(ctx: PbiContext) -> None:
    """Stop the active trace."""
    from pbi_cli.core.tom_backend import trace_stop

    run_command(ctx, trace_stop)


@trace.command()
@pass_context
def fetch(ctx: PbiContext) -> None:
    """Fetch trace events."""
    from pbi_cli.core.tom_backend import trace_fetch

    run_command(ctx, trace_fetch)


@trace.command()
@click.argument("path", type=click.Path())
@pass_context
def export(ctx: PbiContext, path: str) -> None:
    """Export trace events to a file."""
    from pbi_cli.core.tom_backend import trace_export

    run_command(ctx, trace_export, path=path)
