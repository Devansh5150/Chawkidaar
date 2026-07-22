import importlib.metadata
import os
import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

REQUIRED_PACKAGES = [
    "typer",
    "rich",
    "fastapi",
    "uvicorn",
    "sqlmodel",
    "pydantic",
    "yaml",  # pyyaml
    "telegram",  # python-telegram-bot
    "git",  # gitpython
    "dotenv",  # python-dotenv
]


def run_doctor() -> None:
    """Run health and environment diagnostic checks for Chawkidaar."""
    console.print(
        Panel(
            "[bold blue]Chawkidaar System Diagnostics (Doctor)[/bold blue]",
            expand=False,
        )
    )

    # Table 1: Environment & System Info
    sys_table = Table(
        title="System Environment",
        show_header=True,
        header_style="bold magenta",
    )
    sys_table.add_column("Check", style="cyan")
    sys_table.add_column("Details", style="green")
    sys_table.add_column("Status", justify="center")

    # Python version check
    v = sys.version_info
    py_version = f"{v.major}.{v.minor}.{v.micro}"
    py_status = (
        "[bold green]PASS[/bold green]"
        if v >= (3, 10)
        else "[bold red]FAIL (Requires Python 3.10+)[/bold red]"
    )
    sys_table.add_row("Python Version", py_version, py_status)

    # Virtual environment check
    in_venv = sys.prefix != sys.base_prefix
    venv_path = sys.prefix if in_venv else "None"
    venv_status = (
        "[bold green]Active[/bold green]"
        if in_venv
        else "[bold yellow]Not in Virtualenv[/bold yellow]"
    )
    sys_table.add_row("Virtual Environment", venv_path, venv_status)

    # OS Platform check
    sys_table.add_row("Operating System", sys.platform, "[bold green]OK[/bold green]")

    # Config / .env file check
    env_exists = os.path.exists(".env")
    env_msg = ".env found" if env_exists else ".env missing (see .env.example)"
    env_status = (
        "[bold green]OK[/bold green]"
        if env_exists
        else "[bold yellow]WARN[/bold yellow]"
    )
    sys_table.add_row(".env Configuration", env_msg, env_status)

    console.print(sys_table)

    # Table 2: Dependency Verification
    dep_table = Table(
        title="Core Dependencies",
        show_header=True,
        header_style="bold magenta",
    )
    dep_table.add_column("Package Module", style="cyan")
    dep_table.add_column("Installed Version", style="yellow")
    dep_table.add_column("Status", justify="center")

    all_passed = True
    for package in REQUIRED_PACKAGES:
        try:
            mod = importlib.import_module(package)
            version = getattr(mod, "__version__", "Installed")
            dep_table.add_row(package, str(version), "[bold green]OK[/bold green]")
        except ImportError:
            dep_table.add_row(package, "Missing", "[bold red]FAIL[/bold red]")
            all_passed = False

    console.print(dep_table)

    if all_passed and sys.version_info >= (3, 10):
        msg = (
            "\n[bold green][+] System is healthy and ready for Chawkidaar"
            " execution![/bold green]\n"
        )
        console.print(msg)
    else:
        msg = (
            "\n[bold yellow][!] Diagnostics completed with warnings or missing"
            " dependencies.[/bold yellow]\n"
        )
        console.print(msg)
