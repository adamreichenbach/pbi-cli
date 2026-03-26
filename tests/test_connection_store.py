"""Tests for pbi_cli.core.connection_store."""

from __future__ import annotations

from pathlib import Path

from pbi_cli.core.connection_store import (
    ConnectionInfo,
    ConnectionStore,
    add_connection,
    get_active_connection,
    load_connections,
    remove_connection,
    save_connections,
)


def test_empty_store() -> None:
    store = ConnectionStore()
    assert store.last_used == ""
    assert store.connections == {}


def test_add_connection_returns_new_store() -> None:
    store = ConnectionStore()
    info = ConnectionInfo(name="test", data_source="localhost:1234")
    new_store = add_connection(store, info)

    assert "test" in new_store.connections
    assert new_store.last_used == "test"
    # Original is unchanged
    assert store.connections == {}


def test_remove_connection() -> None:
    info = ConnectionInfo(name="test", data_source="localhost:1234")
    store = ConnectionStore(last_used="test", connections={"test": info})
    new_store = remove_connection(store, "test")

    assert "test" not in new_store.connections
    assert new_store.last_used == ""


def test_remove_connection_clears_last_used_only_if_matching() -> None:
    info1 = ConnectionInfo(name="a", data_source="host1")
    info2 = ConnectionInfo(name="b", data_source="host2")
    store = ConnectionStore(
        last_used="a",
        connections={"a": info1, "b": info2},
    )
    new_store = remove_connection(store, "b")

    assert new_store.last_used == "a"  # unchanged
    assert "b" not in new_store.connections


def test_get_active_connection_with_override() -> None:
    info = ConnectionInfo(name="test", data_source="localhost")
    store = ConnectionStore(connections={"test": info})

    result = get_active_connection(store, override="test")
    assert result is not None
    assert result.name == "test"


def test_get_active_connection_uses_last_used() -> None:
    info = ConnectionInfo(name="test", data_source="localhost")
    store = ConnectionStore(last_used="test", connections={"test": info})

    result = get_active_connection(store)
    assert result is not None
    assert result.name == "test"


def test_get_active_connection_returns_none() -> None:
    store = ConnectionStore()
    assert get_active_connection(store) is None


def test_save_and_load_roundtrip(tmp_connections: Path) -> None:
    info = ConnectionInfo(
        name="my-conn",
        data_source="localhost:54321",
        initial_catalog="Sales",
    )
    store = add_connection(ConnectionStore(), info)
    save_connections(store)

    loaded = load_connections()
    assert loaded.last_used == "my-conn"
    assert "my-conn" in loaded.connections
    assert loaded.connections["my-conn"].data_source == "localhost:54321"


def test_load_connections_missing_file(tmp_connections: Path) -> None:
    store = load_connections()
    assert store.connections == {}


def test_connection_info_is_frozen() -> None:
    info = ConnectionInfo(name="test", data_source="localhost")
    try:
        info.name = "changed"  # type: ignore[misc]
        assert False, "Should have raised"
    except AttributeError:
        pass
