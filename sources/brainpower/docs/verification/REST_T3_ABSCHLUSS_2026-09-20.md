# T3 – Abschluss des begrenzten synthetischen Ubuntu-Testumfangs

Stand 20.09.2026. Der konkret vereinbarte T3-Umfang einschließlich CPU-Wirkungsnachweis und T3e-Belegabgleich ist abgeschlossen. Dies ist keine Gesamtabnahme von Aurelia, Hermes oder sämtlichen Server-/Produktionsanforderungen.

| Prüfung | Ergebnis | Beleg unter artifacts/ |
|---|---|---|
| Normalende | process_completed; Journal succeeded/active0 | t3normal20-report.json |
| Speichergrenze | memory_verified; OOM/SIGKILL, erwarteter Workerfehler failed/active0 | t3memory20-report.json |
| Unkooperative Prozessgruppe | abort_verified; aborted/active0 | t3abortv220-report.json |
| Controllerverlust | controller_loss_verified; zunächst unknown bei laufendem Worker, Ende unabhängig beobachtet, released_unknown/active0, kein Replay | t3lossv320-report.json |
| CPU-Drosselung | cpu_verified; succeeded/active0, positive gemessene Drosselzähler | t3cpu20-report.json |
| Linux-Transport/TLS | 47 Tests bestanden, keine Fehler/Skips; temporäres CA-Material entfernt | t3tls20-report.json |

Alle fünf Prozessberichte maschinell auf eindeutige Laufkennungen, jeweiligen erwarteten Status/Journalabschluss, package_removed/unit_retired/staging_absent/services_unchanged=true geprüft. CPU-Beleg zusätzlich erneut mit dem Validator ausgewertet, Deltas stimmen überein. Prüfungen wurden nicht erneut ausgeführt. Historische blockierte Läufe und deren getrennte Bereinigung bleiben dokumentiert und werden nicht in Erfolge umgeschrieben.

## CPU-Istwerte

Lauf 2a166896ef1c47ceaa71bfd178710cde, Invocation1167e741a770443a94c98bc09fe9bd54. Dauer4056467424ns, CPU-Nutzungdelta1004695µs, Periodendelta41, gedrosselte Perioden41, Drosselzeit3052260µs. cpu.max=25000/100000, MemoryMax134217728, Swap0, Tasks16. Rund24,8% eines CPU-Kerns während dieses kleinen Messfensters, keine Echtzeitgarantie oder Produktionsdimensionierung.

CPU-Prozess regulär beendet (success/ExecMainCode1/Status0), Journal succeeded/active0. Separate SSH-Abfrage nach dem Lauf: Unit not-found/inactive/MainPID0; SSH/WireGuard/GDM active. Bericht per SCP gesichert und SHA256 lokal/servergleich.

## SHA256 der Abschlussbelege

| Beleg | SHA256 |
|---|---|
| Normal | fd9bd913a25eea50e4ace0be140d777b85281cf77a9e2294e389906c70d35543 |
| Speicher | c6d966f327f2e5d16c7cf0e9cf981087bd4ed83a1cf520c102667ea0a7ecd256 |
| Abbruch | 9f3caa0c65380255fdd660752ea94402a5fb616b65fe9ac6935a2d7ef1cce439 |
| Controllerverlust | 1b890ccb52854834caa9dfeb1713511d35f2a6af003c7967b12e81181f850850 |
| CPU | 7e8c5d0b691b692ca30c0a9caf027692689c4f4cfa978bb9e7cc6d94973a763a |
| TLS | a750a9a6e2f9f78662eca4d8c26deb742e5ec974a24dac5476ebc691d3f87838 |

Letzter lokaler Implementierungsstand: 222 Contract-Tests bestanden (39,318s). Linuxbelege entstanden auf den jeweils dokumentierten, gehashten Paketen; ältere Varianten wurden nicht unter dem neuesten Paket wiederholt. Historische Berichte/Quellanker bleiben erhalten. Rücknahme bezieht sich auf jeweilige Laufunit/-staging; root-eigene Archive, Quelldateien und Testjournal bleiben als Evidenz erhalten.

## Verbleibende Grenzen und Fortsetzung

B07–B09 besitzen nun den vereinbarten synthetischen Ubuntu-Nachweis. Reale modulbezogene Limits/Manifest-/Schema-/Releasebindung, Produktprozesse, Mandanten-/Berechtigungsvarianten und Produktions-CA bleiben gemäß REST_ABDECKUNG_2026-09-20.md separat offen. Keine allgemeine Sandbox gegen feindlichen nativen Code, kein Gesamtserver-Ausfalltest und keine pauschale Sicherheitsgarantie.

Nächster Arbeitsschritt: Quellen-/Voraussetzungsabgleich für Aurelia und Modul-Templates, anschließend konkrete Produktvertragsvarianten planen. S4, Registryaufnahme, Erstmodulwahl und Deployment bleiben eigene Gates. Keine automatische Umsetzung in externen Produktrepositories.

Nach Ende dieser Testläufe Desktop idle-delay wie angekündigt von1800 auf300 Sekunden zurückgesetzt und rückgelesen; Passwortsperre aktiv. Keine weitere KVM-Eingabe für T3 erforderlich.
