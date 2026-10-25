# 10 - Empfehlungen und Produktionsgates

## 1. Zweck dieses Dokuments

Dies ist bewusst **noch kein Implementierungsplan**. Es priorisiert fachlich notwendige Entscheidungen und Zielzustände. Reihenfolge, Aufwand, Verantwortliche und konkrete Arbeitspakete können anschließend in einer gesonderten Planphase festgelegt werden.

## 2. Leitprinzipien

1. Sicherheit und Datenintegrität vor neuen Features.
2. Ehrliche Produktbeschreibung vor Claim-Optimierung.
3. Messbare Verträge vor weiterer Algorithmuskomplexität.
4. Ein führender Daten- und Sessionbegriff.
5. Ein reproduzierbarer Release statt Arbeitsbaumkopie.
6. Kleine, testbare, rückwärtsbewusste Schritte.
7. Reale Nutzerdaten nie als Entwicklungsfixture.

## 3. Sofortige operative Begrenzung

Diese Maßnahmen sind als Betriebsregel sinnvoll, noch bevor Code verändert wird:

1. Nur an `127.0.0.1` oder ein isoliertes Testnetz binden.
2. Öffentlichen/LAN-Port blockieren.
3. Maximal einen Uvicorn-Worker verwenden.
4. Keine realen Klientendaten auf einer erreichbaren Testinstanz.
5. Server-PDF-Pfade, DB-Scan, Löschung und Sensor-WebSockets nicht extern freigeben.
6. `python -m http.server` nicht aus dem Projektroot verwenden.
7. `setup_server.sh` nicht aus der aktuellen Arbeitskopie ausführen.
8. Keine externe Distribution oder Remote-Übertragung vor PII-/Lizenzprüfung.
9. Bestehende Runtime-/Reportdaten zugriffsgeschützt sichern.
10. Produkt nicht als medizinisch validiert, KI-trainiert, D-Wave-berechnet oder produktionsbereit bewerben.

## 4. Entscheidungsblock A - Produktzweck

Vor der technischen Detailplanung muss eine verbindliche Zweckbestimmung gewählt werden.

### Option A: Wellness-/Meditations-/Visualisierungssystem

Erforderlich:

- „Resonanzscore“ als algorithmische Musterähnlichkeit erklären,
- keine Diagnose-, Heilungs- oder Wirkungsclaims,
- EMF als Systemrauschprofil bezeichnen,
- Quantum/D-Wave nur als nicht implementiert/experimentell ausweisen,
- Disclaimer dauerhaft in UI und allen Exporten,
- Krankheitsdaten und Presets neu klassifizieren.

### Option B: Wissenschaftliches Mess-/Analysesystem

Erforderlich:

- messbare Zielgröße,
- Ground-Truth-Datensatz,
- kalibrierte Sensorik,
- feste/versionierte Modelle,
- statistische Validierung,
- Unsicherheitsintervalle,
- Reproduzierbarkeitsnachweis.

### Option C: Medizinische/therapeutische Software

Zusätzlich erforderlich:

- regulatorische Einstufung,
- QMS,
- Risikomanagement,
- klinische Bewertung,
- Software-Lifecycle-/Usability-/Post-Market-Prozesse,
- Datenschutz-Folgenabschätzung und formale Freigaben.

## 5. Priorität 1 - Exposition und Zugriffsschutz

Zielzustände:

1. Anwendung startet bei externem Binding ohne gültige Authkonfiguration nicht.
2. HTTP, WebSocket und Adminoperationen nutzen dasselbe konsistente Authmodell.
3. Rollen mindestens für Nutzer, Operator und Admin.
4. Client-/Sessionobjekte sind an Nutzer/Mandant gebunden.
5. Löschung erfordert echte Autorisierung, nicht nur einen bekannten Token.
6. Tokens erscheinen nicht in URLs/Logs.
7. TLS, Reverse Proxy, Firewall, Trusted Hosts und Origin-Allowlist sind dokumentiert.
8. Swagger/OpenAPI ist im Produktionsmodus geschützt oder deaktiviert.

Produktionsgate:

- unauthentifizierter Zugriff auf alle geschützten HTTP-/WS-Pfade wird in Securitytests abgelehnt.

## 6. Priorität 2 - Pfade und Workload

### 6.1 Pfade

- DBs nur über serverseitige opaque IDs unter einem festen Root.
- Bilder nur über kontrollierten Upload/Import.
- Exporte nur unter festem Exportroot mit servergeneriertem Dateinamen.
- `resolve()` plus Rootcontainment, Symlinkprüfung und Suffix-/MIME-Regeln.
- Löschung nur innerhalb erlaubter Artefaktwurzeln.
- keine absoluten Serverpfade in Responses.

