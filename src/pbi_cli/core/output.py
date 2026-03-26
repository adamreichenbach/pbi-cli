"""Dual-mode output formatter: JSON for agents, Rich tables for humans."""

from __future__ import annotations

import json
import sys
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


console = Console()
error_console = Console(stderr=True)


def print_json(data: Any) -> None:
    """Print data as formatted JSON to stdout."""
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))


def print_success(message: str) -> None:
    """Print a success message to stderr (keeps stdout clean for JSON)."""
    error_console.print(f"[green]{message}[/green]")


def print_error(message: str) -> None:
    """Print an error message to stderr."""
    error_console.print(f"[red]Error:[/red] {message}")


def print_warning(message: str) -> None:
    """Print a warning message to stderr."""
    error_console.print(f"[yellow]Warning:[/yellow] {message}")


def print_info(message: str) -> None:
    """Print an info message to stderr."""
    error_console.print(f"[blue]{message}[/blue]")


def print_table(
    title: str,
    columns: list[str],
    rows: list[list[str]],
) -> None:
    """Print a Rich table to stdout."""
    table = Table(title=title, show_header=True, header_style="bold cyan")
    for col in columns:
        table.add_column(col)
    for row in rows:
        table.add_row(*row)
    console.print(table)


def print_key_value(title: str, data: dict[str, Any]) -> None:
    """Print key-value pairs in a Rich panel."""
    lines = []
    for key, value in data.items():
        lines.append(f"[bold]{key}:[/bold] {value}")
    console.print(Panel("\n".join(lines), title=title, border_style="cyan"))


def format_mcp_result(result: Any, json_output: bool) -> None:
    """Format and print an MCP tool result.

    In JSON mode, prints the raw result. In human mode, attempts to render
    a table or key-value display based on the shape of the data.
    """
    if json_output:
        print_json(result)
        return

    if isinstance(result, list):
        if not result:
            print_info("No results.")
            return
        if isinstance(result[0], dict):
            columns = list(result[0].keys())
            rows = [[str(item.get(c, "")) for c in columns] for item in result]
            print_table("Results", columns, rows)
        else:
            for item in result:
                console.print(str(item))
    elif isinstance(result, dict):
        print_key_value("Result", result)
    else:
        console.print(str(result))
