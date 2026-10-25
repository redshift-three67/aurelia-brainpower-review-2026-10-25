# Wiederaufnahme nach Speicherbereinigung, 02.10.2026

Maßgeblicher lokaler Wiederherstellungspunkt: `checkpoints/Hermes-RadiWorks-20261002-Speicherpause`. Zuerst dort `VERIFY.json`, `MANIFEST.json`, `SOURCE_STATE.json` und `RESTORE.md` lesen. Bei normaler Fortsetzung die aktuellen Arbeitsdateien verwenden; den Checkpoint nur bei wirklichem Verlust nach Hashvergleich gezielt zurückspielen. Er ist eine persönliche lokale Kopie, kein Server- oder Windows-Abbild und keine unabhängig gelagerte Zweitsicherung.

## Fachlicher Stand

- RadiWorks ist weiterhin ein lokaler Modulprototyp ohne Aurelia-Integrationsfreigabe. Die isoliert geprüfte Datenbanksuche und der optionale Fallfokus wurden am 02.10. in `C:\Users\Hubert111\Documents\Radiworks\radiworks_port`, den 8103-Kandidaten und drei RadiWorks-Referenzen in `Modul_Templates` übernommen. Der technische Browsercheck auf 8103 bestand; die bewusste Betreiberprobe mit erneut geladenem gespeicherten Fall steht aus. [Prüfbericht](verification/RADIWORKS_FOKUS_DATENBANKSUCHE_2026-10-02.md).
- Beim letzten dokumentierten 8103-Abgleich waren 3 Fälle, 51 Drafts und 123 Datenbanken sichtbar, Auto AUS und die Broadcast-Queue leer. Der aktive Fall wird nach einem Prozessneustart nicht automatisch ausgewählt. Diese Zahlen sind der damalige Befund, keine neue Live-Abnahme.
- S4.6 ca. 98 %, S4.7 ca. 90 %, Suche/Fokus im Betreiberstand ca. 90 %, S4.8 0 %; dies sind Planungsnäherungen. Danach bleiben Area-Ergänzung, Peggotty-Randfälle, reales Kamera-/Recovery-Umfeld und die getrennte Host-/Mandantenentscheidung offen. Radi144 folgt erst nach der RadiWorks-Vorbereitung.
- Chat-Route laut Betreiber: GPT-6 Sol/high führt, Luna/max für passende begrenzte Worker-Aufgaben, Astra/medium für schwer auflösbare Widersprüche und folgenreiche unabhängige Prüfung. Das ist von den Hermes-/Governors-Routen getrennt. Bei dieser Sicherung wird kein Modellauftrag gestartet.

## Lokale Codex-Modellfrage vor der nächsten Arbeit

- GPT-6.1 Sol wird auf einem zweiten PC desselben Abos angezeigt, hier im Modellwähler bisher nicht. Die Desktop-App meldete Version 26.930.21537 als aktuell; das separate Workspace-Bundle meldete 26.909.12148. Unterschiedliche Nummern allein beweisen keinen Defekt.
- Global ist `gpt-6-sol`/`high` mit dem bewusst für Governors eingerichteten CC-Switch-Provider konfiguriert. CC Switch unverändert lassen. Zwei Konfigurationshinweise im Bild betreffen ignorierte/deprecated Einträge und belegen keine Ursache für die fehlende Modellauswahl.
- Die gesonderte CLI-Diagnose meldete am 02.10. nur rund 4,7 GB freien Platz auf C:, eine beschädigte lokale Codex-Laufzeitdatenbank und einen nicht erreichbaren Runtime-/Update-Dienst. Der CLI-App-Server startete deshalb nicht. Ein Zusammenhang mit dem laufenden Desktop-Modellwähler ist noch **nicht** bewiesen. Kein Reset, keine Datenbankverschiebung und keine CC-Switch-Änderung auf Verdacht.

## Genau hier fortsetzen

1. Nach der Speicherbereinigung freien Platz, Desktop- und Workspace-Status prüfen; nichts aus `.codex\sessions`, `.codex\config.toml`, `Brainpower\checkpoints` oder den RadiWorks-Laufzeitdaten pauschal löschen.
2. Bei Bedarf Modellwähler, gleichen ChatGPT-Workspace und Providerprofil auf beiden PCs vergleichen. GPT-6.1 Sol nicht durch eine ungeprüfte Konfigurationsänderung erzwingen. Die bestehende Sol/high-Chatroute gilt weiter.
3. 8103 und die gespeicherten Fälle lesend prüfen; Fall bewusst erneut laden. Dann die ausstehende Betreiberprobe für Fokus/Suche und die priorisierten RadiWorks-Restfunktionen fortsetzen. Bestätigte Funktionalität erhalten und Produktgates beachten.

Der Checkpoint enthält Quell- und ausgewählte Laufzeitkopien, jedoch weder Git-Historien noch einen Speicherabbild laufender Prozesse. Persönliche Fall- und Draft-Daten bleiben lokal und dürfen nicht als neutrales Release weitergegeben werden.
