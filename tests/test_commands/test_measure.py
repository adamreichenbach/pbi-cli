"""Tests for measure commands."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from pbi_cli.main import cli
from tests.conftest import MockPbiMcpClient


def test_measure_list(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "measure", "list"])
    assert result.exit_code == 0
    assert "Total Sales" in result.output


def test_measure_list_with_table_filter(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(
        cli, ["--json", "measure", "list", "--table", "Sales"]
    )
    assert result.exit_code == 0


def test_measure_get(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(
        cli, ["--json", "measure", "get", "Total Sales", "--table", "Sales"]
    )
    assert result.exit_code == 0
    assert "Total Sales" in result.output


def test_measure_create(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, [
        "--json", "measure", "create", "Revenue",
        "-e", "SUM(Sales[Revenue])",
        "-t", "Sales",
    ])
    assert result.exit_code == 0


def test_measure_update(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, [
        "--json", "measure", "update", "Revenue",
        "-t", "Sales",
        "-e", "SUM(Sales[Amount])",
    ])
    assert result.exit_code == 0


def test_measure_delete(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, [
        "--json", "measure", "delete", "Revenue", "-t", "Sales",
    ])
    assert result.exit_code == 0


def test_measure_rename(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, [
        "--json", "measure", "rename", "OldName", "NewName", "-t", "Sales",
    ])
    assert result.exit_code == 0


def test_measure_move(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, [
        "--json", "measure", "move", "Revenue",
        "-t", "Sales",
        "--to-table", "Finance",
    ])
    assert result.exit_code == 0
