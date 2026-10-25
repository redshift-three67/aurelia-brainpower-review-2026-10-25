# Phase 3 – Exportäquivalenz-Gate (vor einer echten Parallel-Exportintegration)

**Status:** definiert, nicht freigegeben; der heutige Parallelmodus bleibt ausschließlich planend.
**Betriebsprofil:** Variante A, lokaler Einoperator, Loopback-only.
**Sicherheitsgrenze:** Dieses Dokument autorisiert weder eine Migration noch einen Schreibvorgang.

## 1. Zweck und aktueller Ausgangspunkt

Der produktive Web-Launcher erzeugt weiterhin unverändert seinen Legacy-CLI-Aufruf mit
`--export C:\Benutzer_Archive_Start` (`apps/web/launcher.py:21-94`). Der additive
Parallelmodus wird ausschließlich bei gesetztem serverseitigem
`MORPHIC_PARALLEL_EXPORT_ROOT` aktiviert. Er berechnet einen pseudonymen Planpfad,
registriert ihn im Runtime-Manifest und erzeugt keine Datei
(`core/compliance/artifact_repository.py:55-66`, `apps/web/main.py:506-561`).

Der zuletzt ergänzte rein synthetische Test belegt für einen temporären Root:

1. den Pfad mit Tenant-, Client-, Kategorie- und Sessionsegmenten,
2. den registrierten, fehlenden `parallel_export_plan` im Erasure-Dry-run und
3. einen leeren `ReportCatalog`, solange keine Exportdatei existiert.

Er ersetzt keinen Schreib- oder Migrationsnachweis.

## 2. Nicht verhandelbare Invarianten

| ID | Invariante | Prüfnachweis vor Freigabe |
|---|---|---|
| E0 | Keine Resonanz-, NLS-, Profil-, Gruppen-, Multiplex- oder Scoringlogik wird berührt. | Diff-Review und bestehende Äquivalenztests bleiben grün. |
| E1 | Der produktive Legacy-Befehl und sein `--export`-Wert bleiben bis zu einer ausdrücklich freigegebenen Migration bytegleich. | Vergleich der vollständigen Launcher-Commandliste mit und ohne `MORPHIC_PARALLEL_EXPORT_ROOT`. |
| E2 | Ohne `MORPHIC_PARALLEL_EXPORT_ROOT` gibt es weder Parallelplan, Runtime-Planartefakt noch neuen Schreibpfad. | Negativer API- und Repositorytest. |
| E3 | Der Parallelpfad enthält nur validierte pseudonyme Tenant-/Client-/Kategorie-/Sessionsegmente, nie Name, Geburtsdatum oder Geburtsort. | Unit-Tests für Pfadvalidierung und synthetische Identitäten. |
| E4 | Bis Gate-Freigabe darf kein Parallelpfad Dateien oder Verzeichnisse erzeugen. | Read-only-Test: Pfad und Root bleiben fehlend; ReportCatalog liefert keine Datei. |
| E5 | Bestehende `Benutzer_Archive__ws-*`-Ordner, reale Exportroots, Backups und Runtime-Daten werden nie als Testfixture gelesen, geschrieben, verschoben oder gelöscht. | Ausschließlich `tmp_path`-Fixtures; Review der Testpfade. |
| E6 | Erasure bleibt Completion-Report/Dry-run; ein Parallelplan ist kein Löschauftrag. | Runtime-Manifest-Test mit `path_state: missing`; keine `execute_erasure`-Ausführung. |

## 3. Voraussetzung für einen separaten Schreib-Gate-Antrag

Ein künftiger Schreibtest ist nur zulässig, wenn alle folgenden Voraussetzungen vorliegen:

1. Der Nutzer gibt den separaten Gate-Auftrag ausdrücklich frei.
2. Vor jeder Mutation existiert eine zeitgestempelte ShadowCopy außerhalb des Projektbaums
   mit Hashmanifest; keine Secrets, Runtime-Inhalte oder Klientenexporte sind enthalten.
3. Der Änderungsumfang nennt exakt den Writer/Adapter, die Artefakttypen und die
   vorgesehenen Report-Roots. Er darf nicht stillschweigend den Legacy-Writer ersetzen.
4. Alle Testdaten sind synthetisch und temporär; weder `C:\Benutzer_Archive_Start` noch
   tenant-suffixierte Produktionsroots werden geöffnet.
5. Der neue Writer bleibt zunächst opt-in, serverseitig konfiguriert und additiv. Ein
   Umschalten des Legacy-Defaults ist ein eigenes, späteres Migrationsgate.

Fehlt eine Voraussetzung, bleibt der Parallelmodus plan-only.

