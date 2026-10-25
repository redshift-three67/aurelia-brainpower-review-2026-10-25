"""Case- und Session-Persistenz mit stabilen, append-only Analyse-Sessions."""

from __future__ import annotations

import copy
import hashlib
import hmac
import json
import secrets
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any

from ..persistence import atomic_json_replace
from ..scope import ScopeContext


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class CaseNameError(ValueError):
    """Ein Fallname darf nie eine Pfadkomponente steuern."""


class SessionError(ValueError):
    pass


class CaseStore:
    def __init__(self, cases_dir: Path, *, scope: ScopeContext | None = None) -> None:
        self.cases_dir = Path(cases_dir)
        self.scope = scope
        self.cases_dir.mkdir(parents=True, exist_ok=True)
        self.current: dict[str, Any] | None = None
        self._lock = RLock()
        self._reference_key = secrets.token_bytes(32)

    def _stamp_scope(self, case: dict[str, Any]) -> None:
        if self.scope is None:
            return
        expected = self.scope.to_dict()
        stored = case.get("scope")
        if stored is not None and stored != expected:
            raise CaseNameError("Fall liegt ausserhalb des aktiven Scope")
        case["scope"] = expected
        case.update(expected)

    def _has_scope(self, case: dict[str, Any]) -> bool:
        return self.scope is None or case.get("scope") == self.scope.to_dict()

    @staticmethod
    def default_name() -> str:
        return datetime.now().strftime("%Y.%m.%d-%H%M%S")

    @staticmethod
    def _file_name(case_name: str) -> str:
        if not isinstance(case_name, str):
            raise CaseNameError("Fallname muss Text sein")
        normalized = case_name.strip()
        if not normalized:
            raise CaseNameError("Fallname darf nicht leer sein")
        if any(char in normalized for char in ("/", "\\", "\x00", ":")):
            raise CaseNameError("Fallname darf keine Pfadzeichen enthalten")
        if normalized in (".", ".."):
            raise CaseNameError("Fallname darf kein Pfadsegment sein")
        return f"{normalized.replace(' ', '')}.json"

    def _case_path(self, case_name: str) -> Path:
        root = self.cases_dir.resolve()
        path = (root / self._file_name(case_name)).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise CaseNameError("Fallname liegt ausserhalb des Fallverzeichnisses") from exc
        return path

    def list_names(self) -> list[str]:
        names = []
        for file in self.cases_dir.glob("*.json"):
            if file.name == "dashboardInformations.json":
                continue
            try:
                case = json.loads(file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if self._has_scope(case):
                names.append(file.stem)
        return sorted(names, key=str.lower)

    def reference_for_name(self, name: str) -> str:
        stem = Path(self._file_name(name)).stem
        return hmac.new(self._reference_key, stem.encode("utf-8"), hashlib.sha256).hexdigest()

    def resolve_reference(self, reference: str) -> str | None:
        if len(reference) != 64:
            return None
        for stem in self.list_names():
            if hmac.compare_digest(reference, self.reference_for_name(stem)):
                return stem
        return None

    def list_entries(self, *, recent: bool = False) -> list[dict[str, str]]:
        stems = self.recent_list() if recent else self.list_names()
        entries: list[dict[str, str]] = []
        for stem in stems:
            case = self.load(stem, record_recent=False, activate=False)
            if case is not None:
                entries.append({"name": case.get("name") or stem,
                                "ref": self.reference_for_name(stem),
                                "legacy_name": stem})
        return entries

    def save(self, case: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            case.setdefault("name", None)
            if not case.get("name"):
                case["name"] = self.default_name()
            case.setdefault("created", now_iso())
            case["lastChange"] = now_iso()
            case.setdefault("tenant_id", None)
            case.setdefault("client_id", None)
            case.setdefault("sessionList", [])
            case.setdefault("topTenList", [])
            self._stamp_scope(case)
            path = self._case_path(case["name"])
            if path.exists():
                try:
                    stored = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                    raise CaseNameError("Vorhandener Fall kann nicht sicher überschrieben werden") from exc
                if (
                    not isinstance(stored, dict)
                    or stored.get("name") != case["name"]
                    or stored.get("scope") != case.get("scope")
                    or not self._has_scope(stored)
                ):
                    raise CaseNameError("Fallname kollidiert mit vorhandenem Fall oder Scope")
            atomic_json_replace(path, case)
            self.current = case
            return case

    def load(
        self,
        name: str,
        *,
        record_recent: bool = True,
        activate: bool = True,
    ) -> dict[str, Any] | None:
        path = self._case_path(name)
        if not path.exists():
            return None
        with self._lock:
            case = json.loads(path.read_text(encoding="utf-8"))
            if not self._has_scope(case):
                return None
            if activate:
                self.current = case
            if record_recent:
                self.recent_update(name)
            return case

    @property
    def _recent_path(self) -> Path:
        return self.cases_dir / "dashboardInformations.json"

    def recent_update(self, name: str) -> list[str]:
        try:
            info = json.loads(self._recent_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            info = {}
        recent: list[str] = info.get("recentlyLoadedCases", [])
        if name in recent:
            recent.remove(name)
        recent.insert(0, name)
        if len(recent) > 11:
            del recent[11:]
        atomic_json_replace(
            self._recent_path,
            {"recentlyLoadedCases": recent},
        )
        return recent

    def recent_list(self) -> list[str]:
        try:
            info = json.loads(self._recent_path.read_text(encoding="utf-8"))
            recent = info.get("recentlyLoadedCases", [])
        except (OSError, json.JSONDecodeError, AttributeError):
            return []
        if not isinstance(recent, list):
            return []
        if self.scope is None:
            return recent
        visible = set(self.list_names())
        return [name for name in recent if isinstance(name, str) and name in visible]

    @staticmethod
    def _passport_summary(passport: dict[str, Any]) -> dict[str, Any]:
        return {
            "run_id": passport.get("run_id"),
            "seed": passport.get("seed"),
            "seed_scheme": passport.get("seed_scheme"),
            "passport_schema_version": passport.get("passport_schema_version"),
            "input_hash_scheme": passport.get("input_hash_scheme"),
            "signatur_status": passport.get("signatur_status"),
            "replayable": passport.get("replayable", False),
            "entropy_mode": passport.get("entropy_mode"),
            "copyguard_digest": passport.get("copyguard_digest"),
            "kernel": passport.get("kernel"),
            "kernel_version": passport.get("kernel_version"),
        }

    @staticmethod
    def _new_session(
        analysis_dict: dict[str, Any],
        passport: dict[str, Any],
        draft_id: str | None,
        entropy_checkpoint: dict[str, Any] | None = None,
        *,
        parent_session_id: str | None = None,
    ) -> dict[str, Any]:
        return {
            "sessionId": uuid.uuid4().hex,
            "parentSessionId": parent_session_id,
            "revision": 0,
            "created": now_iso(),
            "intention": None,
            "description": None,
            "analysisBaseline": copy.deepcopy(analysis_dict),
            "analysisResult": copy.deepcopy(analysis_dict),
            "passport": CaseStore._passport_summary(passport),
            "draftId": draft_id,
            "gvHistory": [],
            "gvState": {"generalVitality": 0, "counter": 0, "totalRuns": 0},
            "entropyCheckpoint": copy.deepcopy(entropy_checkpoint),
        }

    def plan_attach_analysis(
        self,
        analysis_dict: dict[str, Any],
        passport: dict[str, Any],
        *,
        draft_id: str | None = None,
        entropy_checkpoint: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]] | None:
        """Plant eine neue Session ohne den aktuellen Fall zu mutieren."""
        with self._lock:
            if not self.current:
                return None
            case = copy.deepcopy(self.current)
        case.setdefault("sessionList", [])
        session = self._new_session(
            analysis_dict,
            passport,
            draft_id,
            entropy_checkpoint,
        )
        case["sessionList"].append(session)
        case["lastChange"] = now_iso()
        return case, session

    def plan_assign_legacy_session_id(
        self,
        index: int,
        *,
        case: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Ergaenzt Legacy-Felder nur im gemeinsam persistierbaren Endzustand."""
        document = copy.deepcopy(case) if case is not None else self._current_copy()
        session = self._session_at_in(document, index)
        if not session.get("sessionId"):
            session["sessionId"] = uuid.uuid4().hex
            session.setdefault("revision", 0)
            session.setdefault("gvHistory", [])
            session.setdefault("gvState", {"generalVitality": 0, "counter": 0, "totalRuns": 0})
            session.setdefault("entropyCheckpoint", None)
            session.setdefault("analysisBaseline", copy.deepcopy(session.get("analysisResult") or {}))
            document["lastChange"] = now_iso()
        return document, session

    def plan_persist_gv_event(
        self,
        session_id: str,
        expected_revision: int,
        snapshot: dict[str, Any],
        entropy_checkpoint: dict[str, Any],
        event_kind: str,
        *,
        case: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        document = copy.deepcopy(case) if case is not None else self._current_copy()
        session = self._session_by_id_in(document, session_id)
        if session.get("revision", 0) != expected_revision:
            raise SessionError("Session wurde zwischenzeitlich geaendert")
        event = {
            "sequence": len(session.setdefault("gvHistory", [])) + 1,
            "kind": event_kind,
            "gv": snapshot.get("gv"),
            "rateIndex": snapshot.get("rateIndex"),
            "state": {
                "generalVitality": snapshot.get("generalVitality", 0),
                "counter": snapshot.get("counter", 0),
                "totalRuns": snapshot.get("totalRuns", 0),
                "pageStart": snapshot.get("pageStart", 0),
                "pageLength": snapshot.get("pageLength", 21),
            },
            "result": copy.deepcopy(snapshot.get("result", {})),
            "entropyCheckpoint": copy.deepcopy(entropy_checkpoint),
        }
        if snapshot.get("stickPadReceiptId") is not None:
            event["stickPadReceiptId"] = snapshot["stickPadReceiptId"]
        session["gvHistory"].append(event)
        session["analysisResult"] = copy.deepcopy(snapshot.get("result", {}))
        session["gvState"] = event["state"]
        session["entropyCheckpoint"] = event["entropyCheckpoint"]
        session["revision"] = expected_revision + 1
        document["lastChange"] = now_iso()
        return document, session

    def plan_fork_session_for_new_round(
        self,
        session_id: str,
        *,
        page_start: int = 0,
        page_length: int = 21,
        entropy_checkpoint: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        document = self._current_copy()
        parent = self._session_by_id_in(document, session_id)
        baseline = copy.deepcopy((parent.get("analysisResult") if page_start else parent.get("analysisBaseline"))
                                 or parent.get("analysisResult") or {})
        if page_start < 0 or page_length < 1 or page_start >= len(baseline.get("rateObjects", [])):
            raise SessionError("Ungueltige GV-Ergebnisseite")
        affected = (baseline.get("rateObjects", []) if page_start == 0
                    else baseline["rateObjects"][page_start:page_start + page_length])
        for rate in affected:
            rate["gv"] = 0
            rate["recurringGeneralVitality"] = 0
        occurrences: dict[int, int] = {}
        for rate in baseline.get("rateObjects", []):
            gv = rate.get("gv") or 0
            if gv:
                occurrences[gv] = occurrences.get(gv, 0) + 1
        for rate in baseline.get("rateObjects", []):
            gv = rate.get("gv") or 0
            rate["recurringGeneralVitality"] = occurrences.get(gv, 0) if gv else 0
        child = self._new_session(
            baseline,
            parent.get("passport") or {},
            entropy_checkpoint,
            parent_session_id=session_id,
        )
        child["gvState"].update({"pageStart": page_start, "pageLength": page_length})
        document.setdefault("sessionList", []).append(child)
        document["lastChange"] = now_iso()
        return document, child

    def plan_set_session_draft(
        self,
        case: dict[str, Any],
        session_id: str,
        draft_id: str,
    ) -> dict[str, Any]:
        document = copy.deepcopy(case)
        self._session_by_id_in(document, session_id)["draftId"] = draft_id
        document["lastChange"] = now_iso()
        return document

    def current_target_key(self, case: dict[str, Any]) -> str:
        return self._file_name(case["name"])

    def apply_planned_case(self, case: dict[str, Any]) -> None:
        with self._lock:
            self.current = case

    def _current_copy(self) -> dict[str, Any]:
        with self._lock:
            if not self.current:
                raise SessionError("Kein Fall geladen")
            return copy.deepcopy(self.current)

    @staticmethod
    def _session_at_in(case: dict[str, Any], index: int) -> dict[str, Any]:
        sessions = case.get("sessionList", [])
        if index < 0 or index >= len(sessions):
            raise SessionError("Session existiert nicht")
        return sessions[index]

    @staticmethod
    def _session_by_id_in(case: dict[str, Any], session_id: str) -> dict[str, Any]:
        for session in case.get("sessionList", []):
            if session.get("sessionId") == session_id:
                return session
        raise SessionError("Session existiert nicht")

    def attach_analysis(
        self,
        analysis_dict: dict[str, Any],
        passport: dict[str, Any],
        *,
        draft_id: str | None = None,
        entropy_checkpoint: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Haengt jede Analyse als neue Session an; vorhandene Sessions bleiben unveraendert."""
        with self._lock:
            if not self.current:
                return None
            case = self.current
            case.setdefault("sessionList", [])
            session = self._new_session(
                analysis_dict,
                passport,
                draft_id,
                entropy_checkpoint,
            )
            case["sessionList"].append(session)
            self.save(case)
            return session

    def session_at(self, index: int, *, assign_legacy_id: bool = False) -> dict[str, Any]:
        if not self.current:
            raise SessionError("Kein Fall geladen")
        sessions = self.current.get("sessionList", [])
        if index < 0 or index >= len(sessions):
            raise SessionError("Session existiert nicht")
        session = sessions[index]
        if assign_legacy_id and not session.get("sessionId"):
            session["sessionId"] = uuid.uuid4().hex
            session.setdefault("revision", 0)
            session.setdefault("gvHistory", [])
            session.setdefault("gvState", {"generalVitality": 0, "counter": 0, "totalRuns": 0})
            session.setdefault("entropyCheckpoint", None)
            session.setdefault("analysisBaseline", copy.deepcopy(session.get("analysisResult") or {}))
            self.save(self.current)
        return session

    def session_by_id(self, session_id: str) -> dict[str, Any]:
        if not self.current:
            raise SessionError("Kein Fall geladen")
        for session in self.current.get("sessionList", []):
            if session.get("sessionId") == session_id:
                return session
        raise SessionError("Session existiert nicht")

    def set_session_draft(self, session_id: str, draft_id: str) -> dict[str, Any]:
        with self._lock:
            session = self.session_by_id(session_id)
            session["draftId"] = draft_id
            self.save(self.current)
            return session

    def persist_gv_event(
        self,
        session_id: str,
        expected_revision: int,
        snapshot: dict[str, Any],
        entropy_checkpoint: dict[str, Any],
        event_kind: str,
    ) -> dict[str, Any]:
        with self._lock:
            session = self.session_by_id(session_id)
            if session.get("revision", 0) != expected_revision:
                raise SessionError("Session wurde zwischenzeitlich geaendert")
            event = {
                "sequence": len(session.setdefault("gvHistory", [])) + 1,
                "kind": event_kind,
                "gv": snapshot.get("gv"),
                "rateIndex": snapshot.get("rateIndex"),
                "state": {
                    "generalVitality": snapshot.get("generalVitality", 0),
                    "counter": snapshot.get("counter", 0),
                    "totalRuns": snapshot.get("totalRuns", 0),
                },
                "result": copy.deepcopy(snapshot.get("result", {})),
                "entropyCheckpoint": copy.deepcopy(entropy_checkpoint),
            }
            session["gvHistory"].append(event)
            session["analysisResult"] = copy.deepcopy(snapshot.get("result", {}))
            session["gvState"] = event["state"]
            session["entropyCheckpoint"] = event["entropyCheckpoint"]
            session["revision"] = expected_revision + 1
            self.save(self.current)
            return session

    def fork_session_for_new_round(self, session_id: str) -> dict[str, Any]:
        with self._lock:
            parent = self.session_by_id(session_id)
            baseline = copy.deepcopy(parent.get("analysisBaseline") or parent.get("analysisResult") or {})
            for rate in baseline.get("rateObjects", []):
                rate["gv"] = 0
                rate["recurringGeneralVitality"] = 0
            child = self._new_session(
                baseline,
                parent.get("passport") or {},
                None,
                parent_session_id=session_id,
            )
            self.current.setdefault("sessionList", []).append(child)
            self.save(self.current)
            return child
