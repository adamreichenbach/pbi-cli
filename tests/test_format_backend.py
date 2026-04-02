"""Tests for pbi_cli.core.format_backend.

Covers format_get, format_clear, format_background_gradient, and
format_background_measure against a minimal in-memory PBIR directory tree.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from pbi_cli.core.errors import PbiCliError
from pbi_cli.core.format_backend import (
    format_background_conditional,
    format_background_gradient,
    format_background_measure,
    format_clear,
    format_get,
)

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

PAGE_NAME = "overview"
VISUAL_NAME = "test_visual"
FIELD_PROFIT = "Sum(financials.Profit)"
FIELD_SALES = "Sum(financials.Sales)"


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _minimal_visual_json() -> dict[str, Any]:
    """Return a minimal visual.json with two bound fields and no objects."""
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/"
        "fabric/item/report/definition/visual/1.0.0/schema.json",
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {"SourceRef": {"Entity": "financials"}},
                                        "Property": "Profit",
                                    }
                                },
                                "queryRef": FIELD_PROFIT,
                                "active": True,
                            },
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {"SourceRef": {"Entity": "financials"}},
                                        "Property": "Sales",
                                    }
                                },
                                "queryRef": FIELD_SALES,
                                "active": True,
                            },
                        ]
                    }
                }
            },
        },
    }


@pytest.fixture
def report_with_visual(tmp_path: Path) -> Path:
    """Build a minimal PBIR definition folder with one page containing one visual.

    Returns the ``definition/`` path accepted by all format_* functions.

    Layout::

        <tmp_path>/
          definition/
            version.json
            report.json
            pages/
              pages.json
              overview/
                page.json
                visuals/
                  test_visual/
                    visual.json
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
            "pageOrder": [PAGE_NAME],
        },
    )

    page_dir = pages_dir / PAGE_NAME
    page_dir.mkdir()
    _write_json(
        page_dir / "page.json",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/"
            "fabric/item/report/definition/page/1.0.0/schema.json",
            "name": PAGE_NAME,
            "displayName": "Overview",
            "displayOption": "FitToPage",
            "width": 1280,
            "height": 720,
            "ordinal": 0,
        },
    )

    visuals_dir = page_dir / "visuals"
    visuals_dir.mkdir()

    visual_dir = visuals_dir / VISUAL_NAME
    visual_dir.mkdir()
    _write_json(visual_dir / "visual.json", _minimal_visual_json())

    return definition


# ---------------------------------------------------------------------------
# Helper to read saved visual.json directly
# ---------------------------------------------------------------------------


def _read_visual(definition: Path) -> dict[str, Any]:
    path = definition / "pages" / PAGE_NAME / "visuals" / VISUAL_NAME / "visual.json"
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 1. format_get on a fresh visual returns empty objects
# ---------------------------------------------------------------------------


def test_format_get_fresh_visual_returns_empty_objects(report_with_visual: Path) -> None:
    """format_get returns empty objects dict on a visual with no formatting."""
    result = format_get(report_with_visual, PAGE_NAME, VISUAL_NAME)

    assert result["visual"] == VISUAL_NAME
    assert result["objects"] == {}


# ---------------------------------------------------------------------------
# 2. format_background_gradient adds an entry to objects.values
# ---------------------------------------------------------------------------


def test_format_background_gradient_adds_entry(report_with_visual: Path) -> None:
    """format_background_gradient creates objects.values with one entry."""
    format_background_gradient(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        input_table="financials",
        input_column="Profit",
        field_query_ref=FIELD_PROFIT,
    )

    data = _read_visual(report_with_visual)
    values = data["visual"]["objects"]["values"]
    assert len(values) == 1


# ---------------------------------------------------------------------------
# 3. Gradient entry has correct FillRule.linearGradient2 structure
# ---------------------------------------------------------------------------


