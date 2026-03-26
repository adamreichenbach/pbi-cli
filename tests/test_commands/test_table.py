"""Tests for table commands."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from pbi_cli.main import cli
from tests.conftest import MockPbiMcpClient


def test_table_list(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "table", "list"])
    assert result.exit_code == 0
    assert "Sales" in result.output


def test_table_get(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "table", "get", "Sales"])
    assert result.exit_code == 0


def test_table_create(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, [
        "--json", "table", "create", "NewTable", "--mode", "Import",
    ])
    assert result.exit_code == 0


def test_table_delete(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "table", "delete", "OldTable"])
    assert result.exit_code == 0


def test_table_refresh(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "table", "refresh", "Sales"])
    assert result.exit_code == 0
