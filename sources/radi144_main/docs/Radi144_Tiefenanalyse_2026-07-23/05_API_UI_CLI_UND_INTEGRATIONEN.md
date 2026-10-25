# 05 - API, UI, CLI und Integrationen

## 1. FastAPI-Oberfläche

Alle Router werden unter `/api/v1` eingebunden (`main.py:110-113`).

### 1.1 Endpunktinventar

| Gruppe | Endpunkt | Zweck |
|---|---|---|
| Analyse | `POST /analyze-matrix` | Hauptanalyse |
| Analyse | `POST /analyze-sequence` | Fokusfolge, intern Einzelanalysen |
| Analyse | `POST /analyze-group` | Wrapper für Gruppenmodus |
| Analyse | `POST /analyze-geo` | Wrapper für Geomodus |
| DB | `GET /db/list` | listet Referenzdateien samt absoluten Pfaden |
| DB | `POST /db/rank` | zweistufiges Dateiname-/Inhaltsranking |
| DB | `POST /db/scan` | bewertet bis zu 5.000 Einträge |
| Export | `POST /export/pdf` | PDF-Blob und optional serverseitige Datei |
| EMF | `POST /emf/enable` | aktiviert globalen EMF-Zustand |
| EMF | `POST /emf/disable` | deaktiviert globalen EMF-Zustand |
| EMF | `GET /emf/status` | aktueller Status |
| EMF | `GET /emf/profile` | neues Profil |
| EMF | `GET /emf/monitor` | eingebettete HTML-Monitorseite |
| EMF | `WS /emf/ws` | periodische Profilupdates |
| EMF | `WS /emf/client-sensor` | Remote-Audio/GPS/HRV/Gerätedaten |
| Amplifier | `GET /amplifier/list` | Registryliste |
| Amplifier | `POST /amplifier/set/{name}` | setzt globalen Amplifier |
| Amplifier | `POST /amplifier/clear` | löscht globalen Amplifier |
| Amplifier | `POST /amplifier/match` | Empfehlungen |
| Amplifier | `POST /amplifier/add` | Registryerweiterung |
| Clients | `GET /clients/safety/posture` | Safety-Block |
| Clients | `GET /clients` | PII-reduzierte Liste |
| Clients | `GET /clients/{id}/erasure-manifest` | Löschvorschau |
| Clients | `DELETE /clients/{id}` | Löschkaskade |
| Clients | `GET /clients/{id}/audit` | Auditereignisse |

### 1.2 Requestmodell

Positiv:

- Pydantic wird verwendet.
- `iterations` hat ein Minimum von 100.
- Base64-Bilder haben ein 4-MiB-Limit.
- DB-`limit` und `top_n` besitzen Querygrenzen.

Unzureichend:

- `matrix_size` ist beliebiges `int`, nicht `Literal[12,24,36]`.
- `focus` besitzt kein Längenlimit.
- `iterations` besitzt kein Maximum und ist wirkungslos.
- `focus_weight`, `calculation_mode`, `symmetry`, `palette` sind freie Strings.
- Gruppenmitglieder sind freie Dictionaries ohne Mengenlimit.
- mehrere Vektormodi können gleichzeitig gesetzt sein.
- `client_id` und `client_data` können gleichzeitig gesetzt sein.
- Geo-Koordinaten besitzen keine Bereichsprüfung.
- Datei- und Pfadfelder sind nicht sandboxed.

### 1.3 Identitätszuordnung

Bei gleichzeitigem `client_data` und `client_id`:

- `_build_client_data` verwendet `client_data` für die Analyse (`app/api/resonance.py:279-305`).
- `_mirror_api_session` verwendet bevorzugt die Registryidentität aus `client_id` (`:83-102`).

Das Ergebnis von Person/Objekt B kann damit unter Client A archiviert werden. Das ist ein Datenintegritäts- und später ein Berechtigungsproblem.

### 1.4 Responseverluste

Die Engine erzeugt unter anderem:

- `intensity`,
- `bio_info`,
- `used_palette`,
- `hrv_score`,
- `quantum_active`,
- `focus_weight`.

Das API-Responsemodell übernimmt mehrere dieser Felder nicht (`app/api/resonance.py:255-276`; `app/schemas/resonance.py:55-77`). CLI und Browser/API zeigen deshalb unterschiedliche fachliche Resultate.

### 1.5 Fehlerbehandlung

Positiv:

- viele Eingabefehler werden als 400/404/413 abgebildet,
- temporäre Bilder werden bereinigt,
- fehlendes ReportLab ergibt 501.

Problematisch:

- interne Exceptiontexte gehen in HTTP-500-Antworten (`app/api/resonance.py:462-466`),
- DB-Einzelfehler werden übersprungen und Ergebnisse partiell fortgesetzt,
- EMF-Enable bestätigt „enabled“, ohne den tatsächlichen Enginezustand zu prüfen,
- WebSockets senden interne Fehlermeldungen zurück,
- breite `except Exception` erschweren die Diagnose.

## 2. Authentisierung und CORS

### 2.1 HTTP-Gate

