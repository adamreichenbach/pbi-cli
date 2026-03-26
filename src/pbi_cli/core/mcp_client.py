"""MCP client: communicates with the Power BI MCP server binary over stdio.

Uses the official `mcp` Python SDK to handle JSON-RPC framing and protocol
negotiation. Exposes a synchronous API for Click commands while managing
an async event loop internally.
"""

from __future__ import annotations

import asyncio
import atexit
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from pbi_cli.core.binary_manager import resolve_binary
from pbi_cli.core.config import load_config


class McpClientError(Exception):
    """Raised when the MCP server returns an error."""


class PbiMcpClient:
    """Synchronous wrapper around the async MCP stdio client.

    Usage:
        client = PbiMcpClient()
        result = client.call_tool("measure_operations", {
            "operation": "List",
            "connectionName": "my-conn",
        })
    """

    def __init__(
        self,
        binary_path: str | Path | None = None,
        args: list[str] | None = None,
    ) -> None:
        self._binary_path = str(binary_path) if binary_path else None
        self._args = args
        self._loop: asyncio.AbstractEventLoop | None = None
        self._session: ClientSession | None = None
        self._cleanup_stack: Any = None
        self._started = False

    def _resolve_binary(self) -> str:
        """Resolve binary path lazily."""
        if self._binary_path:
            return self._binary_path
        return str(resolve_binary())

    def _resolve_args(self) -> list[str]:
        """Resolve binary args from config or defaults."""
        if self._args is not None:
            return self._args
        config = load_config()
        return list(config.binary_args)

    def _ensure_loop(self) -> asyncio.AbstractEventLoop:
        """Get or create the event loop."""
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
        return self._loop

    def start(self) -> None:
        """Start the MCP server process and initialize the session."""
        if self._started:
            return

        loop = self._ensure_loop()
        loop.run_until_complete(self._async_start())
        self._started = True
        atexit.register(self.stop)

    async def _async_start(self) -> None:
        """Async startup: spawn the server and initialize MCP session."""
        binary = self._resolve_binary()
        args = self._resolve_args()

        server_params = StdioServerParameters(
            command=binary,
            args=args,
        )

        # Create the stdio transport
        self._read_stream, self._write_stream = await self._enter_context(
            stdio_client(server_params)
        )

        # Create and initialize the MCP session
        self._session = await self._enter_context(
            ClientSession(self._read_stream, self._write_stream)
        )

        await self._session.initialize()

    async def _enter_context(self, cm: Any) -> Any:
        """Enter an async context manager and track it for cleanup."""
        if self._cleanup_stack is None:
            self._cleanup_stack = []
        result = await cm.__aenter__()
        self._cleanup_stack.append(cm)
        return result

    def call_tool(self, tool_name: str, request: dict[str, Any]) -> Any:
        """Call an MCP tool synchronously.

        Args:
            tool_name: The MCP tool name (e.g., "measure_operations").
            request: The request dict (will be wrapped as {"request": request}).

        Returns:
            The parsed result from the MCP server.

        Raises:
            McpClientError: If the server returns an error.
        """
        if not self._started:
            self.start()

        loop = self._ensure_loop()
        return loop.run_until_complete(self._async_call_tool(tool_name, request))

    async def _async_call_tool(self, tool_name: str, request: dict[str, Any]) -> Any:
        """Execute a tool call via the MCP session."""
        if self._session is None:
            raise McpClientError("MCP session not initialized. Call start() first.")

        result = await self._session.call_tool(
            tool_name,
            arguments={"request": request},
        )

        if result.isError:
            error_text = _extract_text(result.content)
            raise McpClientError(f"MCP tool error: {error_text}")

        return _parse_content(result.content)

    def list_tools(self) -> list[dict[str, Any]]:
        """List all available MCP tools."""
        if not self._started:
            self.start()

        loop = self._ensure_loop()
        return loop.run_until_complete(self._async_list_tools())

    async def _async_list_tools(self) -> list[dict[str, Any]]:
        """List tools from the MCP session."""
        if self._session is None:
            raise McpClientError("MCP session not initialized.")

        result = await self._session.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description or "",
            }
            for tool in result.tools
        ]

    def stop(self) -> None:
        """Shut down the MCP server process."""
        if not self._started:
            return

        loop = self._ensure_loop()
        loop.run_until_complete(self._async_stop())
        self._started = False
        self._session = None

    async def _async_stop(self) -> None:
        """Clean up all async context managers in reverse order."""
        if self._cleanup_stack:
            for cm in reversed(self._cleanup_stack):
                try:
                    await cm.__aexit__(None, None, None)
                except Exception:
                    pass
            self._cleanup_stack = []

    def __del__(self) -> None:
        try:
            self.stop()
        except Exception:
            pass


def _extract_text(content: Any) -> str:
    """Extract text from MCP content blocks."""
    if isinstance(content, list):
        parts = []
        for block in content:
            if hasattr(block, "text"):
                parts.append(block.text)
        return "\n".join(parts) if parts else str(content)
    return str(content)


def _parse_content(content: Any) -> Any:
    """Parse MCP content blocks into Python data.

    MCP returns content as a list of TextContent blocks. This function
    tries to parse the text as JSON, falling back to raw text.
    """
    import json

    if isinstance(content, list):
        texts = []
        for block in content:
            if hasattr(block, "text"):
                texts.append(block.text)

        if len(texts) == 1:
            try:
                return json.loads(texts[0])
            except (json.JSONDecodeError, ValueError):
                return texts[0]

        combined = "\n".join(texts)
        try:
            return json.loads(combined)
        except (json.JSONDecodeError, ValueError):
            return combined

    return content


# Module-level singleton for REPL mode (keeps server alive across commands).
_shared_client: PbiMcpClient | None = None


def get_shared_client() -> PbiMcpClient:
    """Get or create a shared MCP client instance."""
    global _shared_client
    if _shared_client is None:
        _shared_client = PbiMcpClient()
    return _shared_client


def get_client(repl_mode: bool = False) -> PbiMcpClient:
    """Get an MCP client.

    In REPL mode, returns a shared long-lived client.
    In one-shot mode, returns a fresh client (caller should stop() it).
    """
    if repl_mode:
        return get_shared_client()
    return PbiMcpClient()
