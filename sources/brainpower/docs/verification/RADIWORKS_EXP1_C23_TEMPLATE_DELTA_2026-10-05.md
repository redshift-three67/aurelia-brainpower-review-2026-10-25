# RadiWorks EXP1-C2/C3 — vorbereitetes Modul-Template-Delta

Stand 05.10.2026. Nur Vertragsvorbereitung im Governor-Arbeitsbereich; kanonische Modul_Templates, RadiWorks-Quellordner und Aurelia wurden nicht geändert. Maßgebliche Umsetzung: `runtime/rw-exp1c23-20261005`; technische Nachweise im C23-Abschlussbericht.

## Additiver Modulvertrag

- Standard `original`; optionaler ausdrücklich gestarteter `experimental`-Vergleich, Formel `radi144-matrix-cpu-v1`, CPU-Profil80000, höchstens21Raten je ausgewählter Originalseite. Keine automatische Moduswahl, keine automatische Original-GV-/Broadcast-Übernahme.
- Serverseitig autorisierte Originalquelle mit privatem vollständigem Katalog-/Kontext-/Baseline-/Passport-Snapshot; öffentliche `comparisonBasis={schema,id,digest}` nur Referenz. Originalzeitpunkt und nachfolgende Beobachtungen getrennt. Voraussetzung exakte Einzeldatei bis4MiB und vollständiger persönlicher Kontext. Ältere/ungeeignete Sitzungen sichtbar sperren, Originalfunktion erhalten.
- Job-ID, eigene Vergleichssitzungs-ID, sourceSessionId, requestId, parentJobId, autoritativer Scope/Fall, inputDigest, sourceDigest, Kataloghash, Kontextbindung, Formel-/Implementierungshash, Parameter und Ergebnisdigest. Werte und Namen vor öffentlichen Projektionen durch CopyGuard; keine vollständigen persönlichen Snapshots/Katalogtexte in Browserantworten.
- SQLite: queued/running/completed/failed/cancelled/interrupted. Persistenz vor Ausführung, kontrollierter Zustandswechsel, identischer requestId+Input idempotent; abweichende Bindung Konflikt. Restart unterbricht offen, kein Replay. Bewusstes Retry: neue IDs, gleiche immutable Eingabe/Elternreferenz; nach Implementierungsdrift verweigern.
- GET `/comparisons/capability`, `/comparisons/sources`, `/comparisons`, `/comparisons/{job_id}`; POST Start `/comparisons`, Abbruch `/comparisons/{job_id}/cancel`, Retry `/comparisons/{job_id}/retry`. Exakte tatsächliche Modelle/Parameter siehe `engine/src/radiworks/api/comparisons.py`; keine unversionierte externe Zusage. Mutationen verwenden bestehenden Schutzvertrag und aktuelle serverseitige Fallreferenz.
- Browser: Originalstandard, explizite Quelle/Seite/Gewicht, eigene Ergebnistabelle/Historie; Originalposition1-basiert über Seitengrenzen. Original-EW/GV am Analysezeitpunkt vs Experimental-Score/Intensität. Nach verlorener Antwort gebundene Anfrage-ID erhalten und bewusst abgleichen; keine automatische zweite Erstellung. Fall-/Ansichtswechsel müssen verspätete Antworten entkräften.
- Ein eigener CPU-Prozess pro Instanz; optionaler Dependency-Pfad `RADIOWORKS_EXP1_CPU_DEPS`, gepinntes Windows-Profil. Kein globaler Torch-Import, keine Installation in Live-venv, keine stille Modell-/Algorithmusalternative. Ressourcenbudget über mehrere Module ist noch Plattformaufgabe.

## Design, persönlicher Kontext und Plattformgrenzen

Bestehendes dunkles RadiWorks-/Aurelia-Template wird additiv verwendet; keine Neugestaltung oder Schriftersetzung in diesem Block. Bestehende Originaltabelle und Broadcast-Dock bleiben erhalten. Formfelder haben Beschriftungen und Statusmeldungen; 320/375px/Tastatur im synthetischen Browser geprüft, keine vollständige neue WCAG-/EEAT-/DSGVO-Zertifizierung.

Geburtsort ist optional ausdrücklich wählbar, Wohnort und untypisierter Altort bleiben numerisch inaktiv. Das Bild bleibt Kontext-only. Bekannte stabile Heuristiken; keine Embeddings/semantische KI oder neue Formeln. Textliche Werte dürfen keine Wirkung/Diagnose suggerieren.

Vor Aurelia: Adapter-Mandanten-/Nutzer-/Jobautorität, Speicher-/Katalogrechte, Versions-/Importvertrag, quotas und passende Linux-Abhängigkeiten konkret implementieren und prüfen. Lokaler servergebundener Scope ersetzt keine Plattform-RLS. C23-Datenmigration/Recovery müssen private comparison_sources und Vergleichs-SQLite zusätzlich zum Originalbestand erhalten. Neues S4.8-Gate bleibt geschlossen.
