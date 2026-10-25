# P3 – öffentlicher Windows-Backup-/Restoreweg

Stand: 11.10.2026. Begrenzter positiver Referenznachweis an ausschließlich synthetischen Schema-v8-Katalogen. Zwei frische Läufe des unveränderten, vor Ausführung geprüften Harness: jeweils **10 bestanden, 0 Fehlschläge, 0 Fehler, 0 Skips**. Keine vollständige Modul-, Mandanten-, Writer-/Job- oder Linux-Abnahme.

| Gegenstand | Tatsächliches Ergebnis |
|---|---|
| Öffentliche Funktionen | Originale `create_catalog_backup` und `restore_catalog_backup` ausgeführt; keine Ersatz-Registry oder Guardumgehung |
| Backup | Öffentliche Erstellung von SQLite, Manifest und Completion; SHA-256, Größe, Schema 8 und `no_productive_activation` geprüft |
| Wiederherstellung | Neuer Zielkatalog bytegleich zum gesicherten SQLite; Integrität, Drafts und Kontextabfragen erhalten; zwei unabhängige neue Zieldateien geprüft |
| Windows-Publishing | Delegation an originale Registry-Funktionen; 18 Rename-Delegationen erfolgreich, eine erwartete `FileExistsError`; alle mit `replace=False` |
| Negativfälle | Vorhandenes Backup-/Restoreziel erhalten, manipulierte Datenbank und fehlende Completion abgelehnt; direkte Publish-Fehler bereinigen temporäre Datei |
| Quellen und Harness | Zehn aktuelle Quelldateien sowie Runner/Test vor/nach und zwischen Läufen hashgleich; HEAD und tracked-only Status gleich |
| Gespeicherte Nachweise | Je 29 synthetische Dateien unabhängig erneut per Hash geprüft; Roundtrip-Datenbank, Manifest und Completion zusätzlich miteinander verglichen |

## Ausführung und Bindung

Originalquelle: `C:/morphic_v1/.worktrees/operator-workbench-phase1`, HEAD `151e2bb0a69d49677a0b1e40e0bffd0f172d34c4`, tracked-only Status leer. Zehn Module: `apps.web.durable_io`, `core.admin_catalog.source_policy`, `core.source_registry`, `core.admin_catalog.contracts`, `validation_attestation`, `validation`, `store`, `service`, `paths`, `backup` (die letzten sieben unter `core.admin_catalog`). Module werden aus unveränderten gebundenen Bytes geladen; keine Produkt-`__init__`-Datei ausgeführt. Das Laden von `durable_io` belegt allein keine Prüfung aller seiner Funktionen.

Lunas statische Aufnahme empfiehlt private Alias-Namensräume. Der tatsächliche Harness nutzt stattdessen leere `core`-/`apps`-Namensräume mit begrenzten Imports und ursprünglichen `__file__`-Pfaden. Diese Abweichung ist ausdrücklich dokumentiert; beide Wege vermeiden Produktinitialisierer. Ausgeführte und beobachtete Modulmenge stimmen mit den zehn zugelassenen Modulen überein.

Runner-SHA-256: `06cbe5aef295b6464f6ec077f90886be2ddd075786ef7a241e5fc4034aba3234`. Test-SHA-256: `3508d47eda5ed3fd3484571e79b34e945d24a820f7835b6884ab97929a1369b8`. Statische Quellenbindung: `9b4c77622ce80d3d9adb713ead36e8981be8012e7a06e02dd756246f8be1b930`.

Die erste statische Baseline führte null Produktmodule aus. Vor Produkt-I/O wurden zwei Astra-Befunde korrigiert: Guard-Test ohne vorherige SQLite-Fixture; Runner-Lesezulassung und Fehlerformatierungsfallback. Beide tatsächlichen Läufe sind an die danach geprüfte Baseline v2 gebunden. Keine Produktfehler wurden durch Mocks oder Ersatzquellen verdeckt.

## Zehn tatsächliche Prüffälle

