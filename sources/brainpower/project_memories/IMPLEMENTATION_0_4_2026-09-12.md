# Wiederaufnahmepunkt Governor 0.4

Betreiberfreigabe: Snapshotvergleich erledigt. Vollständiger Windows-Erstinstaller gewünscht, aber erst nach funktionaler Gesamtabnahme. Helles Design ausdrücklich umsetzen. Strukturierte Rückfragen mit UI-Antwort statt echtem interaktivem Terminal akzeptiert. Grundsatzfreigabe A–D bleibt bestehen.

## Tatsächlicher Stand

Hauptdienst auf `http://127.0.0.1:8787/`: Version 0.4.0, lokale Beobachtung an, automatische Modellreviews aus, Hermes/Terra medium mit Astra medium als ausgewähltem Supervisor. Einstellung wurde nicht automatisch umgeschaltet. Matrixprojekte und Schritte sowie Evidence-/Decision-Hashes stimmen vor und nach diesem Update exakt überein (`artifacts/deployment-v04.json`). Keine echten Produktdateien verändert, keine Produktgates abgenommen.

Hell/Dunkel/System und persistente Fragen für scoped Planung/Pilot-Patch sind implementiert. Antworten setzen nach Quellenprüfung und unabhängiger Bestätigung beider Modellrollen denselben Auftrag fort. Umfangsänderung stoppt zur neuen Prüfung. Exakte Patchquellen einschließlich ungetrackter/fehlender Dateien werden gebunden. Keine stdin-/Terminal-Fernbedienung. Pro Auftrag höchstens drei Fragen.

Kontrollierte Pilotübernahme ist implementiert: vorbereiteter exakter Diff, gesonderte Vorschlagshash-Freigabe, tatsächliche erfolgreiche Tests/Nachreview, aktuelle Planauswahl, Sicherung, Konfliktprüfung, eigene Rücknahme, dauerhaft sichtbare Transaktionsbelege. Nur ausdrücklich erlaubte unabhängige Pilotwurzeln; die historischen fünf Produkte und Gruppen bleiben ausgeschlossen. Die Hauptkonfiguration enthält keine solchen Pilotwurzeln. Keine Reparaturschleife oder automatische Folgeschritte.

## Nachweise

- Vollständige Suite: 322 Fälle, 320 bestanden, 2 Symlink-Skips; `artifacts/unit-tests-v04.txt`.
- Echter Rückfrageablauf für Terra/Sol und Terra/Astra bis zum akzeptierten Plan: `artifacts/operator-questions-live-2026-09-12-r3/report.json`.
- Echter Patch, unveränderter unittest, unabhängiger Nachreview beider Varianten: `artifacts/staging-pilot-live-2026-09-12-v04/report.json`.
- Beide tatsächlichen Übernahmen und bytegenauen Rücknahmen im synthetischen Pilot, getrenntes Journal: `artifacts/pilot-applyback-2026-09-12-v04/report.json`.
- Frühere blockierte diagnostische Läufe bleiben erhalten. Alte Laufwerkskennung führte korrekt zur Sperre; frische Nachweise wurden erstellt. Keine Schutzprüfung wurde hierfür umgangen.
- Browser: Themes, wartende Frage nach Neustart, Entwurf während Live-Update, Abbruch, konkrete Freigabediffs und dauerhafte Rücknahmebelege geprüft. Hauptseite neu geladen; Prüfserver 8788/8789 und ihre Tabs geschlossen.

Die kleinen synthetischen Fälle belegen keine allgemeine Modellüberlegenheit oder fachliche Vollabnahme der fünf Produkte. Die Planfrage und der Änderungspilot waren separate Prüffälle; der Änderungspilot hatte einen fest vorgegebenen Betreiberplan.

## Exakt hier weiter

Zuerst `docs/GOVERNOR_0_4.md`, `docs/VERIFICATION_0_4.md`, `docs/LLM_OPERATING_CONTRACT.json` und `docs/OFFENE_SCHRITTE_2026-09-12.md` lesen. Der Gesamtplan bleibt `docs/KONSOLIDIERUNG_SINGLE_MATRIX_VAULT_2026-09-12.md`.

Nächste Priorität ist die vollständige geprüfte Aufnahme der fünf Mitglieder und der hybride Gruppenabgleich mit nachvollziehbar bestätigter Übernahme in Strategie und Matrix. Darauf folgen allgemeine, schrittbezogene Ausführungsfreigaben, begrenzte Reparatur, Fortschritt und ausdrücklich genehmigte Schrittfolgen. Produktadapter/Live-Tests, Vault-Rückspiegelung, leerer neuer Projektstart und Mehrgruppenrobustheit bleiben offen. Der volle Windows-Bootstrap kommt nach der Gesamtabnahme. Das portable 0.4-ZIP ist weiterhin kein vollständiger Erstinstaller.

Grundsatzfreigaben nicht erneut anfragen. Konkrete Produktumfänge und geänderte Pläne dem Betreiber nachvollziehbar zur Freigabe vorlegen. Automatische Reviews nicht allein aufgrund der Fortsetzung einschalten. Historische Checkpoints und WIP erhalten; keine Sicherung ungeprüft zurückspielen.
