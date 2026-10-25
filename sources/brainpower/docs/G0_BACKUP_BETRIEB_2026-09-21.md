# Backup-Betrieb: Iststand und verbleibende Abnahme

23.09. Betreiberentscheidung: RPO höchstens12h, RTO höchstens12h, Aufbewahrung7täglich/4wöchentlich/6monatlich, Fehler per E-Mail. Empfänger/Versandweg und Abnahme noch offen. Siehe [gebündelter Server-/Hermes-Abschluss](SERVER_HERMES_ABSCHLUSS_2026-09-23.md). Die nachfolgenden historischen Aussagen zur zurückgestellten RPO-Entscheidung sind damit überholt; Timer bleibt deaktiviert.

23.09.13:48UTC: [Betriebsrepository-Vorbereitung abgeschlossen](verification/BACKUP_REPOSITORY_2026-09-23.md). Linux-Selftest und einmaliger Rootlauf bestanden; neues getrenntes SMB-Repository aurelia-operations-v1 vollständig geprüft, synthetischer Restore bestätigt. Eigener Mount entfernt, Originalzustand unverändert. Timer disabled/inactive, PostgreSQL gestoppt. Automatik und produktiver Dateien-/DB-Sicherungsablauf bleiben offen. Folgende Aussage „noch nicht übertragen/ausgeführt“ beschreibt den vorherigen Stand und ist damit überholt.

Betreiberfestlegung23.09.: vorläufig maximal12h Serverausfallzeit (RTO-Ziel). Noch kein gemessener vollständiger Wiederanlauf und keine G0-Freigabe daraus ableiten. RPO weiterhin zurückgestellt bis zur Aktivierungsentscheidung. Vorbereitungspaket in docs/superpowers/plans/2026-09-23-backup-repository-preparation.md; lokal getestet, noch nicht übertragen/ausgeführt.

Aktuell22.09.16:22UTC: [Sammelprüfung](verification/BACKUP_PREFLIGHT_2026-09-22.md) bestätigt fehlende Repository- UND Passwortdatei des automatischen Dienstes. SMB-Zugangsdaten root0600 vorhanden; NAS-Mount aktuell nicht eingehängt, Quellmounts vorhanden. PG sauber gestoppt, Sicherungswerkzeuge vorhanden; Timerdisabled/inactive. Fehlende Basiskonfiguration jetzt konkret belegt. Frühere Einzelsicherungen verwenden gesonderte Pfade und bleiben davon getrennte gültige Nachweise. Nächster Schritt: Einrichtungspaket vorbereiten, keine weiteren identischen Diagnoseläufe.

Stand: 21.09.2026. Lesende SSH-Prüfung; keine Timeraktivierung oder Änderung von Serverdiensten. Keine Gesamtfreigabe.

Aktualisierung22.09.: [Detailprüfung](verification/BACKUP_DETAIL_2026-09-22.md) liefert alle vier Quellen und fünf Ausschlüsse, stoppt anschließend mit FileNotFoundError beim Repository-Konfigurationsschritt. Ziel dieses automatischen Dienstes weiterhin nicht bestätigt. PostgreSQL-Datenverzeichnis liegt außerhalb der Quellen; automatische DB-Sicherung nicht durch diesen Dateidienst abgedeckt. Timer bleibt disabled/inactive. Keine Wiederholung von bpbd21.

Betreiberentscheidung: Maximale Datenverlustzeit (RPO) und Wiederanlaufziel (RTO) werden später gemeinsam besprochen. Vor einer Aktivierung des automatischen Backups gezielt erneut ansprechen. Bis dahin technische Prüfungen fortsetzen, keine Zielwerte als vereinbart behandeln.

## Ergänzung: privilegierte Strukturprüfung 21:06 UTC

Betreiber führte bpba21 aus. Bericht per SSH gelesen und unter artifacts/backup-audit21-report.json gespeichert; SHA256 lokal/servergleich `35ec11e61e6c3a2cf7cc205e592af0ac9dcf8a99d27833d83fd8b7c361956642`. Programmhash `be48545d39f4e65e7704a2f2e532a97f7ad95b79319e4dc016be69e58327ec73`, 484 Bytes, root750.

- Erkannt: `set -eu`, drei test-Zeilen, mountpoint-Aufruf und abschließendes exec /usr/bin/restic backup mit --repository-file, --password-file, --files-from /etc/aurelia-backup/paths und --exclude-file /etc/aurelia-backup/excludes. Unbekannte Argumente ausgeblendet; keine vollständige Semantikprüfung.
- Quellenliste: vier Einträge, davon /etc, /srv/build, /srv/aurelia erkannt; ein weiterer Eintrag redigiert. Liste root644, 47 Bytes, SHA256 `7838fb01a6796f4a52aff26b1e6d3d82ef79d3035b970af75c777a484f8214b4`.
- Ausschlussliste: fünf Einträge, alle redigiert. Liste root644, 93 Bytes, SHA256 `1c142882d63080fbdd066224b7260d71752ff7498df56083a801ecb95217f758`.
- Kein Backup gestartet, keine Änderung. Frisch bestätigt: Timer disabled/inactive, PostgreSQL16/main down.

