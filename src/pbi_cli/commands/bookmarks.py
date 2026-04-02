"""PBIR bookmark management commands."""

from __future__ import annotations

import click

from pbi_cli.commands._helpers import run_command
from pbi_cli.main import PbiContext, pass_context


@click.group()
@click.option(
    "--path",
    "-p",
    default=None,
    help="Path to .Report folder (auto-detected from CWD if omitted).",
)
@click.pass_context
def bookmarks(ctx: click.Context, path: str | None) -> None:
    """Manage report bookmarks."""
    ctx.ensure_object(dict)
    ctx.obj["report_path"] = path


@bookmarks.command(name="list")
@click.pass_context
@pass_context
def list_bookmarks(ctx: PbiContext, click_ctx: click.Context) -> None:
    """List all bookmarks in the report."""
    from pbi_cli.core.bookmark_backend import bookmark_list
    from pbi_cli.core.pbir_path import resolve_report_path

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(ctx, bookmark_list, definition_path=definition_path)


@bookmarks.command(name="get")
@click.argument("name")
@click.pass_context
@pass_context
def get_bookmark(ctx: PbiContext, click_ctx: click.Context, name: str) -> None:
    """Get full details for a bookmark by NAME."""
    from pbi_cli.core.bookmark_backend import bookmark_get
    from pbi_cli.core.pbir_path import resolve_report_path

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(ctx, bookmark_get, definition_path=definition_path, name=name)


@bookmarks.command(name="add")
@click.option("--display-name", "-d", required=True, help="Human-readable bookmark name.")
@click.option("--page", "-g", required=True, help="Target page name (active section).")
@click.option("--name", "-n", default=None, help="Bookmark ID (auto-generated if omitted).")
@click.pass_context
@pass_context
def add_bookmark(
    ctx: PbiContext,
    click_ctx: click.Context,
    display_name: str,
    page: str,
    name: str | None,
) -> None:
    """Add a new bookmark pointing to a page."""
    from pbi_cli.core.bookmark_backend import bookmark_add
    from pbi_cli.core.pbir_path import resolve_report_path

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(
        ctx,
        bookmark_add,
        definition_path=definition_path,
        display_name=display_name,
        target_page=page,
        name=name,
    )


@bookmarks.command(name="delete")
@click.argument("name")
@click.pass_context
@pass_context
def delete_bookmark(ctx: PbiContext, click_ctx: click.Context, name: str) -> None:
    """Delete a bookmark by NAME."""
    from pbi_cli.core.bookmark_backend import bookmark_delete
    from pbi_cli.core.pbir_path import resolve_report_path

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(ctx, bookmark_delete, definition_path=definition_path, name=name)


@bookmarks.command(name="set-visibility")
@click.argument("name")
@click.option("--page", "-g", required=True, help="Page name (folder name).")
@click.option("--visual", "-v", required=True, help="Visual name (folder name).")
@click.option(
    "--hidden/--visible",
    default=True,
    help="Set the visual as hidden (default) or visible in the bookmark.",
)
@click.pass_context
@pass_context
def set_visibility(
    ctx: PbiContext,
    click_ctx: click.Context,
    name: str,
    page: str,
    visual: str,
    hidden: bool,
) -> None:
    """Set a visual hidden or visible inside bookmark NAME.

    NAME is the bookmark identifier (hex folder name).
    Use --hidden to hide the visual, --visible to show it.
    """
    from pbi_cli.core.bookmark_backend import bookmark_set_visibility
    from pbi_cli.core.pbir_path import resolve_report_path

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(
        ctx,
        bookmark_set_visibility,
        definition_path=definition_path,
        name=name,
        page_name=page,
        visual_name=visual,
        hidden=hidden,
    )
