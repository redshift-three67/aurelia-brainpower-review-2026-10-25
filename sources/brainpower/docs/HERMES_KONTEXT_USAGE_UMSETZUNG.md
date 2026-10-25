# Kontextprüfung und Verbrauch je Auftrag

Freigegebener Umfang vom 15.09.2026, auf Basis der Bestandsaufnahme.

Eine gemeinsame Prüfung verwendet die tatsächliche Transportgrenze: Hermes 95000, Router 120000 Zeichen. Grenzen sind keine Tokenbudgets. Keine stille Kürzung, Erhöhung oder Ausweichroute.

Ein lokaler Aufrufbeleg wird vor jedem über den Jobrunner gestarteten Modellaufruf gespeichert und danach mit Status sowie gültigen Provider-Tokenwerten ergänzt. Fehler/Abbruch behalten ihren Beleg; bei hartem Prozessende bleibt der begonnene Aufruf mit unbekanntem Verbrauch sichtbar. Wiederaufgenommene Aufträge ergänzen neue Belege. Die UI summiert ausschließlich diese Belege, nicht mehrfach verschachtelte Reviewberichte. Alte Aufträge ohne Belege werden als nicht erfasst angezeigt.

Unbekannt ist nicht null. Nur nichtnegative ganzzahlige Providerwerte zählen. Teilwerte werden als unvollständig gekennzeichnet. Keine Preisberechnung, keine zusätzlichen Modellaufrufe, keine Änderung der Freigaben.

## Umsetzung und Prüfung

- Gemeinsame Kontextprüfung und synthetische Grenztests für beide Transporte.
- Persistente Aufrufbelege mit normalisierten Tokens und Tests für Teilfehler, Abbruch, Wiederaufnahme und doppelte Anzeige.
- Anschluss an Jobrunner und Auftragsdarstellung; keine Rückrechnung alter Ergebnisse.
- Relevante Unit-Tests, JS-Syntax, synthetische Browserprüfung, lokale Zero-tool-Probe und Gesamtsuite.
- Keine Änderung externer Produktrepos; kein impliziter Commit oder Dienstneustart während laufender Aufträge.

## Ergebnis 15.09.2026

Implementiert: `model_usage.py` mit gemeinsamer Transportprüfung, normalisierten Providerwerten und dauerhaftem Beleg je Aufrufversuch. Jobrunner erfasst Router-/Hermes-Reviews, Plan-/Patch-/Rückfrageaufrufe, Modellchecks und Post-Test-Reviews. Store liefert `token_usage` getrennt vom fachlichen Ergebnis. Die Auftragskarte zeigt Summen, Unvollständigkeit und einzelne Modellaufrufe; erneute Darstellung verändert keine Summen. Wiederaufnahme ergänzt Belege zum selben Auftrag. Vorab abgewiesene Kontexte erzeugen keinen gestarteten Modellaufruf.

Grenzen: Fehlt nach einem Transportfehler, Abbruch oder Prozessende die Provider-Usage, bleibt sie unbekannt. Keine nachträgliche Abfrage beim Provider. Keine rückwirkende Migration alter Berichte und keine Preisberechnung. Die Zeichenlimits sind weiterhin keine tatsächlichen Kontextfenster-/Tokenmessungen der Modelle. Ein Supervisor-Preflight ist erst möglich, sobald dessen vollständiger Prompt einschließlich vorheriger Antwort vorliegt.

Prüfung: 350 Python-Tests, davon 348 bestanden und zwei ausgelassen (127,598 Sekunden). JS-Syntax und `tests/test_token_ui.cjs` bestanden. Lokale installierte Hermes-Probe mit `probe_only=True` erfolgreich, `tool_count=0`, `approval_granted=false`; keine neue Modellinferenz. Browsernavigation zur isolierten synthetischen Instanz wurde mit `ERR_BLOCKED_BY_CLIENT` abgewiesen. Visuelle Browserabnahme deshalb offen; der Darstellungs-Unit-Test ersetzt sie nicht.

Aktivierung: Live-Journal vor Neustart lokal gesichert (`artifacts/pre-token-usage-journal-2026-09-15.db`, nicht veröffentlichen). Keine aktiven/wartenden Aufträge. Governor kontrolliert neu gestartet, `/health` erfolgreich und alle 22 zurückgegebenen Aufträge mit `token_usage`. Automatische Reviews weiterhin aus, Supervisor weiterhin Sol. Testinstanz wieder gestoppt.

Browsernachprüfung nach Betreiber-Neuladen: Geöffnete Live-Seite auf Port 8787 erreichbar und live verbunden. Tab „Aufträge & Ergebnisse 22“ geöffnet; 14 historische Modellaufträge zeigen im gerenderten DOM ausdrücklich „Tokenverbrauch: nicht erfasst“. Keine neue Modellprüfung gestartet. Damit ist die Darstellung historischer Aufträge im echten Browser geprüft. Die Browserdarstellung numerischer Teil-/Gesamtwerte in der isolierten Testinstanz bleibt offen; dafür bestehen bisher Darstellungs-Unit-Tests.

Ergänzung nach ausdrücklich beauftragtem Aufnahme-/Planfortschritt: Der echte Planauftrag `bf85cc5da30e404e9ef98b5c958edb76` liefert im gerenderten Browser-DOM 52.877 Eingangs-, 1.890 Ausgangs- und 54.767 Gesamttokens bei zwei Aufrufen. Die Werte stimmen mit den Aufrufbelegen überein. Damit ist auch die numerische Gesamtanzeige im Browser beobachtet. Der fachlich blockierte Plan wurde nicht als Strategie übernommen; erfolgreicher Transport und fachliches Urteil bleiben getrennt. Kein zusätzlicher Modelllauf nur für die Anzeige.
