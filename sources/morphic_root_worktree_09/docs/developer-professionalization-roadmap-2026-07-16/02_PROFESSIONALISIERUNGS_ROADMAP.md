# Gatefähige Professionalisierungs-Roadmap

## Leitprinzipien

- Kein Big Bang; jeder Block ist unabhängig rücksetzbar und reviewbar.
- Sicherheits-/Persistence-Gates zuerst, Komfort/Innovation danach.
- Bestehendes Verhalten durch Characterization-/Equivalence-Tests einfrieren.
- Produktive Daten und Authorities bleiben vor expliziter Freigabe unverändert.
- Code-, Dokument- und Post-State-Freeze bleiben getrennte Zustände.
- Aufwand: S = 1–2 Entwicklertage, M = 3–7, L = 1–3 Wochen; nur Planungsgröße, keine Terminzusage.

## Phasenübersicht

| Phase | Ziel | Aufwand | Abhängigkeit | Exit-Kriterium |
|---|---|---:|---|---|
| P0 | F5-B/v10 sicher schließen | L | aktuell aktiv | zwei technische + zwei Dokument-APPROVE, danach verifizierte ShadowCopy |
| P1 | Deterministische Test-/Worktree-Hygiene | M | P0 | Vollsuite erzeugt keine Repository-Artefakte; Baselinefehler 0 |
| P2 | Reproduzierbare Toolchain und CI | M | P1 | Lockfile + Windows-CI + saubere Neuinstallation |
| P3 | Authority-/Persistence-Kern vereinheitlichen | L | P0–P2 | Registry/Stage/Backup nutzen einen geprüften Contract |
| P4 | Architektur-/Entrypoint-Konsolidierung | L | P2 | aktive Entry Points und Modulownership eindeutig |
| P5 | Admin Composition/Auth/API/UI | L | P0/P3/P4 | fail-closed Adminbetrieb, Browser-/API-Akzeptanz |
| P6 | Runtime-Aktivierung und Fallbackpolicy | L | P5 | atomare Catalog-Wirkung, kein gemischter Legacyfallback |
| P7 | Release, Observability, Betrieb | M | P2–P6 | reproduzierbares Release + Runbooks + Recovery Drill |
| P8 | kontrollierte Innovation/Performance | fortlaufend | stabile Releases | messbarer Nutzen ohne Default-Drift |

## P0 – F5-B/v10

**Scope:** ausschließlich aktuelle v10-Root-Causes.

Tasks:

1. Parent-Substitution für Stage, Index, Ledger, Rollback-Snapshot und Key als echte REDs reproduzieren und die zuvor gebundene Parent-Identität verpflichtend bis zur Commitprimitive transportieren.
2. v7-Known-Answer-DB/Backup-Fixtures und echte REDs.
3. atomare v7→v8-Migration mit Neuvalidierungspflicht.
4. Restore-v7→temporär migriertes v8→neues Ziel.
5. handlegebundene Backup-/Restore-Publikation plus Completion-Record.
6. POSIX sichere Primitive oder explizit fail-closed.
7. produktive Validation-Key-Provider-Komposition ohne Stage-Key-Kopplung.
8. vollständige Regression/operative Nachweise.
9. Freeze v10 und zwei unabhängige Reviews.
10. Dokumentfreeze, zwei Reviews, externe Post-State-ShadowCopy.

**Nicht in P0:** CI-Neubau, Verzeichnisbereinigung, Modulverschiebung, Admin-UI oder Algorithmusänderung.

## P1 – Test- und Worktree-Hygiene

### P1.1 Inventar ohne Mutation

- maschinenlesbare Top-Level-Klassifikation;
- Runtime-/Archive-/PII-Risiken nur als Metadaten erfassen;
- Owners und Retention je Root festlegen;
- keine Löschung.

### P1.2 Externe Runtime-Roots

Dateien voraussichtlich:

- `core/runtime_paths.py` oder bestehende Pfadpolicy erweitern;
- Launcher/Worker/Exporter-Aufrufer;
- Tests für Worktree-Ausschluss und Reparse-/Traversal-Schutz.

RED-Verträge:

- Default darf nicht im Git-Toplevel liegen;
- expliziter Projektpfad fail-closed;
- Tests verwenden `tmp_path`;
- keine Parent-Erzeugung bei invalider Konfiguration.

### P1.3 Testdeterminismus

- Clock-Fixture statt reales Datum;
- Rate-Limiter pro Test/App-Instanz isolieren;
- Ports dynamisch reservieren;
- externe `--basetemp`-Policy;
- Vollsuite zweimal hintereinander mit identischem Ergebnis;
- Vor-/Nach-Status und Authority-Hashes.

### P1.4 kontrollierte Bereinigung

Erst nach Freigabe:

- exakt bekannte synthetische Artefakte löschen oder extern archivieren;
- PII-/Operatorarchive nach eigener Datenschutz-/Retentionentscheidung behandeln;
- `.gitignore` aktualisieren;
- keine Wildcard-Löschung ungeprüfter Roots.

Exit: clean interpretierbarer Source-Status und `0 failed` in der Vollsuite.

## P2 – Toolchain und CI

### P2.1 Dependency Authority

- `pyproject.toml` vollständig machen;
- Extras: `hardware`, `scientific`, `quantum`, `gpu`, `dev`;
- `requirements.txt` als generiertes Kompatibilitätsartefakt oder entfernen;
- `uv.lock` erzeugen und Neuinstallation in leerer Umgebung prüfen.

### P2.2 Developer Commands

Einheitliche Befehle, z. B.:

```text
uv sync --extra dev
uv run pytest tests -q
uv run ruff check .
uv run python -m apps.cli --help
```

Windows-Launcher dürfen intern auf dieselbe Authority verweisen; kein bare `pip`/fremdes Python.

