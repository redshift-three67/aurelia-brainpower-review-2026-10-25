# Aurelia-Gesamtstand: Bestandsaufnahme vor Export

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Den genehmigten zweiteiligen Gesamtsnapshot durch eine begrenzte, nicht mutierende Quelleninventur und ein getestetes Inventarwerkzeug vorbereiten; keine Pflichtlücke als Vollständigkeit ausgeben.

**Architecture:** Getrennte neue Werkzeug- und private Belegordner innerhalb des bestehenden Brainpower-Arbeitsbereichs. Kein Git-Worktree aus dem übergeordneten persönlichen Profilrepository. Die Inventur liest Verzeichnis- und Dateimetadaten ohne Inhalte, folgt keinen erkannten Reparse-/Symlinkpfaden und protokolliert Fehler/Begrenzungen ausdrücklich. Originalquellen, Datenbanken und Dienste bleiben unverändert.

**Tech Stack:** Python-Standardbibliothek, unittest, native PowerShell für neue Owner/SYSTEM-ACL und gezielte Metadaten; vorhandenes Git nur lesend mit deaktivierten optionalen Schreiblocks.

**Approved design:** `docs/superpowers/specs/2026-10-25-aurelia-gesamtstand-review-snapshot-design.md`, Betreiberbestätigung 25.10.2026 im Chat. Diese Freigabe betrifft geschützte Gesamtsicherung plus privates bereinigtes Reviewrepository. Sie ersetzt keine bestehenden Grenzen für geschützte Live-SQL-Definitionen, Materialstarts, bezahlte Scans oder Diensteingriffe. Die zitierte spätere CI-Freigabefrage wird nicht als bereits ausgeführter Lauf behandelt.

## 1. Kontrollablage und Quellenvertrag

Files:
- Create: `runtime/aurelia-gesamtstand-prep-20261025/OPERATOR_APPROVAL.json`
- Create: `runtime/aurelia-gesamtstand-prep-20261025/SOURCES.json`
- Create: `runtime/aurelia-gesamtstand-prep-20261025/STATE.json`

- [x] Neuen Kontrollordner anlegen und tatsächlich verwendete Identität prüfen. Der Shellprozess ist `CodexSandboxOffline`, nicht der Betreiber. Vorbereitung erlaubt daher ausdrücklich Betreiber, temporären Arbeitsprozess und SYSTEM; Vererbung ist aus. Endgültige Sicherung verlangt Betreiber/SYSTEM und gesonderte Prüfung. Keine Quell-ACL verändern.
- [ ] Bestätigung und Grenzen speichern; Pflichtquellen aus dem Entwurf mit tatsächlichen Pfaden abgleichen.
- [ ] Governors, Brainpower, Aurelia, Modul_Templates, RadiWorks, Radi144, beide Morphic-Stände, RadiFarben, Explorer/Thom und relevante Archivwurzeln explizit aufführen. Serverbelege separat von frischer Serveraufnahme klassifizieren.

## 2. Inventarwerkzeug zuerst negativ prüfen

Files:
- Create: `runtime/aurelia-gesamtstand-tooling-20261025/test_inventory.py`
- Create after red: `runtime/aurelia-gesamtstand-tooling-20261025/inventory.py`

Die zuerst erstellten Werkzeugkopien im privaten Belegordner bleiben historische Anfangsversionen. Ausschließlich der getrennte `tooling`-Ordner ist der aktuelle geprüfte Kandidat. Die Zugriffstrennung wurde nach dem belegten Editorfehler hergestellt; eine native DACL-only-Ergänzung für den Betreiber funktionierte, während PowerShell Set-Acl beim Folgeaufruf SeSecurityPrivilege verlangte.

- [ ] Tests vor Implementierung schreiben und fehlendes Werkzeug als erwarteten Testfehler nachweisen.
- [ ] API `inventory_component(component_id, root, max_entries=200000, max_seconds=90, exclude_rel=())` implementieren. Rückgabe enthält Metadaten, neutrale Fehlercodes, Grenzen und immer `snapshot_complete=false`.
- [ ] API `write_report_exclusive(path, report)` implementieren; neues Ziel exklusiv erzeugen, vorhandene Belege nie überschreiben.
- [ ] Dateiinhalte werden nicht gelesen. Größen sind logische Statwerte und keine physische Speicher-/Inodebedarfsgarantie. Symlinks/Reparsepunkte werden als offene Verknüpfungen verzeichnet. Ausgenommene eigene Kontrollablage wird explizit benannt.

Konkrete Verifikation:

```powershell
python -X utf8 -I -S -B runtime/aurelia-gesamtstand-tooling-20261025/test_inventory.py
```

