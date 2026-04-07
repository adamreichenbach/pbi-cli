"""Tests for PBIR report layer hardening fixes."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pbi_cli.core.errors import PbiCliError
from pbi_cli.core.pbir_path import _find_from_pbip
from pbi_cli.core.report_backend import report_convert, report_create
from pbi_cli.core.visual_backend import (
    visual_add,
    visual_bind,
)


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


@pytest.fixture
def report_with_page(tmp_path: Path) -> Path:
    """Build a minimal PBIR report with one page."""
    defn = tmp_path / "Test.Report" / "definition"
    defn.mkdir(parents=True)
    _write(defn / "version.json", {"$schema": "...", "version": "2.0.0"})
    _write(
        defn / "report.json",
        {
            "$schema": "...",
            "themeCollection": {"baseTheme": {"name": "CY24SU06"}},
            "layoutOptimization": "None",
        },
    )
    _write(
        defn / "pages" / "pages.json",
        {
            "$schema": "...",
            "pageOrder": ["test_page"],
            "activePageName": "test_page",
        },
    )
    page_dir = defn / "pages" / "test_page"
    page_dir.mkdir(parents=True)
    _write(
        page_dir / "page.json",
        {
            "$schema": "...",
            "name": "test_page",
            "displayName": "Test Page",
            "displayOption": "FitToPage",
            "width": 1280,
            "height": 720,
        },
    )
    (page_dir / "visuals").mkdir()
    return defn


# ---------------------------------------------------------------------------
# Fix #1: Measure detection via role heuristic
# ---------------------------------------------------------------------------


class TestMeasureDetection:
    def test_value_role_creates_measure_ref(self, report_with_page: Path) -> None:
        """--value bindings should produce Measure references, not Column."""
        visual_add(report_with_page, "test_page", "bar_chart", name="chart1")
        visual_bind(
            report_with_page,
            "test_page",
            "chart1",
            bindings=[{"role": "value", "field": "Sales[Amount]"}],
        )
        vfile = report_with_page / "pages" / "test_page" / "visuals" / "chart1" / "visual.json"
        data = json.loads(vfile.read_text(encoding="utf-8"))
        proj = data["visual"]["query"]["queryState"]["Y"]["projections"][0]
        assert "Measure" in proj["field"]
        assert "Column" not in proj["field"]

    def test_category_role_creates_column_ref(self, report_with_page: Path) -> None:
        """--category bindings should produce Column references."""
        visual_add(report_with_page, "test_page", "bar_chart", name="chart2")
        visual_bind(
            report_with_page,
            "test_page",
            "chart2",
            bindings=[{"role": "category", "field": "Date[Year]"}],
        )
        vfile = report_with_page / "pages" / "test_page" / "visuals" / "chart2" / "visual.json"
        data = json.loads(vfile.read_text(encoding="utf-8"))
        proj = data["visual"]["query"]["queryState"]["Category"]["projections"][0]
        assert "Column" in proj["field"]
        assert "Measure" not in proj["field"]

    def test_field_role_on_card_creates_measure(self, report_with_page: Path) -> None:
        """--field on card should be a Measure (Values role is the correct Desktop key)."""
        visual_add(report_with_page, "test_page", "card", name="card1")
        visual_bind(
            report_with_page,
            "test_page",
            "card1",
            bindings=[{"role": "field", "field": "Sales[Revenue]"}],
        )
        vfile = report_with_page / "pages" / "test_page" / "visuals" / "card1" / "visual.json"
        data = json.loads(vfile.read_text(encoding="utf-8"))
        proj = data["visual"]["query"]["queryState"]["Values"]["projections"][0]
        assert "Measure" in proj["field"]

    def test_explicit_measure_flag_override(self, report_with_page: Path) -> None:
        """Explicit measure=True forces Measure even on category role."""
        visual_add(report_with_page, "test_page", "bar_chart", name="chart3")
        visual_bind(
            report_with_page,
            "test_page",
            "chart3",
            bindings=[{"role": "category", "field": "Sales[Calc]", "measure": True}],
        )
        vfile = report_with_page / "pages" / "test_page" / "visuals" / "chart3" / "visual.json"
        data = json.loads(vfile.read_text(encoding="utf-8"))
        proj = data["visual"]["query"]["queryState"]["Category"]["projections"][0]
        assert "Measure" in proj["field"]


# ---------------------------------------------------------------------------
# Fix #2: visual_bind merges with existing bindings
# ---------------------------------------------------------------------------


class TestBindMerge:
    def test_second_bind_preserves_first(self, report_with_page: Path) -> None:
        """Calling bind twice should keep all bindings."""
        visual_add(report_with_page, "test_page", "bar_chart", name="merged")

        # First bind: category
        visual_bind(
            report_with_page,
            "test_page",
            "merged",
            bindings=[{"role": "category", "field": "Date[Year]"}],
        )

        # Second bind: value
        visual_bind(
            report_with_page,
            "test_page",
            "merged",
            bindings=[{"role": "value", "field": "Sales[Amount]"}],
        )

        vfile = report_with_page / "pages" / "test_page" / "visuals" / "merged" / "visual.json"
        data = json.loads(vfile.read_text(encoding="utf-8"))
        query = data["visual"]["query"]

        # Both roles should have projections
        assert len(query["queryState"]["Category"]["projections"]) == 1
        assert len(query["queryState"]["Y"]["projections"]) == 1

        # PBIR 2.7.0: Commands is a legacy binary format field - must not be present
        assert "Commands" not in query


# ---------------------------------------------------------------------------
# Fix #3: Table names with spaces
# ---------------------------------------------------------------------------


class TestFieldRefParsing:
    def test_table_with_spaces(self, report_with_page: Path) -> None:
        """Table[Column] notation should work with spaces in table name."""
        visual_add(report_with_page, "test_page", "bar_chart", name="spaces")
        result = visual_bind(
            report_with_page,
            "test_page",
            "spaces",
            bindings=[{"role": "category", "field": "Sales Table[Region Name]"}],
        )
        assert result["bindings"][0]["query_ref"] == "Sales Table.Region Name"

    def test_simple_names(self, report_with_page: Path) -> None:
        """Standard Table[Column] still works."""
        visual_add(report_with_page, "test_page", "bar_chart", name="simple")
        result = visual_bind(
            report_with_page,
            "test_page",
            "simple",
            bindings=[{"role": "category", "field": "Date[Year]"}],
        )
        assert result["bindings"][0]["query_ref"] == "Date.Year"

    def test_invalid_format_raises(self, report_with_page: Path) -> None:
        """Missing brackets should raise PbiCliError."""
        visual_add(report_with_page, "test_page", "card", name="bad")
        with pytest.raises(PbiCliError, match="Table\\[Column\\]"):
            visual_bind(
                report_with_page,
                "test_page",
                "bad",
                bindings=[{"role": "field", "field": "JustAName"}],
            )


# ---------------------------------------------------------------------------
# Fix #4: _find_from_pbip guard
# ---------------------------------------------------------------------------


class TestPbipGuard:
    def test_nonexistent_dir_returns_none(self, tmp_path: Path) -> None:
        result = _find_from_pbip(tmp_path / "does_not_exist")
        assert result is None

    def test_file_instead_of_dir_returns_none(self, tmp_path: Path) -> None:
        f = tmp_path / "afile.txt"
        f.write_text("x")
        result = _find_from_pbip(f)
        assert result is None


# ---------------------------------------------------------------------------
# Fix #9: report_convert overwrite guard
# ---------------------------------------------------------------------------


class TestConvertGuard:
    def test_convert_blocks_overwrite(self, tmp_path: Path) -> None:
        """Second convert without --force should raise."""
        report_create(tmp_path, "MyReport")
        # First convert works (pbip already exists from create, so it should block)
        with pytest.raises(PbiCliError, match="already exists"):
            report_convert(tmp_path, force=False)

    def test_convert_force_allows_overwrite(self, tmp_path: Path) -> None:
        """--force should allow overwriting existing .pbip."""
        report_create(tmp_path, "MyReport")
        result = report_convert(tmp_path, force=True)
        assert result["status"] == "converted"
