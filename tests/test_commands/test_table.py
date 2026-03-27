"""Tests for table commands."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from click.testing import CliRunner

from pbi_cli.main import cli


def test_table_list(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "table", "list"])
    assert result.exit_code == 0
    assert "Sales" in result.output


def test_table_get(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "table", "get", "Sales"])
    assert result.exit_code == 0


def test_table_delete(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "table", "delete", "Sales"])
    assert result.exit_code == 0
    assert "deleted" in result.output