### 6.2 Ressourcen

- `matrix_size` strikt 12/24/36 und hardwareseitig verfügbar.
- Maxima für Fokus, Sequenz, Gruppe, Bild, DB, Matrix und PDF.
- Rate Limits und Requestbodylimit.
- Analyse als Job mit Job-ID, Status, Timeout und Cancel.
- genau kontrollierte Engine-/GPU-Concurrency.
- sichere OOM-Behandlung und Commit-/VRAM-/Peakbudget.
- DB-Scan drastisch begrenzen oder offline/job-basiert ausführen.

Produktionsgate:

- Path-Traversal-, Symlink-, Oversize-, Rate- und OOM-Tests bestehen ohne Prozessabbruch oder Datenkorruption.

## 7. Priorität 3 - Persistenz und Datenschutz

Zielzustände:

1. Client, Session, Resultat, Artefakt und Audit in transaktionaler SQLite-/PostgreSQL-Persistenz.
2. Foreign Keys, Unique Constraints und versionierte Migrationen.
3. Ein Run entspricht einer Session; Fokusresultate sind Kindobjekte.
4. Artefakte haben Hash, Größe, MIME, Retentionklasse und relativen Pfad.
5. Löschung als persistentes, wiederanlaufsicheres Journal mit `pending/done/failed`.
6. vollständiges Dateninventar einschließlich Browser, Logs, Bus und Backups.
7. Retentionmatrix pro Datenklasse.
8. PII at rest und Backups verschlüsselt.
9. zufällige IDs oder HMAC-basierte Pseudonyme.
10. Test- und Produktivdaten strikt getrennt.

Produktionsgate:

- Parallelitäts-, Crash-, Disk-full-, Migration-, Backup-, Restore- und Lösch-Retry-Tests bestehen.

## 8. Priorität 4 - Enginevertrag und Fachkorrektheit

### 8.1 Reproduzierbarkeit

- lokale RNG-Generatoren statt globaler Zustandsänderung,
- feste/versionierte Projektionsbasis für vergleichbare Scores,
- vollständige kanonische Eingabe in Seed/Manifest,
- Kandidatenzahl und Algorithmusversion speichern,
- Hardware-/Dependencyeinfluss explizit machen,
- Score nach jeder Matrixtransformation neu berechnen,
- `Deaktiviert` entfernt Fokus aus Ziel und Seed,
- Bildname nicht aus zufälliger Tempdatei ableiten,
- Gruppenreihenfolge kanonisieren.

### 8.2 Vertragsehrlichkeit

- wirkungslose API-Felder implementieren oder entfernen,
- D-Wave-/5-Elemente-/Remote-Sensor-No-ops klar markieren oder entfernen,
- Geburtszeit, Organuhr, Geo und Amplifier-Key korrigieren,
- Engine- und API-Ausgaben angleichen,
- Scores nicht als kalibrierte Prozentwerte darstellen, solange keine Kalibration existiert.

### 8.3 Evidenz

- Referenzdaten mit Quelle, Lizenz, Version, Evidenzgrad und Reviewstatus,
- keine Akkuranz-/Wirksamkeitszahlen ohne reproduzierbare Studie,
- EMF nur mit kalibrierter Sensorik als Feldmessung bezeichnen.

Produktionsgate:

- deterministische Golden Tests, Scoredefinition, Nullverteilung, Fachreview und Claim-Traceability sind dokumentiert und bestanden.

## 9. Priorität 5 - UI, CLI und Integrationen

### Browser

- sichere DOM-Konstruktion statt unescaped `innerHTML`,
- CSP ohne Inline-Handler,
- Auth-/Sessionintegration,
- Session-ID und Artefaktbeziehung im State,
- LocalStorage Opt-in, TTL und „alle lokalen Daten löschen“,
- externe Fonts lokal ausliefern,
- CSV-Formula-Neutralisierung,
- Accessibility und Playwright-E2E.

### PowerShell

- `Invoke-Expression` vollständig entfernen,
- Argumentarray und direkter Call-Operator,
- PowerShell 5.1/7 Parser- und Live-Tests,
- Klartext-Tempdaten minimieren und bereinigen.

### CLI

- Pfade relativ zu Projekt-/Configroot statt CWD,
- Export-, Audio- und Archivkomponenten trennen,
- Audio streamend schreiben,
- konsistente Feldnamen und Exitcodes,
- Plattformfähigkeiten klar kennzeichnen.

### Bus

