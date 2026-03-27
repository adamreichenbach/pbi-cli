"""REPL command -- starts an interactive pbi-cli session."""

from __future__ import annotations

import click

from pbi_cli.main import PbiContext, pass_context


@click.command()
@pass_context
def repl(ctx: PbiContext) -> None:
    """Start an interactive REPL session.

    Keeps a persistent .NET connection alive across commands for
    near-instant execution. Type 'exit' or press Ctrl+D to quit.
    """
    from pbi_cli.utils.repl import start_repl

    start_repl(json_output=ctx.json_output, connection=ctx.connection)
