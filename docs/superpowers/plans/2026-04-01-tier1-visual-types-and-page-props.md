# Tier 1 Gap-Fill: cardVisual, actionButton, Page Properties, Container Objects

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the four highest-priority features discovered from Supply Chain Analytics .pbip export: `cardVisual` and `actionButton` visual types, page background/visibility controls, and `visualContainerObjects` setters for border/background/title.

**Architecture:** All changes follow the existing pure-function pattern -- `fn(definition_path: Path, ...) -> dict[str, Any]`. Visual types extend `pbir_models.py` and `visual_backend.py` plus add JSON templates and preview renderer entries. Page and container props are new functions in `report_backend.py` and `visual_backend.py` respectively, each wired to a Click subcommand.

**Tech Stack:** Python 3.10+, pytest, ruff, click, JSON file I/O (no new dependencies).

---

## File Map

| File | Change |
|------|--------|
| `src/pbi_cli/core/pbir_models.py` | Add `cardVisual`, `actionButton` to `SUPPORTED_VISUAL_TYPES` and `VISUAL_TYPE_ALIASES` |
| `src/pbi_cli/core/visual_backend.py` | Add entries for both types to `VISUAL_DATA_ROLES`, `MEASURE_ROLES`, `ROLE_ALIASES`, `DEFAULT_SIZES`; add `visual_set_container()` |
| `src/pbi_cli/templates/visuals/cardVisual.json` | **New** template with `queryState.Data` + `sortDefinition` + `visualContainerObjects` |
| `src/pbi_cli/templates/visuals/actionButton.json` | **New** template with no `queryState`, top-level `howCreated` |
| `src/pbi_cli/preview/renderer.py` | Add color/icon entries for both types |
| `src/pbi_cli/core/report_backend.py` | Add `page_set_background()` and `page_set_visibility()` |
| `src/pbi_cli/commands/report.py` | Add `set-background` and `set-visibility` subcommands |
| `src/pbi_cli/commands/visual.py` | Add `set-container` subcommand |
| `tests/test_visual_backend.py` | New tests for new types and `visual_set_container` |
| `tests/test_report_backend.py` | New tests for `page_set_background` and `page_set_visibility` |
| `src/pbi_cli/__init__.py` | Bump version `3.3.0` → `3.4.0` |
| `pyproject.toml` | Bump version `3.3.0` → `3.4.0` |

---

## Task 1: Add cardVisual and actionButton Visual Types

### What to know

From the real Desktop export of Supply Chain Analytics:

- **cardVisual** (25 occurrences) is the modern card. Its queryState uses a `"Data"` role (not `"Fields"`). It also has a top-level `sortDefinition` in `query` and a `visualContainerObjects` key alongside `visual.objects`.
- **actionButton** (25 occurrences) is a navigation/action button. It has **no `query`/`queryState`** at all. It requires a top-level `"howCreated": "InsertVisualButton"` field.
- Both types were previously absent from `SUPPORTED_VISUAL_TYPES`, causing `visual_add cardVisual` to raise `VisualTypeError`.

**Files:**
- Modify: `src/pbi_cli/core/pbir_models.py`
- Modify: `src/pbi_cli/core/visual_backend.py`
- Create: `src/pbi_cli/templates/visuals/cardVisual.json`
- Create: `src/pbi_cli/templates/visuals/actionButton.json`
- Modify: `src/pbi_cli/preview/renderer.py`
- Modify: `tests/test_visual_backend.py`

---

- [ ] **Step 1a: Write failing tests for cardVisual and actionButton**

Add these tests at the bottom of `tests/test_visual_backend.py` (after the existing imports, extend the import list to include nothing new -- `visual_add` and `visual_list` are already imported):

```python
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
```

- [ ] **Step 1b: Run tests to verify they fail**

```bash
cd "e:/Coding Projects/Open Source/pbi-cli"
python -m pytest tests/test_visual_backend.py::test_visual_add_card_visual tests/test_visual_backend.py::test_visual_add_action_button -v
```

Expected: FAIL with `VisualTypeError` (type not in SUPPORTED_VISUAL_TYPES).

- [ ] **Step 1c: Update pbir_models.py**

In `src/pbi_cli/core/pbir_models.py`:

Add `"cardVisual"` and `"actionButton"` to the `SUPPORTED_VISUAL_TYPES` frozenset (in the v3.1.0 additions block or add a new `# v3.4.0 additions` comment):

```python
# v3.4.0 additions
"cardVisual",
"actionButton",
```

Add to `VISUAL_TYPE_ALIASES` dict:

```python
# v3.4.0 additions
"card_visual": "cardVisual",
"modern_card": "cardVisual",
"action_button": "actionButton",
"button": "actionButton",
```

- [ ] **Step 1d: Update visual_backend.py**

In `src/pbi_cli/core/visual_backend.py`:

Add to `VISUAL_DATA_ROLES`:
```python
# v3.4.0 additions
"cardVisual": ["Data"],
"actionButton": [],
```

Add `"Data"` to `MEASURE_ROLES` frozenset (cardVisual's Data role accepts measures):
```python
MEASURE_ROLES: frozenset[str] = frozenset({
    "Y", "Values", "Fields", "Indicator", "Goal",
    # v3.1.0 additions
    "ColumnY", "LineY", "X", "Size",
    # v3.4.0 additions
    "Data",
})
```

Add to `ROLE_ALIASES`:
```python
# v3.4.0 additions
"cardVisual": {"field": "Data", "value": "Data"},
"actionButton": {},
```

Add to `DEFAULT_SIZES`:
```python
# v3.4.0 additions -- sizes from real Desktop export
"cardVisual": (217, 87),
"actionButton": (51, 22),
```

- [ ] **Step 1e: Create cardVisual.json template**

Create `src/pbi_cli/templates/visuals/cardVisual.json`:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.5.0/schema.json",
  "name": "__VISUAL_NAME__",
  "position": {
    "x": __X__,
    "y": __Y__,
    "z": __Z__,
    "height": __HEIGHT__,
    "width": __WIDTH__,
    "tabOrder": __TAB_ORDER__
  },
  "visual": {
    "visualType": "cardVisual",
    "query": {
      "queryState": {
        "Data": {
          "projections": []
        }
      },
      "sortDefinition": {
        "sort": [],
        "isDefaultSort": true
      }
    },
    "objects": {},
    "visualContainerObjects": {},
    "drillFilterOtherVisuals": true
  }
}
```

- [ ] **Step 1f: Create actionButton.json template**

Create `src/pbi_cli/templates/visuals/actionButton.json`:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.5.0/schema.json",
  "name": "__VISUAL_NAME__",
  "position": {
    "x": __X__,
    "y": __Y__,
    "z": __Z__,
    "height": __HEIGHT__,
    "width": __WIDTH__,
    "tabOrder": __TAB_ORDER__
  },
  "visual": {
    "visualType": "actionButton",
    "objects": {},
    "visualContainerObjects": {},
    "drillFilterOtherVisuals": true
  },
  "howCreated": "InsertVisualButton"
}
```

- [ ] **Step 1g: Update preview renderer**

In `src/pbi_cli/preview/renderer.py`, add to `_VISUAL_COLORS` after the v3.1.0 block:

```python
# v3.4.0 additions
"cardVisual": "#767171",
"actionButton": "#E8832A",
```

Add to `_VISUAL_ICONS` after the v3.1.0 block:

```python
# v3.4.0 additions
"cardVisual": "&#9632;",
"actionButton": "&#9654;",
```

- [ ] **Step 1h: Run tests to verify they pass**

```bash
python -m pytest tests/test_visual_backend.py::test_visual_add_card_visual tests/test_visual_backend.py::test_visual_add_card_visual_alias tests/test_visual_backend.py::test_visual_add_action_button tests/test_visual_backend.py::test_visual_add_action_button_aliases -v
```

Expected: all PASS.

- [ ] **Step 1i: Run full test suite and ruff**

```bash
python -m pytest -m "not e2e" -q
python -m ruff check src/ tests/
```

Expected: zero failures, zero ruff errors.

- [ ] **Step 1j: Commit**

```bash
cd "e:/Coding Projects/Open Source/pbi-cli"
git add src/pbi_cli/core/pbir_models.py src/pbi_cli/core/visual_backend.py
git add src/pbi_cli/templates/visuals/cardVisual.json src/pbi_cli/templates/visuals/actionButton.json
git add src/pbi_cli/preview/renderer.py tests/test_visual_backend.py
git commit -m "feat: add cardVisual and actionButton visual types (v3.4.0)"
```

