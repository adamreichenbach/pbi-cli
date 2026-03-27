"""Connection session manager for Power BI Desktop.

Maintains a persistent connection to the Analysis Services engine,
reusable across commands in both REPL and one-shot modes.
"""

from __future__ import annotations

import atexit
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Session:
    """An active connection to a Power BI Analysis Services instance."""

    server: Any  # Microsoft.AnalysisServices.Tabular.Server
    database: Any  # Microsoft.AnalysisServices.Tabular.Database
    model: Any  # Microsoft.AnalysisServices.Tabular.Model
    adomd_connection: Any  # Microsoft.AnalysisServices.AdomdClient.AdomdConnection
    connection_name: str
    data_source: str


# Module-level session for REPL mode persistence
_current_session: Session | None = None


def connect(data_source: str, catalog: str = "") -> Session:
    """Connect to an Analysis Services instance.

    Args:
        data_source: The data source (e.g., ``localhost:57947``).
        catalog: Optional initial catalog / database name.

    Returns:
        A new ``Session`` with active TOM and ADOMD connections.
    """
    from pbi_cli.core.dotnet_loader import get_adomd_connection_class, get_server_class

    Server = get_server_class()
    AdomdConnection = get_adomd_connection_class()

    conn_str = f"Provider=MSOLAP;Data Source={data_source}"
    if catalog:
        conn_str += f";Initial Catalog={catalog}"

    server = Server()
    server.Connect(conn_str)

    # Pick the first database (PBI Desktop has exactly one)
    db = server.Databases[0]
    model = db.Model

    # Build connection name from database info
    db_name = str(db.Name) if db.Name else ""
    connection_name = f"PBIDesktop-{db_name[:20]}-{data_source.split(':')[-1]}"

    # ADOMD connection for DAX queries
    adomd_conn = AdomdConnection(conn_str)
    adomd_conn.Open()

    session = Session(
        server=server,
        database=db,
        model=model,
        adomd_connection=adomd_conn,
        connection_name=connection_name,
        data_source=data_source,
    )

    global _current_session
    _current_session = session

    return session


def disconnect(session: Session | None = None) -> None:
    """Disconnect an active session."""
    global _current_session
    target = session or _current_session

    if target is None:
        return

    try:
        target.adomd_connection.Close()
    except Exception:
        pass
    try:
        target.server.Disconnect()
    except Exception:
        pass

    if target is _current_session:
        _current_session = None


def get_current_session() -> Session | None:
    """Return the current session, or None if not connected."""
    return _current_session


def ensure_connected() -> Session:
    """Return the current session, raising if not connected."""
    from pbi_cli.core.errors import ConnectionRequiredError

    if _current_session is None:
        raise ConnectionRequiredError()
    return _current_session


def get_session_for_command(ctx: Any) -> Session:
    """Get or establish a session for a CLI command.

    In REPL mode, returns the existing session.
    In one-shot mode, reconnects from the saved connection store.
    """
    global _current_session

    if ctx.repl_mode and _current_session is not None:
        return _current_session

    # One-shot mode: reconnect from saved connection
    from pbi_cli.core.connection_store import get_active_connection, load_connections

    store = load_connections()
    conn = get_active_connection(store, override=ctx.connection)
    if conn is None:
        from pbi_cli.core.errors import ConnectionRequiredError

        raise ConnectionRequiredError()

    return connect(conn.data_source, conn.initial_catalog)


@atexit.register
def _cleanup() -> None:
    """Disconnect on process exit."""
    disconnect()
