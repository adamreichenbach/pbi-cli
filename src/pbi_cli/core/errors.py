"""User-facing error types for pbi-cli.

These exceptions integrate with Click's error formatting so that
errors display cleanly in both normal and REPL modes.
"""

from __future__ import annotations

import click


class PbiCliError(click.ClickException):
    """Base error for all pbi-cli user-facing failures."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class BinaryNotFoundError(PbiCliError):
    """Raised when the MCP server binary cannot be resolved."""

    def __init__(
        self,
        message: str = "Power BI MCP binary not found. Run 'pbi setup' first.",
    ) -> None:
        super().__init__(message)


class ConnectionRequiredError(PbiCliError):
    """Raised when a command requires an active connection but none exists."""

    def __init__(self, message: str = "No active connection. Run 'pbi connect' first.") -> None:
        super().__init__(message)


class McpToolError(PbiCliError):
    """Raised when an MCP tool call fails."""

    def __init__(self, tool_name: str, detail: str) -> None:
        self.tool_name = tool_name
        self.detail = detail
        super().__init__(f"{tool_name}: {detail}")
