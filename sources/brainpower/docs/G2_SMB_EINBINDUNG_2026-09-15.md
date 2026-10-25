# G2-SMB: geprüfter Stand und nächste Einrichtung

Neuster Stand 18.09.2026: Synthetischer NAS-Backup-/Restoretest bestanden und per SSH bestätigt; siehe `verification/SMB_RESTORE_2026-09-18.md`. Einmalige Sicherung echter Serverkonfigurationen vorbereitet, Root-Ausführung noch offen. Keine Timeraktivierung. Nachfolgende Zwischenstände chronologisch historisch lesen.

Aktualisierung 18.09.2026: CIFS vorhanden; Anmeldung mit k213487 und RO-Mount erfolgreich, SMB 3.1.1 mit Verschlüsselung laut Root-Prüfbericht `/var/tmp/aurelia-smb-probe-t_j8mdke/result.json`. Isolierter NAS-Backup-/Restoretest vorbereitet, aber noch nicht ausgeführt. Lokaler Restic-Selbsttest bestanden; Details und nächster Root-KVM-Befehl in WIEDERAUFNAHME.md. Die folgenden Angaben vom 15.09. sind historisch.

Stand 15.09.2026. Ziel vom Betreiber: `//fra1-nas-backup1.ip-projects.de/213487`.

## Nachgewiesen

- DNS auf dem Ubuntu-Server liefert 103.241.50.253; TCP 445 ist erreichbar. Dies bestätigt weder Login noch Freigaberechte.
- `mount.cifs` fehlt noch; Restic ist vorhanden.
- WireGuard-Dienste auf Server und Windows laufen; SSH zu 10.77.0.1 durch den Tunnel funktioniert.
- Es wurde noch kein SMB-Passwort eingegeben, keine Freigabe eingebunden und kein Backup übertragen.

## Vorgesehene Einrichtung

1. `cifs-utils` installieren. Benutzername und gegebenenfalls Domain aus den Providerangaben übernehmen; Sharename ist nicht automatisch Benutzername.
2. Zugangsdaten ausschließlich verdeckt im Serverterminal erfassen und in einer root-eigenen Datei mit Modus 0600 unter einem Verzeichnis mit Modus 0700 ablegen. Keine Passwörter in Chat, Kommandozeile, Repository oder Protokolle aufnehmen.
3. Zunächst nur lesend unter `/mnt/aurelia-g2` testen: SMB 3.1.1 und `seal`, dazu `nosuid,nodev,noexec`, Root-Zugriff. Bei nicht unterstützter Version Ursache prüfen; kein stiller Rückfall auf unverschlüsselte Verbindung.
4. Nach erfolgreicher Anmeldung Freigabe, tatsächliche Verschlüsselung, Kapazität und Rechte prüfen. Danach ausschließlich einen neuen, eindeutig benannten Testbereich beschreiben; vorhandene Providerdaten nicht verändern.
5. Eigenes Restic-Repository mit separatem sicher verwahrtem Repositorypasswort vorbereiten. Kleine synthetische Sicherung, `check`, Restore und Hashvergleich durchführen, bevor echte Konfigurationen gesichert werden.
6. Backupdienst muss sowohl Mount-Abhängigkeit als auch erwartete CIFS-Quelle prüfen. Bei fehlendem NAS abbrechen, damit keine vermeintlichen Backups im lokalen Verzeichnis entstehen. NAS-Ausfall darf den Serverstart nicht blockieren.
7. Erst nach Prüfung Timer aktivieren. Aufbewahrung, RPO/RTO und Benachrichtigungen noch festlegen; kein ungeprüftes Prune. PostgreSQL benötigt zusätzlich einen konsistenten Dump-/Restorepfad; keine Sicherung laufender Datenbankdateien als Ersatz.

SMB benötigt ausgehend TCP 445. Eine zusätzliche eingehende SMB-Firewallfreigabe ist nicht erforderlich. Die Freigabe dient als Backupziel, nicht als produktives Datenbankverzeichnis.

## Quellen und technische Grenze

Der [Provider beschreibt SMBv3 mit Transportverschlüsselung](https://www.ip-projects.de/de/server-feature/server-backup). Die tatsächliche Sitzung muss dies noch nachweisen. [mount.cifs](https://www.man7.org/linux/man-pages/man8/mount.cifs.8.html) dokumentiert `seal` und geschützte Credentials-Dateien.

[Restic weist auf CIFS-Kompatibilitätsprobleme unter Linux hin](https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html) und nennt `GODEBUG=asyncpreemptoff=1` als Workaround. Dies bei der Diensteinrichtung berücksichtigen und mit Backup/Restore testen; vorhandener Kernel 6.8 allein ist kein Abnahmenachweis. Ein vom Provider tatsächlich angebotener alternativer Backendzugang kann gesondert geprüft werden.

Nach Abschluss der Serverprüfungen folgen Hermes-/Governor-Restarbeiten einschließlich Token-Effizienz und Erweiterbarkeit. Modulverifikation folgt erst danach. Frontend-/CMS-Auswahl bleibt offen.
