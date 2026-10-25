# P3 – separater Windows-v7→v8-Migrationsnachweis

Stand: 11.10.2026. Zwei frische tatsächliche Läufe mit korrigierter und erneut geprüfter Fixture: jeweils **12 bestanden, 0 Fehlschläge, 0 Fehler, 0 Skips**. Ausschließlich synthetische Kataloge; keine produktive Migration oder Aktivierung. Der frühere Windows-v8-Nachweis bleibt eigenständig unverändert.

| Prüfumfang | Ergebnis und Grenze |
|---|---|
| Direkte Originalmigration | Exaktes v7-Schema wird v8; erneuter v8-Aufruf liefert `False` und lässt Bytes gleich. Zwei leere synthetische Drafts, ihre Inhalte/Version/Hashes und Kontextfelder erhalten |
| Validierungsstand | Alte Marker `validated_version` und `validated_payload_hash` werden NULL; neue Attestationstabelle leer. Keine tatsächliche erneute Validierung oder Publikationsverweigerung ausgeführt |
| Transaktionsfehler | Fehler am vorhandenen `_migration_checkpoint` vor DDL, nach DDL und vor Commit: alte Datenbankbytes, Schema und Marker erhalten; keine Journal-/WAL-/SHM-Reste |
| Öffentlicher Weg | Originales `migrate_catalog_backup_v7_to_v8` erzeugt neues v8-Bundle, anschließend tatsächliches `restore_catalog_backup` auf neues Ziel. Alte v7-Sicherung und Seed bleiben erhalten |
| Negative öffentliche Eingaben | Vorhandenes Ziel, Datenbanktamper, zusätzliche Completiondatei, v8-Eingabe statt v7 und injizierter Migrationsfehler geprüft; jeweils Ablehnung bzw. Snapshot-Cleanup |
| Unabhängiger Readback | Je39 erfolgreiche synthetische Artefakte per Hash geprüft; beide v8-Bundles/Restores und erhaltene v7-Bundles separat gegen Manifest/Completion verglichen |

## Quellen, Fixture und tatsächliche zwölf Fälle

Originalstand `C:/morphic_v1/.worktrees/operator-workbench-phase1`, HEAD `151e2bb0a69d49677a0b1e40e0bffd0f172d34c4`; tracked-only Status leer. Die zehn Module des früheren positiven v8-Harness plus exakt `core.admin_catalog.migration` wurden aus gebundenen Originalbytes geladen. Elf ausgeführte/beobachtete Module, keine Produktinitialisierer. Originalquellbytes und Algorithmen unverändert; drei Registry-Funktionen durch delegierende Eingabeguards umschlossen, vorhandener Migrationscheckpoint für Fehlerproben temporär ersetzt. Source-Hashes, HEAD, Status und Runner/Test sind vor/nach und zwischen beiden v2-Läufen gleich. Keine Bytegleichheit zu HEAD oder kontinuierliche Überwachung daraus ableiten.

Die neue Fixture ist **nicht** das vollständige historische Known-Answer-Datenmodell. Ein tatsächlicher `CatalogStore` erzeugt zwei leere Drafts (gleicher synthetischer Operator/Workspace, zwei Tenants). Nur in diesem synthetischen Seed wird die Attestationstabelle entfernt und werden alte Validierungsmarker gesetzt; SQLite entfernt ihre angehängten Trigger. Der unveränderte v7-Fingerprint muss passen. Der originale Snapshothelper erstellt daraus die eigentliche Backupdatenbank; danach wird deren Fingerprint erneut geprüft und erst dann das v7-Manifest gebildet. Der v7-Eingangsvertrag verlangt exakt zwei Dateien, kein Completionrecord; der v8-Ausgang exakt drei Dateien.

| Testname | Zweck |
|---|---|
| `test_guards_reject_external_native_sqlite_write_process_import` | Guardkontrollen zuerst, ohne vorherige SQLite-Fixture |
| `test_direct_migration_preserves_context_and_requires_revalidation` | Direkte Migration, Markerreset, Kontextabfragen und idempotentes v8 |
| `test_direct_unsupported_schema_rejected_unchanged` | Nicht unterstütztes Schema ohne Mutation abweisen |
| `test_rollback_before_ddl` | Rollback vor Schemaänderung |
| `test_rollback_after_ddl` | Rollback nach Schemaänderung |
| `test_rollback_before_commit` | Rollback vor Commit |
| `test_public_migration_and_restore` | Öffentliches v7-Bundle → v8-Bundle → neues Restoreziel |
| `test_public_existing_target_preserved` | Bestehendes Ziel bewahren |
| `test_public_source_tamper_rejected` | Hashabweichung abweisen |
| `test_public_extra_completion_rejected` | Nicht erlaubte dritte v7-Datei abweisen |
| `test_public_injected_migration_failure_cleanup` | Originaler Fehlercheckpoint und temporärer Cleanup |
| `test_public_v8_source_rejected` | Falsche Eingangsversion abweisen |

Je Lauf vier Eingabedelegationen an `_directory_commit_guard`, `_held_file_identity` und `_windows_rename_bound_temp`: drei v8-Bundledateien plus ein Restore. Alle vier Renames erfolgreich, `replace=False`; die Restore-Delegation nach `restored.sqlite3` wird ausdrücklich geprüft. **Das sind Funktionsdelegationen, keine direkten WinAPI-Aufrufzahlen.**

## Erhaltene Fehler und Korrekturgrenzen

