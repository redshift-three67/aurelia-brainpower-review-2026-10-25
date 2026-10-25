from __future__ import annotations

import json

import typer

from core.db.health import collect_runtime_health, format_health_report


def health(
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Health-Report als JSON ausgeben.",
    ),
    strict: bool = typer.Option(
        False,
        "--strict",
        help="Warnungen ebenfalls als Fehler behandeln.",
    ),
) -> None:
    """Prueft Python-Umgebung, Profile, Kern-Datenbanken und Exportpfade."""
    report = collect_runtime_health(strict=strict)

    if json_output:
        typer.echo(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        typer.echo(format_health_report(report))

    if not report["ok"]:
        raise typer.Exit(1)