### P2.3 CI

- Windows stable Python 3.11 zuerst;
- lint/compile/unit/security/integration/slow getrennt;
- Logs und JUnit als Artefakte;
- keine Secrets, produktiven DBs oder Netzwerkadapter;
- Linux advisory bis P3 POSIX geschlossen;
- danach required.

Exit: clean checkout → lockbasierte Installation → vollständige definierte Gates reproduzierbar.

## P3 – Authority-/Persistence-Kern

### P3.1 Characterization

- bestehende Registry-/Stage-/Backup-Semantik als Contracttests;
- Windows-/POSIX-Capability-Matrix;
- Faultpoints standardisieren;
- keine Produktionsmigration.

### P3.2 Kleine interne API

Vorgeschlagene Operationen:

```text
read_bound(path, policy) -> BoundBytes
replace_durable(target, bytes, expected_parent)
publish_immutable(target, bytes)
publish_bundle(root, artifacts, completion_record)
```

Contracts:

- no-follow/reparse;
- Parent- und Temp-Inode-Bindung;
- File- und Directory-Flush;
- no-overwrite;
- Post-State-Identity/Bytes;
- fail-closed ohne sichere Plattformprimitive.

### P3.3 Gateweise Migration

1. Source Registry;
2. Stage/Index/Ledger/Key;
3. Catalog Backup/Restore;
4. sonstige kritische File-Authorities.

Nach jedem Schritt: Equivalence, adversariale Matrix, Vollsuite, unabhängiges Review. Keine gleichzeitige API-/Featureänderung.

## P4 – Struktur und Entry Points

### P4.1 Architekturkarte

- aktiver CLI-, Web-, Worker- und Launcherpfad;
- Ownership pro Modul/Authority;
- veraltet/adapter/produktiv;
- Importzyklen und Rootmodule.

### P4.2 Composition Root

- Config, Paths, Key Provider, Store, Registry und Services an einem expliziten Startpunkt verdrahten;
- Domaincode liest keine Umgebungsvariablen und erstellt keine Default-Authorities;
- CLI/Web injizieren Ports/Provider.

### P4.3 Inkrementelle Package-Migration

- jeweils ein Rootmodul;
- alter Import bleibt als deprecateter Wrapper;
- Import-/Behavior-Equivalence;
- erst nach mindestens einem Release entfernen.

Exit: ein kanonischer CLI- und ein kanonischer Webentrypoint; Legacywrapper sichtbar und inventarisiert.

## P5 – Admin Composition, Auth, API und UI

Reihenfolge aus aktivem F6-Plan beibehalten:

1. Admin-Token/Bootstrap/Origin/Host/Rate-Limit fail-closed;
2. getrennte Validation-/Audit-/Stage-Key-Provider;
3. API-Verträge mit CAS, Kontext und Auditgrund;
4. reduzierte normale Source-View;
5. getrennte Admin-UI;
6. Playwright + axe + exakte Request-Payload-Akzeptanz;
7. keine Runtimewirkung.

Exit: Adminverwaltung ist sicher bedienbar, aber Aktivierung bleibt bis P6 entkoppelt.

## P6 – Runtime-Aktivierung

Separate Gates:

1. aktivierte Revision als atomarer Snapshot;
2. vollständige Authority-Abdeckung: Profile, Gruppen, Remedies, Relationen, Multiplexe;
3. eindeutige Fallbackpolicy nach Aktivierung: missing/stale/corrupt/disabled immer fail-closed oder explizit operatorbestätigt; kein stilles Legacy Revival;
4. Shadowvergleich und Known-Answer-Equivalence;
5. Rollback-/Recovery-Drill;
6. erst dann produktive Aktivierung.

Algorithmische Ergebnisse müssen bei Default/Legacy-Modus exakt äquivalent bleiben.

## P7 – Release und Betrieb

- SemVer-/Buildmetadaten und Changelog;
- signiertes/manifestiertes Releaseartefakt;
- SBOM und Dependency-Scan;
- strukturierte redigierte Logs mit Correlation/Job IDs;
- Health/Readiness ohne Secret-/PII-Leak;
- Backup-/Restore-/Key-Rotation-/Incident-Runbooks;
- Recovery Drill auf synthetischer Umgebung;
- Release-Gate mit Rollbacknachweis.

## P8 – Innovation und Performance

Erst nach stabiler Baseline:

- Profiling vor Optimierung;
- optionale GPU/Quantum/Hardwarepfade mit Capability Detection;
- deterministische Seeds und Known-Answer-Fixtures;
- neue Algorithmen additive opt-in, Default bleibt äquivalent;
- keine medizinischen Wirksamkeitsbehauptungen aus technischen Scores ableiten;
- Performanceziele als messbare Budgets, nicht als Architekturvermutung.

## Entscheidungspunkte für die Besprechung

1. Soll POSIX in v10 voll unterstützt oder für mutierende Authority-Pfade zunächst explizit fail-closed werden?
2. Soll v7-Backup automatisch in ein neues v8-Ziel migriert oder nur über einen expliziten Operator-Migrationsbefehl zugelassen werden? Empfehlung: expliziter Befehl.
3. Welche `Benutzer_Archive__ws-*`-Roots enthalten produktive/operatorbezogene Daten und welche sind synthetische Testartefakte? Vor P1 keine Löschung.
4. Soll CI zunächst lokal/selbstgehostet oder GitHub-basiert laufen? Keine produktiven Daten/Keys in Cloud-CI.
5. Welcher Entrypoint ist langfristig kanonisch: `apps/cli`, `apps/web`, oder ein gemeinsamer Composition Root mit beiden Interfaces? Empfehlung: gemeinsamer Root, getrennte Interfaces.
