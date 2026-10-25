# L-G2-Zugangssicherung - Implementierungsplan

> Agentische Ausfuehrung: bestehende Chatfreigabe "ok wir gehen weiter" gilt fuer den zuvor beschriebenen Sicherheitsblock. Luna/max bearbeitet ausschliesslich Controller+Tests; leitender Agent integriert; Astra/medium prueft unabhaengig. Kein weiterer Freigabezyklus fuer bereits genehmigten Umfang. Produktquellen, Cloud-/Integrationsgates bleiben getrennt.

**Ziel:** Separater nicht privilegierter Schluesselzugang und SSH-/IPv4-Grundsicherung mit gesperrtem IPv6-Zugang des neuen Testservers ohne Aussperren.
**Zielbindung:** ausschliesslich vm2565, 193.142.40.36, Ubuntu24.04LTS, gepinnter ED25519-Fingerprint aus docs/SERVER_AKTUELL.md. Alter LUKS-Root und Windows-Liveinstanzen ausgeschlossen.
**Werkzeuge:** SSH vom Windows-Steuerungsrechner; stdlib-Python-Steuerung und reale Linux-Pruefungen auf dem Testserver. Keine lokalen Produktbuilds.

## Grenzen

- Root-Bootstrap bleibt temporaer key-only; nicht Root komplett sperren, bevor ein gepruefter privilegierter Ersatz existiert. Neuer aurelia-ops hat KEINE sudo-/Dockerrechte.
- Beide Schluessel behalten den bestehenden Ablauf16.10.2026 21:08:35UTC (=23:08:35CEST). Keine stillschweigende Verlaengerung oder dauerhafte Privilegfreigabe. Ablauf beendet keine bestehenden Sitzungen.
- Root-Passwort bleibt fuer Provider-VNC unveraendert. SSH-Passwortanmeldung wird erst nach neuem Keylogin deaktiviert. Provider-Konsole verfuegbar halten.
- Betreiberkorrektur: ausschliesslich IPv4 verwenden. UFW22tcp nur fuerIPv4 offen; IPv6 eingehend nicht freigeben. UFW-IPV6=yes dient nur der Filterung vorhandener OS-IPv6-Schnittstellen und ist keine Nutzungserlaubnis. Sonst eingehend verweigern, ausgehend erlauben; Website-/Anwendungsnetze spaeter explizit IPv4. Keine neue globale Web-/DB-Freigabe. Docker kann UFW-Regeln umgehen: vor Dockerbetrieb gesonderte Bindungs-/Filterpruefung, kein aktueller Nachweis dafuer.
- Erst Konfigbackup und aktiver Rueckfalltimer, dann Mutation. Timer schützt bei Verbindungsverlust, ist aber kein rebootfester Restore-/Backupnachweis. Keine Dienstneustarts, wenn Reload genuegt.
- Keine privaten Host-/Clientschluessel, Schattenpasswoerter, Klienten oder Modulquellen in Logs/Projektbackups. Konfigkopien aufServer rootgeschuetzt; lokale Belege nur technische Metadaten/Hashes.

## Schritte und Pruefungen

