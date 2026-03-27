"""Tests for pbi_cli.core.errors."""

from __future__ import annotations

import click

from pbi_cli.core.errors import (
    ConnectionRequiredError,
    DotNetNotFoundError,
    PbiCliError,
    TomError,
)


def test_pbi_cli_error_is_click_exception() -> None:
    err = PbiCliError("test message")
    assert isinstance(err, click.ClickException)
    assert err.format_message() == "test message"


def test_dotnet_not_found_default_message() -> None:
    err = DotNetNotFoundError()
    assert "pythonnet" in err.format_message()


def test_connection_required_default_message() -> None:
    err = ConnectionRequiredError()
    assert "pbi connect" in err.format_message()


def test_tom_error_includes_operation() -> None:
    err = TomError("measure_list", "not found")
    assert "measure_list" in err.format_message()
    assert "not found" in err.format_message()
    assert err.operation == "measure_list"
    assert err.detail == "not found"
