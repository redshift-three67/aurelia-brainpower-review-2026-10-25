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

import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .. import copyguard

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
    def __init__(self, drafts_dir: Path) -> None:
        self.drafts_dir = Path(drafts_dir)
        self.drafts_dir.mkdir(parents=True, exist_ok=True)

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
    ) -> dict[str, Any]:
        visible_texts = [
            r.get("nameOrRate", "") or ""
            for r in analysis_dict.get("rateObjects", [])
        ]
        verdict, findings = copyguard.check_strings(visible_texts)
        digest = copyguard.digest(visible_texts)
        now = datetime.now(timezone.utc)
        draft = {
            "id": str(uuid.uuid4()),
            "tenant_id": tenant_id,
            "client_id": client_id,
            "practitioner_id": practitioner_id,
            "source_kernel": passport.get("kernel"),
            "source_kernel_version": passport.get("kernel_version"),
            "source_run_id": passport.get("run_id"),
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
        self._write(draft)
        return draft

    # -- Lesen ----------------------------------------------------------------

    def get(self, draft_id: str) -> dict[str, Any] | None:
        path = self.drafts_dir / f"{draft_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def list(self, status: str | None = None) -> list[dict[str, Any]]:
        drafts = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(self.drafts_dir.glob("*.json"))
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

    def promote_to_broadcast_queue(
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
        draft = self.transition(draft_id, "promoted", force=False)
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
        return entries

    # -- Internes ---------------------------------------------------------------

    @staticmethod
    def _visible_texts(draft: dict[str, Any]) -> list[str]:
        texts = [r.get("nameOrRate", "") or "" for r in draft["payload"].get("rateObjects", [])]
        if draft.get("practitioner_note"):
            texts.append(draft["practitioner_note"])
        return texts

    def _write(self, draft: dict[str, Any]) -> None:
        path = self.drafts_dir / f"{draft['id']}.json"
        path.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")
