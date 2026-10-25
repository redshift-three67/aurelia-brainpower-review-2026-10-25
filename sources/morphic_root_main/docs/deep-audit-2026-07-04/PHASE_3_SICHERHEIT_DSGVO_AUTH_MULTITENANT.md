# Phase 3 - Sicherheit, DSGVO, Auth Und Multitenant

## Kurzfazit

Die Codebasis besitzt einige reale Schutzmechanismen, aber kein produktionsreifes Sicherheits- oder Multitenant-Modell.
Der Sicherheitszustand ist fuer lokale Einplatz-Nutzung nachvollziehbar, fuer geteilte oder netzwerkseitig exponierte Nutzung jedoch deutlich unzureichend.

## 1. Tatsaechliches Sicherheitsmodell

### Vorhandene Schutzmechanismen

| Kontrolle | Evidenz | Bewertung |
| --- | --- | --- |
| Optionaler API-Key ueber `X-API-Key` | `apps/web/security.py:24-52` | vorhanden, aber default-off |
| In-Memory Rate Limiting pro IP | `apps/web/security.py:26-82` | vorhanden, aber lokal und fluechtig |
| HTML-Sanitizing fuer Report-Preview | `apps/web/reports.py:56-175`, `531-555` | sinnvoll |
| Root-Containment bei Report-Dateien | `apps/web/reports.py:177-183`, `317-341` | sinnvoll |
| Safe-View fuer Privacy-Clientliste | `core/compliance/runtime_manifest.py:134-143` | sinnvoll |
| Gated Erasure plus Audit | `core/compliance/runtime_manifest.py:239-345` | vorhanden |

### Fehlende oder schwache Grundkontrollen

| Thema | Evidenz | Bewertung |
| --- | --- | --- |
| Pflicht-Authentifizierung | `apps/web/security.py:32-45` | fehlt |
| Rollen/Autorisierung | kein Rollenmodell in `apps/web/*` oder `core/compliance/*` | fehlt |
| Besitzpruefung fuer Jobs/Reports | `apps/web/main.py:311-415` | fehlt |
| Security Header | keine Header-Setzung in `apps/web/main.py` ausser No-Cache | fehlt |
| CSP/HSTS/XFO/XCTO | nicht gesetzt | fehlt |
| persistente oder verteilte Rate-Limits | nur In-Memory | schwach |
| WebSocket-Origin-/Auth-Schutz | `apps/web/scan_live.py`, `apps/web/emf.py` | schwach |

## 2. Authentifizierung und Autorisierung

### Reale Funktionsweise

Die aktuelle Web-App setzt auf eine FastAPI-Dependency `verify_api_key()`.

- `apps/web/security.py:37-52`

Logik:

1. Wenn `MORPHIC_API_KEY` gesetzt ist, wird `X-API-Key` erzwungen.
2. Wenn `MORPHIC_API_KEY` nicht gesetzt ist, laeuft die App ohne Auth.

### Praktische Konsequenz

Der lokale Default ist Authentifizierung aus.
Das ist nicht nur theoretisch, sondern durch die Tests implizit bestaetigt.

- `tests/test_web_shell.py:397-519`
- `tests/test_web_shell.py:603-690`

Diese Tests rufen geschuetzte POST-Endpunkte ohne API-Key erfolgreich auf.

### Geschuetzte Endpunkte

- `POST /api/scan/preview` - `apps/web/main.py:380-387`
- `POST /api/scan/jobs` - `apps/web/main.py:389-405`
- `POST /api/harmonization/jobs` - `apps/web/main.py:337-357`
- `POST /api/harmonization/jobs/{job_id}/stop` - `apps/web/main.py:368-378`
- `POST /api/analyze` - `apps/web/analyze.py:16-73`

### Ungeschuetzte Endpunkte mit fachlicher Relevanz

