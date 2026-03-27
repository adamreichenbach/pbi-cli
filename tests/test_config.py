"""Tests for pbi_cli.core.config."""

from __future__ import annotations

from pathlib import Path

from pbi_cli.core.config import PbiConfig, load_config, save_config


def test_default_config() -> None:
    config = PbiConfig()
    assert config.default_connection == ""


def test_with_updates_returns_new_instance() -> None:
    original = PbiConfig(default_connection="conn1")
    updated = original.with_updates(default_connection="conn2")

    assert updated.default_connection == "conn2"
    assert original.default_connection == "conn1"  # unchanged


def test_load_config_missing_file(tmp_config: Path) -> None:
    config = load_config()
    assert config.default_connection == ""


def test_save_and_load_roundtrip(tmp_config: Path) -> None:
    original = PbiConfig(default_connection="my-conn")
    save_config(original)

    loaded = load_config()
    assert loaded.default_connection == "my-conn"


def test_load_config_corrupt_json(tmp_config: Path) -> None:
    config_file = tmp_config / "config.json"
    config_file.write_text("not valid json{{{", encoding="utf-8")

    config = load_config()
    assert config.default_connection == ""  # falls back to defaults


def test_config_is_frozen() -> None:
    config = PbiConfig()
    try:
        config.default_connection = "new"  # type: ignore[misc]
        assert False, "Should have raised"
    except AttributeError:
        pass
