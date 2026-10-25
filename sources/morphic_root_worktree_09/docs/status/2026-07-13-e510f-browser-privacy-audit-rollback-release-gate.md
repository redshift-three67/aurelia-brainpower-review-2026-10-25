# E5.10F – Browser-, Privacy-, Audit- und Rollback-Gesamtfreigabe

**Stand:** 2026-07-13 09:41 CEST
**Branch:** `operator-workbench-phase1`
**Entscheidung:** **E5.10F technisch und browserseitig GO; E5.10 insgesamt GO. Geo bleibt separat NO-GO.**

## Ergebnis

Die bereits implementierte streng lokale Gruppenwirkung ist jetzt im Browser ausschließlich über eine bewusste Einzelaktivierung erreichbar. Der automatisch geladene Gruppen-Draft-Editor aktiviert keinen Scan. Erst Checkbox plus explizit ausgewählter Draft führen dazu, dass `startScanJob()` genau `group_draft_id` ergänzt; Preview, Review, Template und Browserstorage bleiben frei davon.

Ein nach der ersten Freigabe eingetroffenes unabhängiges Read-only-Audit deckte zunächst nicht vollständig belegte Post-Issue- und Artefaktpfade auf. Eine spätere gezielte Code-Review fand zusätzlich TOCTOU, nicht fail-closed geordnete Mutationen, fehlende Retention-Invalidierung, fehlende Operatorbindung des Draft-Namespace und eine mehrdeutige Kontextkodierung. GO wurde jeweils konservativ ausgesetzt. Alle Findings wurden per RED→GREEN reproduziert, minimal behoben und erneut regressionsgeprüft.

```text
bewusster Browser-Opt-in + explizite Draft-Auswahl
→ Phase1ScanRequest.group_draft_id
→ serverseitig abgeleitete subject_id
→ Draft-/Identity-/Consent-/Kontextprüfung
→ DPAPI-Root-Handle im privaten Job-Environment
→ eigener One-Time-Child-Handle je Multiplexprozess
→ ausschließlich in-memory GroupAnalysisOptIn
→ produktiver Top-N-Lauf
```

## Sicherung vor Mutation

Hash-verifizierte ShadowCopy:

`E:\mprphic_v1_Backups\morphic_v1_shadowcopy_20260713_081504_e510f`

- 18 Produktions-, Test- und Statusdateien;
- `SOURCE_MANIFEST.sha256` erzeugt;
- alle 18 Einträge unmittelbar mit `sha256sum -c` als `OK` verifiziert;
- keine Archive, Secrets oder Klientenexporte in die ShadowCopy aufgenommen.

Vor der nachträglichen Post-Issue-Härtung wurde zusätzlich angelegt:

`E:\mprphic_v1_Backups\morphic_v1_shadowcopy_20260713_084026_e510f_post_issue`

- 10 konkret betroffene Produktions-, Test- und Statusdateien;
- alle 10 Einträge per `SOURCE_MANIFEST.sha256` unmittelbar als `OK` bestätigt.

Vor der abschließenden TOCTOU-Härtung von Autorisierungs-I/O zusätzlich:

`E:\mprphic_v1_Backups\morphic_v1_shadowcopy_20260713_091315_e510f_toctou`

- `apps/web/group_analysis_runtime.py` und `tests/test_web_group_productive_activation.py`;
- beide Hashes unmittelbar als `OK` bestätigt.

Vor den abschließenden Review-Fixes zusätzlich:

`E:\mprphic_v1_Backups\morphic_v1_shadowcopy_20260713_092158_e510f_review_fixes`

- 9 konkret betroffene Produktions- und Testdateien;
- alle 9 Einträge per `SOURCE_MANIFEST.sha256` unmittelbar als `OK` bestätigt.

## Browservertrag

| Vertrag | Ergebnis |
|---|---:|
| Aktivierungscheckbox standardmäßig aus | ✅ |
| Draft-Auswahl standardmäßig leer | ✅ |
| Editor-Autoload aktiviert keinen Draft | ✅ |
| Aktivierung ohne Draft wird sichtbar blockiert | ✅ |
| nur realer Scanstart ergänzt `group_draft_id` | ✅ |
| Preview/Review/Template ohne Aktivierungs-ID | ✅ |
| localStorage/sessionStorage ohne Aktivierungs-ID | ✅ |
| Payload ohne Raten/Zentroid/Subject/Handle | ✅ |
| Kill-Switch und Stärke sichtbar | ✅ |
| 320 px ohne horizontalen Seitenoverflow | ✅ |

## Rollback- und Privacy-Matrix

