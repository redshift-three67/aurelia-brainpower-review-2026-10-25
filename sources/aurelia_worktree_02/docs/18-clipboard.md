# Zwischenablage und Harmonisierungsspur (D18, gesetzt)

Module tauschen **Artefakte**, nicht Seiteneffekte.

## AnalysisDraft

Felder mindestens: `id`, `tenant_id`, `client_id`, `practitioner_id`,
`source_kernel`, `source_run_id`, `payload` (JSONB), `copyguard_digest`,
`client_editable_fields`, `status`, Zeitstempel.

Status: `draft` → `client_review` → `ready` → `promoted` | `discarded`.

CopyGuard bei jedem sichtbaren Speichern und vor Promote.
Rolle `client` sieht nur `client_editable_fields` (C12). Kein Kernel-Wechsel
durch Klient. Promote ist Praktiker-Akt (später Step-up, D08).

TTL-Default (U10): 7 Tage, dann Archiv-Vorschlag, **kein** Auto-Delete.

## HarmonizationLane

Einziger Eingang: Promote aus einem Draft. Kein stiller Copy.

`queued → armed → running ⇄ paused → stopped → archived | deleted`

Zeitquelle: `aurelia-timerd` (chrony + monotonic). Browser-`setInterval` ist
keine Uhr. Start/Pause/Stop/Archiv/Löschen = autorisierter Command + ACK
über den WebSocket-Fachkanal (C08).

Parallel: mehrere Spuren je Mandant bis Quota (U03). Emitter bleibt max. 1 (D14).

## WebSocket-Events (skizziert)

`analysis.progress` · `clipboard.updated` · `harm.tick` · `harm.state` ·
`harm.command` → `harm.ack`

Kein Zeugenklartext auf dem Socket. Reconnect an letzter Event-ID.
