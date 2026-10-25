# Codex-Chat: Luna-geführte und Sol-geführte Delegation

Stand 24.09.2026. Auftrag: ausschliesslich Codex-Chat konfigurieren und prüfen; Hermes vollständig ausgenommen. Der Betreiber hat beide Varianten und den anschliessenden Astra-Vergleich freigegeben. Keine Hermes-Module, -Routen oder Produktfreigaben geändert.

## Eingerichtete Varianten

| Profil | Hauptmodell | Helfer |
|---|---|---|
| `chat-luna-lead` (A) | GPT-6 Luna/max | Sol/xhigh für begrenzte Prüfungen; Astra/medium bei verbleibendem wesentlichem Widerspruch |
| `chat-sol-lead` (B) | GPT-6 Sol/xhigh | Luna/max für geeignete unabhängige Teilaufgaben |

Installiert unter `C:/Users/Hubert111/.codex/`: zwei separate `.config.toml`-Profile und drei benannte Agenten `chat_luna`, `chat_sol`, `chat_astra` unter `agents/`. Versionierte Kopien: `artifacts/chat-routing-ab24/config/`. Bytegleichheit und eingelesene Profilmarker geprüft. Die globale Basisdatei und das frühere Profil `agent-duo` wurden dabei nicht verändert. Globale Vorgabe bleibt Luna/max mit Luna/max-Unteragentenvorgabe; sie aktiviert **nicht** automatisch Variante A.

Die Profile erlauben bedarfsgesteuerte native Delegation, begrenzte Aufgaben, frischen Teilkontext und keine rekursive Weitergabe. Höchstens zwei Kindaufgaben je Anfrage sind eine Profilanweisung; die Konfiguration begrenzt zusätzlich gleichzeitig offene Kindaufgaben auf zwei. Das ist keine deterministische Garantie der Modellentscheidung und keine neue Handlungsberechtigung für Produktänderungen.

CLI-Aufruf: `codex -p chat-luna-lead` beziehungsweise `codex -p chat-sol-lead`. Diese Profilaktivierung wurde im installierten CLI geprüft. Ein Profilwechsel der **bereits laufenden Desktop-Aufgabe** ist damit nicht belegt. Für die Anwendung hier im Chat muss das jeweilige Hauptmodell im Modellmenü ausgewählt und die Variante ausdrücklich benannt sein; konkrete Helfer können dann mit den festgelegten Modell-/Reasoningwerten angefordert werden. Die Nutzerbestätigung einer Menüauswahl ersetzt keine technische Auslesung der aktiven Einstellung.

## Echte Delegationsnachweise

Eine native Luna/max-Unteragentenprobe in dieser Aufgabe lieferte das richtige Rechenergebnis. Die beiden Varianten wurden danach mit getrennten lokalen Codex-Sitzungen geprüft, nicht mit einer nachgebauten HTTP-Modellkette. Lokale Codex-Ausführungsdaten belegen Haupt-/Kindbeziehungen, konfigurierte Laufzeitmodelle und Reasoning, abgeschlossene Aufgaben sowie getrennte Verbrauchszähler. Das sind Laufzeitmetadaten, keine Modellselbstauskünfte und keine unabhängige Einsicht in das Modellinnere.

- Luna/max → Sol/xhigh: wiederholt in den A-Zustandsprüfungen abgeschlossen.
- Sol/xhigh → Luna/max: wiederholt in den B-Zustandsprüfungen abgeschlossen.
- Luna/max → Astra/medium: separate ausdrücklich ausgelöste Funktionsprobe bestanden; sie prüft die Fähigkeit, nicht die spontane Eskalationsentscheidung. Von der Vergleichswertung ausgeschlossen.

Das kompakte CLI-JSON zeigte nicht alle Spawn-Ereignisse und enthielt nur die Hauptagenten-Tokens. Deshalb wurde die Bewertung erst nach Ergänzung der Kindnachweise durchgeführt. Alle Auswertungen lesen nur die bekannten Testaufgaben und ihre tatsächlichen Kinder; keine anderen Gespräche.

## Aufgaben und Bewertung

Vorab gespeicherte Fragen und Sollantworten: `artifacts/chat-routing-ab24/manifest.json`. Drei Aufgaben mit je zwei Wiederholungen pro Variante, zunächst A/B, in der Wiederholung B/A. Danach derselbe Satz mit Astra/medium allein (C), Delegation dort deaktiviert. Nur native Agentenwerkzeuge erlaubt, keine Datei-, Shell-, Web- oder MCP-Arbeit; alle Daten synthetisch.

1. Routine: Rechnung mit zwei Positionen; keine Delegation erwartet.
2. Analyse: sieben Schritte einer Zustandsmaschine mit Version, Bestand und Idempotenz; bei A/B unabhängig prüfbarer Teilauftrag, Hauptagent prüft den übrigen Ablauf.
3. Unsicherheit: gleichrangige widersprüchliche Beobachtungen und eine Anweisung innerhalb von Quelltext; fehlende Fakten müssen ungeklärt bleiben.

