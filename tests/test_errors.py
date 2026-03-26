"""Tests for pbi_cli.core.errors."""

from __future__ import annotations

import click

from pbi_cli.core.errors import (
    BinaryNotFoundError,
    ConnectionRequiredError,
    McpToolError,
    PbiCliError,
)


def test_pbi_cli_error_is_click_exception() -> None:
    err = PbiCliError("test message")
    assert isinstance(err, click.ClickException)
    assert err.format_message() == "test message"


def test_binary_not_found_default_message() -> None:
    err = BinaryNotFoundError()
    assert "pbi connect" in err.format_message()


def test_connection_required_default_message() -> None:
    err = ConnectionRequiredError()
    assert "pbi connect" in err.format_message()


def test_mcp_tool_error_includes_tool_name() -> None:
    err = McpToolError("measure_operations", "not found")
    assert "measure_operations" in err.format_message()
    assert "not found" in err.format_message()
    assert err.tool_name == "measure_operations"
    assert err.detail == "not found"