| Testname | Begrenzter Nachweis |
|---|---|
| `test_guards_reject_external_native_sqlite_write_process_import` | Erste Kontrolle vor Produkt-SQLite: unzulässige native Eingabepfade, SQLite-/Dateiziele, Prozess/Socket, Import und Umgebung abgewiesen |
| `test_public_backup_existing_root_preserves_sentinel` | Vorhandener Backuproot bleibt erhalten |
| `test_public_backup_restore_roundtrip` | Vollständige öffentliche v8-Erstellung und Wiederherstellung mit Draft-/Kontextprüfung |
| `test_public_generated_bundle_hash_tamper_rejected` | Gleich große Byteänderung im öffentlich erzeugten Backup abgelehnt |
| `test_public_generated_bundle_missing_completion_rejected` | Fehlender Abschlussnachweis abgelehnt |
| `test_public_restore_existing_target_preserves_sentinel` | Vorhandenes Restoreziel bleibt erhalten |
| `test_real_publish_existing_target_no_overwrite_and_cleanup` | Originaler Publish überschreibt nicht und entfernt temporäre Datei |
| `test_real_publish_wrong_hash_cleanup_before_native` | Falscher erwarteter Hash vor nativer Delegation abgelehnt; temporäre Datei entfernt |
| `test_real_publish_wrong_parent_identity_cleanup` | Abweichende Verzeichnisidentität abgelehnt; temporäre Datei entfernt |
| `test_two_independent_restore_targets_preserve_context` | Zwei separate Zielkopien; kontextgebundene Draftabfragen bleiben getrennt |

Je Lauf wurden 20 Eingabedelegationen an `_directory_commit_guard`, 19 an `_held_file_identity` und 19 an `_windows_rename_bound_temp` erfasst. Das sind **Funktionsdelegationen, keine direkten WinAPI-Aufrufzahlen**; eine Directory-Delegation kann vor dem nativen Öffnen fehlschlagen.

## Review, Absicherung und Grenzen

Leitung: Harness, beide Originalausführungen, unabhängige Hash-/Artefaktkontrolle und Konsolidierung. **GPT-6 Luna/max**: begrenzte statische Quellen-/Loaderaufnahme, keine Originalausführung. **GPT-6 Astra/medium**: unabhängiger SPEC→QUALITY-Review, Ergebnisreview und statischer Abschlusswerkzeugreview, keine eigene Produktausführung. Review ersetzt keine Betreiberfreigabe.

Der erste vorläufige Dokumentenpunkt `Aurelia-P3-Public-Restore-Status-20261011-181956Z` hatte nur unmittelbaren Copy-Readback, kein Vorher-Manifest. Er bleibt unverändert als vorläufiger Beleg erhalten; keine rückwirkende Integritätsbehauptung. Vor Dokumentänderungen wurde ein frischer Punkt mit separat rückgelesenem Vorher-Manifest erstellt: `checkpoints/Aurelia-P3-Public-Restore-Status-20261011-182431Z`. Abschlusskontrolle prüft zunächst Quellen/Harness/Prüfartefakte erneut, dann die vier Vorher-Dateien vor dem vollständigen Wiederaufnahme-Bytesuffixvergleich und anschließend den gesamten lokalen Nachher-Manifestbestand. Status und Anzahl stehen im tatsächlichen Abschlussbeleg; die Erstellung dieses Berichts allein ist noch keine Abschlussbestätigung.

Die Python-Guards begrenzen den bekannten Quell-/Aufrufpfad, sind keine OS-Sandbox; native/deskriptorbasierte I/O wird nicht global abgefangen. Kein Produktdefault, kein realer Registry-Konfigurationsbestand, Key oder Klientensatz verwendet; kein Netzwerk, CLI-/Jobworker, Cloud-/Office-/WSL-/Routing- oder Liveeingriff. Kontextabfragen sind kein Authentifizierungs-/Mandantensicherheitsnachweis. Nicht geprüft: öffentliche späte Create-Fehlerbereinigung, Crash/Race/ACL/Reparse, POSIX-Cleanup, v7-Migration, produktive Aktivierung und Writer-/Job-End-to-End. Keine F:-Vollsicherung.

## Konsequenz für die weitere Planung

Der bisher offene positive **Windows-Schema-v8-Referenzweg** ist jetzt durch zwei tatsächliche Läufe belegt. Frühere Berichte bleiben zeitgebundene eigenständige Nachweise. Übrige P3-Vertrags-/Registry-/Writer-/RMF-Abnahmen, P0/P1/P2 und RF-E1 bleiben offen. POSIX-Ablehnung/Cleanup und v7-Migration folgen getrennt. Danach P4: vollständige siebenmodulige Matrix mit Aurelia und Modul_Templates; erst P5: Entscheidung zur zentralen Datenstruktur. Normative Synchronisierung und Integration bleiben P6–P8/S4.8.

Belege: [Runner und Receipts](../../checkpoints/Aurelia-P3-Public-Restore-Tests-20261011/), [statische Quellenbindung](../../checkpoints/Aurelia-P3-Restore-Loader-Sources-20261011/SOURCE_BINDING.json), [vorheriger Writer-/Templatebericht](AURELIA_P3_WRITER_REGISTRY_TEMPLATE_2026-10-11.md).
