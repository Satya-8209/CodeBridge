"""
Seed Hindsight memory with synthetic past incidents.
Run this BEFORE your demo to give the agent historical context.

Usage:
    python scripts/seed.py
"""
import sys
import os
import json
import time

# Force UTF-8 output on Windows to handle emoji
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import httpx
from rich.console import Console
from rich.progress import track

console = Console()
BACKEND_URL = "http://localhost:8000"


def main():
    console.print("\n[bold cyan]🌱 Seeding Hindsight memory with past incidents...[/bold cyan]\n")

    # Check backend is up
    try:
        httpx.get(f"{BACKEND_URL}/health", timeout=5.0).raise_for_status()
    except Exception:
        console.print("[bold red]❌ Backend is not running![/bold red]")
        console.print("   Start it first: [bold]uvicorn backend.main:app --reload[/bold]")
        sys.exit(1)

    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "seed_incidents.json")
    with open(data_path) as f:
        incidents = json.load(f)

    console.print(f"Found [bold]{len(incidents)}[/bold] incidents to seed.\n")

    success = 0
    for i, inc in enumerate(track(incidents, description="Storing in memory..."), 1):
        try:
            resp = httpx.post(
                f"{BACKEND_URL}/resolve",
                json={
                    "alert_id": f"SEED-{i:03d}",
                    "service": inc["service"],
                    "title": inc["title"],
                    "root_cause": inc["root_cause"],
                    "fix_applied": inc["fix_applied"],
                    "time_to_resolve_minutes": inc["time_to_resolve_minutes"],
                },
                timeout=15.0,
            )
            resp.raise_for_status()
            success += 1
            time.sleep(0.3)  # Be gentle with the API
        except Exception as e:
            console.print(f"[red]  ✗ Failed to seed incident {i}: {e}[/red]")

    console.print(f"\n[bold green]✅ Seeded {success}/{len(incidents)} incidents into Hindsight memory![/bold green]")
    console.print(
        "\n[dim]Now run:[/dim] [bold]python cli/cli.py alert payment-service "
        '-e "OOMKilled: pod restarted"[/bold]\n'
    )


if __name__ == "__main__":
    main()
