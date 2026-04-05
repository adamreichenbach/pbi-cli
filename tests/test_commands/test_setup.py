"""Tests for setup command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from pbi_cli.main import cli


def test_setup_info(cli_runner: CliRunner, tmp_config: Path) -> None:
    with patch("pbi_cli.core.dotnet_loader._dll_dir", return_value=tmp_config / "dlls"):
        result = cli_runner.invoke(cli, ["--json", "setup", "--info"])
    assert result.exit_code == 0
    assert "version" in result.output


def test_setup_verify_missing_pythonnet(cli_runner: CliRunner, tmp_config: Path) -> None:
    with (
        patch("pbi_cli.core.dotnet_loader._dll_dir", return_value=tmp_config / "dlls"),
        patch.dict("sys.modules", {"pythonnet": None}),
    ):
        result = cli_runner.invoke(cli, ["setup"])
    # Should fail because pythonnet is "missing" and dlls dir doesn't exist
    assert result.exit_code != 0


def test_setup_verify_success(cli_runner: CliRunner, tmp_config: Path) -> None:
    # Create fake DLL directory with required files
    dll_dir = tmp_config / "dlls"
    dll_dir.mkdir()
    (dll_dir / "Microsoft.AnalysisServices.Tabular.dll").write_text("fake")
    (dll_dir / "Microsoft.AnalysisServices.AdomdClient.dll").write_text("fake")

    with patch("pbi_cli.core.dotnet_loader._dll_dir", return_value=dll_dir):
        result = cli_runner.invoke(cli, ["--json", "setup"])
    assert result.exit_code == 0
    assert "ready" in result.output
