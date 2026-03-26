"""Tests for pbi_cli.core.config."""

from __future__ import annotations

import json
from pathlib import Path

from pbi_cli.core.config import PbiConfig, load_config, save_config


def test_default_config() -> None:
    config = PbiConfig()
    assert config.binary_version == ""
    assert config.binary_path == ""
    assert config.default_connection == ""
    assert config.binary_args == ["--start", "--skipconfirmation"]


def test_with_updates_returns_new_instance() -> None:
    original = PbiConfig(binary_version="1.0")
    updated = original.with_updates(binary_version="2.0")

    assert updated.binary_version == "2.0"
    assert original.binary_version == "1.0"  # unchanged


def test_with_updates_preserves_other_fields() -> None:
    original = PbiConfig(binary_version="1.0", binary_path="/bin/test")
    updated = original.with_updates(binary_version="2.0")

    assert updated.binary_path == "/bin/test"


def test_load_config_missing_file(tmp_config: Path) -> None:
    config = load_config()
    assert config.binary_version == ""
    assert config.binary_args == ["--start", "--skipconfirmation"]


def test_save_and_load_roundtrip(tmp_config: Path) -> None:
    original = PbiConfig(binary_version="0.4.0", binary_path="/test/path")
    save_config(original)

    loaded = load_config()
    assert loaded.binary_version == "0.4.0"
    assert loaded.binary_path == "/test/path"


def test_load_config_corrupt_json(tmp_config: Path) -> None:
    config_file = tmp_config / "config.json"
    config_file.write_text("not valid json{{{", encoding="utf-8")

    config = load_config()
    assert config.binary_version == ""  # falls back to defaults


def test_config_is_frozen() -> None:
    config = PbiConfig()
    try:
        config.binary_version = "new"  # type: ignore[misc]
        assert False, "Should have raised"
    except AttributeError:
        pass
