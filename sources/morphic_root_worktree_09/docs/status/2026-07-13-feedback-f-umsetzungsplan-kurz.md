# Feedback f – Umsetzungsplan Admin/Repositories

- **Stand:** 2026-07-15
- **Gesamtstatus:** in Arbeit
- **Konservativ dokumentierter Fortschritt:** 55,6 %
- **Feedback f als Gesamtfeature:** NO-GO bis F8
- **Nächster zulässiger Schritt:** F5-A dokumentgebunden doppelt reviewen und danach extern rückverifiziert sichern; F5-B bleibt bis zur Wirksamkeit gesperrt

## Gateübersicht

| Gate | Inhalt | Status | Fortschritt | Nächster relevanter Schritt |
|---|---|---:|---:|---|
| **F0** | Ist-Analyse, Architektur- und Sicherheitsplan | ✅ GO | **100 %** | Abgeschlossen |
| **F1** | Contracts, isolierter SQLite-Store, Cross-Reference-Validierung | ✅ GO | **100 %** | Abgeschlossen; 66 Tests und unabhängiges APPROVE |
| **F2** | Offline Draft, Diff, Publish, Activate, Rollback | ✅ GO | **100 %** | F2.1–F2.4 abgeschlossen; unabhängiges APPROVE |
| **F3** | Profilverwaltung ohne stille Runtimewirkung | ✅ GO | **100 %** | F3.1–F3.3 abgeschlossen; zwei finale hashgebundene APPROVE |
| **F4** | Remedies und Multiplexe vereinheitlichen | ✅ GO | **100 %** | F4.1–F4.4 abgeschlossen; zwei finale hashgebundene APPROVE für F4.4 |
| **F5** | Source-Pipeline härten | 🟡 F5-A CONDITIONAL GO | **0 % formal** | Dokument-Doppelreview und Post-State-ShadowCopy; danach frühestens F5-B |
| **F6** | Geschützte Admin-API und UI | ⬜ offen | **0 %** | Authentisierung und lokale Adminoberfläche |
| **F7** | Erster Onlineadapter ohne Auto-Publish | ⬜ offen | **0 %** | Netzwerk weiterhin default-off |
| **F8** | Runtime-Umschaltung und Release | ⬜ offen | **0 %** | Atomare Runtime-Aktivierung und Release-Gate |

## Prozentstatus

| Kennzahl | Wert |
|---|---:|
| Vollständig abgeschlossene Gates | **5 von 9** |
| Rechnerischer Gate-Fortschritt | **55,6 %** |
| Gewichteter Fortschritt inkl. F4.4 | **55,6 %** |
| Konservativ dokumentierter Projektfortschritt | **55,6 %** |
| Noch offenes gewichtetes Äquivalent | **44,4 %** |
| Online-Repositories | **weiterhin NO-GO** |

## F2-Abschluss

| F2-Teilblock | Ziel | Status |
|---|---|---:|
| **F2.1** | Offline Admin-Service für Draft, Diff, Publish, Activate und Rollback | ✅ GO – 82 Tests, unabhängiges APPROVE |
| **F2.2** | Sicherer externer Catalog-Pfad mit Sandbox-/Symlink-/Reparse-Schutz | ✅ GO – 36 Pfadtests, hashgebundenes APPROVE |
| **F2.3** | Hashverifizierter Backup- und Recovery-Vertrag | ✅ GO – 31 Backup-Tests, 149 Admin-Tests, hashgebundenes APPROVE |
| **F2.4** | Audit-Integritätsstufen einschließlich späterer HMAC-Verankerung explizit machen | ✅ GO – 33 Tests, Known-Answer-Vektor, hashgebundenes APPROVE |

F2 bleibt vollständig offline und isoliert: keine Web-, Runtime-, Engine-, Legacy- oder Netzwerkverdrahtung und ausschließlich synthetische `tmp_path`-Daten.

## F3-Fortschritt

| F3-Teilblock | Ziel | Status |
|---|---|---:|
| **F3.1** | 502 Legacy-Profile read-only und deterministisch normalisieren; Aliase und Gruppenauflösung erhalten; CLI-Fallback separat inventarisieren | ✅ GO – 9 Tests, vollständiger Feldvergleich, hashgebundenes APPROVE ohne P0–P3 |
| **F3.2** | Profil-Draft-CRUD mit Tombstones, Gruppenvalidierung und Alias-Konflikten fail-closed | ✅ GO – 34 Tests, atomare Tombstone-Policy, hashgebundenes APPROVE ohne P0–P3 |
| **F3.3** | Read-only Runtime-Adapter im Schattenmodus | ✅ GO – 17 finale Fokus-/Integritätstests, atomarer verifizierter Snapshot, zwei finale hashgebundene APPROVE ohne P0–P3 |

F3.1–F3.3 haben keine produktive Verdrahtung. Legacy-Authority, CLI-Registry, Gruppenquellen, Enginepfade und `data/remedies.db` bleiben unverändert. F3 ist vollständig GO.

## F4-Fortschritt

