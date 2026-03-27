"""Interactive REPL for pbi-cli with persistent session.

Keeps a direct .NET connection alive across commands so that
subsequent calls are near-instant (no reconnection overhead).

Usage:
    pbi repl
    pbi --json repl
"""

from __future__ import annotations

import platform
import shlex

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory

from pbi_cli.core.config import PBI_CLI_HOME, ensure_home_dir
from pbi_cli.core.output import print_error, print_info, print_warning
from pbi_cli.core.session import get_current_session

_QUIT_COMMANDS = frozenset({"exit", "quit", "q"})
_HISTORY_FILE = PBI_CLI_HOME / "repl_history"


class PbiRepl:
    """Interactive REPL that dispatches input to Click commands."""

    def __init__(
        self,
        json_output: bool = False,
        connection: str | None = None,
    ) -> None:
        self._json_output = json_output
        self._connection = connection

    def _build_completer(self) -> WordCompleter:
        """Build auto-completer from registered Click commands."""
        from pbi_cli.main import cli

        words: list[str] = []
        for name, cmd in cli.commands.items():
            words.append(name)
            if isinstance(cmd, click.Group):
                sub_names = cmd.list_commands(click.Context(cmd))
                for sub in sub_names:
                    words.append(f"{name} {sub}")
                    words.append(sub)
        return WordCompleter(words, ignore_case=True)

    def _get_prompt(self) -> str:
        """Dynamic prompt showing active connection name."""
        session = get_current_session()
        if session is not None:
            return f"pbi({session.connection_name})> "
        return "pbi> "

    def _execute_line(self, line: str) -> None:
        """Parse and execute a single command line."""
        from pbi_cli.main import PbiContext, cli

        stripped = line.strip()
        if not stripped:
            return
        if stripped.lower() in _QUIT_COMMANDS:
            raise EOFError

        # Tokenize -- posix=False on Windows to handle backslash paths
        is_posix = platform.system() != "Windows"
        try:
            tokens = shlex.split(stripped, posix=is_posix)
        except ValueError as e:
            print_error(f"Parse error: {e}")
            return

        # Strip leading "pbi" if user types full command out of habit
        if tokens and tokens[0] == "pbi":
            tokens = tokens[1:]
        if not tokens:
            return

        # Build a fresh Click context per invocation to avoid state leaking
        try:
            ctx = click.Context(cli, info_name="pbi")
            ctx.ensure_object(PbiContext)
            ctx.obj = PbiContext(
                json_output=self._json_output,
                connection=self._connection,
                repl_mode=True,
            )
            with ctx:
                cli.parse_args(ctx, list(tokens))
                cli.invoke(ctx)
        except SystemExit:
            # Click raises SystemExit on --help, bad args, etc.
            pass
        except click.ClickException as e:
            e.show()
        except click.Abort:
            print_warning("Aborted.")
        except KeyboardInterrupt:
            # Ctrl+C cancels current command, not the REPL
            pass
        except Exception as e:
            print_error(str(e))

    def run(self) -> None:
        """Main REPL loop."""
        ensure_home_dir()

        session: PromptSession[str] = PromptSession(
            history=FileHistory(str(_HISTORY_FILE)),
            completer=self._build_completer(),
        )

        print_info("pbi-cli interactive mode. Type 'exit' or Ctrl+D to quit.")

        try:
            while True:
                try:
                    line = session.prompt(self._get_prompt())
                    self._execute_line(line)
                except KeyboardInterrupt:
                    # Ctrl+C on empty prompt prints hint
                    print_info("Type 'exit' or press Ctrl+D to quit.")
                    continue
        except EOFError:
            pass
        finally:
            from pbi_cli.core.session import disconnect

            disconnect()

        print_info("Goodbye.")


def start_repl(
    json_output: bool = False,
    connection: str | None = None,
) -> None:
    """Entry point called by the ``pbi repl`` command."""
    repl = PbiRepl(json_output=json_output, connection=connection)
    repl.run()
