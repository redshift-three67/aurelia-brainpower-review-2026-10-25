# Verifikation Governor 0.3

Stand: 12.09.2026. Dieser Bericht trennt isolierte Regressionstests, beobachtete Browserbedienung, echte Modellaufrufe an einer synthetischen Fixture und den unveränderten Bestand der fünf Produkte. Funktionsumfang und offene Grenzen stehen in [GOVERNOR_0_3.md](GOVERNOR_0_3.md).

## Gesamtsuite

`python -m unittest discover -s tests -v` wurde im Entwicklungsdurchlauf erfolgreich abgeschlossen: **264 Fälle, davon 262 erfolgreich und zwei wegen fehlender Windows-Symlinkberechtigung übersprungen**, keine Fehler oder fehlgeschlagenen Assertions. Laufzeit laut gespeichertem Abschlussprotokoll: 62,274 Sekunden. Reale Windows-Junction-Prüfungen sind davon getrennt und wurden ausgeführt. Nachweis: [unit-tests-v03.txt](../artifacts/unit-tests-v03.txt).

Die Tests behandeln unter anderem dauerhafte Gruppenmitgliedschaft, Pfadduplikate und Überschneidungen, getrennte Modellfreigaben, Scope- und Vault-Grenzen, Hashdrift, Aufnahme und Planrevisionen, Abhängigkeiten, Staging-Erhaltung von Original-WIP und den eingeschränkten unittest-Adapter. Regressionen verhindern insbesondere Erfolg bei null oder ausschließlich übersprungenen Tests sowie bei einer gefälschten Stdout-Erfolgsmeldung mit vorzeitigem `os._exit(0)`. Der separate Abschlussdatensatz und die erneute Prüfung von Originalen und Staging sind erforderlich. Vollständige unveränderte Testquellen gehören zum nachfolgenden Supervisor-Kontext.

## Browserbeobachtung

Die folgenden Interaktionen wurden im Codex-Browserwerkzeug auf der isolierten Vorschau `http://127.0.0.1:8788/` beobachtet und anschließend als Protokoll festgehalten: [browser-check-v03.json](../artifacts/browser-check-v03.json). Das ist eine manuelle Aufzeichnung werkzeugbeobachteter Interaktionen, kein exportierter Playwright-Trace. Ein Screenshot wurde nur inline im Entwicklungsgespräch ausgegeben; es gibt dafür keine neue Screenshotdatei. Ältere `ui-v02`-Bilder sind kein 0.3-Nachweis.

- Synthetisches Single-Projekt mit deaktiviertem Modellversand registriert.
- Gruppe `UI Testgruppe` erstellt und das Projekt dauerhaft als Elternprojekt zugeordnet. Ein unvollständiges Strategie-Template entstand, die ursprüngliche Notiz blieb erhalten.
- Quellengebundene Aufnahme in der Oberfläche bestätigt.
- Zwei ausdrücklich synthetische Planrevisionen aus einer Fixture geladen. Revision 2 zeigte Prioritäten, Begründungen, konkrete Dateipfade, Testbeschreibungen und den Vorgängernamen vor der Auswahl.
- Unabhängigen Schritt ausgewählt; gespeichert wurde nur `plan_selection_only`.
- Nach Korrektur sperrte die Auswahl des abhängigen Schritts allein die Bestätigung und zeigte den fehlenden Vorgänger beim Namen.
- Die Abfrage des Browser-Fehler-/Warnungsprotokolls der Vorschau war leer.
- Nach Migration die Hauptoberfläche auf Port 8787 neu geladen: alle fünf Projekte sichtbar, lokale Beobachtung aktiv, bestehende Gates erhalten.

Die [Vorbereitung der UI-Planfixture](../artifacts/prepare_ui_plan_fixture.py) ist ausdrücklich synthetisch und für das gestoppte Vorschaujournal bestimmt. Sie belegt keine echte Modellplanung und soll nicht gegen das laufende Hauptjournal ausgeführt werden. Keine der beschriebenen Browserhandlungen änderte die fünf Produktrepositories oder nahm deren Gates ab.