---

## Task 2: page_set_background

### What to know

`page.json` has an optional top-level `"objects"` key. When a background color is set in Desktop, it writes:

```json
"objects": {
  "background": [
    {
      "properties": {
        "color": {
          "solid": {
            "color": {
              "expr": {
                "Literal": {"Value": "'#F8F9FA'"}
              }
            }
          }
        }
      }
    }
  ]
}
```

The function merges this into the existing `objects` dict (preserving any other object properties like `outspace`).

**Files:**
- Modify: `src/pbi_cli/core/report_backend.py`
- Modify: `src/pbi_cli/commands/report.py`
- Modify: `tests/test_report_backend.py`

---

- [ ] **Step 2a: Write failing tests**

Add to the imports in `tests/test_report_backend.py`:
```python
from pbi_cli.core.report_backend import (
    page_set_background,
    page_set_visibility,
    ...  # keep existing imports
)
```

Add tests:

```python
# ---------------------------------------------------------------------------
# Task 2 -- page_set_background
# ---------------------------------------------------------------------------

def test_page_set_background_writes_color(sample_report: Path) -> None:
    # sample_report fixture already has a page named "page1"
    result = page_set_background(sample_report, "page1", "#F8F9FA")
    assert result["status"] == "updated"
    assert result["background_color"] == "#F8F9FA"
    page_data = _read(sample_report / "pages" / "page1" / "page.json")
    bg = page_data["objects"]["background"][0]["properties"]["color"]
    assert bg["solid"]["color"]["expr"]["Literal"]["Value"] == "'#F8F9FA'"


def test_page_set_background_preserves_other_objects(sample_report: Path) -> None:
    # Manually set an existing object key first
    page_json = sample_report / "pages" / "page1" / "page.json"
    data = _read(page_json)
    data["objects"] = {"outspace": [{"properties": {"color": {}}}]}
    page_json.write_text(json.dumps(data, indent=2), encoding="utf-8")

    page_set_background(sample_report, "page1", "#FFFFFF")

    updated = _read(page_json)
    assert "outspace" in updated["objects"]
    assert "background" in updated["objects"]


def test_page_set_background_overrides_existing_background(sample_report: Path) -> None:
    page_set_background(sample_report, "page1", "#111111")
    page_set_background(sample_report, "page1", "#AABBCC")
    data = _read(sample_report / "pages" / "page1" / "page.json")
    bg = data["objects"]["background"][0]["properties"]["color"]
    assert bg["solid"]["color"]["expr"]["Literal"]["Value"] == "'#AABBCC'"


def test_page_set_background_raises_for_missing_page(sample_report: Path) -> None:
    with pytest.raises(PbiCliError, match="not found"):
        page_set_background(sample_report, "no_such_page", "#000000")
```

- [ ] **Step 2b: Run to verify tests fail**

```bash
python -m pytest tests/test_report_backend.py::test_page_set_background_writes_color -v
```

Expected: FAIL with `ImportError` (function not yet defined).

- [ ] **Step 2c: Implement page_set_background in report_backend.py**

Add after `page_get()`:

```python
def page_set_background(
    definition_path: Path,
    page_name: str,
    color: str,
) -> dict[str, Any]:
    """Set the background color of a page.

    Updates the ``objects.background`` property in ``page.json``.
    The color must be a hex string, e.g. ``'#F8F9FA'``.
    """
    page_dir = get_page_dir(definition_path, page_name)
    page_json_path = page_dir / "page.json"
    if not page_json_path.exists():
        raise PbiCliError(f"Page '{page_name}' not found.")

    page_data = _read_json(page_json_path)
    background_entry = {
        "properties": {
            "color": {
                "solid": {
                    "color": {
                        "expr": {
                            "Literal": {"Value": f"'{color}'"}
                        }
                    }
                }
            }
        }
    }
    objects = {**page_data.get("objects", {}), "background": [background_entry]}
    _write_json(page_json_path, {**page_data, "objects": objects})
    return {"status": "updated", "page": page_name, "background_color": color}
```

- [ ] **Step 2d: Add set-background CLI command in report.py**

Add after the `diff_theme` command:

```python
@report.command(name="set-background")
@click.argument("page_name")
@click.option("--color", "-c", required=True, help="Hex color e.g. '#F8F9FA'.")
@click.pass_context
@pass_context
def set_background(
    ctx: PbiContext, click_ctx: click.Context, page_name: str, color: str
) -> None:
    """Set the background color of a page."""
    from pbi_cli.core.pbir_path import resolve_report_path
    from pbi_cli.core.report_backend import page_set_background

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(
        ctx,
        page_set_background,
        definition_path=definition_path,
        page_name=page_name,
        color=color,
    )
```

- [ ] **Step 2e: Run tests to verify they pass**

```bash
python -m pytest tests/test_report_backend.py -k "background" -v
```

Expected: all 4 PASS.

- [ ] **Step 2f: Run full suite + ruff**

```bash
python -m pytest -m "not e2e" -q && python -m ruff check src/ tests/
```

- [ ] **Step 2g: Commit**

```bash
git add src/pbi_cli/core/report_backend.py src/pbi_cli/commands/report.py tests/test_report_backend.py
git commit -m "feat: add page_set_background and pbi report set-background command"
```

---

## Task 3: page_set_visibility

### What to know

Hidden pages in Desktop write a top-level `"visibility": "HiddenInViewMode"` key in `page.json`. To unhide, the key is simply removed. The real Supply Chain report has one hidden page (`definition` folder was confirmed to have `"visibility": "HiddenInViewMode"` on that page).

**Files:**
- Modify: `src/pbi_cli/core/report_backend.py` (add function, add to import in test)
- Modify: `src/pbi_cli/commands/report.py` (add subcommand)
- Modify: `tests/test_report_backend.py` (add tests)

---

- [ ] **Step 3a: Write failing tests**

```python
# ---------------------------------------------------------------------------
# Task 3 -- page_set_visibility
# ---------------------------------------------------------------------------

def test_page_set_visibility_hidden(sample_report: Path) -> None:
    result = page_set_visibility(sample_report, "page1", hidden=True)
    assert result["status"] == "updated"
    assert result["hidden"] is True
    data = _read(sample_report / "pages" / "page1" / "page.json")
    assert data.get("visibility") == "HiddenInViewMode"


def test_page_set_visibility_visible(sample_report: Path) -> None:
    # First hide, then show
    page_json = sample_report / "pages" / "page1" / "page.json"
    data = _read(page_json)
    page_json.write_text(
        json.dumps({**data, "visibility": "HiddenInViewMode"}, indent=2),
        encoding="utf-8",
    )

    result = page_set_visibility(sample_report, "page1", hidden=False)
    assert result["hidden"] is False
    updated = _read(page_json)
    assert "visibility" not in updated


def test_page_set_visibility_idempotent_visible(sample_report: Path) -> None:
    # Calling visible on an already-visible page should not add visibility key
    page_set_visibility(sample_report, "page1", hidden=False)
    data = _read(sample_report / "pages" / "page1" / "page.json")
    assert "visibility" not in data


def test_page_set_visibility_raises_for_missing_page(sample_report: Path) -> None:
    with pytest.raises(PbiCliError, match="not found"):
        page_set_visibility(sample_report, "ghost_page", hidden=True)
```

- [ ] **Step 3b: Run to verify failure**

```bash
python -m pytest tests/test_report_backend.py::test_page_set_visibility_hidden -v
```

Expected: FAIL with `ImportError`.

- [ ] **Step 3c: Implement page_set_visibility in report_backend.py**

Add after `page_set_background()`:

```python
def page_set_visibility(
    definition_path: Path,
    page_name: str,
    hidden: bool,
) -> dict[str, Any]:
    """Show or hide a page in the report navigation.

    Setting ``hidden=True`` writes ``"visibility": "HiddenInViewMode"`` to
    ``page.json``.  Setting ``hidden=False`` removes the key if present.
    """
    page_dir = get_page_dir(definition_path, page_name)
    page_json_path = page_dir / "page.json"
    if not page_json_path.exists():
        raise PbiCliError(f"Page '{page_name}' not found.")

    page_data = _read_json(page_json_path)
    if hidden:
        updated = {**page_data, "visibility": "HiddenInViewMode"}
    else:
        updated = {k: v for k, v in page_data.items() if k != "visibility"}
    _write_json(page_json_path, updated)
    return {"status": "updated", "page": page_name, "hidden": hidden}
```

