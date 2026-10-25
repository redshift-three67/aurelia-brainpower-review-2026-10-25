# Aurelia – Datenbereiche, Archive und Echtzeit: erweiterter Bestand

Stand: 09.10.2026. Ergänzung zu [Modulbestand und Datenhoheit](AURELIA_MODULDATEN_BESTAND_2026-10-09.md). **Gezielte statische Inventur und Architekturhypothese; kein fertiges Modul-Reasoning, beschlossenes Schema oder Servernachweis.**

Betreibervorgabe: zentrale Datenhoheit; zuerst bestehende Modulabläufe und Speicher erfassen, dann gemeinsam die Struktur entscheiden. Bestehende Funktionen, Algorithmen und Heuristiken bleiben erhalten. Der Erstabgleich unten erfolgte vor Eingang der Explorer-/Thom-Quellen; deren gebundener Bestand und aktive Cloud-Metadaten sind inzwischen ergänzt. Keine Produktdateien, Access-Daten, Modul_Templates-Verträge, Governors-Routen/Registrierungen, Dienste oder laufenden RadiWorks-Instanzen verändert. In diesem lokalen Datenbereichsabgleich keine Nutzerdatensätze gelesen, keine Access-Routinen ausgeführt und keine Remote-Modellaufträge über Governors gestartet; separate spätere Exportprüfungen sind im Referenzbericht abgegrenzt.

## 1. Datenbereiche für die gemeinsame Matrix

Fortsetzung vom selben Tag: [Copen/Bohm/Thom-Referenzprüfung](AURELIA_REFERENZPRUEFUNG_COPEN_BOHM_THOM_2026-10-09.md) und [administrative 2D-/3D-Assetverwaltung](AURELIA_ADMIN_ASSETS_VORMERKUNG_2026-10-09.md). Der ursprüngliche Bestand unten bleibt auf den damaligen Untersuchungsumfang begrenzt. Zusätzlich vorzusehen: versionierte Assets, Koordinatenrahmen, Punkte/Regionen, Texte, Modulzuordnungen, Lizenz-/Freigabestand und gemeinsame Wiederherstellung. Der spätere Creator gehört zur Aurelia-Administration; aktuelle Modulprüfungen haben Vorrang.

| Bereich | Im Ziel separat zu erfassen | Noch festzulegende Grenzen |
|---|---|---|
| Berichte / Berichtsarchiv | Ergebnisstand, Berichtrevision, verwendete Vorlage, Eingabe-/Katalog-/Verfahrensreferenzen, tatsächlich ausgegebenes Dokument | Entwurf gegenüber Veröffentlichung, Rechte, Export, Korrekturen, Aufbewahrung und Löschung |
| Trends / Trendarchiv | Einzelbeobachtungen, Berechnungsregel/Version, Zeitfenster, Datenstand; gespeicherter Trendstand gegenüber laufend berechneter Ansicht | Vergleichbare Kennzahlen/Einheiten, Lücken, Aggregation, Aktualität, Rohdatenaufbewahrung; kein Gleichsetzen unterschiedlicher Modulwerte |
| Klientenbezogene Zwischenablagen | Ausgefüllter Entwurf mit Sichtbarkeit, Herkunft, Klienten-/Fallreferenz soweit zutreffend, Revision und Freigabestatus | System-Clipboard, Browserzustand und dauerhafter Serverentwurf sind verschiedene Dinge; kein automatischer externer Modellversand |
| Vorlagen / Presets | Vorlagentyp, Inhalt, Version, Besitzer/Sichtbarkeit und Referenz auf daraus erzeugte Exemplare | Plattformweite, tenantprivate, nutzerprivate und klientenbezogene Vorlagen; eine Vorlage ist kein bereits ausgeführter Auftrag |
| Harmonisierung / Archiv | Auftrag, Ausführungsversuch, eingefrorener Kontext und Medienstand, Annahme, Start, Pause, Ende, Fehler und Abbruch | Modulverfahren erhalten; bestätigte Ausführung gegenüber angeforderter Ausführung unterscheiden; kein Wiederstart aus einem Archiv allein |
| Trigger / Echtzeit | Regel-/Konfigurationsstand, Ursache, Annahme/Ablehnung, ausgelöster Auftrag; fachliche Ereignisse und Beobachtungen getrennt von UI-Ticks/Telemetrie | Welche Trigger das Modul tatsächlich besitzt, Reihenfolge, Wiederholungen, Deduplizierung, Rechte und Speicherfrequenz |
| Gemeinsame Grundlagen | Mandanten, Nutzer, Modulabos, Klienten/Fälle, Katalogrevisionen, Medien, Berechtigungen, Audit und Wiederherstellung | Genau ein führender Schreibpfad pro Objekt; kein stiller Abgleich mehrerer Originale und keine automatische Personenvereinigung |