## Echter isolierter Modell-/Testpilot r3

Der [r3-Gesamtbericht](../artifacts/staging-pilot-live-2026-09-12-r3/report.json) lief am 12.09.2026 von 06:50:14 bis 06:51:14 UTC. Reale Modellaufrufe wurden verwendet; der Projektinhalt war ausschließlich synthetisch. Es wurden keine echten Produktinhalte versendet. Automatische Reviews und Apply-back waren aus.

Die Fixture hatte `calc.value()` mit Rückgabe `1` und einen bestehenden unveränderten Test mit `self.assertEqual(value(), 2)`. Der **Betreiberplan war fest vorgegeben**, nicht modellgeneriert oder modellreviewt. Terra schlug die begrenzte Änderung auf `return 2` vor. Der jeweilige Supervisor prüfte den Vorschlag, der Stager erstellte eine separate Kopie, ein echter Standardbibliothek-unittest lief darin, und anschließend bewertete derselbe ausgewählte Supervisor Diffs, Hashes, tatsächliches Testergebnis und sämtliche versiegelten Dateitexte einschließlich des unveränderten Tests.

| Kombination | Patchauftrag | Test-/Nachprüfauftrag | Tatsächlich beobachtetes Ergebnis |
|---|---|---|---|
| Hermes → GPT-5.6 Terra medium + GPT-5.6 Sol medium | `62669f72b0aa484eb1dbb7af6b74f3b4` | `5c209f0579024913a434d3ce513b34c2` | Ein Test, keine Fehler/Fehlschläge/Skips; Abschluss und Quellen verifiziert; final `REVIEW_ONLY`, keine offenen Befunde/Nachweise; `verified=true`, `stale=false`. |
| Hermes → GPT-5.6 Terra medium + GPT-6 Astra medium | `dcf14ae35b93406196f0172310191353` | `b4e4e4837a5c4661bf9fb2d60daecc0f` | Ein Test, keine Fehler/Fehlschläge/Skips; Abschluss und Quellen verifiziert; final `REVIEW_ONLY`, keine offenen Befunde/Nachweise; `verified=true`, `stale=false`. |

Die zugehörigen Einzelberichte liegen im selben r3-Verzeichnis unter den Auftrags-IDs. Der Bericht hält Hermes 21.1 und eine erfolgreiche Zero-Tool-Prüfung mit `tool_count=0` fest. Originalhashes vor/nach dem Lauf stimmen überein; auch die geprüften Workbench-Module änderten sich während des Laufs nicht. Die Testassertion prüft Gleichheit mit `2`, nicht gesondert den Typ; die gestagte Implementierung gibt direkt das Integerliteral `2` zurück.

Die früheren Pilotläufe, insbesondere [r2](../artifacts/staging-pilot-live-2026-09-12-r2/report.json), bleiben Diagnoseevidenz und werden nicht nachträglich als erfolgreich umgedeutet. Der r2-Nachreview deckte auf, dass ein leerer Testdiff die unveränderten Assertions nicht übermittelt hatte. r3 enthält deshalb vollständige hashgeprüfte Staging-Quellen und eine klare Begrenzung des Reviews auf das isolierte Artefakt.

Dies ist ein kleiner Fixture-Nachweis, keine allgemeine Modellgüte-Rangfolge, keine End-to-End-Abnahme modellgenerierter Planung und keine Produkt- oder Integrationsabnahme. Der Python-Audit-Guard ist keine Betriebssystem-Sandbox gegen adversarialen Python-/nativen Code. Es gab keine Rückübertragung in Originaldateien.

## Hauptdienst und erhaltener Bestand

Der Hauptdienst wurde auf Governor **0.3.0** unter `http://127.0.0.1:8787/` umgestellt. Die fünf bekannten Projekt-IDs sind in `aurelia-integration` migriert. Einstellungen im Nachherzustand: `monitor_enabled=true`, `auto_review=false`, Supervisor `gpt-6-astra`.

