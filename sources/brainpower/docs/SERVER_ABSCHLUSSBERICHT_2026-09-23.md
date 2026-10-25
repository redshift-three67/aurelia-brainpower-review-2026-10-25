# Aurelia – Serverbericht und Übergang zu Hermes

Stand23.09.2026. **Begrenzte Belastungsprüfung bestanden; Bericht abgeschlossen. Übergangsbesprechung vor Hermes.**

## Auftrag und Grenze

Betreiber beauftragt gebündelte Belastungsprüfung, Bericht mit offenen Punkten, kurze Besprechung und anschließend Fortsetzung des lokalen Hermes-Projekts. Das erlaubt den Übergang zur Hermes-App-Arbeit, ist keine pauschale Produktions-/Modulfreigabe oder Behauptung einer vollständig erfüllten historischen Ground-Zero-Abnahme. Offene Serverpunkte bleiben gespeichert.

## Erreicht

| Bereich | Nachweis |
|---|---|
| Basis | Ubuntu, RAID1, LUKS2, beide EFI-Auswahlen bei vorhandenen beiden NVMe, Treiberbasis und SSH/VPN-/Firewall-Baseline dokumentiert. |
| Sicherung | Gemeinsame Datei-/Offline-DB-Sicherung auf verschlüsseltem SMB, vollständige Repositoryprüfung und Restore; erster automatischer Vierstundenlauf bestanden. Physischer und logischer DB-Restore separat nachgewiesen. |
| Aufbewahrung | 7 täglich / 4 wöchentlich / 6 monatlich. Reale manuelle Löschung, begrenztes Prune und anschließender Restore bestanden; täglicher Timer aktiviert. |
| Alarme | Backup-Watchdog alle15Minuten, Aufbewahrungs-Watchdog stündlich. SMTP-Testempfang bestätigt; tatsächlicher Serverausfall braucht einen unabhängigen Dienst. |
| Schlüssel | Externe Verwahrung historisch nachgewiesen; aktuelle Verfügbarkeit von Archivpasswort, LUKS-Passphrase und SMB-Zugang vom Betreiber bestätigt. LUKS-Header auf E: hashgleich. Kein neuer vollständiger Off-Server-Restore. |
| Provider | USV und KVM-Zugang laut Betreiber beim Provider abgesichert. Als Betreiber-/Providerangabe dokumentiert, kein eigener Stromausfall- oder BMC-Netztest. |

## Gebündelte Belastungsprüfung

Zehn Minuten synthetische CPU-/RAM-Arbeit ohne Root. Vier Arbeiter auf vier erlaubten logischen CPUs, je256MiB wiederholt beschriebener und per SHA256 geprüfter Speicher, insgesamt1GiB. Pro Prozess512MiB Adressraumgrenze und CPU-Zeitlimit, niedrige Priorität; äußeres Gesamttimeout660Sekunden plus15Sekunden Killfrist. Health-/Temperatur-/Speicher-/RAID- und Dienstkontrollen alle circa5Sekunden. Abbruch bei CPU>=85°C, NVMe>=65°C, verfügbarer RAM<4GiB, degradiertem RAID, fehlerhaftem/veraltetem Healthbericht oder unerwartetem Dienstzustand. Kein DB-/GPU-/Datenträger-Lastlauf, kein Neustart.

Lokaler Guardtest prüft Normalfall sowie sechs Abbruchfälle. Fünfsekündiger Linux-Probelauf mit zwei Arbeitern und32MiB bestanden. Geprüfter Lasthelfer `artifacts/server-load23.py`, SHA256336a121e85401a0cc8db9d1c39b577afce80653426ace09b536c419d3cab0ef2. Remote `/home/klaus999/bpload23.py`, Ergebnis `/home/klaus999/load23-result.json`.

**Ergebnis: bestanden.** Lauf23.09.21:33:05–21:43:05UTC, insgesamt600,24Sekunden. Vier Arbeiter jeweils rund600CPU-Sekunden; zusammen11150 vollständig erfolgreiche Schreib-/SHA256-Prüfzyklen auf je256MiB. 121 Messpunkte, keine ausgelöste Schutzgrenze. Maxima der Messserie: CPU60,25°C, NVMe35,85/44,85°C; ergänzende Live-Abfrage zeigte kurz61,125°C CPU. Mindestens123291MiB verfügbarer RAM. SSH/WireGuard/GDM aktiv, PostgreSQL weitergestoppt, kein Backup-/Retentionlauf während des Tests. Alle Kinder beendet.

