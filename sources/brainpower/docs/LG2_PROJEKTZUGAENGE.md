# LG2: dauerhafte, getrennte SSH-Zugänge

Abgenommen am 16.10.2026 auf `193.142.40.36` / `vm2565`. Jeder Zugang verwendet einen eigenen ED25519-Schlüssel ohne Ablaufdatum und bleibt einzeln widerrufbar. Passwortanmeldung über SSH bleibt aus.

| Zweck | Serverkonto | SSH-Alias | Rechte |
|---|---|---|---|
| Aurelia-Projekt | aurelia-ops, UID/GID 1000 | aurelia-lg2-project | Eigene Projektdateien; kein sudo, keine Docker-Gruppe |
| Website-Projekt rauch-heilpraktiker.de | rauch-web-test, UID/GID 1001 | rauch-lg2-test | Eigener Testbereich; kein sudo, keine Docker-Gruppe |
| Serverwartung | root, UID/GID 0 | aurelia-lg2-admin | Administration; ausschließlich für Wartung |

Die lokalen Profile liegen unter `C:\Users\Hubert111\.ssh\aurelia-lg2-permanent-20261016T061825Z`, jeweils in `ops`, `website` und `admin` als `ssh_config`. Private Schlüssel bleiben dort; keine Übernahme in Repository, Projektarchive, Cloud-Jobs oder Container. Dateirechte wurden ausschließlich für das Betreiberkonto und SYSTEM geprüft. Diese Windows-Rechte unterscheiden keine Anwendungen, die unter demselben Betreiberkonto laufen.

Aurelia-Verbindungsprobe:

```powershell
ssh -4 -F "C:\Users\Hubert111\.ssh\aurelia-lg2-permanent-20261016T061825Z\ops\ssh_config" aurelia-lg2-project "id -un"
```

Für das andere Codex-Projekt ausschließlich die Anleitung [LG2_WEB_TESTZUGANG.md](LG2_WEB_TESTZUGANG.md) verwenden. Der administrative Schlüssel ist kein Projektzugang. Es wurde keine Nachricht an ein anderes Codex-Projekt gesendet.

Alle Profile erzwingen IPv4, den separat bestätigten Hostschlüssel, die jeweilige Identität und öffentliche Schlüsselauthentifizierung. Keine Agentweiterleitung oder Wiederverwendung bestehender SSH-Verbindungen. Seit der Testbasisabnahme erlauben die Projektschlüssel ausschließlich lokale TCP-Weiterleitung zum eigenen Ziel (Aurelia127.0.0.1:18112, Website127.0.0.1:18113); PTY, Reverse-/Unix-Socket-Weiterleitungen und fremde Ziele bleiben gesperrt. Rootschlüssel bleibt restrict. Für einen Vorschautunnel explizit ClearAllForwardings=no und ExitOnForwardFailure=yes verwenden; ursprüngliche Profil-Dateien bleiben unverändert.

Beide Projektverzeichnisse sind mit Modus 0700 getrennt; gegenseitiger Dateizugriff und sudo sind geprüft verweigert. Gemeinsames Betriebssystem und Loopback sind keine vollständige Anwendungs-/Mandantenisolation. Containergrenzen, Dienstanmeldungen und Ressourcenbudgets gehören zum folgenden Teststack-Aufbau.

Die zwei befristeten Bootstrap-Schlüssel wurden erst nach drei erfolgreichen neuen Logins exakt entfernt. Danach wurden alle drei Dauerzugänge erneut erfolgreich angemeldet. Elf Linux-Mocktests bestanden; Luna/max hat das begrenzte Serverwerkzeug erstellt, Astra/medium die sicherheitsrelevanten Änderungen unabhängig geprüft. Gefundene Test-/Abnahmefehler sind korrigiert und nachgeprüft.

Nachweise: `checkpoints/Aurelia-LG2-Dauerzugaenge-20261016T061825Z`. Serverseitige Original-Schlüsseldateien: `/root/aurelia-durable-access-20261016T061825Z/backups`. Aktueller begrenzter Konfigurationssicherungspunkt: `/root/aurelia-durable-checkpoint-20261016T061825Z` (19 Dateien, SHA-256-geprüft). Kein vollständiges Serverabbild oder externes Wiederherstellungsbackup. Alte Schlüssel nicht aus Sicherungen automatisch erneut freischalten.

Aktueller Anschlussstand: [Testbasisabnahme](LG2_TESTBASIS_ABNAHME_2026-10-16.md). IPv4-OS-/SSH-Socketabschluss und rootloser Container-/Proxyaufbau erfolgt, noch keine Produktübertragung/DNS-/Hostingänderung. Quellen-/Lizenz-/Cloudgates für den RadiWorks-Piloten bleiben separat.
