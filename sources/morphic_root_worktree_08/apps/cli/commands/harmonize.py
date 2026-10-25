import typer
from typing import Optional
from cli.utils.backup import log_command

# Sub‑Typer für Harmonisierung‑Befehle
harmonize_app = typer.Typer(help="Harmonisierung‑Befehle")

@log_command
@harmonize_app.command("harmonize")
def harmonize(
    frequency: float = typer.Argument(..., help="Ziel‑Frequenz in Hz (z.B. 432.0)"),
    duration: int = typer.Argument(..., help="Dauer in Minuten"),
    intention: str = typer.Option("harmonization", "--intention", "-i", help="Intention (healing, clearing, protection, etc.)"),
    use_cpu: bool = typer.Option(True, "--cpu/--no-cpu", help="CPU‑Timing‑Modulation verwenden"),
    use_gpu: bool = typer.Option(False, "--gpu/--no-gpu", help="GPU‑Modulation verwenden"),
    use_ram: bool = typer.Option(False, "--ram/--no-ram", help="RAM Access Pattern Modulation verwenden"),
    use_websocket: bool = typer.Option(False, "--websocket/--no-websocket", help="WebSocket‑Übertragung verwenden"),
) -> None:
    """Startet die Harmonisierung mit den angegebenen Parametern."""
    from services import harmonization_worker as worker

    hardware_config = {
        "use_cpu": use_cpu,
        "use_gpu": use_gpu,
        "use_ram": use_ram,
        "use_websocket": use_websocket,
        "use_quartz": False,
    }
    try:
        job_id = worker.start_harmonization_job(
            target_frequency=frequency,
            duration_minutes=duration,
            intention=intention,
            hardware_config=hardware_config,
        )
    except Exception as exc:
        typer.echo(f"[FEHLER] Harmonisierung konnte nicht gestartet werden: {exc}", err=True)
        raise typer.Exit(1) from exc

    typer.echo("[OK] Harmonisierung gestartet")
    typer.echo(f"Job-ID: {job_id}")
    typer.echo(f"Status: python -m apps.cli.main harmonize harmonize-status {job_id}")
    typer.echo(f"Stop:   python -m apps.cli.main harmonize harmonize-stop {job_id}")

@log_command
@harmonize_app.command("harmonize-status")
def harmonize_status(
    job_id: Optional[str] = typer.Argument(None, help="Job‑ID (optional, zeigt alle Jobs wenn leer)"),
    active_only: bool = typer.Option(False, "--active", "-a", help="Nur aktive Jobs anzeigen"),
) -> None:
    """Zeigt den Status von Harmonisierung‑Jobs an."""
    from services import harmonization_worker as worker

    if job_id:
        job = worker.HarmonizationJob.load(job_id)
        if not job:
            typer.echo(f"[FEHLER] Job nicht gefunden: {job_id}", err=True)
            raise typer.Exit(1)
        typer.echo(worker.format_job_status(job))
        return

    jobs = worker.get_active_jobs() if active_only else worker.list_all_jobs()
    if not jobs:
        typer.echo("Keine Harmonisierungs-Jobs gefunden.")
        return

    typer.echo(f"Gefundene Jobs: {len(jobs)}")
    for job in jobs:
        typer.echo(worker.format_job_status(job))

@log_command
@harmonize_app.command("harmonize-stop")
def harmonize_stop(
    job_id: str = typer.Argument(..., help="Job‑ID des zu stoppenden Jobs"),
) -> None:
    """Stoppt einen laufenden Harmonisierung‑Job."""
    from services import harmonization_worker as worker

    if worker.stop_harmonization_job(job_id):
        typer.echo(f"[OK] Harmonisierung gestoppt: {job_id}")
        return

    job = worker.HarmonizationJob.load(job_id)
    if job is None:
        typer.echo(f"[FEHLER] Job nicht gefunden: {job_id}", err=True)
    else:
        typer.echo(f"[FEHLER] Job ist nicht aktiv (Status: {job.status})", err=True)
    raise typer.Exit(1)
