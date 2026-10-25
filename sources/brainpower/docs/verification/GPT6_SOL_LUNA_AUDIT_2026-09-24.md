# GPT-6 Sol xhigh und GPT-6 Luna max — Integrationsprüfung

Betreiberauftrag: vor der gemeinsamen Hermes-Funktionsabnahme zuerst die beiden ausdrücklich benannten Modell-/Reasoning-Kombinationen für Codex-Chat und Hermes prüfen. Keine Änderung der Standardmodelle oder gespeicherten Reasoning-Auswahl in diesem Audit.

## Offizielle Unterstützung

Die offiziellen Modellseiten bestätigen die IDs `gpt-6-sol` und `gpt-6-luna` und für beide unter anderem `xhigh` und `max`. Modellname und Reasoning-Stufe sind getrennte Parameter; kein erfundener Modellname mit angehängtem Effort. Beide unterstützen Responses, den bereits verwendeten Transport.

- https://developers.openai.com/api/docs/models/gpt-6-sol
- https://developers.openai.com/api/docs/models/gpt-6-luna

## Codex-Chat und vorhandener Transport

Die in dieser Sitzung bereitgestellte Codex-App-Werkzeugschnittstelle führt beide gewünschten Modell-/Effort-Kombinationen als auf dem Host unterstützt. Die lokale globale `config.toml` enthält weiterhin `model=gpt-6-astra`, `model_reasoning_effort=medium`, Provider `cc-switch-official`. Globale Vorgabe ist kein Beweis für die tatsächlich aktive Auswahl dieser einzelnen Aufgabe; die Chat-Auswahl wurde weder umgestellt noch visuell bestätigt.

Der lokale Modellcache enthält null Modelle; auch GET auf dem vorhandenen Router `/v1/models` lieferte eine leere Liste. Diese Katalogbefunde allein erlauben keine Aussage über erfolgreiche Inferenz. Deshalb zwei begrenzte echte synthetische Responses-Aufrufe über den vorhandenen lokalen Router, bestehende Authentifizierung, leere Werkzeugliste, store=false und keine Projektinhalte:

| Angefordert | Antwortmodell | Zurückgemeldeter Effort | Abschluss | Zeit | Tokens gesamt |
|---|---|---|---|---|---|
| GPT-6 Sol / xhigh | gpt-6-sol | xhigh | completed, Prüfmarker korrekt | 1,875s | 30 |
| GPT-6 Luna / max | gpt-6-luna | max | completed, Prüfmarker korrekt | 1,454s | 41 |

Originaler bereinigter Nachweis: `artifacts/model-transport-audit-20260924.json`. Einmalige kleine Transportprüfungen, keine Qualitäts-/Leistungsbewertung, kein Stabilitäts-Langzeittest und kein Beweis, welches Modell diesen Chat beantwortet. Zurückgemeldeter Effort ist eine API-Angabe, keine Messung interner Rechenintensität. Der bestehende Transport wurde für das Audit isoliert direkt angesprochen; dies ist ausdrücklich kein erfolgreicher produktiver Hermes-Workflow.

## Hermes/Governor: noch nicht integriert

Reproduzierter lokaler Befund für beide Paare: `routing_policy.validate_effort` und `HermesAdapter.review(..., probe_only=True)` weisen sie vor Prozessstart ab. Der Prüfaufruf stellte sicher, dass dabei kein Unterprozess startete. Nachweis: `artifacts/model-integration-audit-20260924.json`.

Konkrete Integrationslücken:

1. `routing_policy.py`: Modellliste enthält nur Terra 5.6, Sol 5.6 und Astra 6; Stufen und UI-Modi enden bei xhigh. Max fehlt.
2. `config.py`: Orchestrator ist fest auf Terra gebunden; Supervisorliste enthält Sol 5.6/Astra. `llm.py` hat eine separate gleichartige Modellliste, mehrere Abläufe verwenden `MODELS[0]`; `model_usage.py` prüft diese Liste ebenfalls.
3. Die UI bietet keine der beiden neuen Modelloptionen und kein max. RH-1 verwendet eine gemeinsame Reasoning-Auswahl. Gleichzeitig Sol/xhigh und Luna/max in getrennten Rollen erfordert rollenbezogene Bindungen oder ausdrücklich benannte Profile, nicht bloß zwei zusätzliche Menüeinträge.
4. Neue Modellauswahl muss bei Einreihung, jedem Versand sowie Vorschau-/Freigabeprüfung gebunden bleiben. Keine stille Rollenänderung, Absenkung oder Fallback. Vor Integration der Luna-Orchestratorrolle die derzeitigen Terra-Annahmen gezielt auflösen; Luna wird nicht allein durch Aufnahme in eine Supervisorliste zum korrekten Orchestrator.
5. Anschließend lokale Payload-/Negativ-/Drifttests, echte installierte Hermes-Nullwerkzeuginitialisierung und synthetische Ende-zu-Ende-Aufrufe über Hermes; die hier erfolgreichen Routerproben ersetzen diese Nachweise nicht.

Der Governor war beim Audit auf Port 8787 nicht erreichbar; er wurde für die Prüfung weder gestartet noch umkonfiguriert. Frühere Live-Aussagen beziehen sich auf den vorangegangenen Arbeitsstand.

## Entscheidung vor Fortsetzung

Prüfergebnis: gewünschte Paare offiziell unterstützt und auf dem vorhandenen Router live bestätigt; Codex-App-Schnittstelle kennt sie. Hermes-Anwendungsintegration offen. Vor einer Umsetzung die Rollen festlegen: mögliche Ergänzung Luna/max für begrenzte Vorschläge und Sol/xhigh für unabhängigen Review, Astra weiterhin ausdrücklich verfügbar. Dies ist eine Integrationsoption, keine bereits fachlich geprüfte Qualitäts- oder Kostenaussage. Bestehende Standards wurden nicht geändert.

Die gemeinsame Funktionsabnahme ist bis zur geklärten und geprüften Integration zurückgestellt. Keine Aurelia-/Serveränderungen und keine zusätzliche Projektfreigabe durch dieses Audit.
