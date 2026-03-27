"""Tests for pbi_cli.core.output."""

from __future__ import annotations

import json
import sys
from io import StringIO

from pbi_cli.core.output import format_result, print_json


def test_print_json_outputs_valid_json() -> None:
    old_stdout = sys.stdout
    sys.stdout = buf = StringIO()
    try:
        print_json({"key": "value"})
    finally:
        sys.stdout = old_stdout

    parsed = json.loads(buf.getvalue())
    assert parsed == {"key": "value"}


def test_print_json_handles_non_serializable() -> None:
    from pathlib import Path

    old_stdout = sys.stdout
    sys.stdout = buf = StringIO()
    try:
        print_json({"path": Path("/tmp")})
    finally:
        sys.stdout = old_stdout

    parsed = json.loads(buf.getvalue())
    assert "tmp" in parsed["path"]


def test_format_result_json_mode() -> None:
    old_stdout = sys.stdout
    sys.stdout = buf = StringIO()
    try:
        format_result({"name": "Sales"}, json_output=True)
    finally:
        sys.stdout = old_stdout

    parsed = json.loads(buf.getvalue())
    assert parsed["name"] == "Sales"


def test_format_result_empty_list() -> None:
    # Should not raise; prints "No results." to stderr
    format_result([], json_output=False)


def test_format_result_dict() -> None:
    # Should not raise; prints key-value panel
    format_result({"name": "Test"}, json_output=False)


def test_format_result_list_of_dicts() -> None:
    # Should not raise; prints table
    format_result([{"name": "A"}, {"name": "B"}], json_output=False)


def test_format_result_string() -> None:
    # Should not raise; prints string
    format_result("some text", json_output=False)
