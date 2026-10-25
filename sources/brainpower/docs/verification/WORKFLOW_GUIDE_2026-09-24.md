# Schrittführung — Abschluss Block 3b, 24.09.2026

Die bestehende Projekt-/Gruppenansicht zeigt jetzt vier Phasen: Umfang, Aufnahme, Planung und bewusste Freigabe. Kontext, nächster Bedienweg und Sperrgrund stehen zusammen. Höchstens ein vorhandenes, bereits aktiviertes Ziel erhält eine Akzentumrandung. Text beschreibt denselben Hinweis ohne Farbe. Keine automatischen Klicks, Fokuswechsel, Modellaufrufe oder neuen Ausführungsrechte.

Die Führung liest vorhandene Aktualitäts-/Aufnahme-/Planungszustände und die bestehenden Controls. Gruppen sind ausdrücklich als Gruppenplanung ohne allgemeine Gruppenausführung beschriftet. Strategieübernahme und Schrittauswahl bleiben getrennte Entscheidungen. Die letzte Phase zeigt den Plan zur Prüfung, keine pauschale Aufforderung zu dessen Annahme.

## Prüfung

- `tests/test_workflow_guide.cjs`: 13 Entscheidungsfälle plus Rendering für gesperrte/erlaubte Ziele, laufenden Umfangsabruf und fehlenden aktuellen Strategiestatus. Zunächst rot vor Implementierung; nach Reviewbefund erneut rot für fehlende Strategie, danach vollständig grün.
- Unabhängiger begrenzter Review: Kandidaten allein reichten zunächst für Phase 4. Korrektur verlangt auch den aktuellen Strategieladestatus, passend zur bestehenden Übernahmesperre. Keine weitere konkrete Lücke gemeldet; Reviewer führte keine Tests selbst aus.
- Bestehende Scope-/Entwurfs-, Routing-, Token- und Änderungsketten-JavaScript-Prüfungen sowie JS-Syntax erfolgreich. Kein Backend geändert; Python-/Pilotnachweise aus den vorherigen Berichten werden wiederverwendet, keine neue Gesamtsuite behauptet.
- Echter Browser gegen isolierte synthetische Fixture auf Port 8794: Phase 1 ohne Umfang; Phase 2 mit Mitgliedsauswahl und vier unbestätigten Feldern; nur das bereits zulässige Bestätigen wird hervorgehoben; Wechsel zu B zeigt Phase 3; explizites Laden und Wählen des synthetischen Kandidaten zeigt Phase 4. Es wurde keine Aufnahme, Strategie oder Schrittauswahl bestätigt und kein Modellauftrag ausgelöst.
- Sichtprüfung im dunklen Layout: Führung und Akzentfläche lesbar, bestehendes Layout erhalten. Eine zunächst veraltete CSS-Darstellung wurde durch versionierte Stylesheet-Adresse behoben und im Screenshot danach sichtbar bestätigt. Keine gesonderte umfassende Mobil-/Barrierefreiheitsabnahme.

## Übergabe

Die drei Kernblöcke des bestätigten Abschlussplans sind im dokumentierten lokalen Funktionsumfang umgesetzt und geprüft. Nächster Schritt ist die gemeinsame Funktionsabnahme/Besprechung, keine automatische Gesamtproduktfreigabe. Allgemeine Gruppenmatrix-Ausführung, neue Aurelia-Adapter, vollständige Servermigration und neutrale Windows-Ausgabe samt Fremd-PC-Abnahme bleiben separate Arbeiten. Keine neue Live-Provider-Evaluation durchgeführt. Astra/Medium und ausgeschaltete automatische Reviews bleiben erhalten. Reasoning Medium, kein Low-Wechsel offen.
