# Serverklärung und Betreiberentscheidungen – 13.09.2026

## Maßgebliche neue Betreiberentscheidung: Neuaufbau ohne Projektübernahme aus Debian

Der Betreiber erklärt ausdrücklich: Auf dem bestehenden Server befinden sich keine Projekte mehr, die gesichert werden müssen. Der Server soll neu initialisiert und partitioniert, mit Ubuntu gemäß Aurelia-Vorgaben vorbereitet und später mit den lokal entwickelten Projekten bestückt werden. Backup und Überwachung werden in der neuen Ubuntu-Umgebung eingerichtet; deren Wiederherstellung wird anschließend geprüft.

Diese konkrete Entscheidung ersetzt die bisherige Forderung nach einem Restore des alten Projektbestands als Voraussetzung des Neuaufbaus. Für den vom Betreiber als nicht erhaltungsbedürftig erklärten Projektbestand ist die alte Sicherungs-/Restore-Anforderung nicht anwendbar; dies ist eine Betreiberentscheidung, kein bestandener Restore-Test. Nicht als blanket approval zum Löschen unbekannter Datenträger, Provider-Speicher oder lokaler Projekte auslegen. Etwaige bei der Inventur gefundene unklare Nicht-Projektbestände gezielt klären, nicht die bereits entschiedene Projektsicherung erneut verlangen.

Aktuelle Reihenfolge:
1. Lesende Server-/Datenträgerinventur und nutzbaren Konsolenzugang feststellen.
2. Konkreten Ubuntu-Installationsplan mit Zielgeräten, Partitionierung, RAID-/Verschlüsselungskonzept und Managementzugang aus den Aurelia-Vorgaben erstellen und zur finalen Auswahl/Freigabe vorlegen. Der Neuaufbau ist grundsätzlich gewünscht; keine erneute Grundsatzfrage nötig.
3. Nach konkreter Freigabe Ubuntu einrichten, absichern und überwachen.
4. Den vorhandenen 1-TB-G2-Speicher in ein überprüfbares Backupkonzept einbinden, Basiszustand sichern und isoliert wiederherstellen. Restore des neu aufgebauten Systems erst nach Einrichtung prüfen. Vor nicht reproduzierbaren/produktiven Daten einen funktionierenden Sicherungs- und Restoreweg nachweisen.
5. Lokal entwickelte Module nur entsprechend ihrer eigenen Gates integrieren; neuer Server erteilt keine pauschale Modulfreigabe. Ubuntu-Produktprüfungen bleiben Pflicht.

Historische G0-Unterlagen und die alte Prüftabelle sind insoweit überholt. Keine erfolgreichen Backups, Restore-Ergebnisse oder automatische Gateabnahme daraus erfinden. Entscheidung derzeit im Workbench-Projektgedächtnis dokumentiert, noch nicht als konkrete Gateentscheidung im Governor-Journal oder in externen Produktgedächtnissen übernommen. Diese Übernahme muss den neuen Geltungsbereich sichtbar abbilden; nicht den alten Nachweis als bestanden markieren.

In diesem Dokumentationsschritt keine Serveraktion ausgeführt.

## Historischer Verlauf und ergänzende Hardwareevidenz

Die folgenden älteren Backup-Forderungen sind durch die obige Betreiberentscheidung für den alten Projektbestand ersetzt.

## Neueste Bildnachweise: Backupspeicher und Hardware

Diese Ergänzung präzisiert die älteren Bildbefunde weiter unten.

- Speicher.JPG zeigt beim Dedicated GPU Server M G1 den zugehörigen Dienst „Backupspeicher 1 TB G2“. Der Betreiber bestätigt dessen Einsatzfähigkeit. Gebuchter zugehöriger Speicher ist damit belegt; Zugriff, Belegung, Sicherungsjobs und Restore wurden nicht technisch geprüft. Geschwärzte Angaben werden nicht rekonstruiert.
- Speicher_2.JPG zeigt vier DDR5-Module mit jeweils 32768 MB, insgesamt 131072 MB (entspricht der üblichen 128-GB-Ausstattung). Alle vier werden mit NoECC und 3600 MT/s angezeigt. Der Screenshot stützt die RAM-Zielkapazität; die ältere Panelangabe 16384 ist damit als widersprüchliche Übersicht zu behandeln. OS-Inventur steht aus. Keinen aktiven System-ECC-Schutz behaupten; NoECC ist die angezeigte BMC-Angabe, keine eigene elektrische Hardwareprüfung.
- CPU_2.JPG zeigt AMD Ryzen 5 9600X, sechs aktive Kerne, zwölf Threads und 3900 MHz. Das entspricht dem dokumentierten CPU-Ziel auf Ebene der BMC-Anzeige.
- PSU_1.JPG zeigt zwei PWS-741P-1R mit grünen Gesundheitsanzeigen. Dies ist ein Bildzustand, kein Last-/Ausfalltest und kein Nachweis unabhängiger Stromversorgung oder USV.
- Keine Seriennummern, Kontodaten oder vollständigen Speicherzugangsdaten in diesen Bericht übernommen.

