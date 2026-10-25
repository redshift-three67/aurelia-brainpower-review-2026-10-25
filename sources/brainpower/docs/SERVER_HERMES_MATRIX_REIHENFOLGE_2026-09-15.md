# Server, Hermes und erweiterbare Aurelia-Matrix

## Betreiberpriorität vom 15.09.2026

1. Serveradministration und isolierte Ausführungsbasis präzise vorbereiten.
2. Danach den lokalen Hermes-/Governor-Reststand bis zur belastbaren Abnahme vervollständigen.
3. Erst anschließend Modulverifikation und vorbereitete Integrationen durchführen.
4. Drei bis vier weitere Module müssen später regelgerecht in die Aurelia-Produktmatrix aufgenommen und integriert werden können.
5. Aurelia-Frontend-Webframework und Headless-CMS in der administrativen Verwaltung sind offene Architekturentscheidungen; keine Auswahl oder Installation aus diesem Auftrag ableiten.

G2-Ziel wurde geliefert: `//fra1-nas-backup1.ip-projects.de/213487`. DNS und TCP 445 sind vom Server erreichbar; Anmeldung, Einbindung und Restore sind noch nicht geprüft. Details: [SMB-Einbindung](G2_SMB_EINBINDUNG_2026-09-15.md). Die öffentliche Client-IP kann wechseln: keine feste IP als dauerhafte Managementidentität.

## Servervorbereitung und Grenzen

Ubuntu 24.04.5, Python 3.12, minimale GNOME-Pakete, PostgreSQL 16 mit geprüften Checksums, Dev-/Diensttrennung und leere Produkt-Buildpfade sind eingerichtet. Produktcode, Datenbankmigrationen, CUDA und reale Klientendaten bleiben getrennt. GNOME-Eingabe wurde durch libinput repariert und die Anmeldung vom Betreiber bestätigt. Automatischer Suspend wurde unterbunden. ASPEED übernimmt die Anzeige; NVIDIA bleibt der Compute-Gruppe vorbehalten. Rechte nach Neustart geprüft; längerer Desktop-Leerlauftest und CUDA-Workloadtest bleiben offen.

WireGuard ist eingerichtet: Server wg-admin 10.77.0.1, Windows-Client 10.77.0.2, UDP 51820, Clientroute ausschließlich 10.77.0.1/32 und Keepalive 25 Sekunden. Windows-Tunneldienst läuft; SSH durch den Tunnel wurde erfolgreich geprüft. Wiederverbindung nach Router-/IP-Wechsel bleibt offen. Gemäß ausdrücklicher Betreiberfreigabe bleiben öffentliches SSH mit Schlüssel und WireGuard IP-unabhängig erreichbar; andere neue Eingänge werden gesperrt. Keine automatische Beschränkung von SSH auf VPN.

G2-Dateisicherung: Restic, systemd-Service und deaktivierter Timer vorbereitet. Fehlende Repository-/Passwortdateien verhindern Ausführung (negativ getestet). Kein Repository initialisiert, keine Übertragung oder Prune-Regel aktiviert. Pfade /etc, /home/aurelia-dev, /srv/build, /srv/aurelia; Cache-/venv-Verzeichnisse und Backup-Passwort ausgeschlossen. PostgreSQL-Livedaten sind ausdrücklich nicht Bestandteil dieser Dateisicherung; konsistenter Dump-/Restorepfad ist vor Datenbanknutzung zusätzlich zu vervollständigen. RPO/RTO, Aufbewahrung und tatsächliches G2-Protokoll erst nach Lieferung verifizieren.

## Hermes-/Governor-Abschlusskriterien

Zusätzlicher Betreiberprüfpunkt: [Token-Effizienz ohne Qualitätsverlust](HERMES_TOKENEFFIZIENZ_2026-09-15.md). Vorhandene Begrenzungen/Usage-Erfassung von noch ausstehender Relevanzauswahl, durchgängiger Messung und Qualitätsabnahme unterscheiden.

Maßgeblicher Iststand: docs/RESTARBEITEN_0_5.md. Der bestehende Hermes-Reviewer ist zero-tool; Rohantworten bleiben Daten. Ausführungsadapter dürfen diese Grenze nicht unbemerkt aufheben.

- Aktuelle Aufnahmebestätigungen und Quellenbindung separat vom Implementierungsauftrag behandeln.
- Projektadapter mit fester Identität, erlaubten Aktionen, Betriebssystem, Arbeitsverzeichnis, Datenklasse und Rechteprofil.
- Start/Stop, interne Ports, Timeouts, Ressourcenbudgets, Abbruch und Wiederanlauf je Adapter nachweisen.
- Tests an aktuelle Quellenhashes binden; Ergebnis und Freigabe unterscheiden; Drift invalidiert die Folgeverwendung.
- Reparatur nur begrenzt, überprüfbar und rücknehmbar; kein ungeprüftes Ausführen von Modellantworten.
- Abhängige Sequenzen benötigen eine ausdrückliche aktuelle Auswahl und stoppen bei Fehler, Drift oder geändertem Scope.
- Mehrgruppen-/Vault-Abnahme und vollständiges Windows-Erstsetup gemäß vorhandener Reihenfolge abschließen.

## Aufnahme weiterer drei bis vier Module

Vorhanden sind Registrierung, Gruppenzuordnung und Aufnahmeentwürfe (siehe governor_workbench/registry.py, scopes.py und server.py). /api/projects ist nur eine ältere Planungsnotiz; reale Registrierung erfolgt über /api/registry/projects. Keine Aussage, dass Registrierung bereits eine funktionsfähige Aurelia-Integration erzeugt.

Für die spätere Abnahme ist eine isolierte synthetische Gruppe mit neun Einträgen (fünf plus vier) vorzusehen, ohne echte bestehende Gruppen zu verändern. Prüfen:

1. Eindeutige stabile Modul-ID, Quellenpfad und Hash; keine Verwechslung bei gleichen Anzeigenamen.
2. Vertrag, Version/ABI, Abhängigkeiten und Datenklasse; fehlende oder zyklische Abhängigkeiten ablehnen.
3. Unbestätigte Aufnahme kann weder Strategie übernehmen noch ausführen.
4. Gruppenänderung invalidiert betroffene Plan-/Ausführungsnachweise, lässt unabhängige Gruppen unberührt.
5. Isolierte Installation, Start/Stop und Rücknahme eines einzelnen Moduls ohne Änderung anderer Module.
6. API-/Event-/Auth-/Tenant-Verträge und Migrationen gegen Aurelia separat testen.
7. Verwaltungsoberfläche zeigt Berechtigungen, Zustand und Version; CMS-Inhalte erhalten keine Ausführungsberechtigung.
8. Neue Module erweitern nicht automatisch Modellversand, Geheimniszugriff, Hardwarefreigaben oder Produktgates.

Diese Kriterien sind dokumentierte Anforderungen, noch keine ausgeführten neun-Modul-Tests oder neue Modulaufnahmen.
