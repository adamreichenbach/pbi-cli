"""Skill installer commands for Claude Code integration."""

from __future__ import annotations

import importlib.resources
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from importlib.abc import Traversable

import click

from pbi_cli.main import pass_context

SKILLS_TARGET_DIR = Path.home() / ".claude" / "skills"


def _get_bundled_skills() -> dict[str, Traversable]:
    """Return a mapping of skill-name -> Traversable for each bundled skill."""
    skills_pkg = importlib.resources.files("pbi_cli.skills")
    result: dict[str, Traversable] = {}
    for item in skills_pkg.iterdir():
        if item.is_dir() and (item / "SKILL.md").is_file():
            result[item.name] = item
    return result


def _is_installed(skill_name: str) -> bool:
    """Check if a skill is already installed in ~/.claude/skills/."""
    return (SKILLS_TARGET_DIR / skill_name / "SKILL.md").exists()


@click.group("skills")
def skills() -> None:
    """Manage Claude Code skills for Power BI workflows."""


@skills.command("list")
@pass_context
def skills_list(ctx: object) -> None:
    """List available and installed skills."""
    bundled = _get_bundled_skills()
    if not bundled:
        click.echo("No bundled skills found.", err=True)
        return

    click.echo("Available Power BI skills:\n", err=True)
    for name in sorted(bundled):
        status = "installed" if _is_installed(name) else "not installed"
        click.echo(f"  {name:<30} [{status}]", err=True)
    click.echo(
        f"\nTarget directory: {SKILLS_TARGET_DIR}",
        err=True,
    )


@skills.command("install")
@click.option("--skill", "skill_name", default=None, help="Install a specific skill.")
@click.option("--force", is_flag=True, default=False, help="Overwrite existing installations.")
@pass_context
def skills_install(ctx: object, skill_name: str | None, force: bool) -> None:
    """Install skills to ~/.claude/skills/ for Claude Code discovery."""
    bundled = _get_bundled_skills()
    if not bundled:
        click.echo("No bundled skills found.", err=True)
        return

    to_install = (
        {skill_name: bundled[skill_name]}
        if skill_name and skill_name in bundled
        else bundled
    )

    if skill_name and skill_name not in bundled:
        raise click.ClickException(
            f"Unknown skill '{skill_name}'. "
            f"Available: {', '.join(sorted(bundled))}"
        )

    installed_count = 0
    for name, source in sorted(to_install.items()):
        target_dir = SKILLS_TARGET_DIR / name
        if target_dir.exists() and not force:
            click.echo(f"  {name}: already installed (use --force to overwrite)", err=True)
            continue

        target_dir.mkdir(parents=True, exist_ok=True)
        source_file = source / "SKILL.md"
        target_file = target_dir / "SKILL.md"

        # Read from importlib resource and write to target
        target_file.write_text(source_file.read_text(encoding="utf-8"), encoding="utf-8")
        installed_count += 1
        click.echo(f"  {name}: installed", err=True)

    click.echo(f"\n{installed_count} skill(s) installed to {SKILLS_TARGET_DIR}", err=True)


@skills.command("uninstall")
@click.option("--skill", "skill_name", default=None, help="Uninstall a specific skill.")
@pass_context
def skills_uninstall(ctx: object, skill_name: str | None) -> None:
    """Remove installed skills from ~/.claude/skills/."""
    bundled = _get_bundled_skills()
    names = [skill_name] if skill_name else sorted(bundled)

    removed_count = 0
    for name in names:
        target_dir = SKILLS_TARGET_DIR / name
        if not target_dir.exists():
            click.echo(f"  {name}: not installed", err=True)
            continue

        shutil.rmtree(target_dir)
        removed_count += 1
        click.echo(f"  {name}: removed", err=True)

    click.echo(f"\n{removed_count} skill(s) removed.", err=True)
