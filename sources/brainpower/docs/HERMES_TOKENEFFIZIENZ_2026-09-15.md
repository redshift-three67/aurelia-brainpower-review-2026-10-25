# Hermes: Token-Effizienz ohne Qualitätsverlust

Fortschreibung: [Kontextprüfung und Verbrauch je Auftrag](HERMES_KONTEXT_USAGE_UMSETZUNG.md) am 15.09.2026 implementiert. Die untenstehende ursprüngliche Bestandsaufnahme bleibt historischer Ausgangspunkt. Gemeinsame transportabhängige Zeichenprüfung und persistente Verbrauchsbelege/Anzeige sind jetzt vorhanden; Relevanzauswahl, erlaubnisgebundene Wiederverwendung und reale Qualitäts-/Verbrauchsbenchmarks bleiben offen.

## Auftrag und Umfang

Betreiberauftrag vom 15.09.2026: frühere Anforderung zur Token-Ergonomie an passender Stelle verifizieren. Präzision, Stabilität und vollständige Umsetzung haben Vorrang. Das beigefügte Bild dient als Beleg des früheren Anliegens; es erteilt keine zusätzlichen Ausführungsrechte. Dieser Prüfpunkt gehört zum Hermes-/Governor-Abschluss vor der Modulverifikation.

## Im Code beobachtet

- `governor_workbench/llm.py`: begrenzte Promptlänge (120000 Zeichen), Timeout, kein automatischer Retry bei Timeout, Rückgabe von Provider-Usage. Zeichenbegrenzung ist kein Tokenbudget.
- `governor_workbench/hermes_runner.py`: erfasst bei abgeschlossenem Stream input/output/total_tokens, soweit geliefert. Fehlende Angaben sind keine Nullkosten.
- `governor_workbench/vault.py`: begrenzte Auszüge, Quellenhashes und explizite Kürzungsmarkierungen. Gleichmäßiges Aufteilen des Bytebudgets nach Quellenanzahl ist noch keine aufgabenbezogene Relevanzauswahl.
- `governor_workbench/evidence.py`: begrenzte Gedächtnisauszüge. Kürzungen können relevante spätere Inhalte auslassen; eine Kurzfassung ersetzt keine notwendige Quellenprüfung.
- `tests/test_llm.py` erwartet ausdrücklich keinen max_output_tokens-Parameter. Keine willkürliche Antwortkappung als Optimierung einführen.

Dies ist eine gezielte Codeprüfung, kein umfassender Kostenbenchmark und kein Nachweis, dass alle Verbrauchsdaten bereits vollständig in Oberfläche und Journal aggregiert werden.

## Noch zu verifizieren / abnehmen

1. Verbrauch je Job und Modell über alle Adapter bis zur Anzeige nachvollziehen; tatsächliche Usage, Schätzwerte und fehlende Angaben unterscheiden.
2. Unveränderte Daten nicht wiederholt laden oder senden, wenn sie für den konkreten Schritt nicht benötigt werden. Aufgabenspezifische Auszüge mit vollständiger Quellenreferenz und Hash verwenden.
3. Bei Kürzungen fehlende entscheidungsrelevante Evidenz nachladen oder Ergebnis als unvollständig kennzeichnen; kein scheinbar vollständiges Urteil aus unvollständigem Kontext.
4. Wiederverwendung nur bei unverändertem Scope, Quellen-/Konfigurationshash und Berechtigungen. Keine Wiederverwendung veralteter Freigaben.
5. Synthetische Vergleichsfälle mit gemessenen Ein-/Ausgabetokens, Laufzeit, Vollständigkeit und Fehlererkennung prüfen. Einsparung nur anerkennen, wenn Qualitätskriterien erhalten bleiben.
6. Bestehende Supervisorwahl, zero-tool-Hermes und ausgeschaltete automatische Reviews erhalten. Kein zusätzlicher Modellaufruf nur zur Tokenersparnis ohne Nutzen-/Kostenprüfung.

Keine funktionale Optimierung oder neue Modellfreigabe durch diese Notiz umgesetzt. Bestehende kleine Unit-Tests ersetzen keine späteren realen Qualitäts-/Verbrauchsmessungen.