| Fall | Nachweis | Ergebnis |
|---|---|---:|
| A Flag aus | `prepare_group_scan_activation` ohne Storezugriff | ✅ Baseline |
| B Stärke fehlt/0 | ohne Draft-/Identity-/Handlezugriff | ✅ Baseline |
| C gültiger Draft/Consents/Flag/Stärke | Browser-Top-3 real abgeschlossen; positiver synthetischer `AnalysisService`-Effekttest | ✅ Wirkung |
| D Draft-Analyseconsent false | Draft-/Resolution-Tests | ✅ fail-closed |
| E Subject nicht Mitglied | Draft-Autorisierung | ✅ fail-closed |
| F Consent fehlt/widerrufen/abgelaufen | Identity-Source-/Revocation-Tests; Widerruf invalidiert bereits ausgegebene Kontext-Handles | ✅ fail-closed |
| G fremder Owner/Workspace/Tenant | Handle- und Draft-Namespace binden kanonisch an Operator, Workspace und Tenant | ✅ fail-closed |
| H Handle abgelaufen/manipuliert/wiederverwendet | Handle-Store-/Runtime-Tests | ✅ fail-closed |
| I Kill-Switch nach Aktivierung aus | neue Aktivierung wird vor Storezugriff inert | ✅ Baseline |
| J Identity-/Draft-/Retention-Erasure | Invalidierung ist zwingende Vorbedingung der Mutation; kontextgebundene DPAPI-Generation wird rotiert, stale Fan-out kann keine Child-Handles ausgeben | ✅ inert |
| K Response/Snapshot/Trace/Audit/Report/Manifest | realer Run; 51 Runtime-/Report-/Manifest-/Logdateien inklusive 10 PDF-Textextraktionen geprüft | ✅ 0 Leaks |
| L Desktop/320 px/Cleanup | Playwright + gezielte Nachkontrolle | ✅ |

## Reale Browserabnahme

### UI-/Payload-/Responsive-Lauf

Playwright gegen den ausschließlich für E5.10F gestarteten Loopback-Port `52923`:

- Kill-Switch sichtbar freigegeben;
- Initialzustand: Checkbox `false`, Draftwert leer, „Keine produktive Wirkung“;
- zwei synthetische DPAPI-Identitäten mit aktuellen Einzelconsents registriert;
- synthetischer Draft gespeichert;
- nach Reload Editor geladen, Aktivierungsselect weiterhin leer;
- Stärke `0.25` gesetzt;
- Aktivierung ohne Draft sichtbar blockiert;
- nach bewusster Auswahl Status „Bereit“;
- realer Startpayload enthielt `group_draft_id`, aber keine verbotenen Gruppen-/Handlefelder;
- Template und localStorage enthielten weder Draft-ID noch `group_draft_id`;
- 320-px-Nachweis: `viewport=320`, `rootWidth=320`, Panelbreite `213.33`, Selectbreite `176`.

Zwei Browser-Konsolen-404 stammten aus dem absichtlich abgefangenen Fake-Job-Poll/Favicon-Pfad und nicht aus der Aktivierungs-UI.

### Reale produktive Browserausführung

Aktivierter Top-3-Lauf:

```text
job_id: scan-20260713-090028-e89e0fa5
Statusfolge: running → completed
Endstatus: completed
Fortschritt: 100 %
letzter Substep: Trendbericht erstellt
```

Der Lauf durchlief Screening, vollständige Analysen sowie Deutungs-, Remedy-, Synergy- und Trendpfade. Nach Abschluss waren keine `gah-*.dpapi`-Handles mehr im synthetischen Runtime-Verzeichnis vorhanden.

Die realen Job-, Run-Trace- und Resultresponses enthielten nicht:

- Draft-ID oder Gruppenlabel;
- den zweiten Gruppenmember;
- Handle/`gah-`;
- `activation_handle`, `group_member_rates` oder `group_centroid`.

Der vorhandene `review.client_id` des gescannten Klienten blieb sichtbar. Das ist der bereits vor E5.10 vorhandene pseudonyme Einzelklientenschlüssel und weder eine Gruppenmitgliedsliste noch ein Aktivierungsfeld.

Vor dem Cleanup wurden 51 reale Dateien inhaltlich geprüft: 12 Runtime-/Job-/Trace-/Auditdateien sowie 39 neu erzeugte HTML-, JSON-, TXT-, PDF-, Report- und Manifestartefakte. Die zehn PDFs wurden zusätzlich mit `pdftotext` extrahiert. Suchumfang: synthetische Draft-ID, Gruppenlabel, zweiter pseudonymer Member, `group_draft_id`, `activation_handle`, `centroid_rates` sowie kanonische `gah-*`-Handles. Ergebnis: `PASS`, 0 Verstöße.

### Post-Issue-Erasure-Härtung

- Jeder Operator-/Workspace-/Tenant-Kontext besitzt eine zufällige, DPAPI-geschützte Aktivierungsgeneration.
- Root- und Child-Handles tragen diese Generation ausschließlich innerhalb des geschützten Handle-Stores.
- Ungebundene Root-Autorisierungen ohne Generation werden abgewiesen; die Webvorbereitung erfasst die Generation vor Draft-/Identity-/Consent-I/O.
- Consent-Widerruf, produktive Draft-Löschung oder Identity-Erasure rotieren die Generation und löschen vorhandene Kontext-Handles.
- Draft-, Consent-, explizite Identity- und Retention-Mutationen erfolgen erst nach erfolgreicher Invalidierung; schlägt diese fehl, bleiben die fachlichen Daten unverändert.
- Draft-Namespace und Generation-Hash verwenden den vollständigen Kontext und eine kanonische, kollisionsfreie Tupelkodierung.
- Ein bereits in-memory konsumierter Root-Opt-in trägt die alte Generation; nach Rotation wird die Ausgabe weiterer Child-Handles fail-closed mit `LookupError` verweigert.
- Fremde Operator-/Workspace-/Tenant-Kontexte bleiben unangetastet.
- Die Generation überschreitet weder Worker-, API-, UI-, Report-, Trace- noch Manifestgrenzen.

