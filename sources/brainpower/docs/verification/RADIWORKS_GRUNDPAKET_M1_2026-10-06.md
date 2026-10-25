# RadiWorks Grundpaket – M1, 2026-10-06

M1 abgeschlossen: verifizierter Ausgangspunkt für das vom Betreiber freigegebene Grundpaket M1–M6. Keine Umstellung der Dauerinstanzen, kein Abschluss des Gesamtpakets.

## Nachweise
- C23: 131 Produktdateien, Manifest SHA-256 `9ba23c5dbfe856fc6887abf87fe13aba302ec362c1cdd432654d8fa30fe50694` vollständig geprüft.
- Entwicklungsbasis: Backoff-Manifest `60ca99f2fcb5e2a02cda2e7a81983e6b01a26edc4ffed8f981616d00d08b806a`, ausschließlich `engine/src/radiworks/entropy.py` gegenüber C23 geändert. Fehlerpause/Quelllock bereits separat getestet; noch nicht live übernommen.
- Kandidat `runtime/rw-basepackage-20261006`: genaue Produktkopie der Backoff-Basis plus 49 Testdateien. Entwicklung außerhalb Liveports.
- F:-Archiv `F:/Hauptprojekt/Aurelia/RadiWorks-Grundpaket-M1-20261006-131224`: 1.679 manifestierte Dateien nach Kopie erneut per Hash gelesen; sieben SQLite-Backups jeweils `PRAGMA integrity_check = ok`. Quellprodukt erneut unverändert bestätigt.
- Frische Normalbaseline: 686 Tests, 667 bestanden, 19 übersprungen (16 getrennte CPU-Tests, drei Windows-Symlink-Privilegien), null Fehler/Fehlschläge.
- Gepinntes CPU-Profil: 45 Tests bestanden, null übersprungen/Fehlschläge/Fehler.
- Vorhandene Starlette/httpx-Deprecation-Warnung; hier keine Abhängigkeiten umgestellt.
- Sieben `/ping`-Antworten 8103–8109: HTTP 200 vor Sicherung. Keine Live-Fälle abgefragt oder verändert.

## Begrenzungen
Die Sicherung enthält Produkt, Kataloge, Startkonfigurationen, private gespeicherte Dokumente und konsistente Einzel-SQLite-Snapshots. Sie ist kein global atomarer Laufzeitschnappschuss: JSON/Journale sind separat erfasste Dateistände, aktive Broadcasts im RAM und Laufzeit-Leases/Logs sind ausgeschlossen. Wiederherstellung muss den dokumentierten Recovery-Abgleich verwenden. Der externe Fernet-Schlüssel wurde ausdrücklich nicht kopiert; verschlüsselte Journale benötigen ihn weiterhin. Keine generelle Windows- oder Aurelia-Gesamtsicherung behauptet.

## Fortschritt dieses Grundpakets
| Phase | Stand |
|---|---|
| M1 Ausgangssicherung und Baseline | 100 % der abgegrenzten Prüfpunkte |
| M2 Titel und BC1-Zielbindung | begonnen; noch nicht abgenommen |
| M3 Auftrags-RNG | offen |
| M4 persönlicher Vollweg | offen |
| M5 Vier-Modi-Abnahme | offen |
| M6 Quell-/Template-/Portable-Sync | offen |
| Aurelia S4.8 | 0 %, keine Integrationsfreigabe |

Logs: `runtime/rw-basepackage-20261006/evidence/m1-baseline.{log,xml}`, `m1-cpu-baseline.{log,xml}`, `M1_CHECKPOINT.json`. Ausführung: Root und begrenzte Luna-Bestandsprüfung; Astra-Vertragsprüfung für BC1 separat im Gang. Die Ergebnisse prüfen Softwareverhalten, keine Klientenwirkung.
