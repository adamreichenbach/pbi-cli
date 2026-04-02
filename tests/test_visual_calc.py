"""Tests for visual calculation functions in pbi_cli.core.visual_backend.

Covers visual_calc_add, visual_calc_list, visual_calc_delete against a minimal
in-memory PBIR directory tree.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from pbi_cli.core.errors import PbiCliError
from pbi_cli.core.visual_backend import (
    visual_calc_add,
    visual_calc_delete,
    visual_calc_list,
)

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def visual_on_page(tmp_path: Path) -> tuple[Path, str, str]:
    """Build a minimal PBIR definition folder with one page and one visual.

    Returns (definition_path, page_name, visual_name).

    The visual has a minimal barChart structure with an empty Y queryState role.
    """
    definition = tmp_path / "definition"
    definition.mkdir()

    pages_dir = definition / "pages"
    pages_dir.mkdir()

    page_dir = pages_dir / "test_page"
    page_dir.mkdir()

    visuals_dir = page_dir / "visuals"
    visuals_dir.mkdir()

    visual_dir = visuals_dir / "myvisual"
    visual_dir.mkdir()

    _write_json(
        visual_dir / "visual.json",
        {
            "name": "myvisual",
            "position": {"x": 0, "y": 0, "width": 400, "height": 300, "z": 0},
            "visual": {
                "visualType": "barChart",
                "query": {
                    "queryState": {
                        "Y": {
                            "projections": [
                                {
                                    "field": {
                                        "Measure": {
                                            "Expression": {"SourceRef": {"Entity": "Sales"}},
                                            "Property": "Amount",
                                        }
                                    },
                                    "queryRef": "Sales.Amount",
                                    "nativeQueryRef": "Amount",
                                }
                            ]
                        }
                    }
                },
            },
        },
    )

    return definition, "test_page", "myvisual"


def _vfile(definition: Path, page: str, visual: str) -> Path:
    return definition / "pages" / page / "visuals" / visual / "visual.json"


# ---------------------------------------------------------------------------
# 1. visual_calc_add -- adds projection to role
# ---------------------------------------------------------------------------


def test_visual_calc_add_appends_projection(
    visual_on_page: tuple[Path, str, str],
) -> None:
    """visual_calc_add appends a NativeVisualCalculation projection to the role."""
    definition, page, visual = visual_on_page

    visual_calc_add(definition, page, visual, "Running sum", "RUNNINGSUM([Sum of Sales])")

    data = _read_json(_vfile(definition, page, visual))
    projections = data["visual"]["query"]["queryState"]["Y"]["projections"]
    # Original measure projection plus the new calc
    assert len(projections) == 2
    last = projections[-1]
    assert "NativeVisualCalculation" in last["field"]


# ---------------------------------------------------------------------------
# 2. Correct NativeVisualCalculation structure
# ---------------------------------------------------------------------------


def test_visual_calc_add_correct_structure(
    visual_on_page: tuple[Path, str, str],
) -> None:
    """Added projection has correct NativeVisualCalculation fields."""
    definition, page, visual = visual_on_page

    visual_calc_add(
        definition, page, visual, "Running sum", "RUNNINGSUM([Sum of Sales])", role="Y"
    )

    data = _read_json(_vfile(definition, page, visual))
    projections = data["visual"]["query"]["queryState"]["Y"]["projections"]
    nvc_proj = next(
        p for p in projections if "NativeVisualCalculation" in p.get("field", {})
    )
    nvc = nvc_proj["field"]["NativeVisualCalculation"]

    assert nvc["Language"] == "dax"
    assert nvc["Expression"] == "RUNNINGSUM([Sum of Sales])"
    assert nvc["Name"] == "Running sum"


# ---------------------------------------------------------------------------
# 3. queryRef is "select", nativeQueryRef equals calc_name
# ---------------------------------------------------------------------------


def test_visual_calc_add_query_refs(
    visual_on_page: tuple[Path, str, str],
) -> None:
    """queryRef is always 'select' and nativeQueryRef equals the calc name."""
    definition, page, visual = visual_on_page

    visual_calc_add(definition, page, visual, "My Calc", "RANK()")

    data = _read_json(_vfile(definition, page, visual))
    projections = data["visual"]["query"]["queryState"]["Y"]["projections"]
    nvc_proj = next(
        p for p in projections if "NativeVisualCalculation" in p.get("field", {})
    )

    assert nvc_proj["queryRef"] == "select"
    assert nvc_proj["nativeQueryRef"] == "My Calc"


# ---------------------------------------------------------------------------
# 4. visual_calc_list returns [] before any calcs added
# ---------------------------------------------------------------------------


def test_visual_calc_list_empty_before_add(
    visual_on_page: tuple[Path, str, str],
) -> None:
    """visual_calc_list returns an empty list when no calcs have been added."""
    definition, page, visual = visual_on_page

    result = visual_calc_list(definition, page, visual)

    assert result == []


# ---------------------------------------------------------------------------
# 5. visual_calc_list returns 1 item after add
# ---------------------------------------------------------------------------


def test_visual_calc_list_one_after_add(
    visual_on_page: tuple[Path, str, str],
) -> None:
    """visual_calc_list returns exactly one item after adding one calculation."""
    definition, page, visual = visual_on_page

    visual_calc_add(definition, page, visual, "Running sum", "RUNNINGSUM([Sales])")
    result = visual_calc_list(definition, page, visual)

    assert len(result) == 1


# ---------------------------------------------------------------------------
# 6. visual_calc_list returns correct name/expression/role
# ---------------------------------------------------------------------------


def test_visual_calc_list_correct_fields(
    visual_on_page: tuple[Path, str, str],
) -> None:
    """visual_calc_list returns correct name, expression, role, and query_ref."""
    definition, page, visual = visual_on_page

    visual_calc_add(definition, page, visual, "Running sum", "RUNNINGSUM([Sales])", role="Y")
    result = visual_calc_list(definition, page, visual)

    assert len(result) == 1
    item = result[0]
    assert item["name"] == "Running sum"
    assert item["expression"] == "RUNNINGSUM([Sales])"
    assert item["role"] == "Y"
    assert item["query_ref"] == "select"


# ---------------------------------------------------------------------------
# 7. visual_calc_add is idempotent (same name replaces, not duplicates)
# ---------------------------------------------------------------------------


def test_visual_calc_add_idempotent(
    visual_on_page: tuple[Path, str, str],
) -> None:
    """Adding a calc with the same name replaces the existing one, not duplicates."""
    definition, page, visual = visual_on_page

    visual_calc_add(definition, page, visual, "Running sum", "RUNNINGSUM([Sales])")
    visual_calc_add(definition, page, visual, "Running sum", "RUNNINGSUM([Revenue])")

    result = visual_calc_list(definition, page, visual)

    # Still exactly one NativeVisualCalculation named "Running sum"
    running_sum_items = [r for r in result if r["name"] == "Running sum"]
    assert len(running_sum_items) == 1
    assert running_sum_items[0]["expression"] == "RUNNINGSUM([Revenue])"


# ---------------------------------------------------------------------------
# 8. visual_calc_add to non-existent role creates the role
# ---------------------------------------------------------------------------


def test_visual_calc_add_creates_new_role(
    visual_on_page: tuple[Path, str, str],
) -> None:
    """Adding a calc to a role that does not exist creates that role."""
    definition, page, visual = visual_on_page

    visual_calc_add(definition, page, visual, "My Rank", "RANK()", role="Values")

    data = _read_json(_vfile(definition, page, visual))
    assert "Values" in data["visual"]["query"]["queryState"]
    projections = data["visual"]["query"]["queryState"]["Values"]["projections"]
    assert len(projections) == 1
    assert "NativeVisualCalculation" in projections[0]["field"]


# ---------------------------------------------------------------------------
# 9. Two different calcs: list returns 2
# ---------------------------------------------------------------------------


def test_visual_calc_add_two_calcs_list_returns_two(
    visual_on_page: tuple[Path, str, str],
) -> None:
    """Adding two distinct calcs results in two items returned by calc-list."""
    definition, page, visual = visual_on_page

    visual_calc_add(definition, page, visual, "Running sum", "RUNNINGSUM([Sales])")
    visual_calc_add(definition, page, visual, "Rank", "RANK()")

    result = visual_calc_list(definition, page, visual)

    assert len(result) == 2
    names = {r["name"] for r in result}
    assert names == {"Running sum", "Rank"}


# ---------------------------------------------------------------------------
# 10. visual_calc_delete removes the projection
# ---------------------------------------------------------------------------


def test_visual_calc_delete_removes_projection(
    visual_on_page: tuple[Path, str, str],
) -> None:
    """visual_calc_delete removes the named NativeVisualCalculation projection."""
    definition, page, visual = visual_on_page

    visual_calc_add(definition, page, visual, "Running sum", "RUNNINGSUM([Sales])")
    visual_calc_delete(definition, page, visual, "Running sum")

    data = _read_json(_vfile(definition, page, visual))
    projections = data["visual"]["query"]["queryState"]["Y"]["projections"]
    nvc_projections = [
        p for p in projections if "NativeVisualCalculation" in p.get("field", {})
    ]
    assert nvc_projections == []


# ---------------------------------------------------------------------------
# 11. visual_calc_delete raises PbiCliError for unknown name
# ---------------------------------------------------------------------------


def test_visual_calc_delete_raises_for_unknown_name(
    visual_on_page: tuple[Path, str, str],
) -> None:
    """visual_calc_delete raises PbiCliError when the calc name does not exist."""
    definition, page, visual = visual_on_page

    with pytest.raises(PbiCliError, match="not found"):
        visual_calc_delete(definition, page, visual, "Nonexistent Calc")


# ---------------------------------------------------------------------------
# 12. visual_calc_list after delete returns N-1
# ---------------------------------------------------------------------------


def test_visual_calc_list_after_delete_returns_n_minus_one(
    visual_on_page: tuple[Path, str, str],
) -> None:
    """visual_calc_list returns N-1 items after deleting one of N calcs."""
    definition, page, visual = visual_on_page

    visual_calc_add(definition, page, visual, "Running sum", "RUNNINGSUM([Sales])")
    visual_calc_add(definition, page, visual, "Rank", "RANK()")

    assert len(visual_calc_list(definition, page, visual)) == 2

    visual_calc_delete(definition, page, visual, "Running sum")
    result = visual_calc_list(definition, page, visual)

    assert len(result) == 1
    assert result[0]["name"] == "Rank"
