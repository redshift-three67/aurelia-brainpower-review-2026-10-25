# Operator Workbench Korrekturen a–p – konsistenter Umsetzungsplan

> **Für Hermes:** Diesen Plan ausschließlich gateweise, testgetrieben und mit `hash-bound-change-control` ausführen. Noch keine Umsetzung, kein Commit, kein Push und kein Neustart der geschützten Prozesse ohne Freigabe.

**Ziel:** Die neu gemeldeten Bedien-, Profilpool-, EMF-, Berichts-, Archiv-, Harmonisierungs- und Verwaltungsanforderungen beheben, ohne Scan-/Scoring-Präzision, Datenschutz, Tenant-/Owner-Isolation oder den zuletzt grünen Workbench-Stand zu destabilisieren.

**Architektur:** Zuerst wird der tatsächlich laufende Serverstand mit dem aktuellen Worktree in Einklang gebracht. Danach folgen voneinander getrennte TDD-Gates für UI-Wahrheit, EMF-Autorität, Berichtsdatenmodell, Archivhierarchie, optionale Profilkontexte, V1-Harmonisierungsparität, Admin-Catalog und ausschließlich experimentelle Quantum-/Realtime-Erweiterungen. Historische Referenzen werden nur strukturell übernommen; das aktuelle visuelle Reportdesign bleibt erhalten.

**Tech Stack:** FastAPI/Pydantic, Vanilla JavaScript/CSS, pytest, Playwright mit lokalem Chrome, ReportLab, lokales Ollama, bestehender AdminCatalog, optional Qiskit ausschließlich hinter Benchmark-/Opt-in-Gates.

---

## 1. Geltungsbereich und unveränderliche Sicherheitsregeln

- Aktiver Worktree: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
- Branch: `operator-workbench-phase1`
- HEAD bei Planerstellung: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Worktree bleibt absichtlich dirty; kein Reset, pauschales Cleanup, Staging, Commit oder Push.
- Port 8090/PID 17136 (Radi144) bleibt unangetastet.
- Port 8765/PID 12992 (Benutzerserver) wird erst in Gate 0 nach ausdrücklicher Ausführungsfreigabe kontrolliert neu gestartet.
- Für isolierte Browserabnahmen wird ausschließlich ein vorher geprüfter freier Port verwendet; eigener Prozess wird danach beendet.
- Keine echten Klientendaten in Tests. Nur synthetische Identitäten und isolierte Report-/Runtime-Wurzeln.
- Keine Änderung bestehender Scoreformeln in diesem Plan. Anzeigeformatierung bleibt eine Präsentationsschicht.
- Neue optionale Angaben oder Profilfilter sind standardmäßig neutral/deaktiviert und müssen bei Nichtverwendung bit-/payload-äquivalent zum bestehenden Pfad bleiben.
- EMF bleibt default-off und darf nicht als physische Feldmessung bezeichnet werden, solange nur Systemlast, RNG, Timing-Jitter und Sensor-Fallbacks vorliegen.
- Kein Onlineadapter, keine automatische Catalog-Promotion und keine produktive Catalog-Umschaltung durch diese Korrekturrunde.
- Kein finales Post-State-Backup vor den technischen und dokumentgebundenen Freigaben. Die unten dokumentierte Pre-Plan-Absicherung ist ausschließlich Rollback-/Evidenzsicherung.

## 2. Verifizierte Pre-Plan-Absicherung

Externe, privacy-beschränkte Evidenzsicherung:

- Pfad: `C:\Users\Hubert111\Documents\Morphic_Safeguards\2026-07-21_151323_operator-workbench-preplan`
- Kopierte Dirty-Source-/Test-/Reviewdateien: `183`
- Kopierte Bytes: `1.656.932`
- Ausgeschlossen: Runtime-/Jobdaten, Benutzerarchive, Browserabhängigkeiten/-resultate, Caches, Lockfile und credential-sensitiv benannte Dateien.
- Manifest: `SOURCE_MANIFEST.sha256`
- Manifest-SHA-256: `738dabe6dd0e63f2e193c6b8729714aa77e88ba7c24efc441d4cf3b16a253bb0`
- Re-Read- und Source-vs-Copy-Verifikation: `PASS`

Diese Sicherung ist kein technischer Freeze und keine finale ShadowCopy.

## 3. Verifizierter Ist-Zustand zu den Punkten a–p