Betreiberergänzung: [Modulübergreifende Favoriten, klientenbezogene Trends und optionale Benachrichtigungen](AURELIA_FAVORITEN_TRENDS_TRIGGER_VORMERKUNG_2026-10-09.md). Persönliche Favoriten von automatisch erkannten Kandidaten trennen; gemeinsame Klienten-/Katalogzuordnungen bestätigen und Kennzahl-/Verfahrensherkunft erhalten. Trendarchiv, versionierte Triggerentscheidung und Zustellprotokoll gehören in die gemeinsame Matrix. Mail ist ein später ausdrücklich aktivierter Kanal; heute keine Auswertung oder Zustellung eingerichtet.

Die ergänzende [isolierte UI-Referenzprüfung](AURELIA_REFERENZPRUEFUNG_COPEN_BOHM_THOM_2026-10-09.md) bestätigt den Bedarf an einer unveränderlichen Bindung von Klient, Kontextrevision, Rechenlauf und Worttestergebnis: Die Bohm-Oberfläche kann alte Resultate mit einer neuen Klienten-ID archivieren. Copen hält eine lokale Pause beim erneuten Öffnen nicht durchgängig fest. Dies ergänzt den Lebenszyklusvertrag; Bestandsdaten und die Entscheidungshoheit über das künftige zentrale Schema bleiben erhalten.

Archiv, zusammengefasster Trend und Backup haben unterschiedliche Aufgaben. Ein Dateibericht ist kein Restore-Nachweis; eine Live-Anzeige ist kein dauerhaftes Ereignisarchiv. Unveränderliche Auftragsreferenzen bedeuten keine unbegrenzte Speicherung personenbezogener Inhalte.

## 2. Was die Modulquellen derzeit belegen

**Implementiert** bedeutet hier: gezielt gelesener Schreib-/Lesepfad im Quellcode. Aktiver Serverbetrieb, vollständige Routerabdeckung oder frische Funktionsabnahme sind damit nicht bewiesen. **Metadaten** zeigen Objekt-/Feldnamen, keine aktive Funktion. Morphic-Root und registrierter Worktree bleiben getrennt; kein Baum wurde als autoritativ ausgewählt.

