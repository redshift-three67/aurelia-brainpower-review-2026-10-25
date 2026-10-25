# Datenhaltung

Ein Postgres, keine Marketing-„Multi-DB“.

| Schicht | Technik | Inhalt |
|---|---|---|
| OLTP | PostgreSQL 16 | Mandanten, Nutzer, Gruppen, Einwilligungen, Quotas, **AnalysisDraft**, **HarmonizationLane** |
| Zeit | Timescale Hypertables | Timer-Ticks, Telemetrie, Harmonisierungskurven |
| Maße | JSONB, versioniert | Sparse Scores, Draft-Payload |
| Ähnlichkeit | pgvector | Rate-Muster **innerhalb** eines Mandanten |
| Hierarchie | ltree | Rate-Katalog, Gruppen |
| Objekte | MinIO | Verschlüsselte Medien, Key pro Mandant |
| OLAP | DuckDB/Arrow (Lesewarehouse) | Aggregate für Trends/Reports, nie die Akte |

Zwischenablage und Spur: [18-clipboard.md](18-clipboard.md).

## Dimensionen des Würfels

Mandant, Praktiker, Klient, Rate-Achse, Protokollversion, Hardwareprofil, Zeit.

## Pflicht an jeder personenbezogenen Tabelle

`tenant_id`, RLS, wo nötig `encryption_key_id`.
Indizes: `(tenant_id, client_id, time)`, `(tenant_id, kernel, time)`.

Mandanten-Export und -Löschung sind Jobs mit Protokoll.
Enterprise-Isolation hinter derselben API, später.
Draft-TTL-Default: 7 Tage, Archiv-Vorschlag, kein Auto-Delete (U10).
