"""Configuration management for pbi-cli.

Manages ~/.pbi-cli/config.json for user preferences.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

PBI_CLI_HOME = Path.home() / ".pbi-cli"
CONFIG_FILE = PBI_CLI_HOME / "config.json"


@dataclass(frozen=True)
class PbiConfig:
    """Immutable configuration object."""

    default_connection: str = ""

    def with_updates(self, **kwargs: object) -> PbiConfig:
        """Return a new config with the specified fields updated."""
        current = asdict(self)
        current.update(kwargs)
        return PbiConfig(**current)


def ensure_home_dir() -> Path:
    """Create ~/.pbi-cli/ if it does not exist. Returns the path."""
    PBI_CLI_HOME.mkdir(parents=True, exist_ok=True)
    return PBI_CLI_HOME


def load_config() -> PbiConfig:
    """Load config from disk. Returns defaults if file does not exist."""
    if not CONFIG_FILE.exists():
        return PbiConfig()
    try:
        raw = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        return PbiConfig(
            default_connection=raw.get("default_connection", ""),
        )
    except (json.JSONDecodeError, KeyError):
        return PbiConfig()


def save_config(config: PbiConfig) -> None:
    """Write config to disk."""
    ensure_home_dir()
    CONFIG_FILE.write_text(
        json.dumps(asdict(config), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
