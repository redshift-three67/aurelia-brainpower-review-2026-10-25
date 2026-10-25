"""Raten-Datenbanken — Port des DataService (FUNKTIONSANALYSE §7.2).

Format unveraendert uebernommen:
- Baum unter ``data/``; ``.txt`` = Datenbank, ``.rscript`` = Skript.
- ``FUNCTION_*``-Dateien werden ignoriert.
- Zeilen: ``NAME`` oder ``NAME\\tURL`` (TAB-Trenner, RateUtils-Konvention).
- Praefix-Matching: ``findAllBySourceName("HOMEOPATHY")`` laedt ALLE
  Datenbanken, deren Dateiname mit dem Praefix beginnt.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from .analysis import Rate
from .catalog_release import CatalogRelease, CatalogSnapshotError
from .javahashmap import java_hashmap_string_order

_RATE_LINE = re.compile(r"\S")


@dataclass
class RateDatabase:
    name: str  # Dateiname ohne .txt (API-Namen sind ohne Suffix)
    file: Path


CATALOG_BINDING_SCHEME = "ordered-rates-sha256-v1"


def catalog_binding(selector: str, rates: list[Rate], *, release_id: str | None = None) -> dict:
    """Hash der geordneten, tatsächlich analysierten Rate-Werte; kein Datei-Hash."""
    payload = {
        "scheme": CATALOG_BINDING_SCHEME,
        "selector": selector,
        "rates": [
            [rate.name, rate.url, rate.source_name, rate.analysis_key]
            for rate in rates
        ],
    }
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    binding = {
        "scheme": CATALOG_BINDING_SCHEME,
        "selector": selector,
        "rateCount": len(rates),
        "digest": hashlib.sha256(encoded).hexdigest(),
    }
    if release_id is not None:
        binding["releaseId"] = release_id
    return binding


class RateRepository:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)
        self.release = CatalogRelease.load_for_data_dir(self.data_dir)
        self.release_id = self.release.release_id if self.release else None
        self._databases: dict[str, Path] = {}
        self._scripts: dict[str, Path] = {}

    # -- Indizierung ------------------------------------------------------

    @staticmethod
    def _iter_files_like_java(directory: Path):
        """DataService.searchForRateFiles: depth-first File.listFiles order."""
        for path in directory.iterdir():
            if path.is_dir():
                yield from RateRepository._iter_files_like_java(path)
            else:
                yield path

    def refresh(self) -> None:
        """DataService order in legacy mode; pinned manifest order in release mode."""
        self._databases.clear()
        self._scripts.clear()
        if self.release:
            self.release.verify_tree()
            files = (
                self.release.data_dir.joinpath(*entry["path"].split("/"))
                for entry in self.release.entries
            )
        else:
            if not self.data_dir.exists():
                return
            files = self._iter_files_like_java(self.data_dir)
        for path in files:
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

    def read_script(self, name: str) -> str | None:
        key = name if name.endswith(".rscript") else name + ".rscript"
        path = self._scripts.get(key)
        if path is None:
            return None
        if self.release:
            return self.release.read_verified(path).decode("utf-8", errors="replace")
        return path.read_text(encoding="utf-8", errors="replace")

    def find_all_by_source_name(self, source_name: str) -> list[Rate]:
        """DataService.findAllBySourceName including prefix matching."""
        rates: list[Rate] = []
        for file in self._selected_files(source_name):
            if self.release:
                content = self.release.read_verified(file)
                rates.extend(self._parse_lines(file, content.decode("utf-8", errors="replace").splitlines()))
            else:
                rates.extend(self._parse(file))
        return rates

    def _selected_files(self, source_name: str) -> list[Path]:
        if source_name.endswith(".txt"):
            return [self._databases[source_name]] if source_name in self._databases else []
        return [
            path
            for name in java_hashmap_string_order(list(self._databases))
            for path in [self._databases[name]]
            if name.startswith(source_name)
        ]

    def find_all_fresh_by_source_name(self, source_name: str) -> list[Rate]:
        """Stick-Pad: pinned release or conservative double-read of legacy files."""
        if self.release:
            self.refresh()
            files = self._selected_files(source_name)
            rates: list[Rate] = []
            for file in files:
                content = self.release.read_verified(file)
                rates.extend(self._parse_lines(file, content.decode("utf-8", errors="replace").splitlines()))
            self.release.verify_tree()
            return rates
        try:
            snapshot = RateRepository(self.data_dir)
            snapshot.refresh()
            files = snapshot._selected_files(source_name)
            if not files:
                return []
            rates: list[Rate] = []
            digests: list[bytes] = []
            for file in files:
                content = file.read_bytes()
                digests.append(hashlib.sha256(content).digest())
                rates.extend(self._parse_lines(file, content.decode("utf-8", errors="replace").splitlines()))
            for file, digest in zip(files, digests):
                if hashlib.sha256(file.read_bytes()).digest() != digest:
                    raise CatalogSnapshotError("Katalog waehrend des Lesens veraendert")
            current = RateRepository(self.data_dir)
            current.refresh()
            if current._selected_files(source_name) != files:
                raise CatalogSnapshotError("Katalog waehrend des Lesens veraendert")
            return rates
        except OSError as exc:
            raise CatalogSnapshotError("Katalog waehrend des Lesens nicht verfuegbar") from exc

    # -- Parser -----------------------------------------------------------

    @staticmethod
    def _parse(file: Path) -> list[Rate]:
        try:
            lines = file.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return []
        return RateRepository._parse_lines(file, lines)

    @staticmethod
    def _parse_lines(file: Path, lines: list[str]) -> list[Rate]:
        rates: list[Rate] = []
        for line in lines:
            if not line or not line.strip():
                continue
            name, _, url = line.partition("\t")
            rates.append(
                Rate(
                    name=name.strip(),
                    url=url.strip() or None,
                    source_name=file.name,
                    analysis_key=line,
                )
            )
        return rates
