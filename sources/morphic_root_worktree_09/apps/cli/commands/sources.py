from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from core.admin_catalog import (
    AdminCatalogService,
    CatalogContext,
    CatalogServiceError,
    ContractError,
)
from core.admin_catalog.store import CatalogStore, CatalogStoreError
from core.admin_catalog.validation_key_composition import (
    ValidationKeyCompositionError,
    validation_key_provider_from_environment,
    validation_key_provider_from_keyring,
)
from core.source_registry import (
    DEFAULT_SOURCE_REGISTRY_PATH,
    SourceImportPlan,
    SourceRegistry,
    SourceRegistryError,
    validate_manifest_file,
)
from core.source_data_promotion import (
    SourceDataPromotionError,
    import_staged_source_data_to_draft,
    preflight_staged_source_data_to_draft,
    promote_staged_source_data,
    stage_source_data_batch,
    validate_staged_source_artifact,
)


source_app = typer.Typer(help="Verwaltet optionale externe und lokale Quellen-Repositories.")


def _load_registry(registry_path: Path) -> SourceRegistry:
    try:
        return SourceRegistry.load(registry_path)
    except (OSError, UnicodeError, json.JSONDecodeError, SourceRegistryError) as exc:
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
    except (OSError, UnicodeError, json.JSONDecodeError, SourceRegistryError) as exc:
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
    except (OSError, UnicodeError, json.JSONDecodeError, SourceRegistryError) as exc:
        typer.echo(f"[FEHLER] {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"[OK] Quelle deaktiviert: {source.id}")


@source_app.command("validate")
def validate_source_registry(
    manifest_path: Optional[Path] = typer.Argument(None, help="Optionales einzelnes Source-Manifest."),
    import_root: Optional[Path] = typer.Option(
        None,
        "--import-root",
        help="Expliziter Admin-Importroot fuer lokale Source-Manifeste.",
    ),
    registry_path: Path = typer.Option(
        DEFAULT_SOURCE_REGISTRY_PATH,
        "--registry",
        help="Pfad zur Source-Registry JSON-Datei.",
    ),
) -> None:
    try:
        if manifest_path is not None:
            validate_manifest_file(manifest_path, import_root=import_root)
            typer.echo(f"[OK] Manifest gueltig: {manifest_path}")
        else:
            registry = SourceRegistry.load(registry_path)
            typer.echo(f"[OK] Registry gueltig: {registry.path} ({len(registry.list_sources())} Quellen)")
    except (OSError, UnicodeError, json.JSONDecodeError, SourceRegistryError) as exc:
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
    import_root: Optional[Path] = typer.Option(
        None,
        "--import-root",
        help="Expliziter Admin-Importroot fuer lokale Source-Manifeste.",
    ),
    approval_id: str = typer.Option(
        ...,
        "--approval-id",
        help="Explizite Approval-ID fuer das hashgebundene Staging-Artefakt.",
    ),
    replace: bool = typer.Option(False, "--replace", help="Bestehende Source-ID im Staging-Plan erlauben."),
) -> None:
    registry = _load_registry(registry_path)
    try:
        staged_path = registry.stage_manifest(
            manifest_path,
            staging_dir,
            replace=replace,
            import_root=import_root,
            approval_id=approval_id,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, SourceRegistryError) as exc:
        typer.echo(f"[FEHLER] {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"[OK] Manifest staged: {staged_path}")


@source_app.command("import-plan")
def plan_source_import(
    manifest_path: Path = typer.Argument(..., help="JSON-Manifest einer administrativen Quelle."),
    registry_path: Path = typer.Option(
        DEFAULT_SOURCE_REGISTRY_PATH,
        "--registry",
        help="Pfad zur Source-Registry JSON-Datei.",
    ),
    replace: bool = typer.Option(False, "--replace", help="Bestehende Source-ID im Plan ersetzen."),
    import_root: Optional[Path] = typer.Option(
        None,
        "--import-root",
        help="Expliziter Admin-Importroot fuer lokale Source-Manifeste.",
    ),
) -> None:
    registry = _load_registry(registry_path)
    try:
        plan = registry.plan_import_manifest(
            manifest_path,
            replace=replace,
            import_root=import_root,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, SourceRegistryError) as exc:
        typer.echo(f"[FEHLER] {exc}", err=True)
        raise typer.Exit(1) from exc
    _echo_import_plan(plan, prefix="[PLAN]")


@source_app.command("import")
def import_source(
    staged_path: Path = typer.Argument(..., help="Freigegebenes Source-Stage-Artefakt."),
    registry_path: Path = typer.Option(
        DEFAULT_SOURCE_REGISTRY_PATH,
        "--registry",
        help="Pfad zur Source-Registry JSON-Datei.",
    ),
    rollback_dir: Optional[Path] = typer.Option(
        None,
        "--rollback-dir",
        help="Optionaler Ordner fuer Rollback-Snapshots vor dem Schreiben.",
    ),
    batch_id: str = typer.Option("", "--batch-id", help="Optionale Batch-ID fuer den Rollback-Snapshot."),
) -> None:
    registry = _load_registry(registry_path)
    try:
        source = registry.import_manifest(
            staged_path,
            rollback_dir=rollback_dir,
            batch_id=batch_id or None,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, SourceRegistryError) as exc:
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
    expected_revision: int = typer.Option(
        ...,
        "--expected-revision",
        min=0,
        help="Erwartete aktuelle Registry-Revision fuer konfliktfreien Rollback.",
    ),
) -> None:
    registry = _load_registry(registry_path)
    try:
        registry.rollback_import(
            batch_id,
            rollback_dir=rollback_dir,
            expected_revision=expected_revision,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, SourceRegistryError) as exc:
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
    quarantine_dir: Optional[Path] = typer.Option(
        None,
        "--quarantine-dir",
        help="Separater Root fuer quarantined analysis_only-Datenbatches.",
    ),
) -> None:
    registry = _load_registry(registry_path)
    try:
        staged_path = stage_source_data_batch(
            batch_path,
            staging_dir,
            registry,
            quarantine_dir=quarantine_dir,
        )
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        SourceDataPromotionError,
        SourceRegistryError,
    ) as exc:
        typer.echo(f"[FEHLER] {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"[OK] Datenbatch staged: {staged_path}")


@source_app.command("data-import-draft")
def import_source_data_draft(
    staged_path: Path = typer.Argument(..., help="Validierter immutable Stage-Datenbatch."),
    catalog_db: Path = typer.Option(
        ..., "--catalog-db", help="Explizite isolierte Admin-Catalog-SQLite-Datei."
    ),
    staging_root: Path = typer.Option(
        ..., "--staging-root", help="Expliziter autoritativer Stage-Root."
    ),
    registry_path: Path = typer.Option(
        ...,
        "--registry",
        help="Pfad zur aktuell zu revalidierenden Source-Registry JSON-Datei.",
    ),
    draft_id: str = typer.Option(..., "--draft-id", help="Neue Catalog-Draft-ID."),
    operator_id: str = typer.Option(..., "--operator-id"),
    workspace_id: str = typer.Option(..., "--workspace-id"),
    tenant_id: str = typer.Option(..., "--tenant-id"),
    scope: str = typer.Option(..., "--scope"),
    actor_id: str = typer.Option(..., "--actor-id"),
    reason: str = typer.Option(..., "--reason"),
    base_revision_id: str = typer.Option(
        "",
        "--base-revision-id",
        help="Optionale explizite Catalog-Revision als Draftbasis; nie implizit aktiv.",
    ),
    validation_keyring: Optional[Path] = typer.Option(
        None,
        "--validation-keyring",
        help="Externe JSON-Keyring-Datei fuer Admin-Catalog-Validation-Attestations.",
    ),
) -> None:
    registry = _load_registry(registry_path)
    try:
        context = CatalogContext(
            operator_id=operator_id,
            workspace_id=workspace_id,
            tenant_id=tenant_id,
            scope=scope,
        )
        validate_staged_source_artifact(
            staged_path,
            staging_root=staging_root,
            registry=registry,
        )
        if base_revision_id and not catalog_db.is_file():
            raise SourceDataPromotionError(
                "Explicit base revision requires an existing Catalog database."
            )
        if not base_revision_id:
            preflight_staged_source_data_to_draft(
                staged_path,
                staging_root=staging_root,
                registry=registry,
                context=context,
            )
        validation_provider = (
            validation_key_provider_from_keyring(validation_keyring)
            if validation_keyring is not None
            else validation_key_provider_from_environment(required=False)
        )
        service = AdminCatalogService(
            CatalogStore(catalog_db, validation_key_provider=validation_provider)
        )
        base_entries = ()
        if base_revision_id:
            stored = service.store.get_revision_entries(context, base_revision_id)
            if stored is None:
                raise SourceDataPromotionError(
                    "Explicit base revision does not exist in the requested context."
                )
            base_entries = stored
            preflight_staged_source_data_to_draft(
                staged_path,
                staging_root=staging_root,
                registry=registry,
                context=context,
                base_entries=base_entries,
            )
        result = import_staged_source_data_to_draft(
            staged_path,
            staging_root=staging_root,
            registry=registry,
            service=service,
            context=context,
            draft_id=draft_id,
            actor_id=actor_id,
            reason=reason,
            base_revision_id=base_revision_id,
        )
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        CatalogServiceError,
        CatalogStoreError,
        ContractError,
        SourceDataPromotionError,
        SourceRegistryError,
        ValidationKeyCompositionError,
    ) as exc:
        typer.echo(f"[FEHLER] {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(
        f"[OK] Source-Draft erstellt: {result.draft.draft_id} "
        f"version={result.draft.version} receipt={result.receipt.receipt_sha256}"
    )
    typer.echo("[INFO] Kein Catalog-Publish und keine Activation ausgefuehrt.")


