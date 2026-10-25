# T3 – lesende Ubuntu-Vorprüfung

20.09.2026, bestehender SSH-Schlüsselzugang über 10.77.0.1, Benutzer klaus999 (UID 1000), strikte bekannte Hostidentität. Keine Serverdateien geschrieben, Dienste gestartet, Pakete installiert oder Einstellungen verändert.

| Beobachtung | Ergebnis | Bedeutung |
|---|---|---|
| Kernel | 6.8.0-139-generic | Laufende Plattform; kein Neustart erforderlich |
| Python | 3.12.3 | Standardbibliotheks-Testpaket grundsätzlich möglich |
| systemd | 255 / 255.4-1ubuntu8.17 | Kandidat für eigenen begrenzten Prozesskontext |
| cgroup | cgroup2fs; cpu, memory, pids vorhanden | Harte Limits technisch vorbereitbar, Durchsetzung noch ungetestet |
| Benutzerdelegation | Delegate=yes; cpu memory pids | Verfügbar, aber keine dauerhafte Testsitzung daraus ableiten |
| Benutzerverwaltung | degraded; Linger=no | GNOME UsbProtection fehlgeschlagen; T3 nicht an Desktop koppeln |
| Systemfehler | `systemctl --failed` ohne Einträge | Momentaufnahme, kein vollständiger Gesundheitsnachweis |
| SSH | active | Lesender Zugang funktioniert |
| WireGuard | wg-quick@wg-admin aktiv, wg-admin mit 10.77.0.1/32 | Erste Abfrage wg0 war falscher Einheitenname, kein WireGuard-Ausfall |
| Speicher /var/tmp | 105 GiB frei | Platz vorhanden; keine Diskquota-/Dauerbetriebszusage |
| TLS / SQLite | OpenSSL 3.0.13; SQLite 3.45.1 | Werkzeuge vorhanden; Linux-Transporttests bleiben auszuführen |
| /var/tmp/aurelia-t3 | Verzeichnisprüfung negativ | Testbereich noch nicht eingerichtet |

Erster gebündelter SSH-Aufruf endete mit Code 1 wegen der abschließenden negativen Verzeichnisprüfung. Die ausgegebenen Einzelergebnisse sind getrennt ausgewertet; der Aufruf wird nicht als insgesamt erfolgreicher Test geführt. Eine zweite lesende Abfrage klärte Benutzerfehler und den tatsächlichen WireGuard-Namen.

T3-Ausführung bleibt ungetestet. Kein sudo-/Rootrecht für neue Dienstaktionen nachgewiesen; ein geöffnetes Root-KVM-Terminal ist kein SSH-Rootzugang. Grenzen und Abnahmekriterien stehen im T3-Vorbereitungsplan. Der GNOME-Befund wurde lediglich dokumentiert, nicht repariert oder als Sicherheitsentwarnung bewertet.
