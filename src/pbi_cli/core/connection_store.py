"""Persist named connections to ~/.pbi-cli/connections.json."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from pbi_cli.core.config import PBI_CLI_HOME, ensure_home_dir


CONNECTIONS_FILE = PBI_CLI_HOME / "connections.json"


@dataclass(frozen=True)
class ConnectionInfo:
    """A saved connection to a Power BI instance."""

    name: str
    data_source: str
    initial_catalog: str = ""
    workspace_name: str = ""
    semantic_model_name: str = ""
    tenant_name: str = "myorg"
    connection_string: str = ""


@dataclass(frozen=True)
class ConnectionStore:
    """Immutable store of named connections."""

    last_used: str = ""
    connections: dict[str, ConnectionInfo] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.connections is None:
            object.__setattr__(self, "connections", {})


def load_connections() -> ConnectionStore:
    """Load connections from disk."""
    if not CONNECTIONS_FILE.exists():
        return ConnectionStore()
    try:
        raw = json.loads(CONNECTIONS_FILE.read_text(encoding="utf-8"))
        conns = {}
        for name, data in raw.get("connections", {}).items():
            conns[name] = ConnectionInfo(name=name, **{k: v for k, v in data.items() if k != "name"})
        return ConnectionStore(
            last_used=raw.get("last_used", ""),
            connections=conns,
        )
    except (json.JSONDecodeError, KeyError, TypeError):
        return ConnectionStore()


def save_connections(store: ConnectionStore) -> None:
    """Write connections to disk."""
    ensure_home_dir()
    data = {
        "last_used": store.last_used,
        "connections": {name: asdict(info) for name, info in store.connections.items()},
    }
    CONNECTIONS_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def add_connection(store: ConnectionStore, info: ConnectionInfo) -> ConnectionStore:
    """Return a new store with the connection added and set as last-used."""
    new_conns = dict(store.connections)
    new_conns[info.name] = info
    return ConnectionStore(last_used=info.name, connections=new_conns)


def remove_connection(store: ConnectionStore, name: str) -> ConnectionStore:
    """Return a new store with the named connection removed."""
    new_conns = {k: v for k, v in store.connections.items() if k != name}
    new_last = store.last_used if store.last_used != name else ""
    return ConnectionStore(last_used=new_last, connections=new_conns)


def get_active_connection(store: ConnectionStore, override: str | None = None) -> ConnectionInfo | None:
    """Get the active connection: explicit override, or last-used."""
    name = override or store.last_used
    if not name:
        return None
    return store.connections.get(name)
