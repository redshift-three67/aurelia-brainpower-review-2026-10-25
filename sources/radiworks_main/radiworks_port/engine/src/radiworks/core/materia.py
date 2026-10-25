"""Materia Medica — Port der Suchebene (FUNKTIONSANALYSE §9).

Original: 1008 Clarke-JSONs, Lucene im RAM (remedyName, remedyAlternativeNames,
body, Kategorie-Felder; StandardAnalyzer, Top 20). Der Port liest dieselben
JSON-Dateien und ersetzt Lucene durch eine gewichtete Token-Suche ohne
externe Abhaengigkeit; ein Wechsel auf SQLite-FTS5 bleibt moeglich, das
Dateiformat ist unverändert.

Korrigierter Original-Defekt: Das Query-Highlighting nutzte replaceAll mit
Roh-Query (Regex-Injection, FUNKTIONSANALYSE §13.1) — hier: escaptes,
wörtliches Highlighting.
"""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

_TOKEN = re.compile(r"[\wæÆœŒ]+", re.UNICODE)


@dataclass
class Remedy:
    remedy_name: str
    remedy_alternative_names: str = ""
    categories: dict[str, list[str]] = field(default_factory=dict)

    def tokens(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for text in [self.remedy_name, self.remedy_alternative_names]:
            for token in _TOKEN.findall(text.lower()):
                counts[token] = counts.get(token, 0) + 3  # Name schlaegt Body
        for symptoms in self.categories.values():
            for symptom in symptoms:
                for token in _TOKEN.findall(symptom.lower()):
                    counts[token] = counts.get(token, 0) + 1
        return counts


class MateriaMedica:
    def __init__(self, clarke_dir: Path) -> None:
        self.clarke_dir = Path(clarke_dir)
        self.remedies: list[Remedy] = []
        self._index: list[dict[str, int]] = []
        self._clinical: dict[str, list[str]] = {}

    def load(self) -> int:
        """Liest alle Clarke-JSONs (Format unveraendert) + Clinical-Index."""
        self.remedies.clear()
        self._index.clear()
        self._clinical: dict[str, list[str]] = {}
        if not self.clarke_dir.exists():
            return 0
        for path in sorted(self.clarke_dir.glob("*.json")):
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            remedy = Remedy(
                remedy_name=raw.get("remedyName", path.stem),
                remedy_alternative_names=raw.get("remedyAlternativeNames", ""),
                categories=raw.get("categories", {}),
            )
            self.remedies.append(remedy)
            self._index.append(remedy.tokens())
        self._build_clinical_index()
        return len(self.remedies)

    def _build_clinical_index(self) -> None:
        """ClarkeMateriaMedica-Äquivalent: Symptom -> Remedies (aus den
        'Clinical'-Kategorien der Korpusdateien, statt einer Merged-Datei)."""
        index: dict[str, list[str]] = {}
        for remedy in self.remedies:
            for symptom in remedy.categories.get("Clinical", []):
                index.setdefault(symptom, []).append(remedy.remedy_name)
        self._clinical = index

    def load_merged_clinical_index(self, path: Path) -> int:
        """Original-Quelle der Wahrheit: data/radionics/HOMEOPATHY/
        clarkeMateriaMedica.json (AnalysisService lädt genau diese Datei).
        Format: {"clinicalSymptoms": [{"symptom": str, "remedies": [str]}]}.
        Überschreibt den generierten Index, wenn die Datei existiert."""
        try:
            raw = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return 0
        entries = raw.get("clinicalSymptoms") or []
        index: dict[str, list[str]] = {}
        for entry in entries:
            symptom = entry.get("symptom")
            remedies = entry.get("remedies") or []
            if symptom and remedies:
                index[symptom] = remedies
        if index:
            self._clinical = index
        return len(index)

    def compare_clarke(self, name_or_rate: str, result_names: list[str]) -> dict:
        """Port von AnalysisService.analyzeClarke (Berechnungsteil).

        clinical: Symptome der Ziel-Remedy; shared: Symptom -> Anzahl der
        ERGEBNIS-Raten, die es teilen; others: je Ergebnis-Rate die mit der
        Ziel-Remedy geteilten Symptome (grün im Original-Report) und deren
        übrige Symptome (dunkel im Original-Report).
        """
        target = name_or_rate.strip().lower()
        clinical = sorted(
            symptom for symptom, remedies in self._clinical.items()
            if any(r.lower() == target for r in remedies)
        )
        shared: dict[str, int] = {}
        others: dict[str, dict[str, list[str]]] = {}
        for other in result_names:
            other_clean = (other or "").strip()
            if not other_clean or other_clean.lower() == target:
                continue
            shared_symptoms: list[str] = []
            for symptom, remedies in self._clinical.items():
                names_lower = [r.lower() for r in remedies]
                if symptom in clinical and any(r.lower() == other_clean.lower() for r in names_lower):
                    shared_symptoms.append(symptom)
                    shared[symptom] = shared.get(symptom, 0) + 1
            if shared_symptoms:
                others[other_clean] = {"shared": shared_symptoms}
        ranked = sorted(shared.items(), key=lambda pair: -pair[1])[:20]
        return {
            "rate": name_or_rate,
            "clinical": clinical,
            "sharedCounts": [{"symptom": s, "count": c} for s, c in ranked],
            "others": others,
        }

    def search(self, query: str, field: str | None = None, limit: int = 20) -> list[dict]:
        """MateriaMedicaSearchEngine.searchIndex — Top-N mit gewichteten Treffern."""
        terms = [t.lower() for t in _TOKEN.findall(query or "")]
        if not terms:
            return []
        scored: list[tuple[float, Remedy]] = []
        for remedy, tokens in zip(self.remedies, self._index):
            if field and field not in ("body", "remedyName", "remedyAlternativeNames"):
                hits = sum(1 for s in remedy.categories.get(field, []) if any(t in s.lower() for t in terms))
                score = float(hits)
            else:
                score = float(sum(tokens.get(t, 0) for t in terms))
            if score > 0:
                scored.append((score, remedy))
        scored.sort(key=lambda pair: -pair[0])
        return [
            {
                "remedyName": self._highlight(remedy.remedy_name, terms),
                "remedyAlternativeNames": remedy.remedy_alternative_names,
                "score": score,
                "clinical": [
                    self._highlight(s, terms)
                    for s in remedy.categories.get("Clinical", [])[:6]
                ],
            }
            for score, remedy in scored[:limit]
        ]

    @staticmethod
    def _highlight(text: str, terms: list[str]) -> str:
        """Wörtliches, escaptes Highlighting (ersetzt die replaceAll-Injektion)."""
        escaped = html.escape(text)
        for term in sorted(terms, key=len, reverse=True):
            pattern = re.compile(re.escape(html.escape(term)), re.IGNORECASE)
            escaped = pattern.sub(lambda m: f"<b>{m.group(0)}</b>", escaped, count=1)
        return escaped
