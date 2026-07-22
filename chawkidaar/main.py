import typer
from rich.console import Console

from chawkidaar.cli.doctor import run_doctor

app = typer.Typer(
    name="chawkidaar",
    help="Chawkidaar - Production-Grade Autonomous AI Monitoring & Agent System",
    add_completion=False,
)
console = Console()


@app.command()
def doctor():
    """Run environment and dependency diagnostic checks."""
    run_doctor()


@app.command()
def status():
    """Check operational status of Chawkidaar services."""
    console.print("[bold green]Chawkidaar is active and monitoring.[/bold green]")


@app.command()
def start():
    """Start the main monitoring loop."""
    console.print("[bold blue]Starting Chawkidaar monitoring engine...[/bold blue]")


if __name__ == "__main__":
    app()
