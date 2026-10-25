"""Raten-Datenbanken — Port des DataService (FUNKTIONSANALYSE §7.2).

Format unveraendert uebernommen:
- Baum unter ``data/``; ``.txt`` = Datenbank, ``.rscript`` = Skript.
- ``FUNCTION_*``-Dateien werden ignoriert.
- Zeilen: ``NAME`` oder ``NAME\\tURL`` (TAB-Trenner, RateUtils-Konvention).
- Praefix-Matching: ``findAllBySourceName("HOMEOPATHY")`` laedt ALLE
  Datenbanken, deren Dateiname mit dem Praefix beginnt.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .analysis import Rate

_RATE_LINE = re.compile(r"\S")


@dataclass
class RateDatabase:
    name: str  # Dateiname ohne .txt (API-Namen sind ohne Suffix)
    file: Path


class RateRepository:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)
        self._databases: dict[str, Path] = {}
        self._scripts: dict[str, Path] = {}

    # -- Indizierung ------------------------------------------------------

    def refresh(self) -> None:
        """DataService.refreshDatabaseList + searchForRateFiles."""
        self._databases.clear()
        self._scripts.clear()
        if not self.data_dir.exists():
            return
        for path in sorted(self.data_dir.rglob("*")):
            if not path.is_file():
                continue
            name = path.name
            if name.startswith("FUNCTION_"):
                continue
            if name.endswith(".txt"):
                self._databases[name] = path
            elif name.endswith(".rscript"):
                self._scripts[name] = path

    # -- Abfragen ---------------------------------------------------------

    def database_names(self) -> list[str]:
        """DataService.getDatabaseNames — Namen ohne .txt."""
        return sorted(name[:-4] for name in self._databases)

    def script_names(self) -> list[str]:
        return sorted(name[:-8] for name in self._scripts)

    def find_all_by_source_name(self, source_name: str) -> list[Rate]:
        """DataService.findAllBySourceName inkl. Praefix-Matching.

        Endet die Anfrage auf ``.txt``: exakt eine Datei. Sonst: alle
        Datenbanken, deren Dateiname mit ``source_name`` beginnt (Kategorien
        wie HOMEOPATHY/BIOLOGICAL/... sind Praefix-Selektoren).
        """
        if source_name.endswith(".txt"):
            files = [self._databases[source_name]] if source_name in self._databases else []
        else:
            files = [
                path
                for name, path in sorted(self._databases.items())
                if name.startswith(source_name)
            ]
        rates: list[Rate] = []
        for file in files:
            rates.extend(self._parse(file))
        return rates

    # -- Parser -----------------------------------------------------------

    @staticmethod
    def _parse(file: Path) -> list[Rate]:
        rates: list[Rate] = []
        try:
            lines = file.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return rates
        for line in lines:
            if not line or not line.strip():
                continue
            name, _, url = line.partition("\t")
            rates.append(
                Rate(
                    name=name.strip(),
                    url=url.strip() or None,
                    source_name=file.name,
                )
            )
        return rates
