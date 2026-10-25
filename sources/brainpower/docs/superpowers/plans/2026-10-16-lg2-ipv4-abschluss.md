# LG2: IPv4-Abschluss und Paketvorschau

Reasoning: Medium. Betreiberfreigaben: Betrieb ohne IPv6; geplante Reihenfolge weiterführen. Keine neue Produkt-, Migrations- oder Releaseupgrade-Freigabe.

## Ziel und unveränderte Grenzen

193.142.40.36 / vm2565, Ubuntu 24.04: bestehende IPv4-Adresse, Gateway, DNS, drei getrennte Dauerzugänge und UFW-Regeln erhalten. IPv6-Adressen, Routen und lokale TCP-/UDP-Bindungen entfernen und die Konfiguration dauerhaft auf IPv4 setzen. Keine Schlüssel-/Passwortänderung, kein Neustart, keine Änderung des alten Rootservers oder der Windows-Dauerinstanzen.

## Konkreter Umfang

Nur sechs Konfigdateien: bestehendes `/etc/netplan/50-cloud-init.yaml`, neues cloud-init-Netzwerk-disable, eigenes sysctl-Fragment, eigenes sshd-Fragment, eigenes ssh.socket-Drop-in und bestehendes `/etc/default/chrony` (DAEMON_OPTS um -4 ergänzen). UFW bleibt einschließlich IPv6-Filterung unverändert. Cloud-init hat bereits eine Provider-Veraltungswarnung zur user-Zeichenkette; keine Ausführungsfehler, keine Änderung dieser Benutzervorgaben.

## Reihenfolge und Abnahme

1. Vorbefund und exakte Quellbytes/Metadaten sichern; einziges Netplan-Interface, IPv4-Daten, bestehende SSH-/Chrony-/Socketzustände und neu anzulegende Pfade bestätigen.
2. Begrenztes Python-Standardbibliothekswerkzeug mit Linux-Mocktests entwickeln: sichere Pfade, atomare Dateischritte, dauerhafter Status, Konflikterkennung, Rücknahme und Commit-Grenzen. Erst erwarteten roten Testlauf, danach grün belegen. Parent übernimmt reale Serveraktionen; Luna darf nur Werkzeug/Tests bearbeiten. Unabhängiger Astra-Review vor Aktivierung.
3. Kandidaten unter geschütztem Serverpfad mit `netplan generate --root-dir` prüfen. Originale einschließlich Metadaten und Laufzeitsysctls rootgeschützt sichern. Eigenständige Rücknahme-Datei/CLI prüfen und 15-Minuten-systemd-Rückfalltimer vor jeder Konfigänderung aktivieren.
4. Anwendung in eigener systemd-Serviceaktion: sechs Dateien schreiben, sshd-Syntax prüfen, Netplan und gezielte sysctls anwenden, systemd neu lesen, SSH-Master/Socket kontrolliert neu binden und Chrony neu starten. Bestehende SSH-Sitzung ist kein Abnahmenachweis. Gesamte Apply-Aktion als Type=exec mit RuntimeMaxSec=300 und TimeoutStopSec=10 begrenzen; zusätzlich alle Unterbefehle begrenzen. Der 15-Minuten-Rückfall darf nicht dauerhaft an einem gehaltenen Lock scheitern. Rückfalldienst als oneshot mit TimeoutStartSec=300 begrenzen (RuntimeMaxSec allein begrenzt keinen oneshot-Start).
5. Frische IPv4-Anmeldung aller drei Rollen; richtige Benutzer, Projekttrennung und fehlende sudo-Rechte bestätigen. Alle Interfaces ohne IPv6-Adressen/Routen, keine IPv6-TCP-/UDP-Listener, jedes relevante disable_ipv6=1, SSH ausschließlich IPv4, Chrony -4, DNS und Dienste gesund; UFW und Schlüsseldateien unverändert. Bei Fehler Rücknahme, keine falsche Erfolgsmeldung.
6. Erst bei passenden aktuellen Dateien/Laufzeit und frischen drei Loginbelegen nach applied_at committen, danach Rückfalltimer stoppen und dessen Inaktivität prüfen. Belege an Transaktion und Zielmanifest binden. Konflikte mit fremden Änderungen blockieren die automatische Überschreibung. Beim Rückfall ursprüngliche Sysctlwerte vor der ursprünglichen Netplan-Konfiguration aktivieren; rolled_back erst nach Datei- und Laufzeitprüfung. Vorher und nachher alle 19 bestätigten SSH-/Firewalldateien sowie aktive Firewallregeln vergleichen.
7. Nur IPv4-APT-Indexaktualisierung und Upgrade-Simulation. Paketanwendung, Docker-/Appaufbau und weitere Infrastruktur anhand des Ergebnisses getrennt behandeln; kein Upgrade auf Ubuntu 26.04.
8. Aktuellen Einstieg und begrenzten Sicherungspunkt aktualisieren. Kein Vollbackup-, Reboot-, Restore- oder Langzeitnachweis behaupten.

## Website-Projekt

Eigener SSH-Zugang ist geprüft; er wird durch Öffnen des anderen Codex-Projekts nicht automatisch übernommen. Anleitung `docs/LG2_WEB_TESTZUGANG.md` kann dort ausdrücklich referenziert werden. Ohne Betreiberauftrag keine Nachricht an den anderen Task. Ressourcenlimits, Test-Weblaufzeit und Previewzugang bleiben nachgelagerte Schritte.
