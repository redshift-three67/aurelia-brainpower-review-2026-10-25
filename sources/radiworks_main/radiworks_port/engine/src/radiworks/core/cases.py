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
from .personal_context import ContextError, ContextSnapshot, context_title, prepare_identity


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

    def _direct_case_path(self, case_name: str) -> Path | None:
        """Return a safe legacy filename path without treating display labels as paths."""
        try:
            file_name = self._file_name(case_name)
        except CaseNameError:
            return None
        if len(file_name) > 240:
            return None
        root = self.cases_dir.resolve()
        path = (root / file_name).resolve()
        if not path.is_relative_to(root):
            raise CaseNameError("Fallname liegt ausserhalb des Fallverzeichnisses")
        return path

    def _case_path(self, case_name: str) -> Path:
        if not isinstance(case_name, str) or not case_name.strip():
            raise CaseNameError("Fallname muss Text sein")
        root = self.cases_dir.resolve()
        matches = []
        for candidate in self.cases_dir.glob("*.json"):
            if candidate.name == "dashboardInformations.json":
                continue
            try:
                document = json.loads(candidate.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                continue
            if isinstance(document, dict) and self._has_scope(document) and document.get("name") == case_name:
                resolved = candidate.resolve()
                if not resolved.is_relative_to(root):
                    raise CaseNameError("Fallname liegt ausserhalb des Fallverzeichnisses")
                matches.append(resolved)
        if len(matches) > 1:
            raise CaseNameError("Fallname ist nicht eindeutig")
        if matches:
            return matches[0]
        path = self._direct_case_path(case_name)
        if path is None:
            raise CaseNameError("Fallname kann nicht als Legacy-Dateiname aufgelöst werden")
        return path
    def find_identity(self, case_id: str) -> tuple[Path, dict] | None:
        matches = []
        for candidate in self.cases_dir.glob("*.json"):
            if candidate.name == "dashboardInformations.json":
                continue
            try:
                document = json.loads(candidate.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                continue
            if isinstance(document, dict) and self._has_scope(document) and document.get("caseId") == case_id:
                resolved = candidate.resolve()
                if not resolved.is_relative_to(self.cases_dir.resolve()):
                    raise CaseNameError("Fallidentität liegt ausserhalb des Fallverzeichnisses")
                matches.append((resolved, document))
        if len(matches) > 1:
            raise CaseNameError("Fallidentität ist nicht eindeutig")
        return matches[0] if matches else None

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

    def _reference_for_path(self, path: Path) -> str:
        return hmac.new(self._reference_key, path.stem.encode("utf-8"), hashlib.sha256).hexdigest()

    def reference_for_name(self, name: str) -> str:
        return self._reference_for_path(self._case_path(name))

    def reference_for_case(self, case: dict[str, Any]) -> str:
        case_id = case.get("caseId")
        owner = self.find_identity(case_id) if isinstance(case_id, str) else None
        if owner is not None:
            return self._reference_for_path(owner[0])
        return self.reference_for_name(case.get("name"))

    def resolve_reference(self, reference: str) -> str | None:
        if len(reference) != 64:
            return None
        for stem in self.list_names():
            expected = hmac.new(self._reference_key, stem.encode("utf-8"), hashlib.sha256).hexdigest()
            if hmac.compare_digest(reference, expected):
                return stem
        return None

    def list_entries(self, *, recent: bool = False) -> list[dict[str, str]]:
        stems = self.recent_list() if recent else self.list_names()
        entries: list[dict[str, str]] = []
        for stem in stems:
            path = self._direct_case_path(stem)
            if path is None or not path.is_file():
                try:
                    path = self._case_path(stem)
                except CaseNameError:
                    continue
            try:
                case = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                continue
            if not isinstance(case, dict) or not self._has_scope(case):
                continue
            entries.append({
                "name": case.get("name") or path.stem,
                "ref": self._reference_for_path(path),
                "legacy_name": path.stem,
            })
        return entries
    def save(self, case: dict[str, Any], *, allow_rename: bool = False, allow_new_context: bool = False, allow_inherited_context: bool = False, origin_reference: str | None = None) -> dict[str, Any]:
        with self._lock:
            supplied_sessions = "sessionList" in case
            if "titleMode" in case and case["titleMode"] not in ("manual", "context"):
                raise CaseNameError("Titelmodus muss manual oder context sein.")
            case.setdefault("name", None)
            case.setdefault("created", now_iso())
            case["lastChange"] = now_iso()
            case.setdefault("tenant_id", None)
            case.setdefault("client_id", None)
            case.setdefault("sessionList", [])
            case.setdefault("topTenList", [])
            self._stamp_scope(case)

            owner = self.find_identity(case["caseId"]) if isinstance(case.get("caseId"), str) else None
            stored_path = owner[0] if owner is not None else None
            stored = owner[1] if owner is not None else None
            clone_source = None
            mode = case.get("titleMode", "manual")

            if stored is None and allow_rename and origin_reference is not None:
                # Legacy rename must identify its source, never substitute the active case.
                stem = self.resolve_reference(origin_reference)
                source_path = self._direct_case_path(stem) if stem is not None else None
                source = self.load_reference(origin_reference, record_recent=False, activate=False)
                if source_path is None or source is None:
                    raise CaseNameError("Ursprünglicher Fall ist nicht sicher auflösbar")
                if case.get("caseId") is not None and case.get("caseId") != source.get("caseId"):
                    raise CaseNameError("Ursprüngliche Fallidentität stimmt nicht überein")
                stored_path, stored = source_path, source

            if stored is None and mode == "manual" and case.get("name"):
                try:
                    candidate_path = self._case_path(case["name"])
                except CaseNameError:
                    candidate_path = None
                if candidate_path is not None and candidate_path.is_file():
                    try:
                        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
                    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                        raise CaseNameError("Vorhandener Fall kann nicht sicher überschrieben werden") from exc
                    if isinstance(candidate, dict) and self._has_scope(candidate) and candidate.get("name") == case["name"]:
                        stored_path, stored = candidate_path, candidate

            if stored is not None and "titleMode" not in case:
                if "titleMode" in stored:
                    case["titleMode"] = stored["titleMode"]
                mode = stored.get("titleMode", "manual")
            elif stored is None and "titleMode" not in case:
                case["titleMode"] = "manual"
                mode = "manual"
            else:
                mode = case.get("titleMode", "manual")
            if mode not in ("manual", "context"):
                raise CaseNameError("Titelmodus muss manual oder context sein.")

            if owner is not None and mode == "manual" and not allow_rename and case.get("name") != owner[1].get("name"):
                clone_source = owner[1]
                owner = None
                stored = None
                stored_path = None
                case.pop("caseId", None)
                case.pop("contextVersion", None)

            if mode == "context":
                if not case.get("caseId"):
                    case["caseId"] = (stored or {}).get("caseId") or uuid.uuid4().hex
                try:
                    case["name"] = context_title(case)
                except ContextError as exc:
                    raise CaseNameError(str(exc)) from exc
            elif not case.get("name"):
                case["name"] = (stored or {}).get("name") or self.default_name()

            try:
                prepare_identity(case, stored)
            except ContextError as exc:
                raise CaseNameError(str(exc)) from exc

            if owner is not None:
                path = owner[0]
            elif stored_path is not None and (allow_rename or stored is not None):
                path = stored_path
            elif mode == "context":
                path = self.cases_dir / f"case-{case['caseId']}.json"
            else:
                path = self._case_path(case["name"])
            root = self.cases_dir.resolve()
            path = path.resolve()
            if not path.is_relative_to(root):
                raise CaseNameError("Fall liegt ausserhalb des Fallverzeichnisses")

            stored_at_path = None
            if path.exists():
                try:
                    stored_at_path = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                    raise CaseNameError("Vorhandener Fall kann nicht sicher überschrieben werden") from exc
                if stored_path is None or path != stored_path:
                    raise CaseNameError("Fallname kollidiert mit vorhandenem Fall")
                if (
                    not isinstance(stored_at_path, dict)
                    or stored_at_path.get("scope") != case.get("scope")
                    or not self._has_scope(stored_at_path)
                    or (stored_at_path.get("name") != case["name"]
                        and not allow_rename
                        and not (mode == "context" and stored_at_path.get("caseId") == case.get("caseId")))
                ):
                    raise CaseNameError("Fallname kollidiert mit vorhandenem Fall oder Scope")

            source = stored_at_path or stored or clone_source
            if stored_at_path is not None and not supplied_sessions:
                case["sessionList"] = copy.deepcopy(stored_at_path.get("sessionList", []))
            incoming_sessions = case.get("sessionList")
            if not isinstance(incoming_sessions, list) or any(not isinstance(item, dict) for item in incoming_sessions):
                raise SessionError("Sitzungsliste ist ungültig")
            sources = source.get("sessionList", []) if source is not None else []
            preserved_contexts = []
            for index, original in enumerate(sources):
                identifier = original.get("sessionId")
                matches = ([item for item in incoming_sessions if item.get("sessionId") == identifier]
                           if identifier is not None else incoming_sessions[index:index+1])
                if len(matches) != 1 or matches[0].get("contextSnapshot") != original.get("contextSnapshot"):
                    raise SessionError("Sitzungskontexte dürfen weder geändert, ergänzt noch entfernt werden")
                if matches[0].get("comparisonBasis") != original.get("comparisonBasis"):
                    raise SessionError("Feste Vergleichsbelege dürfen nicht geändert werden")
                if original.get("comparisonBasis") is not None and matches[0].get("analysisBaseline") != original.get("analysisBaseline"):
                    raise SessionError("Belegte Originalgrundlagen dürfen nicht geändert werden")
                if original.get("comparisonBasis") is not None and matches[0].get("passport") != original.get("passport"):
                    raise SessionError("Belegte Originalprovenienz darf nicht geändert werden")
                if original.get("contextSnapshot") is not None:
                    preserved_contexts.append((identifier, original["contextSnapshot"]))
            for session in incoming_sessions:
                if session.get("comparisonBasis") is not None:
                    originals = [old for old in sources if old.get("sessionId") == session.get("sessionId")]
                    if not originals and not allow_new_context:
                        raise SessionError("Neue Vergleichsbelege entstehen nur im serverseitigen Originalauftrag")
                snapshot = session.get("contextSnapshot")
                if snapshot is None or (session.get("sessionId"), snapshot) in preserved_contexts:
                    continue
                if not (allow_new_context or allow_inherited_context):
                    raise SessionError("Neue feste Sitzungskontexte entstehen nur bei einem serverseitigen Analyseauftrag")
                checked = ContextSnapshot.from_payload(snapshot).payload()
                if checked["scope"] != (self.scope.to_dict() if self.scope else None):
                    raise SessionError("Neuer Sitzungskontext passt nicht zum Scope")
                parents = [item for item in sources if item.get("sessionId") == session.get("parentSessionId")]
                inherited = (allow_inherited_context and session.get("parentSessionId") is not None
                             and len(parents) == 1 and parents[0].get("contextSnapshot") == checked)
                # Copies retain historical provenance; only a persisted parent may supply it.
                if not inherited and (not allow_new_context or checked["caseId"] != case.get("caseId")):
                    raise SessionError("Neuer Sitzungskontext passt nicht zum Fall oder Elternauftrag")
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
        return self._load_path(self._case_path(name), record_recent=record_recent, activate=activate)

    def load_reference(
        self,
        reference: str,
        *,
        record_recent: bool = True,
        activate: bool = True,
    ) -> dict[str, Any] | None:
        stem = self.resolve_reference(reference)
        if stem is None:
            return None
        path = self._direct_case_path(stem)
        if path is None:
            return None
        return self._load_path(path, record_recent=record_recent, activate=activate)

    def _load_path(
        self,
        path: Path,
        *,
        record_recent: bool,
        activate: bool,
    ) -> dict[str, Any] | None:
        if not path.is_file():
            return None
        with self._lock:
            case = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(case, dict) or not self._has_scope(case):
                return None
            if activate:
                self.current = case
            if record_recent:
                self.recent_update(path.stem)
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
        previous = copy.deepcopy(case)
        try:
            prepare_identity(case, previous)
            context_snapshot = ContextSnapshot.capture(case, self.scope).payload()
        except ContextError as exc:
            raise SessionError(str(exc)) from exc
        case.setdefault("sessionList", [])
        session = self._new_session(
            analysis_dict,
            passport,
            draft_id,
            entropy_checkpoint,
        )
        session["contextSnapshot"] = context_snapshot
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
            None,
            entropy_checkpoint,
            parent_session_id=session_id,
        )
        if parent.get("contextSnapshot") is not None:
            child["contextSnapshot"] = ContextSnapshot.from_payload(parent["contextSnapshot"]).payload()
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
        case_id = case.get("caseId")
        owner = self.find_identity(case_id) if isinstance(case_id, str) else None
        path = owner[0] if owner is not None else self._case_path(case["name"])
        return path.name
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
        """Compatibility helper with the same frozen context as the planned API path."""
        with self._lock:
            planned = self.plan_attach_analysis(
                analysis_dict, passport, draft_id=draft_id,
                entropy_checkpoint=entropy_checkpoint,
            )
            if planned is None:
                return None
            case, session = planned
            self.save(case, allow_new_context=True)
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
            if parent.get("contextSnapshot") is not None:
                child["contextSnapshot"] = ContextSnapshot.from_payload(parent["contextSnapshot"]).payload()
            document = copy.deepcopy(self.current)
            document.setdefault("sessionList", []).append(child)
            self.save(document, allow_inherited_context=True)
            return child
