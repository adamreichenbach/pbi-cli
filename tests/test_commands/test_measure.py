"""Tests for measure commands."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from click.testing import CliRunner

from pbi_cli.main import cli


def test_measure_list(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "measure", "list"])
    assert result.exit_code == 0
    assert "Total Sales" in result.output


def test_measure_list_with_table_filter(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "measure", "list", "--table", "Sales"])
    assert result.exit_code == 0


def test_measure_get(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(
        cli, ["--json", "measure", "get", "Total Sales", "--table", "Sales"]
    )
    assert result.exit_code == 0
    assert "Total Sales" in result.output


def test_measure_create(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(
        cli,
        ["--json", "measure", "create", "Revenue", "-e", "SUM(Sales[Revenue])", "-t", "Sales"],
    )
    assert result.exit_code == 0
    assert "created" in result.output


def test_measure_delete(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(
        cli, ["--json", "measure", "delete", "Total Sales", "-t", "Sales"]
    )
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_measure_rename(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(
        cli, ["--json", "measure", "rename", "Total Sales", "Revenue", "-t", "Sales"]
    )
    assert result.exit_code == 0
