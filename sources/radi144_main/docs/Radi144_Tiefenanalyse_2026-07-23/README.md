# Radi144 - codebasierte Tiefenanalyse

**Analysestand:** 23.07.2026  
**Repository:** `C:\Users\Hubert111\Documents\Radi144`  
**Untersuchter Stand:** aktueller Arbeitsbaum auf Branch `fix/r144-frontend-synergy`, HEAD `9649e9b`  
**Zweck:** rein analytische Bestandsaufnahme als Grundlage für eine spätere Planerstellung

## 1. Aussage dieser Dokumentation

Diese Dokumentationssuite beschreibt, was der aktuell vorhandene Code tatsächlich tut, wie die Projektbereiche zusammenspielen, welche Eigenschaften bereits tragfähig sind und welche Lücken einem produktiven Einsatz entgegenstehen.

Das wichtigste Gesamturteil lautet:

> Radi144 ist funktional breit, aber in der aktuellen Form ein Entwicklungsprototyp. Ein isolierter lokaler Einbenutzerbetrieb ist mit klaren Einschränkungen möglich. Ein öffentlich erreichbarer, mehrbenutzerfähiger, geschäftskritischer oder medizinisch/therapeutisch positionierter Produktivbetrieb ist derzeit nicht vertretbar.

Die wesentlichen Gründe sind:

- fail-open Zugriffsschutz in der lokal vorgefundenen Serverkonfiguration,
- frei wählbare serverseitige Lese-, Schreib- und teilweise Löschpfade,
- fehlende Transaktions- und Mehrprozesssicherheit der JSON-Persistenz,
- unbeschränkte rechenintensive API-Pfade,
- globale, nebenläufig nicht isolierte Engine-Zustände,
- Klartextspeicherung personenbezogener und potenziell gesundheitsbezogener Daten,
- nicht konsistente Lösch-, Backup- und Aufbewahrungsprozesse,
- keine reproduzierbare Build-, Release- oder Deploymentkette,
- deutliche Abweichungen zwischen Produktbehauptungen und realer Algorithmik,
- fehlende wissenschaftliche, klinische und regulatorische Validierung.

## 2. Analyseregeln

Die Analyse trennt drei Arten von Aussagen:

| Kennzeichnung | Bedeutung |
|---|---|
| **Codebefund** | Direkt aus ausführbarem Code, Konfiguration, Tests oder Datenstruktur ableitbar |
| **Dokumentationsaussage** | Behauptung aus README, Handbuch, UI oder älterer Analyse; nicht automatisch wahr |
| **Einschätzung** | Technische, wissenschaftliche, betriebliche oder regulatorische Bewertung des Befunds |

Prioritäten im Risikoregister:

| Priorität | Bedeutung |
|---|---|
| **P0** | Kritisch; bei zutreffendem Betriebsszenario unmittelbarer Blocker für Einsatz oder Exposition |
| **P1** | Hoch; Release- oder Produktionsblocker |
| **P2** | Mittel; wichtige Funktions-, Qualitäts- oder Betriebsrisiken |
| **P3** | Niedrig; Wartbarkeit, Konsistenz oder langfristige Qualität |

## 3. Abgrenzung

Nicht durchgeführt wurden:

- Änderungen an Produktcode, Konfiguration, Referenzdaten oder Runtime-Daten,
- dynamische Exploitversuche,
- medizinische oder klinische Wirksamkeitsprüfung,
- externe Rechtsberatung,
- externe CVE-, Lizenz- oder Supply-Chain-Scans,
- produktives Deployment auf Debian/CUDA-Zielhardware,
- vollständiger Browser-E2E-Test,
- Last-, Langzeit-, Parallelitäts- oder Restore-Test.

Erstellt wurde ausschließlich dieser gesonderte Dokumentationsordner.

## 4. Arbeitsbaum und Gültigkeitsgrenze

Der untersuchte Arbeitsbaum war nicht sauber:

- geändert: `main.py`
- geändert: `user_workflow.css`
- geändert: `user_workflow.html`
- geändert: `user_workflow.js`
- unversioniert: `tests/test_standalone_ui_serving.py`
- unversioniert: `user_workflow.css_old`
- unversioniert: `user_workflow.js_old`

Die Analyse beschreibt daher den **aktuellen Dateistand auf dem Rechner**, nicht ausschließlich den letzten Commit. Insbesondere die integrierte Same-Origin-Auslieferung der Browseroberfläche und Port 8090 liegen im aktuellen Arbeitsbaum, können aber von einer reinen HEAD-Auslieferung abweichen.

## 5. Dokumentationsstruktur

