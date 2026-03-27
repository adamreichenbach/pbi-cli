"""Tests for REPL functionality (non-interactive parts)."""

from __future__ import annotations

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


def test_repl_get_prompt_no_connection() -> None:
    repl = PbiRepl()
    prompt = repl._get_prompt()
    assert prompt == "pbi> "


def test_repl_get_prompt_with_session(monkeypatch: pytest.MonkeyPatch) -> None:
    from tests.conftest import build_mock_session

    session = build_mock_session()
    monkeypatch.setattr("pbi_cli.core.session._current_session", session)

    repl = PbiRepl()
    prompt = repl._get_prompt()
    assert "test-conn" in prompt

    # Clean up
    monkeypatch.setattr("pbi_cli.core.session._current_session", None)


def test_repl_execute_line_empty() -> None:
    repl = PbiRepl()
    # Should not raise
    repl._execute_line("")
    repl._execute_line("   ")


def test_repl_execute_line_exit() -> None:
    repl = PbiRepl()
    with pytest.raises(EOFError):
        repl._execute_line("exit")


def test_repl_execute_line_quit() -> None:
    repl = PbiRepl()
    with pytest.raises(EOFError):
        repl._execute_line("quit")


def test_repl_execute_line_help() -> None:
    repl = PbiRepl()
    # --help should not crash the REPL (Click raises SystemExit)
    repl._execute_line("--help")
