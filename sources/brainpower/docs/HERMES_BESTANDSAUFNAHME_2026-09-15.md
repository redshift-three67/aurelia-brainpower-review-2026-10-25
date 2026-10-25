# Hermes/Governor: Bestandsaufnahme vor der Matrixfortsetzung

Stand: 15.09.2026. Auftrag: lokale Bestandsaufnahme während der SMB-Providerklärung. Keine Produktimplementierung, keine neuen Modellaufrufe oder Betreiberentscheidungen. Server-SMB bleibt unverbunden; zuletzt verweigerte Anmeldung, neuer möglicher Providerbenutzer `k213487` noch ungeklärt.

## Aktueller Journalstand

`runtime/journal.db` ausschließlich mit SQLite `mode=ro` und `query_only` gelesen; keine zweite Store-Instanz auf dem Live-Journal erzeugt.

- Fünf registrierte Projekte in einer Gruppe.
- Null bestätigte Aufnahmen (`reg_intake`), zehn gespeicherte Aufnahmeentwürfe einschließlich Historie.
- Null Plankandidaten und null übernommene Strategierevisionen.
- Keine laufenden, wartenden oder eingereihten Aufträge zum Prüfzeitpunkt.
- Automatische Reviews aus; ausgewählter Supervisor `gpt-5.6-sol`.

Die vorhandenen abgeschlossenen Vergleiche ersetzen keine fachliche Aufnahmebestätigung. Die Aktualität der externen Produktquellen wurde in dieser lokalen Prüfung nicht neu festgestellt.

## Fähigkeiten und Grenzen

| Bereich | Im lokalen Stand vorhanden | Noch erforderlicher Nachweis/Ausbau |
|---|---|---|
| Aufnahme/Strategie | Quellengebundene Entwürfe, explizite Annahme, unveränderliche Strategieübernahme | Vier Aufnahmefelder pro Projekt prüfen; anschließend aktuelle Strategie erzeugen und bewusst übernehmen |
| Register/Erweiterung | Stabile IDs, Gruppenrollen, Pfadabgrenzung, Versandfreigabe pro Projekt | Modulverträge, Laufzeitintegration und gemeinsamer Betrieb mit Aurelia |
| Ausführung | Begrenzter unabhängiger Staging-/Apply-/Rollback-Pilot | Konkrete Windows-/Ubuntu-Projektadapter, Rechte, Start/Stop, Ports, Ressourcen und Abbruch |
| Tests und Review | Isolierte unittest-Ausführung und quellengebundener unabhängiger Review | Reale Testprofile und Live-Nachweise für jedes Produkt |
| Fortschritt/Reparatur | Auftragsstatus und Nachweise | Begrenzte Reparatur, belastbare Vorgängernachweise, genehmigte abhängige Schrittfolgen |
| Hermes-Isolation | Zero-tool-Vertrag und Isolationstests vorhanden | Installierte Hermes-Kompatibilität bei Integrationsänderung erneut live ohne Modellversand prüfen |
| Installation | Lokales Workbench-Setup | Gesamtabnahme auf sauberer fremder Windows-Instanz erst nach funktionalem Abschluss |

## Token-Effizienz: gezielte Codeprüfung

`llm.py` und `hermes_runner.py` geben Provider-Usage zurück; `planning_llm.py` und hybride Reviews erhalten Aufrufberichte unter `calls`. Dies ist noch keine durchgängige Verbrauchsbilanz aller erfolgreichen, abgebrochenen und fehlgeschlagenen Teilaufrufe. In `static/app.js` wurde keine dedizierte Tokenaggregation gefunden; generische Ergebnisdarstellung ersetzt keine Verbrauchsansicht.

Die Grenzen unterscheiden sich: Router maximal 120000 Promptzeichen, HermesAdapter maximal 95000. Plan-/Patch-Prüfungen arbeiten teilweise mit 120000 Zeichen. Dadurch kann ein dort zugelassener Kontext am Hermes-Transport abgewiesen werden. Kein neuer Fehlerlauf mit realen Modellen wurde ausgelöst; dies ist eine statisch festgestellte Vertragsdifferenz.

