# Vorprüfung Medium / Low — 16.09.2026

## Entscheidung

Medium bleibt Standard. Keine automatische Umstellung aktiviert. Für den bestehenden Codex-Chat ist keine verifiziert verfügbare Selbstumschaltung nachgewiesen; klare Hinweise und Nutzerbestätigung bleiben der verfügbare Ablauf. Hermes kann später über RH-1 vor einzelnen Aufträgen explizit Low wählen, nach separater Implementierung und Abnahme. Die Produktionsadapter weisen Low derzeit weiterhin zurück.

## Tatsächlich ausgeführter Kurztest

Sechs echte Anfragen über die konfigurierte lokale CC-Switch-Route, Modell stets gpt-6-astra, drei identische synthetische Aufgaben jeweils einmal Medium und Low. Reihenfolge paarweise gewechselt. Keine Projektinhalte, Werkzeuge, automatischen Wiederholungen oder Änderungen an produktiven Routingregeln. Der isolierte Versuch verwendet den vorhandenen Transport direkt; er ist kein Hermes-Ende-zu-Ende-Test. Die Antwort meldete jeweils das angeforderte Modell und Effort; dies ist Router-/Antwortmetadaten-Evidenz, keine unabhängige Provider-Attestierung.

Vorab festgelegte erwartete JSON-Ergebnisse wurden exakt verglichen; kein Modell als Prüfer, kein generierter Code ausgeführt.

| Aufgabe | Medium gesamt | Low gesamt | Korrekt Medium / Low |
|---|---:|---:|---|
| Typen und Wertebereich | 129 | 105 | ja / ja |
| Transitive Belegentwertung | 136 | 135 | ja / ja |
| Strikte Abschlussbedingungen | 198 | 198 | ja / ja |
| Summe | 463 | 438 | 3/3 / 3/3 |

Input jeweils 376 Tokens; Output einschließlich Reasoning 87 versus 62. Gesamtersparnis 25 Tokens bzw. 5,40 %, Outputreduktion 28,74 %. Reasoning-Tokens 35 versus 12, bereits im Output enthalten. Keine Cache-Hits gemeldet. Gesamtlatenz 10,703 versus 7,907 Sekunden, aber eine Low-Antwort war langsamer (3,016 statt 2,125 Sekunden). Diese Einmalmessung belegt weder eine allgemeine Geschwindigkeitsverbesserung noch gleiche Qualität bei komplexer Codearbeit. Gesamter Versuch: 901 gemeldete Tokens, ohne diesen Chat und Werkzeuge. Keine Aussage zu Eurokosten oder Codex-Kontingentverbrauch.

## Szenarien und Grenzen

1. Alles Medium: heutige Basis. Kein Routingaufwand, bewährte Produktionsregeln.
2. Halbautomatischer Chat: Planung Medium; nur ein hinreichend großes, risikoarmes Umsetzungspaket mit geklärtem Plan als Low-Kandidat. Vorher Abschlussnachricht `Bitte jetzt auf Low umschalten. Danach: „Low bereit“.`, danach vor Review `Bitte jetzt zurück auf Medium umschalten. Danach: „Medium bereit“.`. Nutzerbestätigung ist kein unabhängig gemessener Laufzeitzustand. Unklarheit oder unerwartete Komplexität: Arbeit am sicheren Punkt anhalten und Medium anfordern. Zusätzliche Nachrichten/erneute Kontextverarbeitung können Einsparungen übersteigen. Ein Prompt allein ändert keine Einstellung.
3. Hermes-Automatik: technisch über explizite Parameter pro Anfrage möglich; RH-1 muss Auswahlregel, manuelle Priorität, Protokollierung und fehlende Providerunterstützung prüfen. Unklare Klassifikation, Sicherheitsarbeit, Migrationen, Backups und kritische Reviews bleiben Medium. Keine automatische Wahl höherer Stufen, kein Modellwechsel und keine zusätzlichen Projektfreigaben. Diese Automatik wurde hier nicht implementiert oder Ende-zu-Ende getestet.
4. Transparenter Proxy-Umschalter im bestehenden Codex-Chat: ohne belegte Integration nicht empfehlen. Eine unterhalb der Oberfläche umgeschriebene Anfrage kann von der angezeigten Auswahl abweichen. Die dokumentierte API-Funktion configuration_update ist kein Nachweis einer entsprechenden Steuerfunktion in diesem Chat.

Rechenbeispiel ausschließlich für die gemessenen drei Aufgaben: Alle auf Low ergäben 438 statt 463 Tokens ohne Zusatzaufwand. Mehr als 25 zusätzliche Tokens für Steuerung/Bestätigung/erneute Kontextverarbeitung würden diesen Vorteil aufheben. Eine zusätzliche vollständige Medium-Wiederholung der Low-Aufgaben ergäbe 901 statt 463 Tokens (+94,60 %). Das ist kein Vorschlag, erforderliche Prüfungen wegzulassen. Für den echten Arbeitsmix gilt: Nettoersparnis = vermiedener Verbrauch geeigneter Aufgaben minus Routing-, Umschalt-, Review- und Nacharbeitsmehrverbrauch. Ein belastbarer Prozentsatz für das Projekt oder diesen langen Chat ist damit noch nicht bestimmbar.

## Empfehlung und nächste Prüfungen

Halbautomatische Hinweise für größere klar abgegrenzte Pakete beibehalten; keine Umschaltung für einzelne Kleinstaufgaben. Hermes-RH-1 an der bestehenden Stelle nach Abschlussnachweisen weiter planen. Vor Aktivierung repräsentative Implementierungsaufgaben in isolierten Kopien mehrfach vergleichen, mit denselben Tests und Abnahmekriterien, Fehler-/Nacharbeitsquote, Kontext-/Cacheverbrauch und Rückkehr zu Medium. Keine uneingeschränkte Qualitätsgarantie aus drei Kurzaufgaben ableiten. Kein breiter Rollout auf Grundlage dieser Messung.

Rohdaten: `artifacts/reasoning_eval_2026-09-16/results.json`; maschinell geprüfte Zusammenfassung: `artifacts/reasoning_eval_2026-09-16/summary.json`. Bestehender Pause-Wiederherstellungspunkt bleibt unverändert; diese Vorprüfung entstand danach.

Quellen: [Codex-Konfiguration](https://learn.chatgpt.com/docs/config-file/config-reference), [OpenAI-Modellhinweise und configuration_update](https://developers.openai.com/api/docs/guides/latest-model). API-Unterstützung ersetzt keinen Kompatibilitätsnachweis der gesamten CC-Switch-/Hermes-/Desktop-Kette.