| Bereich | RadiWorks | Radi144 | RadiMorphic | RadiFarben |
|---|---|---|---|---|
| Berichte / Archiv | Fall-/Sitzungs-JSON, persönliche SQLite-Aufträge und Ergebnisse; Fallstatistik aus Sitzungen. Kein umfassendes versioniertes Berichtsarchiv in diesem Abgleich belegt. | Klienten-, Sitzungs-, Artefakt-JSON; Berichte als referenzierte Dateien. Atomic Replace belegt, Aufbewahrung/Restore nicht. | Root: Dateiberichte und JSON-Manifeste/Katalog. Worktree: zusätzliche sichere Dateiöffnungen/IDs und tenantabhängige Wurzeln; nicht jeder Manifest-Schreiber übergibt Kontext. | Metadaten: `frmReporting`, drei Reportobjekte, Logbuch. Aktuelle Berichtberechnung und Archivabläufe offen. |
| Trends / Archiv | Dauerhafte GV-Beobachtungen, je Broadcast höchstens 1.000; History-Antwort höchstens 200 mit Gesamtzahl/Truncation. Watchlist-Historie höchstens 50 in der Antwort. Vollständiges dauerhaftes Resonanz-Ereignisarchiv dadurch nicht bewiesen. | `TREND_SNAPSHOT` im Busvokabular; kein Trendproduzent im untersuchten Pfad. | Root/Worktree: JSON-Trend-Rollup Schema 1 plus HTML/PDF und Artefaktregistrierung; kein Rohdatenarchiv. Worktree-Ausgabewurzel abhängig von Tenant-Konfiguration. | Keine aktive Trendroutine aus aktuellen Metadaten nachgewiesen. |
| Zwischenablagen | Browser kopiert Top-21/Prompt in System-Clipboard; zusätzlich eigenständiger persistenter Prüfdraft. Kein universeller zentraler Klienten-Clipboard-Dienst belegt. | Browserzustand mit Klientendaten in localStorage; aktives Ergebnis kann als JSON kopiert werden. Kein servergebundener Clipboard-Auftrag. | Root: im geprüften Webpfad nicht belegt. Worktree: überschreibbarer Workbench-Entwurf sowie separate Group-Drafts mit Consent-/Retentionfeldern und Windows-DPAPI; nicht jeder Entwurf hat Klienten-/Sitzungsbindung. | Kein aktueller entsprechender Ablauf allein aus Metadaten belegt. |
| Vorlagen / Presets | Fallbezogenes Medienprofil und Layerreferenzen; eingefrorener Präsentationsbeleg pro Broadcast. Kein allgemeiner Vorlagen-Versionsdienst belegt. | Bis 21 Browser-Templates, nach Namen ersetzt, ohne eigene Revision; CLI-Templateformat und Sessionexport besitzen getrennte Formatversionen. | Worktree: Template-IDs/Zeitstempel in `templates.json`, keine eigene Revisionshistorie; Scanprofile/Fingerprints davon getrennt. Root-Webpfad: entsprechender Store nicht belegt. | Metadaten: `tblAufstellVorlagen` mit Benutzer/Auswahl/Beschriftung/Symbol/Schrift/Erfasst; keine Template-Revisionshistorie nachgewiesen. |
| Harmonisierung / Archiv | Dauerhafte Annahme-/Ziel-/Entropie-/Abschluss- und Dynamic-Adjustment-Belege; flüchtige Queue wird beim Neustart nicht automatisch wieder ausgeführt. | Browser steuert Harmonisierungsitems, Timer und Audio im Speicher; API setzt `harmonization_status=not_requested`. Dauerhaftes Harmonisierung-Jobarchiv dort nicht belegt. | Root: JSON-Jobs ohne direkte Client/Session/Tenantbindung in Basisfeldern; Event-JSONL. Worktree: Schema 2, tenant/operator/report, Lease/Owner-Prüfung und Idempotenz; unsichere Wiederherstellung unterbricht, startet nicht automatisch neu. Bereinigung kann Jobs/Events löschen. | Metadaten: `tblBesendungen` mit Aktiv/Adressat/SendetextQuelle/Rate, `frmBesendung`, Radon-Datei-/Bildstrukturen. Aktive Auftragspersistenz und Wiederanlauf offen. |
| Trigger / Echtzeit | Auto-Regelkreis und Dynamic Adjustments mit eigenen Belegen. WebSocket-Replay nur RAM-Puffer mit 256 Ereignissen/Bootkennung und Lückenmeldung. Resonanzzähler im Prozess, browserlokale Anzeigelöschung; GV-Historie davon getrennt. | WebSocket-EMF/Sensorsignale ohne belegte Archivschreiber im Handler. Bus-SQLite-Schema/Consumer-Acks vorhanden, finale Pfadverdrahtung und Publish laut Code nicht abgeschlossen. | In-Memory-Streams gegenüber jobbezogenem JSONL; Worktree `progress_events.py` ausdrücklich nicht in Webjob-Laufzeit verdrahtet. Keine allgemeine dauerhafte Replay-API belegt. | Metadaten: `Radon_Timer`, `Radon_Timer2`, `Radon_Timer3` mit Termin-/Wiederholungsfeldern. Keine aktuelle Timer-/Trigger-Ausführung nachgewiesen. |

Zusätzliche Grenzen:

- RadiWorks meldet Broadcast-Resonanzen im betrachteten Kernel als `source=simulated`. GV-Ziehungen und persönliche Scores sind Softwarewerte, keine hier nachgewiesene gemessene Klientenreaktion. Neue Archive dürfen diese Bedeutung nicht umdeuten.
- RadiWorks-GV-Dokumente besitzen Scope-/Auftrags-/Sitzungsbindungen und getrennte Beobachtungsziehungen. Die Anzeigenlimits sind keine Aussage über vollständige Archivierung aller anderen Signale. Die Resonanzanzeige kann zurückgesetzt werden, ohne GV-Beobachtungen zu löschen.
- Radi144-Template-Schemaversion, Algorithmusrevision und Berichtrevision sind getrennte Eigenschaften. Aus persönlichen Feldern abgeleitete IDs werden nicht ungeprüft zur Plattformidentität.
- Morphic-Worktree ergänzt echte lokale Mechanismen gegenüber Root. Allgemeine Methoden/Schreibpfade sind aber nicht überall gleich geschützt; Registrierung des Worktrees ersetzt keine vollständige Integrationsabnahme. Die vorhandene DPAPI-Bindung ist Windows-nutzerspezifisch und kein bereits portierter Ubuntu-Schlüsselvertrag.
- Radifarben-Begriffe werden nicht automatisch auf RadiWorks-Semantik abgebildet. Eine Access-Timerzeile belegt beispielsweise keine funktionsgleiche Aurelia-Harmonisierungsspur.

