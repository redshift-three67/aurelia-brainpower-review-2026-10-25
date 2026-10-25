# Tiefenanalyse des aktuellen Projektstands

## 1. Executive Summary

Das Projekt ist ein großer, funktionsreicher Python/FastAPI/CLI-Monolith mit modularisierten Kernbereichen, umfangreicher TDD-Evidenz und außergewöhnlich konservativer Change-Control für kritische Authorities. Die aktuelle F5-B/v10-Arbeit schließt reale P1-Sicherheitsbefunde aus zwei driftfreien v9-Reviews. Zwei Root-Cause-Klassen sind inzwischen substanziell bearbeitet: externe HMAC-Authentisierung der Draft-Validation-Attestation und Windows-handlebasierte Authority-Publikation einschließlich Parent-/Temp-Swap-Abwehr. Der aktuelle Scope ist jedoch **nicht freigabefähig**, weil Schema-v7→v8-Migration, alte Backups, Backup-/Restore-Publikation, POSIX-Parität und produktive Provider-Komposition offen sind. Es existiert kein Freeze v10 und keine aktuelle Vollregression.

Gesamturteil: **fortgeschrittener, gut getesteter Entwicklungsstand mit professioneller Security-Governance, aber aktuell formell und technisch `NO-GO` für F5-B**.

## 2. Größe und Struktur

| Kennzahl | Livewert | Messbasis |
|---|---:|---|
| Git-getrackte Dateien | 585 | `git ls-files` |
| Python-Dateien | 290 | Endungszählung über `git ls-files` |
| Python-Zeilen | 71.179 | UTF-8-Zeilenzählung der getrackten `.py`-Dateien |
| Markdown-Zeilen | 21.963 | gleiche Methode |
| JSON-Zeilen | 114.499 | gleiche Methode; überwiegend Daten, nicht Programmcode |
| JavaScript/CSS/HTML | 2.946 / 2.742 / 1.913 Zeilen | gleiche Methode |
| statisch gefundene Testfunktionen | 653 | Regex `^def test_|^async def test_`; Parametrisierungen erhöhen reale Testfälle |
| kompakter Git-Status | 351 Zeilen | 37 modifiziert, 314 untracked Einträge |
| vollständige untracked Population | 63.994 Dateien | `git status --short --untracked-files=all` |

Die 63.994 untracked Dateien umfassen 195 `Benutzer_Archive__ws-*`-Roots mit 63.750 Dateien. Die Root-Zeitstempel reichen vom 10. bis 15. Juli 2026; sie wurden nicht als Teil dieser Analyse gelöscht oder verändert. Das ist primär ein Repository-/Runtime-Hygienerisiko, nicht automatisch ein v10-Codefehler.

### Schichten

```text
PowerShell/CMD-Launcher + CLI + FastAPI/Vanilla-JS
                    |
               apps/cli, apps/web
                    |
       Services / Operator- und Job-Orchestrierung
                    |
 core/*: Analyse, Profile, Gruppen, Reporting, Privacy
                    |
 core/admin_catalog + source_registry/source_data_promotion
                    |
 SQLite-, JSON-, Stage-, Ledger- und Export-Authorities
```

Relevante F5-B-Verantwortung:

| Modul | Verantwortung | Aktueller Zustand |
|---|---|---|
| `core/admin_catalog/store.py` | Catalog-Drafts, Revisionen, Validate/Publish, Schema | HMAC-Attestation integriert; Migration fehlt |
| `core/admin_catalog/validation_attestation.py` | externe Validation-Key-Authority | neu, explizit injizierbar, kein unsicherer Default |
| `core/admin_catalog/backup.py` | SQLite-Backup/Restore, Manifest/Fingerprint | Schema 8 gebunden; Publikation und v7-Kompatibilität offen |
| `core/source_registry.py` | Registry und gemeinsame FS-Commitprimitive | Windows deutlich gehärtet; POSIX unter starkem Angreifermodell offen |
| `core/source_data_promotion.py` | Stage/Index/Ledger/Snapshot/Key | verwendet gemeinsame Primitive |
| `apps/cli/commands/sources.py` | CLI-Komposition | konstruiert `CatalogStore(catalog_db)` noch ohne Validation-Key-Provider (`:355`) |

## 3. Formeller Gate- und Freeze-Stand

| Gate | Status | Evidenz |
|---|---|---|
| F1 | GO | aktiver Plan `:108-115` |
| F2 | GO | Plan `:119-186` |
| F3 | GO | Plan `:190-238` |
| F4 | GO | Plan `:242-309` |
| F5-A | abgeschlossen | Plan `:313-315` |
| F5-B | **NO-GO** | Freeze v9 `:7-29,285-292` |
| Freeze v8 | superseded | ein APPROVE, ein REQUEST CHANGES |
| Freeze v9 | superseded | beide Reviews REQUEST CHANGES, P1-Befunde |
| Freeze v10 | existiert nicht | aktueller Livezustand |