Vault verteilt ein begrenztes Bytebudget auf Quellen und markiert Kürzungen. Es gibt damit keine nachgewiesene aufgabenspezifische Relevanzauswahl. Der Vergleichspfad verwendet bereits einen Terra-Entwurf für zwei unabhängige Supervisoren statt zweier Terra-Entwürfe.

Nächster sinnvoller lokaler Implementierungsblock:

1. Einheitlichen transportabhängigen Kontext-Preflight definieren; überschrittene Grenzen früh verständlich melden, ohne stille Kürzung oder Transportwechsel.
2. Usage je Aufruf, Job und Modell normalisieren und anzeigen. Fehlende Angaben bleiben unbekannt, nicht null; fehlgeschlagene Aufrufe dürfen nicht unsichtbar werden. Keine Kostenbehauptung ohne belastbare Preisdaten.
3. Synthetisch testen: fehlende Usage, Teilfehler, Abbruch, doppelte Ergebnisanzeige ohne Doppelzählung, Scope-/Quellenwechsel und gekürzte entscheidungsrelevante Evidenz.
4. Erst anschließend Relevanzauswahl/Wiederverwendung bewerten. Wiederverwendung nur bei gleicher Quelle, Konfiguration, Scope und Berechtigung. Keine automatische Übernahme alter Freigaben.

Siehe auch [Token-Effizienz-Anforderung](HERMES_TOKENEFFIZIENZ_2026-09-15.md). Dieser Bericht implementiert keine der genannten Erweiterungen und startet keinen Kostenbenchmark.

## Zusätzlicher Erweiterungstest

Eine temporäre Datenbank und ausschließlich synthetische Verzeichnisse wurden verwendet. Fünf bekannte IDs plus vier zusätzliche Module ließen sich in einer Gruppe registrieren. Neun eindeutige IDs, Gruppenzuordnung nach erneuter Registry-Initialisierung und standardmäßig ausgeschalteter Modellversand wurden per Assertions bestätigt.

Das prüft die Registerbasis für neun Einträge. Es prüft weder neun produktive Module noch API-/Event-/Tenant-Verträge, Migrationen, Abhängigkeitsausführung oder einen vollständigen Mehrgruppen-Lifecycle. Die echte Gruppe blieb unverändert.

## Reihenfolge

1. Lokale technische Grundlagen: Kontext-/Verbrauchsnachweise und klar begrenzte Adapterverträge vorbereiten.
2. Betreiber prüft fünf Aufnahmen; daraus aktuelle Strategie ableiten und übernehmen. Kein Infrastrukturauftrag ersetzt diese fachlichen Entscheidungen.
3. Projektadapter zunächst mit synthetischen Piloten, danach mit jeweils genehmigten Produktscopes ausbauen.
4. Test-/Live-Nachweise, Reparatur und abhängige Folgen; Mehrgruppen-/Vault- und Neun-Modul-Gesamtabnahme.
5. Vollständiges Windows-Erstsetup und anschließende Produktmodul-Verifikation/Integration.

SMB-/Restore-Abnahme läuft nach Providerklärung separat weiter. Frontendframework und Headless-CMS bleiben offene Architekturentscheidungen.

## Prüfung

`python -m unittest discover -s tests`: 343 Tests in 127,530 Sekunden, Ergebnis `OK (skipped=2)`; somit 341 bestanden, zwei ausgelassen. Zusätzlich bestand der oben beschriebene synthetische Neun-Einträge-Test. Kein funktionaler Quellcode wurde verändert. Keine neue Live-Modellprüfung oder Browser-Gesamtabnahme durchgeführt. Diese Tests bestätigen nicht die noch fehlende allgemeine Produktausführung.