## 3. Aurelia und Modul_Templates: Plan gegenüber Implementierung

| Quelle | Belegter Inhalt | Abgrenzung |
|---|---|---|
| Aurelia `docs/05-data.md`, `02-architecture.md` | Zielbild PostgreSQL/Timescale, JSONB, zentrale Objektablage, getrennte Laufzeitdienste | Keine frische Inventur installierter Ubuntu-Dienste. `pgvector` im alten Zielbild ist keine neue Freigabe für Embeddings/semantische KI-Suche. |
| Aurelia `docs/18-clipboard.md` | Draft-Lebenszyklus, CopyGuard/Freigabe, HarmonizationLane, Rollen und Archividee | Ausdrücklich **zur Bestätigung**. Kein verbindlicher universeller Modulablauf und kein Nachweis vollständiger Implementierung. |
| Aurelia `docs/21-timer.md` | Geplante dauerhafte Zustände, WAL, getrennte Kanäle, Checkpoints 500–1.000 ms gegenüber 50-ms-Anzeige | WAL ist keine Uhr. Keine gemessene Echtzeit-/Verlustgarantie; Reset-Lücken und Wiederanlaufpolitik müssen konkret entschieden werden. |
| Aurelia Migrationen/`src/lib/db.ts` | Auth, Tenant/Membership-Struktur; PostgreSQL-Treiber oder flüchtiger PGlite-Fallback | Modularchive/RLS/Aborechte noch kein nachgewiesener Gesamtvertrag; fehlende Produktions-DB darf künftig nicht still in flüchtigen Modus führen. |
| Modul_Templates `standards/API_CONTRACT.md` | Ereignisumschlag, Boot-/Cursor-Reconnect, Replay-Lücken und Fachereignisse | Ereignisformat allein speichert keine Historie. Fähigkeiten je Modul erklären; kein Zwang zu einem RadiWorks-Kernel oder identischer Zahlenbedeutung. |
| Governors-Projektmatrix | Fünf registrierte Projekte, alte Intakebelege; RadiFarben unregistriert | Die neue Datenbereichsmatrix ist zunächst **lokaler Beleg**. Kein frischer Governors-Intake, Gruppenreview, Routingwechsel oder neuer Datenversand. |

## 4. Datenbankvarianten zur späteren Entscheidung

Meine derzeitige Präferenz ist eine **PostgreSQL-Basis innerhalb der freigegebenen Servergrenze**, mit typisierten Fachobjekten, tenantgeschützten Modulbereichen und zentral verwalteten Dateiobjekten. Das ist eine Vergleichsbasis, keine vorweggenommene Strukturentscheidung.

| Variante | Geeignet für | Empfehlung / Voraussetzung |
|---|---|---|
| PostgreSQL, bei Bedarf native Zeitpartitionierung, gezielte Indizes, versionierte JSONB-Payloads | Klienten/Fälle, Rechte, Kataloge, Auftragszustände, Berichte und zunächst Beobachtungen/Trends | Zuerst als synthetische Baseline vergleichen. Keine pauschale Partitionierung kleiner Tabellen; Transaktions-, Tenant- und Restorevertrag zuerst. |
| PostgreSQL plus Timescale | Größere zeitbezogene Reihen, Aufbewahrungsfenster und zeitliche Zusammenfassungen | Optional nach Lastmessung und Prüfung einer konkreten unterstützten Version/Lizenz/Betriebsform. Nicht zur Voraussetzung für alle Module machen. |
| Separater zentral kontrollierter Analysespeicher, etwa ClickHouse; DuckDB/Arrow für begrenzte Auswertungen | Sehr große lesende Aggregationen, wenn die Baseline nachweislich nicht genügt | Späterer Bedarfsschritt; zusätzliche Verzögerung, Betrieb und Löschweitergabe. Keine zweite führende Klienten-/Auftragsdatenbank. |

