"""Entry point for the pbi-cli management command."""

from __future__ import annotations

import click

from pbi_cli import __version__


@click.group()
@click.version_option(version=__version__, prog_name="pbi-cli")
def cli() -> None:
    """pbi-cli: CLI management tool for pbi-cli-tool.

    Use this command to set up Claude Code integration before using 'pbi'.

    Typical first-time setup:

    \b
        pipx install pbi-cli-tool
        pbi-cli skills install
        pbi connect
    """


def _register_commands() -> None:
    from pbi_cli.commands.skills_cmd import skills

    cli.add_command(skills)


_register_commands()
