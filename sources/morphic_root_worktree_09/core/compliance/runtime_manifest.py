from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from apps.web.durable_io import durable_mkdir_parents

if TYPE_CHECKING:
    from core.compliance.group_activation_handle_store import GroupActivationHandleStore
    from core.compliance.local_client_identity_store import LocalClientIdentityStore
    from core.compliance.operator_context import OperatorContext


DEFAULT_ERASURE_GATE_TOKEN = "MORPHIC_ERASURE_ACKNOWLEDGED"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUNTIME_DIR = PROJECT_ROOT / "data" / "runtime"

STORE_DEFAULTS: dict[str, dict[str, Any]] = {
    "clients": {"schema_version": 1, "clients": []},
    "sessions": {"schema_version": 1, "sessions": []},
    "artifacts": {"schema_version": 1, "artifacts": []},
    "audit_log": {"schema_version": 1, "entries": []},
}


def runtime_root() -> Path:
    override = os.getenv("MORPHIC_RUNTIME_DIR", "").strip()
    return Path(override) if override else DEFAULT_RUNTIME_DIR


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clean(value: object) -> str:
    return str(value or "").strip()


def _stable_client_key(client: dict[str, Any]) -> str:
    parts = (
        _clean(client.get("first_name")).casefold(),
        _clean(client.get("last_name") or client.get("name")).casefold(),
        _clean(client.get("birth_date")),
        _clean(client.get("birth_place")).casefold(),
    )
    return "|".join(parts)


def stable_client_id(client: dict[str, Any]) -> str:
    digest = hashlib.sha256(_stable_client_key(client).encode("utf-8")).hexdigest()[:20]
    return f"cli-{digest}"