| Punkt | Verifizierter Stand | Konsequenz |
|---|---|---|
| a | `GET http://127.0.0.1:8765/api/workbench/scan-profile-catalog?profile_level=4` liefert `404`. Gleichzeitig ist die ausgelieferte `app.js` bytegleich mit dem Worktree (`9118034b…`). PID 12992 läuft mit globalem Python 3.12 statt Projekt-`.venv`. | Kein primärer Datenfehler: Der laufende Python-Prozess hat die später ergänzte Route nicht importiert. Kontrollierter Neustart plus Startskript-/Versionstransparenz zuerst. |
| b | Viele Optionen besitzen bereits Hinweise, aber Adaptive Limits, Harmonisierungs-Hardwareoptionen, Intention, Frequenz, Persistenzaktionen und einige fortgeschrittene Funktionen sind nicht einheitlich erklärt. | Ein zentraler Options-Erklärungsvertrag statt weiterer vereinzelter Texte. |
| c | Backenddefault ist `adaptive_limits=False` (`apps/web/contracts.py:28`), HTML ist aber `checked` (`apps/web/static/index.html:369`). Aktivierung kann den Phase-2-Detailumfang auf `min(top_k, max(32, top_n*16))` begrenzen (`apps/cli/commands/scan.py:496-501`) und begrenzt zusätzlich sichtbare Resultate auf höchstens 5 (`apps/web/display_scores.py:8,19-23`). | HTMLdefault auf aus; beide Wirkungen und ein Beispiel erklären. Die Scoreformel bleibt unverändert, die Auswahl der detailliert analysierten Profile kann sich bei entsprechend großem `top_k` aber ändern. |
| d | `GET /api/emf/status` meldet `{"active":false}`. Default-off ist absichtlich (`apps/web/main.py:353-358`). Aktivierung existiert nur als geschütztes `POST /api/emf/enable`; die Workbench bietet keinen Bedienpfad. | Explizite Aktivieren/Deaktivieren-Bedienung mit Status-/Quellenwahrheit. Kein Auto-Enable. |
| d / Radi144 | Morphic `EMFProfileService` und Radi144 verwenden primär RNG-/Timing-/Systemlast-/Sensor-Proxywerte; Radi144 beschreibt RTL-SDR nur als spätere Pluginoption. | UI-Bezeichnung muss „System-/Entropie-basierter EMF-Proxy“ lauten, solange keine bestätigte Feldsensorquelle aktiv ist. |
| e | Screenshot zeigt Level 4 und dauerhaft „Scanprofil-Pool wird geladen“. Eine read-only Direktauswertung der aktuellen autoritativen Funktion ergab bei Planerstellung Level 1=`5`, Level 2=`35`, Level 3=`55`, Level 4=`208`; diese Zahlen sind Evidenz, keine künftig hartcodierte Produktkonstante. Das Payload kann Namen liefern, erreicht den alten Serverprozess aber nicht. | Nach Restart: dynamisch aus der Autorität abgeleitete Zusammenfassung, Herkunft, Ergebnisziel, Such-/Detailansicht und klare Fehler-/Retryzustände. |
| f | Zwei Links führen aus dem primären Workflow zum Systemmodell: `Systemmodell oeffnen` in `apps/web/static/index.html:463` und `Systemfluss ansehen` in `apps/web/static/index.html:644`. | Beide Links vollständig aus der primären Workbench entfernen; die separate Dokumentationsroute darf intern bestehen bleiben. |
| g | Der aktuelle Scan ruft `tools.interpretation_generator` bereits mit `--llm` auf (`apps/cli/commands/scan.py:1777-1801`). Bei fehlendem Ollama wird regelbasiert zurückgefallen, aber der Bericht kann dies fälschlich als „KI-Text generiert“ darstellen (`tools/interpretation_generator.py:295-301`). Der direkte Toolpfad nutzt die stärkere Post-LLM-Compliance des historischen CLI-Wrappers nicht. Die read-only geprüfte Referenz `E:\Backup Morphic\morphic_v1\Mustermann` enthält 22 HTML-Berichte mit 316 Tabellen und wiederkehrenden Abschnitten für Fokus/Symptom, Basis-Metriken, Resonanzwerte, Subgruppen, Einflussfaktoren, Deutung, Quantum-Trigger und Harmonisierungsschritte; sie ist strukturell reich, aber stark tabellenlastig. | Kein blindes „LLM wieder einbauen“ und kein Kopieren des alten Designs, sondern Statuswahrheit, explizites lokales Opt-in, strukturierte Ausgabe, Post-LLM-Compliance, reproduzierbare Provenienz und responsive Neuordnung der bewährten Inhaltsabschnitte. |
| h | `core/client_profile.py` kennt ein optionales `gender`, der aktive Web-/Scanpfad verdrahtet es nicht verlässlich. `schwangerschaft_wechseljahre` bündelt Schwangerschaft und Wechseljahre (`core/profile_sync/__init__.py:1396-1410`). | Machbar, aber nur als expliziter, neutraler Profilkontext und zunächst Metadata-/Shadow-Gate. Keine automatische Namensableitung und keine sofortige Scoregewichtung. |
| i | Live-API meldet aktuell 188 Dateien: 48 HTML, 45 PDF, 42 JSON, 53 TXT in 11 Sessions. HTML ist inline darstellbar; PDF wird bewusst nur verlinkt, JSON/TXT als Text behandelt. | Operatorliste standardmäßig auf HTML-Berichte reduzieren. JSON/PDF bleiben Archiv-/Exportartefakte, nicht primäre Inline-Berichte. |
| j | PDF wird durch strukturelle HTML-Extraktion in ReportLab rekonstruiert (`tools/pdf_exporter.py`), nicht aus derselben visuellen Rendering-Engine gedruckt. Dadurch kann Inhalt/Layout von HTML abweichen. | Einen kanonischen Report-Inhaltsvertrag verwenden und PDF-Struktur mit Raster-/Text-/Seitenbruchtests gegen HTML prüfen. |
| k UI | Berichtskatalog steht links neben der Vorschau (`index.html:532-560`, `app.css:889-892`). | Katalog oben als horizontale/kompakte Auswahl, Preview darunter über volle Breite. |
| k Archiv | Der aktuelle Helper schreibt `ReportType / ClientSlug` (`tools/reporting_common.py:461-486`); Catalog versteht ebenfalls Type-first. Gewünscht ist `Client / Session / ReportType`. | Neue kanonische Hierarchie plus dual-read und kopierende, hashverifizierte Migration; niemals In-place-Move als erster Schritt. |
| l | Das zentrale HTML-Theme ist bereits responsive, einzelne Reportgeneratoren und große Tabellen nutzen aber unterschiedliche Inhaltsstrukturen. PDF ist naturgemäß A4 statt responsiv. | Ein gemeinsames semantisches Reportmodell; HTML adaptiv, PDF sauber paginiert. |
| m | V1-Ursequenz: Opt-in Harmonisierung, Defaults 21s Impuls/42s Pause, Faktor ×21 Min, Auswahl hohe/mittlere Priorität, Label-Deduplizierung, Score-Sortierung, max. 20 Items und Rundenermittlung (`Run-MultiplexScan.ps1:897-1099`). Webdefault ist derzeit 3s/2s und Backendgrenze max. 5s. | Eigener Paritätsgate; nicht gemeinsam mit Berichts- oder Scoreänderungen umsetzen. |
| n | Eine getrennte, adminauth-geschützte Admin-Catalog-API und Admin-UI existieren bereits technisch (`apps/web/admin_catalog.py`, `static/admin.html`, Status F6.4). Runtimeadapter bleibt standardmäßig Legacy; Shadow/Catalog-Aktivierung ist separat gegatet. | Keine zweite Verwaltung bauen. Bestehende Adminoberfläche sicher fertigstellen/freigeben und Poolquelle in der Workbench transparent machen. |
| o | Grover/Qiskit existiert bereits für Synergy (`core/quantum_synergy/grover_search.py`, `workflow/step09_quantum.py`). Das Oracle markiert Kandidaten zunächst klassisch O(N), anschließend läuft Qiskit typischerweise im Simulator. | Kein belegter schnellerer Scan. Nur Benchmark-/Experimentalgate; keine Integration in Kernranking ohne messbaren Vorteil und Ergebnisäquivalenz. |
| p | Scanpolling, Hardwaretruth, EMF-WebSocket und Harmonisierungstelemetrie existieren fragmentiert. | Ein gemeinsames, wahrheitsgebundenes Live-Dashboard mit textuellem Fallback; nur aktive Quellen visualisieren. |

