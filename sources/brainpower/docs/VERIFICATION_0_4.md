# Verifikation Governor 0.4

Stand: 12.09.2026. [Funktionsumfang und Grenzen](GOVERNOR_0_4.md). Echte Modellprüfungen verwenden ausschließlich synthetische Projektinhalte. Keine neue Abnahme der fünf Produkte ist damit verbunden.

## Regressionen und Browser

Die vollständige Suite `python -m unittest discover -s tests -q` besteht mit **322 Fällen: 320 erfolgreich, zwei wegen fehlender Symlinkberechtigung übersprungen**. Laufzeit 102,060 Sekunden. Nachweis: `artifacts/unit-tests-v04.txt`. JavaScript-Syntaxprüfung von `app.js` und `theme.js` erfolgreich.

Zusätzlich zu den 0.3-Grenzen geprüft: dauerhafte Fragen, begrenzte Antworten, identische Auftrags-ID, unabhängige Umfangsprüfung, Abbruch-/Antwortkonkurrenz, Neustart, ungetrackte und neu auftauchende Dateien während einer Patchfrage, Ablehnung doppelter JSON-Felder, konkrete Apply-Freigabe, Rücknahme, fremde WIP, Teilfehler, beschädigte Sicherungen, dauerhafte Wiederholungssperre und Fehlerbelege. Ein verspäteter Abbruch darf einen bereits abgeschlossenen Schreibvorgang nicht als unverändert darstellen. Wiederherstellungsbelege bleiben nach Neustart und auch nach mehr als 40 neueren Aufträgen sichtbar.

Werkzeugbeobachtete Browserprüfung an getrennten Instanzen auf 8788 und 8789:

- Hell, Dunkel und System gewählt; Hell bleibt nach Neuladen erhalten. Keine Fehler im Browserprotokoll.
- Synthetische wartende Frage über Dienstneustart erhalten; Auftrag, Supervisor, Frage und Quellenbindung oberhalb der Matrix sichtbar. Eingetragener Antwortentwurf bleibt während Live-Aktualisierung und Themewechsel erhalten. Anschließender ausdrücklicher Abbruch schließt den Testauftrag.
- Die echten Pilotbelege zeigen Zielordner, Dateihashes, vollständigen Diff und konkrete Freigabereferenz. Bereits übernommene und zurückgenommene Vorschläge sind für erneute Übernahme gesperrt. Zwei dauerhafte Transaktionsbelege zeigen „Zurückgenommen“; keine erneuten Rücknahmebuttons.
- Hauptseite nach Update geladen: fünf Projekte, aktive Beobachtung, Astra-Auswahl, Live-Verbindung, keine Browserfehler. Zusätzliche Prüfserver und Tabs anschließend geschlossen.

Das ist ein Protokoll beobachteter Bedienungen, kein exportierter Browsertrace. Screenshots wurden im Gespräch ausgegeben; keine neue Screenshotdatei wird behauptet. Die echten Schreibaktionen wurden durch den Worker und in einem separaten HTTP-Ende-zu-Ende-Test ausgeführt, nicht durch Browserklicks auf die bereits verbrauchten echten Freigaben.

## Echter Rückfrageablauf

`artifacts/operator-questions-live-2026-09-12-r3/report.json`, 08:08:57–08:10:27 UTC:

| Kombination | Auftrag | Nachweis |
|---|---|---|
| Hermes/Terra medium + Sol medium | `243394e7b7c14712914943356a51d867` | Tatsächliche Frage, Warten, gespeicherte Alpha-Antwort, beide Rollen bestätigen unveränderten Umfang, derselbe Auftrag liefert unabhängig geprüften Plan und gespeicherten Kandidaten |
| Hermes/Terra medium + Astra medium | `8fe2ef3e603b4305b7efc8e119e42008` | Gleicher vollständiger Ablauf mit separatem Supervisor; gespeicherter Kandidat |

Hermes-Probe und Terra-Aufrufe bestätigen null Werkzeuge. Originaldateien und die elf erfassten Programmmodule blieben während des Laufs unverändert. Der erfolgreiche Plan ist weiterhin keine Ausführungsfreigabe.

Die früheren Läufe bleiben erhalten: Im ersten Lauf verhinderten positive Aussagen in den Sperrlisten bereits die Frage. In r2 funktionierte die Rückfrage, aber die abschließende Planprüfung vermischte zukünftige Ausführungsnachweise mit der aktuellen Planbewertung. Die Anweisungen wurden nach Phase präzisiert; die strenge Sperrlogik wurde nicht gelockert. r3 ist ein neuer diagnostischer Durchlauf, kein verschwiegener Wiederholungsversuch.

## Echter Änderungs-, Test- und Übernahmepilot

`artifacts/staging-pilot-live-2026-09-12-v04/report.json`, 08:13:15–08:14:22 UTC: Beide Kombinationen erzeugten einen begrenzten Patch, bestanden jeweils einen tatsächlich ausgeführten unittest und einen sauberen unabhängigen Nachreview. Der vorhandene Test blieb unverändert. Der synthetische Betreiberplan war fest vorgegeben; dies ist kein Nachweis einer vollständigen modellgenerierten Umsetzungsplanung.

`artifacts/pilot-applyback-2026-09-12-v04/report.json`, 08:15:19–08:15:24 UTC: Die beiden echten Testbelege wurden in ein separates Journal mit kopiertem Staging übernommen. Anschließend liefen tatsächliche Vorbereitungs-, Apply- und Rollback-Aufträge. Beide Ergebnisse sind `applied_and_restored`, sämtliche erfassten Originalbytes wurden wiederhergestellt, das ursprüngliche Evaluationsjournal blieb unverändert. In diesem Übernahmetest gab es keine zusätzlichen Modellaufrufe.

Ein vorheriger Versuch mit den älteren 0.3-r3-Belegen stoppte korrekt vor dem Schreiben: Gespeicherte und aktuell gemeldete Laufwerkskennung unterschieden sich. Dieser Bericht bleibt unter `artifacts/pilot-applyback-2026-09-12/report.json` erhalten. Alte Manifestbindungen wurden nicht umgeschrieben oder umgangen; stattdessen entstand der frische 0.4-Nachweis. Änderungen einer Laufzeit-/Dateisystemidentität können somit eine erneute Vorbereitung erforderlich machen.

Diese kleinen Fälle belegen die getesteten Abläufe, keine generelle Modellüberlegenheit, fachliche Gesamtakkuranz oder Abnahme beliebiger Projekte und Testframeworks.

## Hauptbetrieb

Der Dienst auf Port 8787 wurde nach Sicherung des ruhenden Journals auf **0.4.0** aktualisiert. `artifacts/deployment-v04.json` bestätigt unveränderte Einstellungen, Evidence- und Decision-Hashes sowie identische Matrixprojekte und Arbeitsschritte gegenüber unmittelbar vor dem Update. Lokalbeobachtung bleibt an, automatische Modellreviews bleiben aus, Supervisor bleibt Astra. Keine Pilottransaktion und keine Testfrage wurden in das Hauptjournal übertragen. Der zuvor erledigte Snapshotvergleich bleibt separat dokumentiert.