Frische separate Nachkontrolle: keine Python-Testprozesse, keine failed Units, alle vier Backup-/Retentiontimer weiterhin active/enabled; CPU wieder44,125°C. Ergebnis lokal `artifacts/server-load23-report.json`, SHA256 `7de3beaf14a8eb315b1536f1de03907db1674ef085334ba3df693abf1227f4bc` identisch zur Serverdatei. Der ursprüngliche lokale SSH-Client lieferte trotz abgeschlossenem Serverprozess keine Rückkehr und wurde gezielt geschlossen. Deshalb stammt der Erfolgsnachweis aus dem vollständig gelesenen, hashgleichen Ergebnisbericht und separater Prozess-/Dienstprüfung, nicht aus dessen lokalem Exitcode. Keine Wiederholung des Lastlaufs notwendig.

 Ein Erfolg belegt dieses begrenzte Lastprofil, keinen vollständigen128GiB-RAMtest, ECC-Nachweis, GPU-Lasttest oder mehrtägigen Hardware-Burn-in.

## Offene Punkte mit Wiedervorlage

| Punkt | Status / Zeitpunkt |
|---|---|
| ECC | Providerbeleg fehlt. Bei Non-ECC explizite Risiko-/Beschaffungsentscheidung vor sensiblen Produktivdaten. |
| Secure Boot / Installationsprovenienz | Secure Boot deaktiviert; alte Neuinstallationsnachweise nicht nachträglich erzeugt. Abweichungen bei Gesamt-G0 einordnen, keine spontane Firmwareänderung. |
| Erste planmäßige Aufbewahrung | Timer aktiv; manueller Lauf bestanden. Ersten geplanten Lauf24.09.03:00CEST später nachweisen. |
| Online-DB-Backup | Vor Start einer dauerhaft laufenden Produktdatenbank nötig. Aktuelles Cold-Profil lehnt laufendes PostgreSQL ab. |
| Rescue / vollständiger Wiederaufbau | Vom Betreiber für später zurückgestellt; RTO12h bleibt Ziel ohne Vollrestore-Nachweis. |
| Zweite aktuelle Datenkopie | Vom Betreiber zurückgestellt; SMB einzige aktuell nachgewiesene externe Datenkopie. Erinnerung beim Übergang am23.09. erfolgt; Standort bleibt Betreiberentscheidung. Einmalige Erinnerungsautomation anschließend pausiert. |
| Externe Ausfallüberwachung | Vom Betreiber zurückgestellt; später über externen Dienst. Keine Einrichtung jetzt. |
| RPO12h | Vierstündlicher Sicherungsplan und Altersalarm aktiv; keine langfristige Einhaltungsgarantie aus einzelnen erfolgreichen Läufen. |
| Wartungszugang | Temporärer SSH-Key erlaubt neue Anmeldungen nur bis24.09.15:45:51CEST. Keine automatische Verlängerung oder neue Dauerrechte. |

## Kurze Besprechung vor Hermes

Vorgeschlagene Reihenfolge: lokale Hermes-Funktionslücken anhand des aktuellen Codes und aktiven App-Zustands abgleichen; bereits bestandene Pilot-/Testketten nicht neu implementieren. Danach Routingharmonisierung RH-1 und fehlende konkrete Adapter/Mehrgruppen-Abnahmen priorisieren. Allgemeine Produktfreigaben, Strategiewahl und Serverdeployments bleiben separate Schritte; kein Erstmodul automatisch auswählen. Die aktuelle Priorisierung und noch nicht umgesetzte Funktionen sind zunächst zu bestätigen, ältere Statusseiten enthalten historische Zwischenstände.

Medium bleibt Standard. Low nur für abgegrenzte Routinepakete nach ausdrücklicher Umschaltaufforderung und Bestätigung. Kein Modell-/Reasoningwechsel aus diesem Bericht.

## Nachweise

- SERVER_AKTUELL.md und SERVER_ABNAHME_AKTUELL_2026-09-23.md
- verification/BACKUP_RUNTIME_2026-09-23.md
- verification/RETENTION_RUNTIME_2026-09-23.md
- verification/RECOVERY_CUSTODY_MONITOR_2026-09-23.md
- verification/BOOTPFAD_ERGEBNIS_2026-09-20.md
- verification/G0_NACHTBEOBACHTUNG_2026-09-21.md