## 4. Zielarchitektur

```text
Klienteneingabe
  ├─ Pflichtdaten
  ├─ optionale lokale Kontexte (separat, consent-bound)
  └─ optionaler Profilkontext: alle / weiblich / männlich / divers-kein Filter
         ↓
Scan-Konfiguration
  ├─ Level → autoritativer interner Pool
  ├─ optionale, tatsächlich runtime-aktive Catalog-Profile
  ├─ Top-N Ergebnisziel
  └─ Adaptive Limits default AUS
         ↓
Review
  ├─ Poolquelle + Revision
  ├─ Anzahl intern/extern
  ├─ durchsuchbare Profildetails
  └─ klare Fehler-/Retry-/Stale-Server-Zustände
         ↓
Scan → kanonische Session-ID → kanonisches Reportmodell
         ↓
ArchiveRoot / ClientSlug / SessionId /
  ├─ Resonanz/
  ├─ Deutung/
  ├─ Remedies/
  ├─ Synergy/
  └─ Trends/
         ↓
HTML (responsive Primärbericht) + PDF (paginiert) + JSON (Maschinenartefakt)
         ↓
optional: V1-paritätsgebundene Harmonisierung
```

## 5. Umsetzungsreihenfolge

### Gate 0 – Laufenden Serverstand kontrolliert angleichen (Punkt a/e)

**Ziel:** Beweisen, dass der Poolfehler durch Prozess-/Routenstand entsteht, und den Benutzerserver ohne Portkollision auf den geprüften Worktreestand bringen.

**Dateien:**
- Neu: `tests/test_workbench_runtime_version_contract.py`
- Optional neu: `scripts/run_operator_workbench.ps1`
- Ändern nur falls nötig: `apps/web/main.py`, `apps/web/workbench.py`, `apps/web/static/app.js`, `apps/web/static/workbench-api.js`, `apps/web/static/workbench-state.js`, `apps/web/static/workbench-render.js`

**RED-Verträge:**
1. Runtime-Info enthält Build-/HEAD-/Startzeitkennung ohne interne Pfade oder Secrets.
2. `scan-profile-catalog` liefert für Level 1–4 exakt dieselben Profile/Anzahlen wie `get_top_n_analysis_profiles_by_level(level)`; die bei Planerstellung gemessene Legacy-Baseline 5/35/55/208 wird als Evidenz, nicht als Produktlogik festgehalten.
3. Browser unterscheidet 404/401/422/503/Timeout und zeigt Retry statt dauerhaftem „wird geladen“.
4. Ein verspäteter Katalogresponse überschreibt weiterhin keine neuere Auswahl.
5. Katalogzustand ist explizit `loading|ready|error` statt mehrdeutigem `null`; der Catch-Zweig rendert Phase 1 und die Reviewkarte terminal neu.
6. Unabhängige Bootstrap-Reads laufen parallel und isoliert; Event-Listener werden vor Netzwerk-I/O registriert. Jeder Request besitzt Timeout/`AbortController`, ohne dass ein hängender Health-/Sources-Request den Katalog blockiert.
7. Bekannte `SourceRegistryError`-/Datei-/Strukturfehler werden serverseitig in einen redigierten HTTP-503-Vertrag übersetzt; keine internen Pfade im Response.
8. Level, Requesttoken und Katalogfingerprint bleiben gemeinsam gebunden; alte Daten werden sichtbar als veraltet markiert und können keinen Scanstart autorisieren.

**GREEN:**
- Offizielles Startskript nutzt ausschließlich `C:\morphic_v1\.venv\Scripts\python.exe`.
- Vor Neustart: Port/PID/Commandline dokumentieren; danach Readiness prüfen; bei Fehler sofort alter Prozessstartbefehl als Rollbackanweisung bereithalten.
- Benutzerserver erst nach ausdrücklicher Ausführungsfreigabe beenden.

**Abnahme:**
- `GET /api/workbench/scan-profile-catalog?profile_level=4` → 200 und Count/Namen entsprechen im selben Prozess der aktuellen autoritativen Profilfunktion; kein hartcodierter Count.
- Kein Reload-Loop, keine Konsolenfehler, Ports 8090 und andere geschützte Ports unverändert.

### Gate 1 – Einheitlicher Erklärungsvertrag für optionale Funktionen (Punkt b)

**Ziel:** Jede optionale oder wirkungsändernde Funktion erhält in leicht verständlicher Sprache: Zweck, Standardzustand, Auswirkung, Nichtauswirkung und Datenschutz-/Hardwaregrenze.

**Dateien:**
- `apps/web/static/index.html`
- `apps/web/static/workbench-render.js`
- `apps/web/static/app.css`
- Neu: `tests/test_workbench_option_explanations.py`
- `tests/browser/workbench.spec.js`

**Pflichtinventar:** Fokus-Historie, Hauptsymptom, Geburtszeit/E-Mail/Notizen, Referenzbild, planetarer Vektor, Profilvorlage, Entropiemodus, Adaptive Limits, Workbench Expert, EMF, lokale KI-Deutung, Profilkontext, Harmonisierungsintention, Frequenz, Impuls/Pause, Dauerfaktor, CPU/GPU/RAM/WebSocket/Driver Layer, Templatepersistenz. Technische Begriffe wie DPAPI, Kill-Switch, Policy-Kandidat und Gruppenstärke erhalten eine alltagssprachliche Übersetzung; lokale Optionen nennen Speicherortklasse, Aufbewahrung, Löschweg und Wirkung auf den aktuellen Scan. Die mögliche Maximaldauer von 441 Minuten muss vor Harmonisierungsstart prominent bestätigt werden.

**Vertrag:** Kein optionales Control ohne zugeordneten Hint (`aria-describedby`) und explizites „Standard: aus/neutral“, sofern zutreffend.

### Gate 2 – Adaptive Limits default-off und verständlich (Punkt c)