def test_format_background_gradient_correct_structure(report_with_visual: Path) -> None:
    """Gradient entry contains the expected FillRule.linearGradient2 keys."""
    format_background_gradient(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        input_table="financials",
        input_column="Profit",
        field_query_ref=FIELD_PROFIT,
    )

    data = _read_visual(report_with_visual)
    entry = data["visual"]["objects"]["values"][0]
    fill_rule_expr = entry["properties"]["backColor"]["solid"]["color"]["expr"]["FillRule"]
    assert "linearGradient2" in fill_rule_expr["FillRule"]
    linear = fill_rule_expr["FillRule"]["linearGradient2"]
    assert "min" in linear
    assert "max" in linear
    assert "nullColoringStrategy" in linear


# ---------------------------------------------------------------------------
# 4. Gradient entry selector.metadata matches field_query_ref
# ---------------------------------------------------------------------------


def test_format_background_gradient_selector_metadata(report_with_visual: Path) -> None:
    """Gradient entry selector.metadata equals the supplied field_query_ref."""
    format_background_gradient(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        input_table="financials",
        input_column="Profit",
        field_query_ref=FIELD_PROFIT,
    )

    data = _read_visual(report_with_visual)
    entry = data["visual"]["objects"]["values"][0]
    assert entry["selector"]["metadata"] == FIELD_PROFIT


# ---------------------------------------------------------------------------
# 5. format_background_measure adds an entry to objects.values
# ---------------------------------------------------------------------------


def test_format_background_measure_adds_entry(report_with_visual: Path) -> None:
    """format_background_measure creates objects.values with one entry."""
    format_background_measure(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        measure_table="financials",
        measure_property="Conditional Formatting Sales",
        field_query_ref=FIELD_SALES,
    )

    data = _read_visual(report_with_visual)
    values = data["visual"]["objects"]["values"]
    assert len(values) == 1


# ---------------------------------------------------------------------------
# 6. Measure entry has correct Measure expression structure
# ---------------------------------------------------------------------------


def test_format_background_measure_correct_structure(report_with_visual: Path) -> None:
    """Measure entry contains the expected Measure expression keys."""
    format_background_measure(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        measure_table="financials",
        measure_property="Conditional Formatting Sales",
        field_query_ref=FIELD_SALES,
    )

    data = _read_visual(report_with_visual)
    entry = data["visual"]["objects"]["values"][0]
    measure_expr = entry["properties"]["backColor"]["solid"]["color"]["expr"]
    assert "Measure" in measure_expr
    assert measure_expr["Measure"]["Property"] == "Conditional Formatting Sales"
    assert measure_expr["Measure"]["Expression"]["SourceRef"]["Entity"] == "financials"


# ---------------------------------------------------------------------------
# 7. Applying gradient twice (same field_query_ref) replaces, not duplicates
# ---------------------------------------------------------------------------


def test_format_background_gradient_idempotent(report_with_visual: Path) -> None:
    """Applying gradient twice on same field replaces the existing entry."""
    format_background_gradient(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        input_table="financials",
        input_column="Profit",
        field_query_ref=FIELD_PROFIT,
    )
    format_background_gradient(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        input_table="financials",
        input_column="Profit",
        field_query_ref=FIELD_PROFIT,
    )

    data = _read_visual(report_with_visual)
    values = data["visual"]["objects"]["values"]
    assert len(values) == 1


# ---------------------------------------------------------------------------
# 8. Applying gradient for different field_query_ref creates second entry
# ---------------------------------------------------------------------------


def test_format_background_gradient_different_fields(report_with_visual: Path) -> None:
    """Two different field_query_refs produce two entries in objects.values."""
    format_background_gradient(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        input_table="financials",
        input_column="Profit",
        field_query_ref=FIELD_PROFIT,
    )
    format_background_gradient(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        input_table="financials",
        input_column="Sales",
        field_query_ref=FIELD_SALES,
    )

    data = _read_visual(report_with_visual)
    values = data["visual"]["objects"]["values"]
    assert len(values) == 2
    refs = {e["selector"]["metadata"] for e in values}
    assert refs == {FIELD_PROFIT, FIELD_SALES}


# ---------------------------------------------------------------------------
# 9. format_clear sets objects to {}
# ---------------------------------------------------------------------------


