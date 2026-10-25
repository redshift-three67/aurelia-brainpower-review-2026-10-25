# RadiWorks C23 / Portable5 — Abschlussstand

Stand: 2026-10-05T16:27:59.139086+02:00. Maßgeblicher aktueller Bericht; ältere Abschlussberichte bleiben historische Evidenz.

## Ergebnis und Betriebsstand

Alle sieben Dauerinstanzen **8103–8109** verwenden `C:/Users/Hubert111/Documents/Brainpower/runtime/rw-c23-fixed-release-20261005`: 131 gepinnte Produktdateien plus äußerer Servicewrapper. **13 API-Fälle und sämtliche Falldateibytes** sind nach geschlossenem Vorher-Checkpoint unverändert. Homes, Scopes, Katalog, Clarke-Pfad und externe Schlüsselkonfiguration blieben identisch. Der vorhandene E:-Recoverykey bleibt nur auf8103;8104–8109 bleiben seeded ohne neuen Recoverykey. Bewusst beendete Broadcasts werden nicht automatisch wieder gestartet. Originalmodus bleibt Standard; CPU80k-Vergleich ist getrennt und ausdrücklich wählbar. Browser nach Neustart mit Strg+F5 neu laden: opaque Fallreferenzen sind laufzeitbezogen, stabile Fall-IDs/Daten bleiben erhalten.

Acht Windows-Aufgaben einschließlich Watchdog sind aktiviert. Actions/Triggers/Principals/Settings sind vor/nach Wechsel gleich. Listener, Marker, Argumente, Prozessbilder, Startzeit und Hostkette aller sieben Dienste wurden erneut geprüft. Der Wartungsablauf hielt zunächst sicher vor einem Backup an: Aufgabenstop beendete den pythonw-Starter, alte Hidden-PowerShell-Hosts samt eigenen Konsolen blieben zurück. Acht eigene Hosts wurden anhand exakter Identität geprüft und nach sauberem Engine-Ende beendet; vor dem Backup waren ihre Kinder ebenfalls verschwunden. Keine fremden PIDs oder Ports beendet. Dies ist kein neu eingeführter automatischer Taskstop-Mechanismus. 8090 und der ältere synthetische Pilot8110 blieben außerhalb des Eingriffs. Tatsächliches Windows-Neustarten/Codex-Schließen wurde heute nicht ausgeführt.

## Eng begrenzte Katalogkorrektur

Der echte Portable-Lauf machte einen Originalnamen mit abschließendem Leerzeichen sichtbar. Drei Vergleichsmodule prüften bislang die zuvor getrimmte Namensvariante. Sie prüfen nun den **exakten ersten tabgetrennten Katalogwert**; leere/Whitespace-Anfragen werden weiter abgewiesen. Genau drei von131 Produktdateien geändert;128 andere Produktdateien und der äußere Wrapper sind bytegleich. Originalanalyse, Entropie und Formeln wurden nicht verändert. Vor Wechsel waren alle sieben Vergleichsstores leer. Bereits gültige ältere Vergleichsaufträge wurden zusätzlich auf unveränderte Lesbarkeit geprüft; keine allgemeine Garantie für beliebige direkte Alt-Store-Eingaben.

## Fünferpaket für einen anderen Windows-PC

[ZIP](C:/Users/Hubert111/Documents/Brainpower/builds/RadiWorks-Portable5-0.3.0-rc1.zip) · [Kurzstart](C:/Users/Hubert111/Documents/Brainpower/builds/RadiWorks-Portable5-0.3.0-rc1/KURZSTART.md) · [SHA-Datei](C:/Users/Hubert111/Documents/Brainpower/builds/RadiWorks-Portable5-0.3.0-rc1.zip.sha256)

Version **Portable5 0.3.0-rc1**, Engine weiterhin0.2.0; ZIP **201,223,708 Bytes** (~192MiB), entpackt630,300,719Bytes (~601MiB), **18,505 Dateien**. ZIP-CRC und SHA aller Payloaddateien wurden aus dem Archiv rückgelesen; finale Archiv-SHA erneut bestätigt:

`249af06ede3065a70f3c295f6218784313317a0a449033e8e81fc01f0d03772d`

Enthält eingebettetes CPython3.13.7x64, Anwendungs-/CPU-Abhängigkeiten, versionierten Katalog und Clarke-Daten, Herkunfts-/Lizenzdateien sowie Start-/Stop-/Statuswerkzeuge. **Keine bestehenden Fälle, Keys oder Nutzerhomes.** Fünf getrennte Homes/Scopes; fünf private Fernetkeys erst beim Zielstart unter dem dortigen LOCALAPPDATA, nicht im Paket. Defaultports8103–8107, Count1–5 und anderer Portblock möglich. Start-5.cmd aus Explorer/eigenständiger PowerShell ausführen; kein Codex oder installiertes Python erforderlich. Vollständig entpacken auf lokales NTFS, nach Erststart nicht unkontrolliert verschieben. Geordneter Stopp/Neustart erhält eigene Daten. Es wird kein Autostart/Scheduler installiert.

Windows10/11x64 benötigt zusätzlich **Microsoft VC++v14x64**; Vorprüfung vorhanden, keine automatische Installation oder Kopie von System-DLLs. [Offizielle Laufzeit](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170). Nach erfüllten Voraussetzungen offline über Loopback betreibbar. Start/Stop verifiziert viele Dateien und kann auf diesem Rechner mehrere Minuten dauern: einmal auslösen, Meldung abwarten. Fünf Instanzen sind kein Versprechen für fünf gleichzeitig laufende CPU80k-Aufträge. Nur private administrative Tests mit erfundenen Fällen; öffentliche Datenlizenz/Clarke-Rechte nicht vollständig verifiziert.