**Ziel:** UI und Backenddefault angleichen.

**Dateien:**
- `apps/web/static/index.html:369`
- `apps/web/static/app.js`
- `apps/web/launcher.py`
- `apps/cli/commands/scan.py`
- `apps/web/display_scores.py`
- `tests/test_web_display_scores.py`
- `tests/test_topn_cli_phase1_options.py`
- `tests/browser/workbench.spec.js`

**RED:**
- Erstladung und „Neuer Fall“ ergeben `adaptive_limits=false`.
- Ohne Adaptive Limits bleibt der angeforderte `top_k` für die Phase-2-Detailanalyse unverändert; mit Opt-in gilt der bestehende Cap `min(top_k, max(32, top_n*16))`.
- Mit Opt-in wird zusätzlich der sichtbare Ergebnis-/Berichtsumfang auf höchstens 5 begrenzt.
- Die Scoreformel bleibt unverändert; Tests müssen aber ausdrücklich belegen, dass eine durch den Opt-in verkleinerte Detailkandidatenmenge die Ergebnisauswahl ändern kann und daher im Review sichtbar ist.

**GREEN-Copy:** „Alle Profile des gewählten Levels werden zunächst gescreent. Adaptive Limits kann danach bei großem internen Detailumfang die Zahl der vollständig weiteranalysierten Profile auf `max(32, Top-N × 16)` begrenzen und zeigt im Ergebnis/Report höchstens 5 Treffer. Die Scoreformel selbst wird nicht verändert; durch die kleinere Detailauswahl können sich die finalen Treffer ändern. Standard: aus.“

### Gate 3 – Scanprofil-Pool als verständliche Entscheidungshilfe (Punkt e)

**Ziel:** Die Reviewkarte zeigt nicht nur einen Ladezustand, sondern den konkreten geplanten Screeningumfang.

**Dateien:**
- `apps/web/workbench.py`
- `apps/web/static/workbench-render.js`
- `apps/web/static/index.html`
- `apps/web/static/app.css`
- `tests/test_web_scan_profile_catalog.py`
- `tests/test_workbench_render_js.py`
- `tests/browser/workbench.spec.js`

**UI-Vertrag:**
- Zusammenfassung verwendet ausschließlich das aktuelle Responsepayload, z. B. „Level 4 prüft 208 Profile; angezeigt werden anschließend Top-5“; die Zahl wird niemals im Frontend hartcodiert.
- Badges: Poolquelle `Legacy`, `Catalog Shadow` oder `Catalog aktiv`; Revision nur in sicherer Kurzform.
- Intern/extern strikt getrennt; aktive Registry-Quellen sind keine gescannten Profile.
- `<details>` mit alphabetischer, durchsuchbarer Profilliste, Namen und optional sicherer Kategorie.
- Bei Fehler: HTTP-Klasse, verständlicher Grund, „erneut laden“, kein falscher Nullpool.
- Laden mit Timeout und Skeleton; Analyse darf bei unbekanntem Pool nicht so aussehen, als sei er bestätigt.
- Screenshot-Abnahme für Desktop, Tablet und 375px.

### Gate 4 – Primärworkflow vereinfachen (Punkt f und Berichtslayout k)

**Ziel:** Dokumentationslink entfernen und Reportpreview priorisieren.

**Dateien:**
- `apps/web/static/index.html:463,532-560,640-645`
- `apps/web/static/app.css:889-1029`
- `tests/test_workbench_dogfood_reports_harmonization.py`
- `tests/browser/workbench.spec.js`

**GREEN:**
- `Systemmodell oeffnen` und `Systemfluss ansehen` vollständig aus dem primären Workflow entfernen.
- Katalog oberhalb der Vorschau; horizontal scrollbar/kompakt auf Desktop, gestapelt auf Mobil.
- Preview darunter über volle Panelbreite; keine Sticky-Seitenspalte.
- Tastaturfokus und `aria-pressed` bleiben erhalten.

### Gate 5 – EMF-Aktivierung und Quellenwahrheit (Punkt d)

**Ziel:** Operator kann die vorhandene Telemetrie bewusst aktivieren/deaktivieren und versteht ihre technische Grenze.

**Dateien:**
- `apps/web/emf.py`
- `apps/web/emf_authority.py`
- `web_app.py` (Legacy-Entry-Point nur dekommissionieren oder auf dieselbe Autorität delegieren; keine zweite Aktivierungswahrheit belassen)
- `apps/web/workbench.py`
- `apps/web/static/workbench-api.js`
- `apps/web/static/app.js`
- `apps/web/static/workbench-render.js`
- `apps/web/static/index.html`
- `tests/test_web_emf_security.py`
- `tests/test_emf_enable_authority.py`
- `tests/browser/workbench.spec.js`

**RED:**
1. Seitenaufruf aktiviert EMF nie automatisch.
2. Expliziter Button ruft geschütztes POST auf; UI revalidiert Status und Hardwaretruth.
3. Deaktivieren entzieht bestehende Lease; spätere Messung/WebSocket-Sendung bleibt gesperrt.
4. Fehlende/ungültige Messwerte erzeugen kein `0` und keine Gauge.
5. UI zeigt Quelle pro Teilwert (`rng`, `cpu_timing`, `system_load`, `sensor_entropy`) und Fallbackstatus.
6. Legacy-`/api/v1/emf/*` und dessen WebSocket dürfen die neue Autorität weder durch prozesslokales Boolean noch durch Connect-Auto-Enable umgehen; Launcher-/Route-Abdeckung statisch und behaviorbasiert prüfen.

**Bezeichnung:** „System-/Entropie-basierter EMF-Proxy-Index“. Erst bei bestätigter physischer Sensorquelle darf eine andere Bezeichnung erscheinen. Radi144-Code wird nicht importiert.

**Bedienung:** Default aus, „Aktivieren“ mit kurzer Erklärung, „Deaktivieren“, Status „aktiv bis manuell deaktiviert“ beziehungsweise definierte Sessionpolicy. Kein medizinischer Belastungsclaim.

### Gate 6 – Berichtskatalog auf nutzerrelevante HTML-Berichte fokussieren (Punkt i)

**Ziel:** Der Katalog zeigt standardmäßig nur die nutzbaren HTML-Berichte pro Klient/Session.