Das Gate ist standardmäßig deaktiviert, wenn `API_KEY` leer oder Placeholder ist (`main.py:87-98`). Bei gesetztem Key prüft es alle nicht explizit offenen HTTP-Pfade, obwohl der Kommentar nur `/api/v1/*` nennt.

Folge:

- `/user_workflow.html`, CSS und JavaScript erhalten 401,
- Browser-`fetch` sendet keinen `x-api-key`,
- es gibt keinen konsistenten sicheren UI-Modus.

### 2.2 CORS

Der aktuelle Arbeitsbaum verwendet loopback-only als Default und deaktiviert Credentials bei Wildcard. Das ist gegenüber einem pauschalen `*` positiv. CORS ist jedoch kein Authentisierungsmechanismus; nicht browserbasierte Clients werden dadurch nicht begrenzt.

### 2.3 WebSockets

Die HTTP-Middleware schützt WebSockets nicht. Beide Endpunkte akzeptieren direkt (`app/api/resonance.py:1072-1138`). Es fehlen:

- Authentisierung,
- Rollen-/Mandantenprüfung,
- Origin-Allowlist,
- Payload- und Arraylimits,
- Rate Limits,
- Verbindungsgrenzen,
- Client-/Sessionbindung,
- Bereinigung globaler Sensordaten beim Disconnect.

## 3. Browserworkflow

### 3.1 Technologie und Navigation

Die UI besteht aus einer HTML-, einer CSS- und einer globalen JavaScriptdatei. Sie nutzt:

- zehn DOM-basierte Schritte,
- Inline-Eventhandler,
- keine URL-Routen oder History-API,
- kein Modul-/Buildsystem,
- kein explizites State-Management,
- kein Framework.

Das ist leicht auslieferbar und ohne Frontend-Build nutzbar, erschwert aber Testbarkeit, Isolation und CSP-Härtung.

### 3.2 Ablauf

1. Willkommen
2. Vektortyp/Klient
3. Fokus
4. Konfiguration
5. EMF
6. Analyse
7. Matrix
8. Details
9. Harmonisierung
10. Export

### 3.3 Mehrfachfokus

Die UI nutzt nicht den Sequenzendpunkt, sondern sendet pro Fokus einen Einzelrequest (`user_workflow.js:1030-1060`). Nachteile:

- keine atomare Sequenz,
- mehrere Sessions,
- Teilresultate trotz UI-Fehler,
- kein Batch-/Resume-Modell,
- keine serverseitige Cancel-Kooperation.

### 3.4 XSS-Risiko

Die vorhandene Funktion `escapeHtml` wird nicht konsequent verwendet. Direkte `innerHTML`-Interpolationen betreffen:

- Name, Geburtsort, Fokus, Geo-Label und Pfade (`user_workflow.js:820-862`),
- API-Responsefelder (`:1207-1238`),
- gespeicherte Templatewerte (`:2323-2340`).

Da Templates persistent in LocalStorage liegen, ist persistentes DOM-XSS möglich. Eine restriktive CSP fehlt und Inline-Handler würden eine strikte CSP zusätzlich erschweren.

### 3.5 Datenschutz

Die UI speichert automatisch sensible Eingaben (`user_workflow.js:1370-1403`) und lädt Google Fonts extern (`user_workflow.html:7`). Es fehlen:

- transparente Einwilligung zum lokalen Speichern,
- TTL,
- „alle lokalen Daten löschen“,
- getrennte Datenklassen,
- lokale Verschlüsselung,
- offline ausgelieferte Fonts.

### 3.6 Claims und Safety

Die aktive UI bezeichnet das Produkt als „Naturheilpraxis“, „Heilsame Resonanzmatrix“, „KI-gestützte Resonanzberechnung“ und „personalisierte Frequenz-Harmonisierung“ (`user_workflow.html:14-16`, `:53`). Der API-Safety-Block wird im Browser nicht erkennbar dauerhaft gerendert.

### 3.7 Export

- PDF: Backend-Blob, aber keine Sessionverknüpfung.
- Excel-Button: erzeugt tatsächlich CSV (`user_workflow.js:1569-1601`).
- CSV: Name und Fokus werden ohne robuste Quoting-/Formelneutralisierung geschrieben.
- Audio: WebM, obwohl Kommentare/Bezeichnungen teilweise WAV erwarten.

### 3.8 Accessibility

Erkannte Lücken:

- Navigationselemente und Modals ohne vollständige Semantik/Fokussteuerung,
- Inline-Interaktion ohne durchgängige Tastaturmodelle,
- versteckte Auswahlcontrols,
- keine erkennbare Reduced-Motion-Regel,
- kein dokumentierter Screenreader-/Kontrasttest.

## 4. PowerShell-Workflow

### 4.1 Rolle

`generate_matrix.ps1` ist ein umfangreicher interaktiver Adapter für:

- Klientendaten,
- Fokusverlauf,
- Templates,
- DB-Ranking/Scan,
- Analyseoptionen,
- Start von `dev_cli.py`,
- Harmonisierung.

