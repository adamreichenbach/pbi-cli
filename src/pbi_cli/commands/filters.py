"""PBIR filter management commands."""

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
def filters(ctx: click.Context, path: str | None) -> None:
    """Manage page and visual filters."""
    ctx.ensure_object(dict)
    ctx.obj["report_path"] = path


@filters.command(name="list")
@click.option("--page", required=True, help="Page name (folder name, not display name).")
@click.option("--visual", default=None, help="Visual name (returns visual filters if given).")
@click.pass_context
@pass_context
def filter_list_cmd(
    ctx: PbiContext,
    click_ctx: click.Context,
    page: str,
    visual: str | None,
) -> None:
    """List filters on a page or visual."""
    from pbi_cli.core.filter_backend import filter_list
    from pbi_cli.core.pbir_path import resolve_report_path

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(
        ctx,
        filter_list,
        definition_path=definition_path,
        page_name=page,
        visual_name=visual,
    )


@filters.command(name="add-categorical")
@click.option("--page", required=True, help="Page name (folder name, not display name).")
@click.option("--table", required=True, help="Table name.")
@click.option("--column", required=True, help="Column name.")
@click.option(
    "--value",
    "values",
    multiple=True,
    required=True,
    help="Value to include (repeat for multiple).",
)
@click.option("--visual", default=None, help="Visual name (adds visual filter if given).")
@click.option("--name", "-n", default=None, help="Filter ID (auto-generated if omitted).")
@click.pass_context
@pass_context
def add_categorical_cmd(
    ctx: PbiContext,
    click_ctx: click.Context,
    page: str,
    table: str,
    column: str,
    values: tuple[str, ...],
    visual: str | None,
    name: str | None,
) -> None:
    """Add a categorical filter to a page or visual."""
    from pbi_cli.core.filter_backend import filter_add_categorical
    from pbi_cli.core.pbir_path import resolve_report_path

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(
        ctx,
        filter_add_categorical,
        definition_path=definition_path,
        page_name=page,
        table=table,
        column=column,
        values=list(values),
        visual_name=visual,
        name=name,
    )


@filters.command(name="add-topn")
@click.option("--page", required=True, help="Page name (folder name, not display name).")
@click.option("--table", required=True, help="Table containing the filtered column.")
@click.option("--column", required=True, help="Column to filter (e.g. Country).")
@click.option("--n", type=int, required=True, help="Number of items to keep.")
@click.option("--order-by-table", required=True, help="Table containing the ordering column.")
@click.option("--order-by-column", required=True, help="Column to rank by (e.g. Sales).")
@click.option(
    "--direction",
    default="Top",
    show_default=True,
    help="'Top' (highest N) or 'Bottom' (lowest N).",
)
@click.option("--visual", default=None, help="Visual name (adds visual filter if given).")
@click.option("--name", "-n_", default=None, help="Filter ID (auto-generated if omitted).")
@click.pass_context
@pass_context
def add_topn_cmd(
    ctx: PbiContext,
    click_ctx: click.Context,
    page: str,
    table: str,
    column: str,
    n: int,
    order_by_table: str,
    order_by_column: str,
    direction: str,
    visual: str | None,
    name: str | None,
) -> None:
    """Add a TopN filter (keep top/bottom N rows by a ranking column)."""
    from pbi_cli.core.filter_backend import filter_add_topn
    from pbi_cli.core.pbir_path import resolve_report_path

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(
        ctx,
        filter_add_topn,
        definition_path=definition_path,
        page_name=page,
        table=table,
        column=column,
        n=n,
        order_by_table=order_by_table,
        order_by_column=order_by_column,
        direction=direction,
        visual_name=visual,
        name=name,
    )


@filters.command(name="add-relative-date")
@click.option("--page", required=True, help="Page name (folder name, not display name).")
@click.option("--table", required=True, help="Table containing the date column.")
@click.option("--column", required=True, help="Date column to filter (e.g. Date).")
@click.option("--amount", type=int, required=True, help="Number of periods (e.g. 3).")
@click.option(
    "--unit",
    required=True,
    help="Time unit: days, weeks, months, or years.",
)
@click.option("--visual", default=None, help="Visual name (adds visual filter if given).")
@click.option("--name", "-n", default=None, help="Filter ID (auto-generated if omitted).")
@click.pass_context
@pass_context
def add_relative_date_cmd(
    ctx: PbiContext,
    click_ctx: click.Context,
    page: str,
    table: str,
    column: str,
    amount: int,
    unit: str,
    visual: str | None,
    name: str | None,
) -> None:
    """Add a RelativeDate filter (e.g. last 3 months)."""
    from pbi_cli.core.filter_backend import filter_add_relative_date
    from pbi_cli.core.pbir_path import resolve_report_path

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(
        ctx,
        filter_add_relative_date,
        definition_path=definition_path,
        page_name=page,
        table=table,
        column=column,
        amount=amount,
        time_unit=unit,
        visual_name=visual,
        name=name,
    )


@filters.command(name="remove")
@click.argument("filter_name")
@click.option("--page", required=True, help="Page name (folder name, not display name).")
@click.option("--visual", default=None, help="Visual name (removes from visual if given).")
@click.pass_context
@pass_context
def remove_cmd(
    ctx: PbiContext,
    click_ctx: click.Context,
    filter_name: str,
    page: str,
    visual: str | None,
) -> None:
    """Remove a filter by name from a page or visual."""
    from pbi_cli.core.filter_backend import filter_remove
    from pbi_cli.core.pbir_path import resolve_report_path

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(
        ctx,
        filter_remove,
        definition_path=definition_path,
        page_name=page,
        filter_name=filter_name,
        visual_name=visual,
    )


@filters.command(name="clear")
@click.option("--page", required=True, help="Page name (folder name, not display name).")
@click.option("--visual", default=None, help="Visual name (clears visual filters if given).")
@click.pass_context
@pass_context
def clear_cmd(
    ctx: PbiContext,
    click_ctx: click.Context,
    page: str,
    visual: str | None,
) -> None:
    """Remove all filters from a page or visual."""
    from pbi_cli.core.filter_backend import filter_clear
    from pbi_cli.core.pbir_path import resolve_report_path

    report_path = click_ctx.parent.obj.get("report_path") if click_ctx.parent else None
    definition_path = resolve_report_path(report_path)
    run_command(
        ctx,
        filter_clear,
        definition_path=definition_path,
        page_name=page,
        visual_name=visual,
    )
