"""Tests for pbi_cli.core.mcp_client (unit-level, no real server)."""

from __future__ import annotations

import json

from pbi_cli.core.mcp_client import (
    _extract_text,
    _parse_content,
    get_client,
    get_shared_client,
)


# ---------------------------------------------------------------------------
# _parse_content tests
# ---------------------------------------------------------------------------


class FakeTextContent:
    """Mimics mcp TextContent blocks."""

    def __init__(self, text: str) -> None:
        self.text = text


def test_parse_content_single_json() -> None:
    blocks = [FakeTextContent('{"name": "Sales"}')]
    result = _parse_content(blocks)
    assert result == {"name": "Sales"}


def test_parse_content_single_plain_text() -> None:
    blocks = [FakeTextContent("just a string")]
    result = _parse_content(blocks)
    assert result == "just a string"


def test_parse_content_multiple_blocks() -> None:
    blocks = [FakeTextContent("hello"), FakeTextContent(" world")]
    result = _parse_content(blocks)
    assert result == "hello\n world"


def test_parse_content_non_list() -> None:
    result = _parse_content("raw value")
    assert result == "raw value"


def test_parse_content_json_array() -> None:
    blocks = [FakeTextContent('[{"a": 1}]')]
    result = _parse_content(blocks)
    assert result == [{"a": 1}]


# ---------------------------------------------------------------------------
# _extract_text tests
# ---------------------------------------------------------------------------


def test_extract_text_from_blocks() -> None:
    blocks = [FakeTextContent("error occurred")]
    result = _extract_text(blocks)
    assert result == "error occurred"


def test_extract_text_non_list() -> None:
    result = _extract_text("plain error")
    assert result == "plain error"


# ---------------------------------------------------------------------------
# get_client / get_shared_client tests
# ---------------------------------------------------------------------------


def test_get_client_oneshot_returns_fresh() -> None:
    c1 = get_client(repl_mode=False)
    c2 = get_client(repl_mode=False)
    assert c1 is not c2


def test_get_shared_client_returns_same_instance() -> None:
    c1 = get_shared_client()
    c2 = get_shared_client()
    assert c1 is c2
