"""Stick-Pad mit reproduzierbarem Standard und explizitem Original-Zeitmodus.

Im Java-Original wird beim Erfassen jeder Position derselbe Millisekundenwert
zu x und y addiert. Der bisherige Port-Modus ohne diese Addition bleibt erhalten.
"""

from __future__ import annotations

import copy
import json
import time
import uuid
from pathlib import Path
from threading import RLock
from typing import Callable

from .analysis import AnalysisResult, Rate, RateObject
from .rates import catalog_binding
from ..persistence import atomic_json_replace
from .javaprng import JavaRandom


class StickPad:
    @staticmethod
    def _valid_position(position: object) -> bool:
        if not isinstance(position, dict):
            return False
        if any(type(position.get(key)) is not int for key in ("x", "y", "seedX", "seedY")):
            return False
        mode = position.get("mode")
        captured = position.get("capturedAtMs")
        if mode == "reproducible":
            return (
                captured is None
                and position["seedX"] == position["x"]
                and position["seedY"] == position["y"]
            )
        return (
            mode == "original"
            and type(captured) is int
            and position["seedX"] == position["x"] + captured
            and position["seedY"] == position["y"] + captured
        )

    @classmethod
    def _valid_receipt(cls, receipt: object) -> bool:
        valid = (
            isinstance(receipt, dict)
            and isinstance(receipt.get("id"), str)
            and receipt.get("kind") in ("analysis", "gv")
            and receipt.get("mode") in ("reproducible", "original")
            and isinstance(receipt.get("positions"), list)
            and bool(receipt["positions"])
            and all(cls._valid_position(p) and p["mode"] == receipt["mode"] for p in receipt["positions"])
        )
        if not valid:
            return valid
        if "runId" in receipt and (not isinstance(receipt["runId"], str) or not receipt["runId"]):
            return False
        if "catalog" not in receipt:
            return True
        catalog = receipt["catalog"]
        return (
            receipt["kind"] == "analysis"
            and isinstance(catalog, dict)
            and catalog.get("scheme") == "ordered-rates-sha256-v1"
            and isinstance(catalog.get("selector"), str)
            and (catalog["selector"] == "" or bool(catalog["selector"].strip()))
            and type(catalog.get("rateCount")) is int
            and catalog["rateCount"] > 0
            and isinstance(catalog.get("digest"), str)
            and len(catalog["digest"]) == 64
            and all(char in "0123456789abcdef" for char in catalog["digest"])
            and ("releaseId" not in catalog or (
                isinstance(catalog["releaseId"], str)
                and len(catalog["releaseId"]) == 32
                and all(char in "0123456789abcdef" for char in catalog["releaseId"])
            ))
        )

    def __init__(
        self,
        storage_path: Path | None = None,
        *,
        clock_ms: Callable[[], int] | None = None,
    ) -> None:
        self.storage_path = Path(storage_path) if storage_path is not None else None
        self.clock_ms = clock_ms or (lambda: time.time_ns() // 1_000_000)
        self._lock = RLock()
        self.positions: list[dict] = []
        self._receipts: list[dict] = []
        if self.storage_path is not None and self.storage_path.exists():
            document = json.loads(self.storage_path.read_text(encoding="utf-8"))
            if (
                not isinstance(document, dict)
                or document.get("version") != 1
                or not isinstance(document.get("positions"), list)
                or not isinstance(document.get("receipts"), list)
                or len(document["receipts"]) > 20
                or not all(self._valid_position(p) for p in document["positions"])
                or len({p["mode"] for p in document["positions"]}) > 1
                or not all(self._valid_receipt(r) for r in document["receipts"])
            ):
                raise ValueError("Stick-Pad-Zustand ist ungueltig")
            self.positions = document["positions"]
            self._receipts = document["receipts"]

    def _commit(self, positions: list[dict], receipts: list[dict] | None = None) -> None:
        if receipts is None:
            receipts = self._receipts
        if self.storage_path is not None:
            atomic_json_replace(self.storage_path, self._document(positions, receipts))
        self.positions = positions
        self._receipts = receipts

    @staticmethod
    def _document(positions: list[dict], receipts: list[dict]) -> dict:
        return {"version": 1, "positions": copy.deepcopy(positions), "receipts": copy.deepcopy(receipts)}

    def transaction_lock(self) -> RLock:
        """Haelt Positionsplanung und gemeinsame Recovery-Persistenz zusammen."""
        return self._lock

    def apply_persisted_document(self, document: dict) -> None:
        """Nur nach erfolgreicher Recovery-Transaktion und unter transaction_lock."""
        self.positions = copy.deepcopy(document["positions"])
        self._receipts = copy.deepcopy(document["receipts"])

    def status(self) -> dict:
        with self._lock:
            return {
                "mode": self.positions[0]["mode"] if self.positions else None,
                "positions": copy.deepcopy(self.positions),
                "lastReceipt": copy.deepcopy(self._receipts[-1]) if self._receipts else None,
            }

    def add_position(self, x: int, y: int, *, mode: str = "reproducible") -> int:
        return self.record_position(x, y, mode=mode)["positions"]

    def record_position(self, x: int, y: int, *, mode: str = "reproducible") -> dict:
        if mode not in ("reproducible", "original"):
            raise ValueError("Unbekannter Stick-Pad-Modus")
        with self._lock:
            if self.positions and self.positions[0]["mode"] != mode:
                raise ValueError("Modus innerhalb eines Stick-Pad-Laufs nicht wechseln")
            captured_ms = int(self.clock_ms()) if mode == "original" else None
            offset = captured_ms if captured_ms is not None else 0
            position = {
                "x": int(x), "y": int(y),
                "seedX": int(x) + offset, "seedY": int(y) + offset,
                "capturedAtMs": captured_ms, "mode": mode,
            }
            updated = [*self.positions, position]
            self._commit(updated)
            return {"positions": len(updated), "capture": copy.deepcopy(position)}

    def clear(self) -> int:
        with self._lock:
            count = len(self.positions)
            self._commit([])
            return count

    def _receipt(self, kind: str, catalog: dict | None = None, *, run_id: str | None = None) -> dict:
        receipt = {
            "id": uuid.uuid4().hex,
            "kind": kind,
            "mode": self.positions[0]["mode"],
            "positions": copy.deepcopy(self.positions),
        }
        if catalog is not None:
            receipt["catalog"] = catalog
        if run_id is not None:
            receipt["runId"] = run_id
        return receipt

    def _finish(self, receipt: dict) -> None:
        self._commit([], [*self._receipts[-19:], receipt])

    # -- Analyse (StickPad.analyze) ---------------------------------------

    def analyze(self, rates: list[Rate]) -> AnalysisResult:
        result, _ = self.analyze_with_capture(rates)
        return result

    def analyze_with_capture(
        self, rates: list[Rate], *, selector: str | None = None,
    ) -> tuple[AnalysisResult, dict | None]:
        with self._lock:
            result, receipt, _, after = self.plan_analysis_with_capture(
                rates, selector=selector,
            )
            self._commit(after["positions"], after["receipts"])
            return result, receipt

    def plan_analysis_with_capture(
        self, rates: list[Rate], *, selector: str | None = None,
        run_id: str | None = None, release_id: str | None = None,
    ) -> tuple[AnalysisResult, dict, dict, dict]:
        """Plant die Originalberechnung samt Beleg, ohne Positionen zu verbrauchen."""
        with self._lock:
            if not self.positions:
                raise ValueError("Keine Stick-Pad-Positionen gesammelt.")
            if not rates:
                raise ValueError("Keine Raten fuer die Stick-Pad-Analyse")
            binding = catalog_binding(selector, rates, release_id=release_id) if selector is not None else None
            values: dict[str, int] = {}
            url_by_name = {r.name: r.url for r in rates if r.url}
            for position in self.positions:
                rate_index = JavaRandom(position["seedX"]).next_int(len(rates))
                rate = rates[rate_index]
                energetic_value = JavaRandom(position["seedY"]).next_int(10) + 1
                values[rate.name] = values.get(rate.name, 0) + energetic_value
            result = AnalysisResult()
            for name, value in values.items():
                parts = name.split("\t")
                if len(parts) > 1:
                    result.rate_objects.append(
                        RateObject(energetic_value=value, name_or_rate=parts[0], url=parts[1])
                    )
                else:
                    result.rate_objects.append(
                        RateObject(energetic_value=value, name_or_rate=name, url=url_by_name.get(name))
                    )
            result.sort()
            receipt = self._receipt("analysis", binding, run_id=run_id)
            before = self._document(self.positions, self._receipts)
            after = self._document([], [*self._receipts[-19:], receipt])
            return result, copy.deepcopy(receipt), before, after

    # -- GV (StickPad.checkGeneralVitality, Positionen werden verbraucht) --

    def check_general_vitality(self) -> int | None:
        gv, _ = self.check_general_vitality_with_capture()
        return gv

    def check_general_vitality_with_capture(self) -> tuple[int | None, dict | None]:
        with self._lock:
            planned = self.plan_general_vitality_with_capture()
            if planned is None:
                return None, None
            gv, receipt, _, after = planned
            self._commit(after["positions"], after["receipts"])
            return gv, receipt

    def plan_general_vitality_with_capture(self) -> tuple[int, dict, dict, dict] | None:
        """Berechnet GV und Vorher/Nachher-Dokument ohne Positionen zu verbrauchen."""
        with self._lock:
            if not self.positions:
                return None
            draws = sorted(
                (JavaRandom(position["seedX"]).next_int(1000) + 1 for position in self.positions),
                reverse=True,
            )
            gv = draws[0]
            if gv > 950:
                remaining = list(self.positions)
                roll = JavaRandom(remaining.pop(0)["seedY"]).next_int(100)
                while roll >= 50 and remaining:
                    gv += roll
                    roll = JavaRandom(remaining.pop(0)["seedY"]).next_int(100)
            receipt = self._receipt("gv")
            before = self._document(self.positions, self._receipts)
            after = self._document([], [*self._receipts[-19:], receipt])
            return gv, copy.deepcopy(receipt), before, after
