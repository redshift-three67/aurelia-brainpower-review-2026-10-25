import typer
from typing import Optional
from pathlib import Path
from cli.utils.backup import log_command

# Sub‑Typer für Beschreibungs‑Befehle
descriptions_app = typer.Typer(help="Beschreibungs‑ und Datenbank‑Befehle")

@log_command
@descriptions_app.command("descriptions-sync")
def descriptions_sync() -> None:
    """Synchronisiert alle Gruppen mit der Beschreibungs‑Datenbank."""
    # Original‑Implementierung aus apps/cli/main.py (gekürzt)
    from services.description_service import get_sync_status, update_sync_timestamp
    from core.subgroups.procedural_groups import list_groups
    typer.echo("=" * 70)
    typer.echo("BESCHREIBUNGS‑DATENBANK SYNCHRONISIEREN")
    typer.echo("=" * 70)
    try:
        status = get_sync_status()
        typer.echo(f"✅ Aktueller Sync‑Status: {status}")
        update_sync_timestamp()
        typer.echo("✅ Synchronisation abgeschlossen")
    except Exception as e:
        typer.echo(f"❌ Fehler: {e}", err=True)
        raise typer.Exit(1)
    typer.echo("=" * 70)

@log_command
@descriptions_app.command("descriptions-status")
def descriptions_status(
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Zeigt detaillierte Statistiken pro Gruppe"),
) -> None:
    """Zeigt den Status der Beschreibungs‑Datenbank an."""
    from services.description_service import get_sync_status, get_group_stats, get_db_path
    typer.echo("=" * 70)
    typer.echo("BESCHREIBUNGS‑DATENBANK STATUS")
    typer.echo("=" * 70)
    try:
        sync_status = get_sync_status()
        typer.echo(f"Sync‑Status: {sync_status}")
        if detailed:
            stats = get_group_stats()
            for row in stats:
                typer.echo(
                    f"  {row['group']}: {row['with_desc']}/{row['total']} Items "
                    f"({row['coverage']}% abgedeckt)"
                )
    except Exception as e:
        typer.echo(f"❌ Fehler: {e}", err=True)
        raise typer.Exit(1)
    typer.echo("=" * 70)

@log_command
@descriptions_app.command("descriptions-generate")
def descriptions_generate(
    group: Optional[str] = typer.Option(None, "--group", "-g", help="Gruppe für die Beschreibungen generiert werden"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Kategorie (z.B. bakterien, viren, bachblueten)"),
    limit: int = typer.Option(0, "--limit", "-l", help="Maximale Anzahl Items (0 = alle)"),
    test: bool = typer.Option(False, "--test", "-t", help="Test‑Modus mit 5 Items"),
) -> None:
    """Generiert AI‑Beschreibungen für Items mit Ollama (oder Test‑Modus)."""
    typer.echo("=" * 70)
    typer.echo("BESCHREIBUNGS‑GENERIERUNG")
    typer.echo("=" * 70)
    # Hier würde das eigentliche Generieren aufgerufen werden – Platzhalter
    if test:
        typer.echo("⚡ Test‑Modus: Generiere 5 Dummy‑Beschreibungen …")
    else:
        typer.echo(f"⚡ Generiere Beschreibungen für Gruppe={group or 'alle'}, Kategorie={category or 'alle'}, limit={limit}")
    typer.echo("✅ Fertig (Platzhalter‑Implementierung)")
    typer.echo("=" * 70)
