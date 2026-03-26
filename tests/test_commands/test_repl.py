"""Tests for REPL functionality (non-interactive parts)."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from pbi_cli.main import cli
from pbi_cli.utils.repl import PbiRepl


def test_repl_command_exists(cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(cli, ["repl", "--help"])
    assert result.exit_code == 0
    assert "interactive REPL" in result.output


def test_repl_build_completer() -> None:
    repl = PbiRepl()
    completer = repl._build_completer()
    # Should contain known commands
    assert "measure" in completer.words
    assert "dax" in completer.words
    assert "connect" in completer.words
    assert "repl" in completer.words


def test_repl_get_prompt_no_connection(tmp_connections: Path) -> None:
    repl = PbiRepl()
    prompt = repl._get_prompt()
    assert prompt == "pbi> "


def test_repl_get_prompt_with_connection(tmp_connections: Path) -> None:
    from pbi_cli.core.connection_store import (
        ConnectionInfo,
        ConnectionStore,
        add_connection,
        save_connections,
    )

    store = add_connection(
        ConnectionStore(),
        ConnectionInfo(name="test-conn", data_source="localhost"),
    )
    save_connections(store)

    repl = PbiRepl()
    prompt = repl._get_prompt()
    assert prompt == "pbi(test-conn)> "


def test_repl_execute_line_empty() -> None:
    repl = PbiRepl()
    # Should not raise
    repl._execute_line("")
    repl._execute_line("   ")


def test_repl_execute_line_exit() -> None:
    repl = PbiRepl()
    import pytest
    with pytest.raises(EOFError):
        repl._execute_line("exit")


def test_repl_execute_line_quit() -> None:
    repl = PbiRepl()
    import pytest
    with pytest.raises(EOFError):
        repl._execute_line("quit")


def test_repl_execute_line_strips_pbi_prefix(
    monkeypatch: pytest.MonkeyPatch,
    tmp_connections: Path,
) -> None:
    from tests.conftest import MockPbiMcpClient

    mock = MockPbiMcpClient()
    factory = lambda repl_mode=False: mock  # noqa: E731
    monkeypatch.setattr("pbi_cli.commands._helpers.get_client", factory)

    repl = PbiRepl(json_output=True)
    # "pbi measure list" should work like "measure list"
    repl._execute_line("pbi --json measure list")


def test_repl_execute_line_help() -> None:
    repl = PbiRepl()
    # --help should not crash the REPL (Click raises SystemExit)
    repl._execute_line("--help")
