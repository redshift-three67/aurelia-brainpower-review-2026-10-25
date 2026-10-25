# T3d: Linux-TLS-Nachweis vorbereitet

Linux-Testausführung nach ausdrücklicher Betreiberfreigabe einmalig abgeschlossen. Der vom Ressourcen-/Abbruchtest unabhängige T3d-Schritt ist nachgewiesen; T3c bleibt offen.

## Tatsächlicher Ubuntu-Nachweis

Am 20.09.2026 um 12:45:16 UTC als klaus999 mit `/usr/bin/python3 -I -B /home/klaus999/t3tls20.pyz` ausgeführt. Vorher Server-Paket-SHA256 gegen freigegebenes lokales Archiv geprüft.

- **47 Tests bestanden**, 0 Fehler, 0 Fehlschläge, 0 Skips; Testlaufzeit 5,729 s, Rückgabecode 0.
- `linux_tls_verified`, Python 3.12.3, OpenSSL 3.0.13, unprivilegiert und ausschließlich synthetisch.
- Temporäres Testmaterial laut Bericht entfernt; zusätzliche SSH-Suche nach eigenen `/tmp/aurelia-t3-tls-*`-Verzeichnissen ohne Treffer.
- SSH, wg-admin und GDM vor und nach dem Lauf active.
- Export `artifacts/t3tls20-report.json` lokal gesichert und maschinell geprüft. Server- und lokaler SHA256 identisch: `a750a9a6e2f9f78662eca4d8c26deb742e5ec974a24dac5476ebc691d3f87838`.

Dies belegt den synthetischen Loopback-TLS-Vertrag auf Ubuntu, keine produktive Aurelia-Integration, keinen externen Netzwerkpfad und keine Produktfreigabe. Speicherlimit-Wirkung und Controllerverlust bleiben gesonderte T3c-Nachweise.

## Vorbereitung (historisch)

## Umfang des konkreten Laufs

Einmalig 47 bestehende Tests aus `test_contract_transport`, `test_contract_deadlines` und `test_contract_policy` als unprivilegierter klaus999. Nur synthetische Daten. Eigene temporäre CA/Zertifikate, ausschließlich Loopback und dynamische Ports. Kein systemweiter Truststore, keine Dienstinstallation, keine Firewall-/Governoränderung, keine Modellaufrufe. Kein Root und keine KVM erforderlich.

Der Server meldet Python 3.12.3, OpenSSL 3.0.13 und dynamischen Portbereich 32768–60999; Governor-Port 8787 wird somit nicht für dynamische Testlistener verwendet. Testhilfe wählt feste plattformspezifische OpenSSL-Pfade, keinen PATH-Fallback. Fehlendes OpenSSL führt zu Fehler statt Skip.

## Belege der Vorbereitung

- Drei neue Plattformtests mit vorher beobachtetem Fehlschlag; danach gesamte lokale Suite: **185 Tests bestanden**, 0 Fehler/Skips, 40,742 s.
- Lokaler Archivbau: 13 Dateien syntaktisch geprüft und byteweise mit Quellen verglichen.
- `artifacts/rest-t3-tls-20260920.pyz`: SHA256 `6dbc114c4ed8e90c41384d040387ec49194584c3ca7bdab707912cbd0fa94c49`.
- Einzeldatei-Hashes: `artifacts/rest-t3-tls-20260920-manifest.json`.
- Einstieg: `artifacts/t3-tls-main-20260920.py`.

Geplanter Bericht `/home/klaus999/t3tls20-report.json` wird exklusiv angelegt, keine automatische Wiederholung. Erfolgsstatus nur bei exakt 47 bestandenen Tests, null Skips und entfernten temporären Materialien. Bei einem Prozessabbruch ist ein unvollständiger Bericht kein Erfolg; verbliebene eigene Materialien wären gesondert zu prüfen. Die einzelnen Netzwerk-/OpenSSL-Aufrufe haben Zeitgrenzen; keine harte globale Laufzeitgarantie wird behauptet.

Freigabe, Übertragung, Serverhashprüfung und einmalige Ausführung sind erledigt; Bericht und temporäre Rücknahme ausgewertet. Nicht wiederholen. Kein Produkt-GO.
