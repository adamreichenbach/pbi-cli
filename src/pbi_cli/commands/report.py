"""PBIR report management commands."""

from __future__ import annotations

from pathlib import Path

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
def report(ctx: click.Context, path: str | None) -> None:
    """Manage Power BI PBIR reports (pages, themes, validation)."""
    ctx.ensure_object(dict)
    ctx.obj["report_path"] = path


@report.command()
@click.pass_context
@pass_context
def info(ctx: PbiContext, click_ctx: click.Context) -> None:
    """Show report metadata summary."""
    from pbi_cli.core.pbir_path import resolve_report_path
    from pbi_cli.core.report_backend import report_info

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(ctx, report_info, definition_path=definition_path)


@report.command()
@click.argument("target_path", type=click.Path())
@click.option("--name", "-n", required=True, help="Report name.")
@click.option(
    "--dataset-path",
    default=None,
    help="Relative path to semantic model folder (e.g. ../MyModel.Dataset).",
)
@pass_context
def create(
    ctx: PbiContext, target_path: str, name: str, dataset_path: str | None
) -> None:
    """Scaffold a new PBIR report project."""
    from pbi_cli.core.report_backend import report_create

    run_command(
        ctx,
        report_create,
        target_path=Path(target_path),
        name=name,
        dataset_path=dataset_path,
    )


@report.command(name="list-pages")
@click.pass_context
@pass_context
def list_pages(ctx: PbiContext, click_ctx: click.Context) -> None:
    """List all pages in the report."""
    from pbi_cli.core.pbir_path import resolve_report_path
    from pbi_cli.core.report_backend import page_list

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(ctx, page_list, definition_path=definition_path)


@report.command(name="add-page")
@click.option("--display-name", "-d", required=True, help="Page display name.")
@click.option("--name", "-n", default=None, help="Page ID (auto-generated if omitted).")
@click.option("--width", type=int, default=1280, help="Page width in pixels.")
@click.option("--height", type=int, default=720, help="Page height in pixels.")
@click.pass_context
@pass_context
def add_page(
    ctx: PbiContext,
    click_ctx: click.Context,
    display_name: str,
    name: str | None,
    width: int,
    height: int,
) -> None:
    """Add a new page to the report."""
    from pbi_cli.core.pbir_path import resolve_report_path
    from pbi_cli.core.report_backend import page_add

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(
        ctx,
        page_add,
        definition_path=definition_path,
        display_name=display_name,
        name=name,
        width=width,
        height=height,
    )


@report.command(name="delete-page")
@click.argument("name")
@click.pass_context
@pass_context
def delete_page(ctx: PbiContext, click_ctx: click.Context, name: str) -> None:
    """Delete a page and all its visuals."""
    from pbi_cli.core.pbir_path import resolve_report_path
    from pbi_cli.core.report_backend import page_delete

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(ctx, page_delete, definition_path=definition_path, page_name=name)


@report.command(name="get-page")
@click.argument("name")
@click.pass_context
@pass_context
def get_page(ctx: PbiContext, click_ctx: click.Context, name: str) -> None:
    """Get details of a specific page."""
    from pbi_cli.core.pbir_path import resolve_report_path
    from pbi_cli.core.report_backend import page_get

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(ctx, page_get, definition_path=definition_path, page_name=name)


@report.command(name="set-theme")
@click.option("--file", "-f", required=True, type=click.Path(exists=True), help="Theme JSON file.")
@click.pass_context
@pass_context
def set_theme(ctx: PbiContext, click_ctx: click.Context, file: str) -> None:
    """Apply a custom theme to the report."""
    from pbi_cli.core.pbir_path import resolve_report_path
    from pbi_cli.core.report_backend import theme_set

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(
        ctx,
        theme_set,
        definition_path=definition_path,
        theme_path=Path(file),
    )


@report.command(name="get-theme")
@click.pass_context
@pass_context
def get_theme(ctx: PbiContext, click_ctx: click.Context) -> None:
    """Show the current theme (base and custom) applied to the report."""
    from pbi_cli.core.pbir_path import resolve_report_path
    from pbi_cli.core.report_backend import theme_get

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(ctx, theme_get, definition_path=definition_path)


@report.command(name="diff-theme")
@click.option(
    "--file", "-f", required=True, type=click.Path(exists=True),
    help="Proposed theme JSON file.",
)
@click.pass_context
@pass_context
def diff_theme(ctx: PbiContext, click_ctx: click.Context, file: str) -> None:
    """Compare a proposed theme JSON against the currently applied theme.

    Shows which theme keys would be added, removed, or changed.
    """
    from pbi_cli.core.pbir_path import resolve_report_path
    from pbi_cli.core.report_backend import theme_diff

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(
        ctx,
        theme_diff,
        definition_path=definition_path,
        theme_path=Path(file),
    )


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


@report.command()
@click.option("--full", is_flag=True, default=False, help="Run enhanced validation with warnings.")
@click.pass_context
@pass_context
def validate(ctx: PbiContext, click_ctx: click.Context, full: bool) -> None:
    """Validate the PBIR report structure and JSON files."""
    from pbi_cli.core.pbir_path import resolve_report_path

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)

    if full:
        from pbi_cli.core.pbir_validators import validate_report_full

        run_command(ctx, validate_report_full, definition_path=definition_path)
    else:
        from pbi_cli.core.report_backend import report_validate

        run_command(ctx, report_validate, definition_path=definition_path)


@report.command()
@pass_context
def reload(ctx: PbiContext) -> None:
    """Trigger Power BI Desktop to reload the current report.

    Sends Ctrl+Shift+F5 to Power BI Desktop. Tries pywin32 first,
    falls back to PowerShell, then prints manual instructions.

    Install pywin32 for best results: pip install pbi-cli-tool[reload]
    """
    from pbi_cli.utils.desktop_reload import reload_desktop

    run_command(ctx, reload_desktop)


@report.command()
@click.option("--port", type=int, default=8080, help="HTTP server port (WebSocket uses port+1).")
@click.pass_context
@pass_context
def preview(ctx: PbiContext, click_ctx: click.Context, port: int) -> None:
    """Start a live preview server for the PBIR report.

    Opens an HTTP server that renders the report as HTML/SVG.
    Auto-reloads in the browser when PBIR files change.

    Install websockets for this feature: pip install pbi-cli-tool[preview]
    """
    from pbi_cli.core.pbir_path import resolve_report_path
    from pbi_cli.preview.server import start_preview_server

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(
        ctx,
        start_preview_server,
        definition_path=definition_path,
        port=port,
    )


@report.command()
@click.argument("source_path", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, type=click.Path(), help="Output directory.")
@click.option("--force", is_flag=True, default=False, help="Overwrite existing .pbip file.")
@pass_context
def convert(ctx: PbiContext, source_path: str, output: str | None, force: bool) -> None:
    """Convert a .Report folder into a distributable .pbip project.

    Creates the .pbip project file and .gitignore for version control.
    Note: does NOT convert .pbix to .pbip (use Power BI Desktop for that).
    """
    from pbi_cli.core.report_backend import report_convert

    run_command(
        ctx,
        report_convert,
        source_path=Path(source_path),
        output_path=Path(output) if output else None,
        force=force,
    )
