# Automatisches Backup: Quellen geklärt, Zielkonfiguration offen

Betreiber führte bpbd21 aus. Berichtzeitpunkt 22.09.2026 16:08:58 UTC. Per SSH vollständig gelesen, lokal unter artifacts/backup-detail21-report.json gesichert. SHA256 lokal/servergleich: `0b6066bb7c7deed3d4dedcd2e367b629fcd3bcb039e407a81653f70d876a96a5`.

## Ergebnis

Status `inspection_incomplete`, Fehlerklasse `FileNotFoundError`. Programmhash und beide Listen stimmen mit der vorherigen Strukturprüfung überein. Keine Sicherung gestartet und keine Konfiguration geändert. Frische SSH-Prüfung bestätigt PostgreSQL16/main down und Backup-Timer disabled/inactive.

| Bereich | Sichtbarer Inhalt |
|---|---|
| Quellen | /etc; /home/aurelia-dev; /srv/build; /srv/aurelia |
| Ausschlüsse | **/node_modules; **/.venv; **/__pycache__; /home/aurelia-dev/venvs; /etc/aurelia-backup/password |
| Mountbedingungen im Programm | mountpoint -q für /home, /srv/build, /srv/aurelia |
| Aufruf | restic backup mit Repositorydatei, Passwortdatei, Cacheverzeichnis und beiden Listen |
| Repository | Keine Beobachtung exportiert; Fehler beim anschließenden Lesen/Verarbeiten von /etc/aurelia-backup/repository |
| Mountinventar | Wegen vorherigen Abbruchs nicht erreicht |

Die Reihenfolge des Helfers lokal geprüft: Nach den beiden erfolgreichen Listen folgt das Lesen der Repositorydatei, vor dem Export des Repositorybefunds und vor findmnt. FileNotFoundError spricht hier für die fehlende Repositorydatei; separate privilegierte Existenzprüfung noch nicht erfolgt. Ein erfolgreiches Ende der Konsolenausgabe war keine vollständige Abnahme: entscheidend ist der JSON-Status.

## Bedeutung und nächste zusammenhängende Arbeit

1. Zielkonfiguration für diesen automatischen Dienst ist nicht belegt. Erfolgreiche separate SMB-Testrepositories ersetzen diese Konfiguration nicht. Vor Einrichtung Zielpfad und erwarteten SMB-Mount gemeinsam validieren; lokale Ersatzablage bei fehlendem NAS verhindern.
2. PostgreSQL16/main unter /var/lib/postgresql liegt außerhalb der vier Quellen. Vorhandene physische/logische Restorebelege bleiben gültig; dieser Dateibackup-Aufruf stellt noch keine automatische DB-Sicherung dar. Für laufenden PostgreSQL ist ein konsistenter eigener Sicherungsweg erforderlich, kein bloßes Hinzufügen des Live-Datenverzeichnisses.
3. /srv/aurelia/backup-staging ist nicht ausdrücklich ausgeschlossen. Vor automatischem Betrieb klären, welche dort abgelegten Archive absichtlich mitgesichert werden. Die Liste enthält keine ausdrücklichen Ausschlüsse für lokale Labor-/Testbestände innerhalb der Quellbäume.
4. Kennwortübergabe und weitere ausgeblendete Vorbedingungen sind noch nicht vollständig semantisch geprüft. Keine automatische Freigabe aus der Strukturansicht.
5. Nächsten privilegierten Schritt als Paket aus konkreter Ziel-/Mountprüfung und Konsistenzprüfung vorbereiten. bpbd21 nicht erneut starten. Timer erst nach technischer Abnahme und der vom Betreiber vertagten Besprechung von RPO/RTO aktivieren; Provider-Recovery weiterhin separat offen.
