"""Tests for pbi_cli.commands._helpers."""

from __future__ import annotations

import pytest

from pbi_cli.commands._helpers import build_definition, run_command
from pbi_cli.core.errors import TomError
from pbi_cli.main import PbiContext


def test_build_definition_required_only() -> None:
    result = build_definition(
        required={"name": "Sales"},
        optional={},
    )
    assert result == {"name": "Sales"}


def test_build_definition_filters_none() -> None:
    result = build_definition(
        required={"name": "Sales"},
        optional={"description": None, "folder": "Finance"},
    )
    assert result == {"name": "Sales", "folder": "Finance"}
    assert "description" not in result


def test_build_definition_preserves_falsy_non_none() -> None:
    result = build_definition(
        required={"name": "Sales"},
        optional={"hidden": False, "count": 0, "label": ""},
    )
    assert result["hidden"] is False
    assert result["count"] == 0
    assert result["label"] == ""


def test_run_command_formats_result() -> None:
    ctx = PbiContext(json_output=True)
    result = run_command(ctx, lambda: {"status": "ok"})
    assert result == {"status": "ok"}


def test_run_command_exits_on_error_oneshot() -> None:
    ctx = PbiContext(json_output=True, repl_mode=False)

    def failing_fn() -> None:
        raise RuntimeError("boom")

    with pytest.raises(SystemExit):
        run_command(ctx, failing_fn)


def test_run_command_raises_tom_error_in_repl() -> None:
    ctx = PbiContext(json_output=True, repl_mode=True)

    def failing_fn() -> None:
        raise RuntimeError("boom")

    with pytest.raises(TomError):
        run_command(ctx, failing_fn)


def test_run_command_passes_kwargs() -> None:
    ctx = PbiContext(json_output=True)

    def fn_with_args(name: str, count: int) -> dict:
        return {"name": name, "count": count}

    result = run_command(ctx, fn_with_args, name="test", count=42)
    assert result == {"name": "test", "count": 42}
