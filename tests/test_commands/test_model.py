"""Tests for model commands."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from click.testing import CliRunner

from pbi_cli.main import cli


def test_model_get(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "model", "get"])
    assert result.exit_code == 0
    assert "TestModel" in result.output


def test_model_stats(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["--json", "model", "stats"])
    assert result.exit_code == 0
