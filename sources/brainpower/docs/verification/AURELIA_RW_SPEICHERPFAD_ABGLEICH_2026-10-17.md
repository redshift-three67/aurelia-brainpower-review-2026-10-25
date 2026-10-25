# RadiWorks: statischer Schreibpfad- und Transaktionsabgleich

Stand 17.10.2026. Dieser Bericht ergänzt den [begrenzten Quellabgleich vom 16.10.](AURELIA_RW_SPEICHERZULASSUNG_QUELLPRUEFUNG_2026-10-16.md). Kein Produktpatch, keine Laufzeitprüfung und keine Security-Schließung.

## Quellenbindung und Methode

- Unabhängiger Pilotcheckout `runtime/rw-pilot-session-fix-20261016`, HEAD `d1eb34260179a499e2b0362bf609ce96957b78aa`; beim Inventarlauf keine Änderungen an versionierten Dateien.
- [Inventar](AURELIA_RW_SPEICHERPFAD_INVENTAR_2026-10-17.json): 59 Python-Produktdateien mit SHA256, 140 syntaktische Kandidaten für I/O/Transaktionen und 19 Aufrufe von `atomic_json_replace`; Pilotentry separat gehasht. Inventar-SHA256 `7a3dc6758b9ea34eebdafd9cf8b698564a18afae16eace7f94ec5f260bac3b41`.
- AST ohne Produktimporte/-ausführung; anschließend gezielte Prüfung der Aufrufer, Transaktionsfolgen und Start-/Hintergrundpfade. Ergänzender Namensabgleich erfasste insbesondere `json.dump` in `persistence.py:64` und `core/catalog_release.py:106`, die nicht im ursprünglichen primitiven Kandidatensatz standen.
- 140 Kandidaten sind weder 140 Writer noch 140 Fehler: enthalten sind Lesezugriffe, SELECT, Stringersetzungen und stdout/Pipes. Statischer Namensabgleich beweist keine beliebige dynamische/native I/O-Abdeckung. Hostlogs, Buildcache und fremde Prozesse liegen außerhalb dieses Produktinventars.

## Ergebnis für den Schutzentwurf

| Bereich | Geprüfte Grenze / Konsequenz |
|---|---|
| JSON / Bilder | Temporäre Datei, Datei-fsync und Replace neben dauerhaftem Zuwachs zählen. Verzeichnis-fsync ist in `persistence.py:38–49` best effort; erfolgreicher Readback beweist keine Stromausfalldauerhaftigkeit. Bild-Deduplikation ersetzt keine Begrenzung paralleler Uploads. |
| Mehrdatei-Recovery | Marker enthält vollständige Zielzustände und wird mehrfach geschrieben. Vorher-/Nachher-Digestprüfung bindet Zielersatz; Budget muss die ganze Operation vor ihrem ersten Marker umfassen. Kein pauschales Löschen oder unbegrenzter Recovery-Bypass. |
| Originalanalyse | Zulassung vor Journalanlage und erstem Draw; Commit des Zufallsjournals liegt vor Draft-/Fallpersistenz. Reines Instrumentieren des JSON-Helfers kommt dafür zu spät. |
| Persönliche Analyse / Vergleich | Seed-Freeze und SQLite-Auftragsannahme sowie Dispatch/Endstatus getrennt betrachten. Beide Stores brauchen Begleitdatei-/Transaktionsbudget. Controllerkonstruktion speichert nur Pfade/Locks; Storeinitialisierung beim Start unter Runtime-Lease. |
| Broadcast / Auto / Watchlist / GV-Beobachtung | Annahme, Zufallscheckpoint, Queueaufnahme, fortlaufende Checkpoints und Abschluss unterscheiden. Vollständige Draft-/Statusdokumente werden erneut geschrieben. Stoppen/Unterbrechen kann selbst Persistenz brauchen. |
| Fall / Stick-Pad / Profil / Einstellungen | Fachliche Locks und Versionen erhalten. Fallaktivierung/Zuletzt-Index und ältere Settings-Getter/-Setter können mutieren. Fehler darf keinen erfolgreich gespeicherten Zustand vortäuschen. |
| Start / Kataloghilfen | Bootstrap und direkte Staging-/Katalogwrites liegen außerhalb des JSON-Helfers. Recovery und interrupted-Markierungen liegen vor Freigabe neuer Arbeit, brauchen aber selbst Platz. |
| Leseähnliche Randfälle | Broadcastvorschau kann Legacy-Fallidentität speichern. Persönliche GETs mutieren keine fachliche Jobzeile, nutzen aber `BEGIN IMMEDIATE`; physische SQLite-Effekte bleiben ungeprüft. RAM-Entropieimport und Script-ANALYZE sind keine zusätzlich belegten Dateispeicher. |

Genaue Aufrufer, Zeilen und vorgeschlagene Zulassungsgrenzen stehen einmalig im [Schutzentwurf](../superpowers/specs/2026-10-17-radiworks-speicherschutz-entwurf.md). Die geprüften Quellen beweisen noch keine ausreichende Kapazität oder sichere Fehlerbehandlung unter echter ENOSPC-/Abbruch-/Konkurrenzlast.

## Unabhängige Prüfung und nächster Schritt

Luna/max prüfte begrenzt die Analyse-/SQLite-/Entropie-/Auto-Aufrufer. Astra/medium prüfte den Entwurf und verlangte drei Präzisierungen: alle R1-Schreibflächen und Ausgaben begrenzen, Sichtbarkeit von Datenträgerdauerhaftigkeit unterscheiden und keine garantierte R2-Spitzenreserve aus wenigen Messpunkten ableiten. Diese Punkte sind eingearbeitet. Der abschließende Delta-Review fand keine verbleibenden Blocker in genau diesem Korrekturbereich; nur Dokumentprüfung, kein Nachweis technischer Durchsetzung und keine Aktivierungsfreigabe oder Befundschließung.

Abschließender lokaler Nachweis: alle 59 Produktdateien und der Pilotentry entsprechen erneut ihren Inventarhashes, HEAD unverändert und versionierte Pilotdateien ohne Änderungen. Inventarhash, neue Dokumentverweise und Platzhalterprüfung erfolgreich. Keine Produktimporte/-tests oder Serveraktionen für diesen Dokumentationsblock.

Nächster Block ist R1 aus dem verlinkten Entwurf: additive, synthetische und begrenzte Linux-Fehler-/Messproben nach Prüfung des schriftlichen Entwurfs durch den Betreiber. Noch kein R1-Test ausgeführt. Erst danach konkrete Eingangsgrößen-/Spitzenbedarfsverträge und Implementierungsplan für R2; R2 bleibt inaktiv. Keine Änderung der Windows-Dauerinstanzen, bestehenden Linux-Vorschau, Analysealgorithmen, Server-/Websitebudgets, Modul_Templates oder zentralen Datenbank. Kein neuer Cloud-Scan beauftragt.