## 4. Verbindliche Testmatrix für einen künftigen Schreib-Gate-Antrag

| Test | RED-Behauptung | minimale GREEN-Bedingung | Verbotene Nebenwirkung |
|---|---|---|---|
| A. Launcher-Invarianz | Aktivierter Parallelroot verändert die Legacy-Commandliste. | Vollständige `command`-Liste einschließlich `--export` ist identisch; nur die additiven Responsefelder unterscheiden sich. | Keine CLI-Ausführung. |
| B. Disabled-by-default | Fehlender Root erzeugt einen Plan oder eine Datei. | Kein Plan, kein Manifestartefakt, kein neuer Root. | Kein Zugriff auf Exportroots. |
| C. Plan- und Kataloggrenze | Ein Plan wird als Bericht gelistet oder legt Ordner an. | Manifest meldet registriert/`missing`; Katalog bleibt leer; temporärer Root bleibt fehlend. | Keine Dateierzeugung. |
| D. Isolierter Schreibadapter | Der neue Adapter schreibt außerhalb eines `tmp_path`-Roots oder akzeptiert unkanonische Segmente. | Jeder Schreibversuch bleibt innerhalb eines dedizierten temporären Roots und verweigert unkanonische Segmente vor I/O. | Keine Legacy- oder realen Archive. |
| E. Inhaltsäquivalenz | Für denselben deterministischen synthetischen Eingabefall weicht der neue Artefaktinhalt fachlich vom Legacy-Referenzartefakt ab. | Definierte JSON-/HTML-/Text-/PDF-Regressionen vergleichen die freigegebenen Inhalte nach dokumentierter, deterministischer Normalisierung von ausschließlich Zeitstempeln und Pfaden. | Keine Änderung von Scoring oder Reportinhalt. |
| F. Katalog- und Manifestintegration | Nach einem isolierten künstlichen Write fehlt der neue Artefakttyp im Katalog oder Manifest. | Der Katalog zeigt nur tatsächlich geschriebene, erlaubte Dateitypen; das Manifest referenziert den exakten Pfad und Zustand. | Kein Zugriff auf nicht-temporäre Roots. |
| G. Erasure-Dry-run | Der neue Pfad wird als vollständig löschbar behauptet, obwohl der Index lückenhaft ist. | Completion-Report nennt registrierte und nicht abgedeckte Speicherklassen; kein Löschaufruf. | Keine Löschung. |

Die Inhaltsäquivalenz in Test E ist ausdrücklich enger als eine Pfadgleichheit: Die Pfadstruktur
soll sich ändern, die fachlich freigegebenen Artefaktinhalte jedoch nicht. Jede Normalisierung
muss im Test lokal, eng begrenzt und dokumentiert sein; sie darf weder Scores noch Berichtsblöcke
wegfiltern.

## 5. Freigabe- und Abbruchkriterien

Ein Schreib-Gate ist nur grün, wenn alle Tests A–G mit temporären synthetischen Daten grün sind,
die vollständige Testsuite grün ist, `git diff --check` keine Fehler meldet und ein Review bestätigt:

- keine Änderung des produktiven Legacy-Commands oder seiner Exportinhalte,
- keine Scoring-/Profil-/Multiplexänderung,
- keine reale Export-, Runtime-, Backup- oder Secret-Datei berührt,
- kein Erasure-Schreibpfad aktiviert und
- kein Commit oder Push ohne gesonderte Nutzerfreigabe.

Bei einem Fehlschlag oder einer unklaren Inhaltsabweichung wird die Arbeit am neuen Writer gestoppt.
Der Legacy-Pfad bleibt alleiniger produktiver Schreibpfad; der Parallelplan bleibt rein lesend.

## 6. Gegenwärtige Evidenz

- `tests/test_synthetic_parallel_export_plan.py`: rein synthetischer Manifest-/Reportkatalog-Lesetest.
- `tests/test_parallel_export_plan_configuration.py`: Parallelmodus ist standardmäßig deaktiviert und plant nur bei serverseitigem Root.
- `tests/test_web_workbench_runtime.py`: Web-Scanstart ergänzt den Plan ohne Dateischreiben und behält den Legacy-`--export`-Wert bei.
- `tests/test_topn_export_paths.py`: bestehende Legacy-Pfadform und Tenant-Suffixierung sind als Bestandsverhalten abgedeckt.

Zum Zeitpunkt der Gate-Definition: gezielte Regressionen `20 passed`; Vollsuite
`321 passed, 2 skipped`. Diese Evidenz ist kein Schreib-Gate und keine Produktionsfreigabe.