class RuntimeManifestService:
    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root is not None else runtime_root()

    def path_for(self, store_name: str) -> Path:
        if store_name not in STORE_DEFAULTS:
            raise KeyError(f"Unknown runtime store: {store_name}")
        return self.root / f"{store_name}.json"

    def load_store(self, store_name: str) -> dict[str, Any]:
        path = self.path_for(store_name)
        if not path.exists():
            return json.loads(json.dumps(STORE_DEFAULTS[store_name]))
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        default = json.loads(json.dumps(STORE_DEFAULTS[store_name]))
        default.update(payload if isinstance(payload, dict) else {})
        return default

    def save_store(self, store_name: str, payload: dict[str, Any]) -> None:
        path = self.path_for(store_name)
        durable_mkdir_parents(path.parent, mode=0o700)
        tmp = path.with_suffix(path.suffix + f".tmp.{uuid4().hex[:8]}")
        tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(path)

    def append_audit(
        self,
        *,
        action: str,
        client_id: str,
        entity_type: str,
        entity_id: str,
        outcome: str = "ok",
        detail: dict[str, Any] | None = None,
        actor: str = "system",
    ) -> dict[str, Any]:
        store = self.load_store("audit_log")
        entry = {
            "event_id": f"aud-{uuid4().hex[:12]}",
            "created_at": _now(),
            "actor": actor or "system",
            "action": action,
            "client_id": client_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "outcome": outcome,
            "detail": detail or {},
        }
        store["entries"].append(entry)
        self.save_store("audit_log", store)
        return entry

    def get_or_create_client(
        self,
        client: dict[str, Any],
        *,
        context: "OperatorContext | None" = None,
    ) -> dict[str, Any]:
        store = self.load_store("clients")
        client_id = stable_client_id(client)
        for entry in store["clients"]:
            if entry.get("client_id") == client_id:
                return entry

        stamp = _now()
        entry = {
            "client_id": client_id,
            "first_name": _clean(client.get("first_name")),
            "last_name": _clean(client.get("last_name") or client.get("name")),
            "birth_date": _clean(client.get("birth_date")),
            "birth_place": _clean(client.get("birth_place")),
            "created_at": stamp,
            "updated_at": stamp,
        }
        if context is not None:
            entry.update(
                {
                    "owner_id": context.workspace_id,
                    "workspace_id": context.workspace_id,
                    "tenant_id": context.tenant_id,
                }
            )
        store["clients"].append(entry)
        self.save_store("clients", store)
        self.append_audit(
            action="client_register",
            client_id=client_id,
            entity_type="client",
            entity_id=client_id,
        )
        return entry

    def get_client(self, client_id: str) -> dict[str, Any]:
        """Return an internal client-record copy or fail closed when unknown."""

        lookup = _clean(client_id)
        for entry in self.load_store("clients")["clients"]:
            if entry.get("client_id") == lookup:
                return json.loads(json.dumps(entry))
        raise LookupError("client not found")

    def record_group_analysis_consent(
        self,
        client_id: str,
        *,
        context: "OperatorContext",
        enabled: bool,
        consent_version: str,
        valid_until: datetime,
    ) -> dict[str, Any]:
        """Record versioned consent only for an already owner-/tenant-bound client."""

        lookup = _clean(client_id)
        version = _clean(consent_version)
        if not version:
            raise ValueError("consent_version is required")
        if valid_until.tzinfo is None or valid_until.utcoffset() is None:
            raise ValueError("valid_until must be timezone-aware")
        expiry = valid_until.astimezone(UTC).replace(microsecond=0)
        if enabled and expiry <= datetime.now(UTC):
            raise ValueError("enabled consent valid_until must be in the future")
        expiry_text = expiry.isoformat().replace("+00:00", "Z")
        store = self.load_store("clients")
        entry = next(
            (item for item in store["clients"] if item.get("client_id") == lookup),
            None,
        )
        if entry is None:
            raise LookupError("client not found")
        required_binding = ("owner_id", "workspace_id", "tenant_id")
        if any(not _clean(entry.get(field)) for field in required_binding):
            raise ValueError("legacy client is not owner-/tenant-bound")
        if entry.get("owner_id") not in (context.operator_id, context.workspace_id):
            raise PermissionError("client belongs to another owner")
        if entry.get("workspace_id") != context.workspace_id:
            raise PermissionError("client belongs to another workspace")
        if entry.get("tenant_id") != context.tenant_id:
            raise PermissionError("client belongs to another tenant")

        stamp = _now()
        entry["group_analysis"] = {
            "enabled": bool(enabled),
            "consent_version": version,
            "valid_until": expiry_text,
            "updated_at": stamp,
        }
        entry["updated_at"] = stamp
        self.save_store("clients", store)
        self.append_audit(
            action="group_analysis_consent",
            client_id=lookup,
            entity_type="client",
            entity_id=lookup,
            detail={"enabled": bool(enabled), "consent_version": version},
            actor=context.operator_id,
        )
        return {
            "client_id": lookup,
            "enabled": bool(enabled),
            "consent_version": version,
        }

    def list_clients_safe(self) -> list[dict[str, Any]]:
        store = self.load_store("clients")
        return [
            {
                "client_id": entry.get("client_id", ""),
                "created_at": entry.get("created_at", ""),
                "updated_at": entry.get("updated_at", ""),
            }
            for entry in store["clients"]
        ]

    def create_session(
        self,
        client: dict[str, Any],
        *,
        session_id: str = "",
        focus: str = "",
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        client_entry = self.get_or_create_client(client)
        client_id = client_entry["client_id"]
        resolved_session_id = session_id.strip() if session_id else f"sess-{uuid4().hex[:12]}"
        store = self.load_store("sessions")
        for entry in store["sessions"]:
            if entry.get("session_id") == resolved_session_id:
                return entry

        entry = {
            "session_id": resolved_session_id,
            "client_id": client_id,
            "created_at": _now(),
            "focus": focus,
            "config": config or {},
            "artifact_ids": [],
        }
        store["sessions"].append(entry)
        self.save_store("sessions", store)
        self.append_audit(
            action="session_register",
            client_id=client_id,
            entity_type="session",
            entity_id=resolved_session_id,
        )
        return entry

    def register_artifact(
        self,
        client: dict[str, Any],
        *,
        artifact_type: str,
        path: str | Path,
        label: str = "",
        session_id: str = "",
        focus: str = "",
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        session = self.create_session(client, session_id=session_id, focus=focus, config=config)
        artifact_id = f"art-{uuid4().hex[:12]}"
        artifact = {
            "artifact_id": artifact_id,
            "session_id": session["session_id"],
            "client_id": session["client_id"],
            "artifact_type": artifact_type,
            "path": str(Path(path)),
            "label": label,
            "created_at": _now(),
        }

        artifact_store = self.load_store("artifacts")
        artifact_store["artifacts"].append(artifact)
        self.save_store("artifacts", artifact_store)

        session_store = self.load_store("sessions")
        for entry in session_store["sessions"]:
            if entry.get("session_id") == session["session_id"]:
                entry.setdefault("artifact_ids", []).append(artifact_id)
                break
        self.save_store("sessions", session_store)

        self.append_audit(
            action="artifact_register",
            client_id=session["client_id"],
            entity_type="artifact",
            entity_id=artifact_id,
            detail={"path": artifact["path"], "artifact_type": artifact_type, "label": label},
        )
        return artifact

    def _client_exists(self, client_id: str) -> bool:
        return any(entry.get("client_id") == client_id for entry in self.load_store("clients")["clients"])

    def _collect_for_client(self, client_id: str) -> dict[str, Any]:
        sessions = [
            entry
            for entry in self.load_store("sessions")["sessions"]
            if entry.get("client_id") == client_id
        ]
        session_ids = {entry.get("session_id") for entry in sessions}
        artifacts = [
            entry
            for entry in self.load_store("artifacts")["artifacts"]
            if entry.get("client_id") == client_id or entry.get("session_id") in session_ids
        ]
        return {"sessions": sessions, "artifacts": artifacts}

    def _workbench_runtime_dry_run(
        self, client_id: str, workbench_root: str | Path | None
    ) -> list[dict[str, Any]]:
        if workbench_root is None:
            return []
        client = next(
            (entry for entry in self.load_store("clients")["clients"] if entry.get("client_id") == client_id),
            {},
        )
        identity = {
            field: _clean(client.get(field))
            for field in ("first_name", "last_name", "birth_date", "birth_place")
        }
        identity["client_id"] = client_id

        def matched_fields(value: Any) -> set[str]:
            matches: set[str] = set()
            if isinstance(value, dict):
                for key, nested in value.items():
                    if key in identity and identity[key] and _clean(nested) == identity[key]:
                        matches.add(key)
                    matches.update(matched_fields(nested))
            elif isinstance(value, list):
                for nested in value:
                    matches.update(matched_fields(nested))
            return matches

        findings: list[dict[str, Any]] = []
        for store in ("draft", "templates", "run_traces"):
            path = Path(workbench_root) / f"{store}.json"
            finding: dict[str, Any] = {"store": store, "path": str(path)}
            if not path.exists():
                finding["state"] = "missing"
            else:
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    finding["state"] = "invalid_json"
                else:
                    matches = sorted(matched_fields(payload))
                    finding["matched_identity_fields"] = matches
                    finding["state"] = "identity_match" if matches else "no_identity_match"
            findings.append(finding)
        return findings

    def _web_job_log_dry_run(
        self,
        client_id: str,
        workbench_root: str | Path | None,
        web_job_root: str | Path | None,
    ) -> list[dict[str, Any]]:
        if web_job_root is None:
            return []
        attributable_run_ids: set[str] = set()
        if workbench_root is not None:
            trace_path = Path(workbench_root) / "run_traces.json"
            try:
                traces = json.loads(trace_path.read_text(encoding="utf-8")).get("run_traces", [])
            except (OSError, json.JSONDecodeError, AttributeError):
                traces = []
            for trace in traces:
                review = trace.get("review", {}) if isinstance(trace, dict) else {}
                if isinstance(review, dict) and review.get("client_id") == client_id:
                    run_id = str(trace.get("run_id", "")).strip()
                    if run_id:
                        attributable_run_ids.add(run_id)

        root = Path(web_job_root)
        findings: list[dict[str, Any]] = []
        for path in sorted(root.glob("*.log")) if root.is_dir() else []:
            job_id = path.name.removesuffix(".stdout.log").removesuffix(".stderr.log")
            findings.append(
                {
                    "path": str(path),
                    "job_id": job_id,
                    "attribution": (
                        "attributable_via_run_trace"
                        if job_id in attributable_run_ids
                        else "unattributable_global"
                    ),
                }
            )
        return findings

    def _harmonization_dry_run(
        self, harmonization_root: str | Path | None
    ) -> list[dict[str, Any]]:
        if harmonization_root is None:
            return []
        root = Path(harmonization_root)
        paths = list(root.glob("*.json")) if root.is_dir() else []
        events = root / "events"
        if events.is_dir():
            paths.extend(events.glob("*.jsonl"))
        return [
            {"path": str(path), "attribution": "unattributable_global"}
            for path in sorted(paths)
        ]

    def erasure_manifest(
        self,
        client_id: str,
        *,
        workbench_root: str | Path | None = None,
        web_job_root: str | Path | None = None,
        harmonization_root: str | Path | None = None,
        identity_store: "LocalClientIdentityStore | None" = None,
        context: "OperatorContext | None" = None,
    ) -> dict[str, Any]:
        lookup = _clean(client_id)
        collected = self._collect_for_client(lookup)

        def path_state(raw_path: Any) -> str:
            if not raw_path:
                return "unregistered"
            target = Path(str(raw_path))
            if not target.exists():
                return "missing"
            if target.is_file():
                return "exists_file"
            if target.is_dir():
                return "exists_directory"
            return "exists_other"

        manifest = {
            "client_id": lookup,
            "client_entry_present": self._client_exists(lookup),
            "sessions": [entry.get("session_id") for entry in collected["sessions"]],
            "artifacts": [
                {
                    "id": entry.get("artifact_id"),
                    "path": entry.get("path"),
                    "artifact_type": entry.get("artifact_type"),
                    "path_state": path_state(entry.get("path")),
                }
                for entry in collected["artifacts"]
            ],
            "dry_run": True,
            "covered_storage_classes": [
                "runtime_manifest_clients",
                "runtime_manifest_sessions",
                "runtime_manifest_artifacts",
                "registered_artifact_paths",
            ],
            "uncovered_storage_classes": [
                "web_job_logs",
                "workbench_drafts_templates_traces",
                "harmonization_job_events",
                "browser_local_storage",
                "unregistered_export_artifacts",
                "backups",
            ],
            "harmonization_artifacts": self._harmonization_dry_run(
                harmonization_root
            ),
            "web_job_logs": self._web_job_log_dry_run(
                lookup, workbench_root, web_job_root
            ),
            "workbench_runtime": self._workbench_runtime_dry_run(
                lookup, workbench_root
            ),
            "gated": True,
            "gate_token_required": True,
        }
        if identity_store is not None:
            if context is None:
                raise ValueError("context is required for hardened identity erasure")
            manifest["hardened_identity"] = identity_store.erasure_dry_run(
                lookup,
                context=context,
            )
        self.append_audit(
            action="erasure_manifest",
            client_id=lookup,
            entity_type="client",
            entity_id=lookup,
            outcome="ok" if manifest["client_entry_present"] else "not_found",
            detail={
                "sessions": len(manifest["sessions"]),
                "artifacts": len(manifest["artifacts"]),
            },
        )
        return manifest

    def execute_erasure(
        self,
        client_id: str,
        *,
        gate_token: str,
        actor: str = "system",
        identity_store: "LocalClientIdentityStore | None" = None,
        activation_handle_store: "GroupActivationHandleStore | None" = None,
        context: "OperatorContext | None" = None,
    ) -> dict[str, Any]:
        expected = os.getenv("MORPHIC_ERASURE_GATE_TOKEN", "").strip() or DEFAULT_ERASURE_GATE_TOKEN
        lookup = _clean(client_id)
        if gate_token != expected:
            self.append_audit(
                action="erasure_execute",
                client_id=lookup,
                entity_type="client",
                entity_id=lookup,
                outcome="gated",
                detail={"reason": "invalid gate token"},
                actor=actor,
            )
            raise ValueError("Gate token required for erasure execution.")

        if identity_store is not None:
            if context is None:
                raise ValueError("context is required for hardened identity erasure")
            identity_store.erasure_dry_run(lookup, context=context)
            if activation_handle_store is None:
                from core.compliance.group_activation_handle_store import (
                    GroupActivationHandleStore,
                )

                activation_handle_store = GroupActivationHandleStore(
                    self.root / "group-activation-handles"
                )
            activation_handle_store.invalidate_context(context)
        result = self._erase_client_records(lookup, action="erasure_execute", actor=actor)
        if identity_store is not None:
            result["removed_hardened_identity"] = identity_store.erase(
                lookup,
                context=context,
                confirmation_id=lookup,
            )
            if result["removed_hardened_identity"] and result["outcome"] == "not_found":
                result["outcome"] = "ok"
        return result

    def _erase_client_records(self, lookup: str, *, action: str, actor: str = "system") -> dict[str, Any]:
        collected = self._collect_for_client(lookup)
        client_store = self.load_store("clients")
        session_store = self.load_store("sessions")
        artifact_store = self.load_store("artifacts")

        before_clients = len(client_store["clients"])
        before_sessions = len(session_store["sessions"])
        before_artifacts = len(artifact_store["artifacts"])

        client_store["clients"] = [
            entry for entry in client_store["clients"] if entry.get("client_id") != lookup
        ]
        session_store["sessions"] = [
            entry for entry in session_store["sessions"] if entry.get("client_id") != lookup
        ]
        artifact_ids = {entry.get("artifact_id") for entry in collected["artifacts"]}
        artifact_store["artifacts"] = [
            entry for entry in artifact_store["artifacts"] if entry.get("artifact_id") not in artifact_ids
        ]

        removed_files = 0
        for artifact in collected["artifacts"]:
            raw_path = artifact.get("path")
            if not raw_path:
                continue
            try:
                target = Path(str(raw_path))
                if target.exists() and target.is_file():
                    target.unlink()
                    removed_files += 1
            except OSError:
                pass

        self.save_store("clients", client_store)
        self.save_store("sessions", session_store)
        self.save_store("artifacts", artifact_store)

        removed_clients = before_clients - len(client_store["clients"])
        removed_sessions = before_sessions - len(session_store["sessions"])
        removed_artifacts = before_artifacts - len(artifact_store["artifacts"])
        outcome = "ok" if removed_clients or removed_sessions or removed_artifacts or removed_files else "not_found"
        self.append_audit(
            action=action,
            client_id=lookup,
            entity_type="client",
            entity_id=lookup,
            outcome=outcome,
            detail={
                "removed_clients": removed_clients,
                "removed_sessions": removed_sessions,
                "removed_artifacts": removed_artifacts,
                "removed_files": removed_files,
            },
            actor=actor,
        )
        return {
            "client_id": lookup,
            "removed_clients": removed_clients,
            "removed_sessions": removed_sessions,
            "removed_artifacts": removed_artifacts,
            "removed_files": removed_files,
            "outcome": outcome,
        }

    def audit_for_client(self, client_id: str) -> list[dict[str, Any]]:
        lookup = _clean(client_id)
        return [
            entry
            for entry in self.load_store("audit_log")["entries"]
            if entry.get("client_id") == lookup
        ]

    def _parse_timestamp(self, raw: str | None) -> datetime | None:
        if not raw:
            return None
        try:
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except ValueError:
            return None

    def _last_activity_for_client(
        self,
        client_id: str,
        client_entry: dict[str, Any],
        sessions: list[dict[str, Any]],
    ) -> datetime | None:
        timestamps = [
            ts
            for ts in (
                self._parse_timestamp(client_entry.get("updated_at")),
                self._parse_timestamp(client_entry.get("created_at")),
            )
            if ts is not None
        ]
        for session in sessions:
            if session.get("client_id") == client_id:
                ts = self._parse_timestamp(session.get("created_at"))
                if ts is not None:
                    timestamps.append(ts)
        return max(timestamps) if timestamps else None

    def find_expired_clients(
        self, retention_days: int, *, now: datetime | None = None
    ) -> list[str]:
        """Findet Client-IDs, deren letzte bekannte Aktivitaet (juengste
        Session oder Client-Erstellung/-Aktualisierung) laenger als
        `retention_days` zurueckliegt.

        Rein lesend - loescht nichts. Siehe `purge_expired` fuer die
        eigentliche Loeschung.
        """
        reference = now or datetime.now(UTC)
        threshold = reference - timedelta(days=retention_days)
        clients = self.load_store("clients")["clients"]
        sessions = self.load_store("sessions")["sessions"]

        expired: list[str] = []
        for client in clients:
            client_id = client.get("client_id", "")
            last_activity = self._last_activity_for_client(client_id, client, sessions)
            if last_activity is not None and last_activity < threshold:
                expired.append(client_id)
        return expired

    def purge_expired(
        self,
        retention_days: int,
        *,
        dry_run: bool = False,
        actor: str = "system",
        identity_store: "LocalClientIdentityStore | None" = None,
        activation_handle_store: "GroupActivationHandleStore | None" = None,
        context: "OperatorContext | None" = None,
    ) -> list[str]:
        """Loescht alle Clients (inkl. Sessions/Artefakte/Dateien), deren
        letzte Aktivitaet aelter als `retention_days` ist.

        Nutzt denselben Loeschpfad wie `execute_erasure`, aber ohne
        Gate-Token (automatisierte Aufbewahrungsbegrenzung statt
        individueller DSAR-Loeschung) und mit eigener Audit-Action
        (`retention_purge`/`retention_purge_dry_run`).

        Bei `dry_run=True` wird nichts geloescht; es werden nur die
        Kandidaten-Client-IDs ermittelt und auditiert.
        """
        expired_ids = self.find_expired_clients(retention_days)
        if identity_store is not None:
            if context is None:
                raise ValueError("context is required for hardened identity retention")
            for client_id in expired_ids:
                identity_store.erasure_dry_run(client_id, context=context)

        if dry_run:
            self.append_audit(
                action="retention_purge_dry_run",
                client_id="*",
                entity_type="retention",
                entity_id=f"retention-{retention_days}d",
                detail={"candidate_client_ids": expired_ids, "retention_days": retention_days},
                actor=actor,
            )
            return expired_ids

        if identity_store is not None and expired_ids:
            if activation_handle_store is None:
                from core.compliance.group_activation_handle_store import (
                    GroupActivationHandleStore,
                )

                activation_handle_store = GroupActivationHandleStore(
                    self.root / "group-activation-handles"
                )
            activation_handle_store.invalidate_context(context)

        purged: list[str] = []
        for client_id in expired_ids:
            result = self._erase_client_records(client_id, action="retention_purge", actor=actor)
            if identity_store is not None:
                identity_store.erase(
                    client_id,
                    context=context,
                    confirmation_id=client_id,
                )
            if result["outcome"] == "ok":
                purged.append(client_id)

        self.append_audit(
            action="retention_purge",
            client_id="*",
            entity_type="retention",
            entity_id=f"retention-{retention_days}d",
            detail={"purged_client_ids": purged, "retention_days": retention_days},
            actor=actor,
        )
        return purged