Der aktive Plan ist in `:315` erkennbar hinter dem Livezustand: Er beschreibt noch die Vorbereitung von Freeze v9 und muss erst nach Abschluss des v10-Implementierungs-/Verifikationsblocks aktualisiert werden. Eine vorzeitige Planänderung während der Reparatur ist möglich, würde aber später in den Freeze-Scope gehören.

## 4. V9-Root-Causes und heutige Closure

| Root Cause | Aktueller Closure-Stand | Bewertung |
|---|---|---|
| Parent vor Handlebindung austauschbar | Registry bindet Parent-Identität beim Trusted Read und hält Windows-Parent-Handle über Save (`source_registry.py:179-180,253-254,665-675,983-1074`) | gezielt geschlossen, noch nicht unabhängig reviewt |
| Tempname statt Temp-Inode publiziert | Windows `SetFileInformationByHandle(FileRenameInfo)` über gebundenen Descriptor (`source_registry.py:1077-1215`) | gezielt geschlossen, noch nicht unabhängig reviewt |
| SQLite-Attestation forgebar | externe HMAC-Attestation mit Authority-/Key-ID und kanonischem Kontext (`store.py:145-178,1175-1194`) | gezielt geschlossen, noch nicht produktiv komponiert/reviewt |
| Schema-v7→v8-Migration fehlt | bestehende Nicht-v8-DB wird nur abgewiesen (`store.py:1187-1194`) | **offen** |
| Backup/Restore außerhalb gleicher Commit-Boundary | `backup.py:133-143,205-230,299-321` nutzt eigene `os.rename/os.link/os.replace`-Pfade | **offen** |

### Externe Validation-Attestation

Positiv:

- Provider ist explizit und optional am Konstruktor; Validate/Publish sind ohne Provider fail-closed.
- Schema bindet Catalog-Schema 8, Attestation-Format 1, Authority-ID, Key-ID und Algorithmus (`store.py:145-166`).
- Update und Delete der Attestation sind triggerseitig blockiert (`store.py:168-178`).
- Gezielte aktuelle Admin/F5-B-Matrix: 134 passed.

Offen:

- CLI-/produktive Composition Root injiziert keinen Provider (`apps/cli/commands/sources.py:355`).
- Key-Lifecycle, persistente externe Authority, Rotation und Betriebsanweisung sind noch kein produktiver Gate-Vertrag.
- Ein v7-Draft kann nicht kontrolliert auf Neuvalidierung migriert werden.

### Authority-Publikation

Positiv auf Windows:

- Parent wird mit nicht lösch-/umbenennbarer Handlefreigabe gehalten (`source_registry.py:999-1046`).
- Temp-Datei wird einmal geöffnet, identitätsgeprüft und der Descriptor registriert (`:1077-1141`).
- Rename publiziert den gehaltenen Handle, nicht den erneut aufgelösten Tempnamen (`:1144-1215`).
- Tempname-Swap und Parent-Substitution besitzen tatsächliche RED→GREEN-Verträge.
- Source-/Registry-/Draft-/CLI-Matrix: 109 passed.

Offen:

- Die neue Baseline-Parent-Identität gilt gezielt für `SourceRegistry.save()`. Die allgemeinen Helper `_atomic_replace_json()` und `_atomic_publish_bytes()` öffnen den aktuell sichtbaren Parent ohne eine vom vorherigen Authority-Read/Lock transportierte `expected_identity` (`source_registry.py:1238-1265`). Damit bleiben Stage, Index, Ledger, Rollback-Snapshot und Stage-Key gegen Parent-Substitution nicht gleich stark gebunden. Das ist ein eigener v10-Blocker und darf nicht aus dem grünen Registry-Test abgeleitet werden.
- POSIX Replace/Link verwendet weiter Namen relativ zum Directory-FD (`source_registry.py:1202-1223`); der Parent ist gebunden, der gehaltene Temp-Inode aber nicht zwingend die Publikationsquelle. Unter dem expliziten starken Namespace-Angreifermodell ist dies nicht ausreichend.
- `target.parent.mkdir(...)` vor dem Guard (`:1245,1261`) ist für bereits existierende Authorities anders zu bewerten als für neue Roots und benötigt einen expliziten Scope-/Nullmutation-Vertrag.
- Die globale Descriptor-Registry ist prozesslokal; Parallelität ist getestet, aber noch nicht unabhängig adversarial reviewt.

## 5. Backup, Restore und Migration

`core/admin_catalog/backup.py` bindet derzeit Catalog-Schema-Version 8 und Fingerprint `3dde32b4…5385c5` (`:14-23`). Integritäts-, Sidecar-, Bundle- und Hashprüfungen sind umfangreich (`:61-130,146-178,236-318`). Die offenen Grenzen sind jedoch freigabeblockierend:

1. Kein expliziter v7-Fingerprint-/Migrationspfad.
2. `_load_manifest()` akzeptiert ausschließlich die aktuelle Version 8 (`:246-250`), ohne versionierte Upgradeentscheidung.
3. Backup-Erzeugung veröffentlicht DB und Manifest separat mit `os.replace` (`:205-230`); es gibt keinen abschließenden Completion-Record, der nur ein vollständig durables Bundle autorisiert.
4. Restore publiziert über eine separate Pfadprimitive (`:133-143,299-321`) statt dieselbe parent-/handlegebundene Boundary wie Registry/Stage.
5. Fehler nach Zielpublikation dürfen keine unsichere pfadbasierte Rollback-Löschung auslösen; dieser Operator-Recovery-Vertrag muss explizit getestet und dokumentiert werden.

## 6. Test- und Qualitätsstand

| Nachweis | Aktuelles Ergebnis | Aussagegrenze |
|---|---:|---|
| F5-B + Admin Service/Remedy/Profile | 134 passed | aktuell, gezielt |
| Source/Registry/Atomicity/Promotion/Draft/CLI | 109 passed | aktuell, gezielt |
| Atomicity + Promotion | 68 passed | aktuell, gezielt |
| Ruff im aktuellen Änderungsscope | PASS | aktuell, begrenzter Scope |
| letzte Vollsuite v9 | 1002 passed, 8 skipped, 14 baseline-identische Fehler | historisch; **nicht v10-gültig** |
| Top-5 v9 | 1 passed | historisch; nicht v10-gültig |

Die 14 historischen Vollsuitefehler waren ein datumsabhängiges Consent-Fixture und 13 In-Process-Rate-Limiter-Fälle; die HTTP-Fälle liefen v9 einzeln 13/13 grün. Für professionellen Releasebetrieb sind baseline-identische Fehler trotzdem technische Schuld und sollten nach F5-B separat geschlossen werden.

## 7. Produktive Authorities und Betrieb

| Objekt | Livebefund 2026-07-16 |
|---|---|
| `config/source_repositories.json` | SHA-256 `6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3` |
| `data/remedies.db` | SHA-256 `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0` |
| produktiver `.stage-key` | fehlt |
| `MORPHIC_ADMIN_STAGE_KEY` | nicht gesetzt |
| Port 8000 | frei |
| Radi144 | `127.0.0.1:8090`, PID 3304 |

Kein produktives Backup und keine Post-State-ShadowCopy wurden in diesem Dokumentationsblock erzeugt.

## 8. Befundmatrix

| Nr. | Schwere | Befund | Konsequenz |
|---:|---|---|---|
| 1 | hoch | F5-B besitzt keinen positiven Freeze und keine Reviews | formales NO-GO |
| 2 | hoch | v7→v8-DB-/Backupmigration fehlt | bestehende Authorities nicht upgradefähig |
| 3 | hoch | Backup/Restore nutzt nicht die gemeinsame handlegebundene durable Boundary | Namespace-/Crashfenster |
| 4 | hoch | Stage/Index/Ledger/Snapshot/Key transportieren keine zuvor gebundene Parent-Identität in die gemeinsame Commitprimitive | Parent-Substitution bleibt außerhalb `SourceRegistry.save()` offen |
| 5 | hoch | POSIX publiziert weiterhin tempnamenbasiert | starkes Angreifermodell nicht geschlossen |
| 6 | hoch | produktive Validation-Key-Komposition fehlt | sicherer Validate/Publish-Betrieb nicht erreichbar |
| 7 | mittel | aktiver Plan ist gegenüber v10-Livecode veraltet | Handoff-/Freeze-Driftrisiko |
| 8 | mittel | 351 kompakte Statuszeilen und 63.994 untracked Dateien | Review-, Packaging- und Operatorrisiko |
| 9 | mittel | pyproject/requirements sind nicht deckungsgleich | nicht reproduzierbare Umgebung |
| 10 | mittel | keine getrackte CI-Workflowdatei gefunden | Qualität hängt von manuellen Gates ab |
| 11 | niedrig | zahlreiche Root-Skripte/Legacy-Einstiegspunkte | Wartbarkeit und Authority-Klarheit sinken |

## 9. Reifegrad

| Dimension | Bewertung | Begründung |
|---|---:|---|
| Funktionalität | 4.0/5 | breite Engine-, CLI-, Web- und Admin-Funktionalität |
| Testtiefe | 4.2/5 | starke adversariale TDD-Matrix; Vollsuite nicht aktuell grün |
| Security/Governance | 4.1/5 | außergewöhnlich strenge Freeze-/Reviewregeln; v10 noch offen |
| Architektur/Wartbarkeit | 3.1/5 | gute neue Module, aber monolithischer/legacyreicher Gesamtbaum |
| Reproduzierbarkeit/CI | 2.5/5 | kein sichtbarer CI-Workflow, Dependency-Dualität |
| Dokumentation | 3.8/5 | umfangreich, aber Statusdrift und hohe Gate-Dokumentmenge |
| Releasefähigkeit aktuell | 2.4/5 | F5-B NO-GO, kein v10-Freeze, schmutziger Worktree |
| gewichteter Gesamtstand | **3.5/5** | fortgeschrittene Entwicklungsbasis, noch kein professionell freigegebener Gesamtzustand |
