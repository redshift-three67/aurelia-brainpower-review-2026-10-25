"""Case/Session-Persistenz — JSON-Contract des Originals (FUNKTIONSANALYSE §7.1).

Die Feldnamen bleiben bewusst camelCase (name, sessionList, analysisResult,
rateObjects, energeticValue, ...), damit Bestands-Cases aus AetherOnePi
ungenannt ladbar bleiben. Tenant-Felder (tenant_id, client_id) sind zusaetzlich
vorgesehen (Aurelia-Pflicht, Phase-1: null).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .analysis import AnalysisResult


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class CaseStore:
    def __init__(self, cases_dir: Path) -> None:
        self.cases_dir = Path(cases_dir)
        self.cases_dir.mkdir(parents=True, exist_ok=True)
        self.current: dict[str, Any] | None = None

    # -- Benennung (DataService.saveCase-Konvention) -----------------------

    @staticmethod
    def default_name() -> str:
        return datetime.now().strftime("%Y.%m.%d-%H%M%S")

    @staticmethod
    def _file_name(case_name: str) -> str:
        return f"{case_name.replace(' ', '')}.json"

    # -- CRUD --------------------------------------------------------------

    def list_names(self) -> list[str]:
        names = [
            file.stem
            for file in self.cases_dir.glob("*.json")
            if file.name != "dashboardInformations.json"
        ]
        return sorted(names, key=str.lower)

    def save(self, case: dict[str, Any]) -> dict[str, Any]:
        case.setdefault("name", None)
        if not case.get("name"):
            case["name"] = self.default_name()
        case.setdefault("created", now_iso())
        case["lastChange"] = now_iso()
        case.setdefault("tenant_id", None)
        case.setdefault("client_id", None)
        case.setdefault("sessionList", [])
        case.setdefault("topTenList", [])
        path = self.cases_dir / self._file_name(case["name"])
        path.write_text(
            json.dumps(case, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        self.current = case
        return case

    def load(self, name: str) -> dict[str, Any] | None:
        path = self.cases_dir / self._file_name(name)
        if not path.exists():
            path = self.cases_dir / f"{name}.json"
        if not path.exists():
            return None
        case = json.loads(path.read_text(encoding="utf-8"))
        self.current = case
        self.recent_update(name)
        return case

    # -- „LAST CASES" (DataService.loadDashboardInformations, max. 11) ----

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
        self._recent_path.write_text(
            json.dumps({"recentlyLoadedCases": recent}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return recent

    def recent_list(self) -> list[str]:
        try:
            info = json.loads(self._recent_path.read_text(encoding="utf-8"))
            return info.get("recentlyLoadedCases", [])
        except (OSError, json.JSONDecodeError):
            return []

    def attach_analysis(self, analysis_dict: dict[str, Any], passport: dict[str, Any]) -> None:
        """Event-Handler.saveCase: Analyse an letzte Session haengen (neu bei Bedarf)."""
        if not self.current:
            return
        case = self.current
        if not case.get("sessionList"):
            case["sessionList"] = [{"created": now_iso(), "intention": None, "description": None}]
        session = case["sessionList"][-1]
        session["analysisResult"] = analysis_dict
        session["passport"] = {
            "run_id": passport.get("run_id"),
            "seed": passport.get("seed"),
            "kernel": passport.get("kernel"),
            "kernel_version": passport.get("kernel_version"),
        }
        self.save(case)