**Dateien:**
- `apps/web/main.py`
- `apps/web/reports.py`
- `apps/web/static/app.js`
- `apps/web/static/workbench-render.js`
- `apps/web/static/index.html`
- `tests/test_web_reports.py`
- `tests/test_web_catalog_client_view.py`
- `tests/browser/workbench.spec.js`

**Vertrag:**
- Primärliste enthält nur HTML/HTM.
- `/api/reports` erhält einen expliziten, getesteten Primärlistenvertrag statt des heutigen fest verdrahteten `include_all_formats=True`; ein eventueller Expertenmodus für alle Formate ist separat und default-off.
- JSON bleibt Maschinen-/Audit-/Migrationsartefakt, nicht Inline-Nutzerbericht.
- PDF bleibt Exportartefakt; kein scheinbar defekter Inline-Modus.
- Optionaler Expertenhinweis nennt vorhandene Exportartefakte nur als Anzahl, ohne lokale Pfade.
- HTML-Preview bleibt sandboxed, CSP-sicher und selection-token-gebunden.

### Gate 7 – Kanonisches Report-Inhaltsmodell und Deutungsanalyse (Punkt g/l)

**Ziel:** Strukturqualität der historischen Berichte zurückgewinnen, ohne altes Design oder ungeprüfte Aussagen zu übernehmen.

**Dateien:**
- Neu: `tools/report_model.py`
- `apps/cli/commands/scan.py`
- `apps/cli/commands/field.py`
- `tools/interpretation_generator.py`
- `tools/synergy_consolidator.py`
- `tools/remedy_reporter.py`
- `tools/trend_analyzer.py`
- `tools/reporting_common.py`
- Neu: `services/compliance_gate.py` (fachliche Vorlage ausschließlich read-only aus dem historischen V1-Pfad prüfen; nicht blind kopieren)
- Neu: `tests/test_report_model_contract.py`
- Neu: `tests/test_interpretation_llm_contract.py`

**Kanonische Abschnitte:** Titel/Session, Klientenkontext (minimal), Fokus, Methodik/Quellen, Profilübersicht, priorisierte Resonanzen, Cross-Profil-Muster, Remedies, Synergy, Trends, Deutung, lokale KI-Einordnung, Grenzen/Wellbeing-Hinweis, technische Provenienz.

**Historische Strukturreferenz:** Aus `E:\Backup Morphic\morphic_v1\Mustermann` ausschließlich die bewährte Informationsgliederung ableiten: Fokus/Symptom, Basis-Metriken, Resonanzwerte, verwendete Subgruppen, Einflussfaktoren, Deutung, Quantum-Trigger, Synergy/Remedies und nachvollziehbare nächste Schritte. Die 316 historischen Tabellen, alte CSS-Klassen, personenbezogene Inhalte und experimentelle Wirkformulierungen werden nicht übernommen; moderne Karten, progressive Offenlegung und das aktuelle Reportdesign bleiben maßgeblich.

**LLM-Vertrag:**
- explizites lokales Opt-in; standardmäßig aus, bis die Datenschutzentscheidung separat bestätigt ist;
- nur lokales Ollama auf konfigurierter Loopback-Origin; keine externe API;
- Prompt enthält keine Namen, Geburtsdaten, Pfade oder Credentials; Fokus nur bei explizitem Analyseconsent;
- strukturierte JSON-Ausgabe mit erlaubten Abschnitten statt ungebundenem Fließtext;
- Modellallowlist (z. B. `phi3`) und dokumentierte Modellversion;
- kein stilles Ausweichen auf das erste installierte Ollama-Modell; Modellabweichung ist fail-closed oder wird als nicht verwendeter Fallbackgrund ausgewiesen;
- Statusfelder unterscheiden `requested`, `available`, `used`, `rule_based_fallback`, `failed`;
- Post-LLM-Compliance läuft im tatsächlich produktiven Toolpfad vor HTML/PDF;
- HTML escaped alle LLM-Inhalte;
- Scores/Quellbefunde bleiben autoritativ; LLM darf sie weder neu berechnen noch erfinden.

**Qualitätsgate:** Synthetisches Golden-Set vergleicht Abschnittsvollständigkeit, Quellenbindung und Compliance, nicht subjektive „medizinische Genauigkeit“.

### Gate 8 – PDF-Strukturparität (Punkt j)

**Ziel:** PDF und HTML beruhen auf demselben Reportmodell; PDF bleibt A4-paginiert, HTML responsiv.

**Dateien:**
- `tools/pdf_exporter.py`
- `tools/reporting_common.py`
- alle Reportgeneratoren aus Gate 7
- `tests/test_pdf_exporter_real_pdf.py`
- Neu: `tests/test_report_html_pdf_parity.py`

**RED:**
- identische Überschriften/Abschnittsreihenfolge und Tabelleninhalte in HTML und extrahiertem PDF-Text;
- fachlich zentrale `.finding`-Karten, deren heutige `div`/`span`-Struktur der PDF-Extractor verlieren kann, sind als explizite Pflichtfelder abgedeckt;
- keine abgeschnittenen Tabellen, leeren Seiten oder verlorenen Deutungs-/LLM-Abschnitte;
- Header/Footer/Seitenzahlen konsistent;
- Scoreanzeige maximal drei Nachkommastellen;
- PDF enthält Wellbeing-/Compliancehinweis.

**Visuelle Abnahme:** repräsentative synthetische kurze/lange Reports in PDF rendern und Seitenbilder prüfen. Kein Anspruch auf „responsive PDF“; stattdessen saubere A4-Pagination.

### Gate 9 – Neue Archivhierarchie im Schreibpfad (Punkt k)

**Ziel:** Alle Artefakte einer Session liegen zusammen.

**Zielstruktur:**

```text
ArchiveRoot/
  ClientSlug/
    YYYYMMDD_HHMMSS_<SessionKind>/
      Resonanz/
      Deutung/
      Remedies/
      Synergy/
      Trends/
      session-manifest.json
```

**Dateien:**
- `tools/reporting_common.py::client_report_dir`
- `apps/cli/commands/scan.py`
- `apps/cli/commands/field.py`
- `tools/interpretation_generator.py`
- `tools/remedy_reporter.py`
- `tools/synergy_consolidator.py`
- `tools/trend_analyzer.py`
- `apps/web/reports.py`
- Neu: `tests/test_report_archive_hierarchy.py`

