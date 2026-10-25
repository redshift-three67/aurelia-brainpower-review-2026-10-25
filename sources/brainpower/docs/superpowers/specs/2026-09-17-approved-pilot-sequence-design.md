# S1 — Begrenzte genehmigte Pilot-Prüffolge

Status 17.09.2026: S1a/S1b/S1c abgenommen. Gesamtsuite 536 Tests: 534 bestanden und zwei ausgelassen; HTTP/Worker, Browser, Syntax/Vertrag und Hermes-Nullwerkzeugprobe geprüft. Grundlage: Betreiberzustimmung zur empfohlenen Fortsetzung und zu unveränderten Freigabegrenzen. Keine echten Produkt- oder Modellaufträge aus dieser Implementierungsabnahme.

## Entscheidung und Umfang

Erste feste Folge: vorhandener abgeschlossener `scope_patch` mit versiegeltem Arbeitsbereich → `stage_test` einschließlich bestehendem unabhängigem Nachreview → `pilot_assess` → terminaler Halt vor Übernahme.

Dies ist eine Vorbereitungsfolge innerhalb eines ausgewählten Änderungsschritts, noch keine allgemeine Ausführung abhängiger Planschritte. Patch-Erzeugung bleibt ein separater ausdrücklich gestarteter Auftrag. `stage_test` erzeugt keinen eigenständigen `plan_test`-Schrittabschluss.

| Alternative | Bewertung |
|---|---|
| Bestehenden Vorschlag testen und Nachweise prüfen | Gewählt: zwei bekannte Ausführungswege, kein Quellenübergang und keine Zielschreibrechte. |
| Patch-Erzeugung, Rückfragen und Prüfungen gemeinsam steuern | Spätere Erweiterung: zusätzliche Warte-, Egress- und Wiederaufnahmezustände. |
| Allgemeine Planfolge einschließlich Übernahme ausführen | Jetzt ausgeschlossen: würde Adapter- und Quellenübergangsgrenzen über das geprüfte Pilotmodell hinaus erweitern. |

## Feste Freigabegrenzen

1. Neue Vorschau ist lokale Prüfung, keine Versand- oder Ausführungsfreigabe.
2. Expliziter Start bestätigt genau das angezeigte Profil und seinen gebundenen Vorschlag. Die UI nennt den Modellversand für den Nachreview; vorhandene Projekt-/Vault-Egressfreigaben bleiben zusätzlich erforderlich.
3. Nur ein aktiver, unabhängiger, ausdrücklich erlaubter Pilot, ausgewählter `change`-Schritt ohne Vorgänger. Historische fünf Produkte, Gruppen, archivierte Projekte und überlappende Wurzeln bleiben ausgeschlossen.
4. Ein Start erlaubt höchstens einen `stage_test` und bei frischem Erfolg genau einen `pilot_assess`. Keine Wiederholung, Alternativmodelle, automatische Reparaturplanung oder neuen Kandidaten.
5. Ende bei bestandenem Nachweis: `awaiting_transfer_decision`, terminal und ohne reservierten Worker. Das ist keine Übernahmefreigabe und kein fachlicher Planabschluss.
6. `pilot_prepare`, `pilot_apply`, `pilot_verify`, `pilot_complete`, `pilot_transition`, `plan_test`, fachlicher Reviewabschluss und Rollback bleiben separate bestehende Bedienwege. Die Folge ruft keinen davon auf.
7. Medium bleibt unverändert; vorhandener Supervisor/Transport werden gebunden. RH-1 bleibt zurückgestellt. Automatische Hintergrundreviews werden weder aktiviert noch für die Folge benötigt.

## Vorschau und Bindung

Geschützte APIs:

- `POST /api/sequences/preview`: exakt `{stage_job_id}`. Keine neue Job-/Freigabe-/Sequenzzeile; lokale Beobachtungscaches dürfen durch frische Prüfung aktualisiert werden.
- `POST /api/sequences/start`: exakt `{stage_job_id, binding_hash, note}`, nichtleere Begründung höchstens 2000 Zeichen. Kein vom Client gelieferter Befehl, Modellname oder Ablaufgraph.
- `POST /api/sequences/cancel`: exakt `{sequence_id}`. Abbruch ist journalisiert und betrifft nur zugehörige eigene Aufträge.

Vorschau liefert entweder `eligible=false` mit konkretem Sperrgrund oder das Profil `pilot_test_assess_v1` und einen SHA-256 der kanonischen Bindung. Die Bindung enthält Profil-/Implementierungsidentität, Vorschlagsauftrag, Stage-ID/Manifesthash, Kandidat/Schritt, aktuelle Auswahl-ID, Quellenhash, registrierte Wurzel/Dateisystemidentität, aktuelle Pilot-/Egressregeln, Testadapteridentität, Supervisor/Transport/Medium sowie die ID des zuletzt vorhandenen Staging-Tests (oder null). Keine Zugangsdaten in Hashmaterial, Berichten oder Logs.

Vorschau verifiziert aktuelle Original- und Stagingdateien. Start rekonstruiert diese Bindung serverseitig; jede Abweichung zum angezeigten Hash verhindert den Start. Dieselben fachlichen Prüfungen gelten vor Ausführung und am Übergang zum zweiten Teil. Ein Snapshot ist keine atomare Dateisystemsicherung.

Die Vorstart-Referenz auf den letzten Test wird nach eigener Testanlage gezielt durch die journalisierte eigene Test-ID ersetzt. Sie darf nicht ungeprüft mit der alten Vorstart-ID verglichen oder durch einen fremden Versuch ersetzt werden.

## Speicherung und einzelner Worker

