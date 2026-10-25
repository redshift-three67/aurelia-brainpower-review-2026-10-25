# RadiWorks R6.2 – Quellabgleich, Start5 und Gesamtsicherung

Abgeschlossen: 2026-10-09T02:12:37.341113+02:00. Keine S4.8-Integrationsfreigabe.

| Schritt | Ergebnis |
|---|---|
| R6.1 Dauerinstanzen | 8103–8109 mit R6; laufende Instanzen bei diesem Sicherungsblock nicht neu gestartet. |
| R6.2 Quelle / Templates | 200/200 Produktdateien gleich; drei additive Template-Nachträge; 82 gezielte Tests und 37 JS-Syntaxprüfungen bestanden. |
| Start5 0.4.0-rc1 | 18.574 Payload-Dateien SHA-/CRC-geprüft; fünf isolierte Instanzen, Fall-/Medienpersistenz, Stop/Restart und vier Analyse-/Zufallskombinationen auf 13 Raten bestanden. [Paketbericht](../../runtime/rw-r6-portable5-20261008/REPORT.md). Neue physische Zweit-PC-Abnahme bleibt getrennt. |
| Gesamtsicherung | Beide deklarierten Projektarchive vollständig rückgelesen, SQLite geprüft, stabile Quelldrift 0. |
| Begrenzte Restoreprobe | 400 archivierte Produktdateien, Paket-ZIP und Codex-TOML geprüft; drei ausgewählte SQLite-Kopien tatsächlich wiederhergestellt und auf Integrität geprüft. Kein Vollsystemrestore. |
| S4.8 | 0 % / keine Freigabe; DB-/Host-/Mandantenvertrag gesondert. |

Paket: `C:\Users\Hubert111\Documents\Brainpower\builds\new-version\RadiWorks-Portable5-0.4.0-rc1.zip`, SHA-256 `df5eeb82c7bdbea242f127196cd8a3ab58bae205d5d6e9159022327dfde89890`.

Die alte Start5-Version bleibt erhalten. Der historische lokale Schlüsselroot für 0.3/0.4 ist bewusst identisch; keine automatische Fallmigration. Das verteilbare ZIP enthält keine bestehenden Fälle oder Schlüssel.

## Private Archive

- Governors: `F:\Hauptprojekt\Governors\20261009-005558`; 300543 manifestierte Dateien, 6807 SQLite-Snapshots geprüft; Manifest-SHA `60c257c8ce8b26aeb0b57fbe2d022e2da171ea762a87fc9a733b00a3e3113e74`.
- Aurelia: `F:\Hauptprojekt\Aurelia\20261009-005558`; 274555 manifestierte Dateien, 27 SQLite-Snapshots geprüft; Manifest-SHA `76a73f093d63cdded0b7e07cfbc65d6086f30111a4eeebaf22fa61f82de58859`.

Die Archive enthalten Einzel-Online-Snapshots und zeitgestempelte Live-Logpräfixe, keine gemeinsame atomare Momentaufnahme. Generierte Abhängigkeiten/Caches, aktive nicht wiederherstellbare Locks und bekannte unlesbare historische Quellen sind ausdrücklich in OMISSIONS.json aufgeführt. Kein frischer Remote-Linuxexport und kein Windows-Diskimage. Private Schlüssel/Auth-/Session-/Falldaten liegen ausschließlich im geschützten Archiv.

Zuerst COMPLETE.txt, VERIFY.json, MANIFEST.jsonl, PROJECT_STATUS.md, RESTORE.md und completion/ lesen. Abschlussbelege wurden nach der Kernarchivprüfung separat ergänzt und haben einen eigenen rückgelesenen Manifestnachweis. Kernmanifest und VERIFY bleiben unverändert.

Nächster Entscheidungsblock: neue Start5-Zweit-PC-/Betreiberabnahme und ausführliche Aurelia-Datenbankstrukturplanung; weitere Module und S4.8 erst gesondert. Chat-Helfer: Luna6/max (Start5), Astra6/medium (Manager-/Archivreview). Aktives Leitmodell wird nicht aus Konfigurationsdateien abgeleitet.
