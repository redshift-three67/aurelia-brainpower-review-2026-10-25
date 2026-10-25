"""Explicit single-case rate checks, separate from analysis/GV-round and broadcast."""
from __future__ import annotations
import copy, json, re, threading, uuid
from datetime import datetime, timezone
from .analysis import check_general_vitality
from .personal_context import ContextSnapshot, ContextError
from ..persistence import atomic_json_replace, document_digest

HEX32 = re.compile(r"[0-9a-f]{32}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
TERMINAL = {"completed", "cancelled", "failed", "interrupted"}
class WatchlistError(ValueError): pass

class WatchlistController:
    def __init__(self, root, scope):
        self.root = root; self.scope = scope.to_dict(); self._lock = threading.RLock()
        self._thread = None; self._active = None; self._closed = False
        if root.is_symlink() or root.is_junction(): raise WatchlistError("Watchlist-Ablage darf kein Link sein.")
        root.mkdir(parents=True, exist_ok=True)
        for path in root.glob("*.json"):
            record = self._read(path.stem)
            if record["status"] not in TERMINAL:
                record["status"] = "interrupted"; self._write(record)

    def _validate_basis(self, basis):
        fields = {"caseId", "sessionId", "contextSnapshot", "sessionDigest", "indices", "rates", "referenceGv", "mode", "seed"}
        if type(basis) is not dict or set(basis) != fields: raise WatchlistError("Ungültiger Watchlist-Bezug.")
        for key in ("caseId", "sessionId"):
            if type(basis[key]) is not str or not HEX32.fullmatch(basis[key]): raise WatchlistError("Ungültige Fall-/Sitzungskennung.")
        if type(basis["sessionDigest"]) is not str or not HEX64.fullmatch(basis["sessionDigest"]): raise WatchlistError("Sitzungsbeleg fehlt.")
        try: snap = ContextSnapshot.from_payload(basis["contextSnapshot"]).payload()
        except ContextError as exc: raise WatchlistError("Fallkontext ist nicht belegt.") from exc
        if snap["caseId"] != basis["caseId"] or snap["scope"] != self.scope: raise WatchlistError("Watchlist liegt außerhalb des Fallbereichs.")
        indices = basis["indices"]; rates = basis["rates"]
        if (type(indices) is not list or not 1 <= len(indices) <= 100 or any(type(i) is not int or not 0 <= i < 4096 for i in indices)
                or len(set(indices)) != len(indices) or type(rates) is not list or len(rates) != len(indices)
                or any(type(r) is not str or not r.strip() or len(r) > 4096 for r in rates)):
            raise WatchlistError("Bitte 1 bis 100 verschiedene Ergebnisraten wählen.")
        if type(basis["referenceGv"]) is not int or not 0 <= basis["referenceGv"] <= 1000000: raise WatchlistError("Original-Fall-GV fehlt.")
        if basis["mode"] not in ("seeded", "stochastic") or (basis["mode"] == "seeded" and type(basis["seed"]) is not int) or (basis["mode"] == "stochastic" and basis["seed"] is not None):
            raise WatchlistError("Zufallsmodus und Seed widersprechen sich.")

    def _path(self, job):
        if type(job) is not str or not HEX32.fullmatch(job): raise WatchlistError("Ungültiger Watchlist-Auftrag.")
        path = self.root / (job + ".json")
        if path.is_symlink() or path.is_junction(): raise WatchlistError("Watchlist-Beleg darf kein Link sein.")
        return path

    def _read(self, job):
        try: record = json.loads(self._path(job).read_text(encoding="utf8"))
        except (OSError, ValueError) as exc: raise WatchlistError("Watchlist-Beleg ist nicht lesbar.") from exc
        fields = {"schemaVersion", "id", "scope", "createdAt", "status", "input", "rows", "error", "requestId", "digest"}
        if (type(record) is not dict or set(record) != fields or type(record["schemaVersion"]) is not int or record["schemaVersion"] != 1
                or record["id"] != job or record["scope"] != self.scope or record["status"] not in TERMINAL | {"queued", "running"}
                or record["digest"] != document_digest({k: v for k, v in record.items() if k != "digest"})):
            raise WatchlistError("Watchlist-Beleg wurde verändert.")
        if record["requestId"] is not None and (type(record["requestId"]) is not str or not HEX32.fullmatch(record["requestId"])): raise WatchlistError("Anfragekennung ist ungültig.")
        self._validate_basis(record["input"])
        rows = record["rows"]; basis = record["input"]
        if type(rows) is not list or len(rows) > len(basis["indices"]): raise WatchlistError("Watchlist-Ergebnisse sind ungültig.")
        for i, row in enumerate(rows):
            if (type(row) is not dict or set(row) != {"inputIndex", "rate", "gv", "checkpoint"}
                    or row["inputIndex"] != basis["indices"][i] or row["rate"] != basis["rates"][i]
                    or type(row["gv"]) is not int or not 0 <= row["gv"] <= 1000000 or type(row["checkpoint"]) is not dict):
                raise WatchlistError("Watchlist-Ergebnisbezug ist ungültig.")
        if record["status"] == "completed" and len(rows) != len(basis["indices"]): raise WatchlistError("Watchlist-Abschluss ist unvollständig.")
        return record

    def _write(self, record):
        record = {k: v for k, v in record.items() if k != "digest"}; record["digest"] = document_digest(record)
        atomic_json_replace(self._path(record["id"]), record)

    def submit(self, basis, provider, request_id=None):
        self._validate_basis(basis)
        with self._lock:
            if request_id is not None:
                if type(request_id) is not str or not HEX32.fullmatch(request_id): raise WatchlistError("Ungültige Anfragekennung.")
                for path in self.root.glob("*.json"):
                    existing = self._read(path.stem)
                    if existing["requestId"] == request_id:
                        if existing["input"] != basis: raise WatchlistError("Anfragekennung gehört zu anderen Eingaben.")
                        return existing
            if self._closed or (self._thread and self._thread.is_alive()) or self._active:
                raise WatchlistError("Ein Watchlist-Auftrag läuft bereits; bitte Abschluss oder Abbruch abwarten.")
            record = {"schemaVersion": 1, "id": uuid.uuid4().hex, "scope": self.scope,
                "createdAt": datetime.now(timezone.utc).isoformat(), "status": "queued",
                "input": copy.deepcopy(basis), "rows": [], "error": None, "requestId": request_id}
            self._write(record); self._active = record["id"]
            try: self._launch(record["id"], provider)
            except Exception:
                record["status"] = "failed"; record["error"] = "worker-start"; self._write(record); self._active = None; raise
            return self._read(record["id"])

    def _launch(self, job, provider):
        self._thread = threading.Thread(target=self._run, args=(job, provider), name="watchlist", daemon=True)
        self._thread.start()

    def _run(self, job, provider):
        try:
            with self._lock:
                record = self._read(job)
                if self._closed or record["status"] in TERMINAL: return
                record["status"] = "running"; self._write(record)
            for index, rate in zip(record["input"]["indices"], record["input"]["rates"]):
                with self._lock:
                    if self._closed or self._read(job)["status"] in TERMINAL: return
                gv = check_general_vitality(provider)
                provider.commit_journal()
                checkpoint = provider.checkpoint()
                with self._lock:
                    record = self._read(job)
                    if self._closed or record["status"] in TERMINAL: return
                    record["rows"].append({"inputIndex": index, "rate": rate, "gv": gv, "checkpoint": checkpoint})
                    self._write(record)
            with self._lock:
                record = self._read(job)
                if not self._closed and record["status"] not in TERMINAL:
                    record["status"] = "completed"; self._write(record)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).exception("Watchlist-Ausführung fehlgeschlagen")
            with self._lock:
                record = self._read(job)
                if record["status"] not in TERMINAL:
                    record["status"] = "failed"; record["error"] = type(exc).__name__; self._write(record)
        finally:
            with self._lock:
                if self._active == job: self._active = None

    def get(self, job):
        with self._lock: return copy.deepcopy(self._read(job))

    def history(self, case_id):
        with self._lock:
            records = [self._read(path.stem) for path in self.root.glob("*.json")]
            return sorted([row for row in records if row["input"]["caseId"] == case_id], key=lambda row: row["createdAt"])[-50:]

    def cancel(self, job):
        with self._lock:
            record = self._read(job)
            if record["status"] not in TERMINAL:
                record["status"] = "cancelled"; self._write(record)
            return record

    def shutdown(self):
        failure = None
        with self._lock:
            self._closed = True
            thread = self._thread
            try:
                if self._active:
                    record = self._read(self._active)
                    if record["status"] not in TERMINAL:
                        record["status"] = "interrupted"; self._write(record)
            except Exception as exc:
                failure = exc
        # The runtime lease must outlive every worker even if status persistence failed.
        if thread and thread is not threading.current_thread():
            try: thread.join()
            except Exception as exc:
                if failure is None: failure = exc
        if failure is not None: raise failure
