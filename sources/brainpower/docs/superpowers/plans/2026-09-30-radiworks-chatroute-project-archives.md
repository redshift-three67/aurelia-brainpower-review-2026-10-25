# RadiWorks-Abschluss, Codex-Chat-Route und Projektarchive — Ausführungsplan

> Für die Ausführung: drei getrennte Prüfpakete. Vorhandene Projektarbeit, produktive Daten und Freigabegates bleiben erhalten. Die Arbeit ist vom Betreiber beauftragt; Dokumentation und Sicherung ersetzen keine S4-/Aurelia-Gesamtfreigabe.

**Ziel:** RadiWorks als lokalen Aurelia-Modulprototyp möglichst weit abschließen, die Codex-Chat-Route B portierbar erklären und verifizierte Projektstände auf `F:\Hauptprojekt` ablegen.

**Architektur:** Jeder Projektstand erhält Quellpfade, Git- und WIP-Status, Hashmanifest, bekannte Ausschlüsse und einen Lese-/Wiederherstellungsleitfaden. Governors und die Aurelia-Gruppe liegen unter getrennten Zielwurzeln. RadiWorks-Freigaben werden ausschließlich anhand vorhandener und neu gemessener Belege weitergeführt.

**Technik:** Python/PowerShell auf Windows; Codex-Konfiguration als TOML; RadiWorks Python/vanilla Webapp; SHA-256 und SQLite-Online-Backup für zugängliche Laufzeitdaten.

## 1. Quell- und Zielzustand fixieren

- [x] Ziel `F:` und expliziten Pfad `F:\Hauptprojekt` prüfen; bestehenden ähnlich geschriebenen Ordner nicht verändern.
- [x] Registrierten `morphic_v1`-Worktree gegenüber dem fast leeren `Documents\RadiMorphic` identifizieren.
- [x] Git-/WIP-, Größen-, Laufzeitdaten- und Zugriffsstatus der sechs Quellbäume erfassen; generierte Umgebungen/alte Rücksicherungen von aktuellen Daten trennen. Die Größenaufnahme meldete einzelne unzugängliche temporäre Artefaktordner; jede Sicherung muss diese Ausschlüsse nennen.

## 2. Portierbare Codex-Chat-Route B

- [x] Aktuelle OpenAI-Dokumentation für Unteragenten, Config und Modellrollen öffnen.
- [x] Tatsächliche lokale Konfigurationsdateien und frühere Funktions-/Kostenbelege gegen die Dokumentation abgleichen.
- [x] Eigenständige Markdown-Anleitung für anderen PC schreiben: Sol/high führt, Luna/max nur für ausdrücklich beauftragte begrenzte Arbeit, Astra/medium für unabhängige kritische Prüfung; Konfigurationsbeispiel, Test, Rücknahme und realistische Grenzen der Genauigkeits-/Tokenaussagen.

## 3. Verifizierte Projektstände auf F:

- [x] Snapshot-Helfer mit fest verdrahteten Quell-/Zielwurzeln, Ausschlussliste, Reparse-Schutz, SHA-256-Manifest, SQLite-Online-Kopien und Vollprüfung erstellen; synthetische Kollisions-/Manipulationsprobe bestanden.
- [x] Unter `F:\Hauptprojekt\Governors\20260930-2` Brainpower-/Governor-Quell- und Laufzeitstand mit Entwicklerübersicht zu Mechanismen, Routen, Gedächtnis und Matrix ablegen: 82.861 Dateien, 796 SQLite-Kopien verifiziert.
- [x] Unter `F:\Hauptprojekt\Aurelia\20260930-1` Plattform, RadiWorks, Radi144, registrierten `morphic_v1`-Quellbaum und Modul_Templates samt Git-/WIP-Zustand und übergeordnetem Aurelia-Status ablegen: 274.403 Dateien, 26 SQLite-Kopien verifiziert; RadiFarben nicht als aufgenommenes Modul dargestellt.
- [x] Kopierte Daten, Hashmanifest, SQLite-Konsistenz, lokale Dokumentlinks und Windows-Sonderdateien prüfen; Auslassungen dokumentiert. Ein alter Hermes-Review-Ordner war nicht lesbar; generierte Umgebungen/Testbereiche wurden ausgelassen. Kein Quellprojekt zurückgeschrieben.

## 4. RadiWorks lokal weiter abschließen

- [x] Aktuellen Kandidaten/Arbeitsstand, Test- und Hostlücken gegen S4.6/S4.7 und `Modul_Templates` erneut prüfen.
- [x] Ohne Aurelia-Hoständerung den unveränderten Kandidaten mit vollständiger Engine-Suite und isoliertem Browser-Smoke frisch prüfen; kein zusätzlicher lokaler Produktfehler festgestellt.
- [x] Ziel-Ubuntu-24.04.4-, weitere WCAG-/Screenreader-, Hostautoritäts- und Betreiber-Gates ausdrücklich offen halten; S4.8 nicht automatisch freigeben.
- [x] Abschlussbericht mit exaktem Modulstand, Restliste und nächstem M0-Übergang zu Radi144 schreiben.

## 5. Anschluss nach dem Sicherungspunkt: Radi144 M0

- [x] Radi144-Quelle, HEAD/WIP, tatsächlichen Default-Port, API-/WebSocket-Einstiege und Template-Ausgangslage lesend erfassen.
- [x] Tests in einer Kopie ohne produktive Laufzeitdaten ausführen: 88 nicht-Git-Regelfälle im ersten Vollauf grün; nach eigenem Git-Kontext 9/9 Git-Regelfälle grün. [M0-Baseline](../../verification/RADI144_M0_BASELINE_2026-09-30.md).
- [ ] Fachlichen Umfang und Live-Workflow für die nächste Radi144-M1/M2-Prüfung mit dem Betreiber konkretisieren; Port 8090 und bestehende Nutzerdaten erhalten.
