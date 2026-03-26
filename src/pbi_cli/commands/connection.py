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
from pbi_cli.core.mcp_client import get_client
from pbi_cli.core.output import (
    print_error,
    print_json,
    print_success,
    print_table,
)
from pbi_cli.main import PbiContext, pass_context


@click.command()
@click.option(
    "--data-source",
    "-d",
    default=None,
    help="Data source (e.g., localhost:54321). Auto-detected if omitted.",
)
@click.option("--catalog", "-C", default="", help="Initial catalog / dataset name.")
@click.option(
    "--name", "-n", default=None, help="Name for this connection (auto-generated if omitted)."
)
@click.option(
    "--connection-string", default="", help="Full connection string (overrides data-source)."
)
@pass_context
def connect(
    ctx: PbiContext,
    data_source: str | None,
    catalog: str,
    name: str | None,
    connection_string: str,
) -> None:
    """Connect to a Power BI instance via data source.

    If --data-source is omitted, auto-detects a running Power BI Desktop instance.
    """
    _ensure_ready()

    if data_source is None:
        data_source = _auto_discover_data_source()

    conn_name = name or _auto_name(data_source)

    request: dict[str, object] = {
        "operation": "Connect",
        "dataSource": data_source,
    }
    if catalog:
        request["initialCatalog"] = catalog
    if connection_string:
        request["connectionString"] = connection_string

    repl = ctx.repl_mode
    client = get_client(repl_mode=repl)
    try:
        result = client.call_tool("connection_operations", request)

        # Use server-returned connectionName if available, otherwise our local name
        server_name = _extract_connection_name(result)
        effective_name = server_name or conn_name

        info = ConnectionInfo(
            name=effective_name,
            data_source=data_source,
            initial_catalog=catalog,
            connection_string=connection_string,
        )
        store = load_connections()
        store = add_connection(store, info)
        save_connections(store)

        if ctx.json_output:
            print_json({"connection": effective_name, "status": "connected", "result": result})
        else:
            print_success(f"Connected: {effective_name} ({data_source})")
    except Exception as e:
        print_error(f"Connection failed: {e}")
        raise SystemExit(1)
    finally:
        if not repl:
            client.stop()


@click.command(name="connect-fabric")
@click.option("--workspace", "-w", required=True, help="Fabric workspace name (exact match).")
@click.option("--model", "-m", required=True, help="Semantic model name (exact match).")
@click.option("--name", "-n", default=None, help="Name for this connection.")
@click.option("--tenant", default="myorg", help="Tenant name for B2B scenarios.")
@pass_context
def connect_fabric(
    ctx: PbiContext, workspace: str, model: str, name: str | None, tenant: str
) -> None:
    """Connect to a Fabric workspace semantic model."""
    _ensure_ready()

    conn_name = name or f"{workspace}/{model}"

    request: dict[str, object] = {
        "operation": "ConnectFabric",
        "workspaceName": workspace,
        "semanticModelName": model,
        "tenantName": tenant,
    }

    repl = ctx.repl_mode
    client = get_client(repl_mode=repl)
    try:
        result = client.call_tool("connection_operations", request)

        server_name = _extract_connection_name(result)
        effective_name = server_name or conn_name

        info = ConnectionInfo(
            name=effective_name,
            data_source=f"powerbi://api.powerbi.com/v1.0/{tenant}/{workspace}",
            workspace_name=workspace,
            semantic_model_name=model,
            tenant_name=tenant,
        )
        store = load_connections()
        store = add_connection(store, info)
        save_connections(store)

        if ctx.json_output:
            print_json({"connection": effective_name, "status": "connected", "result": result})
        else:
            print_success(f"Connected to Fabric: {workspace}/{model}")
    except Exception as e:
        print_error(f"Fabric connection failed: {e}")
        raise SystemExit(1)
    finally:
        if not repl:
            client.stop()


@click.command()
@click.option(
    "--name", "-n", default=None, help="Connection name to disconnect (defaults to active)."
)
@pass_context
def disconnect(ctx: PbiContext, name: str | None) -> None:
    """Disconnect from the active or named connection."""
    store = load_connections()
    target = name or store.last_used

    if not target:
        print_error("No active connection to disconnect.")
        raise SystemExit(1)

    repl = ctx.repl_mode
    client = get_client(repl_mode=repl)
    try:
        client.call_tool(
            "connection_operations",
            {
                "operation": "Disconnect",
                "connectionName": target,
            },
        )

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
        if not repl:
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

        print_key_value(
            "Active Connection",
            {
                "Name": conn.name,
                "Data Source": conn.data_source,
                "Catalog": conn.initial_catalog,
            },
        )


def _auto_discover_data_source() -> str:
    """Auto-detect a running Power BI Desktop instance.

    Raises click.ClickException if no instance is found.
    """
    from pbi_cli.core.output import print_info
    from pbi_cli.utils.platform import discover_pbi_port

    port = discover_pbi_port()
    if port is None:
        raise click.ClickException(
            "No running Power BI Desktop instance found.\n"
            "  1. Open Power BI Desktop and load a .pbix file\n"
            "  2. Run 'pbi connect' again, or specify manually: pbi connect -d localhost:<port>"
        )

    data_source = f"localhost:{port}"
    print_info(f"Auto-detected Power BI Desktop on {data_source}")
    return data_source


def _ensure_ready() -> None:
    """Auto-setup binary and skills if not already done.

    Lets users go straight from install to connect in one step:
        pipx install pbi-cli-tool
        pbi connect -d localhost:54321
    """
    from pbi_cli.core.binary_manager import resolve_binary

    try:
        resolve_binary()
    except FileNotFoundError:
        from pbi_cli.core.binary_manager import download_and_extract
        from pbi_cli.core.output import print_info

        print_info("MCP binary not found. Running first-time setup...")
        download_and_extract()

    from pbi_cli.commands.skills_cmd import SKILLS_TARGET_DIR, _get_bundled_skills

    bundled = _get_bundled_skills()
    any_missing = any(not (SKILLS_TARGET_DIR / name / "SKILL.md").exists() for name in bundled)
    if bundled and any_missing:
        from pbi_cli.core.output import print_info

        print_info("Installing Claude Code skills...")
        for name, source in sorted(bundled.items()):
            target_dir = SKILLS_TARGET_DIR / name
            if (target_dir / "SKILL.md").exists():
                continue
            target_dir.mkdir(parents=True, exist_ok=True)
            source_file = source / "SKILL.md"
            target_file = target_dir / "SKILL.md"
            target_file.write_text(source_file.read_text(encoding="utf-8"), encoding="utf-8")
        print_info("Skills installed.")


def _extract_connection_name(result: object) -> str | None:
    """Extract connectionName from MCP server response, if present."""
    if isinstance(result, dict):
        return result.get("connectionName") or result.get("ConnectionName")
    return None


def _auto_name(data_source: str) -> str:
    """Generate a connection name from a data source string."""
    cleaned = data_source.replace("://", "-").replace("/", "-").replace(":", "-")
    return cleaned[:50]
