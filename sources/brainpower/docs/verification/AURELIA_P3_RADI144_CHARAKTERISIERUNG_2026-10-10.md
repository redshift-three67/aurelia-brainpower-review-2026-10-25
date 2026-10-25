# Aurelia P3 – Radi144: Konflikte, Teilfehler und Wiederholung

Stand 10.10.2026. Der freigegebene P3-Teilblock wurde mit ausschließlich synthetischen Dateien ausgeführt. Zwölf Charakterisierungsfälle bestätigen das beobachtete Verhalten; sie bestätigen weder Fehlerfreiheit noch eine vollständige Radi144-, P3- oder Integrationsabnahme. Formeln und Produktdateien wurden nicht geändert.

Ausgangspunkt: [Einstiege und Writer](AURELIA_P3_RADI144_EINSTIEGE_2026-10-10.md). Maßgeblicher [Gesamtplan](../superpowers/plans/2026-10-10-aurelia-module-lokale-referenz-und-datenstruktur.md); P0-Linux-Runtime bleibt offen, P1/P2-Portierung wurde dadurch nicht gestartet.

## Ausführung und Aussagegrenzen

Die zwölf Szenarien liefen zunächst durch Luna6/max und nach unabhängiger Prüfung und enger Fixture-Präzisierung erneut durch die Leitung. Der letzte Lauf endete mit Exitcode 0 am 10.10.2026 um 13:09:05 Berliner Zeit. Python 3.11.12, FastAPI 0.104.1 und Pydantic 2.13.4 wurden aus der bestehenden Radi144-Testumgebung genutzt. Alle 13 gebundenen Originaldateien waren vor/nach den Läufen SHA-gleich.

Die Services, Modelle und Schemas wurden aus ihren unveränderten Quellbytes in kontrollierte Module geladen. Die globale API initialisiert beim Import eine Rechenengine und wurde nicht importiert. Für Sequenz und Berichtregistrierung wurden fünf genaue Funktionskörper aus `app/api/resonance.py` über AST geladen; Routing-Dekoratoren wurden ausgelassen. Die Analysegrenze der Sequenz war synthetisch, PDF-Dateien waren vorab erzeugte Platzhalter. Keine Aussage über Berechnungsparität, PDF-Rendering, HTTP-Antworten oder Browserfunktion folgt daraus.

Werkzeug und Nachweise liegen unter `checkpoints/Aurelia-P3-Radi144-20261010`: `characterize_radi144.py`, `results.json`, `source_bindings.json`, `REPORT.md`. Drei frühere Fehlversuche bleiben erhalten: Windows-Scratchrechte, bereits angelegtes Fixture-Verzeichnis und eine falsche Prüfung von `str(HTTPException)` statt `detail`. Das sind Werkzeug-/Umgebungsfehler, keine Produktbefunde. Die endgültige Dateilöschprobe verwendet eine reguläre synthetische Datei; ein früherer Lauf verwendete dafür ein Verzeichnis und ist entsprechend enger aussagekräftig.

## Belegte Szenarien

| Fallgruppe | Ausgeführt | Beobachtung | Für P4/P5 mitführen |
|---|---:|---|---|
| Zwei Store-Schreiber | 1 | A und B laden denselben alten Stand; nach A-save/B-save fehlt A's Ergänzung. | Versionsvergleich, Konfliktregel oder Serialisierung, wenn mehrere Writer vorgesehen sind. Keine Aussage über tatsächliche Race-Häufigkeit. |
| Runtime-Vorlagenexport | 1 | 22 Sitzungen ergeben die letzten 21 Listeneinträge, rückwärts. Fehlender Klient: archivierter Name als Fallback, Datum/Ort leer. | Kontextrevision und Listenreihenfolge explizit halten; Export kann aktuelle Klientenstammdaten lesen und ist kein Nachweis historischer Unveränderlichkeit. |
| Berichtregistrierung | 2 | Manifest-Save-Fehler: kein Eintrag/Link; Retry erzeugt einen. Linkfehler nach Manifest-Save: erster Eintrag bleibt unverknüpft; Retry erzeugt zweite ID und verknüpft diese. | Wiederholungsidentität, Teilveröffentlichung und konsistente Datei-/Manifest-/Sitzungsbindung festlegen. PDF-Rendering und Output-Route ungeprüft. |
| Zweiter Fokus scheitert | 1 | Erste Sitzung bleibt gespeichert; Sequenzfunktion erzeugt HTTPException mit Status 500 und Ursache in `detail`. Keine HTTP-Antwort erzeugt. | Gesamtauftrag und einzelne Versuche/Fokusschritte trennen; Teilabschluss und Retry-Regeln festhalten. Engine/Formeln ungeprüft. |
| Ungültiges Lösch-Gate | 1 | Drei Stores bleiben erhalten; gated-Audit wird geschrieben. | Service-Gate von API-/Tenant-/Benutzerberechtigung unterscheiden; diese wurden nicht geprüft. |
| Löschung: Storefehler | 3 | Klient-Save-Fehler erhält alle Stores. Sitzungs-Save-Fehler: Klient entfernt, Sitzung/Artefakt erhalten. Artefakt-Save-Fehler: Klient/Sitzung entfernt, Artefakt erhalten. Die letzten beiden Retries melden `not_found` und lassen Reste zurück. | Löschziele und Fortschritt unabhängig vom bereits entfernten Klienten auffindbar halten. Keine pauschale Wiederaufnahmegarantie. |
| Löschung: Dateisystemfehler | 2 | Datei-/Verzeichnisfehler wird geloggt; spätere Schritte können weiterlaufen und `ok` zurückgeben. Restpfad bleibt auch nach Retry erhalten. | Teilfehler sichtbar, erlaubte Pfadbereiche/Eigentum und wiederaufnehmbare Bereinigung festlegen. Kein echter ACL-/Lock-Test. |
| Audit-Save-Fehler | 1 | `ok` und Audit-ID werden zurückgegeben, obwohl keine Auditdatei dauerhaft gespeichert wurde. | Zurückgegebene ID und persistierter Nachweis unterscheiden; überprüfbare Bestätigung nötig. |