Nächster Backup-Schritt: vorhandene Sicherungspunkte, Datum/Erfolgsstatus, geschützten Umfang, freien Speicher und einen getrennten Restore-Nachweis prüfen. Die Eignung von 1 TB hängt vom tatsächlich zu sichernden Datenumfang und der Aufbewahrung ab. Zweite Kopie/Verschlüsselung gemäß Aurelia-G0 separat nachweisen. Keine neue Kapazität oder Hardware ohne Inventur empfehlen. G0-SRV-0 bleibt bis Nachweis und Abnahme offen.

## Aktuelle Betreiberangaben

- Serverziel 185.242.115.210; bestehender Nutzer klaus999; aktueller Zugang laut Betreiber über RDP/SSH.
- Der bestehende Server läuft unter Debian. Ubuntu und Aurelia sind dort noch nicht eingerichtet. Kein vorhandener Aurelia-Codepfad auf dem Server voraussetzen. Lokaler Aurelia-Code bleibt in Documents/ChatGPT/Aurelia.
- Erreichbare Provider-IPMI/KVM-Konsole bestätigt. Bilder zeigen Supermicro-BMC und Fernkonsole; Virtual-Media-/Recovery-Funktion noch nicht durch eigenen Funktionstest abgenommen.
- Betreiber folgt den konkreten Befunden/Empfehlungen und dem Testplan aus artifacts/QUELLEN_GATE_TESTPLAN_2026-09-13.md. Varianten werden technisch geprüft und empfohlen; finale Umsetzung entscheidet der Betreiber. Aufnahmen/Matrix bleiben gesonderte konkrete Annahmen.

## Backup-Evidenz präzise trennen

Frühere Aussage: tägliche Backups vorhanden (Betreiberangabe). Aktuelle Erklärung verweist auf IPMI/KVM und das Bild Server Control Panel_Backup.JPG. Dieses Bild zeigt eine allgemeine Web-Anleitung für libvirt/KVM-VM-Backups mit virsh blockcopy, keine Backupübersicht, keinen konkreten erfolgreichen Sicherungsjob und keinen Restorebericht.

IPMI/KVM-over-IP (Hardware-Fernkonsole) und KVM/libvirt (Virtualisierung) sind unterschiedliche Techniken. Vorhandener Fernzugang belegt weder VM-Betrieb noch eine eingerichtete tägliche Sicherung. Der zugehörige 1-TB-G2-Speicher ist inzwischen belegt (siehe Ergänzung oben). Tatsächliches Sicherungssystem, Zugriffspfad, Umfang, letzte erfolgreiche Sicherung und Restore-Nachweis bleiben ungeklärt. Die Betreiberangabe wird weder als bewiesen noch als widerlegt behandelt. RAID1 ersetzt keinen unabhängigen Backup-/Restore-Nachweis. Keine virsh-Anweisungen aus dem Bild ausführen.

## Weitere Bildbefunde

- Installationspanel bietet Ubuntu 24.04 Noble LTS manuell per PXE und warnt ausdrücklich vor automatischem Neustart bei Aktivierung. Keine Boot-/Installationsaktion ausführen; genaue Medienversion nicht als geprüft betrachten.
- Paneltext zeigt RAM: 16384, während Aurelia-Verfassung 128 GB DDR5 als Ziel nennt. Einheit/Aktualität/Serverzuordnung offen; keine tatsächliche 16-GB-Hardware daraus ableiten. Durch lesende Inventur klären.
- Verkehrskurven belegen keine Backups. Historische BMC-Ereignisse nicht ohne Liveprüfung als aktuelle Hardwarefehler behandeln.

## Nächste Schritte

1. Den jetzt belegten 1-TB-G2-Backupspeicher auf konkrete Sicherungspunkte und erfolgreiche Jobs prüfen; Speicherbuchung und tatsächliche Datensicherung getrennt behandeln.
2. Bestehende Debian-Installation lesend inventarisieren: Hardware/Datenträger, Dienste und Sicherungsmechanismus; keine vertraulichen Inhalte ausgeben. Zugangsprüfung ist noch nicht erfolgt. Die alte lokale SSH-Konfiguration mit Komma wurde nicht geändert.
3. Zu erhaltende Daten/Anwendungen und separates Restoreziel konkret erfassen; Betreiber kennt mögliche ausschließlich fachliche Erhaltungsanforderungen.
4. Vor einer Neuinstallation Backup-/Restore-Nachweis und Geräte-/Installationsplan prüfen und konkret freigeben lassen. Ubuntu-Zielabnahme erfolgt nach sicherer Einrichtung; lokale Vertrags-/Testvorbereitung kann vorher weitergehen.

Keine Produktdateien, Governor-Journalentscheidungen oder Einstellungen geändert; keine Serververbindung, Sicherung, Wiederherstellung, Neustart oder Installation in dieser Bildprüfung ausgeführt.

Referenzen: https://www.supermicro.com/en/solutions/management-software/bmc-resources ; https://www.libvirt.org/manpages/virsh.html#blockcopy