### 4.2 Positive Aspekte

- nutzt `$PSScriptRoot` für zentrale Pfade,
- Fokus kann robust über UTF-8-Temporärdatei übergeben werden,
- kann Windows-Dateidialoge nutzen,
- unterstützt einen breiten Funktionsumfang.

### 4.3 Kritisches Problem

Argumente werden als Strings mit eingebetteten Anführungszeichen aufgebaut und mit `Invoke-Expression` ausgeführt (`generate_matrix.ps1:999-1034`; weitere Stellen `:420`, `:529`). Eingebettete PowerShell-Metazeichen können die Befehlsstruktur verändern.

### 4.4 Drift

- PowerShell- und Browserdefaults unterscheiden sich.
- Runtime-Metadatenadapter erwartet teilweise `weight`/`quantum_active`, API speichert `focus_weight`/`use_quantum` (`app/services/session_archive_service.py:109-128`).
- Fokus- und Sessiondateien enthalten Klartextdaten.

## 5. Python-CLI

### 5.1 Funktionsumfang

42 CLI-Argumente decken unter anderem ab:

- Einzelklient, Gruppe, Geo, Bild, DB,
- Matrixgröße und Modus,
- HRV, Planetary, EMF, Amplifier, Symmetrie,
- PDF/XLSX/Logs,
- Harmonisierung und Audio,
- Busregister, Poll, ACK und Status.

### 5.2 Positive Aspekte

- CLI beschränkt Modus, Symmetrie und Matrixgröße mit `choices`.
- Fokusdatei ist robuster als lange Shellargumente.
- mehrere Exporte und Sessionarchivierung sind integriert.
- Bus ist opt-in statt automatisch verdrahtet.

### 5.3 Probleme

- viele Pfade basieren auf `os.getcwd()` (`dev_cli.py:118-149`),
- Klarname wird in Ordner- und Lognamen verwendet,
- große Monolithdatei,
- Exporte und Manifest können auseinanderlaufen,
- CPU kann fälschlich als CUDA gekennzeichnet werden,
- Tkinter/Winsound sind Windows-/Desktop-spezifisch,
- Audioakkumulation ist nicht streamingfähig,
- Python- und Browser-Harmonizer divergieren fachlich.

## 6. PDF, XLSX und CSV

### 6.1 API-PDF

Stärken:

- ReportLab-XML-Werte werden escaped,
- Dateiname wird sanitisiert,
- quadratische Matrix wird geprüft,
- Disclaimer wird eingebettet.

Risiken:

- Matrixgröße ist unbegrenzt,
- Client kann beliebigen `output_path` vorgeben,
- vorhandene Datei wird überschrieben,
- Elternverzeichnisse werden angelegt,
- serverseitige Pfade sind nicht auf Exportroot begrenzt.

### 6.2 CLI-Reports

CLI-PDF/XLSX enthalten Identitäts- und Fokusdaten. Für Tabellenwerte fehlt ein konsistenter Schutz gegen Formeln mit führendem `=`, `+`, `-` oder `@`.

## 7. EMF-Integration

Die WebSocketbeschreibung behauptet, Remote-Sensordaten würden in die Kompensation integriert (`app/api/resonance.py:1121-1136`). Der aktuelle Profilcode liest sie jedoch nicht. Das Interface bestätigt somit eine Integration, die fachlich noch nicht stattfindet.

Mehrere Clients schreiben in dasselbe globale Dictionary. Es gibt keine Trennung nach Client oder Session.

## 8. Interchange-Bus

### 8.1 Stärken

- autarker SQLite-Consumer,
- kanonisches JSON und SHA-256,
- Safety-Marker,
- Schema-Referenzprüfung,
- Cursor/ACK,
- WAL und Audit.

### 8.2 Grenzen

- `verify()` ist eine ungeschützte Selbstkonsistenzprüfung, keine Signatur/HMAC (`app/interchange_bus/envelope.py:123-130`).
- Jeder DB-Schreibberechtigte kann Payload und Hash gemeinsam neu erzeugen.
- `content_hash` wird im Consumer nicht separat gegen `payload` geprüft.
- ACL wird serialisiert, aber nicht autorisiert.
- Tabellen-Topic und Envelope-Topic werden nicht sichtbar gegeneinander geprüft.
- ACK und Audit sind getrennte Transaktionen.
- keine Poison-Message-/Quarantänepersistenz.

## 9. Schnittstellen-Gesamtbewertung

Radi144 besitzt mehr Schnittstellen als ein typischer Prototyp, aber keinen einheitlichen Produktvertrag. Die spätere Planung sollte zuerst festlegen:

1. welcher Einstiegspunkt führend ist,
2. welche Funktionen lokal, serverseitig oder experimentell sind,
3. wie Authentisierung und Sessions in UI/API/WebSockets funktionieren,
4. welches kanonische Analyse- und Sessionmodell gilt,
5. welche Exporte offiziell unterstützt werden,
6. welche Funktionen fachlich echt, simuliert oder Mock sind,
7. welche APIs intern bleiben und welche öffentlich stabilisiert werden.
