# P3 – Bericht-Dateisystemreferenzen, 11.10.2026

Zwei frische korrigierte Läufe: jeweils **12 bestanden, 0 Fehler/Fehlschläge/Skips**. Leitung implementierte und führte aus; Astra6/medium prüfte den Werkzeugscope, beide Baselines und die Ergebnisgrenzen unabhängig. Keine Produktänderung.

| Vertragsbereich | Beobachtung |
|---|---|
| Zwei synthetische Roots | Gleiche relative Dateien erhalten unterschiedliche standortgebundene IDs; Client-/Session-/Pfadzuordnung stimmt |
| Inhaltsrevision | ID bleibt gleich; Validate/Preview lesen aktuellen Inhalt und aktuelle Größe. Die ID ist kein Inhalts-/Versionshash |
| Fehlende Datei / unbekannte ID | Sauber abgewiesen; frischer Index entfernt die fehlende Datei |
| HTML-Vorschau | Getestete Script-/Iframe-/Eventattribute entfernt; kein umfassender Browser-/XSS-Nachweis |
| JSON-Vorschau | Scoreanzeige auf drei Dezimalstellen, gespeicherte Originaldatei bleibt bytegleich |
| Text/PDF | Textvorschau begrenzt; PDF liefert nur Dateiverweis, keine geprüfte PDF-Darstellung |
| Download | Echter Windows-Dateihandle liefert synthetische Bytes; Stream danach geschlossen |
| Traversal / Rootidentität | Ungültige Komponenten vor nativer Öffnung abgewiesen; falsche erwartete Rootidentität mit echtem Handle abgewiesen |
| Streamlänge | Synthetische BytesIO-Fälle: Unterlänge abgewiesen, Überlänge auf deklarierte Länge begrenzt; Streams geschlossen |

Genau drei erfasste Originalmodule `apps/web/display_scores.py`, `report_handles.py`, `reports.py` mit unveränderten Bytes kompiliert; keine Produktinitialisierer. HEAD `151e2bb0a69d49677a0b1e40e0bffd0f172d34c4`, tracked-only Status und Source-/Harnesshashes vor/nach sowie zwischen den erfolgreichen Läufen gleich. Leitung hat aktuelle Quellen-/Werkzeughashes erneut nachgerechnet.

Erstlauf: 11 erfolgreich, 1 Werkzeug-Importfehler (`_strptime` bei Datumsformatierung), 0 Skips; unveränderte Bindung. Der Filter wurde um dieses Python-Standardmodul ergänzt. Ursprüngliche Baseline und Fehlbeleg bleiben erhalten; v2-Baseline vor korrigierter Ausführung unabhängig geprüft. Kein Produktfehler aus dem Guardfehler abgeleitet.

Belege: `checkpoints/Aurelia-P3-Morphic-Report-Tests-20261011/`; Erstbeleg, zwei erfolgreiche Ergebnisse, beide Review-Baselines und Werkzeuge. Tatsächliche native Öffnungen werden protokolliert und durch einen vorgeschalteten synthetischen Scratch-Pfadfilter an die unveränderte Windows-Implementierung delegiert. Namespacepakete werden ausschließlich im Prüfprozess angelegt.

**Grenzen:** Keine OS-Sandbox oder vollständige Prozessüberwachung; allgemeine Python-Lesezugriffe und ctypes sind nicht global isoliert. Nur der geprüfte bekannte Quellweg mit synthetischen Roots. Kein Reparse-/ADS-/Race-/ACL-/Crash-/Linux-Nachweis, keine HTTP/Auth/Tenant-/CLI-/Writer-/Job-Ende-zu-Ende-Abnahme. Zwei verschiedene Root-IDs belegen keine Mandantentrennung; der Index gruppiert anhand der Pfadkonvention. Produktive Roots, Klienten und laufende Jobs wurden nicht erfasst. Kein vollständiger Backup-/Restore-Nachweis.

Für P4/P5 festhalten: Dateistandort, fachliche Sitzung und unveränderliche Inhaltsversion sind verschiedene Bindungen. Die zentrale Struktur muss Archivversionen und autorisierte Mandanten-/Klientenzuordnung gesondert vorsehen; dieses Ergebnis implementiert keine neue Datenbankstruktur und ersetzt keine Entscheidung.

Nächster P3-Scope: verbliebene Writer-/Registry-/Restore-Verträge und RF-E1. P0/P1/P2 bleiben getrennt offen; danach vollständige siebenmodulige P4-Matrix mit Aurelia/Modul_Templates vor P5 zentraler Datenstrukturentscheidung. Keine Live-/Cloud-/Office-/WSL-/Routing-/normative Modul_Template-Änderung oder neue F:-Vollsicherung.
