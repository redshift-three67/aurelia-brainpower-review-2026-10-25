# L-G2 – dauerhafte Zugänge: freigegeben und abgenommen

Stand: 16.10.2026. Die drei Dauerzugänge sind abgenommen. Die ursprünglich bis heute Abend befristeten Bootstrap-Freischaltungen wurden gezielt abgelöst; die neuen Schlüssel haben kein Ablaufdatum und bleiben einzeln widerrufbar.

## Vorgeschlagene Rollen

| Zugang | Umfang | Laufzeit |
|---|---|---|
| Aurelia-Projekt: aurelia-ops | Eigener Benutzer und eigene Projektdateien, kein sudo und keine Docker-Gruppe | Dauerhaft bis zum gezielten Widerruf |
| Website-Projekt: rauch-web-test | Eigener Benutzer/Schlüssel/Testbereich, kleineres Ressourcenbudget, keine Aurelia-Datei- oder Geheimnisfreigabe | Dauerhaft bis zum gezielten Widerruf |
| Administration | Separater Wartungsschlüssel mit Rootrechten; nur zur Serververwaltung, nicht in Projekt-/Cloud-Jobs oder Anwendungscontainern | Freigegeben: dauerhaft bis zum Widerruf |

Dauerhaft bedeutet: Der Server weist den Schlüssel nicht wegen eines eingetragenen Ablaufdatums zurück. Schlüssel bleiben einzeln sperrbar und austauschbar. Passwortlogin per SSH bleibt aus; Provider-Konsole bleibt erhalten. Die bestehenden Bootstrap-Schlüssel werden erst nach erfolgreichen neuen, getrennten Logins abgelöst. Kein heimliches Verlängern der heutigen Freischaltungen.

## Geplanter Ablauf nach Freigabe

1. Eigene Schlüssel/strikte SSH-Profile je Rolle lokal außerhalb des Repositorys vorbereiten; private Dateien nur Betreiber/SYSTEM zugänglich. Keine privaten Schlüssel in Chat, Projektarchiv oder Cloud.
2. Serverseitig SSH-/Kontenkonfiguration sichern; vorhandene gültige Anmeldung erhalten.
3. Dauerhaften Administrationsschlüssel getrennt freischalten und neuen IPv4-Login prüfen. Danach Bootstrap-Freischaltung gezielt ablösen; Root-Passwortlogin bleibt gesperrt.
4. Aurelia-Projektzugang mit dauerhafter, widerrufbarer Freischaltung separat testen. Keine neuen privilegierten Gruppen.
5. Website-Benutzer ohne Adminrechte anlegen und eigenen Zugang prüfen. Dateirechte/Secrets trennen. Port-/Ressourcenbudget erst nach bekannter Website-Laufzeit festlegen.
6. Preview-Tunnel später nur zu ausdrücklich festgelegten lokalen Diensten erlauben; derzeitige restrict-Keys erlauben sie noch nicht. Gemeinsames Loopback ist keine vollständige Projektisolation; Testdienste benötigen eigene Zugriffskontrollen. Datenbank-/Cloud-/Produktgates bleiben bestehen.

## Betreiberfreigabe und Abnahme

Der Betreiber hat die drei vorgeschlagenen getrennten Dauerzugänge einschließlich des separaten Root-Wartungsschlüssels am 16.10.2026 ausdrücklich mit „Ja bitte, richte diese ein.“ freigegeben. Die Zugangseinrichtung aus den Schritten 1 bis 5 ist abgeschlossen; Ressourcenbudgets und Preview-Tunnel aus den Schritten 5/6 bleiben wie vorgesehen spätere Teststack-Arbeit.

Elf Linux-Mocktests erfolgreich. Neue IPv4-Logins als root, aurelia-ops (1000) und rauch-web-test (1001) vor und nach exakter Entfernung der alten zwei Bootstrap-Schlüssel erfolgreich. Kein sudo für beide Projektkonten; gegenseitige Home-Leserechte verweigert; neue Schlüssel nur restrict ohne expiry-time. Alle 16 bestehenden Sicherheitskonfigurationen unverändert und Dienste aktiv. UID-/Profilhash-/Dateidrift-/Retirement-Gates geprüft, unabhängiger Astra/medium-Review ohne verbleibende P1-Befunde. Luna/max für Werkzeug und Tests genutzt. Private Schlüssel bleiben ausschließlich lokal außerhalb des Projekts, ACL Betreiber/SYSTEM geprüft.

Dokumentation: `docs/LG2_PROJEKTZUGAENGE.md`. Nachweis: `checkpoints/Aurelia-LG2-Dauerzugaenge-20261016T061825Z`. Vorher-Schlüsseldateien rootgeschützt unter `/root/aurelia-durable-access-20261016T061825Z/backups`; aktueller 19-Dateien-Sicherungspunkt `/root/aurelia-durable-checkpoint-20261016T061825Z`. Kein vollständiges Server-/externes Backup. Keine Paket-, Netzwerk-, Docker- oder Produktänderung.

## Verifizierter Wiederaufnahmestand

Frischer IPv4-Rootlogin am 16.10.2026 um 08:10 Uhr Europe/Berlin erfolgreich. Sicherheitsvorgang committed, Rückfalltimer inactive/dead, SSH/Socket/Fail2ban aktiv, keine failed Units. IPv6 weiterhin im Betriebssystem vorhanden. Es wurden bei dieser Wiederaufnahme nur Metadaten gelesen; keine Zugangs-, Netzwerk-, Paket- oder Produktänderung.
