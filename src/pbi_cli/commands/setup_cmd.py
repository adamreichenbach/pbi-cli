"""pbi setup: verify environment and install skills."""

from __future__ import annotations

import click

from pbi_cli.core.output import print_error, print_info, print_json, print_success
from pbi_cli.main import PbiContext, pass_context


@click.command()
@click.option("--info", is_flag=True, default=False, help="Show environment info.")
@pass_context
def setup(ctx: PbiContext, info: bool) -> None:
    """Verify the pbi-cli environment is ready.

    Checks that pythonnet and the bundled .NET DLLs are available.
    Also installs Claude Code skills if applicable.
    """
    if info:
        _show_info(ctx.json_output)
        return

    _verify(ctx.json_output)


def _show_info(json_output: bool) -> None:
    """Show environment info."""
    from pbi_cli import __version__
    from pbi_cli.core.dotnet_loader import _dll_dir

    dll_path = _dll_dir()
    dlls_found = list(dll_path.glob("*.dll")) if dll_path.exists() else []

    result = {
        "version": __version__,
        "dll_path": str(dll_path),
        "dlls_found": len(dlls_found),
        "dll_names": [d.name for d in dlls_found],
    }

    # Check pythonnet
    try:
        import pythonnet  # noqa: F401

        result["pythonnet"] = "installed"
    except ImportError:
        result["pythonnet"] = "missing"

    if json_output:
        print_json(result)
    else:
        print_info(f"pbi-cli v{result['version']}")
        print_info(f"DLL path: {result['dll_path']}")
        print_info(f"DLLs found: {result['dlls_found']}")
        print_info(f"pythonnet: {result['pythonnet']}")


def _verify(json_output: bool) -> None:
    """Verify the environment is ready."""
    errors: list[str] = []

    # Check pythonnet
    try:
        import pythonnet  # noqa: F401
    except ImportError:
        errors.append("pythonnet not installed. Run: pip install pythonnet")

    # Check DLLs
    from pbi_cli.core.dotnet_loader import _dll_dir

    dll_path = _dll_dir()
    if not dll_path.exists():
        errors.append(f"DLL directory not found: {dll_path}")
    else:
        required = [
            "Microsoft.AnalysisServices.Tabular.dll",
            "Microsoft.AnalysisServices.AdomdClient.dll",
        ]
        for name in required:
            if not (dll_path / name).exists():
                errors.append(f"Missing DLL: {name}")

    if errors:
        for err in errors:
            print_error(err)
        if json_output:
            print_json({"status": "error", "errors": errors})
        raise SystemExit(1)

    if json_output:
        print_json({"status": "ready"})
    else:
        print_success("Environment is ready.")
