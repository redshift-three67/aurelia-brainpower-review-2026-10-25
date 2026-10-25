# Morphic V1 – Stabilisierung, Security und Operator Workbench: Umsetzungsplan

> **Für Hermes:** Jede Phase strikt nacheinander ausführen. Vor jeder Codephase: zeitgestempelte ShadowCopy, RED-Test, minimale additive Änderung, gezielte Regression, Vollsuite, HTTP-/Browser-Nachweis, Dokumentationsupdate. Kein Commit/Push ohne ausdrückliche Nutzeranweisung.

**Ziel:** Den lokal funktionsfähigen Morphic-V1-Operator-Prototyp schrittweise zu einer nachvollziehbaren, privacy-by-design vorbereiteten und robust bedienbaren Plattform weiterentwickeln, ohne Scoring-, Profil-, Multiplex- oder Kernengine-Verhalten unautorisiert zu verändern.

**Architektur:** Zuerst werden fehlerhafte Workbench-Verträge, XSS- und HTTP-Fehlergrenzen geschlossen. Danach folgen eine explizite lokale/Netzwerk-Identity-Entscheidung, tenantgebundene Daten- und Exportgrenzen sowie Privacy-Lifecycle. Alle späteren Erweiterungen bleiben additiv: neue Adapter/Manifeste/Policies neben dem bestehenden Laufweg, Defaultwerte konservieren das heutige Verhalten.

**Technik:** Python 3.12-Projektvenv, FastAPI/Pydantic, Typer, Vanilla JS, pytest, ReportLab, JSON/SQLite; für Browsergates Playwright + axe-core/Lighthouse CI erst nach isolierter Toolchain-Prüfung.

**Verbindliche Invarianten:**

1. Keine Änderung an Resonanzformeln, NLS-Gewichten, Profil-/Gruppenregeln oder vorhandenen Exportschemas ohne eigenes Algorithmus-/Äquivalenz-Gate.
2. Jede neue Sicherheitsprüfung ist im lokalen Entwicklungsmodus explizit konfigurierbar, aber für Netzwerkbetrieb fail-closed.
3. `tenant_id`, `operator_id` und spätere Rollen werden ausschließlich serverseitig abgeleitet; nicht aus Browserpayloads.
4. Sensible Klartextdaten werden nicht in Tests, Planberichte, Commitmeldungen oder Chat-Ausgaben kopiert.
5. Jede Löschautomatisierung beginnt als Dry-run und benötigt einen vollständigen Artefaktindex.

---

## Phase 0 – Evidenz, ShowCopy und unveränderliche Baseline

**Befunde:** Auditgesamtstand.

