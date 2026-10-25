# RadiWorks R6 – Dauerinstanzen, 08.10.2026

Stand 2026-10-08T09:57:22.969030+02:00. Der Betreiber bestätigt auf 8112 feste/Solfeggio-Töne und Rosa Rauschen hörbar und beauftragt anschließend die Übernahme vor der Pause. Diese Übernahme auf **8103–8109 ist geprüft abgeschlossen**. Weitere R6-Teilpakete bleiben getrennt offen.

## Version und Daten

- Release `runtime/rw-r6-release-20261008`: 200 manifestierte Produktdateien, bytegleich zum abgenommenen Kandidaten `rw-audio-diagnosis-20261008`, Manifest SHA256 `445ece8f8c826e1391fead34c9a4c9b271e3b13b6d59a7654f66f11ab77b6275`. Unveränderter, separat kopierter Servicewrapper aus `tools/radiworks_release_service.py`; dessen Hash wird im Abschlusscheckpoint erfasst. Keine synthetischen Vorschau-/Testdaten übernommen.
- **16 vorhandene Fälle erhalten**, Verteilung 3/3/2/2/3/2/1. Alle 225 bisherigen statischen Daten-/Konfigurationsdateien außer den sieben neu geschriebenen technischen Instanzmarkern bytegleich zur geschlossenen Sicherung. Alle vorhandenen Datensätze in sieben SQLite-Datenbanken unverändert, `integrity_check=ok`; neue persönliche Stores sind additive getrennte Dateien.
- Home, Port, Katalog, Clarke-Pfad und alle sieben verschiedenen Scope-Kombinationen unverändert. Schlüsselinhalt weder ausgegeben noch kopiert. Vorhandener externer E:-Wiederherstellungsschlüssel weiterhin nur auf **8103** konfiguriert; 8104–8109 behalten ihre bisherige Konfiguration ohne Recoveryschlüssel. Stochastic bei aktivem Fall dort nicht als neu freigegeben behaupten.
- Auto und virtuelle Broadcasts für den freigegebenen Wechsel beendet; keine automatische Wiederholung alter Broadcasts. Fälle, Profile und Historien erhalten. 8112 bleibt unverändert verfügbar.

## Betriebs- und Browserprüfung

- Alle sieben Listener nur 127.0.0.1; tatsächliche PID, Servicekonfiguration, Scope und Produktmanifest geprüft. Alle sieben Dienste durch ihre vorhandenen Windows-Aufgaben gestartet; die acht Taskdefinitionen einschließlich Watchdog vor/nach exakt identisch und aktiviert. Kein Windows-Neustart und kein tatsächliches Schließen von Codex in dieser Prüfung; vorhandene Anmeldetrigger/Watchdog bleiben erhalten.
- Beim ersten Pilotversuch hatte `Stop-ScheduledTask` alte abgetrennte PowerShell-Hosts nicht beendet. Die Pilotidentität erkannte deshalb den alten Release und verhinderte eine falsche Erfolgsmeldung. Alte Hosts ausschließlich nach vollständigem Befehls-/Portabgleich beendet, Pilot sauber heruntergefahren, neuer Schedulerstart danach geprüft. Jetzt genau sieben zugehörige Hosts; keine Produktänderung nötig.
- 123 Datenbanken je API; 131 Dropdownoptionen inklusive acht Gruppen. Auf allen sieben Instanzen echte Chrome-Prüfung mit stummer Audioausgabe: Original-GV/21er-/Auto-Bedienung, Persönliche-Heuristik-Bereich, Audioaktivierungsknopf und Dock öffnen/Escape sichtbar/funktional; keine JavaScript-Pageerrors. Keine neuen Analysen, Falländerungen oder Broadcastaufträge durch diese Prüfung.
- 6/6 Schedulerlauncher-Tests frisch bestanden; PowerShell-Host geparst. Der Produktcode ist manifestgleich zum bereits geprüften Kandidaten: dessen 100/100 JS-Tests, Vier-Modi-/PCM-/Medienprüfungen bleiben die vorherigen Nachweise, keine neue Vollsuite behauptet. Digitale Audiofreigabe ist keine Aussage zur Gerätelautstärke; Betreiber-Hörprobe wurde separat bestätigt.

## Sicherung und Rückweg

Private geschlossene Sicherung: `checkpoints/RadiWorks-R6-Dauerinstanzen-Vorher-20261008-094727`. 503 SHA256-verifizierte Dateien / 444.623.863 Bytes in Live- und geschlossener Vorher-Sicherung zusammen, sieben konsistente SQLite-Kopien je Phase; Eigentümer-/SYSTEM-ACL ohne Vererbung. Sie enthält Fall-/Historieninformationen und gehört nicht in Start5 oder öffentliche Artefakte. SQLite-Snapshots abschließend auf DELETE-Journal normalisiert: flüchtige WAL/SHM-Dateien gehören nicht zum Archiv, alle 14 logischen Snapshotinhalte erneut identisch geprüft. Externe Schlüssel müssen separat am bisherigen sicheren Ort erhalten bleiben.

Bei Rücknahme erst alle sieben Hosts kontrolliert anhalten, eigene Dienste per service.stop sauber beenden, dann `scheduled-host.before.ps1` zurück auf den Hostpfad legen. Alte C23-Konfigurationen und Release bleiben unverändert vorhanden. Datenrücknahme nur bewusst aus `closed/PORT`, niemals ungeprüft neuere Fälle überschreiben; Schlüssel außerhalb der Sicherung weiterhin erforderlich. Stopmarker nach belegtem Stillstand entfernen und vorhandene Aufgaben wieder starten; anschließend Produkt-/Scope-/Fallprüfung wiederholen.

## Phasenstand

| Teilpaket | Stand |
|---|---|
| R5 Audio-/Bildprofile und Nutzer-Hörabnahme | 100% dieses freigegebenen Umfangs |
| R6.1 Dauerinstanzen 8103–8109 und Datenbewahrung | **100% geprüft** |
| R6.2 Quellmodul / Modul_Templates / Start5-Aktualisierung | noch offen; nach Pause |
| Vollständige F:-Projekt-/Konfigurationssicherung | noch offen; nach R6.2 |
| Kamera / externe Windows10-Prüfung / Ubuntu-Abnahme | gesonderte Restprüfungen |
| S4.8 Aurelia-Integrationsfreigabe | 0%, keine Freigabe |

Tatsächlich eingesetzter Helfer in dieser Übernahme: GPT-6 Luna/max, rein lesende Kompatibilitäts-/Startpfadprüfung. Root führt Datenbewahrung, Umstellung und Verifikation aus; kein neuer Astra-Aufruf, da keine verbleibende materielle Widersprüchlichkeit. Gewünschte Leitroute GPT-6.1 Sol/high wird nicht aus gespeicherten Defaults als Laufzeitnachweis abgeleitet.

Nachweise: `runtime/rw-r6-rollout-20261008/verified-8103-8104-8105-8106-8107-8108-8109.json`, `tasks-authority-verified.json`, `browser-verified.json`, Vorher-CHECKPOINT und gesonderter Abschlusscheckpoint.
