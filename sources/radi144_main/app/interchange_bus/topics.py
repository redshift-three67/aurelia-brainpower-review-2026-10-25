"""R-10/R-11: Topic-Vokabular + erlaubte schema_refs — M-1 §5.

Kuratierter Satz (kein Modul definiert ad-hoc eigene Topics). Spiegelt ME2s
``interchange_bus/topics.py``. Neue schema_refs werden koordiniert aufgenommen
(M-1 §10) — Radi144 published im MVP nicht, daher hier nur die Leseseite.
"""
from __future__ import annotations

from enum import StrEnum


class Topic(StrEnum):
    SCAN_RESULT = "scan_result"
    POST_SCAN_REPORT = "post_scan_report"
    TREND_SNAPSHOT = "trend_snapshot"
    CATALOG_SNAPSHOT = "catalog_snapshot"


ALLOWED_SCHEMA_REFS: dict[Topic, frozenset[str]] = {
    Topic.SCAN_RESULT: frozenset({"me2.interactive_scan_result.v1", "me2.v2_autoscan.v1"}),
    Topic.POST_SCAN_REPORT: frozenset({
        "me2.deutung_report.v1",
        "me2.trend_report.v1",
        "me2.synergy_report.v1",
        "me2.remedy_report.v1",
        "me2.post_scan_reports.v1",
        "me2.harmonization_wizard.v1",
    }),
    Topic.TREND_SNAPSHOT: frozenset({"me2.trend_snapshot.v1", "me2.archive.v1"}),
    Topic.CATALOG_SNAPSHOT: frozenset({
        "me2.catalog_snapshot_store.v1",
        "me2.catalog_snapshot_store_entry.v1",
    }),
}


def is_allowed_schema_ref(topic: Topic | str, schema_ref: str) -> bool:
    try:
        t = Topic(topic) if not isinstance(topic, Topic) else topic
    except ValueError:
        return False
    return schema_ref in ALLOWED_SCHEMA_REFS.get(t, frozenset())


def topic_values() -> tuple[str, ...]:
    return tuple(t.value for t in Topic)