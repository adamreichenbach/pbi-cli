"""Tests for pbi_cli.commands._helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from pbi_cli.commands._helpers import build_definition, run_tool
from pbi_cli.core.errors import McpToolError
from pbi_cli.main import PbiContext
from tests.conftest import MockPbiMcpClient


def test_build_definition_required_only() -> None:
    result = build_definition(
        required={"name": "Sales"},
        optional={},
    )
    assert result == {"name": "Sales"}


def test_build_definition_filters_none() -> None:
    result = build_definition(
        required={"name": "Sales"},
        optional={"description": None, "folder": "Finance"},
    )
    assert result == {"name": "Sales", "folder": "Finance"}
    assert "description" not in result


def test_build_definition_preserves_falsy_non_none() -> None:
    result = build_definition(
        required={"name": "Sales"},
        optional={"hidden": False, "count": 0, "label": ""},
    )
    assert result["hidden"] is False
    assert result["count"] == 0
    assert result["label"] == ""


def test_run_tool_adds_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    mock = MockPbiMcpClient()
    monkeypatch.setattr("pbi_cli.commands._helpers.get_client", lambda repl_mode=False: mock)

    ctx = PbiContext(json_output=True, connection="my-conn")
    run_tool(ctx, "measure_operations", {"operation": "List"})

    assert mock.calls[0][1]["connectionName"] == "my-conn"


def test_run_tool_no_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    mock = MockPbiMcpClient()
    monkeypatch.setattr("pbi_cli.commands._helpers.get_client", lambda repl_mode=False: mock)

    ctx = PbiContext(json_output=True)
    run_tool(ctx, "measure_operations", {"operation": "List"})

    assert "connectionName" not in mock.calls[0][1]


def test_run_tool_stops_client_in_oneshot(monkeypatch: pytest.MonkeyPatch) -> None:
    mock = MockPbiMcpClient()
    monkeypatch.setattr("pbi_cli.commands._helpers.get_client", lambda repl_mode=False: mock)

    ctx = PbiContext(json_output=True, repl_mode=False)
    run_tool(ctx, "measure_operations", {"operation": "List"})

    assert mock.stopped is True


def test_run_tool_keeps_client_in_repl(monkeypatch: pytest.MonkeyPatch) -> None:
    mock = MockPbiMcpClient()
    monkeypatch.setattr("pbi_cli.commands._helpers.get_client", lambda repl_mode=False: mock)

    ctx = PbiContext(json_output=True, repl_mode=True)
    run_tool(ctx, "measure_operations", {"operation": "List"})

    assert mock.stopped is False


def test_run_tool_raises_mcp_tool_error_on_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingClient(MockPbiMcpClient):
        def call_tool(self, tool_name: str, request: dict) -> None:
            raise RuntimeError("server crashed")

    mock = FailingClient()
    monkeypatch.setattr("pbi_cli.commands._helpers.get_client", lambda repl_mode=False: mock)

    ctx = PbiContext(json_output=True)
    with pytest.raises(McpToolError):
        run_tool(ctx, "measure_operations", {"operation": "List"})
