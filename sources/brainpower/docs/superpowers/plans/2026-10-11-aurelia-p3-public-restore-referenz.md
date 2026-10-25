# P3 – öffentlicher Windows-Backup-/Restoreweg

Freigegebene Fortsetzung des Registry-/Templatevertrags, keine Produktimplementierung. Ausführung mit `superpowers:subagent-driven-development` und unabhängiger SPEC→QUALITY-Prüfung.

Ziel: Originale `create_catalog_backup`/`restore_catalog_backup` über echte Registry-Publishfunktionen prüfen. Nur selbst erzeugte SQLite-v8-Kataloge unter neuem lokalem Prüf-Scratch. Keine Produktdaten, Defaults, Keys, Liveports, Cloud/Office/WSL oder normative Templateänderung. Kein POSIX-Guardbypass und keine Dummy-Registry. Keine führende Morphic-Quelle bestimmen.

- [x] L1 Luna6/max: zehn relevante Module, Importreihenfolge, Modullevel-Nebenwirkungen, Windows-Publishpfad und Quellbindung statisch aufnehmen. Erwarteter Worktree `C:/morphic_v1/.worktrees/operator-workbench-phase1`, HEAD151e2bb0a69d49677a0b1e40e0bffd0f172d34c4. Keine Originalausführung durch Worker.
- [x] T1 Leitung: neuer eigener Harness; sieben bekannte Katalogmodule plus drei direkte Dependencies, nur gebundene Bytes und leere Namespacepakete; keine Produktinitialisierer. Imports/Umgebung, Python-Dateimutationen, SQLite-Ziele, native Registry-Eingabepfade und Prozess-/Netzwerkstarts begrenzen. Guards sind keine OS-Sandbox.
- [x] T2 Echte positive öffentliche Erstellung/Restore mit Manifest/Completion/Hashes/v8-Schema/Originalbytes/Draft/Kontext prüfen. Zusätzlich Nichtüberschreiben, reale Publish-Ablehnung/Temp-Cleanup und unveränderte Quelle. Negative Guardkontrollen vor Original-I/O. Keine Behauptung von Crash-/Race-/ACL-/Tenant-Auth-/Writer-/Jobabnahme.
- [x] R1 Astra6/medium: SPEC dann QUALITY von Loader, Harness, Quellenbindung; vor Originalausführung Baseline bytebinden. Sicherheitsmängel vorher korrigieren; tatsächliche Produktfehler erhalten und getrennt beurteilen.
- [x] T3 Leitung: nach Freigabe eigener Lauf, bei unverändertem Harness zweiter frischer Lauf. Genaue Fallnamen/Anzahl/Skips, Quellen/HEAD/tracked-only/Harness vor/nach und native Delegationsbelege rücklesen. Abweichung ist Fehler, keine stillen Ersatzquellen/Mocks.
- [x] C1 Teilbericht/Hauptplan/Restarbeiten/Wiederaufnahme nach tatsächlichem Ergebnis; Vorher-/Nachher-Dokumentenprüfpunkt mit frisch geprüftem Manifest, alter Wiederaufnahmesuffix erhalten. Keine F:-Vollsicherung.

POSIX-Negativ/Cleanup und v7-Migration bleiben eigenständige spätere Pakete. Weitere P0/P1/P2/P3 und RF-E1 bleiben offen. P4 sieben Module mit Aurelia/Templates, dann P5 zentrale Datenstruktur, P6–P8/S4.8 separat. Orientierung60–90Minuten, Qualität ohne Zeitlimit. Höchstens zwei neue Helfer: Luna6/max und Astra6/medium; keine Routingänderung.