**Verträge:**
- eine server-/orchestratorvergebene Session-ID wird durch alle Generatoren gereicht;
- kein mtime-/„neuester Ordner“-Raten;
- Tenantroot bleibt erhalten;
- kanonische Clientverzeichnisse verwenden eine stabile pseudonyme Client-ID; identifizierende Namen/Geburtsdaten bleiben außerhalb des Pfades in getrennt geschützter Zuordnung;
- ein versionierter Path-Resolver lehnt Traversal, Symlinks/Junctions, reservierte Windows-Namen und Kontextüberschreitungen ab;
- atomare Writes und Artifact-Manifestregistrierung;
- Catalog liest neue Client-first-Struktur und historische Strukturen parallel;
- keine Pfade im Browserpayload.

### Gate 10 – Verlustfreie Archivmigration (Punkt k)

**Ziel:** Bestehende Berichte kopierend in die neue Hierarchie überführen.

**Dateien:**
- Neu: `tools/report_archive_migrate.py`
- Neu: `tests/test_report_archive_migration.py`
- Dokumentation unter `docs/migrations/`

**Phasen:**
1. `inventory` read-only: Klassifikation, Konflikte, unklare Sessionzuordnung.
2. `dry-run`: vollständige Quell→Ziel-Mappingdatei, keine Verzeichniserzeugung im Archiv.
3. Externe Pre-Migration-ShadowCopy nach gesonderter Freigabe.
4. `copy`: niemals move/delete; create-only Zielpfade.
5. SHA-256 und Dateigröße jeder Kopie gegen Quelle prüfen.
6. Catalog dual-read auf Kopie testen; Deduplizierung per Contenthash/Artifact-ID.
7. Cutover erst nach zwei unabhängigen Reviews.
8. Altstruktur bleibt mindestens eine definierte Retentionsperiode read-only erhalten; Löschung ist ein separates Gate.

**Verbot:** `tools/migrate_archive_hierarchy.py` darf für diese Zielmigration nicht verwendet werden. Es migriert in die entgegengesetzte Achsenfolge `Type/Client`, verschiebt/merged direkt und besitzt keinen ausreichenden Hash-, Kollisions- oder Rollbackvertrag.

Echte Berichte werden nicht in Tests oder Plandokumente kopiert.

### Gate 11 – Adaptive Berichte auf modernen Endgeräten (Punkt l)

**Ziel:** Alle HTML-Berichte sind bei 320/375/768/1280px lesbar und per Touch/Tastatur bedienbar.

**Dateien:**
- `tools/reporting_common.py`
- gemeinsame Report-CSS-/Rendererbausteine aus Gate 7
- `apps/web/static/report-preview.css`
- `tests/browser/workbench.spec.js`

**Abnahme:** kein Dokumentoverflow, Tabellen in eigener Scrollfläche, lange Tokens umbrechen, Touchziele mindestens 44px, Druck-CSS, reduzierte Bewegung, sichtbare Fokuszustände, semantische Überschriften und Tabellen.

### Gate 12 – Optionaler Geschlechts-/Profilkontext und Profiltrennung (Punkt h)

**Ziel:** Eine bewusste Auswahl kann klar geschlechtsspezifische Profile filtern, ohne bestehende Scores oder Defaultauswahl zu verändern.

**Empfohlener UI-Wert:** `Alle/keine Angabe` (Default), `weiblicher Profilkontext`, `männlicher Profilkontext`, `divers/kein Filter`. Keine Ableitung aus Name oder Geburtsdaten.

**Dateien:**
- `apps/web/contracts.py`
- `apps/web/static/index.html`
- `apps/web/static/app.js`
- `apps/web/workbench.py`
- `core/profile_sync/__init__.py`
- `core/admin_catalog/contracts.py` beziehungsweise bestehende Profileintrag-Metadaten
- Neu: `tests/test_profile_applicability_contract.py`
- `tests/test_web_scan_profile_catalog.py`

**Gate 12A – Metadata only:**
- kuratierte `applicability = all|female_anatomy|male_anatomy|explicit_only`-Metadaten; keine Keywordableitung aus Frau/Mann/Hormone;
- Default `all` liefert byte-/listenidentischen Pool;
- unbekannte/fehlende Metadaten bleiben `all`, nicht fail-open zu einem Geschlecht;
- Review zeigt Filterwirkung transparent.

**Gate 12B – Kandidaten im Shadow:**
- `schwangerschaft_geburt` und `wechseljahre_menopause` als getrennte inaktive Kandidaten;
- bestehendes `schwangerschaft_wechseljahre` wird nicht gelöscht;
- Alias-/Gruppen-/Remedy-/Multiplex-Closure validieren;
- männliche Kandidaten analog nur aus kuratierten Quellen, nicht per Keywordautomatik.

**Gate 12C – Produktive Aktivierung:** Erst nach fachlicher Freigabe, Baselinevergleich, dualem Review und explizitem Opt-in. Keine Verdrahtung von `calculate_resonance_modifiers()` in dieser Runde; dies wäre eine eigenständige Scoreänderung.

### Gate 13 – V1-Ursequenz der Harmonisierung (Punkt m)

**Ziel:** Webharmonisierung bildet die belegte V1-Sequenz transparent und stoppbar ab.

**Dateien:**
- `apps/web/contracts.py`
- `apps/web/main.py`
- `apps/web/harmonization.py`
- `core/harmonization/sequence_planner.py`
- `services/harmonization_worker.py`
- `services/harmonization_process_entry.py`
- `apps/web/static/index.html`
- `apps/web/static/app.js`
- Neu: `tests/test_harmonization_v1_sequence_contract.py`
- `tests/test_harmonization_sequence_planner.py`
- bestehende Harmonization-/Stop-/Recoverytests

