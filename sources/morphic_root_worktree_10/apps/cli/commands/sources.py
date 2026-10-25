from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from core.source_registry import (
    DEFAULT_SOURCE_REGISTRY_PATH,
    SourceImportPlan,
    SourceRegistry,
    SourceRegistryError,
    validate_manifest,
)
from core.source_data_promotion import (
    SourceDataPromotionError,
    promote_staged_source_data,
    stage_source_data_batch,
)


source_app = typer.Typer(help="Verwaltet optionale externe und lokale Quellen-Repositories.")


def _load_registry(registry_path: Path) -> SourceRegistry:
    try:
        return SourceRegistry.load(registry_path)
    except SourceRegistryError as exc:
        typer.echo(f"[FEHLER] {exc}", err=True)
        raise typer.Exit(1) from exc


@source_app.command("list")
def list_sources(
    registry_path: Path = typer.Option(
        DEFAULT_SOURCE_REGISTRY_PATH,
        "--registry",
        help="Pfad zur Source-Registry JSON-Datei.",
    ),
    scope: str = typer.Option("", "--scope", help="Optionaler Scope-Filter, z.B. tcm oder radiation."),
    active_only: bool = typer.Option(False, "--active-only", help="Nur aktive Quellen anzeigen."),
    json_output: bool = typer.Option(False, "--json", help="Maschinenlesbare JSON-Ausgabe."),
) -> None:
    registry = _load_registry(registry_path)
    sources = registry.list_sources(scope=scope or None, active_only=active_only)

    if json_output:
        typer.echo(json.dumps([source.to_mapping() for source in sources], indent=2, ensure_ascii=False))
        return

    if not sources:
        typer.echo("Keine Quellen gefunden.")
        return

    for source in sources:
        state = "active" if source.active else source.status
        enabled = "enabled" if source.enabled else "disabled"
        scopes = ", ".join(source.scopes)
        typer.echo(f"{source.id}: {source.label} [{enabled}/{state}] scopes={scopes}")


