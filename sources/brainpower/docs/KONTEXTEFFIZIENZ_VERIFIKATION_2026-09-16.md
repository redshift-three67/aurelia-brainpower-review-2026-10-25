# Verifikation: Effizienz bei unverändertem Medium

## Ergebnis

Medium beibehalten; Low-Automatik und häufige Umschalthinweise vorerst zurückstellen. Die aussichtsreichere Untersuchungsrichtung ist gezielter Eingabekontext. Eine zusätzliche Einsparquote ist noch nicht nachgewiesen. Keine produktive Konfiguration, Modellanbindung oder Prüfkriterien verändert; keine neuen Modellaufrufe für diese Verifikation.

## Beobachtete lokale Daten

Journal direkt mit SQLite mode=ro gelesen, ohne Store-Initialisierung. 34 Aufträge insgesamt; Verbrauchstabelle enthält vier abgeschlossene, vollständig bezifferte Modellaufrufe aus zwei scope_plan-Aufträgen. Diese vier Aufrufe sind keine vollständige Verbrauchshistorie aller 34 Aufträge. Fehlende Verbrauchsdaten bleiben unbekannt.

| Gemeldetes Modell | Aufrufe | Input | Output einschließlich ggf. Reasoning | Gesamt |
|---|---:|---:|---:|---:|
| Terra | 2 | 52.462 | 2.203 | 54.665 |
| Sol | 1 | 26.227 | 888 | 27.115 |
| Astra | 1 | 25.990 | 271 | 26.261 |
| Summe | 4 | 104.679 | 3.362 | 108.041 |

Inputanteil 96,89 %, Outputanteil 3,11 %. Das zeigt den Schwerpunkt des gemeldeten Tokenvolumens, nicht den Anteil unnötiger Daten oder die Kostenverteilung. Die lokale Verbrauchstabelle speichert keine getrennten Cache-/Reasoning-Anteile, Promptsegmentgrößen oder Redundanzbelege. Aus ihr lässt sich weder eine Euroersparnis noch eine künftige Verbrauchsreduktion berechnen. Der vorherige synthetische Low-Vergleich liegt separat und gehört nicht zu diesen vier Journalaufrufen.

## Code und Tests

- model_usage.py erfasst Aufrufe vor Versand und persistiert Status, Eingabe-/Ausgabe-/Gesamttokens und Dauer. Unbekannte/ungültige Werte werden nicht als null Verbrauch ausgegeben. Jobabfragen duplizieren keine Messwerte.
- planning_llm.py verwendet bereits _review_input(context, compact=True). Identische next_steps-Einträge werden verlustfrei referenziert; JSON-Typunterschiede und bestehende Referenzmarker verhindern unzulässige Zusammenführung. Eine reine Formatverdichtung ist damit kein neu zu erschließender Gewinn.
- Der ausgewählte unabhängige Supervisor bekommt absichtlich dieselbe Evidenz plus Plan. Diese Wiederholung sichert die unabhängige Prüfung und ist nicht als unnötiger Doppelaufruf nachgewiesen.
- Transportgrenzen stoppen zu große Kontexte vor Modellversand; keine stille Kürzung. Scope-/Vault-Drift und Projektgrenzen bleiben Prüfbedingungen.
- Verifikation: sieben Tests aus tests.test_model_usage und 27 Tests aus tests.test_plan_context_encoding, tests.test_planning_llm, tests.test_scopes, tests.test_scope_vault_drift erfolgreich. Temporäre Fixtures und simulierte Clients; keine neue Live-Evaluation und keine neue Zero-Tool-Liveprobe, da die Integration unverändert blieb.
- Automatische Reviews laut Journal aus; Supervisor Astra. Keine neue automatische Umschaltung eingerichtet.

## Empfehlung

Bestehende Verbrauchserfassung wiederverwenden. Als nächste isolierte Vorprüfung könnte eine lokale Aufschlüsselung nach Promptbestandteilen und exakt identischen Textabschnitten erfolgen, ohne Modellversand oder Kontextänderung. Zeichen-/Bytezahlen dabei ausdrücklich nicht als gemessene Tokens ausgeben. Erst nach Nachweis unnötiger Duplikate einen verlustfreien Umbau prüfen; notwendige unabhängige Quellenprüfung erhalten.

Kompakte Arbeitspaket-Übergaben sind für lange Chats plausibel, aber hier weder hinsichtlich Einsparung noch Vollständigkeit praktisch verglichen. Ein frischer Chat darf erst nach Prüfung von Auftrag, Freigaben, Entscheidungen, offenen Punkten, Dateien und Belegständen als Ersatzkontext dienen. Kein automatisches Zusammenfassen oder Weglassen wichtiger Historie allein zur Tokenersparnis. Vollständige Logs bleiben verfügbar; gekürzte Ausgaben sind keine vollständigen Nachweise. Frühere Tests nur bei weiterhin passenden Quellen und Voraussetzungen wiederverwenden.

Priorität: bestehende Medium-Konfiguration erhalten, Effizienzmaßnahmen messen statt schätzen; keine Qualitätsgarantie aus der kleinen Stichprobe ableiten.