- `GET /api/privacy/clients` - `apps/web/main.py:305-309`
- `GET /api/reports` - `apps/web/main.py:311-313`
- `GET /api/reports/{report_id}/preview` - `apps/web/main.py:315-320`
- `GET /api/reports/{report_id}/file` - `apps/web/main.py:322-335`
- `GET /api/scan/jobs/{job_id}` - `apps/web/main.py:406-411`
- `GET /api/scan/jobs/{job_id}/results` - `apps/web/main.py:413-553`
- `GET /api/harmonization/jobs/{job_id}` - `apps/web/main.py:359-366`

### Autorisierungslage

Es gibt kein Rollenmodell, keine Objektberechtigungen und keine Bindung eines Jobs oder Reports an einen Operator.
Wer eine `job_id` oder `report_id` kennt, kann den jeweiligen Pfad abfragen.

## 3. Multitenant-/Mandantenfaehigkeit

## Aktueller Befund

Es existiert kein echtes Multitenant-System.

### Was vorhanden ist

- `client_id` im Runtime-Manifest
- `session_id` im Runtime-Manifest
- `job_id` fuer Scan- und Harmonisierungsjobs
- Client-/Session-Hierarchien im Report-Dateisystem

### Was fehlt

- Tenant-Entitaet
- Benutzerkonto oder Operator-Entitaet
- Rollen/Scopes
- Isolation pro Organisation oder Mandant
- Ownership-Check bei Read/Write-Operationen
- tenant-spezifische Verschluesselung oder Schluesselverwaltung

### Technischer Schluss

Das aktuelle System ist client- und sessionsortiert, aber nicht mandantenfaehig.
Es ist daher genauer als "single-operator local system mit klientenbezogenen IDs" zu beschreiben, nicht als Multitenant-Architektur.

## 4. DSGVO-nahe Funktionen im Code

### Vorhandene Funktionen

| Funktion | Evidenz | Bewertung |
| --- | --- | --- |
| stabile pseudonyme `client_id` | `core/compliance/runtime_manifest.py:38-50` | gut |
| Safe-View ohne Klartextnamen | `core/compliance/runtime_manifest.py:134-143` | gut |
| Session- und Artefaktregistrierung | `core/compliance/runtime_manifest.py:145-220` | gut |
| Audit-Log | `core/compliance/runtime_manifest.py:81-105` | vorhanden |
| Erasure-Manifest | `core/compliance/runtime_manifest.py:239-268` | vorhanden |
| Loeschkaskade inklusive Datei-Loeschung | `core/compliance/runtime_manifest.py:270-345` | vorhanden |
| CLI fuer Privacy-Operationen | `apps/cli/commands/privacy.py` | vorhanden |
| Consent-Felder in Web-Contracts | `apps/web/contracts.py:22-23`, `97-102` | vorhanden |

### Technische Luecken

| Thema | Evidenz | Problem |
| --- | --- | --- |
| Consent wird nicht persistiert | keine Speicherung in `runtime_manifest.py` | Nachweisfaehigkeit schwach |
| Runtime-Manifest speichert Klartext-PII | `runtime_manifest.py:115-123` | Datenminimierung nur teilweise |
| Fokus und Config werden pro Session gespeichert | `runtime_manifest.py:161-168` | semantisch sensible Zusatzdaten |
| Audit-Actor ist immer `system` | `runtime_manifest.py:92-101` | keine Benutzerzuschreibung |
| Erasure hat Default-Fallback-Token | `DEFAULT_ERASURE_GATE_TOKEN`, `runtime_manifest.py:12`, `271-282` | Gate schwach |
| keine automatische Retention | kein Purge in `runtime_manifest.py` | Speicherbegrenzung fehlt |
| keine Web-DSAR-Endpunkte | nur CLI | operative Luecke |

## 5. Privacy-Widerspruch zwischen Safe-View und Report-Katalog

### Positive Seite

Die Privacy-Clientliste liefert pseudonyme IDs und entfernt Klartext-Personendaten.

- `apps/web/main.py:305-309`
- `tests/test_web_shell.py:375-395`
- `tests/test_runtime_privacy_manifest.py:11-33`

### Negative Seite

Der Web-Report-Katalog gruppiert weiterhin nach Klartext-Client-Slugs aus Name, Geburtsdatum und Geburtsort.