## TDD- und Regressionsevidenz

| Prüfung | Reales Ergebnis |
|---|---:|
| neuer Browservertrag RED | `4 failed` wegen fehlender Controls/Verdrahtung |
| Browser-/Draft-/Policy-/Persistence-Fokus GREEN | `12 passed` |
| E5.10E/F-/Web-/Release-Fokus | `71 passed` |
| Rollback-/Privacy-Matrixfokus | `74 passed` |
| finaler betroffener Fokus | `49 passed` |
| Post-Issue-Erasure RED | `4 failed` wie spezifiziert |
| Post-Issue Handle/Draft/Consent/Erasure GREEN | `44 passed` |
| Post-Issue TOCTOU RED/GREEN | `1 failed` → relevanter Fokus `40 passed` |
| abschließende Review-Findings RED | `6 failed`; ungebundene Root-Autorisierung separat `1 failed` |
| Review-/Post-Issue-Fokus GREEN | `76 passed` |
| Rest-Suite ohne Top-5 nach finaler Härtung | `481 passed, 2 skipped, 13 failed` |
| bekannte gemeinsame HTTP-429-Ausreißer | 13; jeweils in frischem Einzelprozess `1 passed` |
| Top-5-Smoke nach finaler Härtung | `1 passed in 95.40s` |
| Python-Compile | Exit 0 |
| `node --check` (app/API/state) | Exit 0 |
| `git diff --check` | Exit 0; nur bekannte LF→CRLF-Hinweise |

Der gemeinsame Rest-Suite-Lauf wird ausdrücklich nicht als vollständig grüner Einzelprozess dargestellt. Alle 13 Fehler waren HTTP 429 des bekannten globalen Test-IP-Rate-Limiters; dieselben 13 Node-IDs bestanden anschließend jeweils in einem frischen Python-Prozess. Es blieb kein funktionaler Einzeltestfehler offen.

### Unabhängiger Re-Review

Der nach allen Review-Fixes erneut ausgeführte strikt read-only Code-Review endete mit:

```text
Verdikt: APPROVE
Konfidenz: HOCH
Neue P0–P2-Befunde: keine
```

Bestätigt wurden insbesondere die verpflichtende Root-Generation, die Bindung vor Autorisierungs-I/O, die fail-closed Reihenfolge aller vier Mutationspfade, vollständige Operator-/Workspace-/Tenant-Isolation sowie die kanonische Kontextkodierung.

## Gezielter Cleanup

Nach der Abnahme:

- Testserver auf `127.0.0.1:52923` beendet;
- synthetisches Runtime-Verzeichnis entfernt;
- exakt `e510f-browser-synthetic.dpapi` entfernt;
- ausschließlich die erzeugte Top-3-Session `20260713_082855` plus zugehörige Deutung/Remedy/Synergy/Trend-Artefakte entfernt;
- temporäre Playwright-/Server-Skripte und Screenshots entfernt;
- Nachsuche nach `20260713_082855`, `20260713_082902`, `20260713_082907` und `e510f-browser-synthetic`: jeweils 0 Treffer;
- Port 8090 und bestehende Prozesse unverändert gelassen.

Nach dem zweiten realen Lauf zusätzlich:

- Testserver und isolierte Runtime `morphic-e510f-postissue-20260713-084026` entfernt;
- exakt `e510f-postissue-synthetic.dpapi` entfernt;
- ausschließlich die neu erzeugten Zeitstempel `20260713_090037`, `20260713_090043` und `20260713_090048` entfernt;
- Nachsuche über alle drei Zeitstempel, den Draftnamen und temporäre E5.10F-Skripte: jeweils 0 Treffer.

Bestehende ältere Deisenhofer-/Klaus-Testartefakte wurden nicht pauschal gelöscht.

## Verbleibende Grenzen

- `OperatorContext` bleibt eine lokale Vorbereitungsschicht und ist keine echte Authentifizierung.
- Die produktive Gruppenwirkung bleibt streng lokal, default-inaktiv und vom serverseitigen Kill-Switch abhängig.
- Geo ist weiterhin vollständig unverdrahtet und separat NO-GO.
- Kein Commit, Push, Reset, Clean oder Staging wurde durchgeführt.

## Finale Entscheidung

```text
E5.10A–E: technisch GO
E5.10F: GO
E5.10 gesamt: GO
Feedback e – Gruppenpfad: abgeschlossen
Geo: separat NO-GO
```