Diese Anforderungen bestimmen noch keine Datenbanktechnik. Insbesondere wurden keine zentrale Schemaänderung, Migration, produktive Löschung oder Reparatur am Original ausgeführt. Eine Sicherungskopie und ein Retry ersetzen keine getestete Gesamtwiederherstellung.

## Unabhängiger Review und verbleibende Prüfungen

Astra6/medium prüfte Quelle, Harness und Ergebnisse. Die ursprünglichen Fixture-Widersprüche wurden vor dem Abschluss beseitigt; am endgültigen Ergebnis wurde keine materielle Inkonsistenz mehr festgestellt. Dieser Review ist keine Produkt- oder Architekturfreigabe.

Offen bleiben:

- Gleichnamige unterschiedliche Klienten, gemeinsam referenzierte Dateien und zulässige Pfad-/Eigentumsgrenzen. Die Quelle verwendet für Analyseverzeichnisse einen Namenssuffix; praktische API-Erreichbarkeit/Autorisierung wurde nicht abgenommen.
- Alter Writer nach Löschung, Mehrfokus-Retry, fehlende Sitzung nach PDF-Dateischreiben sowie Fehler nach erfolgreichem Dateiersatz.
- Echte Engine-/Formelreferenzen, globale Amplifier-/Request-Parallelität, HTTP/UI, CLI/PowerShell, Abbruch, Crash-Durability und Restore.
- Vollständige Workflow-/Writer-/Kontextmatrix im vereinbarten Modulumfang. Die zwölf Szenarien schließen nur diesen begrenzten Charakterisierungsblock.

Nächste Reihenfolge: diese noch offenen Radi144-Grenzen gezielt ergänzen; unabhängige RadiMorphic-Quell-/Owner-/Lease-Abdeckung und aktuelle RadiFarben-VBA-/Query-/Formularabläufe aufnehmen. Vollständige Explorer-/Thom-Laufzeitprüfung bleibt an die Linux-Testbasis gebunden. Danach gemeinsame siebenmodulige Bedarfsmatrix und Betreiberentscheidung zur zentralen Struktur; keine neue Algorithmus- oder Architekturentscheidung vorwegnehmen.

## Absicherung

Vorher-/Nachher-Dokumente und gebundene Helfer-/Abschlussnachweise: `runtime/aurelia-three-modules-20261009/reference-plan/p3-radi144-20261010-104439Z`. Der Bereich erbt private Benutzer-/SYSTEM-Rechte. Eine frühere unvollständige Dokumentkopie unter `checkpoints/Aurelia-P3-Fortsetzung-20261010-104242Z` wurde ebenfalls auf private Rechte beschränkt und bleibt als Zwischenbeleg erhalten.

Der historische Wiederaufnahme-Tail bleibt mit 291415 Bytes und SHA256 `cc8ab41933c9fb2acf8d48a985c4f840dfc566319b3039038bace91820918533` erhalten. Die 200 R6-Produktdateien werden vor/nach manifestgeprüft. Dauerinstanzen 8103–8109 und Governors 8787 werden lediglich über ihre Listener/PIDs kontrolliert; keine Home-/Klientendaten gelesen, kein Server beendet oder gestartet. Normative Modul_Templates, Produktalgorithmen, Cloudschemata und Routen bleiben unverändert. Keine neue F:-Vollsicherung oder S4.8-Freigabe.
