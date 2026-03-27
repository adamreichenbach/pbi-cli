"""Tests for DAX commands."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

from click.testing import CliRunner

from pbi_cli.main import cli


def _mock_execute_dax(**kwargs: Any) -> dict:
    return {"columns": ["Amount"], "rows": [{"Amount": 42}]}


def _mock_validate_dax(**kwargs: Any) -> dict:
    return {"valid": True, "query": kwargs.get("query", "")}


def _mock_clear_cache(**kwargs: Any) -> dict:
    return {"status": "cache_cleared"}


def test_dax_execute(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    with patch("pbi_cli.core.adomd_backend.execute_dax", side_effect=_mock_execute_dax):
        result = cli_runner.invoke(cli, ["--json", "dax", "execute", "EVALUATE Sales"])
    assert result.exit_code == 0
    assert "42" in result.output


def test_dax_execute_from_file(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
    tmp_path: Path,
) -> None:
    query_file = tmp_path / "query.dax"
    query_file.write_text("EVALUATE Sales", encoding="utf-8")

    with patch("pbi_cli.core.adomd_backend.execute_dax", side_effect=_mock_execute_dax):
        result = cli_runner.invoke(cli, ["--json", "dax", "execute", "--file", str(query_file)])
    assert result.exit_code == 0


def test_dax_execute_no_query(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    result = cli_runner.invoke(cli, ["dax", "execute"])
    assert result.exit_code != 0


def test_dax_validate(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    with patch("pbi_cli.core.adomd_backend.validate_dax", side_effect=_mock_validate_dax):
        result = cli_runner.invoke(cli, ["--json", "dax", "validate", "EVALUATE Sales"])
    assert result.exit_code == 0
    assert "valid" in result.output


def test_dax_clear_cache(
    cli_runner: CliRunner,
    patch_session: Any,
    tmp_connections: Path,
) -> None:
    with patch("pbi_cli.core.adomd_backend.clear_cache", side_effect=_mock_clear_cache):
        result = cli_runner.invoke(cli, ["--json", "dax", "clear-cache"])
    assert result.exit_code == 0
