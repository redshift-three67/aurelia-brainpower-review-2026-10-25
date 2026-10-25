"""AnalysisDraft — Aurelia D18-Vertrag (docs/18-clipboard.md).

"Module tauschen Artefakte, nicht Seiteneffekte." Der Weg des Originals
"BROADCAST MIX" (Analyseergebnis -> direkt in die Broadcast-Queue) wird hier
auf den Aurelia-Vertrag umgestellt: Die Analyse erzeugt einen Draft;
die Harmonisierungs-/Broadcast-Seite hat als einzigen Eingang den Promote
aus einem Draft.

Status: draft -> client_review -> ready -> promoted | discarded
CopyGuard bei jedem sichtbaren Speichern und vor Promote.
TTL-Default (U10): 7 Tage, dann Archiv-Vorschlag, kein Auto-Delete.
"""

from __future__ import annotations

import copy
import json
import threading
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .. import copyguard
from ..persistence import atomic_json_replace, document_digest
from ..scope import ScopeContext
from .broadcast import validate_broadcast_input
from .emitter import DEFAULT_DELAY_MS, DEFAULT_REPEAT

TTL_DAYS = 7  # U10

VALID_TRANSITIONS: dict[str, set[str]] = {
    "draft": {"client_review", "ready", "discarded"},
    "client_review": {"ready", "discarded"},
    "ready": {"promoted", "discarded"},
    "promoted": set(),
    "discarded": set(),
}

# C12: Klient-Rolle sieht nur diese Felder
CLIENT_EDITABLE_FIELDS = ["practitioner_note"]


class DraftError(ValueError):
    pass