Der erste tatsächliche v1-Lauf: fünf erfolgreiche Tests und ein Fehler, null Skips; Abbruch vor dem Migrationscheckpoint wegen Snapshot-/Manifest-Byteabweichung. Kein erfolgreicher öffentlicher Migrationslauf daraus behauptet. Beleg, genaue alte Harnessbytes/Baseline und zwölf Fehlerartefakte sind erhalten und unabhängig erneut gehasht.

Root-Diagnose ausschließlich mit Standardbibliothek und schreibgeschützter synthetischer Eingabe: erster SQLite-Snapshot unterscheidet sich an Offsets27/43/95, zweiter ist bytegleich; Inputs erhalten. Luna hat statisch den historischen Fixture-Helper verfolgt: auch er erzeugt vor dem Manifest einen Snapshot. Korrigiert wurde nur die Testfixture, keine originale Hashprüfung/Migration. Keine allgemeine Zusage, dass jede beliebige schemaidentische SQLite-v7-Datei snapshot-bytegleich ist. Die historische Testquelle wurde nur gelesen, nicht als Modul importiert oder ausgeführt.

Die erste Abschlussprüfung blockierte außerdem vor Erstellung des Dokumentenpunkts wegen eines ungültigen 63-stelligen Hashs im statischen Herkunftsbeleg. Altbeleg und Diagnose bleiben erhalten. Der programmgenerierte v2-Beleg dokumentiert zwei neue direkte Byte-Reads mit gleicher Größe30058 und gültigem SHA-256 `34146cdc6b7fed69cbcecbcdad9fdc687a8a0b0ff8db7bfb68b06031e9de5cfd`; Root prüft ihn frisch. **Frühere Kontinuität dieser nicht ausgeführten historischen Fixturequelle bleibt unbekannt.** Dies korrigiert keinen der elf Produktquellenhashes und keine Testlogik; die erfolgreichen Läufe mussten deshalb nicht wiederholt werden.

## Review und Sicherung

Leitung: eigener neuer Harness, Originalausführung, Diagnose, unabhängige Quellen-/Receipt-/Artefaktnachrechnung und Konsolidierung. **GPT-6 Luna/max**: begrenzte statische Quellen-/Fixtureaufnahme. **GPT-6 Astra/medium**: unabhängiger SPEC→QUALITY-, Korrektur-, Ergebnis- und Abschlusswerkzeugreview; keine eigene Testausführung oder vollständige Scratch-Nachberechnung. Review ersetzt keine Betreiberautorisierung.

Geprüfte v2-Hashes: Runner `4b9f3b087a7f1017de961196d9c18c7e5a9025cbba01baf959910b0fbf518edc`; Test `84bd2c9f3644714b0c9b1c69409da501392daebc092c14be9c5444599f84c400`; Abschlusshelper `1e2710aaa792009a4a3bc5b9c8d984aab74d4b116695fcd3d9670da2c475a407`. Root vergleicht den Helper vor beiden Abschlussphasen separat mit dem Reviewhash.

Lokaler Dokumenten-/Referenzpunkt: `checkpoints/Aurelia-P3-V7-Migration-Status-20261011-191912Z`. Sein vierteiliger Vorher-Dokumentstand ist vor Änderungen separat manifestiert und rückgelesen. Abschlussphase prüft Quellen/Harness/erhaltene Artefakte erneut, dann Vorher-Manifest und vollständigen historischen Wiederaufnahme-Bytesuffix, danach Nachherbestand und dessen Manifest. Der tatsächliche Abschlussbeleg entscheidet über den erfolgreichen final-Lauf; dieser Bericht allein bestätigt noch keine Versiegelung. Keine F:-Vollsicherung, keine externe Authentizitätsgarantie aus Hashmanifesten.

## Verbleibende Grenzen und nächste Reihenfolge

Keine Auth-/Mandantensicherheitsabnahme aus Kontextabfragen. Keine Datenerhaltungszusage für gefüllte historische Einträge, Sourceimports, Revisionen, Tombstones, Aktivierungen oder Auditbestände; deren Originaltesttexte wurden nicht ausgeführt. Keine produktive Aktivierung, Keys/Patienten/Defaults, API/CLI/Jobwriter, externe Dienste, WSL/Cloud/Office/Routing oder Liveeingriffe. Python-Guards sind keine OS-Sandbox; native/deskriptorbasierte I/O wird nicht global überwacht. Crash/Race/Reparse/ACL, konkurrierende Zielerstellung, fremde temporäre Datei, tatsächliche Revalidierung und POSIX bleiben eigene Prüfungen.

P3 nächster unabhängiger Weg: unveränderte POSIX-Ablehnung mit tatsächlicher temporärer Cleanup-Probe; übrige Registry-/Writer-/Job-/RMF-Verträge, P0/P1/P2 und RF-E1 bleiben offen. Danach P4 vollständige siebenmodulige Matrix einschließlich Aurelia/Modul_Templates; erst P5 Entscheidung über die zentrale Datenstruktur. Für P4 sind ursprünglicher Sicherungsstand, abgeleiteter Migrationsstand, Schema-/Inhaltsrevision und Validierungsstatus getrennt zu führen. Keine normative Templatesynchronisierung oder Migrations-/Integrationsfreigabe durch diesen Nachweis.

[Quellenvertrag](../../checkpoints/Aurelia-P3-V7-Migration-Sources-20261011/CONTRACT.md) · [Fixture-Nachtrag](../../checkpoints/Aurelia-P3-V7-Migration-Sources-20261011/SNAPSHOT_FIXTURE_ADDENDUM.md) · [Prüfbelege](../../checkpoints/Aurelia-P3-V7-Migration-Tests-20261011/) · [vorheriger v8-Nachweis](AURELIA_P3_PUBLIC_RESTORE_2026-10-11.md).