**RED-Paritätsfixture:**
- Inputs hohe/mittlere/niedrige Priorität, Duplikatlabels und >20 Einträge;
- der Web-/Servicepfad verwendet den bereits vorhandenen reinen `core.harmonization.sequence_planner` statt dieselbe Auswahl-/Rundenlogik ein zweites Mal zu implementieren;
- Auswahl nur hoch/mittel, je Label höchster Score, Score absteigend, max. 20;
- `rounds=max(1,floor(max_seconds/(items*(pulse+pause))))`;
- V1-Preset 21s/42s, Faktor ×21 Min;
- kein Report/keine Items → kein Start;
- Stop während Impuls und Pause zählt keinen unvollständigen Zyklus;
- die derzeitige 5-Sekunden-API-Grenze wird nicht ersatzlos aufgeweicht: längere 21/42-Segmente müssen weiterhin intern in kurze kooperative Stop-Slices zerlegt werden und die bestehende gemessene Stop-Latenzgrenze einhalten;
- Recovery behält Owner/Lease/Report-/Sessionbindung.

**Gate 13A – Pure Planung:** Bestehenden `core.harmonization.sequence_planner` vervollständigen/prüfen; keinerlei Worker-, Hardware-, Score- oder UI-Wirkung.

**Gate 13B – Workerbindung:** Worker konsumiert ausschließlich den geprüften Plan und arbeitet `Runde → Item → Impuls → Pause` ab. Zielrate und globale Fallbackfrequenz bleiben getrennte Felder; Stop/Recovery bleiben stärker als historisch und werden nicht zurückgebaut.

**Gate 13C – Webbindung:** Serverseitig nur einen completed, owner-/tenantgebundenen Resonanz-/Multiplex-Scan derselben Session zulassen. Keine beliebige HTML/PDF/JSON-Datei als Sequenzquelle; das autoritative Scanartefakt über Manifest-/Artifact-ID auflösen, Plan redigiert voranzeigen und explizit bestätigen lassen.

**UX:**
- explizite Auswahl `Keine`, `Klassisch`, `Hardware`, `Beides`;
- Standard bleibt `Keine` bis bewusster Start;
- „Klassisch“ wird wahrheitsgemäß als Item-/Zeitsequenz ohne Hardwaremodulation erklärt; nur Hardware/Beides darf reale CPU/GPU/RAM-Modulation behaupten;
- Preset „V1 Ur-Sequenz 21/42“; Kurztestpreset klar als Testmodus markieren;
- Frequenz/Ratenquelle pro Item sichtbar;
- Laufzeitvorschau vor Start;
- CPU/GPU/RAM/Driver nur aktivierbar, wenn Hardwaretruth dies erlaubt.
- WebSocket-Hardware ist derzeit Simulation ohne aktiven Server und bleibt default-off beziehungsweise ausdrücklich „Simulation/experimentell“; kein separater ungebundener WebSocket-Port.

Keine Übernahme medizinischer Wirkversprechen aus historischen Texten.

### Gate 14 – Bestehende Adminverwaltung und Poolwirkung sicher abschließen (Punkt n)

**Ziel:** Vorhandene F6-Adminarchitektur nutzen, nicht duplizieren.

**Dateien:**
- `apps/web/admin_catalog.py`
- `apps/web/static/admin.html`
- `apps/web/static/admin-catalog.js`
- `core/admin_catalog/runtime_adapter.py`
- `core/profile_sync/__init__.py`
- bestehende `tests/test_admin_catalog_*`

**Reihenfolge:**
1. Live-Status gegen aktuelle F6-Dokumente und Code rekonstruieren; veraltetes `PROJECT_MEMORY` nicht als alleinige Wahrheit verwenden.
2. Admin-UI bleibt getrennt und adminauth-geschützt; kein normaler Workbench-Link, solange der bestehende F6-Vertrag dies untersagt.
3. Workbench zeigt nur sicheren Poolstatus: Legacy/Catalog Shadow/Catalog aktiv, Revision-Kurz-ID, Count.
4. Erweiterungen nur als Draft → Validate → Diff → Publish → Activate/Rollback.
5. Profil, Gruppen, Remedies und Multiplexreferenzen müssen als transitive Einheit validiert werden.
6. Neue Themen zuerst `import-preview`/Shadow; keine direkte Änderung produktiver Legacydateien.
7. Onlineadapter bleiben default-off mit Allowlist, HTTPS/DNS/IP/Redirect-Schutz und separater Sourcefreigabe.
8. Runtimeumschaltung ist ein eigenes Freezegate; kein stiller Legacyfallback nach expliziter Catalogaktivierung.

### Gate 15 – Grover/Qiskit Machbarkeit statt unbelegter Beschleunigungsbehauptung (Punkt o)

**Ziel:** Messen, ob Quantumkomponenten einen realen ergonomischen Nutzen liefern.

**Dateien:**
- `core/quantum_synergy/grover_search.py`
- `core/quantum_synergy/hybrid_engine.py`
- `apps/cli/workflow/step09_quantum.py`
- Neu: `benchmarks/benchmark_quantum_synergy.py`
- Neu: `tests/test_quantum_default_equivalence.py`

**Benchmarkmatrix:** Kandidaten 5/35/55/208, Qiskit nicht installiert, Simulator, klassischer Fallback; Warm-/Cold-Start, Laufzeit, Peak-RAM, Ergebnismengenüberlappung und deterministischer Seed.

**Entscheidungsregel:**
- Kein Einbau in Profil-Screening/Matrixscoring ohne belegten End-to-End-Vorteil und identische autoritative Vorauswahl.
- Der aktuelle klassische Oracleaufbau ist O(N); Simulator-Grover ist daher voraussichtlich nicht schneller.
- Qiskit bleibt additiv für Synergy/Experiment, standardmäßig klassisch und mit ehrlicher `quantum_used`-Anzeige.

### Gate 16 – Wahrheitsgebundene Echtzeitvisualisierung (Punkt p)

**Ziel:** Aktive Laufzeitfunktionen verständlich visualisieren, ohne inaktive Systeme als live darzustellen.

**Dateien:**
- `apps/web/scan_live.py`
- `apps/web/emf.py`
- `apps/web/hardware_truth.py`
- `apps/web/static/app.js`
- `apps/web/static/workbench-render.js`
- `apps/web/static/app.css`
- Neu: `tests/test_realtime_visualization_contract.py`
- `tests/browser/workbench.spec.js`

