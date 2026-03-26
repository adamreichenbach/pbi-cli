"""Tests for connection commands."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from pbi_cli.main import cli
from tests.conftest import MockPbiMcpClient


def test_connect_success(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["connect", "-d", "localhost:54321"])
    assert result.exit_code == 0
    assert len(patch_get_client.calls) == 1
    assert patch_get_client.calls[0][0] == "connection_operations"


def test_connect_json_output(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "connect", "-d", "localhost:54321"])
    assert result.exit_code == 0
    assert "connected" in result.output


def test_connect_fabric(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["connect-fabric", "-w", "My Workspace", "-m", "My Model"])
    assert result.exit_code == 0
    assert patch_get_client.calls[0][1]["operation"] == "ConnectFabric"


def test_disconnect(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    # First connect, then disconnect
    cli_runner.invoke(cli, ["connect", "-d", "localhost:54321"])
    result = cli_runner.invoke(cli, ["disconnect"])
    assert result.exit_code == 0


def test_disconnect_no_active_connection(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["disconnect"])
    assert result.exit_code != 0


def test_connections_list_empty(
    cli_runner: CliRunner,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["connections", "list"])
    assert result.exit_code == 0


def test_connections_list_json(
    cli_runner: CliRunner,
    patch_get_client: MockPbiMcpClient,
    tmp_connections: Path,
) -> None:
    cli_runner.invoke(cli, ["connect", "-d", "localhost:54321"])
    result = cli_runner.invoke(cli, ["--json", "connections", "list"])
    assert result.exit_code == 0
    assert "localhost" in result.output
