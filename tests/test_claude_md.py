"""Tests for CLAUDE.md snippet injection and removal."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def tmp_claude_md(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect CLAUDE_MD_PATH to a temp directory."""
    claude_md = tmp_path / ".claude" / "CLAUDE.md"
    monkeypatch.setattr("pbi_cli.core.claude_integration.CLAUDE_MD_PATH", claude_md)
    return claude_md


def _get_funcs():
    """Lazy import to avoid circular import at collection time."""
    from pbi_cli.core.claude_integration import (
        _PBI_CLI_MARKER_END,
        _PBI_CLI_MARKER_START,
        ensure_claude_md_snippet,
        remove_claude_md_snippet,
    )

    return (
        ensure_claude_md_snippet,
        remove_claude_md_snippet,
        _PBI_CLI_MARKER_START,
        _PBI_CLI_MARKER_END,
    )


class TestEnsureClaudeMdSnippet:
    def test_creates_file_when_missing(self, tmp_claude_md: Path) -> None:
        ensure, _, start, end = _get_funcs()
        assert not tmp_claude_md.exists()
        ensure()
        assert tmp_claude_md.exists()
        content = tmp_claude_md.read_text(encoding="utf-8")
        assert start in content
        assert end in content
        assert "power-bi-dax" in content

    def test_appends_to_existing(self, tmp_claude_md: Path) -> None:
        ensure, _, start, end = _get_funcs()
        tmp_claude_md.parent.mkdir(parents=True, exist_ok=True)
        tmp_claude_md.write_text("# My Preferences\n\n- No em dashes\n", encoding="utf-8")
        ensure()
        content = tmp_claude_md.read_text(encoding="utf-8")
        assert content.startswith("# My Preferences")
        assert "- No em dashes" in content
        assert start in content
        assert end in content

    def test_is_idempotent(self, tmp_claude_md: Path) -> None:
        ensure, _, _, _ = _get_funcs()
        tmp_claude_md.parent.mkdir(parents=True, exist_ok=True)
        tmp_claude_md.write_text("# Existing\n", encoding="utf-8")
        ensure()
        first_content = tmp_claude_md.read_text(encoding="utf-8")
        ensure()
        second_content = tmp_claude_md.read_text(encoding="utf-8")
        assert first_content == second_content


class TestRemoveClaudeMdSnippet:
    def test_removes_snippet(self, tmp_claude_md: Path) -> None:
        ensure, remove, start, end = _get_funcs()
        tmp_claude_md.parent.mkdir(parents=True, exist_ok=True)
        tmp_claude_md.write_text("# Existing\n", encoding="utf-8")
        ensure()
        assert start in tmp_claude_md.read_text(encoding="utf-8")
        remove()
        content = tmp_claude_md.read_text(encoding="utf-8")
        assert start not in content
        assert end not in content

    def test_preserves_other_content(self, tmp_claude_md: Path) -> None:
        ensure, remove, start, _ = _get_funcs()
        tmp_claude_md.parent.mkdir(parents=True, exist_ok=True)
        tmp_claude_md.write_text("# My Preferences\n\n- No em dashes\n", encoding="utf-8")
        ensure()
        remove()
        content = tmp_claude_md.read_text(encoding="utf-8")
        assert "# My Preferences" in content
        assert "- No em dashes" in content
        assert start not in content

    def test_noop_when_not_present(self, tmp_claude_md: Path) -> None:
        _, remove, _, _ = _get_funcs()
        tmp_claude_md.parent.mkdir(parents=True, exist_ok=True)
        original = "# My Preferences\n\n- No em dashes\n"
        tmp_claude_md.write_text(original, encoding="utf-8")
        remove()
        assert tmp_claude_md.read_text(encoding="utf-8") == original

    def test_noop_when_file_missing(self, tmp_claude_md: Path) -> None:
        _, remove, _, _ = _get_funcs()
        assert not tmp_claude_md.exists()
        remove()  # Should not raise
        assert not tmp_claude_md.exists()