def _record_source_data_consistency(
    staged_path: Path,
    ledger_path: Path,
    registry_path: Path,
    dry_run: bool,
) -> None:
    registry = _load_registry(registry_path)
    try:
        result = promote_staged_source_data(
            staged_path,
            ledger_path,
            registry=registry,
            dry_run=dry_run,
        )
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        SourceDataPromotionError,
        SourceRegistryError,
    ) as exc:
        typer.echo(f"[FEHLER] {exc}", err=True)
        raise typer.Exit(1) from exc
    prefix = "[DRY-RUN]" if dry_run else "[OK]"
    typer.echo(
        f"{prefix} Source-Datenkonsistenz: {result['source_id']} "
        f"{result['data_type']} records={result['record_count']}"
    )


@source_app.command("data-record-consistency")
def record_source_data_consistency(
    staged_path: Path = typer.Argument(..., help="Validierter staged Datenbatch."),
    ledger_path: Path = typer.Option(
        ...,
        "--ledger",
        help="Lokales Consistency-Ledger; kein Catalog-Publish oder externer Tamper-Anker.",
    ),
    registry_path: Path = typer.Option(
        DEFAULT_SOURCE_REGISTRY_PATH,
        "--registry",
        help="Pfad zur aktuell zu revalidierenden Source-Registry JSON-Datei.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Consistency-Plan anzeigen und vorhandenes Ledger pruefen, ohne zu schreiben.",
    ),
) -> None:
    _record_source_data_consistency(
        staged_path,
        ledger_path,
        registry_path,
        dry_run,
    )


@source_app.command("data-promote", deprecated=True)
def promote_source_data(
    staged_path: Path = typer.Argument(..., help="Validierter staged Datenbatch."),
    ledger_path: Path = typer.Option(
        ...,
        "--ledger",
        help="Lokales Consistency-Ledger; kein Catalog-Publish oder externer Tamper-Anker.",
    ),
    registry_path: Path = typer.Option(
        DEFAULT_SOURCE_REGISTRY_PATH,
        "--registry",
        help="Pfad zur aktuell zu revalidierenden Source-Registry JSON-Datei.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Consistency-Plan anzeigen und vorhandenes Ledger pruefen, ohne zu schreiben.",
    ),
) -> None:
    typer.echo(
        "[DEPRECATED] 'data-promote' wird durch 'data-record-consistency' ersetzt; "
        "dieser Pfad schreibt nur lokale Konsistenz, kein Catalog-Publish."
    )
    _record_source_data_consistency(
        staged_path,
        ledger_path,
        registry_path,
        dry_run,
    )
