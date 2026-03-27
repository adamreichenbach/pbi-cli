"""Tests for remaining command groups to boost coverage."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from click.testing import CliRunner

from pbi_cli.main import cli


def test_column_list(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "column", "list", "--table", "Sales"])
    assert result.exit_code == 0


def test_relationship_list(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "relationship", "list"])
    assert result.exit_code == 0


def test_database_list(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "database", "list"])
    assert result.exit_code == 0


def test_security_role_list(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "security-role", "list"])
    assert result.exit_code == 0


def test_calc_group_list(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "calc-group", "list"])
    assert result.exit_code == 0


def test_partition_list(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "partition", "list", "--table", "Sales"])
    assert result.exit_code == 0


def test_perspective_list(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "perspective", "list"])
    assert result.exit_code == 0


def test_hierarchy_list(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "hierarchy", "list"])
    assert result.exit_code == 0


def test_expression_list(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "expression", "list"])
    assert result.exit_code == 0


def test_calendar_list(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "calendar", "list"])
    assert result.exit_code == 0


def test_trace_start(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "trace", "start"])
    assert result.exit_code == 0


def test_transaction_begin(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "transaction", "begin"])
    assert result.exit_code == 0


def test_transaction_commit(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "transaction", "commit"])
    assert result.exit_code == 0


def test_transaction_rollback(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "transaction", "rollback"])
    assert result.exit_code == 0


def test_advanced_culture_list(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "advanced", "culture", "list"])
    assert result.exit_code == 0
