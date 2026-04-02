"""Tests for enhanced PBIR validators."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pbi_cli.core.pbir_validators import (
    validate_bindings_against_model,
    validate_report_full,
)


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


@pytest.fixture
def valid_report(tmp_path: Path) -> Path:
    """Build a minimal valid PBIR report for validation tests."""
    defn = tmp_path / "Test.Report" / "definition"
    defn.mkdir(parents=True)

    _write(defn / "version.json", {"$schema": "...", "version": "1.0.0"})
    _write(defn / "report.json", {
        "$schema": "...",
        "themeCollection": {"baseTheme": {"name": "CY24SU06"}},
        "layoutOptimization": "Disabled",
    })

    page_dir = defn / "pages" / "page1"
    page_dir.mkdir(parents=True)
    _write(page_dir / "page.json", {
        "$schema": "...",
        "name": "page1",
        "displayName": "Page One",
        "displayOption": "FitToPage",
        "width": 1280,
        "height": 720,
        "ordinal": 0,
    })
    _write(defn / "pages" / "pages.json", {
        "$schema": "...",
        "pageOrder": ["page1"],
    })

    vis_dir = page_dir / "visuals" / "vis1"
    vis_dir.mkdir(parents=True)
    _write(vis_dir / "visual.json", {
        "$schema": "...",
        "name": "vis1",
        "position": {"x": 0, "y": 0, "width": 400, "height": 300},
        "visual": {"visualType": "barChart", "query": {}, "objects": {}},
    })

    return defn


class TestValidateReportFull:
    def test_valid_report_is_valid(self, valid_report: Path) -> None:
        result = validate_report_full(valid_report)
        assert result["valid"] is True
        assert result["summary"]["errors"] == 0

    def test_valid_report_has_no_warnings(self, valid_report: Path) -> None:
        result = validate_report_full(valid_report)
        assert result["summary"]["warnings"] == 0

    def test_nonexistent_dir(self, tmp_path: Path) -> None:
        result = validate_report_full(tmp_path / "nope")
        assert result["valid"] is False
        assert result["summary"]["errors"] >= 1

    def test_missing_report_json(self, valid_report: Path) -> None:
        (valid_report / "report.json").unlink()
        result = validate_report_full(valid_report)
        assert result["valid"] is False
        assert any("report.json" in e["message"] for e in result["errors"])

    def test_missing_version_json(self, valid_report: Path) -> None:
        (valid_report / "version.json").unlink()
        result = validate_report_full(valid_report)
        assert result["valid"] is False

    def test_invalid_json_syntax(self, valid_report: Path) -> None:
        (valid_report / "report.json").write_text("{bad json", encoding="utf-8")
        result = validate_report_full(valid_report)
        assert result["valid"] is False
        assert any("Invalid JSON" in e["message"] for e in result["errors"])

    def test_missing_theme_collection(self, valid_report: Path) -> None:
        _write(valid_report / "report.json", {
            "$schema": "...",
            "layoutOptimization": "Disabled",
        })
        result = validate_report_full(valid_report)
        assert result["valid"] is False
        assert any("themeCollection" in e["message"] for e in result["errors"])

    def test_missing_layout_optimization(self, valid_report: Path) -> None:
        _write(valid_report / "report.json", {
            "$schema": "...",
            "themeCollection": {"baseTheme": {"name": "CY24SU06"}},
        })
        result = validate_report_full(valid_report)
        assert result["valid"] is False
        assert any("layoutOptimization" in e["message"] for e in result["errors"])

    def test_page_missing_required_fields(self, valid_report: Path) -> None:
        _write(valid_report / "pages" / "page1" / "page.json", {
            "$schema": "...",
            "name": "page1",
        })
        result = validate_report_full(valid_report)
        assert result["valid"] is False
        assert any("displayName" in e["message"] for e in result["errors"])
        assert any("displayOption" in e["message"] for e in result["errors"])

    def test_page_invalid_display_option(self, valid_report: Path) -> None:
        _write(valid_report / "pages" / "page1" / "page.json", {
            "$schema": "...",
            "name": "page1",
            "displayName": "P1",
            "displayOption": "InvalidOption",
            "width": 1280,
            "height": 720,
        })
        result = validate_report_full(valid_report)
        assert any("Unknown displayOption" in w["message"] for w in result["warnings"])

    def test_visual_missing_position(self, valid_report: Path) -> None:
        vis_path = valid_report / "pages" / "page1" / "visuals" / "vis1" / "visual.json"
        _write(vis_path, {
            "$schema": "...",
            "name": "vis1",
            "visual": {"visualType": "barChart"},
        })
        result = validate_report_full(valid_report)
        assert result["valid"] is False
        assert any("position" in e["message"] for e in result["errors"])

    def test_visual_missing_name(self, valid_report: Path) -> None:
        vis_path = valid_report / "pages" / "page1" / "visuals" / "vis1" / "visual.json"
        _write(vis_path, {
            "$schema": "...",
            "position": {"x": 0, "y": 0, "width": 100, "height": 100},
            "visual": {"visualType": "card"},
        })
        result = validate_report_full(valid_report)
        assert result["valid"] is False
        assert any("name" in e["message"] for e in result["errors"])


class TestPageOrderConsistency:
    def test_phantom_page_in_order(self, valid_report: Path) -> None:
        _write(valid_report / "pages" / "pages.json", {
            "$schema": "...",
            "pageOrder": ["page1", "ghost_page"],
        })
        result = validate_report_full(valid_report)
        assert any("ghost_page" in w["message"] for w in result["warnings"])

    def test_unlisted_page_info(self, valid_report: Path) -> None:
        page2 = valid_report / "pages" / "page2"
        page2.mkdir(parents=True)
        _write(page2 / "page.json", {
            "$schema": "...",
            "name": "page2",
            "displayName": "Page Two",
            "displayOption": "FitToPage",
            "width": 1280,
            "height": 720,
        })
        result = validate_report_full(valid_report)
        assert any("page2" in i["message"] and "not listed" in i["message"] for i in result["info"])


class TestVisualNameUniqueness:
    def test_duplicate_visual_names(self, valid_report: Path) -> None:
        vis2_dir = valid_report / "pages" / "page1" / "visuals" / "vis2"
        vis2_dir.mkdir(parents=True)
        _write(vis2_dir / "visual.json", {
            "$schema": "...",
            "name": "vis1",  # Duplicate of vis1
            "position": {"x": 0, "y": 0, "width": 100, "height": 100},
            "visual": {"visualType": "card"},
        })
        result = validate_report_full(valid_report)
        assert result["valid"] is False
        assert any("Duplicate visual name" in e["message"] for e in result["errors"])


class TestBindingsAgainstModel:
    def test_valid_binding_passes(self, valid_report: Path) -> None:
        vis_path = valid_report / "pages" / "page1" / "visuals" / "vis1" / "visual.json"
        _write(vis_path, {
            "$schema": "...",
            "name": "vis1",
            "position": {"x": 0, "y": 0, "width": 400, "height": 300},
            "visual": {
                "visualType": "barChart",
                "query": {
                    "Commands": [{
                        "SemanticQueryDataShapeCommand": {
                            "Query": {
                                "Version": 2,
                                "From": [{"Name": "s", "Entity": "Sales", "Type": 0}],
                                "Select": [{
                                    "Column": {
                                        "Expression": {"SourceRef": {"Source": "s"}},
                                        "Property": "Region",
                                    },
                                    "Name": "s.Region",
                                }],
                            }
                        }
                    }],
                },
            },
        })
        model = [{"name": "Sales", "columns": [{"name": "Region"}], "measures": []}]
        findings = validate_bindings_against_model(valid_report, model)
        assert len(findings) == 0

    def test_invalid_binding_warns(self, valid_report: Path) -> None:
        vis_path = valid_report / "pages" / "page1" / "visuals" / "vis1" / "visual.json"
        _write(vis_path, {
            "$schema": "...",
            "name": "vis1",
            "position": {"x": 0, "y": 0, "width": 400, "height": 300},
            "visual": {
                "visualType": "barChart",
                "query": {
                    "Commands": [{
                        "SemanticQueryDataShapeCommand": {
                            "Query": {
                                "Version": 2,
                                "From": [{"Name": "s", "Entity": "Sales", "Type": 0}],
                                "Select": [{
                                    "Column": {
                                        "Expression": {"SourceRef": {"Source": "s"}},
                                        "Property": "NonExistent",
                                    },
                                    "Name": "s.NonExistent",
                                }],
                            }
                        }
                    }],
                },
            },
        })
        model = [{"name": "Sales", "columns": [{"name": "Region"}], "measures": []}]
        findings = validate_bindings_against_model(valid_report, model)
        assert len(findings) == 1
        assert findings[0].level == "warning"
        assert "NonExistent" in findings[0].message

    def test_measure_binding(self, valid_report: Path) -> None:
        vis_path = valid_report / "pages" / "page1" / "visuals" / "vis1" / "visual.json"
        _write(vis_path, {
            "$schema": "...",
            "name": "vis1",
            "position": {"x": 0, "y": 0, "width": 400, "height": 300},
            "visual": {
                "visualType": "card",
                "query": {
                    "Commands": [{
                        "SemanticQueryDataShapeCommand": {
                            "Query": {
                                "Version": 2,
                                "From": [{"Name": "s", "Entity": "Sales", "Type": 0}],
                                "Select": [{
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Source": "s"}},
                                        "Property": "Total Revenue",
                                    },
                                    "Name": "s.Total Revenue",
                                }],
                            }
                        }
                    }],
                },
            },
        })
        model = [{"name": "Sales", "columns": [], "measures": [{"name": "Total Revenue"}]}]
        findings = validate_bindings_against_model(valid_report, model)
        assert len(findings) == 0

    def test_no_commands_is_ok(self, valid_report: Path) -> None:
        findings = validate_bindings_against_model(
            valid_report,
            [{"name": "Sales", "columns": [], "measures": []}],
        )
        assert len(findings) == 0
