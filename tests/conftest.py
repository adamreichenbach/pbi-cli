"""Shared test fixtures for pbi-cli v2 (direct .NET backend)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

# ---------------------------------------------------------------------------
# Mock TOM objects used by the mock session
# ---------------------------------------------------------------------------


class MockCollection:
    """Simulates a .NET ICollection (iterable, with Count/Add/Remove)."""

    def __init__(self, items: list[Any] | None = None) -> None:
        self._items = list(items or [])

    def __iter__(self) -> Any:
        return iter(self._items)

    def __getitem__(self, index: int) -> Any:
        return self._items[index]

    @property
    def Count(self) -> int:
        return len(self._items)

    def Add(self, item: Any = None) -> Any:
        if item is not None:
            self._items.append(item)
            return item
        # Parameterless Add() -- create a simple object and return it
        obj = type(
            "TraceObj",
            (),
            {
                "Name": "",
                "AutoRestart": False,
                "ID": "trace-1",
                "Update": lambda self: None,
                "Start": lambda self: None,
                "Stop": lambda self: None,
            },
        )()
        self._items.append(obj)
        return obj

    def Remove(self, item: Any) -> None:
        self._items.remove(item)


@dataclass
class MockMeasure:
    Name: str = "Total Sales"
    Expression: str = "SUM(Sales[Amount])"
    DisplayFolder: str = ""
    Description: str = ""
    FormatString: str = ""
    IsHidden: bool = False


@dataclass
class MockColumn:
    Name: str = "Amount"
    DataType: str = "Double"
    Type: str = "DataColumn"
    SourceColumn: str = "Amount"
    DisplayFolder: str = ""
    Description: str = ""
    FormatString: str = ""
    IsHidden: bool = False
    IsKey: bool = False


@dataclass
class MockPartition:
    Name: str = "Partition1"
    Mode: str = "Import"
    SourceType: str = "M"
    State: str = "Ready"


@dataclass
class MockRelationship:
    Name: str = "rel1"
    FromTable: Any = None
    FromColumn: Any = None
    ToTable: Any = None
    ToColumn: Any = None
    CrossFilteringBehavior: str = "OneDirection"
    IsActive: bool = True


@dataclass
class MockHierarchy:
    Name: str = "DateHierarchy"
    Description: str = ""
    Levels: Any = None

    def __post_init__(self) -> None:
        if self.Levels is None:
            self.Levels = MockCollection()


@dataclass
class MockLevel:
    Name: str = "Year"
    Ordinal: int = 0
    Column: Any = None


@dataclass
class MockRole:
    Name: str = "Reader"
    Description: str = ""
    ModelPermission: str = "Read"
    TablePermissions: Any = None

    def __post_init__(self) -> None:
        if self.TablePermissions is None:
            self.TablePermissions = MockCollection()


@dataclass
class MockPerspective:
    Name: str = "Sales View"
    Description: str = ""


@dataclass
class MockExpression:
    Name: str = "ServerURL"
    Kind: str = "M"
    Expression: str = '"https://example.com"'
    Description: str = ""


@dataclass
class MockCulture:
    Name: str = "en-US"


class MockTable:
    """Simulates a TOM Table with nested collections."""

    def __init__(
        self,
        name: str = "Sales",
        data_category: str = "",
        description: str = "",
    ) -> None:
        self.Name = name
        self.DataCategory = data_category
        self.Description = description
        self.IsHidden = False
        self.CalculationGroup = None
        self.Measures = MockCollection([MockMeasure()])
        self.Columns = MockCollection([MockColumn()])
        self.Partitions = MockCollection([MockPartition()])
        self.Hierarchies = MockCollection()


class MockModel:
    """Simulates a TOM Model."""

    def __init__(self) -> None:
        self.Name = "TestModel"
        self.Description = ""
        self.DefaultMode = "Import"
        self.Culture = "en-US"
        self.CompatibilityLevel = 1600

        self.Tables = MockCollection([MockTable()])
        self.Relationships = MockCollection()
        self.Roles = MockCollection()
        self.Perspectives = MockCollection()
        self.Expressions = MockCollection()
        self.Cultures = MockCollection()

    def SaveChanges(self) -> None:
        pass

    def RequestRefresh(self, refresh_type: Any) -> None:
        pass


class MockDatabase:
    """Simulates a TOM Database."""

    def __init__(self, model: MockModel | None = None) -> None:
        self.Name = "TestDB"
        self.ID = "TestDB-ID"
        self.CompatibilityLevel = 1600
        self.LastUpdate = "2026-01-01"
        self.Model = model or MockModel()


class MockServer:
    """Simulates a TOM Server."""

    def __init__(self, database: MockDatabase | None = None) -> None:
        db = database or MockDatabase()
        self.Databases = MockCollection([db])
        self.Traces = MockCollection()

    def Connect(self, conn_str: str) -> None:
        pass

    def Disconnect(self) -> None:
        pass

    def BeginTransaction(self) -> str:
        return "tx-001"

    def CommitTransaction(self, tx_id: str = "") -> None:
        pass

    def RollbackTransaction(self, tx_id: str = "") -> None:
        pass


class MockAdomdConnection:
    """Simulates an AdomdConnection."""

    def Open(self) -> None:
        pass

    def Close(self) -> None:
        pass


def build_mock_session() -> Any:
    """Build a complete mock Session for testing."""
    from pbi_cli.core.session import Session

    model = MockModel()
    database = MockDatabase(model)
    server = MockServer(database)
    adomd = MockAdomdConnection()

    return Session(
        server=server,
        database=database,
        model=model,
        adomd_connection=adomd,
        connection_name="test-conn",
        data_source="localhost:12345",
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_session() -> Any:
    """A fresh mock session."""
    return build_mock_session()


@pytest.fixture
def patch_session(monkeypatch: pytest.MonkeyPatch, mock_session: Any) -> Any:
    """Monkeypatch get_session_for_command to return mock session."""
    monkeypatch.setattr(
        "pbi_cli.core.session.get_session_for_command",
        lambda ctx: mock_session,
    )
    # Also patch modules that import get_session_for_command at module level
    monkeypatch.setattr(
        "pbi_cli.commands.model.get_session_for_command",
        lambda ctx: mock_session,
    )
    # Also patch connection commands that call session.connect directly
    monkeypatch.setattr(
        "pbi_cli.core.session.connect",
        lambda data_source, catalog="": mock_session,
    )
    # Skip skill install in connect
    monkeypatch.setattr("pbi_cli.commands.connection._ensure_ready", lambda: None)
    return mock_session


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
