# P3 – begrenzte Backup-Referenzprüfung

Am 11.10.2026 wurden zwei frische synthetische Prüfungen durchgeführt: jeweils **14 bestanden, 0 Fehler, 0 Fehlschläge, 0 Skips**. Die Leitung hat Ergebnisse, identische Fallnamen und die aktuellen sieben Quellenhashes zusätzlich nachgerechnet. Astra6/medium hat Werkzeuge und Ergebnisgrenzen unabhängig geprüft; die vier gefundenen Werkzeugmängel wurden vor den erfolgreichen Läufen korrigiert.

| Geprüft | Ergebnis |
|---|---|
| Echter SQLite-Snapshothelper mit synthetischem Katalog | Draft und eigener Kontext erhalten, fremder Kontext nicht zugänglich; Quelle unverändert |
| Synthetisch konstruierte Manifest-/Completion-Dateien | Gültiger Vertrag akzeptiert |
| Öffentliche Restore-Ablehnungen | Bestehendes Ziel, fehlende/ungültige Completion, Zusatzdatei, Größen-/Hash-/Schemaänderung und unzulässige Aktivierungsflags abgelehnt |
| Relative und Traversal-Ziele | Abgelehnt; tatsächliche Ziele und zugehörige temporäre Dateien nicht angelegt |
| Quellenbindung | HEAD `151e2bb0a69d49677a0b1e40e0bffd0f172d34c4`; sieben Quellhashes und Harnesshashes vor/nach sowie zwischen beiden Läufen gleich |

Belege: `checkpoints/Aurelia-P3-Morphic-Backup-Tests-20261011/`, insbesondere `result-root-first.json`, `result-root-repeat.json` und die beiden `SOURCE_BINDING`-Dateien. Ein vorausgehender direkter unittest-Aufruf scheiterte vor Produktausführung am fehlenden isolierten Alias; dies war kein erfolgreicher Testlauf. Erst die beiden Guard-Runner-Läufe zählen als ausgeführte 14-Fall-Prüfung.

**Nicht abgenommen:** vollständiger positiver öffentlicher Backup-/Publish-/Restoreweg, Registrybindung, Migration, Writer-/Bericht-/Job-E2E, API/Auth, Crash-/Race-/ACL-/Ubuntu-Verhalten. Der Publishweg bindet weitere Registryfunktionen und wurde nicht durch Attrappen ersetzt. Die Manifest-Dateien wurden für diese Prüfung konstruiert, nicht durch den öffentlichen Export erzeugt.

Python-Guards sind keine OS-Sandbox. Die Beobachtung geladener Namespaces ist keine vollständige Prozessüberwachung; begrenzte Import-/Leseaussagen beruhen auch auf dem geprüften Codepfad. Kein Untracked-Inventar und keine kontinuierliche Driftgarantie. Keine Produkt-, Live-, Cloud-, WSL-, Office-, Routing- oder normative Modul_Template-Änderung.

Die Leitung implementierte und führte diesen Block aus. Astra6/medium prüfte unabhängig. Der vorgesehene Luna6/max-Worker blieb beim Initialisieren ausstehend und führte keine Berichttests aus; die Leitung übernahm dessen Scope, ohne einen Modellwechsel zu behaupten. Die Berichtprüfung bleibt offen, insbesondere die kontrollierte Ausführung des Windows-Handlewegs an ausschließlich synthetischen Roots.

Reihenfolge bleibt: übrige P3-Referenzverträge, siebenmodulige P4-Matrix mit Aurelia/Modul_Templates, danach P5-Entscheidung zur zentralen Datenstruktur. Keine vollständige Modulabnahme aus diesem Teilnachweis ableiten. Lokaler Dokumentations-/Belegprüfpunkt wird mit Vorher-/Nachherdateien und frisch verifiziertem SHA-256-Manifest gesichert; keine neue F:-Vollsicherung.
