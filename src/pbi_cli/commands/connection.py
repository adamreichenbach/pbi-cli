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
from pbi_cli.core.output import (
    print_error,
    print_info,
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
@pass_context
def connect(
    ctx: PbiContext,
    data_source: str | None,
    catalog: str,
    name: str | None,
) -> None:
    """Connect to a Power BI instance via data source.

    If --data-source is omitted, auto-detects a running Power BI Desktop instance.
    """
    if data_source is None:
        data_source = _auto_discover_data_source()

    from pbi_cli.core.session import connect as session_connect

    try:
        session = session_connect(data_source, catalog)

        # Use provided name, or the session's auto-generated name
        effective_name = name or session.connection_name

        info = ConnectionInfo(
            name=effective_name,
            data_source=data_source,
            initial_catalog=catalog,
        )
        store = load_connections()
        store = add_connection(store, info)
        save_connections(store)

        if ctx.json_output:
            print_json(
                {
                    "connection": effective_name,
                    "status": "connected",
                    "dataSource": data_source,
                }
            )
        else:
            print_success(f"Connected: {effective_name} ({data_source})")
            from pbi_cli.commands.skills_cmd import _is_installed, _get_bundled_skills

            bundled = _get_bundled_skills()
            any_missing = any(not _is_installed(name) for name in bundled)
            if any_missing:
                print_info(
                    "Tip: Claude Code skills not yet installed. "
                    "Run 'pbi-cli skills install' to register pbi-cli skills with Claude Code."
                )
    except Exception as e:
        print_error(f"Connection failed: {e}")
        raise SystemExit(1)


@click.command()
@click.option(
    "--name", "-n", default=None, help="Connection name to disconnect (defaults to active)."
)
@pass_context
def disconnect(ctx: PbiContext, name: str | None) -> None:
    """Disconnect from the active or named connection."""
    from pbi_cli.core.session import disconnect as session_disconnect

    store = load_connections()
    target = name or store.last_used

    if not target:
        print_error("No active connection to disconnect.")
        raise SystemExit(1)

    session_disconnect()

    store = remove_connection(store, target)
    save_connections(store)

    if ctx.json_output:
        print_json({"connection": target, "status": "disconnected"})
    else:
        print_success(f"Disconnected: {target}")


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
    """Auto-detect a running Power BI Desktop instance."""
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



