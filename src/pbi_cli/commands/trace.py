"""Diagnostic trace commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import run_tool
from pbi_cli.main import PbiContext, pass_context


@click.group()
def trace() -> None:
    """Manage diagnostic traces."""


@trace.command()
@pass_context
def start(ctx: PbiContext) -> None:
    """Start a diagnostic trace."""
    run_tool(ctx, "trace_operations", {"operation": "Start"})


@trace.command()
@pass_context
def stop(ctx: PbiContext) -> None:
    """Stop the active trace."""
    run_tool(ctx, "trace_operations", {"operation": "Stop"})


@trace.command()
@pass_context
def fetch(ctx: PbiContext) -> None:
    """Fetch trace events."""
    run_tool(ctx, "trace_operations", {"operation": "Fetch"})


@trace.command()
@click.argument("path", type=click.Path())
@pass_context
def export(ctx: PbiContext, path: str) -> None:
    """Export trace events to a file."""
    run_tool(ctx, "trace_operations", {"operation": "Export", "filePath": path})