PostgreSQL unterstützt native Partitionierung; bei partitionierten Tabellen müssen globale Unique-/Primärschlüssel die Partitionierungsspalten berücksichtigen. Deshalb Identität/Deduplizierung nicht erst nach Wahl der Partitionen entwerfen. [PostgreSQL Partitionierung](https://www.postgresql.org/docs/current/ddl-partitioning.html).

JSONB ist sinnvoll für geprüfte modulspezifische Erweiterungen, aber kein Ersatz für Rechte, Identitäten und wichtige relationale Verknüpfungen. Es bewahrt weder die ursprüngliche Textformatierung noch doppelte Objektschlüssel. Unveränderte Rohquellen bei Bedarf separat referenzieren; führende Nullen, Reihenfolge, Dubletten und algorithmisch relevante Dezimalstrings nicht beiläufig normalisieren. [PostgreSQL JSON](https://www.postgresql.org/docs/current/datatype-json.html).

**Timescale-Grenze:** Die konsultierte offizielle Dokumentation zur Anlage kontinuierlicher Aggregate verlangt in diesem Kontext eine zugrunde liegende Hypertable ohne aktive RLS-Policies. Das ist kein pauschales Verbot von Hypertable-RLS, verhindert aber eine ungeprüfte Kombination unserer Mandantenanforderungen mit solchen Aggregaten. **Persönliche Daten nicht durch Abschalten von RLS passend machen.** Zunächst normale tenantgeschützte Summarytabellen mit einem berechtigten, versionierten Aggregationsworker vorsehen; auch dessen Gruppierungs-/Konfliktschlüssel müssen Tenant und erforderliche Sichtbarkeit enthalten. Eignung kontinuierlicher Aggregate erst für die konkrete Version/Konfiguration nachweisen. [Offizielle CAGG-Anlage](https://raw.githubusercontent.com/timescale/docs/latest/use-timescale/continuous-aggregates/create-a-continuous-aggregate.md), [PostgreSQL RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html).

Timescale beschreibt Real-time-Aggregate ab Version 2.13 standardmäßig als deaktiviert. Aktualität und Refreshpolitik müssen bewusst festgelegt werden. Retention mit überlappendem Refresh kann auch Aggregate entfernen; ein Rollup ist kein unverlierbares Archiv. [Continuous Aggregates](https://www.tigerdata.com/docs/learn/continuous-aggregates), [Retention und Aggregate](https://raw.githubusercontent.com/timescale/docs/latest/use-timescale/data-retention/data-retention-with-continuous-aggregates.md).

Ohne gemessene Datenraten, Spitzenlast, Nutzer-/Jobparallelität, Aufbewahrung und zulässige Verzögerung kann keine Variante als performanteste belegt werden. Benötigte Vergleichsdaten: p95/p99 für Schreiben/Lesen, Wiederanlauf, Speicherbedarf, Konflikte, nachträgliche Korrekturen/Löschungen und Tenant-Isolation. Kein Versionsupgrade oder zusätzlicher Dienst wird hier eingerichtet.

## 5. Multidimensional und in Echtzeit – konkrete Bedeutung

Keine neue Universal-Zahlenformel: Beobachtungen können beispielsweise nach Mandant, Klient/Fall, Sitzung, Modul, Auftrag/Versuch, Rate/Katalogrevision, Kontext-/Verfahrensstand und Zeit ausgewertet werden. **Nur zutreffende Referenzen verpflichten.** Nicht jedes Ereignis besitzt eine Rate oder einen Klienten.

Ein neutraler Ereignisrahmen braucht Typ, Schemaversion, Herkunft, Rechtebereich und definierte Referenzen. Ein Stream benennt seine eigene Sequenz und Neustartgrenze; Zeitstempel allein liefern keine globale Reihenfolge. Für zeitliche Werte Aufnahme-/Beobachtungszeit von Empfangs-/Speicherzeit trennen. Fehlende Werte/Lücken explizit führen, nicht als Null oder künstliche Ziehung auffüllen. Berichte und gespeicherte Trends referenzieren ihren verwendeten Datenstand und ihre Berechnungsregel.

| Vorgang | Empfohlene dauerhafte Grundlage | Live-Verhalten |
|---|---|---|
| Auftrag annehmen / Zustand ändern | Zustand plus Fachereignis/Outbox in derselben Transaktion | Annahme-ACK getrennt von Ausführungsbestätigung |
| GV / sonstige Beobachtung | Fachlich definierte Einzelbeobachtung mit Bindung und Quellenbedeutung | Nur tatsächliche neue Beobachtung aktualisiert den Messwert; Anzeige kann öfter zeichnen |
| Fortschrittsanzeige | Definierte Zustände/Checkpoints; gewünschte Telemetrie gesondert | Nicht automatisch jeden 50-ms-Frame als fachlichen Archivdatensatz speichern |
| Trigger auswerten | Regelversion, Ursache, deduplizierte Entscheidung und resultierender Auftrag | Kein unbeschränkter SQL-/Skriptausführungspfad und keine stille neue Heuristik |
| Reconnect / Wiederherstellung | Autorisierten Zustand lesen, Ereignisse gegebenenfalls erneut zustellen | Zustandsrekonstruktion und Nachrichtenzustellung **lösen keine Befehle erneut aus** |

PostgreSQL NOTIFY kann als Wecksignal dienen, ersetzt aber kein dauerhaftes mandantengeschütztes Event-/Outbox-Ledger. Benachrichtigungen sind laut Dokumentation allen DB-Nutzern sichtbar; deshalb keine Klientendaten in solchen Payloads. Zustellung erfolgt bei Commit, gleiche Meldungen können zusammengefasst werden. [PostgreSQL NOTIFY](https://www.postgresql.org/docs/current/sql-notify.html).

Wiederanlaufpolitik bleibt ein eigener Vertrag: verstrichene Uhrzeit, bestätigte Verarbeitungslaufzeit und ausgefallene Verarbeitung unterscheiden. Neustart darf keinen Broadcast heimlich nachholen. Monotone Zeit gilt innerhalb eines Laufzeitkontexts; Boot-/Clock-Gaps dokumentieren. Bei späterem Löschen müssen Ableitungen, Objekte, Replays und Restoreprozesse eine Wiederherstellung gelöschter Inhalte verhindern.

## 6. RadiFarben – Versionierung vor Anpassung

Aktueller lokaler Quellenstand: `C:/Users/Hubert111/Documents/Radifarben/RadiFarben.accdb`, 86.454.272 Bytes, SHA-256 `2b48ce8dec5e0126072e0bc24f07b754b8b64af0651b080d257dcb1b0c8f13bc`. Der neue externe Quellenbeleg bindet Datei und vorhandene reine DAO-Metadaten; er verändert die Access-Datei nicht. Er ist **keine vollständige Quellcodeversionierung, Kopie der ACCDB oder Funktionsabnahme**. Die F:-Gesamtsicherung ist ein eigener früherer Sicherungspunkt.

Aktuelle Metadaten: 49 lokale/fünf verknüpfte Tabellen, 499 lokale Felder, 47 benannte QueryDefs. `tblKlienten.BildRate` ist gegenüber dem historischen Katalog zusätzlich. Inhalte verknüpfter Quellen, aktuelle VBA-/Query-Semantik und aktive Formularpfade bleiben ungeprüft; alte Exportbefunde dürfen nicht auf die geänderte Datei übertragen werden.

Vor einer funktionalen Anpassung: aktuelle Routinen/Abfragen ohne Autoexec/Schreibwirkung charakterisieren, aktive Algorithmen/Formatregeln binden, mit synthetischen Eingaben Referenzausgaben erhalten und dann nur Adapter, zentrale Speicherverträge und gemeinsame UX ergänzen. Jede Rechen-/Parserrevision getrennt versionieren; Bestand erhalten. Der Umfang eines Web-/Linux-Ports wird erst aus diesen Nachweisen bestimmt.

## 7. Optimale Reihenfolge und Abschluss dieses Lesepakets

| Phase | Stand | Nächster Nachweis |
|---|---|---|
| DOM-0 – sechs Datenbereiche | Gezielt über vorhandene lokale Quellen erfasst; geplant/implementiert/Metadaten getrennt | Weitere Repo-Intakes ergänzen, kein Vollständigkeitsversprechen |
| SRC-1 – Quellen | RadiFarben-Datei gebunden; Morphic-Baumunterschied dokumentiert; Explorer/Thom mit Commit und Cloud-Metadaten ergänzt | Autoritativer Morphic-Baum, aktuelle Access-Routinen/Referenzausgaben, aktive Runtime-/Asset-/Lizenzbelege |
| OWN-1 – Lebenszyklen / Hoheit | Vorschläge und Widersprüche dokumentiert | Pro Objekt Schreibzuständigkeit, Sichtbarkeit, Revision, Archiv/Löschung, Restore und Wiederanlauf besprechen |
| DB-1 – Strukturwahl | PostgreSQL-Baseline, Timescale optional, Zusatzanalytics später vorgeschlagen | Module vollständig genug charakterisieren, Lastprofil und konkrete Architekturentscheidung |
| GOV-1 / CONTRACT-1 | Neue Inventur lokal dokumentiert; kein Matrix-Intake durchgeführt | Quellfrische, genehmigte Aufnahmen/Reviews und danach beschlossene Modul_Templates-Verträge |
| DB-2 / MOD-1 | Nicht begonnen | Erst danach synthetische Isolation, Parallelität, Ergebnis-/Formatgleichheit, Wiederherstellung; stufenweise Integration |

Tatsächlich verwendete Helfer: **GPT-6 Luna/max** für Radi144 und beide Morphic-Bäume; **GPT-6 Astra/medium** für unabhängigen Review der Archiv-, Replay-, Tenant-/Timescale-Grenzen. Keine rekursive Delegation. Chatleitung nach Betreibervorgabe GPT-6.1 Sol/high; keine neue Runtime- oder Tokenersparnismessung. Dauerangaben wären vor den unbekannten Quellen nicht belastbar; Qualität bleibt maßgeblich.

## 8. Quellanker und Belege

RadiWorks: `engine/src/radiworks/api/routes.py` (Eventpuffer/Publish/Reconnect), `core/cases.py`, `personal_jobs.py`, `draft.py`, `gv_observations.py`, `watchlist.py`, `broadcast.py`, `broadcast_target.py`, `auto_jobs.py`, `statistics.py`; `webapp/js/views/analyze.js` (System-Clipboard), `statusbar.js`/`broadcast.js` (Resonanzanzeige).

Radi144: `app/api/resonance.py`, `app/models/session_archive.py`, `app/services/session_archive_service.py`, `json_store.py`, `app/interchange_bus/topics.py`, `consumer_store.py`, `user_workflow.js`, `dev_cli.py`.

Morphic Root und Worktree getrennt: `apps/web/reports.py`, `core/compliance/runtime_manifest.py`, `tools/reporting_common.py`, `trend_analyzer.py`, `services/harmonization_worker.py`, `core/realtime_streaming.py`, `core/realtime/event_log.py`; Worktree zusätzlich `apps/web/workbench_runtime.py`, `workbench.py`, `group_drafts.py`, `main.py`, `core/compliance/local_vector_draft_store.py`, `progress_events.py`.

RadiFarben: bestehender rein lesender Beleg `runtime/aurelia-data-inventory-20261009/radifarben-current-schema.json`; keine erneute Datenbanköffnung in dieser Ergänzung. Neue private Vorherkopien/Hashbelege: `runtime/aurelia-data-domains-20261009`. Kein Produkt-Restore/Test oder frischer Ubuntu-Betriebsnachweis durchgeführt. Diese neuen Dokumente sind noch nicht im früheren F:-Gesamtarchiv enthalten.

Ergänzung a–g vom selben Tag: [Administration, systemweite Audiofähigkeit, verlustfreie Layer-/Audioassets, Frequenzreihen und kontrollierte PDF-/Office-/JSON-Importe](AURELIA_ADMIN_MEDIEN_IMPORT_VORMERKUNG_2026-10-09.md). Die minimal implementierte Phase-1-Verwaltung bleibt vom Zielbild für Abos/Therapeuten/Dienste getrennt. Originalbytes, Ableitungen, Asset-/Profilrevisionen, Rechte und Importprovenienz in die gemeinsame Matrix aufnehmen; keine Schemaentscheidung oder Implementierung.

## 9. Aktuelle Ergänzung: gemeinsame Rechte- und Datenbindungsmatrix

Der [Prüfplan mit 22 Fallgruppen](superpowers/plans/2026-10-09-aurelia-isolierte-rechtepruefung.md) hat einen begrenzten P1-Lauf: [363 SQL-Aktionen, 317 erfüllt/46 Zielabweichungen](verification/AURELIA_P1_RECHTE_2026-10-09.md). P2/P3 bleiben offen. Er erweitert den Bestand um aktive Cloud-Strukturbelege; er macht aus offenen Modul-/Plattformzielen keine implementierten Funktionen.

| Datendomäne | Gemeinsame Abnahmefrage | Beleggrenze / Testbezug |
|---|---|---|
| Klient/Fall und Identitätsmapping | Wer darf welchen Klienten in welchem Modul nutzen? Bleiben Quell-IDs getrennt? | P1 SQL-Owner-/NULL-Bezüge geprüft, widersprüchliche Querbezüge angenommen; reale Cloud-Endpunkte und Tenant/Delegation offen, R01–R04/R14–R15 |
| Auftrag, Sitzung, Kontext und Versuch | Gehören Ergebnis, Worttest, Rate, Modell und Medien zu demselben festgehaltenen Stand? | Bohm-Archivfehlzuordnung synthetisch beobachtet; Thom-Jobs ohne Sessionfeld, R05–R08/R17 |
| Verwaltung/Abo/Ressourcen | Mitgliedschaft, Objektzugriff, Modulabo und Workerbefugnis gleichzeitig erfüllt? | Aurelia-Phase-1-Membership ist kein vollständiger Abo-/Delegationsvertrag, R09–R10/R15–R17 |
| Katalog/Vorlage und Frequenzreihe | Private Importe und freigegebene Revisionen mit Herkunft/Rechten getrennt? | Keine automatische Tabellenfamilien-/Formelvereinheitlichung; Frequenzreihen Zielanforderung, R18 |
| Medien, Layer, Audio und 2D/3D | Zugriff, verwendete Revision und Original-/Ableitungs-/Lizenzstand nachvollziehbar? | Thom-öffentliche Fotos vs. Explorer-private Signaturen; keine Objektvollständigkeit geprüft, R11–R12/R21–R22 |
| Berichte/Trends/Favoriten/Clipboard | Sichtbarkeit und Quellen-/Regelversion korrekt, auch modulübergreifend? | Archiv, Live-Ansicht, abgeleiteter Trend und Backup getrennt; R19, keine neue universelle Scoreformel |
| Trigger, Replay und Echtzeit | Rechte, Deduplizierung und Empfänger stimmen; erzeugt Reconnect keinen zweiten Auftrag? | Publikationsmitgliedschaft/Mock-Relay beweisen keine echte Empfangsgrenze, R13/R20 |
| Löschung/Aufbewahrung/Restore | Werden DB, Objekte, Ableitungen und Sperr-/Löschstände gemeinsam berücksichtigt? | Export allein enthält keine Storage-Dateien; R22 erst mit synthetischen Objekten |

Ein eigener normaler Nutzer, ein delegierter Nutzer, ein Tenantadmin und ein Service-Worker sind unterschiedliche Prüfkategorien. Ob und wie Delegation sowie Rechte bei Aboablauf/laufenden Aufträgen gelten, muss vor Zielabnahme ausdrücklich beschlossen werden. Bestehende Quelllogik zuerst charakterisieren, vorgeschlagene Aurelia-Regeln danach getrennt testen. Kein Produktcode, produktiver Rechtebestand oder normativer Templatevertrag geändert.

P1 konkretisiert die Anforderungen an konsistente Auftrag-/Klienten-/Objektbezüge sowie effektive tabellenweite Rechte. Ein erlaubter Hauptdatensatz kann heute einen fachlich unpassenden Unterbezug tragen. RLS-Zeilenschutz ersetzt weder diesen Zusammenhang noch die Begrenzung von TRUNCATE. Keine neue zentrale Datenstruktur oder wirksame Plattformfähigkeit durch diese Charakterisierung.


## 9. Lokale Referenzen vor dem Strukturentscheid, 10.10.2026

[Konsolidierter Phasenplan](superpowers/plans/2026-10-10-aurelia-module-lokale-referenz-und-datenstruktur.md) präzisiert die bisherige Reihenfolge: lokale Ist-Reproduktion mit synthetischen Fällen dient zunächst der Modulcharakterisierung. Sie übernimmt keine historischen Klienten oder laufenden Jobs und ersetzt weder zentrale DB-2-/P3-Verträge noch Integrationsabnahmen. Baselines und Machbarkeit vor jeder jeweiligen Portierung sichern; alle benötigten Auth-/Storage-/Realtime-/Worker-/Assetpfade und externen Abhängigkeiten berücksichtigen.

Sechs Module neben RadiWorks: Radi144, RadiMorphic, RadiFarben, Copen, Bohm und Thom. Copen/Bohm teilen die Explorer-App, Thom ist eine zweite Quellanwendung. Backendbeziehungen bestimmen vor lokaler Dienstaufteilung; ursprüngliche Modulschemata zunächst erhalten. Gemeinsame zentrale Datenhoheit erst nach vollständigerer Workflowmatrix entscheiden, minimalen Aurelia-Kern und normative Modul_Templates vor schreibenden Adaptern abstimmen, danach ein Modul nach dem anderen entwickeln/abnehmen. Archiv-, Trend-, Entwurfs-, Medien-, Generator-, Import-, Verwaltungs-, Lösch- und Restorevorgaben bleiben vollständig als Pflichtdomänen im neuen Plan geführt.
