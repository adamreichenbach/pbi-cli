"""Connection management commands."""

from __future__ import annotations

import click

from pbi_cli.core.connection_store import (
    ConnectionInfo,
    add_connection,
    get_active_connection,
    load_connections,
    remove_connection,
    save_connections,
)
from pbi_cli.core.mcp_client import PbiMcpClient, get_client
from pbi_cli.core.output import (
    format_mcp_result,
    print_error,
    print_json,
    print_success,
    print_table,
)
from pbi_cli.main import PbiContext, pass_context


@click.command()
@click.option("--data-source", "-d", required=True, help="Data source (e.g., localhost:54321).")
@click.option("--catalog", "-C", default="", help="Initial catalog / dataset name.")
@click.option("--name", "-n", default=None, help="Name for this connection (auto-generated if omitted).")
@click.option("--connection-string", default="", help="Full connection string (overrides data-source).")
@pass_context
def connect(ctx: PbiContext, data_source: str, catalog: str, name: str | None, connection_string: str) -> None:
    """Connect to a Power BI instance via data source."""
    conn_name = name or _auto_name(data_source)

    request: dict = {
        "operation": "Connect",
        "connectionName": conn_name,
        "dataSource": data_source,
    }
    if catalog:
        request["initialCatalog"] = catalog
    if connection_string:
        request["connectionString"] = connection_string

    client = get_client()
    try:
        result = client.call_tool("connection_operations", request)

        info = ConnectionInfo(
            name=conn_name,
            data_source=data_source,
            initial_catalog=catalog,
            connection_string=connection_string,
        )
        store = load_connections()
        store = add_connection(store, info)
        save_connections(store)

        if ctx.json_output:
            print_json({"connection": conn_name, "status": "connected", "result": result})
        else:
            print_success(f"Connected: {conn_name} ({data_source})")
    except Exception as e:
        print_error(f"Connection failed: {e}")
        raise SystemExit(1)
    finally:
        client.stop()


@click.command(name="connect-fabric")
@click.option("--workspace", "-w", required=True, help="Fabric workspace name (exact match).")
@click.option("--model", "-m", required=True, help="Semantic model name (exact match).")
@click.option("--name", "-n", default=None, help="Name for this connection.")
@click.option("--tenant", default="myorg", help="Tenant name for B2B scenarios.")
@pass_context
def connect_fabric(ctx: PbiContext, workspace: str, model: str, name: str | None, tenant: str) -> None:
    """Connect to a Fabric workspace semantic model."""
    conn_name = name or f"{workspace}/{model}"

    request: dict = {
        "operation": "ConnectFabric",
        "connectionName": conn_name,
        "workspaceName": workspace,
        "semanticModelName": model,
        "tenantName": tenant,
    }

    client = get_client()
    try:
        result = client.call_tool("connection_operations", request)

        info = ConnectionInfo(
            name=conn_name,
            data_source=f"powerbi://api.powerbi.com/v1.0/{tenant}/{workspace}",
            workspace_name=workspace,
            semantic_model_name=model,
            tenant_name=tenant,
        )
        store = load_connections()
        store = add_connection(store, info)
        save_connections(store)

        if ctx.json_output:
            print_json({"connection": conn_name, "status": "connected", "result": result})
        else:
            print_success(f"Connected to Fabric: {workspace}/{model}")
    except Exception as e:
        print_error(f"Fabric connection failed: {e}")
        raise SystemExit(1)
    finally:
        client.stop()


@click.command()
@click.option("--name", "-n", default=None, help="Connection name to disconnect (defaults to active).")
@pass_context
def disconnect(ctx: PbiContext, name: str | None) -> None:
    """Disconnect from the active or named connection."""
    store = load_connections()
    target = name or store.last_used

    if not target:
        print_error("No active connection to disconnect.")
        raise SystemExit(1)

    client = get_client()
    try:
        result = client.call_tool("connection_operations", {
            "operation": "Disconnect",
            "connectionName": target,
        })

        store = remove_connection(store, target)
        save_connections(store)

        if ctx.json_output:
            print_json({"connection": target, "status": "disconnected"})
        else:
            print_success(f"Disconnected: {target}")
    except Exception as e:
        print_error(f"Disconnect failed: {e}")
        raise SystemExit(1)
    finally:
        client.stop()


@click.group()
def connections() -> None:
    """Manage saved connections."""


@connections.command(name="list")
@pass_context
def connections_list(ctx: PbiContext) -> None:
    """List all saved connections."""
    store = load_connections()

    if ctx.json_output:
        from dataclasses import asdict
        data = {
            "last_used": store.last_used,
            "connections": [asdict(c) for c in store.connections.values()],
        }
        print_json(data)
        return

    if not store.connections:
        print_error("No saved connections. Run 'pbi connect' first.")
        return

    rows = []
    for info in store.connections.values():
        active = "*" if info.name == store.last_used else ""
        rows.append([active, info.name, info.data_source, info.initial_catalog])

    print_table("Connections", ["Active", "Name", "Data Source", "Catalog"], rows)


@connections.command(name="last")
@pass_context
def connections_last(ctx: PbiContext) -> None:
    """Show the last-used connection."""
    store = load_connections()
    conn = get_active_connection(store)

    if conn is None:
        print_error("No active connection.")
        raise SystemExit(1)

    if ctx.json_output:
        from dataclasses import asdict
        print_json(asdict(conn))
    else:
        from pbi_cli.core.output import print_key_value
        print_key_value("Active Connection", {
            "Name": conn.name,
            "Data Source": conn.data_source,
            "Catalog": conn.initial_catalog,
        })


def _auto_name(data_source: str) -> str:
    """Generate a connection name from a data source string."""
    cleaned = data_source.replace("://", "-").replace("/", "-").replace(":", "-")
    return cleaned[:50]