def test_format_clear_sets_empty_objects(report_with_visual: Path) -> None:
    """format_clear sets visual.objects to an empty dict."""
    format_background_gradient(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        input_table="financials",
        input_column="Profit",
        field_query_ref=FIELD_PROFIT,
    )
    format_clear(report_with_visual, PAGE_NAME, VISUAL_NAME)

    data = _read_visual(report_with_visual)
    assert data["visual"]["objects"] == {}


# ---------------------------------------------------------------------------
# 10. format_clear after gradient clears the entries
# ---------------------------------------------------------------------------


def test_format_clear_removes_values(report_with_visual: Path) -> None:
    """format_clear removes objects.values that were set by gradient."""
    format_background_gradient(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        input_table="financials",
        input_column="Profit",
        field_query_ref=FIELD_PROFIT,
    )
    result = format_clear(report_with_visual, PAGE_NAME, VISUAL_NAME)

    assert result["status"] == "cleared"
    data = _read_visual(report_with_visual)
    assert "values" not in data["visual"]["objects"]


# ---------------------------------------------------------------------------
# 11. format_get after gradient returns non-empty objects
# ---------------------------------------------------------------------------


def test_format_get_after_gradient_returns_objects(report_with_visual: Path) -> None:
    """format_get returns non-empty objects after a gradient rule is applied."""
    format_background_gradient(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        input_table="financials",
        input_column="Profit",
        field_query_ref=FIELD_PROFIT,
    )

    result = format_get(report_with_visual, PAGE_NAME, VISUAL_NAME)

    assert result["visual"] == VISUAL_NAME
    assert result["objects"] != {}
    assert len(result["objects"]["values"]) == 1


# ---------------------------------------------------------------------------
# 12. format_get on missing visual raises PbiCliError
# ---------------------------------------------------------------------------


def test_format_get_missing_visual_raises(report_with_visual: Path) -> None:
    """format_get raises PbiCliError when the visual folder does not exist."""
    with pytest.raises(PbiCliError, match="not found"):
        format_get(report_with_visual, PAGE_NAME, "nonexistent_visual")


# ---------------------------------------------------------------------------
# 13. gradient + measure on different fields: objects.values has 2 entries
# ---------------------------------------------------------------------------


def test_gradient_and_measure_different_fields(report_with_visual: Path) -> None:
    """A gradient on one field and a measure rule on another yield two entries."""
    format_background_gradient(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        input_table="financials",
        input_column="Profit",
        field_query_ref=FIELD_PROFIT,
    )
    format_background_measure(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        measure_table="financials",
        measure_property="Conditional Formatting Sales",
        field_query_ref=FIELD_SALES,
    )

    data = _read_visual(report_with_visual)
    values = data["visual"]["objects"]["values"]
    assert len(values) == 2


# ---------------------------------------------------------------------------
# 14. format_background_measure with same field replaces existing entry
# ---------------------------------------------------------------------------


def test_format_background_measure_replaces_existing(report_with_visual: Path) -> None:
    """Applying measure rule twice on same field replaces the existing entry."""
    format_background_measure(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        measure_table="financials",
        measure_property="CF Sales v1",
        field_query_ref=FIELD_SALES,
    )
    format_background_measure(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        measure_table="financials",
        measure_property="CF Sales v2",
        field_query_ref=FIELD_SALES,
    )

    data = _read_visual(report_with_visual)
    values = data["visual"]["objects"]["values"]
    assert len(values) == 1
    prop = values[0]["properties"]["backColor"]["solid"]["color"]["expr"]["Measure"]["Property"]
    assert prop == "CF Sales v2"


# ---------------------------------------------------------------------------
# 15. format_clear returns correct status dict
# ---------------------------------------------------------------------------


def test_format_clear_return_value(report_with_visual: Path) -> None:
    """format_clear returns the expected status dictionary."""
    result = format_clear(report_with_visual, PAGE_NAME, VISUAL_NAME)

    assert result == {"status": "cleared", "visual": VISUAL_NAME}


# ---------------------------------------------------------------------------
# format_background_conditional
# ---------------------------------------------------------------------------

FIELD_UNITS = "Sum(financials.Units Sold)"


