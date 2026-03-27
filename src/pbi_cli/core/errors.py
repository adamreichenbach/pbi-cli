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


class DotNetNotFoundError(PbiCliError):
    """Raised when pythonnet or the bundled .NET DLLs are missing."""

    def __init__(
        self,
        message: str = ("pythonnet is required. Install it with: pip install pythonnet"),
    ) -> None:
        super().__init__(message)


class ConnectionRequiredError(PbiCliError):
    """Raised when a command requires an active connection but none exists."""

    def __init__(self, message: str = "No active connection. Run 'pbi connect' first.") -> None:
        super().__init__(message)


class TomError(PbiCliError):
    """Raised when a TOM operation fails."""

    def __init__(self, operation: str, detail: str) -> None:
        self.operation = operation
        self.detail = detail
        super().__init__(f"{operation}: {detail}")