Die begrenzte Ausgabe belegt noch nicht, dass alle notwendigen Daten enthalten und temporäre Bestände sowie laufende DB-Dateien korrekt ausgeschlossen sind. Auch Repositoryziel, Mountbedingungen und Passwortübergabe sind nur teilweise sichtbar. Nächste privilegierte Prüfung gezielt auf diese offenen Konfigurationsdetails bündeln; keine Wiederholung bereits erfolgreicher Restoretests. Automatik weiterhin nicht freigeben. Betriebsziele und Alarmempfänger sind separat zu entscheiden.

## Aktuell belegter Zustand

| Bereich | Nachweis | Grenze |
|---|---|---|
| Serverkonfiguration | Aktueller SMB-Archivrestore, 38 Pfade; verification/SMB_CONFIG_REFRESH_2026-09-21.md | Kein vollständiges Systemabbild |
| PostgreSQL physisch | Kalte Sicherung auf SMB, Repository-/Restore-/Prüfsummenprüfung bestanden; verification/POSTGRES_SMB_RESTORE_2026-09-21.md | Benötigt passenden PostgreSQL16-Wiederaufbau |
| PostgreSQL logisch | Getrennte Kopie gestartet, Dump/Restore geprüft: 1 Nichttemplate-DB, 15 Rollen, Globals; verification/POSTGRES_LOGICAL_RESTORE_2026-09-21.md | Keine Anwendung und kein vollständiger Server-Recoveryboot geprüft |
| Lokaler Arbeitsstand | Snapshot D:/Aurelia/_Snapshots/Hermes_Aurelia_2026-09-21_13-08-04 vorhanden; historisch 3285 Dateien/152390401 Bytes verifiziert | Kein Serverabbild; aktuelle Änderungen nach Snapshotzeit fehlen. Kein erneuter vollständiger Hashcheck in dieser Prüfung |
| Unabhängiger Rettungsweg | Provideranfrage vorbereitet | Rescue/ISO-Verfügbarkeit und konkrete Bedienung noch unbestätigt |

## Automatisches Serverbackup: frische Beobachtung

- `aurelia-backup-files.timer`: disabled/inactive, kein nächster Lauf. Zeitplan täglich 03:30 Uhr, RandomizedDelaySec=15min, Persistent=true. Serverzeitzone Europe/Berlin. Daraus folgt kein belegtes RPO.
- Service startet `/usr/local/sbin/aurelia-backup-files` und beschreibt ausdrücklich den Ausschluss laufender Datenbanken. Repository-/Passwortdateien sind Vorbedingungen, das Passwort wird über LoadCredential übergeben; Inhalte nicht gelesen.
- `OnFailure` ist leer. Das belegt fehlende Fehlerweiterleitung in dieser Unit, nicht das Fehlen sämtlicher möglicher externer Überwachung.
- Backup-Programm: root, Modus750, 484 Bytes, für den SSH-Benutzer nicht lesbar. Tatsächliche Quellen, Ausschlüsse, Konsistenzprüfungen, Repositoryverwendung und Löschoptionen sind daher noch nicht frisch anhand des Programms geprüft.
- Keine fehlgeschlagenen systemd-Units bei dieser Abfrage. `Result=success` allein belegt keinen neuen Backup-Lauf.

## Nächste Arbeiten in sinnvoller Reihenfolge

| Schritt | Konkreter Abschlussnachweis | Abhängigkeit |
|---|---|---|
| 1. Automatisches Backup prüfen | Privilegierte, bereinigte Prüfung von Programm und Quellenliste; keine Zugangsdaten veröffentlichen. Abgleich mit tatsächlich restaurierten Daten | Root-KVM verfügbar, SSH ohne pauschale sudo-Erweiterung |
| 2. Betriebsziele festlegen | Betreiber bestätigt maximalen Datenverlust (RPO), Wiederanlaufziel (RTO), Aufbewahrung und Empfänger für Fehler | Noch keine numerischen Ziele als vereinbart behandeln |
| 3. Backup-Ablauf passend machen | Konfiguration/Dateien und Datenbankkonsistenz explizit abdecken; Erfolg, Ausfall und ausbleibender Lauf erkennbar | Geprüfter Programmumfang und Betriebsziele |
| 4. Automatischen Ablauf abnehmen | Ein echter Lauf mit zugehörigem Restorebeleg; Fehlererkennung und Zustellung gesondert prüfen | Keine externe Testnachricht ohne Sendeauftrag |
| 5. Unabhängige Recovery prüfen | Bestätigter Rescue-/ISO-Zugang, Rückkehrpfad und kontrollierte Wiederherstellung auf separatem Ziel | Providerantwort; kein destruktiver Ausfalltest improvisieren |
| 6. G0 zusammenführen | Recovery, Backup-Betrieb, Hardware-/Sicherheitsabweichungen und Belastungsnachweise gemeinsam bewerten | Keine Modulfreigabe allein aus grünen Backup-Tests |

Bis zur Festlegung der Aufbewahrung keine automatische Löschung/Prune. Ein täglicher Zeitplan allein garantiert weder höchstens24h Datenverlust noch eine Wiederherstellungsdauer. Bestehende erfolgreiche Tests nicht grundlos wiederholen. Produktrepositories und spätere Modul-/Tenantdaten bleiben eigene Sicherungsumfänge.
