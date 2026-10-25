"""Settings-Speicher — 1:1-Port des AetherOnePi-Schemas (FUNKTIONSANALYSE §7.3).

Schema: { name, booleans{}, integers{}, strings{} } mit selbst-defaultenden
Gettern (Default wird beim ersten Zugriff persistiert) — Verhalten identisch
zu AetherOnePiProcessingConfiguration.
"""

from __future__ import annotations

import json
from pathlib import Path
from threading import RLock
from typing import Any
from .persistence import atomic_json_replace


class Settings:
    def __init__(self, name: str, base_dir: Path) -> None:
        self.name = name
        self._base_dir = base_dir
        self._lock = RLock()
        self.booleans: dict[str, bool] = {}
        self.integers: dict[str, int] = {}
        self.strings: dict[str, str] = {}
        self._load()

    @property
    def path(self) -> Path:
        return self._base_dir / f"{self.name}.json"

    def _load(self) -> None:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        self.booleans = raw.get("booleans", {})
        self.integers = raw.get("integers", {})
        self.strings = raw.get("strings", {})

    def save(self) -> None:
        with self._lock:
            atomic_json_replace(self.path, {
                "name": self.name, "booleans": self.booleans,
                "integers": self.integers, "strings": self.strings,
            })

    def update(self, body: dict) -> None:
        """Validate the entire batch before writing; publish only after durable replace."""
        validated = {}
        for section, expected in (("booleans", bool), ("integers", int), ("strings", str)):
            values = body.get(section, {})
            if type(values) is not dict:
                raise ValueError(f"{section} muss ein Objekt sein")
            for key, value in values.items():
                if type(key) is not str or type(value) is not expected:
                    raise ValueError(f"{section}.{key} hat einen ungültigen Typ")
                bounds = {"broadcast.adjustment.maxFollowups": (0, 3), "broadcast.adjustment.minSeconds": (1, 86400)}
                if section == "integers" and key in bounds and not bounds[key][0] <= value <= bounds[key][1]:
                    raise ValueError(f"{section}.{key} liegt außerhalb der zulässigen Grenze")
                if section == "strings" and key == "entropy.defaultMode" and value not in ("seeded", "stochastic"):
                    raise ValueError("entropy.defaultMode muss seeded oder stochastic sein")
                if section == "strings" and key == "broadcast.optionsVersion" and value != "options-v1":
                    raise ValueError("Unbekannte Broadcast-Optionsversion")
            validated[section] = dict(values)
        with self._lock:
            merged = {section: {**getattr(self, section), **values} for section, values in validated.items()}
            atomic_json_replace(self.path, {"name": self.name, **merged})
            for section, values in merged.items():
                setattr(self, section, values)

    def get_boolean(self, key: str, default: bool) -> bool:
        value = self.booleans.get(key)
        if value is None:
            self.booleans[key] = default
            self.save()
            return default
        return value

    def set_boolean(self, key: str, value: bool) -> None:
        self.booleans[key] = value
        self.save()

    def get_integer(self, key: str, default: int) -> int:
        value = self.integers.get(key)
        if value is None:
            self.integers[key] = default
            self.save()
            return default
        return value

    def set_integer(self, key: str, value: int) -> None:
        self.integers[key] = value
        self.save()

    def get_string(self, key: str, default: str) -> str:
        value = self.strings.get(key)
        if value is None:
            self.strings[key] = default
            self.save()
            return default
        return value

    def set_string(self, key: str, value: str) -> None:
        self.strings[key] = value
        self.save()

    def to_dict(
        self, *, default_booleans: dict[str, bool] | None = None,
        default_strings: dict[str, str] | None = None,
        default_integers: dict[str, int] | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            return {
                "name": self.name,
                "booleans": {**(default_booleans or {}), **self.booleans},
                "integers": {**(default_integers or {}), **self.integers},
                "strings": {**(default_strings or {}), **self.strings},
            }


class SettingsStore:
    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._cache: dict[str, Settings] = {}

    def load(self, name: str = "Settings") -> Settings:
        if name not in self._cache:
            self._cache[name] = Settings(name, self._base_dir)
        return self._cache[name]
