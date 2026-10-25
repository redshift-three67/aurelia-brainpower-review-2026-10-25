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
            self._base_dir.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(
                    {
                        "name": self.name,
                        "booleans": self.booleans,
                        "integers": self.integers,
                        "strings": self.strings,
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

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

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "booleans": self.booleans,
            "integers": self.integers,
            "strings": self.strings,
        }


class SettingsStore:
    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._cache: dict[str, Settings] = {}

    def load(self, name: str = "Settings") -> Settings:
        if name not in self._cache:
            self._cache[name] = Settings(name, self._base_dir)
        return self._cache[name]