def test_format_background_conditional_adds_entry(report_with_visual: Path) -> None:
    """format_background_conditional creates an entry in objects.values."""
    format_background_conditional(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        input_table="financials",
        input_column="Units Sold",
        threshold=100000,
        color_hex="#12239E",
        field_query_ref=FIELD_UNITS,
    )

    data = _read_visual(report_with_visual)
    values = data["visual"]["objects"]["values"]
    assert len(values) == 1


def test_format_background_conditional_correct_structure(report_with_visual: Path) -> None:
    """Conditional entry has Conditional.Cases with ComparisonKind and color."""
    format_background_conditional(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        input_table="financials",
        input_column="Units Sold",
        threshold=100000,
        color_hex="#12239E",
        field_query_ref=FIELD_UNITS,
    )

    data = _read_visual(report_with_visual)
    entry = data["visual"]["objects"]["values"][0]
    cond_expr = entry["properties"]["backColor"]["solid"]["color"]["expr"]["Conditional"]
    assert "Cases" in cond_expr
    case = cond_expr["Cases"][0]
    comparison = case["Condition"]["Comparison"]
    assert comparison["ComparisonKind"] == 2  # gt
    assert comparison["Right"]["Literal"]["Value"] == "100000D"
    assert case["Value"]["Literal"]["Value"] == "'#12239E'"


def test_format_background_conditional_selector_metadata(report_with_visual: Path) -> None:
    """Conditional entry selector.metadata equals the supplied field_query_ref."""
    format_background_conditional(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        input_table="financials",
        input_column="Units Sold",
        threshold=100000,
        color_hex="#12239E",
        field_query_ref=FIELD_UNITS,
    )

    data = _read_visual(report_with_visual)
    entry = data["visual"]["objects"]["values"][0]
    assert entry["selector"]["metadata"] == FIELD_UNITS


def test_format_background_conditional_default_field_query_ref(
    report_with_visual: Path,
) -> None:
    """When field_query_ref is omitted, it defaults to 'Sum(table.column)'."""
    result = format_background_conditional(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        input_table="financials",
        input_column="Units Sold",
        threshold=100000,
        color_hex="#12239E",
    )

    assert result["field"] == "Sum(financials.Units Sold)"


def test_format_background_conditional_replaces_existing(report_with_visual: Path) -> None:
    """Applying conditional twice on same field_query_ref replaces the entry."""
    format_background_conditional(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        input_table="financials",
        input_column="Units Sold",
        threshold=100000,
        color_hex="#FF0000",
        field_query_ref=FIELD_UNITS,
    )
    format_background_conditional(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        input_table="financials",
        input_column="Units Sold",
        threshold=50000,
        color_hex="#00FF00",
        field_query_ref=FIELD_UNITS,
    )

    data = _read_visual(report_with_visual)
    values = data["visual"]["objects"]["values"]
    assert len(values) == 1
    case = values[0]["properties"]["backColor"]["solid"]["color"]["expr"]["Conditional"]["Cases"][0]
    assert case["Value"]["Literal"]["Value"] == "'#00FF00'"


def test_format_background_conditional_comparison_lte(report_with_visual: Path) -> None:
    """comparison='lte' maps to ComparisonKind=5."""
    format_background_conditional(
        report_with_visual,
        PAGE_NAME,
        VISUAL_NAME,
        input_table="financials",
        input_column="Units Sold",
        threshold=10000,
        color_hex="#AABBCC",
        comparison="lte",
        field_query_ref=FIELD_UNITS,
    )

    data = _read_visual(report_with_visual)
    entry = data["visual"]["objects"]["values"][0]
    kind = entry["properties"]["backColor"]["solid"]["color"]["expr"]["Conditional"]["Cases"][0][
        "Condition"
    ]["Comparison"]["ComparisonKind"]
    assert kind == 5  # lte


def test_format_background_conditional_invalid_comparison(
    report_with_visual: Path,
) -> None:
    """An unknown comparison string raises PbiCliError."""
    with pytest.raises(PbiCliError):
        format_background_conditional(
            report_with_visual,
            PAGE_NAME,
            VISUAL_NAME,
            input_table="financials",
            input_column="Units Sold",
            threshold=100,
            color_hex="#000000",
            comparison="between",
        )