**Dateien:**
- Create: `docs/deep-audit-2026-07-10/SESSION_HANDOFF_2026-07-10.md`
- Create: `docs/plans/2026-07-10-morphic-v1-stabilisierung-security-ui-umsetzungsplan.md`
- External create: `E:\mprphic_v1_Backups\morphic_v1_showcopy_YYYYMMDD_HHMMSS\`

**Schritte:**
1. Branch, HEAD, Arbeitsbaum, Ports, freie Zielkapazität und Projektvenv protokollieren.
2. Den aktuellen Audit-, Plan-, Projekt- und Quellstand ohne `.git`, `.venv`, Cache-Verzeichnisse oder ungetrackte Klientenexporte kopieren.
3. Git-HEAD-Dateiliste und zusätzlich ungetrackte Audit-/Plan-Dokumente in ein Quellmanifest aufnehmen.
4. SHA-256-Manifest, Datei-/Bytezahl, Copy-Protokoll und Sitzungsübergabe mit ISO-Zeitstempeln erzeugen.
5. Kopie gegen Manifest prüfen; erst danach eine Codephase beginnen.

**Akzeptanz:** Backup-Verzeichnis existiert; `SOURCE_MANIFEST.sha256` enthält alle Kopierdateien; Hashprüfung ist fehlerfrei; keine PII-Exportordner wurden in die ShowCopy aufgenommen.

---

## Phase 1 – P0 Workbench-Vertrag und Client-Sicherheitsgrenze

**Befunde:** U-10, U-11, S-14, U-01/U-02/U-04/U-05.

**Ziel:** Die Review-Ansicht bleibt bei echter Hardware-Truth stabil, HTTP-Fehler können nicht als Scanstart erscheinen, dynamische Clientdaten werden nicht als HTML interpretiert und der Operator erhält verwertbare Fehlermeldungen.

### Task 1.1: Hardware-Review-Vertrag absichern

**Files:**
- Modify: `apps/web/static/workbench-render.js:123-146`
- Modify/create test: vorhandener Web-/Frontend-Regressionstest, nach Toolchain-Entscheidung `tests/test_web_shell.py` plus Browser-/DOM-Test.

1. RED: Hardware-Snapshot mit `components` als Dict in `renderReviewCards` ausführen; Fehler `comps.map is not a function` reproduzieren.
2. GREEN: dieselbe sichere `Object.values(payload.components || {})`-Normalisierung wie in der Hardwarephase verwenden.
3. Regression: Hardware-Truth-Backendtest, JS-Syntax und Browser-/DOM-Test grün.

### Task 1.2: HTTP-Fehlervertrag zentralisieren

**Files:**
- Modify: `apps/web/static/workbench-api.js:11-97`
- Modify: `apps/web/static/app.js:169-204,250-255,323-350,355-402`
- Test: Browser-/DOM-Test für 401, 422 und 500.

1. RED: Mock-Response 401/422 aus Preview und Jobstart liefert derzeit JSON statt Exception.
2. GREEN: zentraler Request-Helper prüft `response.ok`, extrahiert sichere `detail`-Meldung und wirft einen typisierten Fehler.
3. GREEN: Navigation/Polling nur bei `job_id` und Statusresponse; sichtbarer aria-live Fehler mit Retry-/Korrekturhinweis.
4. Regression: kein erfolgreicher Startstatus/kein Timer/kein Phasenwechsel für Fehlerantworten.

### Task 1.3: Untrusted DOM-Ausgabe eliminieren

**Files:**
- Modify: `apps/web/static/workbench-render.js`
- Modify: `apps/web/static/app.js:269-350`
- Test: XSS-Payloads für Client, Fokus, Reportname, Hardware-Metadaten.

1. RED: Regressionstest setzt `<img onerror>`/`<svg onload>` in dynamische Felder und beweist, dass keine HTML-Knoten entstehen.
2. GREEN: DOM-Nodes und `textContent` statt Interpolation in `innerHTML`; nur statische, geprüfte Templates bleiben erlaubt.
3. Regression: serverseitige Report-Sanitizer-Tests unverändert grün, Preview-Funktion bleibt erhalten.

### Task 1.4: Form-/Navigationsgates

**Files:**
- Modify: `apps/web/static/app.js:441-449,501-510,533-541`
- Modify: `apps/web/static/index.html:43,260-263`
- Test: Browser-/DOM-Test.

1. Vor Preview/Start native Validierung plus explizite Consent-Prüfung auslösen.
2. Fallback-Step-Registry als einzelne Konstante führen; 11 statt 10 als Grenze verwenden.
3. Statische Fortschrittsanzeige auf `1 / 11` korrigieren; Erfolg/Farbe konsistent über Klassen oder `data-state` ausgeben.

**Phasenprüfung:** gezielte Tests + `node --check` aller vier Workbench-JS-Dateien + `pytest tests -q` + loopback HTTP-/Browser-Smoke. Keine Kernengine-Änderung.

---

## Phase 2 – Identity-, AuthN-, AuthZ- und Tenant-Entscheidungsgate

**Befunde:** S-01 bis S-06, S-10, S-13.

**Entscheidung vor Implementierung erforderlich:**

| Variante | Geeignet für | Folge |
|---|---|---|
| A: Lokaler Einoperator (vorläufig) | ausschließlich 127.0.0.1, eine Windows-Benutzeridentität | Startup fail-closed bei nicht-loopback Host; API-Key/ACLs, keine Multiuser-Zusage |
| B: echter Mehrbenutzer-/Multitenantbetrieb | LAN, Server oder SaaS | OIDC/SSO oder gleichwertiger IdP, persistente Principals/Rollen/Tenants, TLS, DB/Repository-Grenzen |

**Bis zur Entscheidung:** keine Pseudo-RBAC auf Basis frei wählbarer `MORPHIC_*`-Environmentwerte als Sicherheitsversprechen implementieren.

**Zielstruktur für Variante B:** `Principal(operator_id, tenant_id, roles)` aus signierter Session/Token; zentraler `require_principal`; `require_resource_access`; jede Job-, Report-, Draft-, Template-, Trace- und WebSocket-Route erhält AuthN + tenant/owner AuthZ vor Datenzugriff/WS-accept.

**Schritte nach Entscheidung:**
1. Threat model, Deploymentprofile und negative Zugriffsmatrix schreiben.
2. RED-Tests für no-auth, falscher tenant, falscher owner, ownerloser Legacyjob, WS vor accept, Reportdownload, Draft/Template/Trace.
3. Zentralen Dependency-/Middleware-Adapter implementieren; lokale Tests mit Fake Principal.
4. Legacyjobs migrieren/quarantänisieren statt sie still zu erlauben.
5. CORS pro Profil strikt setzen; nicht-loopback ohne TLS/Auth/Originpolicy verweigern.
6. API-Key für Maschinenintegration hashen/rotieren oder nach IdP-Einführung entfernen.

**Phasenprüfung:** vollständige positive/negative HTTP- und WebSocket-Tests, CORS-/Header-Test, Tenant-Cross-Access-Test und Vollsuite.

---

## Phase 3 – Privacy Data Lifecycle und sichere Exportgrenze

**Befunde:** S-07 bis S-09, S-12, S-13, D-01.

**Ziel:** Vollständige Datenkarte und kontrollierbare, tenantgebundene Speicherung ohne Klarnamen in technischen Pfaden; Löschung wird nachweisbar, aber nie unkontrolliert automatisiert.

**Schritte:**
1. Datenklassifikation und Artefaktkarte: Runtime JSON, Workbench JSON, Joblogs, Harmonization JSONL, Exporte, LocalStorage, Backups.
2. Tenant-/Client-Scoped Artifact-Repository als additiven Adapter definieren; verschleierter Client-Slug statt Name/Geburtsdaten in neuen Pfaden.
3. Web-Launcher so umbauen, dass er keinen globalen `C:\Benutzer_Archive_Start`-Root mehr erzwingt; Root nur aus serverseitigem Kontext.
4. Erasure-Index mit allen bekannten Artefaktorten erstellen; nur Dry-run + Completion-Report.
5. Hardcoded Löschdefault entfernen; Installationssecret + adminseitige Re-Auth/Freigabe definieren.
6. Lokale Fokushistorie explizit opt-in, löschbar und datenschutztextlich erläutert machen.
7. Windows ACL/DPAPI-Entscheidung für Ruheverschlüsselung prototypisch mit temporären Testdaten nachweisen.

**Phasenprüfung:** Zwei-Tenant-E2E-Exporttest, Erasure-Dry-run/Completeness-Test, kein Klarname in neuen Pfaden, Restore-/Backup-Policy-Test, Vollsuite.

---

## Phase 4 – Nachvollziehbarkeit und Jobsicherheit

**Befunde:** A-01, O-01 bis O-03.

**Ziel:** Der vorhandene Scan bleibt mathematisch unverändert, erhält aber ein versioniertes, maschinenlesbares Laufmanifest und restartfähige Jobmetadaten.

**Schritte:**
1. JSON-Schema für additiven Run-Manifest-Block erstellen: commit, profile/data hashes, seed mode, parameter version, artifact hashes, tenant/client pseudonym.
2. RED-/GREEN-Tests: Defaultlauf erhält keinen Scoreunterschied; Manifest ist vollständig und keine PII gelangt hinein.
3. Persistentes Web-Jobmanifest mit command redaction, owner/tenant, timestamps, exitstatus und Logpfaden ergänzen; App-Start-Recovery read-only testen.
4. Strukturierte JSONL-Progress Events parallel zu stdout ausgeben; UI liest Event bevorzugt, stdout bleibt Fallback.
5. Mehrprozessgrenzen dokumentieren; erst nach Store-Entscheidung DB-/Lock-Migration beginnen.

**Phasenprüfung:** Äquivalenztests unverändert, Restart-Smoke, Event-/Fallback-Test, Vollsuite und Reporthashvergleich.

---

## Phase 5 – Modifier- und Radi144-Klientendaten-Gate

**Befund:** A-02 / Feedbackpunkt e.

**Ziel:** Erst beweisen, welche bestehenden Klientenmodifier den aktiven Pipeline-Score beeinflussen; erst dann minimal notwendige Radi144-Datenerfassung additiv gestalten.

**Schritte:**
1. Vollständigen Callgraph für `calculate_resonance_modifiers()` und `ClientProfile` erstellen; nicht genutzte Werte als „berechnet, nicht verbunden“ markieren.
2. Entscheiden, ob einzelne Modifier technisch und fachlich aktiviert werden sollen; keine medizinischen Werte ohne Datenschutzfolgeabschätzung.
3. Für jeden aktivierten Parameter: Default exakt heutiges Verhalten, finite-safe math, RED-Äquivalenztest, Wirkungstest und Reporttrace.
4. Erst danach UI-Formular mit Feldklassifikation, Zweck, Consent und Erasure-Verknüpfung.

**Phasenprüfung:** unveränderte Core-Äquivalenz, Parameterwirkung nur bei explizitem Opt-in, Privacy-/Erasure-Test.

---

## Phase 6 – Harmonization Worker Truthfulness

**Befund:** O-04.

**Ziel:** Pulse/Pause/Solfeggio sind entweder im Worker messbar wirksam oder werden aus UI/API entfernt bzw. eindeutig als gespeicherte Voreinstellung gekennzeichnet.

**Schritte:**
1. Dauer-, Zyklus- und Frequenzsemantik schriftlich festlegen; keine medizinische Wirkbehauptung.
2. Mock-Clock-RED-Test: Pulse und Pause erzeugen unterschiedliche, deterministische Workerphasen; Solfeggio beeinflusst nur klar definierte Daten/Parameter.
3. State-Machine additiv implementieren; bestehende Defaultdauer rückwärtskompatibel.
4. CLI und Webparameter paritätisch machen oder bewusst dokumentiert trennen.

**Phasenprüfung:** Zeitsemantiktest, Stop-/Restart-Test, Default-Äquivalenz, Vollsuite.

---

## Phase 7 – Operator UX, Accessibility, Performance und Google-/web.dev-Evidenz

**Befunde:** U-01 bis U-14, Google-/CWV-Lücken.

**Schritte:**
1. Scanabbruch, Doppelstart-Sperre, klare Fehlerzustände, Ergebnisnavigation, Hardware-Review und Fallbacknavigation schließen.
2. Native Radio-Controls einsetzen oder vollständige WAI-ARIA-Radiogroup mit Pfeiltasten/Fokusmanagement implementieren.
3. Stepwechsel mit fokussierter Überschrift und klarer Live-Statusansage; globale Pfeiltasten nur im Stepper-Kontext.
4. `/ui/` und `/workflow-stepping` als Legacy/Dokumentation isolieren, deprecaten oder auf den gleichen Sicherheitsstandard heben; externe Fonts nach Privacyentscheidung entfernen.
5. Playwright, axe-core und Lighthouse CI als isolierte Dev-Toolchain etablieren; reale 320px, Zoom, Kontrast, Tastatur, NVDA/Firefox-Checkliste sowie LCP/INP/CLS-Messprotokoll.
6. Katalog pagination/indexieren und Bootstrap-Requests parallelisieren; erst mit realistischen anonymisierten Archiven messen.
7. Für eine spätere öffentliche Marketing-/Dokuseite separate noindex/index-Entscheidung, Search Essentials, robots/sitemap/canonical und Datenschutz-/Impressumsseiten planen. Die Operator-App selbst bleibt standardmäßig nicht indexierbar.

**Phasenprüfung:** Browser-E2E, axe, Lighthouse-Protokoll, manuelle Accessibility-Checkliste, HTTP-Security-Header und Vollsuite.

---

## Phase 8 – Betriebsreife und Dokumentationswahrheit

**Befunde:** D-01, D-02, S-10.

**Schritte:**
1. `README.md`, `config.yaml`, Launcher und Healthchecks auf eine einzige aktuelle, tenantfähige Konfigurationsquelle konsolidieren.
2. CI-Pipeline: Venv-Setup, pytest, JS syntax, Browsergates, dependency/SAST/secret scan, SBOM.
3. Signierte/prüfbare Release- und Backup-/Restore-Probe definieren; kein Git-Remote voraussetzen, solange keines konfiguriert ist.
4. Betriebsrunbook: loopback vs. network deployment, Port-/TLS-/CORS-/Secret-/ACL-Voraussetzungen, Incident- und Restoreablauf.

**Phasenprüfung:** frischer Clone-/Venv-Smoke, CI grün, dokumentierte Restore-Probe, `git diff --check`, Vollsuite.

---

## Abschlusskriterium

„Produktionsreif“ darf erst behauptet werden, wenn Phase 2 und 3 die tatsächliche Betriebsart abdecken, alle P0/P1-Gates mit realen Tests belegt sind, Browser-/Security-/Privacy-Nachweise vorliegen und ein getesteter Restorepunkt existiert. Bis dahin lautet der ehrliche Status: **lokal funktionsfähiger Operator-Prototyp, nicht für externen Mehrbenutzerbetrieb freigegeben.**