- [ ] **Step 3d: Add set-visibility CLI command in report.py**

Add after `set_background`:

```python
@report.command(name="set-visibility")
@click.argument("page_name")
@click.option(
    "--hidden/--visible",
    default=True,
    help="Hide or show the page in navigation.",
)
@click.pass_context
@pass_context
def set_visibility(
    ctx: PbiContext, click_ctx: click.Context, page_name: str, hidden: bool
) -> None:
    """Hide or show a page in the report navigation."""
    from pbi_cli.core.pbir_path import resolve_report_path
    from pbi_cli.core.report_backend import page_set_visibility

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(
        ctx,
        page_set_visibility,
        definition_path=definition_path,
        page_name=page_name,
        hidden=hidden,
    )
```

- [ ] **Step 3e: Run tests**

```bash
python -m pytest tests/test_report_backend.py -k "visibility" -v
```

Expected: all 4 PASS.

- [ ] **Step 3f: Run full suite + ruff**

```bash
python -m pytest -m "not e2e" -q && python -m ruff check src/ tests/
```

- [ ] **Step 3g: Commit**

```bash
git add src/pbi_cli/core/report_backend.py src/pbi_cli/commands/report.py tests/test_report_backend.py
git commit -m "feat: add page_set_visibility and pbi report set-visibility command"
```

---

## Task 4: visual_set_container (visualContainerObjects)

### What to know

`visual.json` contains a `visual.visualContainerObjects` dict that controls border, background, title, and padding at the *container* level (separate from `visual.objects` which controls visual-internal formatting). From the real Desktop export, the schema is:

```json
"visualContainerObjects": {
  "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
  "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
  "title": [{"properties": {"text": {"expr": {"Literal": {"Value": "'My Title'"}}}}}]
}
```

The function accepts keyword arguments for `border_show`, `background_show`, and `title`. It merges only the provided keys into the existing `visualContainerObjects`, leaving others unchanged. All updates are immutable (build new dicts, never mutate).

**Files:**
- Modify: `src/pbi_cli/core/visual_backend.py` (add function)
- Modify: `src/pbi_cli/commands/visual.py` (add subcommand)
- Modify: `tests/test_visual_backend.py` (add tests)

---

- [ ] **Step 4a: Write failing tests**

Add to `tests/test_visual_backend.py` imports:
```python
from pbi_cli.core.visual_backend import (
    visual_add,
    visual_bind,
    visual_delete,
    visual_get,
    visual_list,
    visual_set_container,
    visual_update,
)
```

Add tests:

```python
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
```

- [ ] **Step 4b: Run to verify failure**

```bash
python -m pytest tests/test_visual_backend.py::test_visual_set_container_border_hide -v
```

Expected: FAIL with `ImportError`.

- [ ] **Step 4c: Implement visual_set_container in visual_backend.py**

Add after `visual_update()`:

```python
def visual_set_container(
    definition_path: Path,
    page_name: str,
    visual_name: str,
    border_show: bool | None = None,
    background_show: bool | None = None,
    title: str | None = None,
) -> dict[str, Any]:
    """Set container-level properties (border, background, title) on a visual.

    Only the keyword arguments that are provided (not None) are updated.
    Other ``visualContainerObjects`` keys are preserved unchanged.

    The ``visualContainerObjects`` key is separate from ``visual.objects`` --
    it controls the container chrome (border, background, header title) rather
    than the visual's own formatting.
    """
    visual_dir = get_visual_dir(definition_path, page_name, visual_name)
    visual_json_path = visual_dir / "visual.json"
    if not visual_json_path.exists():
        raise PbiCliError(
            f"Visual '{visual_name}' not found on page '{page_name}'."
        )

    data = _read_json(visual_json_path)
    visual = data["visual"]
    vco: dict[str, Any] = dict(visual.get("visualContainerObjects", {}))

    def _bool_entry(value: bool) -> list[dict[str, Any]]:
        return [{
            "properties": {
                "show": {
                    "expr": {"Literal": {"Value": str(value).lower()}}
                }
            }
        }]

    if border_show is not None:
        vco = {**vco, "border": _bool_entry(border_show)}
    if background_show is not None:
        vco = {**vco, "background": _bool_entry(background_show)}
    if title is not None:
        vco = {**vco, "title": [{
            "properties": {
                "text": {
                    "expr": {"Literal": {"Value": f"'{title}'"}}
                }
            }
        }]}

    updated_visual = {**visual, "visualContainerObjects": vco}
    _write_json(visual_json_path, {**data, "visual": updated_visual})

    return {
        "status": "updated",
        "visual": visual_name,
        "page": page_name,
        "border_show": border_show,
        "background_show": background_show,
        "title": title,
    }
```