- [x] Linux-ReadOnly-Voraussetzungen: sshd -t, Include-Reihenfolge, Dienstreload, UFW-IPv6, Konfliktfreiheit aurelia-ops. User/Gruppe fehlen, sshd -t erfolgreich, CanReload=yes.
- [x] Controller/gezielte Logiktests (Linux-Mocks32/32, echter Systemabgleich noch separat): tools/server/lg2_access_control.py, tests/test_lg2_access_control.py. Schuetzen gegen falschenHost, Symlinks, bestehendenUser/Home, Quelldrift und Timer/Commit/Rollback-Rennen. Tests mit isolierten temporaeren Linux-Dateien/Mock-Subprozessen; keine realen Konfigurationen in Unit-Tests.
- [x] Eigenen Clientkey ausserhalbProjekt vor Erzeugung ACL-Benutzer/SYSTEM beschraenken, separate known_hosts/ssh_config strikt pinnen, ssh -G und public/private Paar pruefen. Keine globalenSSH-Dateien aendern.
- [x] Controllerquelle unabhaengig reviewen, Syntax und gezielte Tests aufLinux ausfuehren; erst bei brauchbarer Evidenz weiter.
- [x] Prepare: rootgeschuetztes eindeutiges Arbeitsverzeichnis, exakte Konfig-Hashes/Metadaten sichern, Rueckfallscript validieren und15min-systemd-Timer vor Mutation pruefen.
- [x] Create-user: unprivilegierter aurelia-ops, Home/SSH-Rechte700/600, eigenes expiringPublicKey. BestehendeKonten/Home/Dateien nicht ueberschreiben. Frischen key-only SSH-Login separat beweisen, keine Adminrechte behaupten.
- [x] Apply unter State/Lock: Digestdrift ausschliessen, 00-aurelia-access.conf definieren; sshd -t und effektive Root-/Ops-Regeln pruefen. PermitRootLogin prohibit-password, PasswordAuthenticationno, KbdInteractiveAuthenticationno, Pubkeyyes; Agent/X11/Tunnelno, TCPForwardinglocal, GatewayPortsno, PermitUserEnvironmentno. UFWIPv6yes nur als Filter,22 ausschliesslich IPv4 erlauben, denyincoming/allowoutgoing, enable; sshreload. Bei Fehler Rueckfall, kein Nachfolgeaufbau.
- [x] Acceptance vorCommit: frische Root- undOps-Logins; echte UFW-/v4-/v6-Regeln, nur vorgesehene Listener, Zeit und ausstehenderTimer pruefen. FremdeProjekte/Dateien unveraendert. IPv6 darf nicht freigegeben sein. IPv4-Zugang frisch beweisen; Client hat keine IPv6-Route (WinError10051), daher externer IPv6-Sperrtest von hier nicht beweisbar. SSH-Socketaktivierung vor ListenAddress/AddressFamily-Aenderung pruefen. Kein blindes IPV6=no, das vorhandenes IPv6 ungefiltert lassen koennte.
- [x] Commit race-sicher: State/Hashes aktuell, Rueckfall nicht bereits gestartet/erfolgt, unter gemeinsamemLock zuerst atomaren Commitmarker schreiben, danach Timer stoppen/bestaetigen; spaeter gestarteterRollback liestCommit und veraendert nichts. Ein Fehler nachMarker gilt als unvollstaendige Timerbereinigung, nicht als fehlende Zugangssicherung.
- [x] Bestands-/Konfig-Nachweise mitSHA-Readback, SERVER_AKTUELL.md undWIEDERAUFNAHME.md inPlace fortschreiben. Sicherheitsblock ist kein Gesamtbackup/Produktionsfreigabe.

## Zusaetzliches Projekt rauch-heilpraktiker.de

Betreiberpraezisierung 16.10.2026: "rauch-heilpraktiker.de" ist der bestehende Codex-Projektname fuer Website-Review/Korrekturen. Benoetigt wird ein eigener paralleler SSH-Zugang zu DIESEM Ubuntu-Testserver, kein Zugang zur bestehenden Website. Getrennten unprivilegierten Projektbenutzer/Schluessel, eigene Testverzeichnisse, Secrets/Netze/Ports und ein kleineres Ressourcenbudget vorsehen. Keine Aurelia-Datenfreigabe oder gemeinsame privilegierte Docker-Gruppe. Nach Servergrundsicherung und Sichtung der Website-Testanforderungen bereitstellen; Website-DNS und bestehendes Hosting bleiben von diesem Zugang unberuehrt.

## Danach

