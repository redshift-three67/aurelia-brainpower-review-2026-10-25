# Operator Workbench Freeze-v4 Review Remediation and Freeze-v5 Plan

Status: IN ARBEIT / NO-GO
Datum: 2026-07-19
Branch: `operator-workbench-phase1`
Baseline/HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`

## 1. Change-Control-Grenze

- Freeze v1 bis v4 sind abgelehnt beziehungsweise superseded und keine Freigabeevidenz.
- Freeze v4 war mit 41/41 Dateien driftfrei, erhielt aber `REQUEST CHANGES` und `REJECT`.
- Jede Remediation nach Freeze v4 erfordert einen vollständigen Freeze v5 und zwei neue unabhängige Reviews.
- Freigabe ausschließlich bei zweimal `APPROVE`, jeweils `P0=P1=P2=P3=0`, vollständiger Scopeprüfung und null Drift.
- Kein Commit, Push, Backup oder externe Post-State-ShadowCopy vor technischem und dokumentarischem Doppel-APPROVE.
- Ports 8000 und 8090 bleiben geschützt. Browserabnahme verwendet ausschließlich einen frisch geprüften isolierten Port 8765.

## 2. Unveränderte Reviewevidenz

| Artefakt | SHA-256 | Urteil |
|---|---|---|
| `docs/reviews/2026-07-19-workbench-remediation-technical-freeze-v4.sha256` | `9d0a26a13577ef4c86bca1309fd2672123b7675dd4c4b13393ac76997b7843ad` | superseded |
| `docs/reviews/2026-07-19-workbench-remediation-technical-review-v4-1.md` | `6e45017b8d575d8e4382beed9a145c09b5cbd84dcba9132c7c120443c61d7e11` | REQUEST CHANGES, P0=0/P1=5/P2=2/P3=1 |
| `docs/reviews/2026-07-19-workbench-remediation-technical-review-v4-2.md` | `5a5f65d586302f61cd9adcc2b04db4f5a921d105621d45900accefc41565136d` | REJECT, P0=0/P1=1/P2=2/P3=2 |

Die beiden Reviewdateien wurden bytegenau aus dem Hermes-Delegationscache kopiert; Quell- und Zielhash waren jeweils identisch.

## 3. Konsolidierte Freeze-v4-Befundmatrix

| ID | Priorität | Ursache | Ausführbarer Abschlussvertrag | Remediationstand vor Freeze v5 |
|---|---:|---|---|---|
| V4-01 | P1 | `pending`-Harmonisierung wurde nicht weiter gepollt | Browserlauf `pending → running → completed`, inklusive pollgetriebener ARIA-Werte | implementiert; Playwright grün |
| V4-02 | P1 | Fehlgeschlagener New-Case-Stop invalidierte Generation/Monitoring vorzeitig | Bei Stopfehler: Reset `false`, Job-ID und Generation bleiben, Polling läuft weiter | implementiert; Playwright grün |
| V4-03 | P1 | Scan-Prozessbaumstop meldete Erfolg ohne belastbare Bestätigung | Windows `taskkill /T /F` mit Timeout/Returncode; POSIX Prozessgruppeneskalation; realer Windows-Eltern/Kind-Test | implementiert; fokussierte Tests grün |
| V4-04 | P1 | Impulsabbruch war innerhalb synchroner Hardwaremodulation nicht begrenzt | Frequenzobergrenze, kooperative Deadline-/Stop-Prädikate in CPU/GPU/RAM/WebSocket und Overrun-Test | implementiert; fokussierte Tests grün |
| V4-05 | P1 | Stop konnte mit `cycle_metrics`/Cycle-Commit konkurrieren | Stopprüfung und Cycle-Commit an gemeinsamer Cross-Process-Lockgrenze; deterministischer Interleaving-Test | implementiert; fokussierte Tests grün |
| V4-06 | P1 | Zwei Scanstarts konnten Pollloops/Resultate mischen und Arbeit verwaisen | Single-Flight-State, deaktivierter Startbutton, genau ein Startrequest/Pollpfad | implementiert; Playwright grün |
| V4-07 | P2 | Produktions-Preview und Browser erwarteten verschiedene Metadaten | Backend liefert additiv `title`, `size`, `file_name`; Browser fällt auf `file_name` zurück | implementiert; Python-/Browservertrag grün |
| V4-08 | P2 | Reset versteckte Statuspanels, ließ aber alte Fallwerte im DOM | Scan-/Harmonisierungslabels, Fortschritt, Logs, Ergebnisse und Previewträger auf sichere Defaults setzen | implementiert; Playwright grün |
| V4-09 | P2 | Previewmoduswechsel behielt alten Bericht im versteckten DOM | Vor jedem Rendern iframe/text vollständig scrubben; HTML→Text→HTML-Vertrag | implementiert; Playwright grün |
| V4-10 | P2/P3 | Mehrere Abschlussclaims stützten sich auf Token-/Fake-Tests | reale Windows-Prozessbaumprüfung, Browser-Lifecycle, pollgetriebener Fortschritt, Single-Flight und Stop-Races | implementiert; vollständige Reviewprüfung bleibt erforderlich |
| V4-11 | P3 | Freeze-v4-Aggregatbeschreibung war mehrdeutig | Freeze v5 verwendet lexikalisch sortierte Hashzeilen und dokumentiert exakt die Byte-/Newline-Rezeptur | offen bis Freeze-v5-Erzeugung |
| V4-12 | P3 | Dokumentation übertrieb Abschluss trotz offener Verträge | Dieser Plan markiert alle Vorreview-Resultate als vorläufig; GO erst nach Doppelreview | implementiert; Dokumentfreeze bleibt nachgelagert |
| V4-13 | P2 | Wiederholte read-only Browser-Bootstraps erschöpften das Mutationslimit | Alle GET-Requests verbrauchen kein Schreib-/Aktionsbudget; POST bleibt auf 60/Minute begrenzt | RED `200/429`, GREEN 61×GET=200 und 61. POST=429; Playwright 8/8 grün |

## 4. Geänderte transitive Produktbereiche

- `apps/web/static/app.js`: Single-Flight, Polling, fehlgeschlagener Reset, vollständiger Lifecycle-/Preview-Scrub.
- `apps/web/static/workbench-state.js`: Scanstart-/Scanlauf-/Mutationszustand.
- `apps/web/main.py`: read-only GETs außerhalb des Mutationsbudgets; Auth-/Ownership-/Resultatpfade aus früheren Remediations.
- `apps/web/reports.py`: produktiver Preview-Metadatenvertrag.
- `apps/web/scan_jobs.py`: exakte Artefaktbindung und bestätigter Prozessbaum-/Prozessgruppenstop.
- `apps/web/contracts.py`: produktive Frequenz- und Puls-/Pausengrenzen.
- `services/harmonization_worker.py`: Stop-/Save-/Cycle-Commit-Serialisierung und kooperative Impulsgrenze.
- `services/hardware_modulation.py`: kooperative Abbruchprädikate in Hardwarepfaden; zwingend in Freeze v5 aufnehmen.
- `tests/browser/`: reviewbare Playwright-Akzeptanz.

## 5. TDD- und Vorfinalevidenz

| Gate | Ergebnis |
|---|---|
| Reportpreview RED | `KeyError: 'title'` |
| Reportpreview GREEN + Reportsuite | `7 passed` |
| Read-only-Rate-Limit RED | GET-Serie ergab `{200, 429}` |
| Read-only-Rate-Limit GREEN | `3 passed`; 61 GET erfolgreich, 61. POST HTTP 429 |
| fokussierte Review-/Web-/Worker-Matrix | `104 passed in 6.94s` |
| isolierte Playwright-Matrix nach Rate-Limit-Fix | `8 passed in 11.5s` |
| erster Vollsuite-Lauf | `1221 passed, 8 skipped, 1 failed`; einziger Fehler war ein veralteter Node-Harness ohne aktive Harmonisierungsjob-ID |
| korrigierter Harness | `2 passed` in `tests/test_workbench_harmonization_status_dom.py` |
| JS-/Python-Syntax und `git diff --check` | PASS, nur bekannte LF/CRLF-Warnungen |

Diese Werte sind vorfinale Evidenz. Nach der letzten Dokument-/Harnessänderung müssen fokussierte Matrix, Vollsuite, statische Checks und isolierte Browsermatrix auf den endgültigen Freeze-v5-Kandidatenbytes erneut laufen.

## 6. Finale Regressionsleiter vor Freeze v5

1. Fokussierte Review-/Web-/Worker-Matrix einschließlich Report- und Harmonization-DOM-Tests.
2. Vollständige Suite: `python -m pytest tests -q`; null Fehler.
3. Sieben JavaScript-Syntaxprüfungen, relevante `py_compile`-Prüfungen und `git diff --check`.
4. Port 8765 frei prüfen; Ports 8000/8090 nur beobachten, nicht verändern.
5. Isolierten Uvicorn auf 8765 mit synthetischem Operator/Tenant starten.
6. Alle acht Playwright-Szenarien grün; keine Console/Page/HTTP-Fehler.
7. Server stoppen, 8765 frei bestätigen und ausschließlich generierte `node_modules`/`test-results` entfernen.
8. Danach keinerlei Produkt-, Test-, Harness- oder Plandatei patchen.

## 7. Freeze-v5-Vertrag

- Scope = vollständige aktuelle tracked Differenz plus alle nicht ignorierten produktiven Test-/Plan-/Reviewartefakte.
- Generierte `tests/browser/node_modules/` und `tests/browser/test-results/` gehören nicht in den Freeze und müssen vorher entfernt sein.
- Freeze v5 muss Freeze v1–v4, beide bytegenauen v4-Reviewberichte, Remediationpläne, Produktcode, transitive Hardwaremodulation und alle Tests enthalten.
- Hashzeilen werden lexikalisch nach relativem Pfad sortiert.
- Aggregat = SHA-256 über exakt diese sortierten Manifestzeilen mit LF-Newline, in der Reihenfolge „as listed“; keine implizite erneute Sortierung.
- Scopepopulation muss exakt Manifestpfade plus das selbstreferenzielle Freeze-v5-Manifest ergeben.
- Nach Freeze-Erzeugung sind keine Repositorypatches erlaubt.

## 8. Reviews und nachgelagerte Gates

1. Zwei neue unabhängige read-only technische Reviews prüfen alle Freeze-v5-Dateien.
2. Beide verifizieren Branch, HEAD, Manifest-SHA, Aggregat, Scope und alle Dateihashes am Anfang und Ende.
3. Bei irgendeinem P0–P3 oder Drift: Freeze v5 superseden, neue RED→GREEN-Gates und Freeze v6.
4. Nur bei zweimal Nullbefund-APPROVE: Gate-/Statusdokumentation aktualisieren.
5. Diese Dokumentänderung erhält einen separaten Dokumentfreeze und zwei weitere Nullbefund-Reviews.
6. Erst danach externe redigierte Post-State-ShadowCopy mit unabhängig verifiziertem SHA-256-Manifest.

Bis zum Abschluss aller Schritte bleibt der Status **NO-GO**.