**Visualisierungen:**
- Scan: Stage, Substep, Fortschritt, aktive Profilnummer/gesamt, Ereigniszeit.
- Entropie/Hardware: Quelle und Status, keine erfundenen Werte.
- EMF: Proxyindexverlauf nur bei gültiger Lease; deaktiviert → keine Kurve.
- Quantum: `classical`, `simulator` oder bestätigter Backendmodus.
- Harmonisierung: aktuelles Item, Impuls/Pause, Runde, Restzeit, aktive Hardwarepfade.

**Grenzen:** kleine bounded Ringbuffer im Browser, keine sensitive Persistenz, keine lokalen Pfade/Commands, tabellarischer Screenreader-Fallback, `prefers-reduced-motion`. Das bestehende 2-Sekunden-Polling heißt „nahe Echtzeit“, nicht Echtzeit. Item-/Hardwarekurven bleiben gesperrt, bis ein eigener authentifizierter, owner-/tenantgebundener und redigierter Eventendpunkt mit Retentionvertrag existiert; JSONL-Dateien werden niemals direkt vom Browser gelesen. Quantum-Amplituden dürfen ohne reale Telemetrie nur als abstrakte Visualisierung bezeichnet werden.

## 6. Punkt-zu-Gate-Matrix

| Nutzerpunkt | Gates |
|---|---|
| a | 0, 3 |
| b | 1 |
| c | 2 |
| d | 5, 16 |
| e | 0, 3 |
| f | 4 |
| g | 7, 8 |
| h | 12 |
| i | 6 |
| j | 8 |
| k (UI) | 4, 6 |
| k (Archiv) | 9, 10 |
| l | 7, 8, 11 |
| m | 13 |
| n | 14 |
| o | 15 |
| p | 16 |

## 7. Regression Ladder je Gate

1. Neue RED-Nodes einzeln sammeln und erwarteten Fehler belegen.
2. Minimaler GREEN-Fix.
3. Nachbartests der betroffenen Module.
4. Workbench/Web-/Report-/Harmonization-Fokusmatrix.
5. `node --check` für jede geänderte JS-Datei.
6. Python-Syntax/Compile für geänderte Pythondateien.
7. `git diff --check`.
8. Vollsuite ausschließlich mit:

```bash
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 OPENBLAS_NUM_THREADS=1
"/c/morphic_v1/.venv/Scripts/python.exe" -m pytest tests -q --tb=short
```

9. Isolierte Playwrightabnahme mit lokalem Chrome auf freiem Port.
10. Eigener Server stoppen, Port freigeben, `node_modules`, `test-results`, `playwright-report` und `package-lock.json` entfernen.
11. Ports 8090 und 8765 beziehungsweise der freigegebene neue Benutzerserver verifizieren.
12. Keine Produkt-/Testpatches nach Start des finalen breiten Laufs; sonst komplette Evidenzleiter wiederholen.

Aktuelle Planbaseline vor Umsetzung:

- Python: `1399 passed, 9 skipped`
- fokussiert: `161 passed`
- Playwright: `23 passed`
- JavaScript-Syntax und `git diff --check`: PASS

## 8. Freeze- und Freigabeverfahren

Für jeden risikoreichen Makroblock (EMF, Reports/Archiv, Profilkontext, Harmonisierung, Adminruntime, Quantum):

1. RED→GREEN und vollständige Regression Ladder.
2. Technischer Hashfreeze mit exaktem Dirty-Scope und Autoritätshashes.
3. Zwei unabhängige driftfreie Read-only-Reviews gegen denselben Freezehash.
4. APPROVE nur bei P0=P1=P2=P3=0 in beiden Reviews.
5. Jeder nachträgliche Code-/Testpatch superseded Freeze und Reviews.
6. Danach Gate-/Statusdokumentation, separater Dokumentfreeze und erforderliche Dokumentreviews.
7. Erst danach externe Post-State-ShadowCopy mit SHA-256-Manifest und unabhängiger Source-vs-Copy-Rückverifikation.
8. Kein Commit/Push ohne ausdrückliche Freigabe.

## 9. Stop-Gates und bewusste Nichtziele

- **Stop nach Gate 0**, falls der kontrollierte Neustart den Katalog nicht mit 200 liefert; dann keine UI-Kosmetik über einen unbekannten Backendfehler legen.
- **Stop vor LLM-Aktivierung**, wenn Ollama nicht loopback-lokal oder das Modell nicht allowlisted ist.
- **Stop vor Archiv-Cutover**, wenn auch nur ein Quellartefakt keine eindeutige Session oder keinen hashgleichen Zielinhalt besitzt.
- **Stop vor Profilfilter-Aktivierung**, solange Metadata-Closure/Defaultäquivalenz nicht bewiesen ist.
- **Stop vor Harmonisierung**, wenn Auswahl-/Rundenparität, Stop oder Recovery nicht testbelegt ist.
- **Stop vor Catalogruntime**, solange F6/F7/F8-Gates oder Validation-Key-/Backup-/Rollback-Grenzen nicht vollständig freigegeben sind.
- **Kein Grover-Einsatz zur Scanbeschleunigung** allein aufgrund theoretischer O(√N)-Formulierung; entscheidend ist gemessene End-to-End-Laufzeit einschließlich klassischer Oracleerzeugung.
- **Keine medizinische Diagnose- oder Wirksamkeitsbehauptung** durch Profile, LLM, EMF oder Harmonisierung.

## 10. Empfohlene operative Priorität

1. Gate 0 – laufenden Server angleichen und Poolfehler schließen.
2. Gates 1–4 – Erklärungen, Adaptive Limits, Pooldetails, klare Review-/Reportoberfläche.
3. Gate 5 – EMF-Aktivierung und Quellenwahrheit.
4. Gates 6–8 – Katalog, Deutung/LLM und PDF-Parität.
5. Gates 9–11 – neue Archivhierarchie, sichere Migration und responsive Berichte.
6. Gate 13 – V1-Harmonisierung als eigener Sicherheitsblock.
7. Gate 12 – optionaler Profilkontext zunächst im Shadow.
8. Gate 14 – bestehende Adminverwaltung/Runtimewirkung formal fortsetzen.
9. Gates 15–16 – Quantumbenchmark und Echtzeitvisualisierung als additive Innovationen.

**Planstatus:** `NO-GO für Umsetzung`, bis der Nutzer die gateweise Ausführung freigibt. Die Pre-Plan-Absicherung ist verifiziert; produktive Prozesse und Daten wurden nicht verändert.