- [ ] **Step 4d: Add set-container CLI command in visual.py**

Look at the existing pattern in `src/pbi_cli/commands/visual.py` for how commands use `--page` and a `NAME` argument. Add:

```python
@visual.command(name="set-container")
@click.argument("name")
@click.option("--page", "-g", required=True, help="Page name or display name.")
@click.option(
    "--border-show/--border-hide",
    default=None,
    is_flag=False,
    flag_value=None,
    help="Show or hide the visual border.",
)
@click.option(
    "--background-show/--background-hide",
    default=None,
    is_flag=False,
    flag_value=None,
    help="Show or hide the visual background.",
)
@click.option("--title", default=None, help="Set container title text.")
@pass_context
def set_container(
    ctx: PbiContext,
    name: str,
    page: str,
    border_show: bool | None,
    background_show: bool | None,
    title: str | None,
) -> None:
    """Set container-level border, background, or title on a visual."""
    from pbi_cli.core.pbir_path import resolve_report_path
    from pbi_cli.core.visual_backend import visual_set_container

    definition_path = resolve_report_path(None)
    run_command(
        ctx,
        visual_set_container,
        definition_path=definition_path,
        page_name=page,
        visual_name=name,
        border_show=border_show,
        background_show=background_show,
        title=title,
    )
```

Note: Click's `--flag/--no-flag` with `default=None` requires a small workaround. Check how the existing `visual.py` handles similar boolean flags (e.g. `--hidden/--visible` in `visual_update`). Mirror that pattern exactly.

- [ ] **Step 4e: Run tests**

```bash
python -m pytest tests/test_visual_backend.py -k "container" -v
```

Expected: all 6 PASS.

- [ ] **Step 4f: Run full suite + ruff**

```bash
python -m pytest -m "not e2e" -q && python -m ruff check src/ tests/
```

- [ ] **Step 4g: Commit**

```bash
git add src/pbi_cli/core/visual_backend.py src/pbi_cli/commands/visual.py tests/test_visual_backend.py
git commit -m "feat: add visual_set_container and pbi visual set-container command"
```

---

## Task 5: Version Bump to 3.4.0

**Files:**
- Modify: `src/pbi_cli/__init__.py`
- Modify: `pyproject.toml`

---

- [ ] **Step 5a: Bump versions**

In `src/pbi_cli/__init__.py`, change:
```python
__version__ = "3.3.0"
```
to:
```python
__version__ = "3.4.0"
```

In `pyproject.toml`, change:
```toml
version = "3.3.0"
```
to:
```toml
version = "3.4.0"
```

- [ ] **Step 5b: Verify final test count and coverage**

```bash
python -m pytest -m "not e2e" -v --tb=short 2>&1 | tail -20
```

Expected: 420+ tests passing (397 before + ~23 new), zero failures.

- [ ] **Step 5c: Final ruff check**

```bash
python -m ruff check src/ tests/
```

Expected: no output (clean).

- [ ] **Step 5d: Commit**

```bash
git add src/pbi_cli/__init__.py pyproject.toml
git commit -m "chore: bump version to 3.4.0"
```

---

## Verification Summary

After all tasks complete:

```bash
# All tests pass
python -m pytest -m "not e2e" -q

# CLI smoke tests
pbi visual add cardVisual --page p1 --x 10 --y 10  # succeeds
pbi visual add actionButton --page p1 --x 0 --y 0  # succeeds, no query
pbi report set-background page1 --color '#F8F9FA'   # updates objects.background
pbi report set-visibility page1 --hidden            # adds visibility key
pbi report set-visibility page1 --visible           # removes visibility key
pbi visual set-container Chart1 --page p1 --border-hide  # sets border show=false
pbi visual set-container Chart1 --page p1 --title "Revenue"  # sets title text
```