## Verifikation und Grenzen

| Prüfpaket | Ergebnis |
|---|---|
| Vollständige CPU/API-Suite | **679 bestanden**,3 bekannte Windows-Skips,0 Fehler/Fehlschläge (682 gesamt) |
| Exakte Katalog-/Altjobprüfungen |6 bestanden;5 davon bereits in der vollen Suite enthalten,1 zusätzliche Altjobprobe |
| Servicewrapper |19 Lifecycleprüfungen bestanden; Wrapper seitdem unverändert |
| Wirklicher Offline-Payloadbetrieb |5 leere isolierte Instanzen aus ZIP, Pfad mit Leerzeichen/Umlaut;5 Originalanalysen erfolgreich |
| Fachlicher TCP-Lauf |21er-GV, virtueller Broadcast isoliert/gestoppt, getrennter21×80000CPU-Auftrag erfolgreich; Original unverändert, gleiche Anfrage kein Duplikat |
| Browser |11 lesende Prüfungen auf8120; keine Schreibrequests, Originalstandard/History/21 Vergleichszeilen geprüft |
| Stop und Neustart |5 saubere Stopps;5 unveränderte Fallbestände, fertiger Vergleich erhalten, keine Duplikate; anschließend alle Testports8120–8124 sauber beendet |
| Schlüssel/SQLite |5 getrennte externe Testkeys;5 Test-SQLite integrity_check=ok |
| Dauerübernahme |7 aktuelle Quellen/Listener/Fallbytevergleiche sowie8 unveränderte aktivierte Taskdefinitionen |
| Zweiter PC / frisches Windows |**Noch nicht tatsächlich abgenommen** |

Belege liegen in [`rw-portable5-acceptance-20261005`](C:/Users/Hubert111/Documents/Brainpower/runtime/rw-portable5-acceptance-20261005): CPU_FULL_FINAL.xml, EXACT_ALL_FINAL.xml, ARCHIVE_VERIFIED.json, TCP_EXERCISE.json, TCP_RESTART.json, CLOSED_STATE_VERIFIED.json, PORTABLE_BROWSER_FINAL.json, LIVE_FIXED_VERIFIED.json, LIVE_FIXED_AUTHORITY.json, LIVE_FIXED_BACKUP_TARGET.json und LIVE_FIXED_RESUME_FINAL.log. Frühere fehlgeschlagene Harness-/Wartungsanläufe sind erhalten; sie werden nicht als erfolgreiche Abnahme gezählt.

## Sicherung und nächste Gates

Geschlossener privater Datencheckpoint: [private-before-fixed-20261005-160515](C:/Users/Hubert111/Documents/Brainpower/runtime/rw-portable5-acceptance-20261005/private-before-fixed-20261005-160515/RESTORE.md), **671 Payloaddateien/247,710,510Bytes**, SHA-Rückleseprüfung, **7 SQLite-Prüfungen erfolgreich**. Owner/SYSTEM-ACL; externe Keys nicht kopiert. Begrenzter Code-/Betriebscheckpoint [RadiWorks-C23-Portable5-20261005-162759](C:/Users/Hubert111/Documents/Brainpower/checkpoints/RadiWorks-C23-Portable5-20261005-162759/RESTORE.md) sichert aktuellen Release, Startwerkzeuge, Konfigurationen ohne Schlüsselinhalt, Tests und Nachweise; ZIP/privater Datencheckpoint bleiben getrennte verifizierte Artefakte. Dies ersetzt kein vollständiges Governors-/Aurelia-/F:-Backup.

Rollback: nie ältere Fälle/Journale/DB über neuere Daten schreiben. Rückkehr zum alten Vergleichsreader nur, wenn nach der Korrektur **keine neuen Vergleichsaufträge** erzeugt wurden; andernfalls korrigierten Reader behalten und vorwärts reparieren. Immer zuerst eigene Writer/Hosts kontrolliert beenden.

| Phase | Stand |
|---|---|
| C23-Übernahme 8103–8109 |100% dieser technischen Übernahme |
| Portable5 Bau und lokale Funktionsabnahme |100% des begrenzten Prüfpakets |
| Persönliche C3-/Zweit-PC-Abnahme |offen, kein seriöser Gesamtprozentsatz |
| Kanonischer RadiWorks-/Modul_Templates-/Aurelia-Abgleich |vorbereitet, abschließende Synchronisation offen |
| Vollständige F:-Projektsicherung/Restoreprobe |offen, nach Abnahme/Quellenabgleich |
| Aurelia S4.8 |0% Freigabe |

Nächster Schritt: privater Zweit-PC-Test und persönliche C3-Probe; anschließend gezielter Quell-/Template-/Adapterabgleich und vollständige zeitgestempelte Governors-/Aurelia-Sicherung einschließlich der vereinbarten Konfigurationen. Erst danach weitere Modulvorbereitung bzw. gesonderte Entscheidung zuS4.8. Kameranachweis, Plattformmandantenautorität/CPU-Quotas/Hostvertrag bleiben gesonderte offene Gates.

Tatsächlich verwendet: Root für Integration/Betriebsprüfung; **Luna6/max** für begrenzte Paketarbeit und Dokumentationsprüfung, **Astra6/medium** für unabhängige Produkt-/Übernahmereviews. Betreibergewählte Chatleitung Sol6.1/high; kein Runtime-Modellnachweis oder gemessener Tokenersparnisclaim. Hermes-Anwendungsrouting unverändert.
