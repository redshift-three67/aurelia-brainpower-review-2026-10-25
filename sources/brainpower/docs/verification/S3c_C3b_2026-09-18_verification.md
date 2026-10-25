# S3c C3b – direkte abhängige Pilotänderung

Stand: 18.09.2026. Internes direktes A→B-Profil umgesetzt; C4/Oberflächen- und Gesamtabnahme separat.

## Verhalten und Nachweise

- B benötigt eigene unveränderliche H1-Zustimmung. Originalplan/H0 und effektiver H1-Stand bleiben getrennt; keine allgemeine Quellenhash-Ersetzung.
- Vorschlag, Modelltransport, eigener Test/Nachreview, Übernahme, Nachprüfung und technischer Abschluss prüfen die Bindung frisch. B erbt keine erfolgreichen Tests von A.
- Historischer A-Beleg wird am wirklichen H2-Dateistand kontrolliert. Auswahl, Adapter, Transaktion, Test-/Verify-Versuche und beide expliziten Dateibereiche bleiben gebunden.
- Jeder neuere B-Vorschlag entwertet ältere Vorschläge vor Test, Modelltransport und Übernahme. Auch ein fehlgeschlagener neuer Versuch zählt.
- Ein späterer physischer Übernahmeversuch einschließlich Rücknahme reaktiviert die alte H1-Zustimmung nicht.
- Temporäre echte A/B-Dateiübernahmen, getrennte technische Abschlüsse, H2-Journalbestätigung und Rücknahme B vor A geprüft. Upstream Modell-/Reviewbelege sind Testfixtures, kein Live-Modellnachweis.

Gezielte Regression: **204 Tests bestanden**, keine Skips, 64,823 Sekunden. Protokoll: `S3c_C3b_2026-09-18_unittest.log`. Enthalten sind Pilot-, Journal-, Folge-, Testketten-, Staging- und Hermes-Regressionen. Lokale Hermes-Probe mit `probe_only=True` bestätigt null Werkzeuge; kein echter Modellauftrag.

Unabhängiger statischer Review fand eine fehlende Prüfung auf neuere B-Vorschläge. Mit zuerst fehlschlagender Regression korrigiert; Nachreview ohne weitere konkrete Befunde. Statischer Review ersetzt keine Tests.

## Grenzen

Zwei direkte Änderungen eines erlaubten unabhängigen Piloten mit getrennten Schreibbereichen. Historische externe Vorgänger nach Quellenwechsel bleiben gesperrt. Keine allgemeine Produktketten-, Server-, NAS-, Deployment- oder Produktfreigabe. Frische Beobachtungen sind keine atomaren Dateisystem-Snapshots. C3/C4-Gesamtabschluss erst nach separater Oberflächen-/Gesamtabnahme bewerten.
