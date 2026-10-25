# T3 – laufende Ressourcenbeobachtung und gezielter Abbruch vorbereitet

20.09.2026: **173 lokale Tests bestanden, 0 Fehler, 0 Skips, 40,626 Sekunden**. Sieben zusätzliche Tests für den neuen Ablauf und seine Backend-Beobachtung; bestehender Prozesszählertest ergänzt. Kein neuer Ubuntu-Lauf.

## Vorbereiteter Ablauf

1. Bestehendes Paket/Runtime und SSH/wg-admin/GDM-Zustände prüfen; neue eindeutige Laufkennung verwenden.
2. Festen synthetischen Worker im Modus ignore_term starten: Hauptprozess und ein mittels fork erzeugter Kindprozess schlafen, ignorieren SIGTERM. Kein CPU-Stresstest und keine Speicherlast-Erzeugung.
3. Innerhalb eines gemeinsamen 5-s-Beobachtungsbudgets mindestens zwei Prozesse in der identisch gebundenen cgroup erfassen. memory.max, memory.swap.max, pids.max und cpu.max lesen und gegen 128 MiB / 0 Swap / höchstens 16 Tasks / höchstens 25 % CPU prüfen.
4. Journalabbruchanforderung speichern, frische Dienstidentität prüfen, genau diese Unit stoppen. systemd darf nach der konfigurierten 2-s-Stopfrist die Prozessgruppe mit SIGKILL beenden; der systemctl-Aufruf hat 5 s Timeout.
5. Inaktive/entfernte eigene Unit, gleiche Bootkennung und fehlende cgroup nachweisen; kein Ende allein aus erfolgreichem Stopkommando ableiten. Nachgelagerte Beobachtungen prüfen diesen Zustand erneut. Unterbrochener/fehlender Beleg bleibt blocked.
6. Journal aborted, bekannte Testdateien gezielt entfernen, Fremddienste erneut vergleichen und Bericht sichern.

Ergebnis abort_verified würde konfigurierte Ressourcenwerte und Ende der Testprozessgruppe bestätigen. Es würde **keine OOM-Durchsetzung, gemessene CPU-Drosselung oder vollständige Crash-Recovery** bestätigen. Prozesszahl belegt die Mitglieder der Testgruppe; eine allgemeine unabhängige Eltern-Kind-Beziehungsanalyse ist nicht implementiert. Der beobachtete Worker ist quellgebunden und erzeugt genau einen Kindprozess.

Die 5-s-Frist begrenzt den Stopkommandoaufruf; nachfolgende separate Belegabfragen haben eigene begrenzte Aufrufe. Eine durchgehend gemessene Gesamtdauer bis zum letzten Journal-/Cleanupbeleg ist hier noch keine Abnahmeaussage. Keine harte Echtzeitgarantie.

## Tests / Artefakt

Neue Runnerfälle: positiver Ablauf, einzelner Prozess, unbegrenztes RAM, fehlender Endebeleg und falsche Identität. Backend: begrenztes Warten auf Prozesspaar sowie wiederholte Nachprüfung nach verschwundener Unit. Vor Implementierung fehlende Funktionen/Belege nachgewiesen; anschließend Gesamtlauf erfolgreich.

Artefakt: `artifacts/rest-t3-runner-20260920-abort.pyz`.
SHA256: `324874e3da33187a51443f2e463e645741dc4c2ad129566b6d692fc2d1956561`.
ZIP-Integrität und Bytegleichheit aller acht Module geprüft; gebautes Paket verweigert Windows-Ausführung mit Exit 2. Historisches v2-Paket bleibt unverändert.

Workerpaket unverändert mit Manifestanker `5379aa7b6d45a25a93ba5a6b1a507e8281c3c99b0f4b555c562b7fffcd7b42f1`.
Neue vorgesehene Laufkennung: `fcc704a500994914980489fbb99afda6`.

## Konkreter Umfang zur separaten Betreiberfreigabe

Einmalige geschützte Bereitstellung des neuen Runners als `/opt/aurelia-t3/runner-abort.pyz`, externen SHA256 prüfen, vorhandenen Normalfallrunner erhalten. Anschließend genau ein Aufruf:

```text
/usr/bin/python3 -I /opt/aurelia-t3/runner-abort.pyz abort fcc704a500994914980489fbb99afda6 5379aa7b6d45a25a93ba5a6b1a507e8281c3c99b0f4b555c562b7fffcd7b42f1
```

Keine Änderung an Produktdiensten, Firewall, SSH oder Serverboot. Maximal 128 MiB RAM, kein Swap, 16 Tasks, 25 % CPU, 20 s Unitlaufzeit. Eigene Testgruppe wird gezielt beendet. Bei Fehler kein automatischer Retry und keine pauschale Bereinigung. Belege/Installation bleiben erhalten. Root-Ausführung erst nach konkreter Freigabe dieses Tests, nicht aus der bereits verbrauchten Normallauf-Freigabe ableiten.