Separate Sequenzdatensätze plus append-only Ereignisse und Verknüpfungen zu gewöhnlichen Jobs sind implementiert. Die Folge selbst ist kein zusätzlich laufender Parent-Job: `Store.create_job` erlaubt nur einen aktiven Job, und ein naiver Parent würde seine Kinder sperren.

- Start speichert gebundene Zustimmung, Sequenzreservierung und ersten gewöhnlichen `stage_test` in einer SQLite-Transaktion.
- Ein aktiver Sequenzlauf reserviert den einen Ausführungsplatz auch zwischen Kindern. Andere Jobstarts, automatische Reviews und die Wiederaufnahme fremder Rückfragen müssen den belegten Platz respektieren. Beobachtung und Abbruch bleiben möglich.
- Nur die interne Koordination darf den exakt erwarteten Kindauftrag mit passender Sequenzreferenz anlegen. Kein öffentlicher Umgehungsschalter für die Busy-Prüfung.
- Nach frischem erfolgreichem Test werden dessen terminaler Zustand und der höchstens einmal erzeugte Folgeauftrag atomar festgeschrieben. Bestehende Ergebnisfelder und `action='stage_test'` bleiben erhalten; `require_latest_stage_test` und Übernahmeprüfungen erkennen den Beleg weiterhin.
- Abbruchentscheidung und Übergang verwenden dieselbe Sperr-/Transaktionsordnung. Ein bereits eingereihtes Kind wird ebenfalls abgebrochen; vor seiner Ausführung wird erneut geprüft.
- Bei bereits laufendem Kind bleibt der aktive Zustand mit `cancel_requested=true` reserviert, bis dessen Abschluss den Abbruch bestätigt. Erst dann ist die Folge terminal; ein Nachfolger wird nicht mehr angelegt. Das Speicherjournal signalisiert selbst keinen Prozessabbruch; diese Aufgabe übernimmt die spätere Worker-Anbindung.
- Pro `stage_job_id` höchstens eine Sequenzaktivierung, auch nach Fehler/Abbruch/Unterbrechung. Identische Startanfragen mit gleicher Bindung und Begründung liefern den vorhandenen Lauf und erzeugen keine neuen Jobs; abweichende Wiederverwendung wird als Konflikt abgewiesen. Ein erneuter Sequenzversuch benötigt einen neuen ausdrücklich erstellten Vorschlag. Manuelle Einzelprüfungen bleiben eigenständige Bedienwege; das ist kein neues globales Testbudget.
- Bei Neustart werden aktive Sequenzen und ihre nicht abgeschlossenen Kinder als unterbrochen gekennzeichnet. Keine Rekonstruktion der Queue aus alten Freigaben, keine erneuten Modellaufrufe und keine automatische Fortsetzung.

Zustände: `testing` → `assessing` → `awaiting_transfer_decision`. Von aktiven Zuständen sind außerdem `blocked`, `failed`, `cancelled`, `interrupted` terminal erreichbar. `blocked` bedeutet unbrauchbare/überholte Voraussetzungen; `failed` einen gescheiterten Test, Review oder technischen Auftrag. Historische Erfolge bleiben datierte Beobachtungen.

## Haltebedingungen

| Bedingung | Verhalten |
|---|---|
| Vorschau veraltet, neue Auswahl oder andere Pilot-/Versandfreigabe | Start ablehnen bzw. aktive Folge blockieren; keine stillschweigende Neubindung. |
| Test fehlgeschlagen, leer, nur übersprungen oder Nachreview unvollständig | Testbericht erhalten; keine Nachweisprüfung automatisch starten. |
| Test meldet Erfolg, Belege/Dateien/Adapter sind nicht mehr aktuell | Blockieren; gespeicherter Erfolg wird nicht als aktuelle Freigabe ausgelegt. |
| Nachweisauftrag completed, aber `evidence_usable` nicht exakt true | Folge blockieren; completed allein ist kein positiver Nachweis. |
| Abbruch, Dienstneustart, verlorene Ausführung oder Zustandskonflikt | Terminal halten; kein Replay und keine automatische Kompensation. |
| Nachweis erfolgreich | Vor jeder Übernahmeentscheidung halten; vorhandene gesonderte Bestätigungen bleiben nötig. |

## Umsetzungsschnitt und Abnahmekriterien

Zuerst S1a: ausschließlich Vorschau, Bindungsvertrag und Tests. Danach S1b: persistente Reservierung, einmalige Kindanlage, Abbruch/Neustart. Erst S1c verbindet die tatsächlichen Adapter und ergänzt die ausdrücklich gestartete UI-Folge.

Abnahme muss insbesondere nachweisen: Quellen-/Stagingdrift; identische neue Auswahl mit neuer ID; Rücknahme der Pilot-/Egressfreigabe; Profil-/Adapter-/Routingdrift; fremde Origin/fehlendes CSRF; Doppelklick/konkurrierender Start; Abbruch vor und während beider Teile; Neustart an jeder Übergangsgrenze; unverändert jüngster Testbeleg; kein Nachfolgemodell bei gescheiterten Voraussetzungen; kein Übernahmevorschlag/keine Zieländerung/keine Abschlussfreigabe. Reale temporäre Dateien und Tests, Modellantworten simuliert. Browser prüft Versandhinweis, Halte-/Sperrgründe und historischen Zustand nach Neuladen.

Keine Behauptung über reale Modellqualität, allgemeine Produktadapter oder saubere Windows-Erstinstallation aus diesen Prüfungen. Gesamtabnahme und anschließend SMB/Backup/Restore bleiben in der bestehenden Reihenfolge.
