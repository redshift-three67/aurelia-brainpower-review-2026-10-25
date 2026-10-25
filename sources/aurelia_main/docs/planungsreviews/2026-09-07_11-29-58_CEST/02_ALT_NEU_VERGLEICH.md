# 02 – Bestehender Plan und empfohlene Korrektur

Status: Vorschlag. ALT bezeichnet ausschließlich den K1-Masterplan vom 25.08.2026 im Konsolidierungs-Worktree. Der Originalwortlaut bleibt unverändert; siehe Quellenmanifest. Die Spalte „alt“ ist eine Zusammenfassung, kein Originalzitat.

## Vollständige Task-Zuordnung

| ALT | Bisheriges Ziel / Reihenfolge | Belegter Stand | Empfehlung | Neues Paket |
|---|---|---|---|---|
| Einstieg | Branch, Basis, sauberer Ausgangsdiff | Task-7-Diff vorhanden; Statusquellen widersprüchlich | Vorhandenen Diff inventarisieren und erhalten; nicht bereinigen oder überschreiben, um formal einen sauberen Stand zu erzeugen | E0 |
| Task 1 | Steuerung und V1/V2-Tip-Sanitisierung | Historisch abgeschlossen dokumentiert | Bestehende Sanitisierung unangetastet lassen; aktuellen Fortschritt von historischen Snapshots trennen | E1 |
| Task 2 | Nichtnormative Governance-Ergänzung | Historisch abgeschlossen dokumentiert | Regeln und historische Referenzen erhalten; dieses Empfehlungspaket nicht automatisch zum Kanon erheben | E1 |
| Task 3 | Fail-closed Publikationsgraph-Scanner | Historisch einschließlich Korrekturen abgeschlossen dokumentiert | Keine Neuentwicklung; erneute Prüfung bei Änderung seines Scopes bzw. vor eigener Publikationsentscheidung | E8 / separater Publikationsschritt |
| Task 4 | K1-Matrix und Kanonvalidator | Commit `1257283`, später erweitert | Vorhandenen Vertrag erhalten; Produktkanonprüfung und Fortschrittsprüfung ausdrücklich unterscheiden | E1 / E8 |
| Task 5 | Aktive Dokumente und Konzeptdaten konsolidieren | Commit `c00fd83` vorhanden | Als implementiert erfassen; keine pauschale Wiederholung; fehlende Abnahmen gezielt nachholen | E0 / E1 |
| Task 6 | Portal und Schale ableiten | Commit `1185a68` vorhanden | Implementierung erhalten; Browserabnahme bleibt offen bis E6/E8 | E6 / E8 |
| Task 7 | Plattformübergreifender Test-Runner | Zwei neue Dateien plus Package-Änderung uncommittiert | Bestehenden Runner prüfen, Restvertrag schließen, Suite ehrlich ausführen | E2 |
| Task 8 | Auth-on-, Migrations-, PWA- und Windows-Testfixtures | Fertigstellung nicht belegt | Beibehalten; temporäre Schreibwirkungen und explizite Skip-Regeln festlegen | E3 |
| Task 9 | Vite-CLI ohne Shell plattformübergreifend auflösen | Fertigstellung nicht belegt | Beibehalten; Windows-/Linux-Nachweise trennen; Buildumgebung ohne Produktionszugriff | E4 |
| Task 10 | Selbsthostende Auth-Invariantenprüfung | Vertragswiderspruch und Lifecycle-Lücken | Einheitliche Optionsnamen; Prozesszuordnung, Portkonflikt und Nachkommenbereinigung prüfen | E5 |
| Task 11 | Browser-Smoke sicher/worktree-portabel | Fertigstellung nicht belegt | Pfadvertrag plus Route-/Viewport-/Zustandsmatrix; keine Gleichsetzung von Homepage-Smoke und Gesamtabnahme | E6 |
| Task 12 | Verwaltete Plattformassets prüfen | Verfügbarkeit in diesem Review nicht vollständig erhoben | Abhängigkeit früh inventarisieren; reales Gate separat implementieren; keine unbelegten Ersatzassets | E0 / E7 |
| Task 13 | Verhaltensneutrale Lintbereinigung | Abschluss nicht frisch geprüft | Beibehalten; tatsächliche Ausgangsbefunde messen statt historische Anzahl erzwingen | E7 |
| Task 14 | Gesamtintegration, Dev/Built-Smoke, Evidenz, zwei Reviews | Abschlussnachweis nicht belegt | Ergebnisse an Snapshot binden; aktualisierte Statusdimensionen; lokale und externe Gates getrennt | E8 |

