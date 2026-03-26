"""Transaction management commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import run_tool
from pbi_cli.main import PbiContext, pass_context


@click.group()
def transaction() -> None:
    """Manage explicit transactions."""


@transaction.command()
@pass_context
def begin(ctx: PbiContext) -> None:
    """Begin a new transaction."""
    run_tool(ctx, "transaction_operations", {"operation": "Begin"})


@transaction.command()
@click.argument("transaction_id", default="")
@pass_context
def commit(ctx: PbiContext, transaction_id: str) -> None:
    """Commit the active or specified transaction."""
    request: dict[str, object] = {"operation": "Commit"}
    if transaction_id:
        request["transactionId"] = transaction_id
    run_tool(ctx, "transaction_operations", request)


@transaction.command()
@click.argument("transaction_id", default="")
@pass_context
def rollback(ctx: PbiContext, transaction_id: str) -> None:
    """Rollback the active or specified transaction."""
    request: dict[str, object] = {"operation": "Rollback"}
    if transaction_id:
        request["transactionId"] = transaction_id
    run_tool(ctx, "transaction_operations", request)