Die Tests prüfen reale temporäre Bäume, unveränderte Quellbytes/-zeiten, deterministische Pfade, Geheimnisdateien ohne Inhaltszugriff, exklusive Belege, Fehlermeldungen ohne Rohinhalte, Dateigrenzen, Zeitgrenzen, Reparseerkennung und vorhandene Linkunterstützung. Ein Betriebssystem-Skip bleibt sichtbar.

## 3. Unabhängiger Review und begrenzte echte Inventur

Files:
- Create: `runtime/aurelia-gesamtstand-prep-20261025/LOCAL_VERIFICATION.json`
- Create: `runtime/aurelia-gesamtstand-prep-20261025/INDEPENDENT_REVIEW.json`
- Create: `runtime/aurelia-gesamtstand-prep-20261025/INVENTORY_*.json`
- Create: `runtime/aurelia-gesamtstand-prep-20261025/INVENTORY_SUMMARY.json`

- [ ] Tests und Syntaxprüfung durchführen; keine Anwendungssuite für das isolierte Werkzeug behaupten.
- [ ] Astra/medium prüft ausschließlich neue Werkzeug-/Test-/Vertragsdateien; keine realen privaten Dateipfade, Konfigurationsinhalte, Falldaten oder Live-Definitionen als Modellpayload.
- [ ] Vor realer Inventur private Ziel-ACL und Quellenliste zurückprüfen. Pro Quelle maximal 200.000 Einträge und ein kooperatives Zeitbudget von 90 Sekunden; blockierende Dateisystemaufrufe werden dadurch nicht hart unterbrochen. Eine Überschreitung wird auch nach dem letzten Stat-Aufruf als unvollständig verzeichnet. Fehler bleiben im Bericht, kein automatischer Retry oder verschleierter Ausschluss.
- [ ] Für nicht zugängliche Pflichtquellen Berechtigungsursache ausschließlich lesend feststellen; keine ACL-Übernahme. Falls die Sandbox eine genehmigte Metadatenprobe verhindert, gezielte Eskalation mit konkretem Umfang verwenden und deren Ergebnis offenlegen.
- [ ] Dateizahlen/Größen/Gitstände mit bisherigen Belegen vergleichen; Unterschiede bleiben Quellenabweichungen, nicht automatisch Fehler oder neue Autorität.

## 4. Nächste Pakete innerhalb des Gesamtauftrags

Diese Phase ist ausdrücklich keine Fertigstellung der Gesamtsicherung. Nach dem echten Inventar werden die folgenden zusammenhängenden Pakete konkretisiert, ohne neue Produktfunktionen einzuführen:

1. Geschützte Zielablage auf F: mit Kapazitätsreserve; Drift-/Rückleseprüfer und differenzierte Sicherung von Arbeitsbaum, Index und eigenen Git-Refs/Objekten. Aktive DBs ausschließlich mit geeignetem konsistentem Sicherungsweg; Originalarchive erhalten.
2. Fehlende Originalquellen, Verknüpfungsziele und notwendige Referenzassets binden. Öffentliche Explorer-/Thom-Commits zusätzlich zu den lokalen Arbeitsständen erhalten, nicht stillschweigend ersetzen.
3. Konkrete frische Serveraufnahme vorbereiten: effektive Konfiguration, Paket-/Dienst-/Containerstände und Restorevoraussetzungen; Geheimnisse geschützt. Keine ungetestete freie Root-Suche oder Veränderung von Host-/Websitebudgets.
4. Separaten Reviewexport mit Entwickler-/LLM-Einstieg, Status-/Anforderungs-/Workflow-/Template-/Serverzuordnung und bereinigten Manifesten erzeugen. Veröffentlichbare Pfade/Inhalte gesondert prüfen; Originalbytes und bereinigte Darstellungen unterscheiden.
5. Privates Repository unter `redshift-three67`, Actions vor Upload aus, zurückgelesene Remote-Dateimenge/Hashes, danach Archivstatus prüfen. Keine bezahlten Review-/Security-/CI-Läufe aus der Snapshoterstellung starten.

## Abschluss dieser Inventurphase

- [ ] Alle Test-/Review-/Inventarbelege speichern; keine Pflichtlücke ohne Grund.
- [ ] `docs/SERVER_AKTUELL.md` kurz aktualisieren und nächste konkrete Arbeit markieren.
- [ ] `snapshot_complete=false` bleibt bestehen, bis alle Pflichtquellen, Sicherungs- und Servernachweise tatsächlich geschlossen sind.

Praktische Schutzgrenzen: vorhandene F:-Archive und Liveinstanzen bleiben erhalten. Keine Änderungen am Profil-Git, an Produktcode, Algorithmen, Authentisierung oder fremdem Websiteprojekt. Späterer RadiWorks-LF-Korrekturcommit und CI-Einmallauf bleiben ein getrennt gebundener Folgeschritt mit Kontingentprüfung.
