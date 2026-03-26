"""Less common operations: culture, translation, function, query-group."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import build_definition, run_tool
from pbi_cli.main import PbiContext, pass_context


@click.group()
def advanced() -> None:
    """Advanced operations: cultures, translations, functions, query groups."""


# --- Culture ---

@advanced.group()
def culture() -> None:
    """Manage model cultures (locales)."""


@culture.command(name="list")
@pass_context
def culture_list(ctx: PbiContext) -> None:
    """List cultures."""
    run_tool(ctx, "culture_operations", {"operation": "List"})


@culture.command()
@click.argument("name")
@pass_context
def culture_create(ctx: PbiContext, name: str) -> None:
    """Create a culture."""
    run_tool(ctx, "culture_operations", {"operation": "Create", "definitions": [{"name": name}]})


@culture.command(name="delete")
@click.argument("name")
@pass_context
def culture_delete(ctx: PbiContext, name: str) -> None:
    """Delete a culture."""
    run_tool(ctx, "culture_operations", {"operation": "Delete", "name": name})


# --- Translation ---

@advanced.group()
def translation() -> None:
    """Manage object translations."""


@translation.command(name="list")
@click.option("--culture", "-c", required=True, help="Culture name.")
@pass_context
def translation_list(ctx: PbiContext, culture: str) -> None:
    """List translations for a culture."""
    run_tool(ctx, "object_translation_operations", {"operation": "List", "cultureName": culture})


@translation.command()
@click.option("--culture", "-c", required=True, help="Culture name.")
@click.option("--object-name", required=True, help="Object to translate.")
@click.option("--table", "-t", default=None, help="Table name (if translating table object).")
@click.option("--translated-caption", default=None, help="Translated caption.")
@click.option("--translated-description", default=None, help="Translated description.")
@pass_context
def create(
    ctx: PbiContext,
    culture: str,
    object_name: str,
    table: str | None,
    translated_caption: str | None,
    translated_description: str | None,
) -> None:
    """Create an object translation."""
    definition = build_definition(
        required={"objectName": object_name, "cultureName": culture},
        optional={
            "tableName": table,
            "translatedCaption": translated_caption,
            "translatedDescription": translated_description,
        },
    )
    run_tool(ctx, "object_translation_operations", {"operation": "Create", "definitions": [definition]})


# --- Function ---

@advanced.group()
def function() -> None:
    """Manage model functions."""


@function.command(name="list")
@pass_context
def function_list(ctx: PbiContext) -> None:
    """List functions."""
    run_tool(ctx, "function_operations", {"operation": "List"})


@function.command()
@click.argument("name")
@click.option("--expression", "-e", required=True, help="Function expression.")
@pass_context
def function_create(ctx: PbiContext, name: str, expression: str) -> None:
    """Create a function."""
    run_tool(ctx, "function_operations", {
        "operation": "Create",
        "definitions": [{"name": name, "expression": expression}],
    })


# --- Query Group ---

@advanced.group(name="query-group")
def query_group() -> None:
    """Manage query groups."""


@query_group.command(name="list")
@pass_context
def qg_list(ctx: PbiContext) -> None:
    """List query groups."""
    run_tool(ctx, "query_group_operations", {"operation": "List"})


@query_group.command()
@click.argument("name")
@click.option("--folder", default=None, help="Folder path.")
@pass_context
def qg_create(ctx: PbiContext, name: str, folder: str | None) -> None:
    """Create a query group."""
    definition = build_definition(required={"name": name}, optional={"folder": folder})
    run_tool(ctx, "query_group_operations", {"operation": "Create", "definitions": [definition]})