APT-Index aktualisieren und Upgrades zunaechst simulieren/bewerten; kein26.04-Releaseupgrade. Paket-/Dockergrundlage und getrennteWebsite-Budgets nach diesenNachweisen. RadiWorks-Quellrechte/cleanprivateRepo/Cloudpilot, P3/P4/P5 undModul_Templates bleiben eigeneGates. DauerhafterWartungszugang/Rechte undProvider-Backup/Restore bleiben vor laengeremBetrieb zu klaeren.

## Tatsaechliche Abnahme16.10.2026

Linux34/34 und finalerAstra-Deltareview ohne neueBefunde. EchteSystemd-Rueckfalldatei vorApply mit15Originalhashes abgenommen; danachKonfigsicherung, Ops-User, frischeLogins, Apply, echteFilter-/Dienstpruefung undCommit erfolgreich.16Dateihashes passen, Rueckfalltimer gestoppt. IPv6 ist imOS noch vorhanden und nicht als vollstaendig deaktiviert abgenommen. ParallelerWebsite-Projektzugang bleibt eigener naechsterSchritt. Zusammenfassung checkpoints/Aurelia-LG2-Access-Abnahme-20261015T223058Z/SUMMARY.json.

## Pause 16.10.2026

**Pause auf Betreiberwunsch, 16.10.2026, 00:34 Uhr Europe/Berlin.** Zugangssicherung abgeschlossen und erneut gelesen: Transaktion committed, Rückfalltimer inactive/dead, keine laufende Zugangssicherungsaktion, SSH/SSH-Socket/Fail2ban aktiv, keine fehlgeschlagenen Dienste. 16 aktuelle Konfigdateien samt Vorgang auf dem Server rootgeschützt gesichert und byte-/hashgeprüft. Keine privaten Schlüssel oder Passwörter im lokalen Sicherungspunkt. Dies ist ein begrenzter Arbeits-/Konfigsicherungspunkt, kein vollständiges Serverabbild oder externes Restore-Backup.

**Exakte Wiederaufnahme:** Zuerst Datum und verbleibenden SSH-Zugang prüfen; beide Schlüssel laufen am 16.10.2026 um 23:08:35 Uhr Europe/Berlin ab. Nach Ablauf keine automatische Verlängerung oder erneute Nutzung alter Installationsbefehle. Danach IPv4-Bindungen/OS-Einstellungen erhaltend vervollständigen (IPv6 ist noch im OS konfiguriert), Paketstand prüfen/simulieren, getrennten Testzugang für das Codex-Projekt „rauch-heilpraktiker.de“ und kleinere Ressourcenlimits vorbereiten. Anschließend versionierte Testbasis; Quell-/Lizenz-/Cloud-/P3/P4/P5- und Modul_Templates-Gates bleiben erhalten. Keine neuen Paket-, Docker-, App- oder Produktänderungen während der Pause. Keine offene Reasoning-Umschaltung.

Sicherungspunkt: checkpoints/Aurelia-LG2-Pause-20261015T223404Z; Serverkonfiguration: /root/aurelia-pause-20261015T223404Z.


## Vorrang bei Wiederaufnahme16.10.2026

**Wiederaufnahme 16.10.2026, 08:10 Uhr Europe/Berlin:** Bestehender IPv4-Rootzugang frisch erfolgreich, Sicherheitsstand committed und Dienste aktiv; keine Serveränderung. Betreiber stellt klar, dass der Testserver langfristig benötigt wird. Nur die provisorischen Schlüssel laufen heute Abend ab. Dauerhafte getrennte Projektzugänge und ein eigener administrativer Wartungszugang sind jetzt vorrangig als konkrete Entscheidung vorbereitet: docs/superpowers/plans/2026-10-16-lg2-dauerzugaenge.md. Unbefristete Zugangsfreigabe einschließlich Root-Wartungsrechten noch nicht erteilt; keine automatische Verlängerung. IPv4-/Paket-/Teststackfolge bleibt danach erhalten.

