# Backup-Betrieb Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans inline; no new user-owned task or subagent required.

**Goal:** Wiederholbarer vierstündlicher Offline-Backup-Ablauf mit unabhängiger Altersüberwachung und Fehler-E-Mail, zunächst deaktiviert installiert und manuell abgenommen.

**Architecture:** Den bereits real geprüften Roundtrip hashgebunden wiederverwenden. Laufresultat und letzter vollständig geprüfter Sicherungszeitpunkt getrennt atomar speichern; nur erfolgreiche Rückleseprüfung plus Aufräumen darf den Erfolgsstand verändern. Eigenständiger Watchdog meldet fehlenden/alten Stand und letzte Laufprobleme; keine laufende DB stoppen und keine NAS-Snapshots löschen.

**Tech Stack:** Python-Standardbibliothek, vorhandenes restic/GNU tar/PostgreSQL16, systemd.

## Umfang und Reihenfolge

- [x] Tests zuerst: Altersgrenzen, fehlende/future Daten, Erfolgskriterien, Fehler überschreibt keinen letzten Erfolg, Alarmdrosselung. `tests/test_backup_runtime23.py` (neun Tests bestanden).
- [x] `artifacts/server-backup-runtime23.py`: wiederverwendbare Zustands-/Alarmfunktionen, rootgeschützter Runner auf geprüftem Paket und unabhängiger Watchdog. Globale Lauf-Sperre, separate Watchdog-Sperre, atomare Zustände; Secrets nur auf dem Server lesen.
- [x] `artifacts/server-backup-install23.py`: feste Hashes prüfen, Rootkopien und systemd-Units schreiben; keinerlei Timeraktivierung. Vorhandene Dateien nicht überschreiben. Geprüften manuellen Beleg als Ausgangsstand übernehmen, ursprünglichen Aufnahmezeitpunkt beibehalten. Installer vorbereitet, Ausführung noch offen.
- [x] Linux-Syntax, systemd-analyze verify und synthetische Tests. Rootinstallation und einmaliger manueller Lauf in einem kurzen Bedienaufruf, Report per SSH geprüft: erfolgreich, Watchdog healthy, Timer aus (23.09.19:18 UTC).
- [ ] Erst nach dieser Abnahme Aktivierung konkret vorbereiten. Laufkalender alle4h UTC, Watchdog alle15min. Warnung ab8h, kritischer Voralarm ab11h, RPO überschritten ab12h. Kein RTO-Nachweis durch Timerinstallation.

## Grenzen

Retention7/4/6 bleibt Vorschau; tatsächliche Löschung erst nach konkreter Abnahme. Aktuelles Cold-Profil blockiert laufende DB; vor Produktivstart Online-Profil erforderlich. Lokale neue Zwischenarchive nach geprüftem Aushängen beseitigen; fremde/alte Arbeitsverzeichnisse unverändert. Fehlerzustände ohne Geheimnisse dauerhaft halten. Watchdog auf demselben Server kann vollständigen Server-/Netzausfall nicht melden; unabhängige Überwachung/Recovery bleiben eigene offene Punkte.

Reasoning: Medium für gesamten Backup-/Aktivierungsblock. Low hier nicht empfehlen.
