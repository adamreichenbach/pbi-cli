"""Tests for setup command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from pbi_cli.main import cli


def test_setup_info(cli_runner: CliRunner, tmp_config: Path) -> None:
    fake_info = {
        "binary_path": "/test/binary",
        "version": "0.4.0",
        "platform": "win32-x64",
        "source": "managed",
    }
    with patch("pbi_cli.commands.setup_cmd.get_binary_info", return_value=fake_info):
        result = cli_runner.invoke(cli, ["--json", "setup", "--info"])
        assert result.exit_code == 0
        assert "0.4.0" in result.output


def test_setup_check(cli_runner: CliRunner, tmp_config: Path) -> None:
    with patch(
        "pbi_cli.commands.setup_cmd.check_for_updates",
        return_value=("0.3.0", "0.4.0", True),
    ):
        result = cli_runner.invoke(cli, ["--json", "setup", "--check"])
        assert result.exit_code == 0
        assert "0.4.0" in result.output


def test_setup_check_up_to_date(cli_runner: CliRunner, tmp_config: Path) -> None:
    with patch(
        "pbi_cli.commands.setup_cmd.check_for_updates",
        return_value=("0.4.0", "0.4.0", False),
    ):
        result = cli_runner.invoke(cli, ["setup", "--check"])
        assert result.exit_code == 0