Alle 18 Antworten waren fachlich korrekt, gültiges JSON und erfüllten die übrigen Ausgabevorgaben. Bei B verwendete eine Antwort für erfolgreiche Schritte `success` statt `applied`. Der ursprüngliche Fragetext schrieb dafür keinen exakten Statusbegriff vor. Rohbewertung bleibt unverändert (B: 5/6 wortgleiche Sollobjekte); zusätzliche fachliche Bewertung akzeptiert diesen gleichbedeutenden Begriff bei **allen** Varianten. Der Prüfer lehnt falsche Bestandswerte und erfundene Gewissheit weiterhin ab. Das ist eine dokumentierte Auswertungspräzisierung, keine nachträgliche Änderung von Aufgaben, Antworten oder Sollzuständen.

## Ergebnis über jeweils sechs Aufgaben

| Variante | Fachlich korrekt | Helfer insgesamt | Laufzeit gesamt / Mittel | Standard-API-Referenz mit gemeldetem Cache | Referenz rechnerisch ohne Cache |
|---|---:|---:|---:|---:|---:|
| A: Luna führt | 6/6 | 4 Sol | 321,123 s / 53,52 s | 0,169236 USD | 0,229394 USD |
| B: Sol führt | 6/6 | 3 Luna | 265,453 s / 44,24 s | 0,227886 USD | 0,524733 USD |
| C: Astra/medium allein | 6/6 | 0 | 161,827 s / 26,97 s | 0,710670 USD | 1,125390 USD |

A lag bei der Standard-API-Referenz rund 26 % unter B und 76 % unter C. B war rund 17 % schneller als A; C war am schnellsten. Dies sind **keine tatsächlich abgebuchten Codex-Kosten** und keine zugesagte Ersparnis bei Accountlimits. Die Rechnung verwendet veröffentlichte Standard-API-Preise ohne Fast-/Regional-/Sondertarife auf beobachtete Tokens einschliesslich aller Testkinder. Abonnementabrechnung, leitende Testsitzung, Einrichtung und vorgelagerte Funktionsproben sind nicht enthalten. Ausgabe-Tokens einschliesslich Reasoning wurden nur einmal gezählt.

| Variante | Eingabetokens | Davon Cachelesungen | Ausgabetokens |
|---|---:|---:|---:|
| A | 381.691 | 230.656 | 4.927 |
| B | 317.850 | 178.048 | 3.494 |
| C | 110.294 | 46.080 | 449 |

Die Tokenzahlen enthalten den Codex-Kontext und alle Modellrunden, nicht nur den kurzen Nutzertext. A verbrauchte mehr Tokens als B und C, war wegen der unterschiedlichen Modellpreise in der Vergleichsrechnung dennoch günstiger. Cachelesungen wurden real gemeldet. Cachewärme war nicht kontrolliert; eine universell optimale Cachequote oder gemeinsame Cache-Nutzung zwischen Modellen ist nicht bewiesen. Deshalb ist zusätzlich die rechnerische Variante ohne Cache angegeben. Zeitmessungen umfassen CLI-Start und Agentenkoordination; keine reinen Inferenzzeiten.

## Stabilität, Empfehlung und Grenzen

Keine Modellfehler, Zeitüberschreitungen, falschen Modellzuordnungen oder unerlaubten Werkzeuge in den 18 Wertungsläufen. Beide Wiederholungen ergaben dieselben fachlichen Ergebnisse. B delegierte den Unsicherheitsfall einmal an Luna und löste ihn einmal selbst; das entsprach seiner erlaubten Ermessensentscheidung, zeigt aber, dass der Aufrufweg nicht deterministisch ist. A verwendete für denselben Fall beide Male Sol; Astra wurde dort nicht angefordert. Fehlende Fakten wurden durch keine Route in Gewissheit umgedeutet.

Vorläufige Empfehlung für kostenbewusste normale Chat-Arbeit: **Variante A** als erprobter Kandidat. Wer Antwortzeit priorisiert, erhielt mit C hier das schnellste Ergebnis. B war ein Mittelweg. Kein Qualitätsvorsprung und keine allgemeine Gleichwertigkeit bei komplexer Produktarbeit belegt: nur drei synthetische Aufgaben, zwei Wiederholungen, keine langen Dialoge, Codeänderungen, Toolketten oder schwierigen realen Projektfälle. Aus dieser Stichprobe folgt keine automatische Freigabe jeder zukünftigen Luna-Entscheidung.

Bereinigte Einzelnachweise, Zusammenfassung und Testtreiber: `artifacts/chat-routing-ab24/`. Bestehende Codex-Warnung zum ignorierten Schlüssel `mcp_servers.codeagentswarm-tasks.type` bleibt ein separater Konfigurationspunkt; keine Modellfehlfunktion daraus abgeleitet.

## Quellen

- Codex-Konfiguration: https://learn.chatgpt.com/docs/config-file/config-reference
- Native Unteragenten: https://learn.chatgpt.com/docs/agent-configuration/subagents
- Luna-Preise: https://developers.openai.com/api/docs/models/gpt-6-luna
- Sol-Preise: https://developers.openai.com/api/docs/models/gpt-6-sol
- Astra-Preise: https://developers.openai.com/api/docs/models/gpt-6-astra
