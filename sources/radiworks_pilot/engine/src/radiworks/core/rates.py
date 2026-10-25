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
_CATALOG_ID = re.compile(r"^catalog-[0-9a-f]{64}$")


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
        self._prefix_selectors_by_id: dict[str, str] = {}
        self._exact_selectors_by_id: dict[str, str] = {}
        self._catalog_id_by_name: dict[str, str] = {}
        self._exact_id_by_filename: dict[str, str] = {}

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
        self._prefix_selectors_by_id.clear()
        self._exact_selectors_by_id.clear()
        self._catalog_id_by_name.clear()
        self._exact_id_by_filename.clear()
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
        for filename in self._databases:
            name = filename[:-4]
            prefix_id = self._opaque_catalog_id("prefix", name)
            exact_id = self._opaque_catalog_id("exact", filename)
            self._prefix_selectors_by_id[prefix_id] = name
            self._exact_selectors_by_id[exact_id] = filename
            self._catalog_id_by_name[name] = prefix_id
            self._exact_id_by_filename[filename] = exact_id

    # -- Abfragen ---------------------------------------------------------

    def database_names(self) -> list[str]:
        """DataService.getDatabaseNames — Namen ohne .txt."""
        return sorted(name[:-4] for name in self._databases)

    @staticmethod
    def _opaque_catalog_id(kind: str, selector: str) -> str:
        value = f"radiworks-catalog-selector-v1\0{kind}\0{selector}".encode("utf-8")
        return "catalog-" + hashlib.sha256(value).hexdigest()

    def catalog_entries(self) -> list[dict[str, str]]:
        entries = []
        for name in self.database_names():
            catalog_id = self._catalog_id_by_name.get(name)
            exact_id = self._exact_id_by_filename.get(name + ".txt")
            if catalog_id is None or exact_id is None:
                continue
            entries.append({
                "id": catalog_id,
                "exactId": exact_id,
                "selector": catalog_id,
                "name": name,
                "label": name,
            })
        return entries

    def exact_id_for_selector(self, selector: str) -> str | None:
        if selector in self._exact_selectors_by_id:
            return selector
        return self._exact_id_by_filename.get(selector)

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
        exact_name = self._exact_selectors_by_id.get(source_name)
        if exact_name is not None:
            return [self._databases[exact_name]]
        prefix_name = self._prefix_selectors_by_id.get(source_name)
        if prefix_name is not None:
            source_name = prefix_name
            return [
                self._databases[name]
                for name in java_hashmap_string_order(list(self._databases))
                if name.startswith(source_name)
            ]
        if _CATALOG_ID.fullmatch(source_name) and source_name not in self._catalog_id_by_name:
            return []
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
