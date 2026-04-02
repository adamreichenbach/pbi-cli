"""Tests for pbi_cli.core.bookmark_backend."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pbi_cli.core.bookmark_backend import (
    SCHEMA_BOOKMARK,
    SCHEMA_BOOKMARKS_METADATA,
    bookmark_add,
    bookmark_delete,
    bookmark_get,
    bookmark_list,
    bookmark_set_visibility,
)
from pbi_cli.core.errors import PbiCliError

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def definition_path(tmp_path: Path) -> Path:
    """Return a temporary PBIR definition folder."""
    defn = tmp_path / "MyReport.Report" / "definition"
    defn.mkdir(parents=True)
    return defn


# ---------------------------------------------------------------------------
# bookmark_list
# ---------------------------------------------------------------------------


def test_bookmark_list_no_bookmarks_dir(definition_path: Path) -> None:
    """bookmark_list returns [] when the bookmarks directory does not exist."""
    result = bookmark_list(definition_path)
    assert result == []


def test_bookmark_list_empty_items(definition_path: Path) -> None:
    """bookmark_list returns [] when bookmarks.json has an empty items list."""
    bm_dir = definition_path / "bookmarks"
    bm_dir.mkdir()
    index = {"$schema": SCHEMA_BOOKMARKS_METADATA, "items": []}
    (bm_dir / "bookmarks.json").write_text(json.dumps(index), encoding="utf-8")

    result = bookmark_list(definition_path)
    assert result == []


# ---------------------------------------------------------------------------
# bookmark_add
# ---------------------------------------------------------------------------


def test_bookmark_add_creates_directory(definition_path: Path) -> None:
    """bookmark_add creates the bookmarks/ directory when it does not exist."""
    bookmark_add(definition_path, "Q1 View", "page_abc")

    assert (definition_path / "bookmarks").is_dir()


def test_bookmark_add_creates_index_file(definition_path: Path) -> None:
    """bookmark_add creates bookmarks.json with the correct schema."""
    bookmark_add(definition_path, "Q1 View", "page_abc")

    index_file = definition_path / "bookmarks" / "bookmarks.json"
    assert index_file.exists()
    data = json.loads(index_file.read_text(encoding="utf-8"))
    assert data["$schema"] == SCHEMA_BOOKMARKS_METADATA


def test_bookmark_add_returns_status_dict(definition_path: Path) -> None:
    """bookmark_add returns a status dict with the expected keys and values."""
    result = bookmark_add(definition_path, "Q1 View", "page_abc", name="mybookmark")

    assert result["status"] == "created"
    assert result["name"] == "mybookmark"
    assert result["display_name"] == "Q1 View"
    assert result["target_page"] == "page_abc"


def test_bookmark_add_writes_individual_file(definition_path: Path) -> None:
    """bookmark_add writes a .bookmark.json file with the correct structure."""
    bookmark_add(definition_path, "Sales View", "page_sales", name="bm_sales")

    bm_file = definition_path / "bookmarks" / "bm_sales.bookmark.json"
    assert bm_file.exists()
    data = json.loads(bm_file.read_text(encoding="utf-8"))
    assert data["$schema"] == SCHEMA_BOOKMARK
    assert data["name"] == "bm_sales"
    assert data["displayName"] == "Sales View"
    assert data["explorationState"]["activeSection"] == "page_sales"
    assert data["explorationState"]["version"] == "1.3"


def test_bookmark_add_auto_generates_20char_name(definition_path: Path) -> None:
    """bookmark_add generates a 20-character hex name when no name is given."""
    result = bookmark_add(definition_path, "Auto Name", "page_xyz")

    assert len(result["name"]) == 20
    assert all(c in "0123456789abcdef" for c in result["name"])


def test_bookmark_add_uses_explicit_name(definition_path: Path) -> None:
    """bookmark_add uses the caller-supplied name."""
    result = bookmark_add(definition_path, "Named", "page_x", name="custom_id")

    assert result["name"] == "custom_id"


# ---------------------------------------------------------------------------
# bookmark_list after add
# ---------------------------------------------------------------------------


def test_bookmark_list_after_add_returns_one(definition_path: Path) -> None:
    """bookmark_list returns exactly one entry after a single bookmark_add."""
    bookmark_add(definition_path, "Q1 View", "page_q1", name="bm01")

    results = bookmark_list(definition_path)
    assert len(results) == 1
    assert results[0]["name"] == "bm01"
    assert results[0]["display_name"] == "Q1 View"
    assert results[0]["active_section"] == "page_q1"


def test_bookmark_list_after_two_adds_returns_two(definition_path: Path) -> None:
    """bookmark_list returns two entries after two bookmark_add calls."""
    bookmark_add(definition_path, "View A", "page_a", name="bm_a")
    bookmark_add(definition_path, "View B", "page_b", name="bm_b")

    results = bookmark_list(definition_path)
    assert len(results) == 2
    names = {r["name"] for r in results}
    assert names == {"bm_a", "bm_b"}


# ---------------------------------------------------------------------------
# bookmark_get
# ---------------------------------------------------------------------------


def test_bookmark_get_returns_full_data(definition_path: Path) -> None:
    """bookmark_get returns the complete bookmark JSON dict."""
    bookmark_add(definition_path, "Full View", "page_full", name="bm_full")

    data = bookmark_get(definition_path, "bm_full")
    assert data["name"] == "bm_full"
    assert data["displayName"] == "Full View"
    assert "$schema" in data


def test_bookmark_get_raises_for_unknown_name(definition_path: Path) -> None:
    """bookmark_get raises PbiCliError when the bookmark name does not exist."""
    with pytest.raises(PbiCliError, match="not found"):
        bookmark_get(definition_path, "nonexistent_bm")


# ---------------------------------------------------------------------------
# bookmark_delete
# ---------------------------------------------------------------------------


def test_bookmark_delete_removes_file(definition_path: Path) -> None:
    """bookmark_delete removes the .bookmark.json file from disk."""
    bookmark_add(definition_path, "Temp", "page_temp", name="bm_temp")
    bm_file = definition_path / "bookmarks" / "bm_temp.bookmark.json"
    assert bm_file.exists()

    bookmark_delete(definition_path, "bm_temp")

    assert not bm_file.exists()


def test_bookmark_delete_removes_from_index(definition_path: Path) -> None:
    """bookmark_delete removes the name from the bookmarks.json items list."""
    bookmark_add(definition_path, "Temp", "page_temp", name="bm_del")
    bookmark_delete(definition_path, "bm_del")

    index_file = definition_path / "bookmarks" / "bookmarks.json"
    index = json.loads(index_file.read_text(encoding="utf-8"))
    names_in_index = [i.get("name") for i in index.get("items", [])]
    assert "bm_del" not in names_in_index


def test_bookmark_delete_raises_for_unknown_name(definition_path: Path) -> None:
    """bookmark_delete raises PbiCliError when the bookmark does not exist."""
    with pytest.raises(PbiCliError, match="not found"):
        bookmark_delete(definition_path, "no_such_bookmark")


def test_bookmark_list_after_delete_returns_n_minus_one(definition_path: Path) -> None:
    """bookmark_list returns one fewer item after a delete."""
    bookmark_add(definition_path, "Keep", "page_keep", name="bm_keep")
    bookmark_add(definition_path, "Remove", "page_remove", name="bm_remove")

    bookmark_delete(definition_path, "bm_remove")

    results = bookmark_list(definition_path)
    assert len(results) == 1
    assert results[0]["name"] == "bm_keep"


# ---------------------------------------------------------------------------
# bookmark_set_visibility
# ---------------------------------------------------------------------------


def test_bookmark_set_visibility_hide_sets_display_mode(definition_path: Path) -> None:
    """set_visibility with hidden=True writes display.mode='hidden' on singleVisual."""
    bookmark_add(definition_path, "Hide Test", "page_a", name="bm_hide")

    result = bookmark_set_visibility(definition_path, "bm_hide", "page_a", "visual_x", hidden=True)

    assert result["status"] == "updated"
    assert result["hidden"] is True

    bm_file = definition_path / "bookmarks" / "bm_hide.bookmark.json"
    data = json.loads(bm_file.read_text(encoding="utf-8"))
    single = data["explorationState"]["sections"]["page_a"]["visualContainers"]["visual_x"][
        "singleVisual"
    ]
    assert single["display"] == {"mode": "hidden"}


def test_bookmark_set_visibility_show_removes_display_key(definition_path: Path) -> None:
    """set_visibility with hidden=False removes the display key from singleVisual."""
    bookmark_add(definition_path, "Show Test", "page_b", name="bm_show")

    # First hide it, then show it
    bookmark_set_visibility(definition_path, "bm_show", "page_b", "visual_y", hidden=True)
    bookmark_set_visibility(definition_path, "bm_show", "page_b", "visual_y", hidden=False)

    bm_file = definition_path / "bookmarks" / "bm_show.bookmark.json"
    data = json.loads(bm_file.read_text(encoding="utf-8"))
    single = data["explorationState"]["sections"]["page_b"]["visualContainers"]["visual_y"][
        "singleVisual"
    ]
    assert "display" not in single


def test_bookmark_set_visibility_creates_path_if_absent(definition_path: Path) -> None:
    """set_visibility creates the sections/visualContainers path if not present."""
    bookmark_add(definition_path, "New Path", "page_c", name="bm_newpath")

    # The bookmark was created without any sections; the function should create them.
    bookmark_set_visibility(definition_path, "bm_newpath", "page_c", "visual_z", hidden=True)

    bm_file = definition_path / "bookmarks" / "bm_newpath.bookmark.json"
    data = json.loads(bm_file.read_text(encoding="utf-8"))
    assert "page_c" in data["explorationState"]["sections"]
    assert "visual_z" in (data["explorationState"]["sections"]["page_c"]["visualContainers"])


def test_bookmark_set_visibility_preserves_existing_single_visual_keys(
    definition_path: Path,
) -> None:
    """set_visibility keeps existing singleVisual keys (e.g. visualType)."""
    bookmark_add(definition_path, "Preserve", "page_d", name="bm_preserve")

    # Pre-populate a singleVisual with a visualType key via set_visibility helper
    bookmark_set_visibility(definition_path, "bm_preserve", "page_d", "visual_w", hidden=False)

    # Manually inject a visualType into the singleVisual
    bm_file = definition_path / "bookmarks" / "bm_preserve.bookmark.json"
    raw = json.loads(bm_file.read_text(encoding="utf-8"))
    raw["explorationState"]["sections"]["page_d"]["visualContainers"]["visual_w"]["singleVisual"][
        "visualType"
    ] = "barChart"
    bm_file.write_text(json.dumps(raw, indent=2), encoding="utf-8")

    # Now hide and verify visualType is retained
    bookmark_set_visibility(definition_path, "bm_preserve", "page_d", "visual_w", hidden=True)

    updated = json.loads(bm_file.read_text(encoding="utf-8"))
    single = updated["explorationState"]["sections"]["page_d"]["visualContainers"]["visual_w"][
        "singleVisual"
    ]
    assert single["visualType"] == "barChart"
    assert single["display"] == {"mode": "hidden"}


def test_bookmark_set_visibility_raises_for_unknown_bookmark(
    definition_path: Path,
) -> None:
    """set_visibility raises PbiCliError when the bookmark does not exist."""
    with pytest.raises(PbiCliError, match="not found"):
        bookmark_set_visibility(definition_path, "nonexistent", "page_x", "visual_x", hidden=True)
