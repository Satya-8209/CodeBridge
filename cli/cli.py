"""
CLI for the Incident Memory Agent.
Uses Typer for a clean command-line experience.

Commands:
  alert   — Fire a new alert and get AI-powered suggestions
  resolve — Mark an incident as resolved and store it in memory
  seed    — Seed memory with synthetic past incidents (for demo)
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import httpx
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich import print as rprint

app = typer.Typer(
    name="incident-agent",
    help="🧠 DevOps Incident Memory Agent — powered by Hindsight + xAI Grok",
    add_completion=False,
)
console = Console()
BACKEND_URL = "http://localhost:8000"


@app.command()
def alert(
    service: str = typer.Argument(..., help="Affected service name (e.g. payment-service)"),
    error: str = typer.Option(..., "--error", "-e", help="Error log or alert description"),
    severity: str = typer.Option("high", "--severity", "-s", help="critical | high | medium | low"),
):
    """
    🚨 Fire a new alert and get memory-powered AI suggestions.

    Example:
        python cli/cli.py alert payment-service -e "OOMKilled: container exceeded memory limit"
    """
    console.print(f"\n[bold yellow]🔍 Querying Hindsight memory...[/bold yellow]")
    console.print(f"   Service: [cyan]{service}[/cyan]")
    console.print(f"   Alert:   [red]{error[:80]}[/red]\n")

    try:
        resp = httpx.post(
            f"{BACKEND_URL}/alert",
            json={
                "title": error[:100],
                "service": service,
                "severity": severity,
                "error_log": error,
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
    except httpx.ConnectError:
        console.print("[bold red]❌ Cannot connect to backend. Is it running?[/bold red]")
        console.print("   Run: [bold]uvicorn backend.main:app --reload[/bold]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")
        raise typer.Exit(1)

    alert_id = data.get("alert_id", "???")
    similar = data.get("similar_incidents", [])
    suggestion = data.get("suggestion", "No suggestion.")
    memory_hit = data.get("memory_hit", False)

    # Memory match panel
    if memory_hit:
        console.print(
            Panel(
                f"[bold green]🧠 Found {len(similar)} similar past incident(s) in memory[/bold green]",
                title="Hindsight Memory",
                border_style="green",
            )
        )
        table = Table(title="Past Incidents", show_header=True, header_style="bold cyan")
        table.add_column("#", width=3)
        table.add_column("Memory Snippet", no_wrap=False)
        table.add_column("Score", width=8)
        for i, inc in enumerate(similar[:3], 1):
            score = f"{inc['score']:.3f}" if inc.get("score") is not None else "—"
            table.add_row(str(i), inc["text"][:200], score)
        console.print(table)
    else:
        console.print(
            Panel(
                "[yellow]🆕 No similar past incidents found in memory yet.[/yellow]\n"
                "[dim]Resolve incidents to build memory over time.[/dim]",
                title="Hindsight Memory",
                border_style="yellow",
            )
        )

    # Suggestion panel
    console.print(
        Panel(
            Markdown(suggestion),
            title=f"💡 AI Suggestion  [dim](Alert ID: {alert_id})[/dim]",
            border_style="blue",
        )
    )

    console.print(
        f"\n[dim]After resolving, run:[/dim] "
        f"[bold]python cli/cli.py resolve {alert_id} "
        f'--service {service} --title "..." --cause "..." --fix "..."[/bold]\n'
    )


@app.command()
def resolve(
    alert_id: str = typer.Argument(..., help="Alert ID returned by the alert command"),
    service: str = typer.Option(..., "--service", help="Service name"),
    title: str = typer.Option(..., "--title", "-t", help="Short incident title"),
    cause: str = typer.Option(..., "--cause", "-c", help="Root cause identified"),
    fix: str = typer.Option(..., "--fix", "-f", help="Fix that was applied"),
    ttm: int = typer.Option(0, "--ttm", help="Time to resolve in minutes"),
):
    """
    ✅ Mark an incident as resolved and store it in Hindsight memory.

    Example:
        python cli/cli.py resolve ABC123 --service payment-service \\
            --title "OOMKilled pod" --cause "Memory leak in retry handler" \\
            --fix "Rolled back to v2.3.1, capped retry list" --ttm 18
    """
    console.print(f"\n[bold green]✅ Storing resolution in Hindsight memory...[/bold green]")

    try:
        resp = httpx.post(
            f"{BACKEND_URL}/resolve",
            json={
                "alert_id": alert_id,
                "service": service,
                "title": title,
                "root_cause": cause,
                "fix_applied": fix,
                "time_to_resolve_minutes": ttm,
            },
            timeout=15.0,
        )
        resp.raise_for_status()
        data = resp.json()
    except httpx.ConnectError:
        console.print("[bold red]❌ Cannot connect to backend.[/bold red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")
        raise typer.Exit(1)

    console.print(
        Panel(
            f"[bold green]Memory stored successfully![/bold green]\n\n"
            f"Alert ID: [cyan]{alert_id}[/cyan]\n"
            f"Service:  [cyan]{service}[/cyan]\n"
            f"Bank:     [cyan]{data.get('bank', 'devops-incident-memory')}[/cyan]\n\n"
            f"[dim]{data.get('message', '')}[/dim]",
            title="🧠 Hindsight Memory Updated",
            border_style="green",
        )
    )


@app.command()
def health():
    """🏥 Check if the backend is running."""
    try:
        resp = httpx.get(f"{BACKEND_URL}/health", timeout=5.0)
        data = resp.json()
        console.print(f"[bold green]✅ Backend is up:[/bold green] {data}")
    except Exception as e:
        console.print(f"[bold red]❌ Backend unreachable: {e}[/bold red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
