"""Tests for pbi_cli.core.tmdl_diff."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from pbi_cli.core.errors import PbiCliError
from pbi_cli.core.tmdl_diff import diff_tmdl_folders

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

_MODEL_TMDL = """\
model Model
\tculture: en-US
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tsourceQueryCulture: en-US

ref table Sales
ref cultureInfo en-US
"""

_RELATIONSHIPS_TMDL = """\
relationship abc-def-111
\tlineageTag: xyz
\tfromColumn: Sales.ProductID
\ttoColumn: Product.ProductID

relationship abc-def-222
\tfromColumn: Sales.CustomerID
\ttoColumn: Customer.CustomerID
"""

_SALES_TMDL = """\
table Sales
\tlineageTag: tbl-001

\tmeasure 'Total Revenue' = SUM(Sales[Amount])
\t\tformatString: "$#,0"
\t\tlineageTag: msr-001

\tcolumn Amount
\t\tdataType: decimal
\t\tlineageTag: col-001
\t\tsummarizeBy: sum
\t\tsourceColumn: Amount

\tpartition Sales = m
\t\tmode: import
\t\tsource
\t\t\tlet
\t\t\t    Source = Csv.Document(...)
\t\t\tin
\t\t\t    Source
"""

_DATE_TMDL = """\
table Date
\tlineageTag: tbl-002

