from __future__ import annotations

import json
from pathlib import Path

import typer

from core.compliance.runtime_manifest import RuntimeManifestService, runtime_root


privacy_app = typer.Typer(help="DSGVO-nahe Runtime-Manifeste, Safe-Views, Audit und Loeschkaskade.")


def _service(runtime: Path | None) -> RuntimeManifestService:
    return RuntimeManifestService(runtime if runtime is not None else runtime_root())


@privacy_app.command("clients")
def list_clients(
    runtime: Path | None = typer.Option(None, "--runtime", help="Runtime-Store-Verzeichnis."),
    json_output: bool = typer.Option(False, "--json", help="Maschinenlesbare JSON-Ausgabe."),
) -> None:
    clients = _service(runtime).list_clients_safe()
    if json_output:
        typer.echo(json.dumps(clients, indent=2, ensure_ascii=False))
        return
    if not clients:
        typer.echo("Keine Klienten im Runtime-Manifest.")
        return
    for client in clients:
        typer.echo(
            f"{client.get('client_id')} created={client.get('created_at')} updated={client.get('updated_at')}"
        )


@privacy_app.command("erasure-manifest")
def erasure_manifest(
    client_id: str = typer.Argument(..., help="Pseudonyme Client-ID, z.B. cli-..."),
    runtime: Path | None = typer.Option(None, "--runtime", help="Runtime-Store-Verzeichnis."),
) -> None:
    manifest = _service(runtime).erasure_manifest(client_id)
    typer.echo(json.dumps(manifest, indent=2, ensure_ascii=False))


@privacy_app.command("erase")
def erase_client(
    client_id: str = typer.Argument(..., help="Pseudonyme Client-ID, z.B. cli-..."),
    runtime: Path | None = typer.Option(None, "--runtime", help="Runtime-Store-Verzeichnis."),
    gate_token: str = typer.Option("", "--gate-token", help="Expliziter Gate-Token fuer Loeschung."),
) -> None:
    try:
        result = _service(runtime).execute_erasure(client_id, gate_token=gate_token)
    except ValueError as exc:
        typer.echo(f"[FEHLER] {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(json.dumps(result, indent=2, ensure_ascii=False))


@privacy_app.command("purge-expired")
def purge_expired(
    retention_days: int = typer.Option(
        ..., "--retention-days", help="Aufbewahrungsfrist in Tagen (DSGVO-Speicherbegrenzung)."
    ),
    runtime: Path | None = typer.Option(None, "--runtime", help="Runtime-Store-Verzeichnis."),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Nur Kandidaten ermitteln, nichts loeschen."
    ),
) -> None:
    service = _service(runtime)
    result = service.purge_expired(retention_days, dry_run=dry_run)
    label = "Kandidaten (dry-run)" if dry_run else "Geloeschte Clients"
    typer.echo(f"{label}: {len(result)}")
    typer.echo(json.dumps(result, indent=2, ensure_ascii=False))


@privacy_app.command("audit")
def audit_client(
    client_id: str = typer.Argument(..., help="Pseudonyme Client-ID, z.B. cli-..."),
    runtime: Path | None = typer.Option(None, "--runtime", help="Runtime-Store-Verzeichnis."),
    json_output: bool = typer.Option(False, "--json", help="Maschinenlesbare JSON-Ausgabe."),
) -> None:
    entries = _service(runtime).audit_for_client(client_id)
    if json_output:
        typer.echo(json.dumps(entries, indent=2, ensure_ascii=False))
        return
    if not entries:
        typer.echo("Keine Audit-Eintraege fuer diesen Klienten.")
        return
    for entry in entries:
        typer.echo(
            f"{entry.get('created_at')} {entry.get('action')} {entry.get('outcome')} {entry.get('entity_type')}:{entry.get('entity_id')}"
        )
