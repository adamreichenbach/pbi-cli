"""TMDL folder diff -- pure Python, no .NET required."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from pbi_cli.core.errors import PbiCliError

# Entity keywords inside table files (at 1-tab indent).
# "variation" is intentionally excluded: it is a sub-property of a column,
# not a sibling entity, so its content stays inside the parent column block.
_TABLE_ENTITY_KEYWORDS = frozenset({"measure", "column", "hierarchy", "partition"})


def diff_tmdl_folders(base_folder: str, head_folder: str) -> dict[str, Any]:
    """Compare two TMDL export folders and return a structured diff.

    Works on any two folders produced by ``pbi database export-tmdl`` or
    exported from Power BI Desktop / Fabric Git.  No live connection needed.

    Returns a dict with keys: base, head, changed, summary, tables,
    relationships, model.
    """
    base = Path(base_folder)
    head = Path(head_folder)
    if not base.is_dir():
        raise PbiCliError(f"Base folder not found: {base}")
    if not head.is_dir():
        raise PbiCliError(f"Head folder not found: {head}")

    base_def = _find_definition_dir(base)
    head_def = _find_definition_dir(head)

    tables_diff = _diff_tables(base_def, head_def)
    rels_diff = _diff_relationships(base_def, head_def)
    model_diff = _diff_model(base_def, head_def)

    any_changed = bool(
        tables_diff["added"]
        or tables_diff["removed"]
        or tables_diff["changed"]
        or rels_diff["added"]
        or rels_diff["removed"]
        or rels_diff["changed"]
        or model_diff["changed_properties"]
    )

    summary: dict[str, Any] = {
        "tables_added": len(tables_diff["added"]),
        "tables_removed": len(tables_diff["removed"]),
        "tables_changed": len(tables_diff["changed"]),
        "relationships_added": len(rels_diff["added"]),
        "relationships_removed": len(rels_diff["removed"]),
        "relationships_changed": len(rels_diff["changed"]),
        "model_changed": bool(model_diff["changed_properties"]),
    }

    return {
        "base": str(base),
        "head": str(head),
        "changed": any_changed,
        "summary": summary,
        "tables": tables_diff,
        "relationships": rels_diff,
        "model": model_diff,
    }


def _find_definition_dir(folder: Path) -> Path:
    """Return the directory that directly contains model.tmdl / tables/.

    Handles both:
    - Direct layout:  folder/model.tmdl
    - SemanticModel:  folder/definition/model.tmdl
    """
    candidate = folder / "definition"
    if candidate.is_dir():
        return candidate
    return folder


def _read_tmdl(path: Path) -> str:
    """Read a TMDL file, returning empty string if absent."""
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _strip_lineage_tags(text: str) -> str:
    """Remove lineageTag lines so spurious GUID regeneration is ignored."""
    return re.sub(r"[ \t]*lineageTag:.*\n?", "", text)


# ---------------------------------------------------------------------------
# Table diffing
# ---------------------------------------------------------------------------


def _diff_tables(base_def: Path, head_def: Path) -> dict[str, Any]:
    base_tables_dir = base_def / "tables"
    head_tables_dir = head_def / "tables"

    base_names = _list_tmdl_names(base_tables_dir)
    head_names = _list_tmdl_names(head_tables_dir)

    added = sorted(head_names - base_names)
    removed = sorted(base_names - head_names)
    changed: dict[str, Any] = {}

    for name in sorted(base_names & head_names):
        base_text = _read_tmdl(base_tables_dir / f"{name}.tmdl")
        head_text = _read_tmdl(head_tables_dir / f"{name}.tmdl")
        if _strip_lineage_tags(base_text) == _strip_lineage_tags(head_text):
            continue
        table_diff = _diff_table_entities(base_text, head_text)
        if any(table_diff[k] for k in table_diff):
            changed[name] = table_diff

    return {"added": added, "removed": removed, "changed": changed}


def _list_tmdl_names(tables_dir: Path) -> set[str]:
    """Return stem names of all .tmdl files in a directory."""
    if not tables_dir.is_dir():
        return set()
    return {p.stem for p in tables_dir.glob("*.tmdl")}


def _diff_table_entities(
    base_text: str, head_text: str
) -> dict[str, list[str]]:
    """Compare entity blocks within two table TMDL files."""
    base_entities = _parse_table_entities(base_text)
    head_entities = _parse_table_entities(head_text)

    result: dict[str, list[str]] = {
        "measures_added": [],
        "measures_removed": [],
        "measures_changed": [],
        "columns_added": [],
        "columns_removed": [],
        "columns_changed": [],
        "partitions_added": [],
        "partitions_removed": [],
        "partitions_changed": [],
        "other_added": [],
        "other_removed": [],
        "other_changed": [],
    }

    all_keys = set(base_entities) | set(head_entities)
    for key in sorted(all_keys):
        keyword, _, name = key.partition("/")
        added_key = f"{keyword}s_added" if f"{keyword}s_added" in result else "other_added"
        removed_key = f"{keyword}s_removed" if f"{keyword}s_removed" in result else "other_removed"
        changed_key = f"{keyword}s_changed" if f"{keyword}s_changed" in result else "other_changed"

        if key not in base_entities:
            result[added_key].append(name)
        elif key not in head_entities:
            result[removed_key].append(name)
        else:
            b = _strip_lineage_tags(base_entities[key])
            h = _strip_lineage_tags(head_entities[key])
            if b != h:
                result[changed_key].append(name)

    # Remove empty other_* lists to keep output clean
    for k in ("other_added", "other_removed", "other_changed"):
        if not result[k]:
            del result[k]

    return result


def _parse_table_entities(text: str) -> dict[str, str]:
    """Parse a table TMDL file into {keyword/name: text_block} entries.

    Entities (measure, column, hierarchy, partition, variation) start at
    exactly one tab of indentation inside the table declaration.
    """
    entities: dict[str, str] = {}
    lines = text.splitlines(keepends=True)
    current_key: str | None = None
    current_lines: list[str] = []

    for line in lines:
        # Entity declaration: starts with exactly one tab, not two
        if line.startswith("\t") and not line.startswith("\t\t"):
            stripped = line[1:]  # remove leading tab
            keyword = stripped.split()[0] if stripped.split() else ""
            if keyword in _TABLE_ENTITY_KEYWORDS:
                # Save previous block
                if current_key is not None:
                    entities[current_key] = "".join(current_lines)
                name = _extract_entity_name(keyword, stripped)
                current_key = f"{keyword}/{name}"
                current_lines = [line]
                continue

        if current_key is not None:
            current_lines.append(line)

    if current_key is not None:
        entities[current_key] = "".join(current_lines)

    return entities


def _extract_entity_name(keyword: str, declaration: str) -> str:
    """Extract the entity name from a TMDL declaration line (no leading tab)."""
    # e.g. "measure 'Total Revenue' = ..."  -> "Total Revenue"
    # e.g. "column ProductID"               -> "ProductID"
    # e.g. "partition Sales = m"            -> "Sales"
    rest = declaration[len(keyword):].strip()
    if rest.startswith("'"):
        end = rest.find("'", 1)
        return rest[1:end] if end > 0 else rest[1:]
    # Take first token, stop at '=' or whitespace
    token = re.split(r"[\s=]", rest)[0]
    return token.strip("'\"") if token else rest


# ---------------------------------------------------------------------------
# Relationship diffing
# ---------------------------------------------------------------------------


def _diff_relationships(base_def: Path, head_def: Path) -> dict[str, list[str]]:
    base_rels = _parse_relationships(_read_tmdl(base_def / "relationships.tmdl"))
    head_rels = _parse_relationships(_read_tmdl(head_def / "relationships.tmdl"))

    all_keys = set(base_rels) | set(head_rels)
    added: list[str] = []
    removed: list[str] = []
    changed: list[str] = []

    for key in sorted(all_keys):
        if key not in base_rels:
            added.append(key)
        elif key not in head_rels:
            removed.append(key)
        elif _strip_lineage_tags(base_rels[key]) != _strip_lineage_tags(head_rels[key]):
            changed.append(key)

    return {"added": added, "removed": removed, "changed": changed}


def _parse_relationships(text: str) -> dict[str, str]:
    """Parse relationships.tmdl into {from -> to: text_block} entries."""
    if not text.strip():
        return {}

    blocks: dict[str, str] = {}
    current_lines: list[str] = []
    in_rel = False

    for line in text.splitlines(keepends=True):
        if line.startswith("relationship "):
            if in_rel and current_lines:
                _save_relationship(current_lines, blocks)
            current_lines = [line]
            in_rel = True
        elif in_rel:
            current_lines.append(line)

    if in_rel and current_lines:
        _save_relationship(current_lines, blocks)

    return blocks


def _save_relationship(lines: list[str], blocks: dict[str, str]) -> None:
    """Extract semantic key from a relationship block and store it."""
    from_col = ""
    to_col = ""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("fromColumn:"):
            from_col = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("toColumn:"):
            to_col = stripped.split(":", 1)[1].strip()
    if from_col or to_col:
        key = f"{from_col} -> {to_col}"
        blocks[key] = "".join(lines)


# ---------------------------------------------------------------------------
# Model property diffing
# ---------------------------------------------------------------------------


def _diff_model(base_def: Path, head_def: Path) -> dict[str, list[str]]:
    base_props = _parse_model_props(_read_tmdl(base_def / "model.tmdl"))
    head_props = _parse_model_props(_read_tmdl(head_def / "model.tmdl"))

    changed: list[str] = []
    all_keys = set(base_props) | set(head_props)
    for key in sorted(all_keys):
        b_val = base_props.get(key)
        h_val = head_props.get(key)
        if b_val != h_val:
            changed.append(f"{key}: {b_val!r} -> {h_val!r}")

    return {"changed_properties": changed}


def _parse_model_props(text: str) -> dict[str, str]:
    """Extract key: value properties at 1-tab indent from model.tmdl."""
    props: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith("\t") and not line.startswith("\t\t") and ":" in line:
            key, _, val = line[1:].partition(":")
            props[key.strip()] = val.strip()
    return props