\tcolumn Date
\t\tdataType: dateTime
\t\tlineageTag: col-002
\t\tsummarizeBy: none
\t\tsourceColumn: Date
"""

# Inline TMDL snippets reused across multiple tests
_NEW_MEASURE_SNIPPET = (
    "\n\tmeasure 'YTD Revenue'"
    " = CALCULATE([Total Revenue], DATESYTD('Date'[Date]))"
    "\n\t\tlineageTag: msr-new\n"
)
_TOTAL_REVENUE_BLOCK = (
    "\n\tmeasure 'Total Revenue' = SUM(Sales[Amount])"
    '\n\t\tformatString: "$#,0"'
    "\n\t\tlineageTag: msr-001\n"
)
_NEW_COL_SNIPPET = (
    "\n\tcolumn Region\n\t\tdataType: string\n\t\tsummarizeBy: none\n\t\tsourceColumn: Region\n"
)
_AMOUNT_COL_BLOCK = (
    "\n\tcolumn Amount"
    "\n\t\tdataType: decimal"
    "\n\t\tlineageTag: col-001"
    "\n\t\tsummarizeBy: sum"
    "\n\t\tsourceColumn: Amount\n"
)
_NEW_REL_SNIPPET = (
    "\nrelationship abc-def-999\n\tfromColumn: Sales.RegionID\n\ttoColumn: Region.ID\n"
)
_TRIMMED_RELS = (
    "relationship abc-def-111\n\tfromColumn: Sales.ProductID\n\ttoColumn: Product.ProductID\n"
)
_REL_222_BASE = (
    "relationship abc-def-222\n\tfromColumn: Sales.CustomerID\n\ttoColumn: Customer.CustomerID"
)
_REL_222_CHANGED = (
    "relationship abc-def-222"
    "\n\tfromColumn: Sales.CustomerID"
    "\n\ttoColumn: Customer.CustomerID"
    "\n\tcrossFilteringBehavior: bothDirections"
)


def _make_tmdl_folder(
    root: Path,
    *,
    model_text: str = _MODEL_TMDL,
    relationships_text: str = _RELATIONSHIPS_TMDL,
    tables: dict[str, str] | None = None,
) -> Path:
    """Create a minimal TMDL folder under root and return its path."""
    if tables is None:
        tables = {"Sales": _SALES_TMDL, "Date": _DATE_TMDL}
    root.mkdir(parents=True, exist_ok=True)
    (root / "model.tmdl").write_text(model_text, encoding="utf-8")
    (root / "database.tmdl").write_text("database\n\tcompatibilityLevel: 1600\n", encoding="utf-8")
    (root / "relationships.tmdl").write_text(relationships_text, encoding="utf-8")
    tables_dir = root / "tables"
    tables_dir.mkdir()
    for name, text in tables.items():
        (tables_dir / f"{name}.tmdl").write_text(text, encoding="utf-8")
    return root


def _make_semantic_model_folder(
    root: Path,
    **kwargs: Any,
) -> Path:
    """Create a SemanticModel-layout folder (definition/ subdirectory)."""
    root.mkdir(parents=True, exist_ok=True)
    defn_dir = root / "definition"
    defn_dir.mkdir()
    _make_tmdl_folder(defn_dir, **kwargs)
    (root / ".platform").write_text("{}", encoding="utf-8")
    return root


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestDiffTmdlFolders:
    def test_identical_folders_returns_no_changes(self, tmp_path: Path) -> None:
        base = _make_tmdl_folder(tmp_path / "base")
        head = _make_tmdl_folder(tmp_path / "head")
        result = diff_tmdl_folders(str(base), str(head))
        assert result["changed"] is False
        assert result["summary"]["tables_added"] == 0
        assert result["summary"]["tables_removed"] == 0
        assert result["summary"]["tables_changed"] == 0

    def test_lineage_tag_only_change_is_not_reported(self, tmp_path: Path) -> None:
        base = _make_tmdl_folder(tmp_path / "base")
        changed_sales = _SALES_TMDL.replace("tbl-001", "NEW-TAG").replace("msr-001", "NEW-MSR")
        head = _make_tmdl_folder(
            tmp_path / "head",
            tables={"Sales": changed_sales, "Date": _DATE_TMDL},
        )
        result = diff_tmdl_folders(str(base), str(head))
        assert result["changed"] is False

    def test_table_added(self, tmp_path: Path) -> None:
        product_tmdl = "table Product\n\tlineageTag: tbl-003\n\n\tcolumn ID\n\t\tdataType: int64\n"
        base = _make_tmdl_folder(tmp_path / "base")
        head = _make_tmdl_folder(
            tmp_path / "head",
            tables={"Sales": _SALES_TMDL, "Date": _DATE_TMDL, "Product": product_tmdl},
        )
        result = diff_tmdl_folders(str(base), str(head))
        assert result["changed"] is True
        assert "Product" in result["tables"]["added"]
        assert result["tables"]["removed"] == []

    def test_table_removed(self, tmp_path: Path) -> None:
        base = _make_tmdl_folder(tmp_path / "base")
        head = _make_tmdl_folder(tmp_path / "head", tables={"Sales": _SALES_TMDL})
        result = diff_tmdl_folders(str(base), str(head))
        assert "Date" in result["tables"]["removed"]

    def test_measure_added(self, tmp_path: Path) -> None:
        modified_sales = _SALES_TMDL + _NEW_MEASURE_SNIPPET
        base = _make_tmdl_folder(tmp_path / "base")
        head = _make_tmdl_folder(
            tmp_path / "head",
            tables={"Sales": modified_sales, "Date": _DATE_TMDL},
        )
        result = diff_tmdl_folders(str(base), str(head))
        assert result["changed"] is True
        sales_diff = result["tables"]["changed"]["Sales"]
        assert "YTD Revenue" in sales_diff["measures_added"]

    def test_measure_removed(self, tmp_path: Path) -> None:
        stripped_sales = _SALES_TMDL.replace(_TOTAL_REVENUE_BLOCK, "")
        base = _make_tmdl_folder(tmp_path / "base")
        head = _make_tmdl_folder(
            tmp_path / "head",
            tables={"Sales": stripped_sales, "Date": _DATE_TMDL},
        )
        result = diff_tmdl_folders(str(base), str(head))
        sales_diff = result["tables"]["changed"]["Sales"]
        assert "Total Revenue" in sales_diff["measures_removed"]

    def test_measure_expression_changed(self, tmp_path: Path) -> None:
        modified_sales = _SALES_TMDL.replace(
            "measure 'Total Revenue' = SUM(Sales[Amount])",
            "measure 'Total Revenue' = SUMX(Sales, Sales[Amount] * Sales[Qty])",
        )
        base = _make_tmdl_folder(tmp_path / "base")
        head = _make_tmdl_folder(
            tmp_path / "head",
            tables={"Sales": modified_sales, "Date": _DATE_TMDL},
        )
        result = diff_tmdl_folders(str(base), str(head))
        sales_diff = result["tables"]["changed"]["Sales"]
        assert "Total Revenue" in sales_diff["measures_changed"]

    def test_column_added(self, tmp_path: Path) -> None:
        modified_sales = _SALES_TMDL + _NEW_COL_SNIPPET
        base = _make_tmdl_folder(tmp_path / "base")
        head = _make_tmdl_folder(
            tmp_path / "head",
            tables={"Sales": modified_sales, "Date": _DATE_TMDL},
        )
        result = diff_tmdl_folders(str(base), str(head))
        sales_diff = result["tables"]["changed"]["Sales"]
        assert "Region" in sales_diff["columns_added"]

    def test_column_removed(self, tmp_path: Path) -> None:
        stripped = _SALES_TMDL.replace(_AMOUNT_COL_BLOCK, "")
        base = _make_tmdl_folder(tmp_path / "base")
        head = _make_tmdl_folder(
            tmp_path / "head",
            tables={"Sales": stripped, "Date": _DATE_TMDL},
        )
        result = diff_tmdl_folders(str(base), str(head))
        sales_diff = result["tables"]["changed"]["Sales"]
        assert "Amount" in sales_diff["columns_removed"]

    def test_relationship_added(self, tmp_path: Path) -> None:
        base = _make_tmdl_folder(tmp_path / "base")
        head = _make_tmdl_folder(
            tmp_path / "head",
            relationships_text=_RELATIONSHIPS_TMDL + _NEW_REL_SNIPPET,
        )
        result = diff_tmdl_folders(str(base), str(head))
        assert "Sales.RegionID -> Region.ID" in result["relationships"]["added"]

    def test_relationship_removed(self, tmp_path: Path) -> None:
        base = _make_tmdl_folder(tmp_path / "base")
        head = _make_tmdl_folder(tmp_path / "head", relationships_text=_TRIMMED_RELS)
        result = diff_tmdl_folders(str(base), str(head))
        assert "Sales.CustomerID -> Customer.CustomerID" in result["relationships"]["removed"]

    def test_relationship_changed(self, tmp_path: Path) -> None:
        changed_rels = _RELATIONSHIPS_TMDL.replace(_REL_222_BASE, _REL_222_CHANGED)
        base = _make_tmdl_folder(tmp_path / "base")
        head = _make_tmdl_folder(tmp_path / "head", relationships_text=changed_rels)
        result = diff_tmdl_folders(str(base), str(head))
        assert "Sales.CustomerID -> Customer.CustomerID" in result["relationships"]["changed"]

    def test_model_property_changed(self, tmp_path: Path) -> None:
        changed_model = _MODEL_TMDL.replace("culture: en-US", "culture: fr-FR")
        base = _make_tmdl_folder(tmp_path / "base")
        head = _make_tmdl_folder(tmp_path / "head", model_text=changed_model)
        result = diff_tmdl_folders(str(base), str(head))
        assert result["summary"]["model_changed"] is True
        assert any("culture" in p for p in result["model"]["changed_properties"])

    def test_semantic_model_layout(self, tmp_path: Path) -> None:
        """Handles the SemanticModel folder layout (definition/ subdirectory)."""
        base = _make_semantic_model_folder(tmp_path / "MyModel.SemanticModel.base")
        head = _make_semantic_model_folder(tmp_path / "MyModel.SemanticModel.head")
        result = diff_tmdl_folders(str(base), str(head))
        assert result["changed"] is False

    def test_missing_base_folder_raises(self, tmp_path: Path) -> None:
        head = _make_tmdl_folder(tmp_path / "head")
        with pytest.raises(PbiCliError, match="Base folder not found"):
            diff_tmdl_folders(str(tmp_path / "nonexistent"), str(head))

    def test_missing_head_folder_raises(self, tmp_path: Path) -> None:
        base = _make_tmdl_folder(tmp_path / "base")
        with pytest.raises(PbiCliError, match="Head folder not found"):
            diff_tmdl_folders(str(base), str(tmp_path / "nonexistent"))

    def test_result_keys_present(self, tmp_path: Path) -> None:
        base = _make_tmdl_folder(tmp_path / "base")
        head = _make_tmdl_folder(tmp_path / "head")
        result = diff_tmdl_folders(str(base), str(head))
        assert "base" in result
        assert "head" in result
        assert "changed" in result
        assert "summary" in result
        assert "tables" in result
        assert "relationships" in result
        assert "model" in result

    def test_no_relationships_file(self, tmp_path: Path) -> None:
        """Handles missing relationships.tmdl gracefully."""
        base = _make_tmdl_folder(tmp_path / "base", relationships_text="")
        head = _make_tmdl_folder(tmp_path / "head", relationships_text="")
        result = diff_tmdl_folders(str(base), str(head))
        assert result["relationships"] == {"added": [], "removed": [], "changed": []}

    def test_backtick_fenced_measure_parsed_correctly(self, tmp_path: Path) -> None:
        """Backtick-triple fenced multi-line measures are parsed without errors."""
        backtick_sales = (
            "table Sales\n"
            "\tlineageTag: tbl-001\n"
            "\n"
            "\tmeasure CY_Orders = ```\n"
            "\t\t\n"
            "\t\tCALCULATE ( [#Orders] , YEAR('Date'[Date]) = YEAR(TODAY()) )\n"
            "\t\t```\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: msr-backtick\n"
            "\n"
            "\tcolumn Amount\n"
            "\t\tdataType: decimal\n"
            "\t\tlineageTag: col-001\n"
            "\t\tsummarizeBy: sum\n"
            "\t\tsourceColumn: Amount\n"
        )
        base = _make_tmdl_folder(tmp_path / "base", tables={"Sales": backtick_sales})
        head = _make_tmdl_folder(tmp_path / "head", tables={"Sales": backtick_sales})
        result = diff_tmdl_folders(str(base), str(head))
        assert result["changed"] is False

    def test_backtick_fenced_measure_expression_changed(self, tmp_path: Path) -> None:
        """A changed backtick-fenced measure expression is detected."""
        base_tmdl = (
            "table Sales\n"
            "\tlineageTag: tbl-001\n"
            "\n"
            "\tmeasure CY_Orders = ```\n"
            "\t\tCALCULATE ( [#Orders] , YEAR('Date'[Date]) = YEAR(TODAY()) )\n"
            "\t\t```\n"
            "\t\tlineageTag: msr-backtick\n"
        )
        head_tmdl = base_tmdl.replace(
            "CALCULATE ( [#Orders] , YEAR('Date'[Date]) = YEAR(TODAY()) )",
            "CALCULATE ( [#Orders] , 'Date'[Year] = YEAR(TODAY()) )",
        )
        base = _make_tmdl_folder(tmp_path / "base", tables={"Sales": base_tmdl})
        head = _make_tmdl_folder(tmp_path / "head", tables={"Sales": head_tmdl})
        result = diff_tmdl_folders(str(base), str(head))
        assert result["changed"] is True
        assert "CY_Orders" in result["tables"]["changed"]["Sales"]["measures_changed"]

    def test_variation_stays_inside_column_block(self, tmp_path: Path) -> None:
        """Variation blocks at 1-tab indent are part of their parent column."""
        tmdl_with_variation = (
            "table Date\n"
            "\tlineageTag: tbl-date\n"
            "\n"
            "\tcolumn Date\n"
            "\t\tdataType: dateTime\n"
            "\t\tlineageTag: col-date\n"
            "\t\tsummarizeBy: none\n"
            "\t\tsourceColumn: Date\n"
            "\n"
            "\tvariation Variation\n"
            "\t\tisDefault\n"
            "\t\trelationship: abc-def-123\n"
            "\t\tdefaultHierarchy: LocalDateTable.Date Hierarchy\n"
        )
        base = _make_tmdl_folder(tmp_path / "base", tables={"Date": tmdl_with_variation})
        head = _make_tmdl_folder(tmp_path / "head", tables={"Date": tmdl_with_variation})
        result = diff_tmdl_folders(str(base), str(head))
        assert result["changed"] is False
