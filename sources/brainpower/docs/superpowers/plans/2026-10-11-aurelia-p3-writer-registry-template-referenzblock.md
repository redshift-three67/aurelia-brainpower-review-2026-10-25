# Aurelia P3 – Writer, Registry und lesender Template-Abgleich

> Begrenzte Ausführung mit `superpowers:subagent-driven-development`. Freigegebener Referenzplan; keine Produktimplementierung, normative Templateänderung, Live-/Cloud-/Office-/WSL-/Routingaktion.

**Ziel:** Die verbleibende Morphic-Writer-/Restorekette präzise eingrenzen und heutige Hostvertragslücken für P4 festhalten. Vollständige Runtimeabnahme nicht durch statische Aufnahme ersetzen.

**Quellen:** Registrierter Worktree `C:/morphic_v1/.worktrees/operator-workbench-phase1`, erwarteter HEAD151e2bb0a69d49677a0b1e40e0bffd0f172d34c4. Bestehende `Modul_Templates` nur lesen. Keine führende Morphic-Quelle auswählen.

## W1 – Writervertrag (Luna6/max)

- [x] Launcher → CLI scan → tatsächlicher Exportwriter → Reportregistrierung gezielt verfolgen, höchstens zehn direkt relevante Dateien. Vor/nach SHA-256, HEAD und tracked-only Zustand festhalten.
- [x] Fachliche Klienten-/Sitzungs-ID, Job-/Versuchs-ID, Ausgabepfad, Inhalts-/Katalogrevision, Zeitpunkt und Fehler-/Abbruchgrenzen mit konkreten physischen Fundstellen trennen. Unverfolgte Pfade ausdrücklich offen halten.
- [x] Bericht und Sourcebinding ausschließlich unter `checkpoints/Aurelia-P3-Morphic-Writer-Contracts-20261011/` schreiben. Keine Importe/CLI-/Worker-/Writerausführung, Geschäftsdateien oder Secrets lesen; keine Agenten.

## R2 – Registry/Restore und Templates (Leitung)

- [x] Reale `_publish_without_overwrite`-Abhängigkeiten und unmittelbar benötigte Imports erfassen; keine Dummy-Registry oder ungeprüfte native Dateiöffnung.
- [x] Aktuelle `MODULE_REGISTRY.md`, `standards/MODUL_STANDARD.md`, `standards/API_CONTRACT.md` bytegebunden lesend aufnehmen; Definitionen vs. tatsächliche Runtime getrennt bewerten.
- [x] Writer-/Report-/Kontext-/Tenant-/Revision-/Job-/Asset-/Archivanforderungen den vorhandenen Hostverträgen zuordnen; fehlende/spezifische Zusagen als P4-Klärung benennen. Keine Behauptung einer vollständigen siebenmoduligen Matrix.
- [x] Konkreten nächsten isolierten positiven Backup-/Restore-Testscope aus echten Dependencies ableiten. Ausführung nur bei geprüftem Loader/Native-I/O-Scope; sonst vorbereiteter NOT_RUN-Vertrag mit Grund.

## Review und Abschluss

- [x] Astra6/medium unabhängig: Quellenbindungen, Fundstellen, Schlussfolgerungen und fehlende Evidenz prüfen. Keine privaten Rohdefinitionen, Geschäftsdaten oder Produktfreigabe.
- [x] Leitung aktuelle Hashes/HEAD nachrechnen; reine Dokumentänderungen mit eigener Vorher-/Nachhersicherung und Manifestprüfung abschließen. Wiederaufnahme-Historie vollständig erhalten.
- [x] Hauptplan um Teilnachweis und nächste konkrete offene Kante ergänzen. P0/P1/P2/P3, P4-Matrix vor P5-Entscheidung, P6–P8/S4.8 separat halten.

Orientierung45–75Minuten, kein Qualitätslimit. Zwei begrenzte Helfer maximal: Luna6/max Writeraufnahme, Astra6/medium Review; keine Änderung der effektiven Desktop-/Governorsroute.

Abschlussgrenze: Alle Häkchen betreffen diesen begrenzten statischen Block einschließlich vorbereiteter NOT_RUN-Prüfverträge, nicht die Ausführung der vollständigen Writer-/Registry-/Restoreabnahme. Aktueller Bericht: ../../verification/AURELIA_P3_WRITER_REGISTRY_TEMPLATE_2026-10-11.md. Keine normative Templateänderung. Lokaler Prüfpunkt Aurelia-P3-Writer-Registry-Status-20261011-174307Z; P0/P1/P2/P3 bleiben offen.
