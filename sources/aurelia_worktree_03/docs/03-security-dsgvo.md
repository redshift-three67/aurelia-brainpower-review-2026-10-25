# Sicherheit und DSGVO

## Datenklassen

| Klasse | Beispiele | Ort |
|---|---|---|
| Öffentlich | Marke, EEAT-Texte, AGB | Edge / diese App |
| Steuerdaten | Mandantennamen, Abo-Stufe, Nutzer-IDs | Control Plane Ubuntu |
| Art. 9 | Zeugen, Sitzungen, Scores, Harmonisierung | Data Plane Ubuntu, Envelope Encryption |

Lovable/US-Cloud hält **keinen** Klartext von Art. 9. Region dort unbelegt.

## Rechtsgrundlagen (geplant)

- Art. 6 Abs. 1 lit. b/f für Konten und Betrieb
- Art. 9 Abs. 2 lit. a (Einwilligung), wo einschlägig lit. h
- Einwilligung widerrufbar, zweckgebunden, dokumentiert
- Auskunft, Export, Löschung als **Jobs**, nicht als E-Mail-Versprechen
- `dataClass` bleibt `synthetic`, bis ein Grant-Modell existiert

Aktuell sind Authentifizierung und Datenbank aktiv, aber ausschließlich für
synthetische Daten. Art.-9-Klartext bleibt gesperrt.

## Ende-zu-Ende, gestuft

Volle E2E, bei der der GPU-Worker nie Klartext sieht, macht Analyse unmöglich.
Deshalb:

1. Transport: TLS 1.3, intern mTLS
2. Ruhe: Envelope Encryption, Tenant-Key, Rotation
3. Verarbeitung: Unwrap nur in RAM des attestierten Workers; kein Swap; kein Payload-Log
4. Nachrichten: MLS (RFC 9420) — Server reicht Ciphertexte
5. D10 / O08: Video, WebRTC, TURN und Aufzeichnung sind vollständig ausgeschlossen; Phase 9 ist gestrichen

## Cache und Wischen (D15)

Marke/JS/Fonts: immutable, long cache. Zeugen/Session:
`Cache-Control: private, no-store`. Kein CDN, kein Service Worker in Phase 0/1.
Wischen: Object-URLs, Cache API, IndexedDB, WebSocket, AudioContext.

## Medien

Die Codec-Familie AVIF/Opus/FLAC/zstd ist eine D11-Empfehlung und bleibt bis
WV06 Wiedervorlage. Fest gesetzt ist: Kompression erfolgt vor Encryption und
Zeugen gelangen niemals in ein öffentliches CDN. Perceptual Hash nur intern.

## CopyGuard

Kein Cloud-LLM über Akten-Copy. Siehe [16-wellbeing.md](16-wellbeing.md).

## TOMs (Minimum)

LUKS, TLS 1.3, RLS, Least Privilege, Patch-Fenster, Sperrkonzept,
Backup-Tests, Step-up für Harmonisierung starten, Emitter-Arming und Zeugen löschen.
