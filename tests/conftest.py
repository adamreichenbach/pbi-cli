"""Shared test fixtures for pbi-cli."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

# ---------------------------------------------------------------------------
# Canned MCP responses used by the mock client
# ---------------------------------------------------------------------------

CANNED_RESPONSES: dict[str, dict[str, Any]] = {
    "connection_operations": {
        "Connect": {"status": "connected", "connectionName": "test-conn"},
        "ConnectFabric": {"status": "connected", "connectionName": "ws/model"},
        "Disconnect": {"status": "disconnected"},
    },
    "dax_query_operations": {
        "Execute": {"columns": ["Amount"], "rows": [{"Amount": 42}]},
        "Validate": {"isValid": True},
        "ClearCache": {"status": "cleared"},
    },
    "measure_operations": {
        "List": [
            {"name": "Total Sales", "expression": "SUM(Sales[Amount])", "tableName": "Sales"},
        ],
        "Get": {"name": "Total Sales", "expression": "SUM(Sales[Amount])"},
        "Create": {"status": "created"},
        "Update": {"status": "updated"},
        "Delete": {"status": "deleted"},
        "Rename": {"status": "renamed"},
        "Move": {"status": "moved"},
        "ExportTMDL": "measure 'Total Sales'\n  expression = SUM(Sales[Amount])",
    },
    "table_operations": {
        "List": [{"name": "Sales", "mode": "Import"}],
        "Get": {"name": "Sales", "mode": "Import", "columns": []},
        "Create": {"status": "created"},
        "Delete": {"status": "deleted"},
        "Refresh": {"status": "refreshed"},
        "GetSchema": {"name": "Sales", "columns": [{"name": "Amount", "type": "double"}]},
        "ExportTMDL": "table Sales\n  mode: Import",
        "Rename": {"status": "renamed"},
        "MarkAsDateTable": {"status": "marked"},
    },
    "model_operations": {
        "Get": {"name": "My Model", "compatibilityLevel": 1600},
        "GetStats": {"tables": 5, "measures": 10, "columns": 30},
        "Refresh": {"status": "refreshed"},
        "Rename": {"status": "renamed"},
        "ExportTMDL": "model Model\n  culture: en-US",
    },
    "column_operations": {
        "List": [{"name": "Amount", "tableName": "Sales", "dataType": "double"}],
        "Get": {"name": "Amount", "dataType": "double"},
        "Create": {"status": "created"},
        "Update": {"status": "updated"},
        "Delete": {"status": "deleted"},
        "Rename": {"status": "renamed"},
        "ExportTMDL": "column Amount\n  dataType: double",
    },
}


# ---------------------------------------------------------------------------
# Mock MCP client
# ---------------------------------------------------------------------------


class MockPbiMcpClient:
    """Fake MCP client returning canned responses without spawning a process."""

    def __init__(self, responses: dict[str, dict[str, Any]] | None = None) -> None:
        self.responses = responses or CANNED_RESPONSES
        self.started = False
        self.stopped = False
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True

    def call_tool(self, tool_name: str, request: dict[str, Any]) -> Any:
        self.calls.append((tool_name, request))
        operation = request.get("operation", "")
        tool_responses = self.responses.get(tool_name, {})
        if operation in tool_responses:
            return tool_responses[operation]
        return {"status": "ok"}

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {"name": "measure_operations", "description": "Measure CRUD"},
            {"name": "table_operations", "description": "Table CRUD"},
            {"name": "dax_query_operations", "description": "DAX queries"},
        ]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_client() -> MockPbiMcpClient:
    """A fresh mock MCP client."""
    return MockPbiMcpClient()


@pytest.fixture
def patch_get_client(
    monkeypatch: pytest.MonkeyPatch, mock_client: MockPbiMcpClient
) -> MockPbiMcpClient:
    """Monkeypatch get_client in _helpers and connection modules."""
    factory = lambda repl_mode=False: mock_client  # noqa: E731

    monkeypatch.setattr("pbi_cli.commands._helpers.get_client", factory)
    monkeypatch.setattr("pbi_cli.commands.connection.get_client", factory)

    # Also patch dax.py which calls get_client directly
    monkeypatch.setattr("pbi_cli.commands.dax.get_client", factory)

    # Skip auto-setup (binary download + skills install) in tests
    monkeypatch.setattr("pbi_cli.commands.connection._ensure_ready", lambda: None)

    return mock_client


@pytest.fixture
def cli_runner() -> CliRunner:
    """Click test runner with separated stdout/stderr."""
    return CliRunner()


@pytest.fixture
def tmp_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect PBI_CLI_HOME and CONFIG_FILE to a temp directory."""
    monkeypatch.setattr("pbi_cli.core.config.PBI_CLI_HOME", tmp_path)
    monkeypatch.setattr("pbi_cli.core.config.CONFIG_FILE", tmp_path / "config.json")
    return tmp_path


@pytest.fixture
def tmp_connections(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect CONNECTIONS_FILE to a temp directory."""
    conn_file = tmp_path / "connections.json"
    monkeypatch.setattr("pbi_cli.core.connection_store.CONNECTIONS_FILE", conn_file)
    monkeypatch.setattr("pbi_cli.core.connection_store.PBI_CLI_HOME", tmp_path)
    monkeypatch.setattr("pbi_cli.core.config.PBI_CLI_HOME", tmp_path)
    monkeypatch.setattr("pbi_cli.core.config.CONFIG_FILE", tmp_path / "config.json")
    return tmp_path