| Dokument | Inhalt |
|---|---|
| [01_EXECUTIVE_SUMMARY.md](01_EXECUTIVE_SUMMARY.md) | Gesamturteil, Reifegrad, Stärken, Blocker und Entscheidungsgrundlage |
| [02_ARCHITEKTUR_UND_KOMPONENTEN.md](02_ARCHITEKTUR_UND_KOMPONENTEN.md) | Einstiegspunkte, Schichten, Komponenten, Zustände und Mermaid-Architektur |
| [03_ENGINE_ALGORITHMEN_UND_FACHLOGIK.md](03_ENGINE_ALGORITHMEN_UND_FACHLOGIK.md) | Tatsächliche Formeln, Zufallslogik, Score, EMF, Bio-, Amplifier- und Audiofunktionen |
| [04_DATEN_PERSISTENZ_UND_LEBENSZYKLUS.md](04_DATEN_PERSISTENZ_UND_LEBENSZYKLUS.md) | Dateninventar, Speicherung, Im-/Export, Löschung, Backups und Datenflüsse |
| [05_API_UI_CLI_UND_INTEGRATIONEN.md](05_API_UI_CLI_UND_INTEGRATIONEN.md) | FastAPI, Browser, PowerShell, CLI, PDF, Audio, WebSockets und Bus |
| [06_SICHERHEIT_DATENSCHUTZ_UND_REGULATORIK.md](06_SICHERHEIT_DATENSCHUTZ_UND_REGULATORIK.md) | Threat Model, Angriffspfade, Datenschutz und regulatorische Grenzen |
| [07_TESTS_QUALITAET_UND_WARTBARKEIT.md](07_TESTS_QUALITAET_UND_WARTBARKEIT.md) | Aktuelle Verifikation, Testarchitektur, Coverage-Lücken und technische Schulden |
| [08_BETRIEB_DEPLOYMENT_UND_RECOVERY.md](08_BETRIEB_DEPLOYMENT_UND_RECOVERY.md) | Installation, Konfiguration, systemd, Logging, Releases, Backup und Supportfähigkeit |
| [09_RISIKOREGISTER_UND_GAP_ANALYSE.md](09_RISIKOREGISTER_UND_GAP_ANALYSE.md) | Konsolidiertes P0-P3-Register und fehlende Produktionsbausteine |
| [10_EMPFEHLUNGEN_UND_PRODUKTIONSGATES.md](10_EMPFEHLUNGEN_UND_PRODUKTIONSGATES.md) | Priorisierte Empfehlungen und prüfbare Freigabekriterien, noch kein Implementierungsplan |
| [11_MERMAID_STRUKTUREN.md](11_MERMAID_STRUKTUREN.md) | Zentrale Architektur-, Sequenz-, Daten-, Trust- und Zielbilddiagramme |
| [12_TRACEABILITY_UND_QUELLEN.md](12_TRACEABILITY_UND_QUELLEN.md) | Befund-zu-Quellstelle-Matrix, Verifikationsprotokoll und Restunsicherheiten |
| [13_GLOSSAR.md](13_GLOSSAR.md) | Leicht verständliche Begriffsdefinitionen |

## 6. Schnelle Lesereihenfolge

Für eine Management- oder Freigabeentscheidung:

1. `01_EXECUTIVE_SUMMARY.md`
2. `09_RISIKOREGISTER_UND_GAP_ANALYSE.md`
3. `10_EMPFEHLUNGEN_UND_PRODUKTIONSGATES.md`

Für eine technische Planerstellung:

1. `02_ARCHITEKTUR_UND_KOMPONENTEN.md`
2. `03_ENGINE_ALGORITHMEN_UND_FACHLOGIK.md`
3. `04_DATEN_PERSISTENZ_UND_LEBENSZYKLUS.md`
4. `05_API_UI_CLI_UND_INTEGRATIONEN.md`
5. `07_TESTS_QUALITAET_UND_WARTBARKEIT.md`
6. `08_BETRIEB_DEPLOYMENT_UND_RECOVERY.md`
7. `10_EMPFEHLUNGEN_UND_PRODUKTIONSGATES.md`

## 7. Wichtiger Hinweis zu Recht und Medizin

Die regulatorischen Abschnitte sind eine technische Risikoanalyse und **keine Rechtsberatung**. Ob Radi144 rechtlich als Wellnesssoftware, Medizinprodukt, Praxissoftware oder anderweitig einzustufen ist, hängt insbesondere von Zweckbestimmung, Vermarktung, Nutzergruppe, tatsächlichem Einsatz und Ausgaben ab. Die im Repository verwendeten gesundheits- und wirkungsnahen Begriffe machen eine fachanwaltliche und medizinprodukterechtliche Prüfung erforderlich, bevor reale Klientendaten produktiv verarbeitet oder entsprechende Leistungsversprechen veröffentlicht werden.