@source_app.command("enable")
def enable_source(
    source_id: str = typer.Argument(..., help="Source-ID, z.B. nlm_mesh."),
    registry_path: Path = typer.Option(
        DEFAULT_SOURCE_REGISTRY_PATH,
        "--registry",
        help="Pfad zur Source-Registry JSON-Datei.",
    ),
    allow_quarantined: bool = typer.Option(
        False,
        "--allow-quarantined",
        help="Erlaubt das explizite Aktivieren quarantined Quellen.",
    ),
) -> None:
    registry = _load_registry(registry_path)
    try:
        source = registry.enable_source(source_id, allow_quarantined=allow_quarantined)
    except SourceRegistryError as exc:
        typer.echo(f"[FEHLER] {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"[OK] Quelle aktiviert: {source.id}")


@source_app.command("disable")
def disable_source(
    source_id: str = typer.Argument(..., help="Source-ID, z.B. nlm_mesh."),
    registry_path: Path = typer.Option(
        DEFAULT_SOURCE_REGISTRY_PATH,
        "--registry",
        help="Pfad zur Source-Registry JSON-Datei.",
    ),
) -> None:
    registry = _load_registry(registry_path)
    try:
        source = registry.disable_source(source_id)
    except SourceRegistryError as exc:
        typer.echo(f"[FEHLER] {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"[OK] Quelle deaktiviert: {source.id}")


@source_app.command("validate")
def validate_source_registry(
    manifest_path: Optional[Path] = typer.Argument(None, help="Optionales einzelnes Source-Manifest."),
    registry_path: Path = typer.Option(
        DEFAULT_SOURCE_REGISTRY_PATH,
        "--registry",
        help="Pfad zur Source-Registry JSON-Datei.",
    ),
) -> None:
    try:
        if manifest_path is not None:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict) and "source" in payload:
                payload = payload["source"]
            if not isinstance(payload, dict):
                raise SourceRegistryError("Manifest muss ein Source-Objekt enthalten.")
            validate_manifest(payload)
            typer.echo(f"[OK] Manifest gueltig: {manifest_path}")
        else:
            registry = SourceRegistry.load(registry_path)
            typer.echo(f"[OK] Registry gueltig: {registry.path} ({len(registry.list_sources())} Quellen)")
    except (OSError, json.JSONDecodeError, SourceRegistryError) as exc:
        typer.echo(f"[FEHLER] {exc}", err=True)
        raise typer.Exit(1) from exc


def _echo_import_plan(plan: SourceImportPlan, *, prefix: str) -> None:
    typer.echo(f"{prefix} {plan.action} {plan.source.id}: {plan.source.label}")
    if not plan.changed_fields:
        return
    for field_name, change in plan.changed_fields.items():
        typer.echo(f"  - {field_name}: {change['current']!r} -> {change['incoming']!r}")


@source_app.command("stage")
def stage_source(
    manifest_path: Path = typer.Argument(..., help="JSON-Manifest einer administrativen Quelle."),
    registry_path: Path = typer.Option(
        DEFAULT_SOURCE_REGISTRY_PATH,
        "--registry",
        help="Pfad zur Source-Registry JSON-Datei.",
    ),
    staging_dir: Path = typer.Option(..., "--staging-dir", help="Zielordner fuer validierte Staging-Manifeste."),
    replace: bool = typer.Option(False, "--replace", help="Bestehende Source-ID im Staging-Plan erlauben."),
) -> None:
    registry = _load_registry(registry_path)
    try:
        staged_path = registry.stage_manifest(manifest_path, staging_dir, replace=replace)
    except (OSError, json.JSONDecodeError, SourceRegistryError) as exc:
        typer.echo(f"[FEHLER] {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"[OK] Manifest staged: {staged_path}")


@source_app.command("import")
def import_source(
    manifest_path: Path = typer.Argument(..., help="JSON-Manifest einer administrativen Quelle."),
    registry_path: Path = typer.Option(
        DEFAULT_SOURCE_REGISTRY_PATH,
        "--registry",
        help="Pfad zur Source-Registry JSON-Datei.",
    ),
    replace: bool = typer.Option(False, "--replace", help="Bestehende Source-ID ersetzen."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Import-Plan anzeigen, ohne die Registry zu schreiben."),
    rollback_dir: Optional[Path] = typer.Option(
        None,
        "--rollback-dir",
        help="Optionaler Ordner fuer Rollback-Snapshots vor dem Schreiben.",
    ),
    batch_id: str = typer.Option("", "--batch-id", help="Optionale Batch-ID fuer den Rollback-Snapshot."),
) -> None:
    registry = _load_registry(registry_path)
    try:
        if dry_run:
            plan = registry.plan_import_manifest(manifest_path, replace=replace)
            _echo_import_plan(plan, prefix="[DRY-RUN]")
            return
        source = registry.import_manifest(
            manifest_path,
            replace=replace,
            rollback_dir=rollback_dir,
            batch_id=batch_id or None,
        )
    except (OSError, json.JSONDecodeError, SourceRegistryError) as exc:
        typer.echo(f"[FEHLER] {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"[OK] Quelle importiert: {source.id}")


@source_app.command("rollback")
def rollback_source_import(
    batch_id: str = typer.Argument(..., help="Batch-ID des Source-Registry-Imports."),
    registry_path: Path = typer.Option(
        DEFAULT_SOURCE_REGISTRY_PATH,
        "--registry",
        help="Pfad zur Source-Registry JSON-Datei.",
    ),
    rollback_dir: Path = typer.Option(..., "--rollback-dir", help="Ordner mit Rollback-Snapshots."),
) -> None:
    registry = _load_registry(registry_path)
    try:
        registry.rollback_import(batch_id, rollback_dir=rollback_dir)
    except (OSError, json.JSONDecodeError, SourceRegistryError) as exc:
        typer.echo(f"[FEHLER] {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"[OK] Import-Batch zurueckgerollt: {batch_id}")


@source_app.command("data-stage")
def stage_source_data(
    batch_path: Path = typer.Argument(..., help="JSON-Datenbatch einer registrierten Quelle."),
    registry_path: Path = typer.Option(
        DEFAULT_SOURCE_REGISTRY_PATH,
        "--registry",
        help="Pfad zur Source-Registry JSON-Datei.",
    ),
    staging_dir: Path = typer.Option(..., "--staging-dir", help="Zielordner fuer validierte Datenbatches."),
) -> None:
    registry = _load_registry(registry_path)
    try:
        staged_path = stage_source_data_batch(batch_path, staging_dir, registry)
    except (OSError, json.JSONDecodeError, SourceDataPromotionError) as exc:
        typer.echo(f"[FEHLER] {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"[OK] Datenbatch staged: {staged_path}")


@source_app.command("data-promote")
def promote_source_data(
    staged_path: Path = typer.Argument(..., help="Validierter staged Datenbatch."),
    ledger_path: Path = typer.Option(..., "--ledger", help="Audit-Ledger fuer Source-Datenpromotionen."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Promotion-Plan anzeigen, ohne Ledger zu schreiben."),
) -> None:
    try:
        result = promote_staged_source_data(staged_path, ledger_path, dry_run=dry_run)
    except (OSError, json.JSONDecodeError, SourceDataPromotionError) as exc:
        typer.echo(f"[FEHLER] {exc}", err=True)
        raise typer.Exit(1) from exc
    prefix = "[DRY-RUN]" if dry_run else "[OK]"
    typer.echo(
        f"{prefix} Source-Datenpromotion: {result['source_id']} "
        f"{result['data_type']} records={result['record_count']}"
    )
