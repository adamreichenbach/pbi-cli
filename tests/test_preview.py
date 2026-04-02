"""Tests for PBIR preview renderer and file watcher."""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import pytest

from pbi_cli.preview.renderer import render_page, render_report
from pbi_cli.preview.watcher import PbirWatcher


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


@pytest.fixture
def preview_report(tmp_path: Path) -> Path:
    """Build a PBIR report suitable for preview rendering."""
    defn = tmp_path / "Test.Report" / "definition"
    defn.mkdir(parents=True)

    _write(defn / "report.json", {
        "$schema": "...",
        "themeCollection": {"baseTheme": {"name": "CY24SU06"}},
        "layoutOptimization": "Disabled",
    })
    _write(defn / "version.json", {"$schema": "...", "version": "1.0.0"})
    _write(defn / "pages" / "pages.json", {
        "$schema": "...",
        "pageOrder": ["overview"],
    })

    page_dir = defn / "pages" / "overview"
    page_dir.mkdir(parents=True)
    _write(page_dir / "page.json", {
        "$schema": "...",
        "name": "overview",
        "displayName": "Executive Overview",
        "displayOption": "FitToPage",
        "width": 1280,
        "height": 720,
        "ordinal": 0,
    })

    # Bar chart visual
    bar_dir = page_dir / "visuals" / "bar1"
    bar_dir.mkdir(parents=True)
    _write(bar_dir / "visual.json", {
        "$schema": "...",
        "name": "bar1",
        "position": {"x": 50, "y": 50, "width": 400, "height": 300, "z": 0},
        "visual": {
            "visualType": "barChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [{"queryRef": "g.Region", "field": {}}]},
                    "Y": {"projections": [{"queryRef": "s.Amount", "field": {}}]},
                },
            },
        },
    })

    # Card visual
    card_dir = page_dir / "visuals" / "card1"
    card_dir.mkdir(parents=True)
    _write(card_dir / "visual.json", {
        "$schema": "...",
        "name": "card1",
        "position": {"x": 500, "y": 50, "width": 200, "height": 120, "z": 1},
        "visual": {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Fields": {"projections": [{"queryRef": "s.Revenue", "field": {}}]},
                },
            },
        },
    })

    return defn


class TestRenderReport:
    def test_renders_html(self, preview_report: Path) -> None:
        html = render_report(preview_report)
        assert "<!DOCTYPE html>" in html

    def test_includes_theme(self, preview_report: Path) -> None:
        html = render_report(preview_report)
        assert "CY24SU06" in html

    def test_includes_page_title(self, preview_report: Path) -> None:
        html = render_report(preview_report)
        assert "Executive Overview" in html

    def test_includes_visual_types(self, preview_report: Path) -> None:
        html = render_report(preview_report)
        assert "barChart" in html
        assert "card" in html

    def test_includes_bar_chart_svg(self, preview_report: Path) -> None:
        html = render_report(preview_report)
        assert "<rect" in html  # Bar chart renders SVG rects

    def test_includes_card_value(self, preview_report: Path) -> None:
        html = render_report(preview_report)
        assert "card-value" in html

    def test_includes_binding_refs(self, preview_report: Path) -> None:
        html = render_report(preview_report)
        assert "g.Region" in html or "s.Amount" in html

    def test_includes_websocket_script(self, preview_report: Path) -> None:
        html = render_report(preview_report)
        assert "WebSocket" in html

    def test_empty_report(self, tmp_path: Path) -> None:
        defn = tmp_path / "Empty.Report" / "definition"
        defn.mkdir(parents=True)
        _write(defn / "report.json", {
            "$schema": "...",
            "themeCollection": {"baseTheme": {"name": "Default"}},
            "layoutOptimization": "Disabled",
        })
        html = render_report(defn)
        assert "No pages" in html


class TestRenderPage:
    def test_renders_single_page(self, preview_report: Path) -> None:
        html = render_page(preview_report, "overview")
        assert "Executive Overview" in html
        assert "barChart" in html

    def test_page_not_found(self, preview_report: Path) -> None:
        html = render_page(preview_report, "nonexistent")
        assert "not found" in html


class TestPbirWatcher:
    def test_detects_file_change(self, preview_report: Path) -> None:
        changes: list[bool] = []

        def on_change() -> None:
            changes.append(True)

        watcher = PbirWatcher(preview_report, on_change, interval=0.1)

        # Start watcher in background
        thread = threading.Thread(target=watcher.start, daemon=True)
        thread.start()

        # Wait for initial snapshot
        time.sleep(0.3)

        # Modify a file
        report_json = preview_report / "report.json"
        data = json.loads(report_json.read_text(encoding="utf-8"))
        data["layoutOptimization"] = "Mobile"
        report_json.write_text(json.dumps(data), encoding="utf-8")

        # Wait for detection
        time.sleep(0.5)
        watcher.stop()
        thread.join(timeout=2)

        assert len(changes) >= 1

    def test_no_false_positives(self, preview_report: Path) -> None:
        changes: list[bool] = []

        def on_change() -> None:
            changes.append(True)

        watcher = PbirWatcher(preview_report, on_change, interval=0.1)
        thread = threading.Thread(target=watcher.start, daemon=True)
        thread.start()

        # Wait without changing anything
        time.sleep(0.5)
        watcher.stop()
        thread.join(timeout=2)

        assert len(changes) == 0

    def test_stop_terminates(self, preview_report: Path) -> None:
        watcher = PbirWatcher(preview_report, lambda: None, interval=0.1)
        thread = threading.Thread(target=watcher.start, daemon=True)
        thread.start()
        time.sleep(0.2)
        watcher.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()
