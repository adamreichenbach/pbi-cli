"""Tests for model commands."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from pbi_cli.main import cli
from tests.conftest import MockPbiMcpClient


def test_model_get(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "model", "get"])
    assert result.exit_code == 0
    assert "My Model" in result.output


def test_model_stats(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "model", "stats"])
    assert result.exit_code == 0


def test_model_refresh(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "model", "refresh"])
    assert result.exit_code == 0