| F4-Teilblock | Ziel | Status |
|---|---|---:|
| **F4.1** | 4.079 Remedies, 1.273 Pathogene und 4.373 Links hashgebunden, schemaexakt und ohne Runtimewirkung inventarisieren | ✅ GO – 14 Tests/1 hostbedingter Skip, zwei finale hashgebundene APPROVE ohne P0–P3 |
| **F4.2** | 55 Runtime-Multiplexe, 40 explizite Remedy-Gruppen, Relationmodell, Custommodelle und BAT-Fallbacks getrennt read-only inventarisieren | ✅ GO – 30 Tests/2 hostbedingte Skips, zwei finale hashgebundene APPROVE ohne P0–P3 |
| **F4.3** | Remedy-/Multiplex-Draft-CRUD und Cross-References | ✅ GO – 29 F4.3-Tests, 323 Admin-Passes/5 Skips, zwei finale hashgebundene APPROVE ohne P0–P3 |
| **F4.4** | Legacy-Remedy-Launcher explizit migrieren oder deprecaten | ✅ GO – Migration auf bestehende Authority, 21 Tests, PS5/PS7, Sandbox-DB, zwei finale hashgebundene APPROVE ohne P0–P3 |

F4.1–F4.4 besitzen keine neue produktive Catalogverdrahtung. `data/remedies.db` und alle Legacy-Authorities bleiben hashidentisch; automatische Publish-/Activate-Wirkung, Scan-/Engine-Runtimewirkung und Netzwerk bleiben NO-GO. F4 ist vollständig GO.

## F5-Makroblöcke und aktueller Zwischenstand

Die Makroblöcke konsolidieren zusammengehörige Umsetzungsschritte, ohne Teilnummern oder
Sicherheitsgates aufzuheben:

| Makroblock | Enthaltene Teilblöcke | Status |
|---|---|---:|
| **F5-A** | F5.5 Source-Policy/lokale Pfadgrenzen; F5.4 atomare Registry-, Audit- und Rollbackpfade; F5.1 vollständiger Batch-Hash, Replay und `analysis_only`-Quarantäne | CONDITIONAL GO; technische Doppel-APPROVE liegen vor, Dokumentreviews/ShadowCopy offen |
| **F5-B** | F5.2 typenspezifische Normalizer; F5.3 kontrollierte Draft-Übernahme | gesperrt bis F5-A GO |
| **F5-C** | F5.6 verbleibende Pipeline-Härtung; F5-Gesamtgate | gesperrt |

F5-A ist rein offline und erzeugt weder Catalog-Publish noch Aktivierung, Netzwerkzugriff,
typenspezifische F5.2-Normalisierung oder lokales Source-Daten-I/O. Das Batch-Ledger ist ein
atomar ersetztes lokales Konsistenzprotokoll mit Replay-Erkennung im intakten Ledger, kein externer
Tamper-Evidence-Anker und kein Source-Daten-Rollback. Die produktive Legacy-v1-Registry bleibt
read-only; Schreibpfade verlangen eine explizite revisionsfähige Arbeitskopie.

Die historischen Reviewbatches `deleg_9444028c` und `deleg_0ab4aeb0` sind nicht gatewirksam; alle
Befunde sind geschlossen. Freeze v3 besitzt zwei driftfreie technische APPROVE mit null P0–P3.
Der Gate-Record definiert CONDITIONAL GO, das erst nach zwei dokumentgebundenen APPROVE und externer
Post-State-Rückverifikation wirksam wird. Technischer Nachweis: Fokus `114 passed, 1 skipped`, Admin `437 passed, 6 skipped`,
breit `921 passed, 8 skipped` plus exakt 14 bekannte Baselinefehler, Top-5 `1 passed in 98.70s`;
statische Checks PASS. Das Consistency-Ledger verwendet Schema v3 und
`data-record-consistency`; `data-promote` ist nur deprecateter Alias. Diese Zahlen sind noch kein F5-A-GO.

## Evidenz

- F1-Gate-Record: `docs/status/2026-07-13-feedback-f-F1-contracts-store.md`
- F2.1-Gate-Record: `docs/status/2026-07-13-feedback-f-F2-1-offline-service.md`
- F2.2-Gate-Record: `docs/status/2026-07-13-feedback-f-F2-2-pfadpolicy.md`
- F2.3-Gate-Record: `docs/status/2026-07-13-feedback-f-F2-3-backup-recovery.md`
- F2.4-Gate-Record: `docs/status/2026-07-13-feedback-f-F2-4-audit-integrity.md`
- F3.1-Gate-Record: `docs/status/2026-07-14-feedback-f-F3-1-legacy-profile-normalisierung.md`
- F3.2-Gate-Record: `docs/status/2026-07-14-feedback-f-F3-2-profil-draft-crud.md`
- F3.3-/F3-Gate-Record: `docs/status/2026-07-14-feedback-f-F3-3-runtime-shadow-adapter.md`
- F4.1-Gate-Record: `docs/status/2026-07-14-feedback-f-F4-1-legacy-remedy-import.md`
- F4.2-Gate-Record: `docs/status/2026-07-14-feedback-f-F4-2-legacy-multiplexmodelle.md`
- F4.3-Gate-Record: `docs/status/2026-07-14-feedback-f-F4-3-remedy-multiplex-draft-crud.md`
- F4.4-/F4-Gate-Record: `docs/status/2026-07-14-feedback-f-F4-4-legacy-remedy-launcher.md`
- F5-A-Gate-Record: `docs/status/2026-07-15-feedback-f-F5-A-source-pipeline-hardening-gate.md`
- Vollständiger Gateplan: `.hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md`
- Gesamtfortschritt: `docs/status/2026-07-12-gesamtstruktur-fortschritt.md`