## Korrekturen an konkreten Verträgen

| Thema | ALT | EMPFOHLEN | Grund / Referenz |
|---|---|---|---|
| Fortsetzung | Niedrigster offener Task laut Ledger | Ledger gegen HEAD und Dirty-Diff prüfen; aktueller Kandidat Task 7 | R01 |
| Testoptionen Task 10 | `spawn`/`fetch` im Beispiel, `spawnImpl`/`fetchImpl` in API | Nur `spawnImpl`/`fetchImpl` | R02 |
| Readiness | Antwort von `/__app-env` | Antwort muss zur eigenen Testinstanz gehören; fremde Antwort darf nicht genügen | R05 |
| Cleanup | Eigenes Kind im `finally` beenden | Eigenen gestarteten Prozessbaum nachweisbar beenden; fremde Prozesse unangetastet | R05 |
| Ergebniszustand | Drei gemischte Klassen | `result`, `freshness`, `implementation`, `gate_state` getrennt | R03 |
| UI-Abnahme | Verweis auf Task 13 | Task 14 / E8; Vorprüfung in E6 | R04 |
| Buildaussage | `build:dev` grün | Explizit Entwicklungsmodus-Build; Produktionsmodus separat | R06 |
| Assetgate | Spät prüfen; aktueller Blocker vorgegeben | Früh erheben; später tatsächliches Ergebnis berichten, nicht erwarteten Blocker festschreiben | Abhängigkeitsmanagement |
| Nachweiserstellung | Endnachweis in Task 14 | Abschlussnachweis weiterhin E8; minimale datierte Ergebnisse bereits je Paket | Wiederaufnahme ohne erneute Vollanalyse |
| Status-HTML | Manuell aktualisiert | Gemeinsame Fortschrittsquelle; Generator optional, Aktualitätsanzeige verpflichtend | R01 |

## Verhältnis zur Produktroadmap

| Ebene | Bestehende Planung | Empfehlung |
|---|---|---|
| K1 | Lokale Konsolidierung ohne Serverfreigabe | E0–E8 vervollständigen; keine Produktphase vorziehen |
| G0-SRV | Backup, Recovery, Installation, Härtung, Gesamtbaseline | Reihenfolge 0–12 erhalten; Backup-/Recovery-Planung darf unabhängig vorbereitet werden, Ausführung braucht den passenden Scope |
| Phase 1 | Nach `G0-SRV-12` AUDIT-02 und Schale abnehmen | Rollen-, Session- und Zwei-Mandanten-Negativtests als explizites Abnahmepaket |
| Phase 2 | Praxisorganisation / Einwilligungen | Erneuter Restore-Nachweis vor Art.-9-Daten; Datenlebenszyklus und Export/Löschung spezifizieren |
| Phase 3 | Kernel-ABI / Raten | Ratenkatalog-Provenienz und Adaptervertrag phasengerecht detaillieren; RadiWorks-Evidenz nicht automatisch übernehmen |
| Phase 4 | CPU-Referenz, dann CUDA / Passport | Reproduzierbarkeit, Isolation, Abbruch und Speicherbereinigung messbar abnehmen |
| Phase 5 | Timer / Harmonisierung | Recovery, Zeitlücken und Ereigniswiederholung explizit prüfen |
| Phase 6 | Archiv / Export / Berichte | Auskunfts-/Exportkonsistenz, Aufbewahrung und Codec-Wiedervorlage |
| Phase 7 | GPU-Härtung | Nur auf bereits abgenommener Referenz; keine Mindestisolation aus Phase 4 bis hier verschieben |
| Phase 8 | Quantum opt-in | Separater Modus und eigener Provenienznachweis |
| Phase 9 | Gestrichen | Bleibt gestrichen |
| Phase 10 | Betrieb / Preise / Restore | Betriebsabnahme einschließlich Wiederherstellbarkeit; Preise gesondert entscheiden |

## Entscheidungsvorschlag für die Besprechung

1. E0/E1 als erste Fortsetzung festlegen: aktuelle Quelle, Statusschema, korrigierte Planverweise.
2. Danach E2–E8 unter Beibehaltung bestehender Task-IDs abarbeiten.
3. E5-Vertrag ausdrücklich vor Implementierung klären; Produktionsabnahme als separates Folgepaket belassen.
4. Weitere Ideen aus Dokument 04 nur selektiv übernehmen. Sie sind keine zusätzlichen automatischen Blocker.
