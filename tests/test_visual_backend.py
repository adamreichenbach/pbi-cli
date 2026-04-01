"""Tests for pbi_cli.core.visual_backend.

Covers visual_list, visual_get, visual_add, visual_update, visual_delete,
and visual_bind against a minimal in-memory PBIR directory tree.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from pbi_cli.core.errors import PbiCliError, VisualTypeError
from pbi_cli.core.visual_backend import (
    visual_add,
    visual_bind,
    visual_delete,
    visual_get,
    visual_list,
    visual_set_container,
    visual_update,
)

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


@pytest.fixture
def report_with_page(tmp_path: Path) -> Path:
    """Build a minimal PBIR definition folder with one empty page.

    Returns the ``definition/`` path (equivalent to ``definition_path``
    accepted by all visual_* functions).

    Layout::

        <tmp_path>/
          definition/
            version.json
            report.json
            pages/
              pages.json
              test_page/
                page.json
                visuals/
    """
    definition = tmp_path / "definition"
    definition.mkdir()

    _write_json(
        definition / "version.json",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/"
            "fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
            "version": "1.0.0",
        },
    )

    _write_json(
        definition / "report.json",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/"
            "fabric/item/report/definition/report/1.0.0/schema.json",
            "themeCollection": {"baseTheme": {"name": "CY24SU06"}},
            "layoutOptimization": "Disabled",
        },
    )

    pages_dir = definition / "pages"
    pages_dir.mkdir()

    _write_json(
        pages_dir / "pages.json",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/"
            "fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
            "pageOrder": ["test_page"],
        },
    )

    page_dir = pages_dir / "test_page"
    page_dir.mkdir()

    _write_json(
        page_dir / "page.json",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/"
            "fabric/item/report/definition/page/1.0.0/schema.json",
            "name": "test_page",
            "displayName": "Test Page",
            "displayOption": "FitToPage",
            "width": 1280,
            "height": 720,
            "ordinal": 0,
        },
    )

    visuals_dir = page_dir / "visuals"
    visuals_dir.mkdir()

    return definition


# ---------------------------------------------------------------------------
# 1. visual_list - empty page
# ---------------------------------------------------------------------------


def test_visual_list_empty(report_with_page: Path) -> None:
    """visual_list returns an empty list when no visuals have been added."""
    result = visual_list(report_with_page, "test_page")

    assert result == []


# ---------------------------------------------------------------------------
# 2-6. visual_add - correct type resolution per visual type
# ---------------------------------------------------------------------------


def test_visual_add_bar_chart(report_with_page: Path) -> None:
    """visual_add with 'bar_chart' alias creates a barChart visual."""
    result = visual_add(report_with_page, "test_page", "bar_chart", name="mybar")

    assert result["status"] == "created"
    assert result["visual_type"] == "barChart"
    assert result["name"] == "mybar"
    assert result["page"] == "test_page"

    # Confirm the file was written with the correct visualType
    vfile = report_with_page / "pages" / "test_page" / "visuals" / "mybar" / "visual.json"
    assert vfile.exists()
    data = json.loads(vfile.read_text(encoding="utf-8"))
    assert data["visual"]["visualType"] == "barChart"


def test_visual_add_line_chart(report_with_page: Path) -> None:
    """visual_add with 'line_chart' alias creates a lineChart visual."""
    result = visual_add(report_with_page, "test_page", "line_chart", name="myline")

    assert result["status"] == "created"
    assert result["visual_type"] == "lineChart"

    vfile = report_with_page / "pages" / "test_page" / "visuals" / "myline" / "visual.json"
    data = json.loads(vfile.read_text(encoding="utf-8"))
    assert data["visual"]["visualType"] == "lineChart"


def test_visual_add_card(report_with_page: Path) -> None:
    """visual_add with 'card' creates a card visual with smaller default size."""
    result = visual_add(report_with_page, "test_page", "card", name="mycard")

    assert result["status"] == "created"
    assert result["visual_type"] == "card"
    # card default size: 200 x 120
    assert result["width"] == 200
    assert result["height"] == 120


def test_visual_add_table(report_with_page: Path) -> None:
    """visual_add with 'table' alias resolves to tableEx."""
    result = visual_add(report_with_page, "test_page", "table", name="mytable")

    assert result["status"] == "created"
    assert result["visual_type"] == "tableEx"

    vfile = (
        report_with_page / "pages" / "test_page" / "visuals" / "mytable" / "visual.json"
    )
    data = json.loads(vfile.read_text(encoding="utf-8"))
    assert data["visual"]["visualType"] == "tableEx"


def test_visual_add_matrix(report_with_page: Path) -> None:
    """visual_add with 'matrix' alias resolves to pivotTable."""
    result = visual_add(report_with_page, "test_page", "matrix", name="mymatrix")

    assert result["status"] == "created"
    assert result["visual_type"] == "pivotTable"

    vfile = (
        report_with_page / "pages" / "test_page" / "visuals" / "mymatrix" / "visual.json"
    )
    data = json.loads(vfile.read_text(encoding="utf-8"))
    assert data["visual"]["visualType"] == "pivotTable"


# ---------------------------------------------------------------------------
# 7. visual_add - custom position and size
# ---------------------------------------------------------------------------


def test_visual_add_custom_position(report_with_page: Path) -> None:
    """Explicitly provided x, y, width, height are stored verbatim."""
    result = visual_add(
        report_with_page,
        "test_page",
        "bar_chart",
        name="positioned",
        x=100.0,
        y=200.0,
        width=600.0,
        height=450.0,
    )

    assert result["x"] == 100.0
    assert result["y"] == 200.0
    assert result["width"] == 600.0
    assert result["height"] == 450.0

    vfile = (
        report_with_page
        / "pages"
        / "test_page"
        / "visuals"
        / "positioned"
        / "visual.json"
    )
    data = json.loads(vfile.read_text(encoding="utf-8"))
    pos = data["position"]
    assert pos["x"] == 100.0
    assert pos["y"] == 200.0
    assert pos["width"] == 600.0
    assert pos["height"] == 450.0


# ---------------------------------------------------------------------------
# 8. visual_add - auto-generated name
# ---------------------------------------------------------------------------


def test_visual_add_auto_name(report_with_page: Path) -> None:
    """When name is omitted, a non-empty hex name is generated."""
    result = visual_add(report_with_page, "test_page", "card")

    generated_name = result["name"]
    assert generated_name  # truthy, not empty
    assert isinstance(generated_name, str)

    # The visual directory should exist under that generated name
    vdir = report_with_page / "pages" / "test_page" / "visuals" / generated_name
    assert vdir.is_dir()
    assert (vdir / "visual.json").exists()


# ---------------------------------------------------------------------------
# 9. visual_add - invalid visual type
# ---------------------------------------------------------------------------


def test_visual_add_invalid_type(report_with_page: Path) -> None:
    """Requesting an unsupported visual type raises VisualTypeError."""
    with pytest.raises(VisualTypeError):
        visual_add(report_with_page, "test_page", "heatmap_3d", name="bad")


# ---------------------------------------------------------------------------
# 10. visual_add - page not found
# ---------------------------------------------------------------------------


def test_visual_add_page_not_found(report_with_page: Path) -> None:
    """Adding a visual to a non-existent page raises PbiCliError."""
    with pytest.raises(PbiCliError):
        visual_add(report_with_page, "ghost_page", "bar_chart", name="v1")


# ---------------------------------------------------------------------------
# 11. visual_list - after adding visuals
# ---------------------------------------------------------------------------


def test_visual_list_with_visuals(report_with_page: Path) -> None:
    """visual_list returns one entry per visual added."""
    visual_add(report_with_page, "test_page", "bar_chart", name="v1")
    visual_add(report_with_page, "test_page", "card", name="v2")

    result = visual_list(report_with_page, "test_page")

    names = {v["name"] for v in result}
    assert "v1" in names
    assert "v2" in names
    assert len(result) == 2

    v1 = next(v for v in result if v["name"] == "v1")
    assert v1["visual_type"] == "barChart"

    v2 = next(v for v in result if v["name"] == "v2")
    assert v2["visual_type"] == "card"


# ---------------------------------------------------------------------------
# 12. visual_get - returns correct data
# ---------------------------------------------------------------------------


def test_visual_get(report_with_page: Path) -> None:
    """visual_get returns the full detail dict matching what was created."""
    visual_add(
        report_with_page,
        "test_page",
        "bar_chart",
        name="detail_bar",
        x=10.0,
        y=20.0,
        width=400.0,
        height=300.0,
    )

    result = visual_get(report_with_page, "test_page", "detail_bar")

    assert result["name"] == "detail_bar"
    assert result["visual_type"] == "barChart"
    assert result["x"] == 10.0
    assert result["y"] == 20.0
    assert result["width"] == 400.0
    assert result["height"] == 300.0
    assert result["is_hidden"] is False
    assert "bindings" in result
    assert isinstance(result["bindings"], list)


# ---------------------------------------------------------------------------
# 13. visual_get - not found
# ---------------------------------------------------------------------------


def test_visual_get_not_found(report_with_page: Path) -> None:
    """visual_get raises PbiCliError when the visual does not exist."""
    with pytest.raises(PbiCliError):
        visual_get(report_with_page, "test_page", "nonexistent_visual")


# ---------------------------------------------------------------------------
# 14. visual_update - position fields
# ---------------------------------------------------------------------------


def test_visual_update_position(report_with_page: Path) -> None:
    """visual_update changes x, y, width, and height in visual.json."""
    visual_add(
        report_with_page,
        "test_page",
        "bar_chart",
        name="movable",
        x=0.0,
        y=0.0,
        width=100.0,
        height=100.0,
    )

    result = visual_update(
        report_with_page,
        "test_page",
        "movable",
        x=50.0,
        y=75.0,
        width=350.0,
        height=250.0,
    )

    assert result["status"] == "updated"
    assert result["name"] == "movable"
    assert result["position"]["x"] == 50.0
    assert result["position"]["y"] == 75.0
    assert result["position"]["width"] == 350.0
    assert result["position"]["height"] == 250.0

    # Confirm the file on disk reflects the change
    vfile = (
        report_with_page / "pages" / "test_page" / "visuals" / "movable" / "visual.json"
    )
    data = json.loads(vfile.read_text(encoding="utf-8"))
    pos = data["position"]
    assert pos["x"] == 50.0
    assert pos["y"] == 75.0
    assert pos["width"] == 350.0
    assert pos["height"] == 250.0


# ---------------------------------------------------------------------------
# 15. visual_update - hidden flag
# ---------------------------------------------------------------------------


def test_visual_update_hidden(report_with_page: Path) -> None:
    """visual_update with hidden=True writes isHidden into visual.json."""
    visual_add(report_with_page, "test_page", "card", name="hideable")

    visual_update(report_with_page, "test_page", "hideable", hidden=True)

    # visual_get must reflect the new isHidden value
    detail = visual_get(report_with_page, "test_page", "hideable")
    assert detail["is_hidden"] is True

    # Round-trip: unhide
    visual_update(report_with_page, "test_page", "hideable", hidden=False)
    detail = visual_get(report_with_page, "test_page", "hideable")
    assert detail["is_hidden"] is False


# ---------------------------------------------------------------------------
# 16. visual_delete - removes the directory
# ---------------------------------------------------------------------------


def test_visual_delete(report_with_page: Path) -> None:
    """visual_delete removes the visual directory and its contents."""
    visual_add(report_with_page, "test_page", "bar_chart", name="doomed")

    vdir = report_with_page / "pages" / "test_page" / "visuals" / "doomed"
    assert vdir.is_dir()

    result = visual_delete(report_with_page, "test_page", "doomed")

    assert result["status"] == "deleted"
    assert result["name"] == "doomed"
    assert result["page"] == "test_page"
    assert not vdir.exists()

    # visual_list must no longer include this visual
    remaining = visual_list(report_with_page, "test_page")
    assert all(v["name"] != "doomed" for v in remaining)


# ---------------------------------------------------------------------------
# 17. visual_delete - not found
# ---------------------------------------------------------------------------


def test_visual_delete_not_found(report_with_page: Path) -> None:
    """visual_delete raises PbiCliError when the visual directory is absent."""
    with pytest.raises(PbiCliError):
        visual_delete(report_with_page, "test_page", "ghost_visual")


# ---------------------------------------------------------------------------
# 18. visual_bind - category and value roles on a barChart
# ---------------------------------------------------------------------------


def test_visual_bind_category_value(report_with_page: Path) -> None:
    """visual_bind adds Category and Y projections to a barChart."""
    visual_add(report_with_page, "test_page", "bar_chart", name="bound_bar")

    result = visual_bind(
        report_with_page,
        "test_page",
        "bound_bar",
        bindings=[
            {"role": "category", "field": "Date[Year]"},
            {"role": "value", "field": "Sales[Amount]"},
        ],
    )

    assert result["status"] == "bound"
    assert result["name"] == "bound_bar"
    assert result["page"] == "test_page"
    assert len(result["bindings"]) == 2

    roles_applied = {b["role"] for b in result["bindings"]}
    assert "Category" in roles_applied
    assert "Y" in roles_applied

    # Verify the projections were written into visual.json
    vfile = (
        report_with_page
        / "pages"
        / "test_page"
        / "visuals"
        / "bound_bar"
        / "visual.json"
    )
    data = json.loads(vfile.read_text(encoding="utf-8"))
    query_state = data["visual"]["query"]["queryState"]

    assert len(query_state["Category"]["projections"]) == 1
    assert len(query_state["Y"]["projections"]) == 1

    # queryRef uses Table.Column format (matching Desktop)
    cat_proj = query_state["Category"]["projections"][0]
    assert cat_proj["queryRef"] == "Date.Year"
    assert cat_proj["nativeQueryRef"] == "Year"

    # The semantic query Commands block should be present
    assert "Commands" in data["visual"]["query"]


# ---------------------------------------------------------------------------
# 19. visual_bind - multiple value bindings on a table
# ---------------------------------------------------------------------------


def test_visual_bind_multiple_values(report_with_page: Path) -> None:
    """visual_bind appends multiple value columns to a tableEx visual."""
    visual_add(report_with_page, "test_page", "table", name="bound_table")

    result = visual_bind(
        report_with_page,
        "test_page",
        "bound_table",
        bindings=[
            {"role": "value", "field": "Sales[Amount]"},
            {"role": "value", "field": "Sales[Quantity]"},
            {"role": "value", "field": "Sales[Discount]"},
        ],
    )

    assert result["status"] == "bound"
    assert len(result["bindings"]) == 3
    assert all(b["role"] == "Values" for b in result["bindings"])

    # Confirm all three projections landed in the Values role
    vfile = (
        report_with_page
        / "pages"
        / "test_page"
        / "visuals"
        / "bound_table"
        / "visual.json"
    )
    data = json.loads(vfile.read_text(encoding="utf-8"))
    projections = data["visual"]["query"]["queryState"]["Values"]["projections"]
    assert len(projections) == 3

    query_refs = [p["queryRef"] for p in projections]
    assert "Sales.Amount" in query_refs
    assert "Sales.Quantity" in query_refs
    assert "Sales.Discount" in query_refs


# ---------------------------------------------------------------------------
# v3.1.0 -- new visual types (Phase 1)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "alias,expected_type",
    [
        ("column", "columnChart"),
        ("column_chart", "columnChart"),
        ("area", "areaChart"),
        ("area_chart", "areaChart"),
        ("ribbon", "ribbonChart"),
        ("waterfall", "waterfallChart"),
        ("scatter", "scatterChart"),
        ("scatter_chart", "scatterChart"),
        ("funnel", "funnelChart"),
        ("multi_row_card", "multiRowCard"),
        ("treemap", "treemap"),
        ("card_new", "cardNew"),
        ("new_card", "cardNew"),
        ("stacked_bar", "stackedBarChart"),
        ("combo", "lineStackedColumnComboChart"),
        ("combo_chart", "lineStackedColumnComboChart"),
    ],
)
def test_visual_add_new_types(
    report_with_page: Path, alias: str, expected_type: str
) -> None:
    """visual_add resolves v3.1.0 type aliases and writes correct visualType."""
    result = visual_add(report_with_page, "test_page", alias, name=f"v_{alias}")

    assert result["status"] == "created"
    assert result["visual_type"] == expected_type

    vfile = (
        report_with_page / "pages" / "test_page" / "visuals" / f"v_{alias}" / "visual.json"
    )
    assert vfile.exists()
    data = json.loads(vfile.read_text(encoding="utf-8"))
    assert data["visual"]["visualType"] == expected_type


def test_visual_add_scatter_has_xyz_query_state(report_with_page: Path) -> None:
    """scatter chart template includes Details, X, Y queryState roles."""
    visual_add(report_with_page, "test_page", "scatter", name="myscatter")

    vfile = report_with_page / "pages" / "test_page" / "visuals" / "myscatter" / "visual.json"
    data = json.loads(vfile.read_text(encoding="utf-8"))
    qs = data["visual"]["query"]["queryState"]
    assert "Details" in qs
    assert "X" in qs
    assert "Y" in qs


def test_visual_add_combo_has_column_y_line_y_roles(report_with_page: Path) -> None:
    """combo chart template includes Category, ColumnY, LineY queryState roles."""
    visual_add(report_with_page, "test_page", "combo", name="mycombo")

    vfile = report_with_page / "pages" / "test_page" / "visuals" / "mycombo" / "visual.json"
    data = json.loads(vfile.read_text(encoding="utf-8"))
    qs = data["visual"]["query"]["queryState"]
    assert "Category" in qs
    assert "ColumnY" in qs
    assert "LineY" in qs


def test_visual_bind_scatter_x_y_roles(report_with_page: Path) -> None:
    """visual_bind resolves 'x' and 'y' aliases for scatterChart."""
    visual_add(report_with_page, "test_page", "scatter", name="sc1")

    result = visual_bind(
        report_with_page,
        "test_page",
        "sc1",
        [
            {"role": "x", "field": "Sales[Amount]"},
            {"role": "y", "field": "Sales[Quantity]"},
        ],
    )

    assert result["status"] == "bound"
    applied = {b["role"] for b in result["bindings"]}
    assert "X" in applied
    assert "Y" in applied


def test_visual_bind_combo_column_line_roles(report_with_page: Path) -> None:
    """visual_bind resolves 'column' and 'line' aliases for combo chart."""
    visual_add(report_with_page, "test_page", "combo", name="cb1")

    result = visual_bind(
        report_with_page,
        "test_page",
        "cb1",
        [
            {"role": "column", "field": "Sales[Revenue]"},
            {"role": "line", "field": "Sales[Margin]"},
        ],
    )

    assert result["status"] == "bound"
    applied = {b["role"] for b in result["bindings"]}
    assert "ColumnY" in applied
    assert "LineY" in applied


def test_visual_add_new_types_default_sizes(report_with_page: Path) -> None:
    """New visual types use non-zero default sizes when no dimensions given."""
    for alias in ("column", "scatter", "treemap", "multi_row_card", "combo"):
        result = visual_add(report_with_page, "test_page", alias, name=f"sz_{alias}")
        assert result["width"] > 0
        assert result["height"] > 0


# ---------------------------------------------------------------------------
# Task 1 tests -- cardVisual and actionButton
# ---------------------------------------------------------------------------

def test_visual_add_card_visual(report_with_page: Path) -> None:
    result = visual_add(
        report_with_page, "test_page", "cardVisual", x=10, y=10
    )
    assert result["status"] == "created"
    assert result["visual_type"] == "cardVisual"
    vdir = report_with_page / "pages" / "test_page" / "visuals" / result["name"]
    vfile = vdir / "visual.json"
    data = json.loads(vfile.read_text())
    assert data["visual"]["visualType"] == "cardVisual"
    assert "Data" in data["visual"]["query"]["queryState"]
    assert "sortDefinition" in data["visual"]["query"]
    assert "visualContainerObjects" in data["visual"]


def test_visual_add_card_visual_alias(report_with_page: Path) -> None:
    result = visual_add(
        report_with_page, "test_page", "card_visual", x=10, y=10
    )
    assert result["visual_type"] == "cardVisual"


def test_visual_add_action_button(report_with_page: Path) -> None:
    result = visual_add(
        report_with_page, "test_page", "actionButton", x=0, y=0
    )
    assert result["status"] == "created"
    assert result["visual_type"] == "actionButton"
    vdir = report_with_page / "pages" / "test_page" / "visuals" / result["name"]
    data = json.loads((vdir / "visual.json").read_text())
    assert data["visual"]["visualType"] == "actionButton"
    # No queryState on actionButton
    assert "query" not in data["visual"]
    assert data.get("howCreated") == "InsertVisualButton"


def test_visual_add_action_button_aliases(report_with_page: Path) -> None:
    for alias in ("action_button", "button"):
        result = visual_add(
            report_with_page, "test_page", alias, x=0, y=0
        )
        assert result["visual_type"] == "actionButton"


# ---------------------------------------------------------------------------
# Task 4 -- visual_set_container
# ---------------------------------------------------------------------------


@pytest.fixture
def page_with_bar_visual(report_with_page: Path) -> tuple[Path, str]:
    """Returns (definition_path, visual_name) for a barChart visual."""
    result = visual_add(report_with_page, "test_page", "barChart", x=0, y=0)
    return report_with_page, result["name"]


def test_visual_set_container_border_hide(
    page_with_bar_visual: tuple[Path, str],
) -> None:
    defn, vname = page_with_bar_visual
    result = visual_set_container(defn, "test_page", vname, border_show=False)
    assert result["status"] == "updated"
    vfile = defn / "pages" / "test_page" / "visuals" / vname / "visual.json"
    data = json.loads(vfile.read_text())
    border = data["visual"]["visualContainerObjects"]["border"]
    val = border[0]["properties"]["show"]["expr"]["Literal"]["Value"]
    assert val == "false"


def test_visual_set_container_background_hide(
    page_with_bar_visual: tuple[Path, str],
) -> None:
    defn, vname = page_with_bar_visual
    visual_set_container(defn, "test_page", vname, background_show=False)
    vfile = defn / "pages" / "test_page" / "visuals" / vname / "visual.json"
    data = json.loads(vfile.read_text())
    bg = data["visual"]["visualContainerObjects"]["background"]
    val = bg[0]["properties"]["show"]["expr"]["Literal"]["Value"]
    assert val == "false"


def test_visual_set_container_title_text(
    page_with_bar_visual: tuple[Path, str],
) -> None:
    defn, vname = page_with_bar_visual
    visual_set_container(defn, "test_page", vname, title="Revenue by Month")
    vfile = defn / "pages" / "test_page" / "visuals" / vname / "visual.json"
    data = json.loads(vfile.read_text())
    title = data["visual"]["visualContainerObjects"]["title"]
    val = title[0]["properties"]["text"]["expr"]["Literal"]["Value"]
    assert val == "'Revenue by Month'"


def test_visual_set_container_preserves_other_keys(
    page_with_bar_visual: tuple[Path, str],
) -> None:
    defn, vname = page_with_bar_visual
    visual_set_container(defn, "test_page", vname, border_show=False)
    visual_set_container(defn, "test_page", vname, title="My Chart")
    vfile = defn / "pages" / "test_page" / "visuals" / vname / "visual.json"
    data = json.loads(vfile.read_text())
    vco = data["visual"]["visualContainerObjects"]
    assert "border" in vco
    assert "title" in vco


def test_visual_set_container_border_show(
    page_with_bar_visual: tuple[Path, str],
) -> None:
    defn, vname = page_with_bar_visual
    visual_set_container(defn, "test_page", vname, border_show=True)
    vfile = defn / "pages" / "test_page" / "visuals" / vname / "visual.json"
    data = json.loads(vfile.read_text())
    val = data["visual"]["visualContainerObjects"]["border"][0][
        "properties"]["show"]["expr"]["Literal"]["Value"]
    assert val == "true"


def test_visual_set_container_raises_for_missing_visual(
    report_with_page: Path,
) -> None:
    with pytest.raises(PbiCliError):
        visual_set_container(
            report_with_page, "test_page", "nonexistent_visual", border_show=False
        )


def test_visual_set_container_no_op_returns_no_op_status(
    page_with_bar_visual: tuple[Path, str],
) -> None:
    defn, vname = page_with_bar_visual
    result = visual_set_container(defn, "test_page", vname)
    assert result["status"] == "no-op"


# ---------------------------------------------------------------------------
# Task 1 (bug fix): schema URL must be 2.7.0
# ---------------------------------------------------------------------------


def test_visual_add_uses_correct_schema_version(report_with_page: Path) -> None:
    result = visual_add(report_with_page, "test_page", "barChart", x=0, y=0)
    vfile = (
        report_with_page / "pages" / "test_page" / "visuals"
        / result["name"] / "visual.json"
    )
    data = json.loads(vfile.read_text())
    assert "2.7.0" in data["$schema"]
    assert "1.5.0" not in data["$schema"]


# ---------------------------------------------------------------------------
# Task 2 (bug fix): visualGroup containers tagged as type "group"
# ---------------------------------------------------------------------------


def test_visual_list_tags_group_containers_as_group(report_with_page: Path) -> None:
    """visual_list returns visual_type 'group' for visualGroup containers."""
    visuals_dir = report_with_page / "pages" / "test_page" / "visuals"
    grp_dir = visuals_dir / "grp1"
    grp_dir.mkdir()
    _write_json(grp_dir / "visual.json", {
        "$schema": "https://example.com/schema",
        "name": "grp1",
        "visualGroup": {"displayName": "Header Group", "visuals": []}
    })
    results = visual_list(report_with_page, "test_page")
    grp = next(r for r in results if r["name"] == "grp1")
    assert grp["visual_type"] == "group"


# ---------------------------------------------------------------------------
# Task 3 -- v3.5.0 new visual types
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("vtype,alias", [
    ("clusteredColumnChart", "clustered_column"),
    ("clusteredBarChart", "clustered_bar"),
    ("textSlicer", "text_slicer"),
    ("listSlicer", "list_slicer"),
])
def test_visual_add_new_v35_types(
    report_with_page: Path, vtype: str, alias: str
) -> None:
    r = visual_add(report_with_page, "test_page", vtype, x=0, y=0)
    assert r["visual_type"] == vtype
    r2 = visual_add(report_with_page, "test_page", alias, x=50, y=0)
    assert r2["visual_type"] == vtype


def test_list_slicer_template_has_active_flag(report_with_page: Path) -> None:
    r = visual_add(report_with_page, "test_page", "listSlicer", x=0, y=0)
    vfile = (
        report_with_page / "pages" / "test_page" / "visuals"
        / r["name"] / "visual.json"
    )
    data = json.loads(vfile.read_text())
    values = data["visual"]["query"]["queryState"]["Values"]
    assert values.get("active") is True


# ---------------------------------------------------------------------------
# v3.6.0 -- no-query visual types (image, shape, textbox, pageNavigator)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("vtype,alias", [
    ("image", "img"),
    ("textbox", "text_box"),
    ("pageNavigator", "page_navigator"),
    ("pageNavigator", "page_nav"),
    ("pageNavigator", "navigator"),
])
def test_visual_add_v36_alias_types(report_with_page: Path, vtype: str, alias: str) -> None:
    r = visual_add(report_with_page, "test_page", alias, x=0, y=0)
    assert r["visual_type"] == vtype


@pytest.mark.parametrize("vtype", ["image", "shape", "textbox", "pageNavigator"])
def test_visual_add_no_query_v36(report_with_page: Path, vtype: str) -> None:
    """No-query types must not have a 'query' key in the written visual.json."""
    r = visual_add(report_with_page, "test_page", vtype, x=0, y=0)
    vfile = (
        report_with_page / "pages" / "test_page" / "visuals" / r["name"] / "visual.json"
    )
    data = json.loads(vfile.read_text())
    assert "query" not in data["visual"]
    assert data["$schema"].endswith("2.7.0/schema.json")


@pytest.mark.parametrize("vtype", ["image", "shape", "pageNavigator"])
def test_insert_visual_button_how_created(report_with_page: Path, vtype: str) -> None:
    """image, shape, pageNavigator must carry howCreated at top level."""
    r = visual_add(report_with_page, "test_page", vtype, x=0, y=0)
    vfile = (
        report_with_page / "pages" / "test_page" / "visuals" / r["name"] / "visual.json"
    )
    data = json.loads(vfile.read_text())
    assert data.get("howCreated") == "InsertVisualButton"


def test_textbox_no_how_created(report_with_page: Path) -> None:
    """textbox is a content visual -- no howCreated key."""
    r = visual_add(report_with_page, "test_page", "textbox", x=0, y=0)
    vfile = (
        report_with_page / "pages" / "test_page" / "visuals" / r["name"] / "visual.json"
    )
    data = json.loads(vfile.read_text())
    assert "howCreated" not in data


# ---------------------------------------------------------------------------
# v3.6.0 -- advancedSlicerVisual
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("alias", [
    "advancedSlicerVisual", "advanced_slicer", "adv_slicer", "tile_slicer",
])
def test_advanced_slicer_aliases(report_with_page: Path, alias: str) -> None:
    r = visual_add(report_with_page, "test_page", alias, x=0, y=0)
    assert r["visual_type"] == "advancedSlicerVisual"


def test_advanced_slicer_has_values_querystate(report_with_page: Path) -> None:
    r = visual_add(report_with_page, "test_page", "advancedSlicerVisual", x=0, y=0)
    vfile = (
        report_with_page / "pages" / "test_page" / "visuals" / r["name"] / "visual.json"
    )
    data = json.loads(vfile.read_text())
    assert "query" in data["visual"]
    assert "Values" in data["visual"]["query"]["queryState"]
    assert isinstance(data["visual"]["query"]["queryState"]["Values"]["projections"], list)


# ---------------------------------------------------------------------------
# Bug fix: card and multiRowCard queryState role must be "Values" not "Fields"
# ---------------------------------------------------------------------------


def test_card_template_uses_values_role(report_with_page: Path) -> None:
    """card visual queryState must use 'Values' not 'Fields' (Desktop compat)."""
    r = visual_add(report_with_page, "test_page", "card", x=0, y=0)
    vfile = (
        report_with_page / "pages" / "test_page" / "visuals" / r["name"] / "visual.json"
    )
    data = json.loads(vfile.read_text())
    qs = data["visual"]["query"]["queryState"]
    assert "Values" in qs
    assert "Fields" not in qs


def test_multi_row_card_template_uses_values_role(report_with_page: Path) -> None:
    """multiRowCard visual queryState must use 'Values' not 'Fields'."""
    r = visual_add(report_with_page, "test_page", "multiRowCard", x=0, y=0)
    vfile = (
        report_with_page / "pages" / "test_page" / "visuals" / r["name"] / "visual.json"
    )
    data = json.loads(vfile.read_text())
    qs = data["visual"]["query"]["queryState"]
    assert "Values" in qs
    assert "Fields" not in qs