- `apps/web/reports.py:430-492`
- `tests/test_web_shell.py:525-600`

Beispiel aus den Tests:

- `client_id == "Mustermann_Klaus_09041966_Augsburg"`
- Label `"Mustermann Klaus 09041966 Augsburg"`

### Konsequenz

Die Anwendung besitzt gleichzeitig:

1. eine gute pseudonymisierte Client-Safe-View,
2. und einen historisierten Reportzugriff, der diese Pseudonymisierung wieder unterlaeuft.

## 6. CORS, Header und Netzwerkhaerte

### Aktuelle Web-App

`apps/web/main.py:181-188` konfiguriert:

- `allow_origins=["*"]`
- `allow_credentials=True`
- `allow_methods=["*"]`
- `allow_headers=["*"]`

Zusammen mit optionaler Auth ist das fuer eine ernsthafte Netzexponierung zu weit.

### Legacy-Web-App

`web_app.py:48-55` war restriktiver und loopback-begrenzt.
Die neue App ist in dieser Hinsicht permissiver geworden.

### Fehlende Sicherheitsheader

Es wurden in der aktuellen App keine Setzungen fuer diese Header gefunden:

- `Content-Security-Policy`
- `X-Content-Type-Options`
- `X-Frame-Options`
- `Strict-Transport-Security`
- `Cross-Origin-Opener-Policy`
- `Cross-Origin-Resource-Policy`

Gemessen an web.dev-Sicherheitsleitlinien fuer sensible Webanwendungen ist das ein klarer Nachteil.

## 7. DSGVO-Readiness als technische Matrix

Hinweis: Das ist keine Rechtsberatung, sondern eine technische Reifegradlesung.

| Bereich | Technischer Stand | Bewertung |
| --- | --- | --- |
| Datenminimierung | Safe-View vorhanden, aber Manifest und Reports halten Klartext-PII | teilweise |
| Zweckbindung/Transparenz | Consent-Felder vorhanden, aber keine echte Nachweis-/Policy-Schicht | schwach |
| Integritaet/Vertraulichkeit | lokale Architektur, aber kaum Web-Haertung | schwach bis mittel |
| Auskunft/Audit | Audit-Log und Client-Audit vorhanden | mittel |
| Loeschung | CLI-Loeschkaskade real vorhanden | mittel bis gut |
| Speicherbegrenzung | keine automatische Retention | schwach |
| Privacy by Design | punktuell sichtbar, aber inkonsistent | teilweise |
| Verantwortlichkeit/Nachweis | kein Operator-Kontext | schwach |

## 8. Schwerste Risiken

### Hoch

1. Kein echtes Auth-/Autorisierungsmodell fuer Reports, Jobstatus und historische Daten.
2. Report-Katalog exponiert PII-nahe Client-Slugs im Web.
3. API-Key ist opt-in statt default-on.
4. Weite CORS-Konfiguration ohne komplementaere starke Schutzschicht.

### Mittel

1. Runtime-Manifest speichert Klartext-PII, Fokus, Config und Artefaktpfade.
2. Consent wird technisch erzwungen, aber nicht revisionssicher gespeichert.
3. Erasure ist gated, aber mit hart kodiertem Fallback-Token.
4. Audit-Log kennt keine menschlichen Akteure.

### Niedrig bis Mittel

1. Keine Security Header.
2. Keine WebSocket-Haertung.
3. Keine sichtbare Trennung zwischen lokaler Einzelnutzung und netzwerkfaehigem Betriebsmodus.

## 9. Sicherheits- und Privacy-Schlussfolgerung

Technisch betrachtet ist das System derzeit am glaubwuerdigsten als lokal betriebene Experten-Workstation mit Privacy-Hilfsfunktionen beschreibbar.
Sobald mehrere Operatoren, mehrere Mandanten oder ein echtes Netzwerk-/Remote-Szenario ins Spiel kommen, reicht die vorhandene Sicherheits- und DSGVO-Struktur nicht aus.