- HMAC/Signatur oder vertrauenswürdige DB-Schreibgrenze,
- ACL-Durchsetzung,
- Topic-/Content-Hash-Konsistenz,
- Quarantäne und Poison-Message-Strategie,
- Migrationen, Retention und Backup.

## 10. Priorität 6 - Engineering und Release

Zielzustände:

1. `pyproject.toml` mit klaren Runtime-/CLI-/Image-/Testextras.
2. Python zunächst verbindlich 3.11/3.12 nach Testmatrix.
3. Plattform-/CUDA-spezifische Locks mit Hashes.
4. saubere Modulgrenzen für Router, Engine, Export, Audio und UI.
5. CI auf Windows und Linux; separater GPU-Runner.
6. Lint, Format, Typing, JS-/PowerShell-/Shellchecks.
7. Coverage-Baseline und Securitygates.
8. Build eines unveränderlichen, signierten Artefakts.
9. SBOM, Lizenz- und Vulnerabilityreport.
10. Release-Tag, Changelog, bekannte Einschränkungen.
11. atomarer Deploy-/Rollbackmechanismus.

Produktionsgate:

- Clean-Install und vollständige Abnahme laufen aus dem Releaseartefakt, nicht aus dem Entwicklerarbeitsbaum.

## 11. Priorität 7 - Betrieb und Recovery

- typisiertes Settingsmodell mit Startupvalidierung,
- technische Liveness/Readiness,
- strukturierte PII-redigierte Logs,
- Request-/Job-/Session-Correlation,
- Metriken und Alerts für Fehler, Latenz, Queue, GPU, RAM, Commit, Disk und Backup,
- definierte SLO,
- RPO/RTO,
- verschlüsselte 3-2-1-Backups,
- automatisierte Restoretests,
- Incident-, Datenschutz-, GPU-Ausfall- und Datenkorruptionsrunbooks,
- benannte Owner und Eskalationswege.

## 12. Vollständige Produktionscheckliste

### Produkt und Recht

- [ ] verbindliche Zweckbestimmung
- [ ] Claims mit Code/Evidenz abgeglichen
- [ ] Datenschutz-/Medizinprodukt-/Werberechtsprüfung
- [ ] Lizenz und Referenzdatenherkunft geklärt

### Security

- [ ] fail-closed Auth für HTTP/WS/Admin
- [ ] Rollen/Mandanten/Ownership
- [ ] TLS/Proxy/Firewall/Origins
- [ ] Pfadsandbox
- [ ] Eingabe-/Rate-/Zeit-/Rechenlimits
- [ ] CSP/XSS-/Formula-Injection-Schutz
- [ ] Secretmanagement und Rotation

### Daten

- [ ] transaktionale Persistenz
- [ ] Migrationen und Constraints
- [ ] Retention und Verschlüsselung
- [ ] vollständige, wiederanlaufsichere Löschung
- [ ] Artefakthashes und portable Pfade
- [ ] Test-/Produktivtrennung

### Engine

- [ ] definierter Scorevertrag
- [ ] reproduzierbare Seeds/Projektion/Manifest
- [ ] keine wirkungslosen oder irreführenden Flags
- [ ] OOM-/Parallelitätsrobustheit
- [ ] Fach-/Evidenzreview

### Qualität

- [ ] grüne Vollsuite ohne nativen Abbruch
- [ ] Browser-E2E und Accessibility
- [ ] Security-/Last-/Concurrencytests
- [ ] Coverage, Lint, Format, Typing
- [ ] Windows/Linux/CUDA-Matrix

### Release/Betrieb

- [ ] saubere Git-Baseline und Release-Tag
- [ ] reproduzierbares signiertes Artefakt
- [ ] Lockfiles, SBOM, Lizenz-/Vulnerabilityscan
- [ ] Health, Logs, Metriken, Alerts
- [ ] Backup-/Restorebeweis und RPO/RTO
- [ ] Upgrade-/Rollbacktest
- [ ] Runbooks, Owner und Incidentprozess

## 13. Empfohlener Fokus der späteren Planerstellung

Die Planphase sollte nicht mit Modulrefactoring beginnen. Sinnvolle Reihenfolge:

1. Einsatzgrenze und Zweckbestimmung entscheiden.
2. P0-Exposition und Datenverlustpfade schließen.
3. Persistenz-/Session-/Löschzielmodell festlegen.
4. Enginevertrag und Claimgrenzen definieren.
5. Release-/Test-/Betriebsfundament aufbauen.
6. Erst danach UI-Konsolidierung, Modulzerlegung und weitere Features planen.
