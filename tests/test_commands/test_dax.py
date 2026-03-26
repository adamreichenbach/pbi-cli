"""Tests for DAX commands."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from pbi_cli.main import cli
from tests.conftest import MockPbiMcpClient


def test_dax_execute(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "dax", "execute", "EVALUATE Sales"])
    assert result.exit_code == 0
    assert "42" in result.output


def test_dax_execute_from_file(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
    tmp_path: Path,
) -> None:
    query_file = tmp_path / "query.dax"
    query_file.write_text("EVALUATE Sales", encoding="utf-8")

    result = cli_runner.invoke(
        cli, ["--json", "dax", "execute", "--file", str(query_file)]
    )
    assert result.exit_code == 0


def test_dax_execute_no_query(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["dax", "execute"])
    assert result.exit_code != 0


def test_dax_validate(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(
        cli, ["--json", "dax", "validate", "EVALUATE Sales"]
    )
    assert result.exit_code == 0
    assert "isValid" in result.output


def test_dax_clear_cache(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "dax", "clear-cache"])
    assert result.exit_code == 0