class DraftStore:
    def __init__(self, drafts_dir: Path, *, scope: ScopeContext | None = None) -> None:
        self.drafts_dir = Path(drafts_dir)
        self.scope = scope
        self._promotion_lock = threading.RLock()
        self._promotion_by_broadcast: dict[str, str] = {}
        self.drafts_dir.mkdir(parents=True, exist_ok=True)

    def _stamp_scope(self, draft: dict[str, Any]) -> None:
        if self.scope is None:
            return
        expected = self.scope.to_dict()
        stored = draft.get("scope")
        if stored is not None and stored != expected:
            raise DraftError("Draft liegt ausserhalb des aktiven Scope")
        draft["scope"] = expected
        draft.update(expected)

    def _has_scope(self, draft: dict[str, Any]) -> bool:
        return self.scope is None or draft.get("scope") == self.scope.to_dict()

    # -- Erzeugung -----------------------------------------------------------

    def create_from_analysis(
        self,
        *,
        analysis_dict: dict[str, Any],
        passport: dict[str, Any],
        database: str,
        tenant_id: str | None = None,
        client_id: str | None = None,
        practitioner_id: str | None = None,
        focus: dict[str, Any] | None = None,
        copyguard_digest: str | None = None,
        persist: bool = True,
    ) -> dict[str, Any]:
        visible_texts = copyguard.visible_rate_texts(analysis_dict)
        verdict, findings = copyguard.check_strings(visible_texts)
        digest = copyguard_digest or copyguard.digest(visible_texts)
        now = datetime.now(timezone.utc)
        draft = {
            "id": str(uuid.uuid4()),
            "tenant_id": tenant_id,
            "client_id": client_id,
            "practitioner_id": practitioner_id,
            "source_kernel": passport.get("kernel"),
            "source_kernel_version": passport.get("kernel_version"),
            "source_run_id": passport.get("run_id"),
            "sessionId": None,
            "sessionRevision": 0,
            "database": database,
            "focus": focus or {},  # Vektor-Bindung: Fall + Absicht der letzten Session
            "payload": analysis_dict,
            "copyguard_digest": digest,
            "copyguard_verdict": verdict,
            "copyguard_findings": findings,
            "client_editable_fields": CLIENT_EDITABLE_FIELDS,
            "practitioner_note": "",
            "status": "draft",
            "created": now.isoformat(timespec="seconds"),
            "updated": now.isoformat(timespec="seconds"),
            "ttl_hint": (now + timedelta(days=TTL_DAYS)).isoformat(timespec="seconds"),
        }
        self._stamp_scope(draft)
        if persist:
            self._write(draft)
        return draft

    @staticmethod
    def target_key(draft: dict[str, Any]) -> str:
        draft_id = draft.get("id")
        if not isinstance(draft_id, str) or not draft_id:
            raise DraftError("Draft hat keine gueltige ID")
        return f"{draft_id}.json"

    def plan_link_session_document(
        self,
        draft: dict[str, Any],
        session_id: str,
        revision: int,
    ) -> dict[str, Any]:
        planned = copy.deepcopy(draft)
        planned["sessionId"] = session_id
        planned["sessionRevision"] = revision
        planned["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        return planned

    def plan_project_session(
        self,
        draft_id: str,
        analysis_dict: dict[str, Any],
        session_id: str,
        revision: int,
    ) -> dict[str, Any]:
        """Baut einen Draft-Endzustand ohne ihn vor der Case-Revision zu schreiben."""
        draft = self.get(draft_id)
        if draft is None:
            raise DraftError(f"Draft {draft_id} existiert nicht")
        if draft["status"] in {"draft", "client_review"}:
            planned = self.plan_link_session_document(draft, session_id, revision)
            planned["payload"] = copy.deepcopy(analysis_dict)
            visible_texts = copyguard.visible_rate_texts(analysis_dict)
            planned["copyguard_digest"] = copyguard.digest(visible_texts)
            planned["copyguard_verdict"], planned["copyguard_findings"] = copyguard.check_strings(visible_texts)
            return planned
        successor = self.create_from_analysis(
            analysis_dict=analysis_dict,
            passport={
                "kernel": draft.get("source_kernel"),
                "kernel_version": draft.get("source_kernel_version"),
                "run_id": draft.get("source_run_id"),
            },
            database=draft["database"],
            tenant_id=draft.get("tenant_id"),
            client_id=draft.get("client_id"),
            practitioner_id=draft.get("practitioner_id"),
            focus=draft.get("focus"),
            persist=False,
        )
        successor["parentDraftId"] = draft_id
        return self.plan_link_session_document(successor, session_id, revision)

    def plan_successor_for_session(
        self,
        draft_id: str,
        analysis_dict: dict[str, Any],
        session_id: str,
        revision: int,
    ) -> dict[str, Any]:
        draft = self.get(draft_id)
        if draft is None:
            raise DraftError(f"Draft {draft_id} existiert nicht")
        successor = self.create_from_analysis(
            analysis_dict=analysis_dict,
            passport={
                "kernel": draft.get("source_kernel"),
                "kernel_version": draft.get("source_kernel_version"),
                "run_id": draft.get("source_run_id"),
            },
            database=draft["database"],
            tenant_id=draft.get("tenant_id"),
            client_id=draft.get("client_id"),
            practitioner_id=draft.get("practitioner_id"),
            focus=draft.get("focus"),
            persist=False,
        )
        successor["parentDraftId"] = draft_id
        return self.plan_link_session_document(successor, session_id, revision)

    def write_planned(self, draft: dict[str, Any]) -> None:
        self._write(draft)

    def link_session(self, draft_id: str, session_id: str, revision: int) -> dict[str, Any]:
        draft = self.get(draft_id)
        if draft is None:
            raise DraftError(f"Draft {draft_id} existiert nicht")
        planned = self.plan_link_session_document(draft, session_id, revision)
        self._write(planned)
        return planned

    def project_session(
        self,
        draft_id: str,
        analysis_dict: dict[str, Any],
        session_id: str,
        revision: int,
    ) -> dict[str, Any]:
        """Aktualisiert nur mutable Drafts, sonst erzeugt einen sauberen Nachfolger."""
        planned = self.plan_project_session(
            draft_id,
            analysis_dict,
            session_id,
            revision,
        )
        self._write(planned)
        return planned

    def successor_for_session(
        self,
        draft_id: str,
        analysis_dict: dict[str, Any],
        session_id: str,
        revision: int,
    ) -> dict[str, Any]:
        """Erzeugt bei einem Session-Fork stets einen neuen, unreviewten Draft."""
        planned = self.plan_successor_for_session(
            draft_id,
            analysis_dict,
            session_id,
            revision,
        )
        self._write(planned)
        return planned

    # -- Lesen ----------------------------------------------------------------

    def _draft_path(self, draft_id: str) -> Path | None:
        try:
            parsed = uuid.UUID(draft_id)
        except (AttributeError, ValueError):
            return None
        if str(parsed) != draft_id:
            return None
        root = self.drafts_dir.resolve()
        path = (root / f"{draft_id}.json").resolve()
        try:
            path.relative_to(root)
        except ValueError:
            return None
        return path

    def get(self, draft_id: str) -> dict[str, Any] | None:
        path = self._draft_path(draft_id)
        if path is None or not path.exists():
            return None
        draft = json.loads(path.read_text(encoding="utf-8"))
        return draft if self._has_scope(draft) else None

    def list(self, status: str | None = None) -> list[dict[str, Any]]:
        drafts = [
            draft
            for path in sorted(self.drafts_dir.glob("*.json"))
            if (draft := json.loads(path.read_text(encoding="utf-8"))) and self._has_scope(draft)
        ]
        if status:
            drafts = [d for d in drafts if d.get("status") == status]
        return drafts

    # -- Statusmaschine ----------------------------------------------------------

    def transition(self, draft_id: str, new_status: str, *, force: bool = False) -> dict[str, Any]:
        draft = self.get(draft_id)
        if draft is None:
            raise DraftError(f"Draft {draft_id} existiert nicht")
        current = draft["status"]
        if new_status not in VALID_TRANSITIONS.get(current, set()):
            raise DraftError(f"Uebergang {current} -> {new_status} nicht erlaubt")
        if new_status == "promoted" and not force:
            # CopyGuard vor Promote (D18-Pflicht)
            verdict, _ = copyguard.check_strings(self._visible_texts(draft))
            if verdict == "block":
                raise DraftError("CopyGuard blockt Promote (fail-closed)")
        draft["status"] = new_status
        draft["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self._write(draft)
        return draft

    # -- Promote -> Harmonisierung/Broadcast (einziger Eingang, D18) -------------

    def prepare_promotion(
        self,
        draft_id: str,
        *,
        max_rates: int = 8,
        seconds_per_rate: int = 60,
        multiplier: int = 1,
    ) -> list[dict[str, Any]]:
        """Aequivalent zum Original 'BROADCAST MIX' — aber nur via Promote.

        Original (Event-Handler.broadcastMix, Zeile 439-441): nur Raten mit
        gv > caseGV, Sortierung gv desc dann energetischer Wert, und
        SEKUNDEN = rate.gv - caseGV (GV-Differenz als Laufzeit!). Hohe
        Raten senden dadurch MINUTEN statt Sekunden — genau das, was den
        live aufbauenden Resonanzaufbau erzeugt. Prototyp-Fuss: mindestens
        60 s je Entry (Usability; das Original wuerde bei kleiner Differenz
        sofort beenden).
        """
        draft = self.get(draft_id)
        if draft is None:
            raise DraftError(f"Draft {draft_id} existiert nicht")
        if draft["status"] != "ready":
            raise DraftError("Promote verlangt einen bereiten Draft")
        verdict, _ = copyguard.check_strings(self._visible_texts(draft))
        if verdict == "block":
            raise DraftError("CopyGuard blockt Promote (fail-closed)")
        rates = draft["payload"].get("rateObjects", [])
        case_gv = draft["payload"].get("generalVitality") or 0
        above = [r for r in rates if (r.get("gv") or 0) > case_gv]
        if not above and rates:
            above = rates
        above.sort(key=lambda r: (-(r.get("gv") or 0), -(r.get("energeticValue") or 0)))
        entries = []
        for r in above[:max_rates]:
            gv = r.get("gv") or 0
            seconds = max((gv - case_gv) if gv > case_gv else 0, seconds_per_rate)
            entries.append(
                {
                    "signature": f"{r['nameOrRate']} {r['energeticValue']} {r.get('potency') or ''}".strip(),
                    "seconds": seconds,
                    "multiplier": multiplier,
                }
            )
        if not entries:
            raise DraftError("Promote braucht mindestens eine Rate")
        for entry in entries:
            validate_broadcast_input(
                entry["signature"], entry["seconds"], entry["multiplier"],
                DEFAULT_DELAY_MS, DEFAULT_REPEAT,
            )
        return entries

    def begin_promotion(self, draft_id: str, **options: int) -> tuple[str, list[dict[str, Any]]]:
        with self._promotion_lock:
            entries = self.prepare_promotion(draft_id, **options)
            draft = self.get(draft_id)
            assert draft is not None
            previous = draft.get("promotion") or {}
            if previous.get("state") not in (None, "failed"):
                raise DraftError("Vorheriger Promote-Versuch braucht manuelle Klärung")
            if previous:
                draft.setdefault("promotion_history", []).append(copy.deepcopy(previous))
            promotion_id = uuid.uuid4().hex
            draft["promotion"] = {
                "id": promotion_id,
                "state": "pending",
                "entries_sha256": document_digest({"entries": entries}),
                "broadcast_ids": [],
            }
            self._write(draft)
            return promotion_id, entries

    def finish_promotion(self, draft_id: str, promotion_id: str, broadcast_ids: list[str]) -> None:
        with self._promotion_lock:
            draft = self.get(draft_id)
            if draft is None or draft.get("promotion", {}).get("id") != promotion_id:
                raise DraftError("Promote-Versuch nicht gefunden")
            if draft["status"] != "ready" or draft["promotion"]["state"] != "pending":
                raise DraftError("Promote-Versuch ist nicht mehr offen")
            draft["status"] = "promoted"
            draft["promotion"]["state"] = "submitted"
            draft["promotion"]["broadcast_ids"] = broadcast_ids
            draft["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            self._write(draft)
            for broadcast_id in broadcast_ids:
                self._promotion_by_broadcast[broadcast_id] = draft_id

    def fail_promotion(self, draft_id: str, promotion_id: str) -> None:
        with self._promotion_lock:
            draft = self.get(draft_id)
            if draft is None or draft.get("promotion", {}).get("id") != promotion_id:
                raise DraftError("Promote-Versuch nicht gefunden")
            if draft["status"] != "ready" or draft["promotion"]["state"] != "pending":
                raise DraftError("Promote-Versuch braucht manuelle Klärung")
            draft["promotion"]["state"] = "failed"
            draft["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            self._write(draft)

    def record_broadcast_terminal(self, payload: dict[str, Any]) -> None:
        broadcast_id = payload.get("broadcastId")
        if not isinstance(broadcast_id, str):
            return
        terminal = (
            "finished" if payload.get("finished")
            else "failed" if payload.get("failed")
            else "stopped" if payload.get("stopped")
            else None
        )
        if terminal is None:
            return
        with self._promotion_lock:
            draft_id = self._promotion_by_broadcast.get(broadcast_id)
            if draft_id is None:
                return
            draft = self.get(draft_id)
            if draft is None:
                return
            promotion = draft.get("promotion") or {}
            if promotion.get("state") != "submitted":
                return
            ids = promotion.get("broadcast_ids") or []
            observed = promotion.setdefault("terminal", {})
            if broadcast_id in observed:
                return
            observed[broadcast_id] = terminal
            if terminal != "finished":
                promotion["state"] = "interrupted"
            elif all(observed.get(item) == "finished" for item in ids):
                promotion["state"] = "completed"
            self._write(draft)
            if promotion["state"] != "submitted":
                for item in ids:
                    self._promotion_by_broadcast.pop(item, None)

    def reconcile_promotions(self) -> None:
        """Nie eine flüchtige Queue aus alten Drafts automatisch neu starten."""
        with self._promotion_lock:
            for draft in self.list():
                promotion = draft.get("promotion") or {}
                if promotion.get("state") in {"pending", "submitted"}:
                    promotion["state"] = "interrupted"
                    draft["promotion"] = promotion
                    self._write(draft)

    def promote_to_broadcast_queue(
        self,
        draft_id: str,
        *,
        max_rates: int = 8,
        seconds_per_rate: int = 60,
        multiplier: int = 1,
    ) -> list[dict[str, Any]]:
        """Kompatibilitätshelfer für bestehende Kern-Tests; REST nutzt den Versuchsdienst."""
        entries = self.prepare_promotion(
            draft_id,
            max_rates=max_rates,
            seconds_per_rate=seconds_per_rate,
            multiplier=multiplier,
        )
        self.transition(draft_id, "promoted")
        return entries

    # -- Internes ---------------------------------------------------------------

    @staticmethod
    def _visible_texts(draft: dict[str, Any]) -> list[str]:
        texts = [r.get("nameOrRate", "") or "" for r in draft["payload"].get("rateObjects", [])]
        if draft.get("practitioner_note"):
            texts.append(draft["practitioner_note"])
        return texts

    def _write(self, draft: dict[str, Any]) -> None:
        self._stamp_scope(draft)
        path = self._draft_path(draft.get("id"))
        if path is None:
            raise DraftError("Draft hat keine gueltige ID")
        atomic_json_replace(path, draft)