Verglichen wurden [Vorherzustand](../artifacts/pre-v03-main/state.json) und [Nachherzustand](../artifacts/post-v03-main-state.json). `evidence_hash`, `decision_hash` und das vollständige bestehende `governor`-Matrixobjekt waren dabei exakt gleich:

| Merkmal | Unveränderter Wert |
|---|---|
| Quellen-/Regelfingerprint | `05f04d8e98e0c10c018cb33b6655f340b8e90c3282f9634a70b4be9d0b3141b1` |
| Entscheidungsfingerprint | `91869ea542f33251f68ee1313cf08f5ae393b3579519e946dcf1c24f9d0743a5` |
| Bestehende Governor-Matrix | Vollständige Objektegleichheit vor/nach der Migration. |

Diese Gleichheit belegt den erhaltenen beobachteten Legacy-Stand zu den Sicherungszeitpunkten. Sie ersetzt weder einen erneuten umfassenden Produktreview noch eine Abnahme offener Gates. Die lokalen Zustandsartefakte enthalten betrieblichen Kontext und gehören nicht ungeprüft in ein portables Release.

Anschließend wurden über `/api/registry/memory` alle fünf vorhandenen `strategy_project_1.md` bis `strategy_project_5.md` ausdrücklich zugeordnet. Alle Antworten meldeten `created=false`; Quellen- und Entscheidungsfingerprint blieben unverändert. Der neuere Nachweis ist [existing-memory-mapping-v03.json](../artifacts/existing-memory-mapping-v03.json). Die fünf Gedächtnisse sind damit zugeordnet, ihre fachliche Aufnahme ist dadurch weiterhin nicht bestätigt. Die Gruppenkarten bieten außerdem ausdrücklich begrenzte Einzelaufnahme und Projekthybridreview; ein solcher Einzelkontext ersetzt keine Gruppenabnahme.

Die gesonderte Paketprüfung ist nachfolgend dokumentiert; alte portable 0.2-Nachweise wurden dafür nicht verwendet.

## Portables Quellpaket

Das Windows-ZIP wurde in einen frischen Arbeitsordner unter `artifacts/portable-v03` entpackt. Alle 93 Manifest-Dateien wurden anhand von SHA-256 geprüft; persönliche Konfiguration, Anmeldedateien, Hauptjournal und Checkpoints waren nicht enthalten. Die Tests aus dieser entpackten Kopie ergaben erneut **264 Fälle, 262 bestanden, zwei übersprungen**, in 63,865 Sekunden. Dies ist ein Test einer frischen Installation auf demselben Windows-Rechner, kein Nachweis auf einer zweiten physischen Windows-Instanz. Produktiver Dienst und Testdateien stimmen bytegenau mit der getesteten Kopie überein. Das anschließend korrigierte Checkpoint-Hilfsskript wurde durch einen eigenen vollständigen Sicherungs- und Manifestprüflauf verifiziert. Die aktuelle Archivprüfsumme steht in `dist/GovernorWorkbench-0.3.0-Windows.zip.sha256`.

## Offen und nächste Arbeit

A–D sind weiterhin nur teilweise umgesetzt. Als nächste freigegebene Entwicklungsarbeit folgen kontrolliertes Apply-back mit Rücknahme-/Konfliktnachweisen, begrenzte Reparatur und explizite Fortschrittsführung; danach die vollständigen projektspezifischen D-Adapter und deren Nachweise. Vault-Spiegelung und ein kontrollierter Umzug/Pfadwechsel bleiben ebenfalls offen. Abhängige Ausführungsfolgen dürfen nicht aus einer bloßen Auswahl als bereits ausführbar behandelt werden.

Die grundsätzliche Freigabe für A→B→C→D wurde erteilt und muss nicht erneut eingeholt werden. Produktgates, neue konkrete Umfangsänderungen und die weiterhin ausgeschaltete Automatik bleiben getrennte Grenzen. Dieser Bericht behauptet keine vollständige Erledigung des Ausbauplans.
